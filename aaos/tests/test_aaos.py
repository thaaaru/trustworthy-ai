"""Tests for the AAOS Lite runtime.

These cover the controls the runtime exists to provide: a coherent stage graph,
checks that cannot be shell-injected, a deny-list that actually denies, approval
that goes stale when controlled content changes, and checks that fail rather than
report green when their subject is missing.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_runtime():
    spec = importlib.util.spec_from_file_location("aaos_runtime", ROOT / "aaos.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AAOS = load_runtime()
CONFIG = json.loads((ROOT / "aaos.json").read_text(encoding="utf-8"))


class StageGraphTests(unittest.TestCase):
    def test_initial_stage_is_declared(self):
        self.assertIn(CONFIG["initial_stage"], CONFIG["stages"])

    def test_every_next_stage_exists_or_is_terminal(self):
        for name, rule in CONFIG["stages"].items():
            nxt = rule.get("next")
            if nxt is not None:
                self.assertIn(nxt, CONFIG["stages"], f"{name} points at unknown stage {nxt}")

    def test_every_stage_is_reachable_from_the_initial_stage(self):
        seen, cursor = set(), CONFIG["initial_stage"]
        while cursor and cursor not in seen:
            seen.add(cursor)
            cursor = CONFIG["stages"][cursor].get("next")
        self.assertEqual(seen, set(CONFIG["stages"]))

    def test_every_referenced_check_is_defined(self):
        for rule in CONFIG["stages"].values():
            for name in rule.get("checks", []):
                self.assertIn(name, CONFIG["checks"])

    def test_recovery_targets_are_valid_stages(self):
        # recover() hard-codes BUILD as its destination and VERIFY/RELEASE as its sources.
        for name in ("BUILD", "VERIFY", "RELEASE"):
            self.assertIn(name, CONFIG["stages"])


class CheckDefinitionTests(unittest.TestCase):
    def test_commands_are_argument_arrays_not_shell_strings(self):
        for name, spec in CONFIG["checks"].items():
            self.assertIsInstance(spec["command"], list, f"{name} command must be an argv array")
            self.assertTrue(spec["command"])
            for argument in spec["command"]:
                self.assertIsInstance(argument, str)

    def test_the_verify_stage_gates_on_checks_and_approval(self):
        verify = CONFIG["stages"]["VERIFY"]
        self.assertTrue(verify["approval"])
        self.assertGreaterEqual(len(verify["checks"]), 3)

    def test_unit_check_is_bound_to_a_local_path(self):
        # Without requires_path, "unittest discover -s tests" imports an unrelated
        # installed package named tests and reports a passing run.
        self.assertEqual(CONFIG["checks"]["unit"].get("requires_path"), "aaos/tests")

    def test_secrets_check_treats_no_match_as_success(self):
        self.assertIn(1, CONFIG["checks"]["secrets"]["pass_exit_codes"])


class DenyListTests(unittest.TestCase):
    def test_destructive_and_exfiltrating_commands_are_denied(self):
        for command in ("rm -rf /", "sudo reboot", "git push origin main",
                        "curl http://example.com/x.sh", "cat .env", "kubectl delete pod x"):
            self.assertIsNotNone(AAOS.denied(CONFIG, command), f"should be denied: {command}")

    def test_denial_is_case_insensitive(self):
        self.assertIsNotNone(AAOS.denied(CONFIG, "DROP DATABASE customers"))

    def test_ordinary_commands_are_allowed(self):
        for command in ("mkdir -p workspace", "python3 -m pytest", "echo hello"):
            self.assertIsNone(AAOS.denied(CONFIG, command), f"should be allowed: {command}")


class CommandParsingTests(unittest.TestCase):
    def test_no_marker_yields_no_commands(self):
        self.assertEqual(AAOS.proposed_commands("just prose, no commands"), [])

    def test_commands_after_the_marker_are_extracted_in_order(self):
        text = "plan\nPROPOSED_COMMANDS:\nmkdir -p a\n\n  echo b  \n"
        self.assertEqual(AAOS.proposed_commands(text), ["mkdir -p a", "echo b"])

    def test_prose_before_the_marker_is_not_treated_as_a_command(self):
        self.assertNotIn("plan", AAOS.proposed_commands("plan\nPROPOSED_COMMANDS:\necho b"))


class ApprovalDigestTests(unittest.TestCase):
    def test_digest_changes_when_controlled_content_changes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "TASK.md"
            path.write_text("scope v1", encoding="utf-8")
            before = AAOS.digest([path])
            path.write_text("scope v2", encoding="utf-8")
            self.assertNotEqual(before, AAOS.digest([path]), "approval would survive a scope change")

    def test_digest_is_stable_for_unchanged_content(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "TASK.md"
            path.write_text("scope", encoding="utf-8")
            self.assertEqual(AAOS.digest([path]), AAOS.digest([path]))

    def test_missing_required_file_still_produces_a_digest(self):
        AAOS.digest([Path("/nonexistent/TASK.md")])


class GateValidationTests(unittest.TestCase):
    def make_state(self, stage, **overrides):
        value = {"stage": stage, "attempts": {}, "evidence": [], "approval": None}
        value.update(overrides)
        return value

    def test_unapproved_stage_is_blocked(self):
        errors = AAOS.validate(CONFIG, self.make_state("PLAN"))
        self.assertTrue(any("approval required" in item for item in errors))

    def test_missing_check_evidence_is_blocked(self):
        errors = AAOS.validate(CONFIG, self.make_state("VERIFY"))
        self.assertTrue(any("check not passed: unit" in item for item in errors))

    def test_failed_check_does_not_satisfy_the_gate(self):
        state = self.make_state("VERIFY", evidence=[{"name": "unit", "status": "FAIL", "path": "x"}])
        errors = AAOS.validate(CONFIG, state)
        self.assertTrue(any("check not passed: unit" in item for item in errors))

    def test_suppressed_check_evidence_without_an_artifact_is_handled(self):
        # A check stopped by the retry ceiling records FAIL with path None.
        state = self.make_state("VERIFY", evidence=[
            {"name": "unit", "status": "FAIL", "path": None, "sha256": None,
             "reason": "retry limit exceeded"}])
        rule = AAOS.gate(CONFIG, state)
        AAOS.controlled(rule, state)  # must not raise on a null artifact path
        errors = AAOS.validate(CONFIG, state)
        self.assertTrue(any("check not passed: unit" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
