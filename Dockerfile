# -------- Build Stage --------
FROM python:3.10-bullseye AS build

WORKDIR /app

# Fix apt sources to HTTPS
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list \
 && sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list

# Install build dependencies (Removed python3-dev as it was for Cython)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | bash

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Create virtual environment and sync dependencies
# This creates the /app/.venv directory
RUN /root/.local/bin/uv sync --frozen --no-install-project

# Copy the rest of the source
COPY . .

# -------- Runtime Stage --------
FROM python:3.10-bullseye

WORKDIR /app

# Fix apt sources
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list \
 && sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy pre-built virtual environment from build stage
COPY --from=build /app/.venv /app/.venv

# Copy source code
COPY . .

# Set PATH for virtual environment so uvicorn is found
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]