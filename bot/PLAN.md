# Bot Development Plan

## Phase 1: Scaffold & Architecture (Task 1)
Establish a testable bot architecture where command handlers are isolated from the Telegram transport layer. Implement a `--test` CLI flag to verify command outputs locally without network dependencies. Set up the `pyproject.toml` for strict dependency management using `uv`.

## Phase 2: Backend API Integration (Task 2)
Implement the `services/` directory with an HTTP client to communicate with the LMS FastAPI backend. Handlers will be updated to fetch real data from endpoints like `/health`, `/items/`, and `/analytics/`. Error handling will be added to manage backend downtime gracefully.

## Phase 3: LLM Intent Routing (Task 3)
Integrate the LLM coding agent (via the Qwen/OpenRouter proxy on port 42005) into the message processing pipeline. Replace exact command matching with natural language understanding. The LLM will classify user intent and extract entities (e.g., mapping "what's my score for lab 4?" to `get_score(task="lab-04")`).

## Phase 4: CI/CD & Deployment
Ensure the bot runs reliably on the remote VM using `nohup`. Follow strict Git workflow (branching, PRs, conventional commits) for every phase to maintain a clean history.
