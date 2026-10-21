# Roadmap

## Phase 0 — Product definition and design
- [x] Create initial documentation structure
- [ ] Confirm MVP scope and acceptance criteria
- [ ] Decide repository input method
- [ ] Decide initial supported language/framework
- [ ] Review threat model and sandbox options
- [ ] Record accepted architecture decisions

## Phase 1 — Read-only repository understanding
- [ ] Create backend skeleton and health endpoint
- [ ] Accept a local ZIP or authorized repository reference (decision pending)
- [ ] Validate repository paths and file types
- [ ] List files and search source safely
- [ ] Show relevant snippets with path/line references
- [ ] Add tests for path traversal and unsupported files

## Phase 2 — Investigation agent
- [ ] Add bounded LangGraph workflow
- [ ] Define typed task state and tool schemas
- [ ] Integrate a compatible LLM through centralized configuration
- [ ] Add repository investigation and test-discovery tools
- [ ] Add timeouts, iteration caps, cancellation, and structured errors
- [ ] Evaluate on a small curated task set

## Phase 3 — Patch proposal and review
- [ ] Generate patch/diff proposals
- [ ] Validate patch paths and reject out-of-scope changes
- [ ] Build a review UI
- [ ] Require explicit approval before applying changes
- [ ] Add patch validation tests

## Phase 4 — Isolated test execution
- [ ] Select and document the sandbox design
- [ ] Enforce CPU, memory, time, disk, and output limits
- [ ] Define network access policy
- [ ] Run approved test commands in isolation
- [ ] Report test results accurately
- [ ] Test sandbox escape and unsafe-command boundaries as appropriate

## Phase 5 — Optional GitHub workflow
- [ ] Choose least-privilege GitHub authentication
- [ ] Create a branch only with user approval
- [ ] Push approved changes only with user approval
- [ ] Prepare a pull request and include test results
- [ ] Keep merge decisions with the user

## Phase 6 — Production and portfolio polish
- [ ] Add authentication if required by the deployment model
- [ ] Add structured logging and observability
- [ ] Add rate limits and usage controls
- [ ] Add CI and a repeatable test suite
- [ ] Dockerize and document deployment
- [ ] Add architecture diagrams, demo, screenshots, and measured evaluation results

## Status convention

Use `Not started`, `In progress`, `Blocked`, `Implemented`, and `Verified`. “Implemented” means code exists; “Verified” means the relevant checks were run and passed.
