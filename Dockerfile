FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install a tiny HTTP client for container healthchecks (pick one)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# App code and tests
COPY app ./app
# COPY tests ./tests

EXPOSE 8080
# For dev you can add --reload; for stability leave it off
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
