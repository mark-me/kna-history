# Application Dockerfile for KNA History
FROM ghcr.io/astral-sh/uv:0.9.16-python3.13-trixie

RUN apt-get update && apt-get install -y \
    certbot \
    libmariadb-dev \
    pkg-config \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    apache2 \
    apache2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build argument for version (will be passed from GitHub Actions)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Copy source code
COPY src ./src

# Install dependencies
RUN uv sync --frozen --no-cache

# Set Python path
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

# Run with gunicorn
CMD ["uv", "run", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "info", "src.app:create_app()"]
