# Development Plan: GitAnalyze Distributed RAG Engine

## Phase 1: Distributed Infrastructure (Redis & Workers)
*   **Goal:** Move repository analysis from the main thread to background workers.
*   **Plan:**
    1.  Install `redis` and `rq` (Redis Queue).
    2.  Create a separate `worker.py` that listens to a Redis queue.
    3.  Move the heavy functions (`clone_repo`, `build_repo_index`) to the worker script.
    4.  Update `main.py` to enqueue the analysis task and return a `job_id` instead of waiting for completion.

## Phase 2: Real-time Communication (WebSockets)
*   **Goal:** Stream analysis progress to the frontend without page reloads.
*   **Plan:**
    1.  Implement `fastapi.WebSocket` routes.
    2.  Frontend: Connect via WebSocket to listen for progress updates (e.g., "Cloning...", "Indexing...").
    3.  Backend: Update the Redis worker to emit status messages to the WebSocket client via a shared Pub/Sub channel or simple state tracker.

## Phase 3: Search Precision (Semantic Vector Optimization)
*   **Goal:** Increase retrieval relevance.
*   **Plan:**
    1.  Implement a more robust "Code-Aware" chunker (instead of just 120 lines, use AST parsing or function-level splitting if possible).
    2.  Implement a re-ranking step or use hybrid search (metadata filters on file extension + vector search).

## Phase 4: Frontend Modernization (TypeScript)
*   **Goal:** Replace Jinja2 templates with a modern SPA or refined dynamic interface.
*   **Plan:**
    1.  Convert the static HTML template to a React/TypeScript interface.
    2.  Integrate the WebSocket client logic in the frontend.

---

### Getting Started
To stay within the "free" and local environment, you'll need:
1.  **Docker:** (Highly recommended) to run Redis locally with one command: `docker run -p 6379:6379 -d redis`.
2.  **Redis Python Client:** `redis` and `rq` libraries.

**Shall we start with Phase 1: Moving repository analysis to Redis workers?**
