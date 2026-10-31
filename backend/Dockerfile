# syntax=docker/dockerfile:1

# --- builder: installs runtime deps into an isolated venv, kept out of
# /app so a dev bind-mount of ./backend over /app never shadows installed
# packages ---
FROM python:3.12-slim AS builder
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- builder-dev: same venv, additionally layered with test tooling ---
FROM builder AS builder-dev

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# --- runtime-base: shared setup for both final images, before either
# venv or application code is copied in ---
FROM python:3.12-slim AS runtime-base
WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- dev: adds pytest and friends, used by docker-compose so tests can
# run inside the container ---
FROM runtime-base AS dev

COPY --from=builder-dev /opt/venv /opt/venv
COPY . .

USER app

# --- final: slim production image, no compilers/build tools, no test
# tooling, non-root user ---
FROM runtime-base AS final

COPY --from=builder /opt/venv /opt/venv
COPY . .

USER app
