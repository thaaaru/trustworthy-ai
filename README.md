# Trustworthy AI: Governed Agents & Continuous Security Assurance

A comprehensive framework for building, governing, and auditing AI agents in enterprise environments using **AAOS Lite MD** (AI Agent Orchestration System) with end-to-end security, privacy, and compliance controls.

> **Trust is not a model feature.** It is an end-to-end property of a socio-technical system.

---

## Overview

This repository contains production-ready patterns and tools for:

- ✅ **Building controlled AI agents** with explicit scope, permissions, and lifecycle gates
- ✅ **Continuous security assurance** replacing periodic, event-driven audits
- ✅ **Governed orchestration** with human approval at consequential gates
- ✅ **Evidence preservation** for compliance, recovery, and auditability
- ✅ **Risk management** through threat modeling and control policies

### Key Problem Statements

1. **Conventional security is periodic; business risk is continuous.**
   - Traditional audits happen annually or after incidents
   - AAOS enables continuous, governed assurance integrated into the engineering workflow

2. **AI systems require different security boundaries than conventional software.**
   - Data, model, and infrastructure must all be protected
   - LLM inputs and outputs require injection, PII, and policy validation
   - Tool-calling systems need strict schemas, idempotency, and audit trails

3. **Agent autonomy must be constrained and verifiable.**
   - Agents operate under an explicit constitution (authority order, lifecycle gates, action classes)
   - Every action is logged, evidenced, and recoverable
   - Human approval is required before deployment and on policy violations

---

## Core Components

### 1. AAOS Lite (`aaos/`)

A **repository-local control plane plus agent runtime**, in one standard-library file
(`aaos/aaos.py`) driven by one config file (`aaos/aaos.json`). Python 3.10+, no dependencies.

**Lifecycle stages:**

```
PLAN ──approval──▶ BUILD ──▶ VERIFY ──checks + approval──▶ RELEASE
                     ▲                   │
                     └──── recover ──────┘
```

- `PLAN` — define purpose, scope, acceptance criteria in `.aaos/TASK.md`; named human approves
- `BUILD` — agents produce bounded changes; proposed shell commands are deny-listed and individually approved
- `VERIFY` — allow-listed checks run and their output is hashed into `.aaos/evidence/`
- `RELEASE` — requires `.aaos/RELEASE.md` with an explicit rollback procedure

**Key controls:**
- Deterministic state machine in `.aaos/STATE.json`
- Approval is bound to a SHA-256 digest of the controlled files — edit a required file after
  approval and the gate reopens, so you cannot approve one version and ship another
- Checks run as argv arrays with `shell=False`; no shell interpretation, no command chaining
- Append-only ledger at `.aaos/LEDGER.jsonl` covering transitions, approvals, checks, and every
  command the agent proposed, ran, skipped, or had blocked
- Retry ceiling on failing checks (`max_check_attempts`)

**Authority order:**
1. Human instructions in the current session
2. The stage gate in `.aaos/STATE.json` and the graph in `aaos.json`
3. `.aaos/TASK.md` and recorded approvals
4. Retrieved project content (treated as untrusted data)

**Action classes:**
- `READ` — inspect repository content within task scope; logged
- `CREATE` / `CHANGE` — agent-proposed commands; deny-list filtered, then approved one at a time
- `EXTERNAL` — denied by default (`curl`, `wget`, `git push`, `sudo`, `.env` access are deny-listed)

**Quickstart:**
```bash
cd aaos
python3 aaos.py init                                     # create .aaos/ and templates
python3 aaos.py status                                   # stage, evidence, current blockers
python3 aaos.py approve --by "PM" --decision approve --note "scope agreed"
python3 aaos.py advance                                  # PLAN -> BUILD
python3 aaos.py run "Add rate limiting to the upload endpoint"
python3 aaos.py advance && python3 aaos.py check         # BUILD -> VERIFY, run checks
python3 aaos.py history                                  # inspect the ledger
python3 aaos.py recover --reason "..."                   # VERIFY/RELEASE -> BUILD
```

Full runtime documentation: [`aaos/README.md`](aaos/README.md).

---

### 2. Trustworthy AI Framework

#### A. Building & Breaking Governed Agents
- Hands-on: build a simple AI orchestrator with AAOS Lite
- Red-team exercise: attempt to break governance (injection, tool misuse, context poisoning)
- Verify controls hold under adversarial conditions

#### B. Driving Information Security Resilience Through Agentic AI

**Thesis:** Move from **periodic assurance** (events → evidence → reports) to **continuous, governed assurance** integrated into engineering.

**Business Continuity Reality:**
- Transactions are continuous
- Risk is continuous
- Assurance should be continuous, not event-driven

**Solution:** Agentic AI as **automated compliance and risk orchestration**
- Policy-aware agents execute business workflows
- Governed guardrails (input sanitization, output validation, audit trails)
- Continuous evidence capture
- Real-time risk signaling

---

## Security & Compliance Architecture

> **Scope note.** This section is the reference architecture this framework argues for — the
> design you build *around* a governed runtime. It is **not** a description of `aaos/aaos.py`,
> which implements the lifecycle gate, the agent loop, and the controls listed under
> [Core Components](#1-aaos-lite-aaos) and nothing else. Sanitization layers, schema
> validation, tenant isolation, and tracing below are your integration work.

### Layered Input/Output Sanitization (target architecture)

```
USER INPUT
  ↓
[1] Format validation (schema, type)
  ↓
[2] Injection detection (heuristic + LLM-based)
  ↓
[3] PII detection (hash + sample + encrypted blob with TTL)
  ↓
[4] Policy validation (content, sentiment, topic)
  ↓
MODEL CALL
  ↓
[5] Output validation (schema, length, policy)
  ↓
[6] PII redaction (automatic removal or encryption)
  ↓
[7] Compliance check (GDPR, SOC 2, HIPAA alignment)
  ↓
USER OUTPUT
```

### Tool/Agent Control Model (target architecture)

**Whitelisting & Idempotency:**
- Pydantic strict schemas (no open-ended string tools)
- Idempotency keys on all side-effect tools (UUID or content hash)
- Per-tool authorization and append-only audit trail

**Multi-Tenant Isolation:**
- Postgres row-level security (RLS)
- `tenant_id` propagated through every span
- Cross-tenant queries must fail verification at test time

**Error Handling:**
- Fail-closed on auth/validation/injection
- Fail-open on transient errors (with exponential backoff)
- Retry budgets enforced per request

### Observability & Cost Tracking (target architecture)

- **OpenTelemetry** on every LLM call, tool call, retrieval
- **Langfuse** for trace inspection, cost attribution, latency SLOs
- **Token budgets** enforced pre-flight (reject before API call)
- **Model fallback chains** (Opus → Sonnet → Haiku) to degrade before failing
- **Prompt caching** always enabled (system + tools + few-shot)

### Red-Teaming & Assurance (target architecture)

**Automated Categories (nightly):**
1. **Injection** — Direct injection, context poisoning, role-play hijack, tool-arg injection
2. **Tool Misuse** — Calling tools with invalid/malicious arguments
3. **Data Exfiltration** — Attempting to extract training data, tenant data, or secrets
4. **Hallucination** — Model generating false claims or fabricated data

**Manual Categories (quarterly):**
5. **Refusal Bypass** — Attempting to circumvent safety guards ("jailbreaks")
6. **Multi-tenant Breach** — Cross-tenant query or RLS bypass

---

## File Structure

```
trustworthy-ai/
├── README.md              (this file)
└── aaos/
    ├── aaos.py            Control plane + agent runtime, standard library only
    ├── aaos.json          Stage graph, checks, agents, model, deny-list
    ├── README.md          Runtime documentation
    └── .aaos/             Created by `aaos.py init`, git-ignored
        ├── STATE.json     Current stage, evidence, approval
        ├── LEDGER.jsonl   Append-only history
        ├── TASK.md        Engagement contract
        ├── RELEASE.md     Release and rollback record
        ├── evidence/      Hashed check output
        └── runs/          Agent transcripts
```

---

## Installation & Setup

### Prerequisites

- **Python 3.10+** — that is the whole list; the runtime imports only the standard library
- **Git** — for the `secrets` check and CI integration

### Step 1: Clone This Repository

```bash
git clone https://github.com/thaaaru/trustworthy-ai.git
cd trustworthy-ai/aaos
```

### Step 2: Initialize the Workflow

```bash
python3 aaos.py init
# Initialized at PLAN. Fill in .aaos/TASK.md next.
```

### Step 3: (Optional) Point It at a Real Model

Agents run against a deterministic `mock` provider by default, so the entire lifecycle works
offline. To use a real model, set the key in the environment and edit `aaos.json`:

```bash
export AAOS_API_KEY=sk-...
```

```json
"model": {
  "provider": "openai_compatible",
  "name": "gpt-4o-mini",
  "base_url": "https://api.openai.com",
  "api_key_env": "AAOS_API_KEY"
}
```

Any OpenAI-compatible `/v1/chat/completions` endpoint works, including a local one. The key is
read from the named environment variable only — never from config, never from the repository.

⚠️ **Never commit secrets.** The `secrets` check greps the working tree for AWS keys, GitLab
PATs, private keys, and inline passwords, and fails the VERIFY gate when it finds them.

### Step 4: Verify Installation

```bash
python3 aaos.py status
# {"stage": "PLAN", "next": "BUILD", "approval_required": true, ... }
```

---

## CI Enforcement (Optional)

The gate lives in `.aaos/STATE.json`, so CI can only read it if that state is committed.
`.gitignore` keeps `aaos/.aaos/runs/` (agent transcripts) out of the repository and tracks
the rest — `STATE.json`, `LEDGER.jsonl`, `TASK.md`, `RELEASE.md`, `evidence/` — because the
audit trail is the deliverable.

Add `.github/workflows/aaos.yml`:

```yaml
name: aaos
on: [pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 aaos/aaos.py status
      - run: python3 aaos/aaos.py check
```

Both commands exit non-zero when the workflow has not been initialized, when a stage has no
checks configured, or when any allow-listed check fails — so an ungoverned branch fails the
build. No container image and no dependency installation step is required.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ERROR: not initialized` | Run `python3 aaos.py init` from the `aaos/` directory |
| `BLOCKED: approval required at ...` | Record a decision: `python3 aaos.py approve --by "..." --decision approve --note "..."` |
| `BLOCKED: approval stale` | A required file changed after approval; re-approve the current content |
| `FAIL: unit` and the evidence says `required path 'tests' does not exist` | A check declaring `requires_path` fails instead of running when that path is missing, so it cannot report green on someone else's installed package. Create `tests/`, or remove `unit` from the stage in `aaos.json` |
| `FAIL: <name> (retry limit exceeded)` | The check has been attempted more than `max_check_attempts` times at this stage; advance or `recover` to reset the counters |
| `BLOCKED (pattern): <command>` | The agent proposed a deny-listed command; adjust `denied_command_patterns` only with a reason |
| `ERROR: set AAOS_API_KEY` | Export the variable named by `model.api_key_env` |

---

## Quick Start

### 1. Initialize a New AI Project with AAOS Governance

```bash
cd aaos
python3 aaos.py init

# Define your task in .aaos/TASK.md
# Example:
# - Requested outcome: a customer-support chatbot
# - In scope: LLM integration, tool-calling (ticket lookup, FAQ search)
# - Acceptance: handles 5 customer personas; passes the injection test suite
# - Out of scope: scheduling, financial transactions

python3 aaos.py status                   # shows remaining blockers
python3 aaos.py approve --by "PM" --decision approve --note "Scope accepted"
python3 aaos.py advance                  # PLAN -> BUILD
```

### 2. Design Security & Controls

In `.aaos/TASK.md`, before leaving PLAN, state:
- **Data flows** (user input → model → tool → output)
- **Threat model** (STRIDE or PASTA)
- **Controls** (per-layer sanitization, idempotency, RLS)
- **Audit strategy** (what to log, for how long, to where)

### 3. Build with Guardrails

```bash
python3 aaos.py run "Wrap the ticket lookup tool in a strict schema"
```

Each configured agent runs in order and its output is written to `.aaos/runs/<timestamp>/`.
Any command an agent proposes after `PROPOSED_COMMANDS:` is:

- checked against `denied_command_patterns` and blocked outright on a match,
- otherwise shown to you and run only on an explicit `y`,
- recorded in `.aaos/LEDGER.jsonl` either way — blocked, skipped, or run with its exit code.

Use `--no-tools` to run the agent chain with execution disabled entirely, and
`--task-file path.md` to pass a task from a file.

### 4. Run Assurance Suite

```bash
python3 aaos.py advance        # BUILD -> VERIFY
python3 aaos.py check          # execute allow-listed checks: unit, compile, secrets

# Review evidence in .aaos/evidence/, then approve it
python3 aaos.py approve --by "QA" --decision approve --note "All checks passing"
python3 aaos.py advance        # VERIFY -> RELEASE
```

Re-running `check` clears the prior approval, so evidence can never be approved before the
run it refers to.

### 5. Release with an Approval Trail

```bash
# Fill in .aaos/RELEASE.md: what ships, verification, rollback procedure
python3 aaos.py approve --by "CTO" --decision approve --note "Ready for prod"
python3 aaos.py status         # confirms the RELEASE gate is clean
```

### 6. Observe & Evolve

```bash
python3 aaos.py history        # inspect the full ledger
python3 aaos.py recover --reason "latency regression in canary"   # back to BUILD
```

---

## Use Cases

### Enterprise Cybersecurity
- **Continuous risk assessment** — Agentic AI runs vulnerability scans, analyzes results, generates risk reports
- **Compliance orchestration** — Automated evidence capture for ISO 27001, SOC 2, HIPAA audits
- **Incident response** — AI-assisted triage with human-verified escalation and runbooks

### Financial Services
- **KYC/AML screening** — Governed agent queries external databases, flags risks, escalates to human reviewer
- **Fraud detection** — Real-time transaction analysis with policy-based guardrails and audit trail
- **Regulatory reporting** — Automated evidence collection for supervisory filings

### Healthcare
- **Clinical decision support** — AI recommendations with PII encryption, clinical note auditing, liability trail
- **Patient data governance** — Automated consent management, HIPAA audit logging, data residency enforcement
- **Research data coordination** — IRB-compliant AI assistance for study coordination and analysis

### SaaS / Multi-Tenant Platforms
- **Customer support automation** — Tenant isolation (RLS), cross-tenant breach detection, per-tenant audit trails
- **Data pipeline governance** — AI-assisted ETL with lineage tracking, quality gates, and cost attribution
- **Self-service analytics** — Governed agent builds queries, validates for security/performance, explains results to users

---

## Learning Resources

### Documentation
- `aaos/README.md` — runtime documentation: stages, controls, configuration
- `aaos/aaos.json` — the lifecycle state machine, check definitions, agents, and deny-list
- `aaos/aaos.py` — the implementation; one file, no dependencies to audit through

### Reading the Controls
- Deny-list and per-command approval: `execute()` in `aaos.py`
- Approval staleness binding: `digest()` and `validate()` in `aaos.py`
- Evidence capture and hashing: `cmd_check()` in `aaos.py`

---

## Security & Compliance Checklist

**Before Production Deployment:**

- [ ] **PLAN stage:** Engagement contract complete (requested outcome, scope, acceptance criteria, out-of-scope list); approved by a named human
- [ ] **PLAN stage:** Threat model and control design documented; risk decisions recorded
- [ ] **BUILD stage:** Change set complete; mapped to acceptance criteria; no deny-listed command was weakened to make it pass
- [ ] **VERIFY stage:** All checks passing; evidence hashed in `.aaos/evidence/`; no unresolved blockers from `status`
- [ ] **VERIFY stage:** Evidence approved by a different person than the implementer
- [ ] **RELEASE stage:** `.aaos/RELEASE.md` states the rollback procedure and it has been rehearsed
- [ ] **Observability:** Tracing enabled; metrics and cost tracking active
- [ ] **Red-team:** Cats 1–4 automated (nightly); cats 5–6 scheduled (quarterly); CRITICAL/HIGH remediated
- [ ] **Multi-tenant:** RLS verified; cross-tenant query test failing (as expected); audit logs showing tenant isolation
- [ ] **Secrets:** `secrets` check green; no API keys in logs; vault rotation schedule set; PII redaction verified
- [ ] **SLA:** Uptime/latency/error/cost targets defined; alerting configured; escalation runbook ready

---

## Contributing

This is a **reference architecture + governance framework**, not a framework requiring pull requests. Organizations should:

1. **Fork or clone** this repository into their codebase
2. **Customize** `aaos/aaos.json` — stage graph, check commands, agents, and deny-list — to your threat model and compliance regime
3. **Wire into your CI/CD** so `aaos.py check` gates pull requests
4. **Train your team** on the stage gates and the authority order above

---

## License & Attribution

**Framework by:** Tharaka (Enterprise Cybersecurity Architect)  
**Presented at:** IEEE CS R10 Summer School 2026

---

## Support & Questions

- **Governance questions?** The authority order and action classes are in the Core Components section above
- **Workflow state issues?** Run `python3 aaos.py status` and `python3 aaos.py history`
- **A command was blocked?** It matched `denied_command_patterns` in `aaos/aaos.json`; change it deliberately, with a reason
- **Evidence gaps?** `init` writes `.aaos/TASK.md` and `.aaos/RELEASE.md`; evidence is captured automatically by `check` (artifact, status, exit code, command, SHA-256)

---

**Built for teams and organizations serious about trustworthy AI in production.** 🔐
