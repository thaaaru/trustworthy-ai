# AAOS Lite

A governed agent runtime in **one file, standard library only**. Python 3.10+, no `pip install`.

It replaces the previous two-package layout (a workflow control plane plus an 11-module
agent runtime, 3 third-party dependencies) with `aaos.py` + `aaos.json`.

## Model

One state machine, four stages:

```
PLAN ──approval──▶ BUILD ──▶ VERIFY ──checks + approval──▶ RELEASE
                     ▲                   │
                     └──── recover ──────┘
```

- **PLAN** — write `.aaos/TASK.md`; a named human approves the scope.
- **BUILD** — agents run; every proposed shell command is deny-list filtered and
  individually approved by a human.
- **VERIFY** — allow-listed checks run with `shell=False`; output is hashed into
  `.aaos/evidence/`; a named human approves the evidence.
- **RELEASE** — requires `.aaos/RELEASE.md` with a rollback procedure.

Approvals are bound to a SHA-256 digest of the controlled files. Change a required file
after approval and the gate reopens — you cannot approve one version and ship another.

Everything lands under `.aaos/`: `STATE.json` (current gate), `LEDGER.jsonl` (append-only
history), `evidence/` (check output), `runs/` (agent transcripts).

## Use

```bash
python3 aaos.py init                                     # create .aaos/ and templates
$EDITOR .aaos/TASK.md
python3 aaos.py approve --by "Name" --decision approve --note "scope agreed"
python3 aaos.py advance                                  # PLAN -> BUILD
python3 aaos.py run "Add rate limiting to the upload endpoint"
python3 aaos.py advance                                  # BUILD -> VERIFY
python3 aaos.py check                                    # unit, compile, secrets
python3 aaos.py approve --by "Name" --decision approve --note "evidence reviewed"
python3 aaos.py advance                                  # VERIFY -> RELEASE
python3 aaos.py history
```

Other commands: `status` (stage, evidence, current blockers), `recover --reason "..."`
(VERIFY or RELEASE back to BUILD), `run --task-file path.md`, `run --no-tools`.

## Configuration

Everything is in `aaos.json`: stage graph, check commands, agents, model, deny-list.

Agents default to a deterministic `mock` provider so the whole lifecycle runs offline.
For a real model:

```bash
export AAOS_API_KEY=sk-...
# aaos.json -> "model": {"provider": "openai_compatible",
#                        "name": "gpt-4o-mini",
#                        "base_url": "https://api.openai.com",
#                        "api_key_env": "AAOS_API_KEY"}
```

Any OpenAI-compatible `/v1/chat/completions` endpoint works, including a local one.

A check may declare `"requires_path": "tests"`. If that path is missing the check records
FAIL without running, rather than letting a tool silently resolve something else — bare
`unittest discover -s tests` will happily import an unrelated installed `tests` package and
report green, which is exactly the false assurance this runtime exists to prevent.

## Controls worth knowing

| Control | Where |
|---|---|
| Deny-list on agent commands | `denied_command_patterns` in `aaos.json` |
| Per-command human approval | `execute()` — prompts unless `--no-tools` |
| Checks cannot be shell-injected | `subprocess.run(..., shell=False)` with argv arrays |
| Approval cannot go stale | `digest()` over required files + passed evidence |
| Checks cannot report false green | `requires_path` fails the check when its subject is absent |
| Retry limit on failing checks | `max_check_attempts` |
| Full audit trail | `.aaos/LEDGER.jsonl`, append-only |

Secrets are never read by the runtime; the model key comes from an environment variable
named in config, and `git push`, `sudo`, `curl`, `.env` access are deny-listed by default.
