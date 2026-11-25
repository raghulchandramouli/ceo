# Company Brain SaaS — Build & Launch Sign-Off Checklist

Reference documents:
- Master design plan: `.cursor/plans/company-brain-saas-plan.md`
- Monorepo layout spec: `.cursor/plans/repo-structure.md`
- Security & ACL invariants: `.cursor/rules/security-acl-invariants.mdc`
- Architecture boundaries: `.cursor/rules/repo-architecture.mdc`

Check off each item (`- [x]`) only after code is merged and verified. Complete the **Phase Sign-Off** block at the end of each phase before starting the next phase.

---

## Cross-Cutting Invariants (Continuous Gate Across All Phases)

- [x] Acyclic package dependency graph enforced (`apps/{api,workers} -> packages/agent -> packages/{brain,connectors,sandbox,surfaces} -> packages/core`; `packages/` never imports `apps/`)
- [x] Every tenant-owned PostgreSQL table carries `tenant_id` with Row-Level Security (RLS) policies in Alembic migrations
- [x] All DB queries execute inside `tenant_session(tenant_id)` (`SET LOCAL app.tenant_id = :tenant_id`)
- [x] All third-party OAuth tokens encrypted via KMS envelope encryption (`ceo_core.security.kms`) with per-tenant DEKs; zero plaintext token logs
- [x] All LLM traffic routed exclusively through ZDR-configured LangChain `BaseChatModel` instances from `ceo_agent.llm.client` (with external LangSmith tracing disabled and `ceo_agent.callbacks` metering attached)
- [x] FastAPI OpenAPI schema and generated TypeScript client (`apps/web/src/lib/api-client/`) pass CI drift check (`just codegen`)
- [x] `evals/suites/acl_leaks/` passes CI with **0% leaks** (hard merge gate)

---

## Phase 0 — Design Partner & Wedge (Week 1)

- [ ] Select and document 1 wedge recurring workflow (e.g., *Founder/Ops Weekly Operating Brief* or *Sales Account Research & Follow-up*) with authoritative sources, accountable owner, approval points, and measurable outcome
- [ ] Recruit 3–5 design partner teams willing to install the Slack app and connect core tools
- [ ] Document ADRs in `docs/architecture/` (RLS strategy, `user ∩ channel` ACL intersection model, Temporal queue topology)

**Phase 0 Sign-Off**
- Owner: `__________________` | Reviewer: `__________________` | Date: `__________`

---

## Phase 1 — Foundation & Core Brain MVP (Weeks 2–5)

### Monorepo & Local Infrastructure
- [ ] Root `pyproject.toml` (`uv` workspace with `ruff`, `pyright`, `pytest`), `package.json` (`pnpm`), `.env.example`, and `justfile` (`up`, `migrate`, `dev`, `eval`, `codegen`)
- [ ] Local stack in `infra/docker/docker-compose.yml` (PostgreSQL 16 with `pgvector` + `pg_trgm`, Redis, Temporal server + UI, MinIO) boots cleanly with `just up`
- [ ] GitHub Actions workflows in `.github/workflows/ci.yml` and `.github/workflows/eval-gate.yml` active on PRs

### Core Database, Security & Identity (`packages/core`)
- [ ] SQLAlchemy async models & Alembic migrations for Phase 1 tables (`tenants`, `users`, `user_identities`, `workspace_policies`, `connector_installations`, `sync_cursors`, `documents`, `document_chunks`, `document_acls`, `agent_runs`, `run_steps`)
- [ ] PostgreSQL RLS policies active and integration-tested for cross-tenant isolation
- [ ] KMS envelope encryption helper (`packages/core/src/ceo_core/security/kms.py`) implemented and tested
- [ ] Canonical identity resolver (`packages/core/src/ceo_core/identity/resolver.py`) maps Slack/Google/Notion IDs to a single `user_id` + group principals

### Permission-Aware Retrieval & Citations (`packages/brain`)
- [ ] SQL pre-filter ACL builder (`acl/filter.py`) enforces `document_acls` *before* vector/BM25 ranking
- [ ] Multiplayer channel-intersection guard (`acl/channel_guard.py`) enforces `asking_user ∩ channel_audience` with DM redirect/decline for private context
- [ ] Ingestion pipeline: normalizer, structure-aware chunker, content-hash deduplicated batch embedder
- [ ] Hybrid retrieval (`retrieval/hybrid.py` + `reranker.py`): `pgvector` + BM25 (`tsvector`) + RRF + freshness decay + canonical source weighting
- [ ] Citation verifier (`citations/verifier.py`) binds every factual claim to `chunk_id` with clickable source link and last-updated timestamp

### Slack Surface & Native Connectors (`packages/surfaces/slack`, `packages/connectors/native`)
- [ ] Slack Events API webhook handler (`apps/api/src/ceo_api/webhooks/slack.py`) verifies signatures, acknowledges fast, debounces via Redis, and dispatches to Temporal
- [ ] Slack thread experience (`packages/surfaces/slack/`): thread context fetching, live streaming progress updates, cited Block Kit replies
- [ ] Native Slack connector (channel/thread history sync + private/public channel ACL mirror)
- [ ] Native Google Workspace connector (Drive incremental sync + file/folder ACL mirror + OAuth v2)
- [ ] Native Notion connector (page/database incremental sync + workspace/page ACL mirror + OAuth)

### API, Workers, LangChain Runtime & Web Onboarding (`apps/api`, `apps/workers`, `packages/agent`, `apps/web`)
- [ ] FastAPI gateway with JWT auth (WorkOS/Clerk), RBAC guards, tenant context middleware, and rate limiting
- [ ] Temporal workers split cleanly across `agent-queue` and `sync-queue` with strictly deterministic workflows and all DB/HTTP/LangChain/LLM I/O isolated in activities
- [ ] LangChain agent runtime (`packages/agent`) implemented inside Temporal activities: ZDR `BaseChatModel` factory (`llm/client.py`), ACL-scoped `BaseRetriever` (`retriever.py`), `with_structured_output()` citation schemas (`runtime.py`), and `AsyncCallbackHandler` metering/tracing (`callbacks.py`)
- [ ] Next.js Web Control Plane `(auth)`, `(onboarding)`, `/connectors` (OAuth install + sync status), and `/brain` (ACL-aware search tester)

### Phase 1 Exit Verification
- [ ] `evals/suites/acl_leaks/` passes with **0% leaks** (cross-tenant, private-doc-in-public-channel, and revoked-ACL scenarios)
- [ ] `evals/suites/citations/` passes groundedness and freshness verification thresholds
- [ ] End-to-end cited answer verified inside a live Slack thread across Slack + Drive + Notion sources

**Phase 1 Sign-Off**
- Owner: `__________________` | Reviewer: `__________________` | Date: `__________` | Tag/Commit: `__________`

---

## Phase 2 — Living Memory, Actions & Approvals (Weeks 6–9)

### Living Workspace Memory (`packages/brain/memory`)
- [ ] `memories` schema & store (`active`, `needs_review`, `archived`) with provenance, confidence, pinning, and expiry
- [ ] Teach-from-Slack flow captures team rules, tone, acronyms, and program notes into living memory
- [ ] Conflict detector (`memory/conflicts.py`) surfaces contradicting sources with dates and renders one-click "Save decision to Company Brain" Slack Block Kit CTA
- [ ] Web Console `/brain` Living Memory viewer/editor (create, edit, pin, approve, archive)

### Policy Gate & Human-in-the-Loop Approvals (`packages/agent`, `apps/workers`)
- [ ] Every connector tool declares a risk tier (`read`, `draft`, `write_internal`, `write_external`) in `ToolRegistry` and is exposed to LangChain via `packages/agent/src/ceo_agent/tools.py` (`StructuredTool`) without permitting unapproved write execution
- [ ] Risk Policy Engine (`packages/agent/src/ceo_agent/policy.py`) evaluates proposed LangChain tool calls against `workspace_policies` (`auto` | `approve` | `deny`)
- [ ] `AgentRunWorkflow` persists `approval_requests`, posts Slack Block Kit Approval Cards (showing proposed action diff + Approve/Edit/Reject), and waits durably on Temporal Signals with expiry/timeout
- [ ] Web Console `/approvals` queue and `/policies` rule builder connected via OpenAPI client

### Managed Connectors & Remote MCP (`packages/connectors/managed`)
- [ ] Managed connector gateway adapter (Composio / Nango / Pipedream Connect) integrated behind `ToolRegistry`
- [ ] Remote MCP client adapter (`mcp_client.py`) supports tenant-configured MCP servers with Policy Gate enforcement
- [ ] Web Console `/connectors` supports managed connector OAuth flows and connection health monitoring

### Phase 2 Exit Verification
- [ ] `evals/suites/action_safety/` passes (0 write/external actions bypass Policy Gate)
- [ ] End-to-end write action pauses in Temporal, displays diff in Slack and Web Console, resumes on signal only after human approval, and records full audit trace in `approval_requests` + `run_steps`
- [ ] Conflict resolution flow verified: conflicting docs surfaced with dates and human decision persisted to `memories`

**Phase 2 Sign-Off**
- Owner: `__________________` | Reviewer: `__________________` | Date: `__________` | Tag/Commit: `__________`

---

## Phase 3 — Standing Responsibilities, Deliverables & Billing (Weeks 10–13)

### Standing Responsibilities (`apps/workers`, `packages/brain/episodic`)
- [ ] `standing_jobs` schema and CRUD API (`apps/api/src/ceo_api/routers/jobs.py`) synced to Temporal Schedules
- [ ] Isolated `jobs-queue` worker running `workflows/standing_job.py`
- [ ] Cross-run episodic state (`packages/brain/src/ceo_brain/episodic/state.py`) persists `last_run_state` (open items, blockers, owners) between cycles
- [ ] Web Console `/jobs` Standing Responsibilities studio (brief, cadence, target channel, accountable human owner, run history, state preview)

### Sandboxed Deliverables (`packages/sandbox`, `packages/core/storage`)
- [ ] Ephemeral sandbox runner (`E2B` or `Modal`) with strict CPU, memory, network, and timeout guards
- [ ] Deliverable templates generating verified PDFs (WeasyPrint/Playwright), Excel spreadsheets (`openpyxl`), charts, and static HTML reports
- [ ] Artifact storage (`ceo_core/storage/artifacts.py`) uploads exclusively to tenant-prefixed S3/R2 paths and exposes short-lived signed URLs only
- [ ] Artifacts attach cleanly in Slack threads and preview/download in Web Console

### Run Inspector & Usage-Based Billing (`packages/core/metering`, `apps/web`)
- [ ] Web Console `/runs` Run Inspector & Audit Log (step timeline, retrieved chunks with citations, approval records, generated artifacts)
- [ ] Metering tracker (`ceo_core/metering/tracker.py`) logs `usage_events` for LLM tokens, sandbox seconds, and metered connector calls
- [ ] Monthly tenant spend caps (`ceo_core/metering/budgets.py`) enforce budget ceilings before launching new runs and alert workspace admins
- [ ] Stripe usage-based meter sync (`stripe_sync.py`), webhook handler (`webhooks/stripe.py`), and Web Console `/billing` dashboard & portal

### Phase 3 Exit Verification
- [ ] Standing job executes 2 consecutive cycles and automatically revisits unresolved blockers from Cycle 1 in Cycle 2
- [ ] Sandboxed PDF and XLSX artifacts generate cleanly, download via short-lived signed URL, and reject cross-tenant access
- [ ] Exceeding a tenant monthly spend cap cleanly blocks new billable runs and alerts the workspace admin

**Phase 3 Sign-Off**
- Owner: `__________________` | Reviewer: `__________________` | Date: `__________` | Tag/Commit: `__________`

---

## Phase 4 — Scale, WhatsApp & Enterprise Trust (Months 4–6)

### WhatsApp Surface (`packages/surfaces/whatsapp`)
- [ ] WhatsApp Business Cloud API webhook handler (`apps/api/src/ceo_api/webhooks/whatsapp.py`) with signature verification
- [ ] WhatsApp client & formatter supporting group/direct threads, canonical phone-to-user identity resolution, citations, and approval prompts

### Entity Graph & Additional Native Connectors
- [ ] Async entity & relationship extraction (`packages/brain/src/ceo_brain/graph/`) populating `entities` and `entity_edges`
- [ ] Graph query path integrated into retrieval for owner/account/decision lookups
- [ ] Native Linear connector (issues, projects, webhooks, ACLs)
- [ ] Native HubSpot connector (accounts, deals, contacts, notes, webhooks, ACLs)

### Production Infrastructure & Compliance (`infra/terraform`, `docs/compliance`)
- [ ] Production Terraform IaC (`infra/terraform/environments/{staging,prod}`) provisioning VPC, RDS/Aurora (Postgres + `pgvector`), Redis, KMS, S3/R2, Temporal, and isolated worker deployments (`agent-queue`, `sync-queue`, `jobs-queue`)
- [ ] Observability live (structured logs, OpenTelemetry traces, queue lag alerts, sync failure alerts, LLM error/latency dashboards)
- [ ] Slack App Directory review submitted and approved
- [ ] Google Workspace CASA Tier 2 assessment completed (if using restricted Gmail/Drive scopes)
- [ ] SOC 2 Type I readiness completed (Vanta/Drata controls mapped to `run_steps`, `approval_requests`, RLS, and KMS)

### Phase 4 Exit Verification
- [ ] Full eval suite (`acl_leaks` = 0%, `citations`, `action_safety`) green against staging environment
- [ ] Disaster recovery drill passed (DB restore, KMS key rotation verification, Temporal worker failover)
- [ ] Compliance evidence packages archived in `docs/compliance/`

**Phase 4 Sign-Off**
- Owner: `__________________` | Reviewer: `__________________` | Date: `__________` | Tag/Commit: `__________`

---

## Final Production Launch Sign-Off

Sign off only when all phases above and all release gates are complete:

- [ ] **Architecture & Reliability**: Acyclic boundaries intact, isolated Temporal queues load-tested, staging/prod Terraform applied cleanly — Signed: `__________________` Date: `__________`
- [ ] **Security & Multi-Tenant Isolation**: RLS audited across all tables, KMS encryption verified, ZDR LLM contracts active, **0% ACL leaks** in CI — Signed: `__________________` Date: `__________`
- [ ] **Product & Quality**: Citations, conflict resolution, human approvals, Standing Jobs, and deliverables validated with design partners — Signed: `__________________` Date: `__________`
- [ ] **Billing & Compliance**: Stripe usage metering & budget caps verified end-to-end; Slack Marketplace, CASA Tier 2, and SOC 2 evidence in place — Signed: `__________________` Date: `__________`
