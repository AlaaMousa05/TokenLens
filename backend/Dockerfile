# syntax=docker/dockerfile:1

# --- builder: installs deps into an isolated venv, kept out of /app so a
# dev bind-mount of ./backend over /app never shadows installed packages ---
FROM python:3.12-slim AS builder
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- final: slim runtime image, no compilers/build tools, non-root user ---
FROM python:3.12-slim AS final
WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /opt/venv /opt/venv
COPY . .

USER app
EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
