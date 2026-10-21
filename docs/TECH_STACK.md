# Technology Stack

## Principles

- Prefer a small stack that supports the MVP.
- Use free or low-cost services for learning and portfolio development where feasible.
- Verify current model capabilities, quotas, SDK versions, and hosting limits before committing to them.
- A listed technology is proposed until the decision is recorded as accepted.

## Proposed initial stack

| Layer | Candidate | Purpose | Status |
|---|---|---|---|
| Language | Python 3.12+ | Backend and agent tools | Proposed |
| API | FastAPI | HTTP API and streaming | Proposed |
| Validation | Pydantic | Request, response, and tool schemas | Proposed |
| Agent workflow | LangGraph | Stateful orchestration, routing, approval pauses | Proposed |
| LLM provider | Groq API with a supported tool-calling model | Reasoning and tool selection | Proposed; verify current model and limits |
| Repository integration | GitHub API / GitHub App or approved token | Repository access and optional pull requests | Open decision |
| Code search | Ripgrep or a controlled indexing/search layer | Find relevant files and symbols | Proposed |
| Testing | pytest initially; repository-specific test commands | Verify patches | Proposed |
| Execution isolation | Container or dedicated sandbox | Safely run untrusted repository code | Must be designed before execution features |
| Frontend | React + TypeScript + Vite | Developer workspace UI | Proposed |
| Styling | Tailwind CSS | UI styling | Proposed |
| Database | To be decided | Users, tasks, approvals, run history | Open decision |
| Observability | Structured logs; tracing tool to be selected | Debugging, latency, token/cost visibility | Proposed |
| Local development | Docker Compose where useful | Reproducible services | Proposed |
| CI | GitHub Actions or equivalent | Automated checks | Proposed |

## LLM cost and provider policy

- Begin with Groq free API access if a currently available model supports the required tool-calling behavior.
- Free-tier limits are not unlimited and can change; design bounded retries, iteration limits, timeouts, and clear quota errors.
- Keep provider/model configuration centralized so providers can be swapped without redesigning the entire application.
- Do not assume every model supports structured output, parallel tool calls, or identical tool-call behavior.
- Do not send secrets or private repository data to an external provider without an explicit data-flow and privacy decision.
- Embeddings and code RAG are not mandatory for the first milestone; add them only if evaluation shows a need.

## Before locking the stack

Confirm:
1. The model's tool-calling capability and current free-tier limits.
2. How repository credentials are stored and scoped.
3. The isolation model for executing tests.
4. Whether the first version needs persistent task state and which database is justified.
5. The target deployment environment and its constraints.
