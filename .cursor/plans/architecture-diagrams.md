# Company Brain SaaS — Architecture Diagrams

Visual standalone SVGs:
- Layered system architecture: `.cursor/architecture-diagram.svg`
- End-to-end sequential flow: `.cursor/sequence-diagram.svg`

Companion docs:
- Master design plan: `.cursor/plans/company-brain-saas-plan.md`
- Monorepo structure: `.cursor/plans/repo-structure.md`
- Sign-off checklist: `.cursor/plans/sign-off-checklist.md`

---

## 1. Full System Architecture

```mermaid
flowchart TB
  subgraph surfaces [User Surfaces]
    SlackApp["Slack App (Events, Threads, Block Kit)"]
    WebConsole["Next.js Web Control Plane (apps/web)"]
    WhatsApp["WhatsApp Cloud API (Phase 4)"]
  end

  subgraph apiLayer [API Gateway - apps/api]
    FastAPI["FastAPI Gateway (JWT, RBAC, Webhooks, Rate Limit, OpenAPI)"]
  end

  subgraph runtime [Durable Execution - apps/workers and Temporal]
    AgentQ["agent-queue (Interactive Threads)"]
    SyncQ["sync-queue (Ingestion and ACLs)"]
    JobsQ["jobs-queue (Standing Jobs - Phase 3)"]
    AgentRuntime["Agent Runtime (packages/agent: Planner, ZDR LLM, Citations)"]
    PolicyGate["Policy and Approval Gate (Phase 2: Temporal Signals)"]
    Sandbox["Isolated Sandbox (packages/sandbox - Phase 3: E2B/Modal)"]
  end

  subgraph brain [Company Brain - packages/brain and packages/core]
    ACLGuard["Identity Resolver + Channel Guard (user ∩ channel)"]
    Retriever["Hybrid Retriever (Pre-Filter ACL -> pgvector + BM25 + RRF)"]
    PgBrain["PostgreSQL 16 + pgvector + RLS (4 Memory Tiers)"]
    Redis["Redis (Debounce, Rate Limits, Streams)"]
    KmsS3["KMS Envelope Encryption + Tenant S3/R2"]
  end

  subgraph connectors [Hybrid Connectors - packages/connectors]
    NativeConn["Native Connectors (Slack, Google Workspace, Notion, Linear, HubSpot)"]
    ManagedConn["Managed Gateway and Remote MCP (Composio, Nango, MCP - Phase 2)"]
  end

  SlackApp <--> FastAPI
  WebConsole <--> FastAPI
  WhatsApp <--> FastAPI

  FastAPI --> Redis
  FastAPI --> AgentQ
  FastAPI --> SyncQ
  FastAPI --> JobsQ

  AgentQ --> AgentRuntime
  JobsQ --> AgentRuntime
  AgentRuntime --> ACLGuard
  ACLGuard --> Retriever
  Retriever --> PgBrain

  AgentRuntime --> PolicyGate
  AgentRuntime --> Sandbox
  Sandbox --> KmsS3

  PolicyGate -->|"Approval Card / Signal"| FastAPI
  PolicyGate -->|"Approved Writes"| NativeConn
  PolicyGate -->|"Approved Writes"| ManagedConn

  NativeConn -->|"Incremental Sync + ACLs"| SyncQ
  ManagedConn -->|"Long-Tail Sync"| SyncQ
  SyncQ -->|"Normalize, Chunk, Embed, ACL Upsert"| PgBrain
  NativeConn --- KmsS3
```

---

## 2. Monorepo Acyclic Dependency Graph

Enforced by `.cursor/rules/repo-architecture.mdc`: packages never import from `apps/`, and `packages/core` has zero internal workspace dependencies.

```mermaid
flowchart LR
  subgraph apps [Deployable Apps]
    Web["apps/web (Next.js)"]
    API["apps/api (FastAPI)"]
    Workers["apps/workers (Temporal)"]
  end

  subgraph layer2 [Layer 2]
    Agent["packages/agent"]
  end

  subgraph layer1 [Layer 1]
    Brain["packages/brain"]
    Connectors["packages/connectors"]
    Surfaces["packages/surfaces"]
    Sandbox["packages/sandbox"]
  end

  subgraph layer0 [Layer 0]
    Core["packages/core (DB, RLS, KMS, Identity, Storage, Metering)"]
  end

  subgraph gates [CI Gates]
    Evals["evals/ (ACL Leaks 0%, Citations, Action Safety)"]
  end

  API -.->|"just codegen (OpenAPI -> TS)"| Web
  API --> Agent
  API --> Surfaces
  API --> Brain
  API --> Connectors
  API --> Core

  Workers --> Agent
  Workers --> Surfaces
  Workers --> Brain
  Workers --> Connectors
  Workers --> Sandbox
  Workers --> Core

  Agent --> Brain
  Agent --> Connectors
  Agent --> Sandbox
  Agent --> Surfaces
  Agent --> Core

  Brain --> Core
  Connectors --> Core
  Surfaces --> Core
  Sandbox --> Core

  Evals --> Agent
  Evals --> Brain
  Evals --> Core
```

---

## 3. Multiplayer Permission-Aware Retrieval Flow (`user ∩ channel`)

Enforces zero unauthorized leaks before any vector or BM25 scoring executes.

```mermaid
flowchart TD
  Inbound["Slack Thread Mention or Message"] --> Verify["Verify Slack Signature + Fast Ack"]
  Verify --> Debounce["Redis Thread Debounce"]
  Debounce --> Session["Open DB via tenant_session(tenant_id) (RLS Active)"]
  Session --> Resolve["Resolve Canonical Identity (user_identities -> user_id + groups)"]
  Resolve --> ScopeCheck{"Shared Channel or Direct Message?"}

  ScopeCheck -->|"Direct Message"| UserPrincipals["Effective Principals = asking_user + groups"]
  ScopeCheck -->|"Shared Channel"| Intersect["Effective Principals = asking_user ∩ channel_audience"]

  UserPrincipals --> PreFilter["SQL Pre-Filter document_acls BEFORE Ranking"]
  Intersect --> PreFilter

  PreFilter --> Hybrid["Hybrid Search: pgvector + BM25 (tsvector) + RRF + Freshness"]
  Hybrid --> PrivateHit{"Only Private User Docs Match in Shared Channel?"}

  PrivateHit -->|"Yes"| DMRedirect["Decline In-Channel or Redirect Privately via DM"]
  PrivateHit -->|"No"| Synthesize["Generate Cited Answer (claim -> chunk_id / memory_id)"]
  Synthesize --> Conflict{"Do Sources Conflict?"}
  Conflict -->|"Yes"| SurfaceConflict["Show Both Sources + Dates + Save Decision to Brain CTA"]
  Conflict -->|"No"| Reply["Post Cited Block Kit Reply in Slack Thread"]
```

---

## 4. Durable Agent Run & Human-in-the-Loop Approval Sequence

```mermaid
sequenceDiagram
  participant User as Teammate in Slack
  participant API as FastAPI (apps/api)
  participant WF as Temporal AgentRunWorkflow
  participant Brain as Company Brain
  participant Policy as Policy Gate
  participant Tool as External Tool API

  User->>API: Mentions bot in thread
  API->>WF: Start or signal workflow (agent-queue)
  WF->>Brain: Pre-filtered ACL hybrid retrieval + living memory
  Brain-->>WF: Grounded chunks + source links + timestamps
  WF->>Policy: Evaluate proposed tool call risk tier
  alt Risk tier is read or auto-approved draft
    Policy-->>WF: Allow
    WF->>Tool: Execute tool via ToolRegistry
    Tool-->>WF: Tool output
  else Risk tier is write_internal or write_external
    Policy-->>WF: Require human approval
    WF->>API: Persist approval_requests + post Block Kit Approval Card
    API->>User: Render proposed diff with Approve / Edit / Reject
    Note over WF: Workflow sleeps durably (zero worker memory held)
    User->>API: Clicks Approve (Slack or Web Console)
    API->>WF: Send Temporal approval signal
    WF->>Tool: Execute bounded write tool
    Tool-->>WF: Confirmed result
  end
  WF->>API: Persist run_steps + usage_events + post cited reply
  API->>User: Cited answer + optional signed artifact link
```

---

## 5. Multi-Tenant Data Model (PostgreSQL + RLS on `tenant_id`)

```mermaid
erDiagram
  tenants ||--o{ users : has
  tenants ||--o{ workspace_policies : configures
  tenants ||--o{ connector_installations : installs
  tenants ||--o{ documents : owns
  tenants ||--o{ memories : stores
  tenants ||--o{ entities : tracks
  tenants ||--o{ standing_jobs : schedules
  tenants ||--o{ agent_runs : executes
  tenants ||--o{ usage_events : meters

  users ||--o{ user_identities : maps_to
  connector_installations ||--o{ sync_cursors : tracks
  connector_installations ||--o{ documents : ingests
  documents ||--o{ document_chunks : splits_into
  documents ||--o{ document_acls : restricts_with

  entities ||--o{ entity_edges : connects
  standing_jobs ||--o{ agent_runs : triggers
  agent_runs ||--o{ run_steps : logs
  agent_runs ||--o{ approval_requests : pauses_for
  agent_runs ||--o{ artifacts : produces
```
