# PipelineWatch

An AI-augmented CI/CD failure analyzer. When a GitHub Actions workflow fails, PipelineWatch automatically fetches the failure details, summarizes the root cause using an LLM, and displays it on a dashboard.

## Architecture

- **Backend:** FastAPI (Python), webhook-driven (HMAC-verified), GitHub API + Groq LLM integration
- **Storage:** SQLite via SQLModel
- **Dashboard:** Server-rendered with Jinja2
- **CI/CD:** GitHub Actions → Docker build → auto-deploy to Render on push to `main`

## Two environments — read this before running locally

**1. Production (Render) — Phase 1 architecture**
The live deployed service processes webhooks inline: verify → fetch → analyze → save, no queue.
This is what actually receives GitHub's webhook in production.

**2. Local development (docker-compose) — Phase 2 architecture**
Running `docker-compose up -d` starts a local observability/decoupling stack:
- **RabbitMQ** — decouples the webhook handler from the slow AI analysis via a producer/consumer queue
- **worker.py** — a separate background process that consumes queued events and does the actual analysis
- **Loki + Promtail** — log aggregation
- **Grafana** — dashboards over the collected logs

This stack is **not deployed** — it demonstrates the decoupled, observable architecture a production system would use at greater scale, run locally for development and demonstration purposes.

## Local setup

```bash
# Start the observability/queue stack
docker-compose up -d

# Terminal 1 — API server
cd backend && source venv/bin/activate
uvicorn app:app --reload --port 8000

# Terminal 2 — worker (only consumes if RABBITMQ_URL is set in .env)
cd backend && source venv/bin/activate
python3 worker.py

# Terminal 3 — simulate a GitHub webhook event
python3 test_webhook_trigger.py <owner>/<repo> <run_id>
```

- Dashboard: http://localhost:8000/dashboard
- RabbitMQ management: http://localhost:15673
- Grafana: http://localhost:3033
