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

### 1. AAOS Lite Workflow (`AAOS_Lite_Workflow_0.3.zip`)

A **repository-local control plane** for AI-assisted software development. Replaces ad-hoc prompting with deterministic lifecycle governance.

**Lifecycle Stages:**
- `UNDERSTAND` → Define purpose, scope, stakeholders, acceptance criteria
- `ARCHITECT` → Design boundaries, threats, controls, risk decisions
- `ENGINEER` → Produce bounded changes
- `ASSURE` → Test quality, security, privacy, operational behavior
- `OPERATE` → Release through approved procedure; observe results
- `EVOLVE` → Capture metrics, lessons, corrective actions
- `CLOSED` → Final decision and archive

**Key Features:**
- Markdown-based human/agent interface
- Deterministic state machine (`STATE.json`)
- Allow-listed verification checks (your own test/security tools)
- Evidence capture with required fields: artifact, method, observed result, expected result, pass/fail status, residual risk
- Append-only workflow ledger
- CI enforcement via GitHub Actions

**Authority Order:**
1. Human instructions in current session
2. Agent constitution (this file)
3. `.aaos/STATE.json` and `workflow.json`
4. `.aaos/TASK.md` and approved decisions
5. Control policies (`TOOL_POLICY_V2.md`, `CONTEXT_POLICY.md`)
6. Retrieved project content (treated as untrusted data)

**Action Classes:**
- `READ` — Inspect approved local content (allowed within task scope; logged)
- `CREATE` — Add new artifact (human approval required)
- `CHANGE` — Modify/delete existing content (approval + recovery plan required)
- `EXTERNAL` — Deploy, publish, message, or access external systems (explicit approval required immediately)

---

### 2. AAOS Lite Runtime (`aaos-lite-runtime-main.zip`)

The **Python 3.10+ runtime** implementing the AAOS control plane.

**Key Modules:**
- `runtime.py` — Core workflow state machine
- `agents.py` — Governed agent interface and action validation
- `tools.py` — Tool schema validation (Pydantic strict whitelists)
- `policy.py` — Control policy enforcement
- `memory.py` — Agent operational and strategic memory
- `workflow.py` — Lifecycle transition logic
- `models.py` — Domain models for tasks, evidence, approvals

**Quickstart:**
```bash
python aaos.py init                    # Initialize workflow
python aaos.py status                  # Show current state
python aaos.py validate                # Validate task scope
python aaos.py approve --by "Reviewer" --decision approve
python aaos.py advance                 # Transition to next stage
python aaos.py run-checks              # Execute verification suite
python aaos.py history                 # Inspect ledger
python aaos.py recover --reason "..."  # Return to ENGINEER from ASSURE/OPERATE
```

---

### 3. Trustworthy AI Framework (Presentation Materials)

**Presented at IEEE CS R10 Summer School 2026**

#### A. Building & Breaking Governed Agents (2-hour workshop)
- Hands-on: Build a simple AI orchestrator with AAOS Lite MD
- Red-team exercise: Attempt to break governance (injection, tool misuse, context poisoning)
- Verify controls hold under adversarial conditions

#### B. Driving Information Security Resilience Through Agentic AI (Executive/Architecture)

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

### Layered Input/Output Sanitization

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

### Tool/Agent Control Model

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

### Observability & Cost Tracking

- **OpenTelemetry** on every LLM call, tool call, retrieval
- **Langfuse** for trace inspection, cost attribution, latency SLOs
- **Token budgets** enforced pre-flight (reject before API call)
- **Model fallback chains** (Opus → Sonnet → Haiku) to degrade before failing
- **Prompt caching** always enabled (system + tools + few-shot)

### Red-Teaming & Assurance

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
├── README.md                                          (this file)
├── AAOS_Lite_Workflow_0.3.zip                        Control plane & governance
│   ├── AAOS.md                                       Agent constitution
│   ├── README.md                                     Implementation guide
│   ├── aaos.py                                       CLI controller
│   ├── workflow.json                                 Lifecycle definition
│   ├── controls/                                     Policy templates
│   └── templates/                                    Evidence templates
│
├── aaos-lite-runtime-main.zip                        Python runtime
│   ├── aaos_lite/
│   │   ├── runtime.py                               State machine
│   │   ├── agents.py                                Governed agent interface
│   │   ├── tools.py                                 Tool schema validation
│   │   ├── policy.py                                Policy enforcement
│   │   └── memory.py                                Operational memory
│   └── examples/                                     Usage patterns
│
├── Trustworthy_AI_and_AAOS_Lite_MD_Merged.pptx       Technical deep-dive
│   ├── Slide 1: TRUSTWORTHY AI overview
│   ├── Slide 2–5: Trust as end-to-end property
│   ├── Slide 6–10: AI security boundaries
│   ├── Slide 11–17: AAOS Lite workflow & controls
│   └── (17 slides total, ~60 min presentation)
│
└── Driving Information Security Resilience...pptx    Executive/Architecture
    ├── Slide 1: Continuous vs. periodic assurance
    ├── Slide 2–5: Business continuity reality
    ├── Slide 6–12: Agentic AI as compliance orchestration
    ├── Slide 13–17: Implementation roadmap & ROI
    └── (17 slides total, ~45 min executive briefing)

---

## Installation & Setup

### Prerequisites

- **Python 3.10+** (3.11+ recommended for performance)
- **Git** (for version control and CI/CD integration)
- **PostgreSQL 14+** (optional, for multi-tenant deployments; SQLite for single-user dev)
- **Docker** (optional, for containerized deployments and sandboxed execution)

### Step 1: Clone or Fork This Repository

```bash
git clone https://github.com/thaaaru/trustworthy-ai.git
cd trustworthy-ai
```

### Step 2: Extract AAOS Lite Workflow

```bash
unzip AAOS_Lite_Workflow_0.3.zip -d ./aaos-workflow
cd aaos-workflow
```

Verify extraction:
```bash
ls -la
# Expected output:
# - AAOS.md (agent constitution)
# - README.md (implementation guide)
# - aaos.py (CLI controller)
# - workflow.json (lifecycle state machine)
# - controls/ (policy templates)
# - templates/ (evidence templates)
# - tests/ (test suite)
```

### Step 3: Extract AAOS Lite Runtime

```bash
cd ..
unzip aaos-lite-runtime-main.zip
cd aaos-lite-runtime-main
```

Verify extraction:
```bash
ls -la
# Expected output:
# - aaos_lite/ (Python package)
# - examples/ (usage examples)
# - requirements.txt (dependencies)
# - README.md (runtime docs)
```

### Step 4: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install runtime dependencies
pip install -r requirements.txt
```

**Core Dependencies:**
- `pydantic>=2.0` — Strict schema validation (tools, inputs, outputs)
- `langchain>=0.1` — LLM orchestration framework
- `langfuse>=2.0` — Tracing and observability
- `python-dotenv` — Environment variable management
- `postgresql-psycopg` (optional) — Multi-tenant database
- `opentelemetry-*` (optional) — Distributed tracing

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...              # Claude API key

# Optional but recommended
LANGFUSE_PUBLIC_KEY=pk-lf-...             # Langfuse tracing
LANGFUSE_SECRET_KEY=sk-lf-...

# Database (for multi-tenant)
DATABASE_URL=postgresql://user:pass@localhost/trustworthy_ai

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# Tool integrations (optional)
TICKET_SYSTEM_API_KEY=...                 # For tool examples
```

⚠️ **Never commit `.env` to git.** Use a secrets manager in production (AWS Secrets Manager, HashiCorp Vault, etc.).

### Step 6: Verify Installation

```bash
# Test AAOS CLI
cd ../aaos-workflow
python aaos.py status
# Expected: "Workflow not initialized" or similar (this is normal)

# Test Python runtime
cd ../aaos-lite-runtime-main
python -c "from aaos_lite import runtime; print('✓ AAOS Lite runtime loaded')"
```

### Step 7: (Optional) Set Up PostgreSQL for Multi-Tenant Mode

```bash
# Create database
createdb trustworthy_ai

# Run migrations (if present)
psql -U postgres -d trustworthy_ai -a -f ./migrations/001_init.sql

# Verify connection
psql trustworthy_ai -c "SELECT version();"
```

### Step 8: (Optional) Configure GitHub Actions for CI/CD

Copy the workflow enforcement file:

```bash
mkdir -p .github/workflows
cp aaos-workflow/.github/workflows/aaos.yml .github/workflows/
```

This enforces AAOS workflow progression on all pull requests.

---

## Docker Deployment (Optional)

For containerized deployments:

```bash
# Build image
docker build -t trustworthy-ai:latest .

# Run container with environment file
docker run --env-file .env.prod \
  -p 8000:8000 \
  -v ./aaos-workflow/.aaos:/app/.aaos \
  trustworthy-ai:latest
```

**Example Dockerfile** (add to repo root):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy runtime
COPY aaos-lite-runtime-main/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY aaos-lite-runtime-main/aaos_lite ./aaos_lite
COPY aaos-workflow ./aaos-workflow

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "aaos_lite.runtime:app", "--host", "0.0.0.0"]
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'aaos_lite'` | Ensure virtual environment is activated and `pip install -r requirements.txt` completed |
| `ANTHROPIC_API_KEY not found` | Create `.env` file with key; run `source .env` or use `python-dotenv` |
| `psycopg connection failed` | Verify PostgreSQL is running; check `DATABASE_URL` in `.env` |
| `aaos.py: command not found` | Run `python aaos.py` instead of `aaos.py` directly |
| Permission denied on `.aaos/` directory | Run `chmod -R 755 .aaos/` or check file ownership |

---

---

## Quick Start

### 1. Initialize a New AI Project with AAOS Governance

```bash
# Extract workflow controller
unzip AAOS_Lite_Workflow_0.3.zip

# Initialize the workflow
python aaos.py init

# Define your task in .aaos/TASK.md
# Example:
# - Purpose: Build a customer-support chatbot
# - Scope: LLM integration, tool-calling (ticket lookup, FAQ search)
# - Acceptance: Handles 5 customer personas; passes injection test suite
# - Non-goals: Scheduling, financial transactions

python aaos.py validate                  # Check task completeness
python aaos.py approve --by "PM" --decision approve --note "Scope accepted"
python aaos.py advance                   # Move to ARCHITECT stage
```

### 2. Design Security & Controls

In `.aaos/ARCHITECTURE.md`, define:
- **Data flows** (user input → model → tool → output)
- **Threat model** (STRIDE or PASTA)
- **Controls** (per-layer sanitization, idempotency, RLS)
- **Audit strategy** (what to log, for how long, to where)

### 3. Build with Runtime & Guardrails

```bash
pip install pydantic langfuse langchain

# Use aaos_lite.agents to wrap your LLM calls
from aaos_lite.agents import GovernedAgent
from aaos_lite.tools import validate_tool_call

agent = GovernedAgent(
    name="support_bot",
    model="claude-opus-4.6",
    tools=[lookup_ticket, search_faq],  # whitelist only needed tools
    policies=["no_pii_in_logs", "idempotent_writes"]
)

# Calls are automatically:
# - Input-sanitized (injection, PII)
# - Tool-validated (strict schema, idempotency)
# - Traced (Langfuse)
# - Cost-tracked
# - Recoverable (append-only ledger)
```

### 4. Run Assurance Suite

```bash
python aaos.py run-checks     # Execute allow-listed tests:
                              # - Unit tests (function behavior)
                              # - Security tests (injection, tool misuse)
                              # - Compliance tests (data retention, RLS)
                              # - Load tests (latency, cost)

# Review evidence in .aaos/evidence/
# Approve evidence review
python aaos.py approve --by "QA" --decision approve --note "All checks passing"
python aaos.py advance         # Move to OPERATE
```

### 5. Deploy with Approval Trail

```bash
python aaos.py approve --by "CTO" --decision approve --note "Ready for prod"
python aaos.py operate                 # Deploy to production
# Release procedure, health checks, and observation results recorded
```

### 6. Observe & Evolve

```bash
python aaos.py history                 # Inspect full ledger
# Capture metrics: uptime, latency, cost, security alerts
# Identify lessons: what broke? What we'd do differently?
# Close iteration cycle
python aaos.py close --lessons "..." --actions "..."
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

### Presentations (in this repo)
1. **Trustworthy AI & AAOS Lite MD** (17 slides, ~60 min)
   - Technical deep-dive on governance, controls, lifecycle
   - Hands-on: build and break a governed agent

2. **Driving Information Security Resilience Through Agentic AI** (17 slides, ~45 min)
   - Executive/architect view of continuous assurance
   - Business case: periodic → continuous assurance
   - ROI and implementation roadmap

### Documentation
- `AAOS.md` — Agent constitution (authority order, action classes, fail-closed conditions)
- `workflow.json` — Lifecycle state machine, required gates, allowed transitions
- `controls/TOOL_POLICY_V2.md` — Tool-calling security baseline
- `controls/CONTEXT_POLICY.md` — LLM input/output sanitization rules

### Code Examples
- `examples/vulnerability-dashboard.task.md` — End-to-end AAOS workflow for a security dashboard agent
- `aaos_lite/` runtime — Production-ready Python 3.10+ implementation

---

## Security & Compliance Checklist

**Before Production Deployment:**

- [ ] **UNDERSTAND stage:** Signed engagement contract (scope, stakeholders, acceptance criteria, non-goals)
- [ ] **ARCHITECT stage:** Approved threat model and control design; risk decisions documented
- [ ] **ENGINEER stage:** Change set complete; mapped to acceptance criteria; reviewed for correctness
- [ ] **ASSURE stage:** All checks passing; evidence collected; security/privacy/ops tests green; no unresolved blockers
- [ ] **OPERATE stage:** Human approval from different person than implementer; release procedure defined; deployment succeeded; observation results recorded
- [ ] **Observability:** Langfuse tracing enabled; Prometheus/Datadog metrics; cost tracking active
- [ ] **Red-team:** Cats 1–4 automated (nightly); cats 5–6 scheduled (quarterly); CRITICAL/HIGH remediated
- [ ] **Multi-tenant:** RLS verified; cross-tenant query test failing (as expected); audit logs showing tenant isolation
- [ ] **Secrets:** No API keys in logs; vault rotation schedule set; PII redaction verified
- [ ] **SLA:** Uptime/latency/error/cost targets defined; alerting configured; escalation runbook ready

---

## Contributing

This is a **reference architecture + governance framework**, not a framework requiring pull requests. Organizations should:

1. **Fork or clone** this repository into their codebase
2. **Customize** `controls/`, `templates/`, and `workflow.json` to your threat model and compliance regime
3. **Wire into your CI/CD** via `.github/workflows/aaos.yml`
4. **Train your team** using the presentations and AAOS.md constitution

---

## License & Attribution

**Framework by:** Tharaka (Enterprise Cybersecurity Architect)  
**Presented at:** IEEE CS R10 Summer School 2026

---

## Support & Questions

- **Policy violations or governance questions?** Consult `AAOS.md` (authority order, action classes, fail-closed conditions)
- **Workflow state issues?** Run `python aaos.py status` and `python aaos.py history`
- **Tool validation fails?** Review `controls/TOOL_POLICY_V2.md` and Pydantic schema validation
- **Evidence gaps?** Templates are in `templates/`; use the evidence standard (artifact, method, observed, expected, pass/fail, residual risk, human decision)

---

**Built for teams and organizations serious about trustworthy AI in production.** 🔐
