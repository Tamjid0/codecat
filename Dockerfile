FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Reproducible tool versions
RUN npm install -g npm@10.8.0 && npm --version && git --version

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e "."

# Sandbox image is same as app image for reproducibility
ENTRYPOINT ["python", "-m", "codecat"]
CMD ["--help"]
