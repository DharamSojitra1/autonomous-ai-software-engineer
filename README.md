# Autonomous AI Software Engineer

An AI-assisted software engineering system that can inspect a code repository, investigate a developer task, propose code changes, generate or update tests, and verify changes in a controlled environment.

> **Project status:** Planning and documentation phase. Treat planned features as goals, not as implemented capabilities.

## Start here

1. Read [`AGENTS.md`](AGENTS.md) before making changes.
2. Read [`docs/PROJECT_GOALS.md`](docs/PROJECT_GOALS.md) to understand the product.
3. Read [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) for current status and important context.
4. Read [`docs/AI_RULES.md`](docs/AI_RULES.md) for collaboration rules.
5. Read [`docs/TECH_STACK.md`](docs/TECH_STACK.md) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) before proposing implementation changes.
6. Check [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/TASK_LOG.md`](docs/TASK_LOG.md) before starting work.

## Core product loop

**Task → Inspect repository → Investigate → Propose patch → Human approval → Run tests safely → Report results → Optional pull request**

The agent must not claim a bug is fixed merely because it generated a patch. It should report what was changed and what verification actually ran.

## Documentation policy

The documentation is the project's shared source of truth. When a major decision or implementation status changes, update the relevant document in the same change.
