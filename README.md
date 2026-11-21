# TokenLens

TokenLens is a sandbox for comparing LLM providers side by side —
running the same prompts against multiple models, judging/scoring the
results, and tracking cost. This repo holds the full stack: a Next.js
frontend and a FastAPI backend with a Redis-backed job queue (ARQ) for
running evaluations in the background and Postgres for persistent data.


## Running it

```bash
cp .env.example .env   # fill in real values, especially provider API keys
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (health check at `/health`)
- Postgres: localhost:5432, Redis: localhost:6379 (exposed for local
  debugging with a DB client / `redis-cli`)

### Running the backend and worker without Docker

1. Create a [Render Key Value](https://render.com/docs/key-value) instance.
   In its Networking settings, allow the public IP address of each machine
   that will connect externally. Copy the **External URL** from its Connect
   menu; external connections use TLS and require authentication. Select the
   `noeviction` memory policy for a job queue. Free instances do not persist
   queued jobs across restarts.
2. Copy `.env.example` to `backend/.env`, set `REDIS_URL` to that external
   `rediss://` URL, and set `DATABASE_URL` to your reachable PostgreSQL
   database, `JWT_SECRET_KEY` to a long random secret, and the provider API
   keys. Both processes read `backend/.env`; environment variables override
   that file. Keep the URL and all credentials private and out of Git.
3. From the repository root in PowerShell, install the backend dependencies
   and start the API:

   ```powershell
   cd backend
   python -m pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
   ```

4. In a separate PowerShell terminal, start the worker from the same
   `backend` directory and Python environment:

   ```powershell
   cd backend
   python -m arq worker.main.WorkerSettings
   ```

The worker must remain running: clicking **Run Evaluation** queues a job; it
does not launch a worker process. The API and worker must use the same Redis
instance, database, and provider credentials. Check `http://127.0.0.1:8000/health`
for Redis and database connectivity. Services running on Render in the same
region can use the Key Value internal URL instead.

The API logs startup and shutdown, HTTP method, route template, status and
duration, and run enqueue outcomes. It does not include request bodies,
credentials, query strings, or actual path parameters in these logs. Keep
Uvicorn's access log disabled (`--no-access-log`) when using another launch
command to avoid duplicate logs and raw URLs.

The worker logs its process ID at startup and shutdown, job and run IDs,
model-call and judging progress, statuses, and failures. To follow the API and
worker logs when using Docker Compose, run `docker compose logs -f backend worker`.
Application progress logs omit prompts, responses, and credentials; framework
exception logs and external logging systems may have different contents.

### Live run updates

Authenticated clients can `GET /runs/{run_id}/events` with an
`Authorization: Bearer <access_token>` header. The owner receives an SSE
`update` event with JSON `{"run_id":"<uuid>","status":"<status>"}` immediately
and after committed changes; statuses are `queued`, `running`, `completed`,
`failed`, or `cancelled`. Fetch the existing run and paginated results REST
endpoints on each event. No provider token streaming is available: complete
responses and individual judgments are committed as they arrive. A terminal
update closes the stream. Connections are independent and reconnection always
starts with the current committed state, rather than replaying event history.
Polling occurs once per second, so rapid commits can be coalesced; the REST
reload sees the latest state. Heartbeat comments keep idle streams active.
Clients should reconnect after a disconnect or stream error; credentials must
not be placed in the URL.

The worker commits each response before judging and each judgment separately.
Failures retain partial results and candidate cost; a restarted job reuses
persisted results and judgments rather than repeating them. Judge costs remain
on the judgments, while the run total is candidate cost as before.
Workers use a renewable per-run Redis lease to prevent duplicate jobs from
calling providers concurrently. A job that cannot acquire the lease defers
using ARQ's retry mechanism; loss of the lease cancels work and defers the
retry. All workers must use the same Redis instance. Leases expire after 60
seconds if a worker dies; prolonged contention can exhaust ARQ's configured
retry limit, without changing the original run. A provider call already in
flight at a crash, lease expiry, or database commit failure can still be
repeated and billed again. Application progress logs do not include prompts
or responses.

Deployment adds the `runs.update_version` column automatically: the API checks
after `create_all`, and the worker checks before processing a job, so neither
assumes Alembic ran. PostgreSQL and SQLite are supported. The database user
must have permission to alter `runs`; a read-only database or failed migration
prevents startup/job processing rather than silently disabling updates. Back up
the database and allow for a brief schema lock before deploying. Deploy API and
worker together: old workers can write results without notifying new streams.

The Azure workflow packages the tracked `backend/tokenlens.db` as
`seed/tokenlens.db`; it does not itself configure `DATABASE_URL` or copy that
seed into a persistent location. Verify the app's actual database URL and
persistent storage configuration before deployment. An existing writable
database, or a writable copy of that older seed, is upgraded in place on first
use; the packaged seed itself is not modified in Git.

The additive upgrade does not stamp Alembic history. If managing schema with
Alembic, run `python -m alembic upgrade head` from `backend` only after
checking its current revision and schema. In particular, a `create_all`
database with no Alembic revision but all `0002_execution_columns` columns
must first be verified and stamped at `0002_execution_columns`; otherwise that
older migration attempts to add existing columns. Revision 0003 safely skips
the column if startup already added it. Automatic startup upgrade covers only
this new column, not other missing historical migrations.

The stream's change version is updated by the ORM when results or judgments change; code that writes these
tables using bulk SQL or outside the application must also increment the
affected run's `update_version` in the same transaction. New databases created
by the application already include the column.

Docker Compose continues to use the root `.env` and local Redis by default.
If you set its `REDIS_URL` to the external URL, both containers use it, although
Compose still starts its local Redis service.

Provider requests omit temperature for all models, so providers use their
defaults and judgment scores may vary between runs. The API retains the
`temperature` field for compatibility, but it does not affect provider
requests. The `gpt-6-astra` context window and pricing configuration are
provisional.

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
  `backend`/`worker` via `app/config.py`. The example points at the Docker
  `postgres` and `redis` service names, not `localhost`.
- `JWT_SECRET_KEY` — secret used to sign access tokens; use a long random
  value and keep it consistent across backend instances.
- `AZURE_API_KEY`, `GOOGLE_API_KEY` — LLM provider
  credentials. Passed to `backend` and `worker` only, via `env_file: .env`
  in `docker-compose.yml` — `frontend` never receives this file, so a key
  can't leak into a browser bundle.
- `NEXT_PUBLIC_API_URL` — the only value passed to `frontend`; not a
  secret, it's the URL the browser uses to reach the backend. In development
  it defaults to `http://127.0.0.1:8000`; production retains the deployed
  backend URL unless overridden. When accessing the frontend from another
  device, set it to a backend address reachable from that device instead.
- `CORS_ALLOWED_ORIGINS` — comma-separated frontend origins allowed by the
  backend CORS middleware; defaults to `*` (all origins, without browser
  credentials). Set specific origins instead to restrict access and allow
  credentialed cross-origin requests.
