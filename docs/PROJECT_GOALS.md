# Project Goals

## Product vision

Build a portfolio-grade Autonomous AI Software Engineer that helps developers investigate and resolve software tasks inside a code repository, with transparent evidence and human control.

## Problem

A conventional chat assistant can explain code, but developers often still need to manually locate relevant files, trace a bug, prepare a patch, write regression tests, execute tests, and review the result.

## Primary user journey

1. A user opens or connects a repository they are authorized to access.
2. The user describes a task, bug, or improvement.
3. The system inspects repository structure and relevant files.
4. The agent creates an investigation plan and gathers evidence using approved tools.
5. The agent proposes a patch and tests, showing a clear diff.
6. The user reviews and approves the proposed change before it is applied.
7. Tests run in a restricted, isolated environment.
8. The system reports changed files, test results, limitations, and remaining risks.
9. Optionally, the system prepares a Git branch and pull request after explicit approval.

## MVP goals

- Support a clearly defined initial repository workflow.
- Inspect files and repository structure using read-only tools.
- Search code and explain findings with file paths and line references where practical.
- Propose code patches without silently applying them.
- Generate or update tests for proposed fixes.
- Run approved tests in a controlled environment.
- Show task progress, tool activity, diffs, logs, and test outcomes.
- Keep the developer in control of file modifications and GitHub write actions.
- Record enough task history to explain what happened.

## Non-goals for the first version

- Fully autonomous merging to a protected branch.
- Unrestricted shell or host-machine access.
- Guaranteed detection of every bug or vulnerability.
- Supporting every programming language and repository format from day one.
- Training a foundation model.
- Rebuilding all capabilities from the existing AI Developer Assistant without a demonstrated need.

## Success criteria

Define measurable acceptance criteria before implementation. Initial candidates:

- The agent identifies the relevant files for a curated set of repository tasks.
- Proposed patches are reviewable and do not modify files without approval.
- Tests run in an isolated environment with resource and time limits.
- The UI distinguishes proposed changes from applied changes.
- Results clearly distinguish passed tests, failed tests, skipped tests, and tests not run.
- Security tests cover path traversal, malicious repository instructions, unsafe commands, secrets exposure, and unauthorized write operations.

Do not publish success-rate claims until they are measured on a documented evaluation set.
