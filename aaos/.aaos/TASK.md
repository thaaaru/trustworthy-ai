# Task

Task-ID: AAOS-001
Owner: Tharaka
Approver: Tharaka
Risk-Tier: MEDIUM

## Requested outcome

Replace the two AAOS archives and the two presentation decks with a single-file governed
runtime that this repository can be held to by its own gate.

## In scope

- `aaos/aaos.py` and `aaos/aaos.json`: lifecycle gate, agent loop, controls
- `aaos/tests/`: tests covering the stage graph, deny-list, digest, and gate validation
- `aaos/POLICY.md`: tool and context policy, with the enforcement point named per rule
- `.github/workflows/aaos.yml`: CI running `status` and `check` on every pull request
- `README.md`: corrected to describe shipped behaviour, with aspirational architecture marked

## Out of scope

- Reintroducing third-party dependencies
- Shipping binary artifacts in the repository
- The ARCHITECTURE, THREATS, EVIDENCE and RETROSPECTIVE templates, which the four-stage
  lifecycle no longer requires

## Acceptance criteria

- AC-01: `python3 aaos/aaos.py check` passes from a clean clone, on real local tests
- AC-02: A check whose subject is missing records FAIL instead of reporting a passing run
- AC-03: Removing a deny-listed pattern fails the test suite
- AC-04: No README statement describes behaviour the runtime does not implement
