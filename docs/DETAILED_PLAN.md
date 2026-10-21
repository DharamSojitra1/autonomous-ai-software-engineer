# Detailed Implementation Plan

Companion to `ROADMAP.md`. The roadmap is the checklist; this file explains **how** to do each phase, what to build, how to test it, and when the phase is done.

> **Status:** Planning. Nothing here is implemented. Items marked *(proposed default)* are suggestions that still need to be recorded as Accepted in `DECISIONS.md`.

Estimated total: **about 12 weeks** at roughly 10-12 hours per week. Adjust freely; finish each phase's exit criteria before moving on.

---

## Proposed defaults to confirm in Phase 0

| Decision | Proposed default | Why |
|---|---|---|
| Repo input | ZIP upload (local path as dev shortcut) | No GitHub auth needed to start |
| Language supported | Python + pytest only | One ecosystem, one test runner |
| Sandbox | Docker, `--network none`, non-root, CPU/mem/time limits | Matches SECURITY.md |
| Database | SQLite | Zero setup, enough for MVP |
| Code RAG | Deferred | Already built in the first project; add only if evals show a need |
| GitHub PR | Phase 5 | Needs everything else working first |
| LLM | Groq, after verifying a current model supports tool calling | Free tier, centralized config |
| Approval flow | Apply patch to a temp copy, run tests, then show diff + results for approval, then write to the real workspace | User judges a patch better with test evidence (propose as DEC-005) |

---

## Target folder structure

```text
autonomous-ai-software-engineer/
  docs/                      # all the .md planning docs
  backend/
    app/
      main.py                # FastAPI app, routers
      config.py              # settings, model names (centralized)
      api/                   # routes only: no business logic
      core/
        paths.py             # path safety, symlink checks
        workspace.py         # create/cleanup temp workspaces
        zip_import.py        # safe ZIP extraction
      tools/                 # list_files, read_file, search_code, propose_patch, run_tests
        registry.py          # tool schemas + authorization
      agent/
        state.py             # typed task state
        graph.py             # LangGraph workflow
        prompts/             # prompts kept separate from logic
        llm.py               # provider wrapper, retries, timeouts
      sandbox/
        runner.py            # Docker execution
        policy.py            # allowed commands
        parsers.py           # pytest result parsing
      services/
        run_service.py       # create/cancel/resume runs
      db/                    # SQLite models
    tests/
      unit/ integration/ security/ e2e/
  eval/
    repos/                   # seeded-bug sample repos (10+)
    tasks.yaml               # task + expected files + expected outcome
    run_eval.py
  frontend/                  # React + TS + Vite (Phase 2 onward, built incrementally)
  docker/
    sandbox.Dockerfile
  docker-compose.yml
```

---

## Phase 0 - Product definition and design (Week 1)

**Goal:** remove ambiguity so coding can start without rework.

Steps
1. Move the docs into `docs/` so README/AGENTS.md links actually resolve.
2. Confirm the proposed defaults above; record each as Accepted in `DECISIONS.md` (DEC-004 split into smaller decisions, plus DEC-005 for the approval flow).
3. Verify the LLM: check Groq's current model list and confirm one model supports tool calling; note current free-tier limits in `TECH_STACK.md`.
4. Write acceptance criteria (see "Acceptance criteria" at the bottom).
5. Review SECURITY.md threats and decide which are in the MVP (all sandbox controls are; the GitHub ones wait for Phase 5).
6. Decide how dependencies get into the no-network sandbox (pre-built image with pinned packages, or a dependency cache volume mounted read-only).
7. Update `TASK_LOG.md` and `ROADMAP.md`.

Exit criteria: all Phase 0 roadmap boxes checked; no "Open" items left in DECISIONS.md that block Phase 1.

---

## Phase 1 - Read-only repository understanding (Weeks 2-3)

**Goal:** safely load a repo and let code (not the LLM yet) list, read, and search it.

Steps
1. Backend skeleton: FastAPI app, `/health`, settings via env vars, pytest set up, linting (ruff), pre-commit.
2. `core/paths.py`: one function that resolves any requested path against the workspace root and rejects `..`, absolute paths, and symlinks that escape. Everything else must go through it.
3. `core/zip_import.py`: safe extraction. Reject zip-slip paths, symlinks, absurd compression ratios, too many files, files above a size cap. Store in a temp workspace with an ID.
4. `core/workspace.py`: create, look up, and delete workspaces; cleanup on a timer and on shutdown.
5. Tools (plain functions with Pydantic input/output models):
   - `list_files(path, max_depth)`: filtered by allowed extensions, size limits
   - `read_file(path, start_line, end_line)`: line-limited, binary detection, secret-pattern redaction
   - `search_code(query, glob)`: ripgrep if installed, Python fallback; capped results with path + line numbers
6. API endpoints: upload repo, list files, read file, search.
7. Build the **evaluation dataset** in parallel: create the first 10 small Python repos, each with one seeded bug and a failing/passing pytest. Record in `eval/tasks.yaml`: task description, repo, expected relevant files, expected fix, test command.

Tests
- Unit: path normalization, binary detection, redaction.
- Security: `../../etc/passwd`, absolute paths, symlink escape, zip-slip, zip bomb, huge file, huge directory.
- Integration: upload then list then read then search.

Exit criteria: all security tests pass; 10 eval repos exist and each one's test demonstrably fails before the fix and passes after the known fix (verified by hand).

---

## Phase 2 - Investigation agent (Weeks 4-6)

**Goal:** a bounded agent that investigates a task using only read-only tools and reports evidence.

Steps
1. `agent/llm.py`: provider wrapper with centralized model name, timeout, bounded retries with backoff, clear quota/rate-limit errors, token usage capture. Mock version for tests.
2. `tools/registry.py`: register tools with JSON schemas; validate every LLM-produced argument with Pydantic; enforce per-tool authorization server-side.
3. `agent/state.py`: typed state (task, plan, messages, evidence list, iteration count, status, errors).
4. `agent/graph.py` (LangGraph):
   - nodes: `plan` then `investigate` (loop: model proposes tool call, app validates and executes, result appended) then `summarize`
   - stop conditions: max iterations, max tool calls, wall-clock timeout, cancellation flag, "enough evidence" decision
5. Prompts in `agent/prompts/`; tell the model that repo content is untrusted data. Never rely on this as the security boundary.
6. Run service + SQLite: create run, store events, status, final report. Cancel endpoint.
7. Streaming: SSE endpoint emitting events (plan created, tool called, tool result summary, final report).
8. Report format: findings with file paths and line numbers, each marked **verified** (backed by tool output) or **hypothesis**.
9. Minimal frontend: upload ZIP, enter task, watch the event stream, see the report.
10. Eval harness `eval/run_eval.py`: run all tasks, measure relevant-file precision/recall, iterations, tokens, latency. Save results to a file.

Tests
- Unit: state transitions, iteration cap, invalid tool args rejected, retry/timeout behavior.
- Integration: mocked LLM drives a full investigation; cancel mid-run.
- Security: prompt injection planted in a README and in code comments (agent must not follow it or call disallowed tools).

Exit criteria: harness runs end to end; you record baseline metrics (e.g., relevant-file recall on 10 tasks) with dataset size and limitations noted.

---

## Phase 3 - Patch proposal and review (Weeks 7-8)

**Goal:** the agent proposes a fix and a regression test as a diff, without touching the real workspace.

Steps
1. Choose the patch format: unified diff or structured edits (file, old text, new text). Structured edits are easier for LLMs to get right; convert to a diff for display.
2. `tools/propose_patch`: validates paths (inside workspace, not outside scope), size limits, file count limits, and that `old text` actually matches.
3. Create a **scratch copy** of the workspace; apply the proposal there only.
4. Add graph nodes: `propose` and `validate_patch`; allow a bounded number of repair attempts if validation fails.
5. Test generation: ask for a regression test that fails before the fix and passes after.
6. Review UI: diff viewer (added/removed lines), file list, clear label "PROPOSED, not applied".
7. Persist patch proposals and their validation results.

Tests
- Unit: patch validation (path escape, mismatched context, oversized patch, binary files).
- Integration: mocked LLM proposes a patch; scratch copy changes, real workspace unchanged.
- Security: patch targeting `../`, `.git/`, or a symlink is rejected.

Exit criteria: for the eval set, proposals are produced and validated; the real workspace is never modified (assert in tests).

---

## Phase 4 - Isolated test execution and approval gate (Weeks 8-10)

**Goal:** run tests safely on the patched scratch copy, then gate the real write behind approval.

Steps
1. `docker/sandbox.Dockerfile`: Python base, pytest, pinned common dependencies, non-root user, no extra tools.
2. `sandbox/policy.py`: allowlist of commands (start with `pytest` plus a few flags); reject everything else server-side.
3. `sandbox/runner.py`: run the container with `--network none`, read-only root filesystem where possible, tmpfs for temp, dropped capabilities, CPU/memory/pids limits, wall-clock timeout, output size cap. Never mount the Docker socket, SSH keys, or host directories other than the scratch copy.
4. `sandbox/parsers.py`: parse pytest results (use `--junitxml` or `-rA`) into passed / failed / skipped / error counts. If parsing fails, report **"result ambiguous"**, never "passed".
5. Graph: `run_tests_before` (confirm the bug reproduces), then `run_tests_after`, then `await_approval` (LangGraph interrupt/pause; resumable after a server restart because state is in SQLite).
6. Approval API + UI: show diff, before/after test results, uncertainty notes; Approve or Reject buttons. On approval, apply to the real workspace; on rejection, discard the scratch copy.
7. Audit trail: record who approved what, when, and the exact diff hash that was approved (reject if the diff changed after approval was requested).
8. Report: clearly separates suggested vs applied, tests passed vs failed vs skipped vs not run.

Tests
- Security: infinite loop test (timeout), fork bomb (pids limit), memory hog, huge output, attempt to reach the network, attempt to read host files, malicious `conftest.py`.
- Integration: full flow on eval repos with a mocked LLM; pause and resume; reject path.
- Unit: result parser on passing, failing, skipped, crashed, and garbage output.

Exit criteria: all sandbox security tests pass; no code path writes to the real workspace without a recorded approval.

---

## Phase 5 - Optional GitHub workflow (Week 11)

**Goal:** turn an approved patch into a branch and pull request.

Steps
1. Choose auth: fine-grained personal access token scoped to a single test repo for the MVP; GitHub App later if desired. Store the token in env/secret storage, never in the DB or logs.
2. Import a repo by URL (clone shallowly into a temp workspace, same safety checks as ZIP).
3. After approval, a **second approval** is required to create a branch and push (explicit in the UI).
4. Create the branch, commit with a clear message, open the PR via the GitHub API; include summary, diff stats, and test results in the PR body.
5. Never merge; the merge decision stays with the user.

Tests
- Mock the GitHub API in tests; one manual run against a throwaway repo.
- Security: attempts to push without approval fail; token redacted from logs.

Exit criteria: a PR is created on a test repo only after two explicit approvals.

---

## Phase 6 - Production and portfolio polish (Week 12)

Steps
1. Structured JSON logging with secret redaction; basic tracing (run ID on every log line; optionally Langfuse or similar).
2. Rate limits and per-user usage caps; authentication if you deploy publicly.
3. CI: GitHub Actions running lint, unit, integration, and security tests.
4. Dockerize backend and frontend with `docker-compose.yml`; document setup.
5. Final evaluation: run the full eval set, publish results with dataset size, model, date, and limitations.
6. README: architecture diagram, screenshots, demo video (agent finds the bug, proposes a fix, shows test results, waits for approval), known limitations.
7. Resume: add outcomes using only measured numbers.

Exit criteria: fresh clone + `docker compose up` works from the README; CI green; measured results documented.

---

## Weekly schedule summary

| Week | Phase | Main output |
|---|---|---|
| 1 | 0 | Decisions accepted, acceptance criteria written |
| 2-3 | 1 | Safe ZIP import, path safety, list/read/search tools, 10 eval repos |
| 4-6 | 2 | LangGraph investigation agent, SSE streaming, minimal UI, baseline metrics |
| 7-8 | 3 | Patch proposals on scratch copy, diff review UI |
| 8-10 | 4 | Docker sandbox, test results, approval gate, audit trail |
| 11 | 5 | Optional GitHub branch and PR with double approval |
| 12 | 6 | CI, deployment, final eval, demo, README, resume |

---

## Acceptance criteria (draft, adjust numbers after the baseline run)

- **Safety (must be 100%):** no write to the real workspace without approval; all path traversal, symlink, zip-slip, and sandbox-limit security tests pass.
- **Investigation:** on the 10-repo eval set, the agent identifies the buggy file in at least N tasks (set N after Phase 2 baseline).
- **Patching:** at least M proposals pass validation and make the seeded test pass (set M after Phase 3/4 baseline).
- **Reporting accuracy:** zero cases where the report says "passed" without a parsed passing result.
- **Bounds:** every run ends within the iteration, tool-call, and time limits.
- **Reproducibility:** eval results are saved with model name, date, dataset size, and notes.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Free-tier rate limits slow evals | Cache nothing sensitive; run small batches; keep a mock LLM for tests; centralize the provider so you can swap |
| LLM produces malformed patches | Structured edits, validation, bounded repair loop |
| Sandbox takes longer than expected | Start with Docker CLI via subprocess; harden incrementally; do not skip the security tests |
| Scope creep (RAG, multi-language, GitHub) | Follow the non-goals in PROJECT_GOALS.md; add only if evals justify |
| Dependencies unavailable offline | Pre-built image with pinned packages, decided in Phase 0 |

## Definition of done for any task

1. Code written and reviewed against the relevant doc.
2. Tests added for normal, edge, failure, and security cases.
3. Tests actually run, with results recorded (never claimed without running).
4. `TASK_LOG.md`, `ROADMAP.md`, and `DECISIONS.md` updated where relevant.
