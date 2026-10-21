# Architecture and Product Decisions

Record significant decisions with status and rationale. Do not treat proposed options as finalized.

## Decision status

- **Proposed:** candidate option; not approved.
- **Accepted:** approved and should be followed.
- **Superseded:** replaced by a later decision.

## DEC-001 — Separate project from AI Developer Assistant
- **Status:** Accepted
- **Decision:** Build the Autonomous AI Software Engineer as a separate project/repository.
- **Rationale:** It should demonstrate a distinct product capability rather than duplicate the existing RAG-focused assistant.
- **Consequence:** Reuse ideas or well-isolated modules only when they genuinely fit; do not copy the whole previous codebase by default.

## DEC-002 — Human approval for consequential actions
- **Status:** Accepted
- **Decision:** The system must show proposed changes and require explicit approval before applying patches or performing external write actions.
- **Rationale:** AI-generated code can be incorrect, and repository actions can have side effects.
- **Consequence:** Approval state, diff review, and authorization checks are part of the design.

## DEC-003 — Prefer free/low-cost LLM access during learning
- **Status:** Accepted as a constraint; provider details remain provisional
- **Decision:** Prefer a free API tier such as Groq when the current model supports required tool calling.
- **Rationale:** Keep learning and experimentation affordable.
- **Consequence:** Handle quotas and provider changes gracefully; do not promise unlimited free usage.

## DEC-004 — Initial stack
- **Status:** Proposed
- **Candidates:** Python, FastAPI, Pydantic, LangGraph, Groq API, React, TypeScript.
- **Open:** Repository connection method, database, sandbox technology, and hosting.
- **Next step:** Validate requirements and record a decision before implementation.
