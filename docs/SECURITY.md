# Security and Safety Requirements

Security is a product requirement, not a prompt-only feature.

## Threats to consider

- Malicious instructions embedded in repository files, comments, READMEs, issues, or test output (prompt injection).
- Path traversal or attempts to read files outside the selected repository.
- Secret discovery and accidental transmission of credentials or private code.
- Malicious build scripts, package lifecycle scripts, tests, or dependencies.
- Destructive commands and unintended file changes.
- Unauthorized GitHub writes or excessive repository permissions.
- Denial of service through huge repositories, long-running commands, large output, or agent loops.
- Sensitive data leaking into logs, traces, model prompts, or evaluation datasets.

## Minimum controls before running repository code

- Never execute untrusted repository code directly on the developer's host.
- Use an isolated sandbox/container with a non-root user and restricted capabilities.
- Apply CPU, memory, process, disk, wall-clock, and output limits.
- Default to no network access during test execution unless a narrowly scoped exception is approved.
- Do not mount host credentials, Docker socket, SSH keys, or unrelated directories into the sandbox.
- Use a temporary workspace and clean it up after execution.
- Validate commands server-side against an explicit policy; do not rely on model-generated commands alone.
- Restrict file paths to the selected repository and prevent symlink/path traversal escapes.
- Treat repository contents and tool output as untrusted data.
- Require explicit approval for applying patches and external write operations.
- Use least-privilege, scoped GitHub credentials; never commit credentials.
- Redact secrets and avoid logging full private source files by default.

## Prompt injection

Heuristic detection may help flag suspicious content, but it is not a complete defense. Security boundaries must be enforced by tool permissions, isolation, input validation, and approval gates.

## Reporting

The agent must distinguish:
- Suggested patch vs. applied patch
- Tests passed vs. tests failed
- Tests not run vs. tests skipped
- Verified findings vs. hypotheses
- A pull request prepared vs. a pull request merged
