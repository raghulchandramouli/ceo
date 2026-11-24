# Monorepo Structure Specification

Polyglot monorepo: **`uv` workspace** (Python backend, Temporal workers, shared libraries, evals) + **`pnpm`** (Next.js App Router web console).

```text
ceo/
├── pyproject.toml                       # Root uv workspace (shared ruff, pyright, pytest, dependency groups)
├── uv.lock
├── package.json                         # Root scripts (codegen, lint, web shortcuts)
├── justfile                             # Single commands: `just up`, `just migrate`, `just dev`, `just eval`, `just codegen`
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml                       # Lint, typecheck, unit/integration tests, OpenAPI drift check
│       └── eval-gate.yml                # Hard-gated ACL leak (0%), citation & action-safety evals on prompt/model PRs
│
├── apps/
│   ├── web/                             # Next.js App Router Control Plane (TypeScript, Tailwind, shadcn/ui)
│   │   ├── package.json
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (auth)/              # Login, WorkOS/Clerk callbacks, invite acceptance
│   │       │   ├── (onboarding)/        # Workspace creation, Slack install, first connector wizard
│   │       │   └── (dashboard)/
│   │       │       ├── brain/           # Knowledge explorer, ACL-aware search tester, Living Memory editor
│   │       │       ├── connectors/      # Native OAuth setup, Composio/Nango/MCP connections, sync health
│   │       │       ├── jobs/            # Standing Responsibilities studio (brief, schedule, owner, last_run_state)
│   │       │       ├── approvals/       # Pending action diffs + Approve/Reject queue
│   │       │       ├── runs/            # Run Inspector & Audit Log (steps, retrieved chunks, artifacts)
│   │       │       ├── policies/        # Risk tier rules (read/draft/write_internal/write_external), RBAC
│   │       │       ├── billing/         # Usage metering, monthly spend caps, Stripe portal
│   │       │       └── settings/        # Tenant settings, user identity mappings, security
│   │       ├── components/
│   │       │   ├── ui/                  # shadcn/ui primitives
│   │       │   ├── brain/               # Citation cards, conflict-resolution widgets, memory rows
│   │       │   ├── approvals/           # Action diff viewer, policy rule builder
│   │       │   └── runs/                # Step timeline, artifact previewer
│   │       └── lib/
│   │           ├── api-client/          # Auto-generated TypeScript client from FastAPI OpenAPI schema
│   │           └── auth.ts
│   │
│   ├── api/                             # FastAPI Gateway (HTTP API, Auth, Webhooks, Signals)
│   │   ├── pyproject.toml
│   │   └── src/ceo_api/
│   │       ├── main.py                  # App factory, lifespan, OpenAPI export
│   │       ├── config.py
│   │       ├── deps.py                  # JWT auth, RBAC guards, tenant-scoped DB session (RLS), Temporal/Redis clients
│   │       ├── middleware/
│   │       │   ├── tenant_context.py    # Ensures every request binds tenant_id cleanly
│   │       │   ├── rate_limit.py        # Redis sliding-window rate limiter
│   │       │   └── webhook_verify.py    # Slack, WhatsApp, Stripe signature verification
│   │       ├── routers/                 # REST endpoints backing apps/web
│   │       │   ├── tenants.py
│   │       │   ├── users.py             # Users, RBAC, canonical user_identities management
│   │       │   ├── connectors.py        # OAuth start/callback, managed connector sessions, manual resync
│   │       │   ├── brain.py             # Search, docs/ACLs inspection, memories CRUD, conflict decisions
│   │       │   ├── jobs.py              # Standing Responsibilities CRUD + Temporal Schedule sync
│   │       │   ├── approvals.py         # List/resolve approvals -> sends Temporal approval signal
│   │       │   ├── runs.py              # Execution traces, run_steps, signed artifact download URLs
│   │       │   ├── policies.py          # Workspace approval policies & spend caps
│   │       │   └── billing.py           # Usage summaries & Stripe checkout/portal
│   │       └── webhooks/                # External event ingress (ack fast -> debounce/dispatch to Temporal)
│   │           ├── slack.py             # Events API, Interactivity (Block Kit Approve/Save-to-Brain), Commands
│   │           ├── whatsapp.py          # WhatsApp Cloud API inbound messages & status webhooks
│   │           ├── connectors.py        # Incremental push webhooks (Google, Notion, Linear, HubSpot, Nango)
│   │           └── stripe.py            # Subscription & usage-billing webhooks
│   │
│   └── workers/                         # Temporal Python Workers (split by task queue for isolation)
│       ├── pyproject.toml
│       └── src/ceo_workers/
│           ├── entrypoint.py            # Runs `agent-queue`, `sync-queue`, `jobs-queue` (all-in-one locally, split in prod)
│           ├── workflows/
│           │   ├── agent_run.py         # Interactive thread workflow + Temporal Signal wait for approvals
│           │   ├── standing_job.py      # Temporal-scheduled workflow with cross-run episodic state
│           │   ├── connector_sync.py    # Backfill, incremental cursor sync, webhook delta sync, ACL mirror
│           │   └── maintenance.py       # Async entity extraction, memory decay/conflicts, Stripe usage rollup
│           └── activities/
│               ├── retrieval.py         # Calls packages/brain with user ∩ channel ACL guard
│               ├── agent.py             # Runs bounded LLM planner/tool loop
│               ├── policy_gate.py       # Evaluates risk policy, persists approval_requests, posts card
│               ├── tool_exec.py         # Executes approved reads/writes via packages/connectors
│               ├── sandbox.py           # Generates PDF/XLSX/charts via packages/sandbox -> S3/R2
│               ├── ingestion.py         # Fetch -> normalize -> chunk -> embed -> ACL upsert -> entity extract
│               ├── surfaces.py          # Posts live status, cited replies, DM redirects (Slack/WhatsApp)
│               └── metering.py          # Records usage_events & enforces tenant budget caps
│
├── packages/                            # Shared Python libraries (strict acyclic dependency order)
│   ├── core/                            # Layer 0: DB, RLS, KMS, Identity, Storage, Metering, Telemetry
│   │   ├── pyproject.toml
│   │   └── src/ceo_core/
│   │       ├── db/
│   │       │   ├── session.py           # Async engine + `tenant_session()` enforcing `SET LOCAL app.tenant_id`
│   │       │   ├── models/              # SQLAlchemy models grouped by domain:
│   │       │   │   ├── tenancy.py       # tenants, users, user_identities, workspace_policies
│   │       │   │   ├── connectors.py    # connector_installations, sync_cursors
│   │       │   │   ├── brain.py         # documents, document_chunks (pgvector+tsvector), document_acls
│   │       │   │   ├── memory.py        # entities, entity_edges, memories
│   │       │   │   ├── execution.py     # standing_jobs, agent_runs, run_steps, approval_requests, artifacts
│   │       │   │   └── billing.py       # usage_events
│   │       │   └── migrations/          # Alembic migrations (incl. PostgreSQL RLS policies & pgvector/pg_trgm indexes)
│   │       ├── security/
│   │       │   ├── kms.py               # Envelope encryption (AWS/GCP KMS + per-tenant DEKs for OAuth tokens)
│   │       │   └── rbac.py              # Role permissions & tenant policy schemas
│   │       ├── identity/
│   │       │   └── resolver.py          # Maps Slack/Google/Notion/Linear/WhatsApp IDs -> canonical user_id + groups
│   │       ├── storage/
│   │       │   └── artifacts.py         # Tenant-prefixed S3/R2 uploads + short-lived signed URLs
│   │       ├── metering/
│   │       │   ├── tracker.py           # LLM token, sandbox-second, and connector-call event emitter
│   │       │   ├── budgets.py           # Monthly spend cap enforcement
│   │       │   └── stripe_sync.py       # Batched Stripe meter reporting
│   │       └── telemetry.py             # Structured logging + OpenTelemetry
│   │
│   ├── brain/                           # Layer 1: 4-Tier Company Brain & Permission-Aware Retrieval
│   │   ├── pyproject.toml
│   │   └── src/ceo_brain/
│   │       ├── acl/
│   │       │   ├── filter.py            # Pre-filter SQL ACL clause builder (runs BEFORE vector/BM25 ranking)
│   │       │   └── channel_guard.py     # Multiplayer channel-intersection rule (user ∩ channel audience, DM fallback)
│   │       ├── ingestion/
│   │       │   ├── normalizer.py        # Canonical doc normalization & source-authority ranking
│   │       │   ├── chunker.py           # Structure-aware chunking (Markdown, Slack threads, emails, tickets)
│   │       │   └── embedder.py          # Batch embedding client + content-hash deduplication
│   │       ├── retrieval/
│   │       │   ├── hybrid.py            # Tier 1: pgvector + BM25 (tsvector) + RRF + freshness decay
│   │       │   └── reranker.py          # Cross-encoder / LLM reranking with source priority weights
│   │       ├── graph/
│   │       │   ├── extractor.py         # Tier 2: Async entity & relationship extraction
│   │       │   └── query.py             # Fast relational lookups ("who owns Acme's renewal?")
│   │       ├── memory/
│   │       │   ├── store.py             # Tier 3: Teachable living memory (teach, pin, expire, review)
│   │       │   └── conflicts.py         # Detects contradicting docs/decisions & drafts resolution prompts
│   │       ├── episodic/
│   │       │   └── state.py             # Tier 4: Run summaries, open loops, standing-job `last_run_state`
│   │       └── citations/
│   │           └── verifier.py          # Claim -> chunk_id/memory_id binding & citation formatting
│   │
│   ├── connectors/                      # Layer 1: Unified Tool Registry + Native & Managed Connectors
│   │   ├── pyproject.toml
│   │   └── src/ceo_connectors/
│   │       ├── base.py                  # BaseConnector, NormalizedDocument, DocumentACL, SyncCursor
│   │       ├── registry.py              # Unified ToolRegistry with risk tiers (read|draft|write_internal|write_external)
│   │       ├── native/                  # Tier 1 first-party connectors (each: oauth, sync, acls, tools, webhooks)
│   │       │   ├── slack/
│   │       │   ├── google_workspace/    # Drive, Gmail, Calendar
│   │       │   ├── notion/
│   │       │   ├── linear/
│   │       │   └── hubspot/
│   │       └── managed/                 # Tier 2 long-tail aggregator & remote MCP
│   │           ├── composio.py
│   │           ├── nango.py
│   │           └── mcp_client.py        # Customer-supplied remote MCP server adapter
│   │
│   ├── surfaces/                        # Layer 1: Chat Platform Clients & Message Renderers (shared by api + workers)
│   │   ├── pyproject.toml
│   │   └── src/ceo_surfaces/
│   │       ├── slack/
│   │       │   ├── client.py            # Workspace-scoped Slack WebClient + thread context fetcher
│   │       │   ├── blocks.py            # Block Kit builders (Approval Cards, Cited Answers, Conflict "Save" CTA)
│   │       │   └── status.py            # Live streaming progress updates in Slack threads
│   │       └── whatsapp/
│   │           ├── client.py            # WhatsApp Cloud API sender/media helper
│   │           └── formatter.py         # Citation & approval message formatting for WhatsApp
│   │
│   ├── sandbox/                         # Layer 1: Ephemeral Code Execution & Deliverable Generation
│   │   ├── pyproject.toml
│   │   └── src/ceo_sandbox/
│   │       ├── runner.py                # Unified SandboxRunner interface + timeout/memory guards
│   │       ├── providers/
│   │       │   ├── e2b.py
│   │       │   └── modal.py
│   │       └── templates/               # Artifact generators (WeasyPrint PDF, openpyxl XLSX, charts, HTML reports)
│   │
│   └── agent/                           # Layer 2: Agent Runtime, Risk Policy Engine & Prompts
│       ├── pyproject.toml
│       └── src/ceo_agent/
│           ├── runtime.py               # Bounded planner/executor loop, step budgets, structured citation output
│           ├── policy.py                # Risk Policy Engine (tool risk tier + tenant policy -> auto | approve | deny)
│           ├── llm/
│           │   ├── client.py            # ZDR enterprise LLM adapters (Anthropic / OpenAI) + token accounting
│           │   └── router.py            # Model routing (fast extraction vs. deep reasoning)
│           └── prompts/                 # Versioned Jinja/Markdown prompt templates (agent, standing jobs, conflicts)
│
├── evals/                               # Automated Quality & Security Evaluation Suite (CI-gated)
│   ├── pyproject.toml
│   ├── datasets/                        # Synthetic multi-tenant workspaces (docs, ACLs, memories, threads)
│   ├── suites/
│   │   ├── acl_leaks/                   # HARD GATE (0% leaks): cross-tenant, private-in-public-channel, revoked ACLs
│   │   ├── citations/                   # Groundedness, claim-to-chunk provenance, freshness conflict resolution
│   │   └── action_safety/               # Verifies no write tool can bypass the Policy Gate
│   └── runner.py                        # Local + CI runner with pass/fail thresholds
│
├── infra/
│   ├── docker/
│   │   ├── docker-compose.yml           # Postgres 16 (pgvector + pg_trgm), Redis, Temporal server + UI, MinIO (local S3)
│   │   ├── api.Dockerfile
│   │   ├── workers.Dockerfile
│   │   └── web.Dockerfile
│   └── terraform/                       # Production IaC (VPC, RDS/Aurora, Redis, KMS, S3/R2, ECS/GKE, Temporal)
│       ├── modules/
│       └── environments/
│           ├── staging/
│           └── prod/
│
└── docs/
    ├── architecture/                    # ADRs (RLS strategy, ACL intersection model, Temporal queue topology)
    └── compliance/                      # Slack App Directory, Google CASA Tier 2, SOC 2 Type I checklists & evidence
```

## Key Architectural Rules

1. **Strict Acyclic Package Dependency Graph**:
   `apps/{api,workers}` → `packages/agent` → `packages/{brain,connectors,sandbox,surfaces}` → `packages/core`.
   Packages never import from `apps/`.
2. **Isolated Temporal Task Queues**:
   `agent-queue` (interactive threads), `sync-queue` (ingestion/backfills), `jobs-queue` (scheduled Standing Responsibilities).
3. **Single Source of Truth for API Types**:
   FastAPI exports OpenAPI → generated TypeScript client in `apps/web/src/lib/api-client/` via `just codegen`.
4. **Phased Module Activation**:
   - **Phase 1**: `apps/{api,workers,web}`, `packages/{core,brain,surfaces/slack,connectors/native/{slack,google_workspace,notion},agent}`, `evals/suites/acl_leaks`, `infra/docker`.
   - **Phase 2**: `packages/brain/memory`, `packages/connectors/managed`, Temporal approval signals + Slack Block Kit cards.
   - **Phase 3**: `apps/workers/workflows/standing_job.py`, `packages/sandbox`, `packages/core/metering` + Stripe, Run Inspector UI.
   - **Phase 4**: `packages/surfaces/whatsapp`, `packages/brain/graph`, `packages/connectors/native/{linear,hubspot}`, `infra/terraform`.
