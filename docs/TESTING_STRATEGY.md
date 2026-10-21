# Testing and Evaluation Strategy

## Testing layers

### Unit tests
- Path normalization and repository boundary checks
- File filtering and code search
- Patch validation
- Tool input schemas and authorization
- Agent state transitions and iteration limits
- Provider error handling and retries
- Output truncation and secret redaction

### Integration tests
- API request/response behavior
- Repository inspection workflow
- LLM tool-call parsing with mocked provider responses
- Approval pause/resume flow
- Test-runner result collection
- Persistence, if selected

### Security tests
- Path traversal attempts
- Symlink escapes
- Prompt injection in repository content
- Unauthorized patch application
- Unauthorized GitHub write operations
- Oversized files and command output
- Timeouts and resource-limit behavior
- Secret redaction

### End-to-end tests
Use a small set of intentionally constructed sample repositories with known tasks and expected outcomes. Avoid using private or sensitive repositories in public evaluations.

## Agent evaluation dataset

For each task, record:
- Task description
- Sample repository and commit/version
- Expected relevant files or evidence
- Expected behavior and disallowed actions
- Expected test command, if applicable
- Whether a patch is expected
- Evaluation result and notes

## Metrics to consider

- Relevant-file retrieval precision/recall
- Task completion rate on a fixed dataset
- Patch validity rate
- Regression test pass rate
- False-positive and false-negative rates for seeded bugs
- Unauthorized-action prevention rate
- Median and p95 latency
- LLM calls and tokens per task
- Human approval/rejection rate

Do not treat an LLM judge as the sole source of truth. Combine deterministic checks, test outcomes, human review, and model-based evaluation where appropriate.

## Reporting rule

Only report metrics that were actually measured, with the dataset size, setup, and limitations documented.
