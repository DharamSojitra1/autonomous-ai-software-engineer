# Implementation Blueprint --- Autonomous AI Software Engineer

> **Status: Planning only.** This document describes proposed contracts
> and tasks. It does not claim that any feature has been implemented.
> Confirm proposed defaults in `DECISIONS.md` before coding.

## 1. What we are building

An AI software-engineering assistant that accepts a small Python
repository and a developer task, investigates the code with read-only
tools, proposes a minimal patch in a disposable copy, runs tests in an
isolated sandbox, shows the diff and evidence, and applies changes only
after explicit human approval. A later phase can open a GitHub pull
request after a separate approval.

### MVP user flow

1.  Upload a ZIP containing a Python repository.
2.  Validate and safely extract it into a managed workspace.
3.  Enter a task, for example: "Fix the pagination off-by-one error and
    add a regression test."
4.  The agent plans a bounded investigation and uses read-only tools.
5.  The report shows findings with file/line evidence, separating
    **verified** facts from **hypotheses**.
6.  The agent proposes a minimal patch and regression test.
7.  Apply the proposal to a scratch copy only.
8.  Run baseline and patched tests in a restricted sandbox.
9.  Show the diff, test outcomes, and any uncertainty.
10. User approves or rejects the exact diff. Approval is tied to a
    server-generated diff hash and workspace fingerprint.
11. Only an approved, unchanged diff can be applied to the managed
    workspace.
12. Persist run status, results, and an audit event.

### MVP non-goals

-   Supporting all languages and test runners.
-   Arbitrary shell access.
-   Automatic merge or deployment.
-   Letting the LLM write directly to the original workspace.
-   Code RAG/vector database unless evaluation demonstrates a need.
-   Access to production credentials or infrastructure.
-   Treating an LLM statement as proof that tests passed.

## 2. Proposed technology defaults

These follow the current planning direction and must be accepted or
changed in `DECISIONS.md`.

  -----------------------------------------------------------------------
  Area                                Proposed default
  ----------------------------------- -----------------------------------
  Input                               ZIP upload; local path only as a
                                      development shortcut

  Initial language/test runner        Python + pytest

  Backend                             Python, FastAPI, Pydantic

  Agent orchestration                 LangGraph with typed state

  LLM                                 Provider wrapper; use Groq only
                                      after verifying a current
                                      tool-calling model and limits

  Persistence                         SQLite for runs, events, patches,
                                      tests, approvals

  Frontend                            React + TypeScript + Vite

  Sandbox                             Docker, no network, non-root,
                                      strict CPU/memory/PID/time/output
                                      limits

  Patch                               Validated structured edits rendered
                                      as unified diff, or a validated
                                      unified diff

  RAG                                 Deferred

  GitHub PR                           Optional Phase 5

  Approval                            Human approval before workspace
                                      write; separate approval before
                                      GitHub push/PR
  -----------------------------------------------------------------------

## 3. Target folder structure

Create this structure incrementally. Do not create every file as an
empty placeholder on day one.

``` text
autonomous-ai-software-engineer/
├── README.md
├── AGENTS.md
├── .gitignore
├── .env.example
├── pyproject.toml
├── docker-compose.yml                     # Phase 6
├── docs/
│   ├── PROJECT_GOALS.md
│   ├── PROJECT_CONTEXT.md
│   ├── AI_RULES.md
│   ├── TECH_STACK.md
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── DETAILED_PLAN.md
│   ├── IMPLEMENTATION_BLUEPRINT.md
│   ├── SECURITY.md
│   ├── TESTING_STRATEGY.md
│   ├── TASK_LOG.md
│   └── DECISIONS.md
├── backend/
│   └── app/
│       ├── main.py                         # app and router registration
│       ├── config.py                       # validated env-backed settings
│       ├── api/
│       │   ├── deps.py
│       │   └── routes/
│       │       ├── health.py
│       │       ├── workspaces.py
│       │       ├── repository.py
│       │       ├── runs.py
│       │       ├── patches.py
│       │       └── approvals.py
│       ├── schemas/
│       │   ├── common.py
│       │   ├── workspace.py
│       │   ├── repository.py
│       │   ├── task.py
│       │   ├── run.py
│       │   ├── finding.py
│       │   ├── patch.py
│       │   ├── test_result.py
│       │   └── approval.py
│       ├── core/
│       │   ├── paths.py                    # root confinement and symlink checks
│       │   ├── workspace.py                # managed workspace lifecycle
│       │   ├── zip_import.py                # safe archive extraction
│       │   ├── events.py
│       │   └── exceptions.py
│       ├── tools/
│       │   ├── registry.py                 # schemas + server-side permissions
│       │   ├── list_files.py
│       │   ├── read_file.py
│       │   ├── search_code.py
│       │   ├── propose_patch.py
│       │   └── run_tests.py                # calls sandbox service, not shell directly
│       ├── agent/
│       │   ├── state.py                    # typed graph state
│       │   ├── graph.py
│       │   ├── llm.py                      # provider wrapper and mock interface
│       │   ├── nodes/
│       │   │   ├── plan.py
│       │   │   ├── investigate.py
│       │   │   ├── summarize.py
│       │   │   ├── propose.py
│       │   │   ├── validate_patch.py
│       │   │   ├── test_patch.py
│       │   │   └── await_approval.py
│       │   └── prompts/
│       │       ├── investigation.md
│       │       └── patching.md
│       ├── sandbox/
│       │   ├── policy.py
│       │   ├── runner.py
│       │   └── parsers.py
│       ├── services/
│       │   ├── workspace_service.py
│       │   ├── run_service.py
│       │   ├── patch_service.py
│       │   ├── approval_service.py
│       │   └── event_service.py
│       └── db/
│           ├── database.py
│           ├── models.py
│           └── repositories.py
├── backend/tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── e2e/
├── eval/
│   ├── repos/bug_001/ ... bug_010/
│   ├── tasks.yaml
│   ├── schemas.py
│   ├── run_eval.py
│   └── results/
├── frontend/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/client.ts
│       ├── api/types.ts
│       ├── pages/NewRunPage.tsx
│       ├── pages/RunDetailPage.tsx
│       ├── pages/HistoryPage.tsx
│       ├── components/RepositoryUpload.tsx
│       ├── components/TaskForm.tsx
│       ├── components/RunTimeline.tsx
│       ├── components/FindingsPanel.tsx
│       ├── components/DiffViewer.tsx
│       ├── components/TestResultsPanel.tsx
│       ├── components/ApprovalControls.tsx
│       └── hooks/useRunEvents.ts
└── docker/
    └── sandbox.Dockerfile
```

### Responsibility boundaries

-   `api/routes/`: HTTP request/response, validation, status codes; no
    agent logic.
-   `schemas/`: typed API contracts.
-   `services/`: business workflow and transaction boundaries.
-   `core/`: filesystem and workspace safety.
-   `tools/`: small typed capabilities available to the agent.
-   `agent/`: planning/control flow; it cannot bypass tool
    authorization.
-   `sandbox/`: only component allowed to start test containers.
-   `db/`: persistence only.
-   `frontend/`: presentation and API calls; never a security boundary.
-   `eval/`: repeatable quality measurement independent of the UI.

## 4. API contracts --- proposed v1

Prefix API routes with `/api/v1`. Use JSON except ZIP upload and
Server-Sent Events (SSE). Use UUIDs for IDs. Return a consistent error
structure and never expose stack traces, secrets, host paths, or
environment variables.

``` json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request could not be processed.",
    "request_id": "req_example"
  }
}
```

### 4.1 Health

  Method   Endpoint    Purpose
  -------- ----------- -------------------------------------------------
  GET      `/health`   Liveness only; no environment or secret details

Response: `{"status":"ok"}`

### 4.2 Workspace and repository endpoints

  --------------------------------------------------------------------------------------------
  Method                  Endpoint                                     Purpose
  ----------------------- -------------------------------------------- -----------------------
  POST                    `/api/v1/workspaces`                         Create an empty managed
                                                                       workspace for
                                                                       development/testing

  POST                    `/api/v1/workspaces/upload`                  Upload and safely
                                                                       extract a ZIP

  GET                     `/api/v1/workspaces/{workspace_id}`          Read workspace metadata

  DELETE                  `/api/v1/workspaces/{workspace_id}`          Delete workspace and
                                                                       scratch copies

  GET                     `/api/v1/workspaces/{workspace_id}/files`    List safe files

  GET                     `/api/v1/workspaces/{workspace_id}/file`     Read a bounded text
                                                                       file

  GET                     `/api/v1/workspaces/{workspace_id}/search`   Search repository text
  --------------------------------------------------------------------------------------------

Upload uses `multipart/form-data`, field `file`. Successful response
(`201`):

``` json
{
  "workspace_id": "uuid",
  "name": "uploaded-repository",
  "status": "ready",
  "file_count": 42
}
```

List query parameters: `path` (optional relative directory),
`max_depth`, `limit`, `cursor`. Read parameters: `path`, `start_line`
(default 1), `end_line` (bounded). Search parameters: `q`, optional
`glob`, `limit`. Every path is validated server-side by `core/paths.py`;
never trust frontend validation.

### 4.3 Run endpoints

  ----------------------------------------------------------------------------------------
  Method                  Endpoint                                 Purpose
  ----------------------- ---------------------------------------- -----------------------
  POST                    `/api/v1/runs`                           Start an
                                                                   investigation/fix task

  GET                     `/api/v1/runs`                           List runs with
                                                                   pagination

  GET                     `/api/v1/runs/{run_id}`                  Get run status/report

  POST                    `/api/v1/runs/{run_id}/cancel`           Request cancellation

  GET                     `/api/v1/runs/{run_id}/events`           Stream events through
                                                                   SSE

  GET                     `/api/v1/runs/{run_id}/events/history`   Replay persisted events
                                                                   after reconnect
  ----------------------------------------------------------------------------------------

Start request:

``` json
{
  "workspace_id": "uuid",
  "task": "Fix the pagination off-by-one error and add a regression test.",
  "mode": "investigate_and_propose",
  "limits": {
    "max_iterations": 8,
    "max_tool_calls": 20,
    "timeout_seconds": 180
  }
}
```

The server clamps limits to configured maximums. The client must not be
able to raise safety limits. Initially, `mode` may be `investigate` or
`investigate_and_propose`; it must never mean "apply automatically."

Start response (`202`):

``` json
{
  "run_id": "uuid",
  "status": "queued",
  "events_url": "/api/v1/runs/uuid/events"
}
```

Run statuses: `queued`, `running`, `awaiting_approval`, `completed`,
`failed`, `cancelled`, `rejected`.

### 4.4 Patch endpoints

  ---------------------------------------------------------------------------------------
  Method                  Endpoint                                Purpose
  ----------------------- --------------------------------------- -----------------------
  GET                     `/api/v1/runs/{run_id}/patches`         List patches

  GET                     `/api/v1/patches/{patch_id}`            Patch metadata/status

  GET                     `/api/v1/patches/{patch_id}/diff`       Get bounded unified
                                                                  diff

  POST                    `/api/v1/patches/{patch_id}/validate`   Validate patch in
                                                                  scratch copy

  POST                    `/api/v1/patches/{patch_id}/tests`      Run permitted tests on
                                                                  scratch copy
  ---------------------------------------------------------------------------------------

Patch statuses: `proposed`, `invalid`, `validated`, `tested`,
`approved`, `rejected`, `applied`, `expired`.

Reject traversal, symlink targets, `.git` edits, binary files,
unexpected paths, stale text context, too many changed files, and
oversized patches.

### 4.5 Test-result endpoints

  ----------------------------------------------------------------------------------
  Method                  Endpoint                           Purpose
  ----------------------- ---------------------------------- -----------------------
  GET                     `/api/v1/runs/{run_id}/tests`      List baseline/patched
                                                             test executions

  GET                     `/api/v1/tests/{test_result_id}`   Read parsed result and
                                                             capped output excerpt
  ----------------------------------------------------------------------------------

Test statuses: `passed`, `failed`, `error`, `timed_out`, `cancelled`,
`ambiguous`, `not_run`. Missing/invalid JUnit XML, a crash, or unclear
output must never be represented as `passed`.

### 4.6 Approval and apply endpoints

  ---------------------------------------------------------------------------------------
  Method                  Endpoint                                Purpose
  ----------------------- --------------------------------------- -----------------------
  POST                    `/api/v1/patches/{patch_id}/approval`   Approve/reject the
                                                                  exact patch

  POST                    `/api/v1/patches/{patch_id}/apply`      Apply an approved,
                                                                  unchanged patch
  ---------------------------------------------------------------------------------------

Approval request:

``` json
{
  "decision": "approve",
  "diff_sha256": "server-generated-hash",
  "comment": "Reviewed diff and test results."
}
```

Rules: - The server computes the authoritative diff hash; a
client-provided value alone is not trusted. - Bind approval to patch ID,
diff hash, base workspace fingerprint, and approving user/session. - Any
patch or base-workspace change invalidates the approval. - Apply must
reject absent, expired, rejected, or mismatched approval. - Approval and
apply are separate actions. - Store audit events for approval and apply
attempts.

### 4.7 Optional GitHub endpoints --- Phase 5 only

  ----------------------------------------------------------------------------------------
  Method                  Proposed endpoint                        Purpose
  ----------------------- ---------------------------------------- -----------------------
  POST                    `/api/v1/github/import`                  Import an allowed
                                                                   GitHub repository URL

  POST                    `/api/v1/patches/{patch_id}/github-pr`   Create branch/push/PR
                                                                   after a second approval
  ----------------------------------------------------------------------------------------

Do not implement these for the MVP. GitHub support needs
URL/redirect/private-IP checks, least-privilege credentials, token
redaction, explicit approval, and no auto-merge.

## 5. Data models

Use SQLite initially. Keep schemas small and add fields when needed.

### Workspace

`id`, `name`, internal `root_path`, `status`, `created_at`,
`expires_at`, bounded `manifest_json`. Never expose absolute host paths.

### Run

`id`, `workspace_id`, `task`, `mode`, `status`, timestamps, cancellation
flag, iteration/tool-call counts, provider/model name, token counts if
available, safe error code/summary.

### RunEvent

`id`, `run_id`, monotonic `sequence`, `event_type`, timestamp,
validated/redacted `payload_json`. Do not persist secrets or
unrestricted raw model traces.

### Finding

`id`, `run_id`, `title`, `description`, `confidence_type` (`verified` or
`hypothesis`), `file_path`, line range, evidence summary.

### PatchProposal

`id`, `run_id`, `workspace_id`, `status`, diff/structured edits,
`diff_sha256`, base workspace fingerprint, validation result,
creation/expiry timestamps.

### TestExecution

`id`, `run_id`, optional `patch_id`, stage (`baseline` or `patched`),
status, passed/failed/skipped/error counts, duration, capped output
excerpt, internal JUnit XML location, timestamps.

### ApprovalAudit

`id`, `patch_id`, diff hash, workspace fingerprint, decision,
actor/session, comment, created/applied timestamps, result.

Use migrations when schema evolution becomes non-trivial. Store uploads,
scratch copies, and test artifacts outside the public/static directory.

## 6. LangGraph agent workflow

Add nodes incrementally by phase:

1.  `validate_request` --- check workspace, task length, and mode.
2.  `plan` --- produce a short investigation plan.
3.  `investigate` --- request read-only tools; backend validates each
    tool call.
4.  `check_stop` --- stop on sufficient evidence, limits, cancellation,
    or failure.
5.  `summarize` --- findings with file/line evidence and
    verified/hypothesis labels.
6.  `propose` --- produce minimal patch and regression test.
7.  `validate_patch` --- validate and apply only to scratch copy.
8.  `run_baseline_tests` --- check whether the original bug reproduces.
9.  `run_patched_tests` --- run tests against the scratch patch.
10. `await_approval` --- persist pending state and pause.
11. `apply_approved_patch` --- re-check approval/hash/fingerprint, then
    apply.
12. `finalize` --- persist status and summary.

Phase 2 stops after `summarize`. Phase 3 adds patch nodes. Phase 4 adds
test, approval, resume, and apply nodes.

### Typed state fields

`run_id`, `workspace_id`, `task`, `mode`, `plan`, bounded message
history, evidence list, findings, iteration/tool-call counts, start
time, patch ID, patch validation, baseline/patched test result IDs,
approval status, cancellation flag, status, and safe error.

Bound every field/list. Do not send the entire repository to the model;
use tools to retrieve bounded relevant excerpts.

### Tool authorization

Every tool must have: - Pydantic input and output schemas. - A
permission category: `read_only`, `scratch_write`, `sandbox_execute`, or
`approved_workspace_write`. - Server-side permission checks. - Argument,
result-size, execution-time, and call-count limits. - Structured errors
and unit/security tests.

The model may request a tool, but the backend validates arguments and
authorizes every call. Prompt instructions are not a security boundary.

## 7. SSE event contract

`GET /api/v1/runs/{run_id}/events` uses `text/event-stream`. Persist
events before streaming where practical so reconnects can replay them.

Event types: - `run.started` - `plan.created` - `tool.started` -
`tool.completed` - `finding.created` - `patch.proposed` -
`patch.validated` - `tests.started` - `tests.completed` -
`approval.required` - `patch.applied` - `run.completed` - `run.failed` -
`run.cancelled`

Example:

``` text
event: tool.completed
data: {"run_id":"uuid","sequence":4,"tool":"search_code","summary":"Found 3 matches","duration_ms":25}
```

Stream concise status and evidence summaries only. Do not stream
secrets, environment variables, hidden reasoning, or unlimited tool
output.

## 8. Frontend implementation order

### New Run page

Files: `NewRunPage.tsx`, `RepositoryUpload.tsx`, `TaskForm.tsx`. -
Upload ZIP and display validation errors. - Enter task and choose
investigation/proposal mode. - Start run and navigate to its detail
page.

### Run Detail page

Files: `RunDetailPage.tsx`, `RunTimeline.tsx`, `FindingsPanel.tsx`,
`DiffViewer.tsx`, `TestResultsPanel.tsx`, `ApprovalControls.tsx`. - Show
progress and safe event summaries. - Separate verified findings from
hypotheses. - Display proposed diff with "PROPOSED --- NOT APPLIED"
label. - Show baseline and patched tests distinctly. - Approve/reject
the exact diff; apply is a separate action.

### History page

File: `HistoryPage.tsx`. Add only after the core run flow works.

Centralize HTTP calls in `api/client.ts` and response types in
`api/types.ts`. Handle SSE reconnects and duplicate event sequence
numbers. Show clear errors for expired workspaces, cancellation, LLM
rate limits, sandbox timeouts, and ambiguous test results.

## 9. Phase-by-phase tasks and exit gates

## Phase 0 --- Product and design decisions

1.  [ ] Move all project docs under `docs/` and fix README links.
2.  [ ] Confirm MVP flow, supported Python/pytest scope, and non-goals.
3.  [ ] Record each accepted or changed default in `DECISIONS.md`.
4.  [ ] Smoke-test a currently available tool-calling model; record
    limits and errors in `TECH_STACK.md`. Keep a mock provider for
    tests.
5.  [ ] Choose how dependencies enter a no-network sandbox: pinned
    prebuilt image or reviewed read-only dependency cache.
6.  [ ] Set upload/file/archive caps, iteration/tool-call limits, run
    timeout, and output caps.
7.  [ ] Define evaluation measurements; set success targets after a
    baseline exists.
8.  [ ] Review security threats and defer GitHub-specific controls to
    Phase 5.
9.  [ ] Update `ROADMAP.md` and `TASK_LOG.md`.

**Deliverable:** accepted MVP specification. No application code
required yet.

## Phase 1 --- Safe repository ingestion and read-only tools

### A. Bootstrap

1.  [ ] Create `.gitignore`, `.env.example`, root `pyproject.toml`, and
    basic tests.
2.  [ ] Create `backend/app/main.py`; register `GET /health`.
3.  [ ] Create `backend/app/config.py` with validated settings.
4.  [ ] Configure pytest and Ruff.
5.  [ ] Add request IDs and consistent safe error responses.

### B. Workspace and archive safety

6.  [ ] Create `core/paths.py`: canonical root confinement, traversal
    rejection, symlink checks.
7.  [ ] Create `core/workspace.py`: unique workspace IDs, lifecycle,
    cleanup metadata.
8.  [ ] Create `core/zip_import.py`: reject zip-slip, symlinks,
    conflicting paths, excessive file count/size, suspicious compression
    ratio.
9.  [ ] Add security tests before any LLM integration.
10. [ ] Add workspace service and SQLite persistence.

### C. Read-only tools/API

11. [ ] Implement `list_files.py` with depth/count/extension/size caps.
12. [ ] Implement `read_file.py` with line bounds, binary detection,
    secret redaction.
13. [ ] Implement `search_code.py` with capped results and path/line
    numbers.
14. [ ] Add workspace/repository Pydantic schemas.
15. [ ] Add upload, metadata, delete, list, read, and search endpoints.
16. [ ] Integration test: upload → list → read → search → delete.
17. [ ] Create 10 seeded-bug Python repositories in `eval/repos/`.
18. [ ] Record task, expected files, known fix, and test command in
    `eval/tasks.yaml`.

**Exit criteria:** archive/path security tests pass; repository
endpoints work; all 10 eval repositories fail before their known fix and
pass after it.

## Phase 2 --- Read-only investigation agent

1.  [ ] Add provider-neutral LLM interface and deterministic mock.
2.  [ ] Add timeout, limited retries, quota/rate-limit mapping, token
    metadata, safe logs.
3.  [ ] Define Pydantic schemas for every tool.
4.  [ ] Implement `tools/registry.py` with allowlist and server-side
    permissions.
5.  [ ] Create typed `agent/state.py`.
6.  [ ] Write investigation prompt; label repository content as
    untrusted.
7.  [ ] Implement `plan`, `investigate`, `check_stop`, `summarize` graph
    nodes.
8.  [ ] Enforce iteration, tool-call, result-size, token, and wall-clock
    limits.
9.  [ ] Add run/event/finding SQLite tables and service.
10. [ ] Add create/list/get/cancel run endpoints.
11. [ ] Add persisted SSE stream and replay endpoint.
12. [ ] Build minimum UI: upload, task form, progress, report.
13. [ ] Test prompt injection in README and code comments.
14. [ ] Implement `eval/run_eval.py`; record relevant-file
    precision/recall, latency, tool calls, iterations and token use.

**Exit criteria:** mocked agent runs end-to-end; live provider smoke
test works when available; cancellation and limits are tested; baseline
evaluation is recorded.

## Phase 3 --- Patch proposal and diff review

1.  [ ] Choose canonical patch format; recommended: structured edits
    checked against original text, rendered as unified diff.
2.  [ ] Add patch schemas and `PatchProposal` persistence.
3.  [ ] Implement `tools/propose_patch.py` and validation service.
4.  [ ] Calculate diff SHA-256 and base workspace fingerprint.
5.  [ ] Create scratch copy; never edit the original during proposal.
6.  [ ] Add `propose` and `validate_patch` graph nodes with bounded
    repair attempts.
7.  [ ] Reject traversal, `.git` paths, symlink targets, binary files,
    stale context, and oversized patches.
8.  [ ] Add patch list/detail/diff/validate endpoints.
9.  [ ] Build `DiffViewer.tsx` with "PROPOSED --- NOT APPLIED".
10. [ ] Test that scratch copy changes but original remains
    byte-for-byte unchanged.
11. [ ] Evaluate patch validity and record results.

**Exit criteria:** patch is validated and reviewable; original workspace
remains unchanged.

## Phase 4 --- Sandboxed tests and human approval

1.  [ ] Create `docker/sandbox.Dockerfile` with pinned dependencies and
    non-root user.
2.  [ ] Implement `sandbox/policy.py`: allow only permitted test
    commands/flags.
3.  [ ] Implement `sandbox/runner.py`; avoid shell concatenation with
    untrusted input.
4.  [ ] Enforce no network, no Docker socket, no credentials/SSH keys,
    no broad host mounts, dropped capabilities, read-only root where
    possible, tmpfs and resource limits.
5.  [ ] Implement `sandbox/parsers.py` using structured pytest/JUnit
    output.
6.  [ ] Run baseline and patched tests separately.
7.  [ ] Persist `TestExecution` and add test-result endpoints.
8.  [ ] Add approval pause/resume backed by persisted state.
9.  [ ] Add approval service and audit table.
10. [ ] Bind approval to patch ID, diff hash and base workspace
    fingerprint.
11. [ ] Implement approve/reject endpoint and separate apply endpoint.
12. [ ] Re-check approval/hash/fingerprint/path safety during apply;
    reject stale approvals.
13. [ ] Build test results and approval UI.
14. [ ] Test timeouts, memory/PID limits, huge output, network attempts,
    host-file attempts, and malicious pytest plugins/conftest.
15. [ ] Document Docker isolation limitations; consider VM/microVM
    isolation before executing public untrusted repositories.

**Exit criteria:** sandbox security tests pass in the target
environment; no write occurs without recorded approval; ambiguous
results are never marked as pass.

## Phase 5 --- Optional GitHub PR workflow

1.  [ ] Threat-model URLs, redirects, private/internal IP access, and
    credential exposure.
2.  [ ] Implement safe URL validation and shallow clone into a temporary
    workspace.
3.  [ ] Add least-privilege GitHub credentials outside the database and
    logs.
4.  [ ] Show repository/branch/change preview.
5.  [ ] Require a second approval for branch creation, push, and PR.
6.  [ ] Create PR body with summary, diff stats, and test outcomes.
7.  [ ] Never merge automatically.
8.  [ ] Mock GitHub API tests; manually test against a disposable
    repository.
9.  [ ] Verify token redaction.

**Exit criteria:** PR is possible only after two approvals; no merge
path exists.

## Phase 6 --- Hardening and portfolio release

1.  [ ] Add structured JSON logging with request/run IDs and secret
    redaction.
2.  [ ] Add authentication, rate limits and per-user usage caps before
    public deployment.
3.  [ ] Add CI for lint, unit, integration, security, and evaluation
    smoke tests.
4.  [ ] Add Docker Compose and documented setup.
5.  [ ] Clean expired workspaces, scratch copies, logs and test
    artifacts.
6.  [ ] Run full evaluation and record
    model/date/dataset/metrics/limitations.
7.  [ ] Verify setup from a fresh clone.
8.  [ ] Add demo scenarios and known limitations.
9.  [ ] Write resume claims only from measured results.
10. [ ] Update roadmap, task log, decisions and docs to match shipped
    behavior.

**Exit criteria:** fresh setup works, CI and security tests pass,
evaluation is reproducible, and demo shows evidence → patch → tests →
approval → apply.

## 10. Environment variables

Add variables only when code consumes them. Keep `.env.example`
non-secret.

``` dotenv
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=sqlite:///./data/app.db
WORKSPACE_ROOT=./data/workspaces
SCRATCH_ROOT=./data/scratch
MAX_UPLOAD_MB=25
MAX_ARCHIVE_FILES=5000
MAX_UNPACKED_MB=200
MAX_FILE_MB=2
MAX_FILE_LINES=500
MAX_SEARCH_RESULTS=100
AGENT_MAX_ITERATIONS=8
AGENT_MAX_TOOL_CALLS=20
AGENT_TIMEOUT_SECONDS=180
LLM_PROVIDER=groq
LLM_MODEL=replace-with-verified-model
LLM_API_KEY=
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
SANDBOX_ENABLED=false
SANDBOX_IMAGE=autonomous-ai-swe-sandbox:latest
SANDBOX_TIMEOUT_SECONDS=60
SANDBOX_MEMORY_MB=512
SANDBOX_CPUS=1
SANDBOX_PIDS_LIMIT=128
SANDBOX_OUTPUT_KB=256
```

Never commit `.env`, credentials, uploaded repositories, or secrets.
Enforce upper bounds in backend validation.

## 11. Testing matrix

  -----------------------------------------------------------------------
  Layer                               Tests
  ----------------------------------- -----------------------------------
  Unit                                path normalization, archive
                                      validation, schemas, patch
                                      validation, event ordering, pytest
                                      parser

  Integration                         upload/list/read/search, mocked
                                      investigation, cancellation, patch
                                      proposal, pause/resume

  Security                            zip-slip, symlink escape,
                                      traversal, zip bomb, prompt
                                      injection, disallowed tools,
                                      sandbox abuse

  E2E                                 upload → investigate → propose →
                                      test → approve → apply

  Evaluation                          bug localization, patch validity,
                                      test outcomes, latency, tool calls,
                                      token use

  Frontend                            upload errors, SSE reconnect,
                                      duplicate events, diff/hash
                                      mismatch, approval states
  -----------------------------------------------------------------------

Use deterministic mock LLM tests in CI. Keep live-provider smoke tests
separate so provider availability does not make every test flaky.

## 12. Non-negotiable safety rules

-   Backend owns authorization; neither model nor frontend can grant
    permissions.
-   Repository files and tool output are untrusted.
-   No arbitrary shell tool in the MVP.
-   Timeout, crash, malformed output, or missing test report is not a
    pass.
-   Every run has iteration, tool-call, time and output caps.
-   Every patch is applied and tested in scratch before approval.
-   Any change to patch/base invalidates approval.
-   No workspace write without valid recorded approval.
-   No GitHub push without second approval.
-   Reports distinguish evidence-backed findings from hypotheses.
-   Every completed task has actual test results and an updated task
    log.

## 13. First five coding sessions

### Session 1 --- Backend skeleton

Create `.gitignore`, `.env.example`, root `pyproject.toml`,
`backend/app/main.py`, `backend/app/config.py`, and `backend/tests/`.
Add `GET /health`, run the server, and test it.

### Session 2 --- Path safety

Create `backend/app/core/paths.py` and unit tests. Prove normal paths
work and traversal/absolute paths/symlink escapes fail. Do not connect
an LLM.

### Session 3 --- Workspace lifecycle

Create `core/workspace.py`, workspace schemas and service. Test
create/get/delete with temporary directories.

### Session 4 --- Safe ZIP import

Create `core/zip_import.py` and the upload endpoint. Test valid ZIP,
zip-slip, symlink entries, file-count caps and unpacked-size caps.

### Session 5 --- Read-only repository tools

Create `tools/list_files.py`, `read_file.py`, `search_code.py` and
corresponding APIs. Finish with an integration test: upload → list →
read → search.

Only after these sessions and security tests pass should agent
integration begin.

## 14. Decisions to track in `DECISIONS.md`

-   [ ] Exact LLM model/provider with verified tool calling and
    acceptable limits.
-   [ ] Structured edits or unified diff as canonical patch
    representation.
-   [ ] Dependency strategy for network-disabled sandbox.
-   [ ] Local-only vs public deployment target; isolation/auth
    requirements differ.
-   [ ] Authentication scheme before multi-user deployment.
-   [ ] Workspace retention and deletion policy.
-   [ ] Realistic evaluation targets after Phase 2 baseline.
