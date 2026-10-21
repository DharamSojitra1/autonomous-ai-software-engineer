# Project Context and Memory

This document is the concise handoff context for a new chat or AI assistant. Keep it current.

## Developer context

- The developer has experience with blockchain development and is transitioning toward GenAI and Agentic AI.
- The developer has already built a separate project called **AI Developer Assistant**.
- That existing project README documents FastAPI, LangChain, LangGraph, Groq, Gemini embeddings, ChromaDB, hybrid retrieval, reranking, agent routing, tool use, authentication, streaming, evaluation, testing, and deployment configuration.
- The new project should build on lessons learned, but should remain a separate repository/product with a distinct core capability.

## New project

- Working name: **Autonomous AI Software Engineer**.
- Name is provisional and can be changed later.
- Core difference: operate on real software repositories through controlled inspect → investigate → propose → approve → test → report workflows, rather than mainly answering developer questions.
- Intended portfolio emphasis: Agentic AI, code/repository understanding, tool orchestration, safe code changes, automated testing, evaluation, and production engineering.

## Current status

- Phase: planning and documentation.
- No implementation should be assumed to exist merely because it appears in a plan or architecture document.
- Product requirements and safety boundaries should be agreed before coding begins.
- The user prefers to understand the project and its design before rushing into implementation.
- Cost matters: start with available free LLM API access where feasible, including a compatible Groq model, while respecting changing quotas and model capabilities.

## Reuse strategy

Potentially reusable concepts or modules from the previous project:
- FastAPI patterns and Pydantic schemas
- Groq LLM integration and retry handling
- LangGraph workflows
- Authentication patterns, if needed
- Streaming, logging, tests, and evaluation practices

Do not copy the entire previous project by default. Inspect source code, license, coupling, and actual requirements before reusing code. Reuse only what is useful and appropriate.

## Open questions

- Final product name and repository name
- GitHub App vs. personal access token vs. ZIP upload for the first repository connection flow
- Initial supported language/framework (Python/FastAPI is a reasonable candidate, but not finalized)
- Sandbox technology and deployment constraints
- Exact model and fallback strategy based on current tool-calling support and free-tier limits
- Whether code RAG is needed for the MVP or can be deferred
- Hosting and persistent storage choices

## Update policy

Update this file when the project goal, major constraints, current phase, or important decisions change. Keep implementation status factual.
