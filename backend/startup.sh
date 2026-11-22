#!/bin/bash
(while true; do
  echo "[worker] starting"
  python -m arq worker.main.WorkerSettings
  echo "[worker] exited with code $?, restarting in 3s..."
  sleep 3
done) &

echo "[startup] starting uvicorn"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log