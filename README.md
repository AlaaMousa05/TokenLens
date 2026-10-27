# TokenLens

TokenLens is a sandbox for comparing LLM providers side by side —
running the same prompts against multiple models, judging/scoring the
results, and tracking cost. This repo holds the full stack: a Next.js
frontend and a FastAPI backend with a Postgres-backed job queue (ARQ +
Redis) for running evaluations in the background.


## Running it

```bash
cp .env.example .env   # fill in real values, especially provider API keys
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (health check at `/health`)
- Postgres: localhost:5432, Redis: localhost:6379 (exposed for local
  debugging with a DB client / `redis-cli`)

## Services

| Service    | What it does |
|------------|---------------|
| `postgres` | Primary datastore. Named volume `postgres_data` persists data across restarts. |
| `redis`    | Backs the ARQ job queue used by `worker`. |
| `backend`  | FastAPI app (`app/main.py`), runs with `--reload` against a bind-mounted `./backend`. `GET /health` reports process status plus live Postgres and Redis connectivity (`"degraded"` if either check fails, rather than reporting `"ok"` incorrectly). |
| `worker`   | Same build/image as `backend` — only the `command:` differs (runs `arq worker.main.WorkerSettings` instead of `uvicorn`). No separate Dockerfile. |
| `frontend` | Next.js app, built with the `dev` stage (`next dev`, source bind-mounted) for local development. The `runner` stage (standalone production build) is also defined in `frontend/Dockerfile` for later deployment use. |

## Environment variables

All variables live in `.env` (see `.env.example` for the full list with
comments):

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — used by the
  `postgres` service itself.
- `DATABASE_URL`, `REDIS_URL` — full connection strings read directly by
  `backend`/`worker` via `app/config.py`. These point at the `postgres`
  and `redis` service names, not `localhost`.
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` — LLM provider
  credentials. Passed to `backend` and `worker` only, via `env_file: .env`
  in `docker-compose.yml` — `frontend` never receives this file, so a key
  can't leak into a browser bundle.
- `NEXT_PUBLIC_API_URL` — the only value passed to `frontend`; not a
  secret, it's the URL the browser uses to reach the backend.

