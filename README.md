# ADK Agent2Agent Microservice (Production-minded)

This project shows an Agent2Agent-style orchestrator using three agents (ResearchAgent, AnalysisAgent, SummaryAgent).
The implementation will use Google ADK Agents if the `adk` package is installed and environment variables point to a model ARN;
otherwise it falls back to local stub agents for development and testing.

Features:
- Sequential Agent-to-Agent orchestration (Agent1 -> Agent2 -> Agent3)
- SSE streaming endpoint `/process` that streams per-agent progress updates (SSE `data:` JSON messages)
- Timeouts, retries (agent-level), structured logging (structlog), Prometheus metrics
- Dockerfile included

## Quick start (local)

1. Create venv and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Run the service:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

3. Health: GET http://localhost:8000/health
   Metrics: GET http://localhost:8000/metrics
   Process (SSE): POST http://localhost:8000/process with JSON body {"query": "your text"}

## Notes on ADK integration
- If you have Google ADK and want to use real models, install the ADK package and set environment variables (e.g., MODEL_PROVIDER=adk and MODEL_ARN).
- The agent wrapper expects ADK `Agent` to have an async `run` method. Adjust `app/agents.py` if your ADK SDK differs.
