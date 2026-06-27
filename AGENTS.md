# AgentOS - Multi-Agent Operating System

AgentOS is a multi-agent framework integrated inside the `agents` application to automate code generation, schema changes, and curriculum diagnostics.

---

## 1. System Topology

AgentOS structures agents into three distinct, hierarchical layers:

```text
       [User Input Intent]
                ↓
    ================================================
    LAYER 1: ORCHESTRATION (Orchestrator, PM)
    ================================================
         /      |       \
        /       |        \  (Assign worker tasks)
       /        |         \
  [Worker]   [Worker]   [Worker]
    ================================================
    LAYER 2: WORKERS (DB, API, Auth, AI, Test, Doc, Review)
    ================================================
         \      |        /
          \     |       /   (Verify executions)
           \    |      /
    ================================================
    LAYER 3: INTELLIGENCE (Monitoring & Telemetry) (Read-Only)
    ================================================
```

---

## 2. Agent Responsibilities

### Layer 1: Orchestration
- **Orchestrator Agent**: Parses the user's initial prompt, analyzes intent, decomposes complex requests into standard workflows, and maps capabilities to steps.
- **Project Manager Agent**: Manages execution state, resolves task dependency boundaries, assigns workers to steps, and aggregates logs and outputs into unified reports.

### Layer 2: Workers
- **Database Architect Agent**: Generates models, indexes, relationships, and migration configurations.
- **Backend API Agent**: Creates standard Django REST Views, Serializers, Validation schemes, and URL endpoints.
- **Authentication Agent**: Integrates role verification filters, scopes checking, and token validation.
- **Storage Agent**: Manages assets upload setups, S3 buckets, and signed files access routines.
- **AI Learning Agent**: Generates timetables, daily review logs, semester calendars, and course plan paths.
- **Testing Agent**: Writes APITests, unit assertions, performance tests, and mock request simulations.
- **Documentation Agent**: Automatically writes developer spec guides, README files, and OpenAPI Swagger references.
- **Review Agent**: Performs security scans, checks lint parameters, and flags code duplications.

### Layer 3: Intelligence (Read-Only)
- **Monitoring & Intelligence Agent**: Continuously audits system performance metrics, active connections, CPU/Memory levels, storage sizes, and student experience scores. **Strictly read-only; never writes to business data.**

---

## 3. Communication Rules & Standards
- **Isolation**: Worker agents never communicate directly with other workers. All task updates, inputs, and outputs must be routed through the Project Manager.
- **State Auditing**: Every agent run writes an `AgentExecutionLog` capturing token overhead and latencies.
- **Fallback safety**: When prompts or local configurations are missing, executors fallback to local defaults to guarantee system uptime.
