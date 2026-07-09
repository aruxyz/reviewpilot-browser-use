FROM python:3.12-slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl ca-certificates git \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libdbus-1-3 libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libxshmfence1 fonts-liberation fonts-noto-color-emoji && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY reviewpilot/ ./reviewpilot/

RUN pip install --no-cache-dir . && \
    pip install --no-cache-dir PyGithub>=2.0.0 && \
    python -m playwright install chromium --with-deps

ENTRYPOINT ["python", "-m", "reviewpilot.github.action"]
