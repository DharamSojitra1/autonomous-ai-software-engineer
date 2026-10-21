# Architecture

## Status

This is a proposed logical architecture, not a claim about implemented code. Update it as design decisions are approved.

## Logical flow

```text
React + TypeScript Workspace
          |
          v
       FastAPI
          |
          v
 Task / Run Service ---- Persistence (to be selected)
          |
          v
 LangGraph Workflow
   |        |         |
   |        |         +--> Approval / Pause / Resume
   |        +------------> LLM provider (Groq initially, if suitable)
   +---------------------> Policy-controlled tool registry
                                 |
                 +---------------+----------------+
                 |               |                |
             Repository       Patch / Diff     Test Runner
             read/search      generation      isolated sandbox
                 |               |                |
                 +---------------+----------------+
                                 |
                                 v
                       Results / Audit Trail
                                 |
                                 v
                         UI + Optional PR
```

## Core workflow stages

1. **Validate task:** authenticate the user, validate request size and repository permissions.
2. **Inspect:** list allowed files and gather repository metadata using read-only tools.
3. **Plan:** produce a bounded task plan with explicit goals and stop conditions.
4. **Investigate:** search files, inspect relevant code and tests, and collect evidence.
5. **Propose:** generate a patch and test changes; do not apply them silently.
6. **Approve:** show a diff and require explicit user approval before writing changes.
7. **Execute tests:** run only permitted commands in an isolated, resource-limited environment.
8. **Verify:** collect exit codes, logs, test counts, and changed-file information.
9. **Report:** summarize findings, modifications, test outcomes, uncertainty, and next steps.
10. **Optional GitHub action:** only after explicit authorization, prepare a branch or pull request.

## Design principles

- Keep repository access and command execution in application-controlled tools.
- Use the LLM for interpretation and planning, not as the security boundary.
- Enforce permissions, path restrictions, timeouts, output limits, and network policy outside the prompt.
- Persist task state only as needed; define retention and secret-redaction behavior.
- Make tool calls and state transitions observable without logging secrets or unnecessary source contents.
- Support cancellation and bounded execution.
