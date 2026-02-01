# docker/Dockerfile
FROM ghcr.io/astral-sh/uv:0.9.16-python3.13-trixie

RUN apt-get update && apt-get install -y certbot
RUN apt-get install -y libmariadb-dev pkg-config python3-dev default-libmysqlclient-dev build-essential apache2 apache2-dev

WORKDIR /app

# Build argument for version
ARG APP_VERSION=dev

# Copy from project root
COPY pyproject.toml uv.lock ./
COPY src ./src

# Install dependencies
RUN uv sync --frozen --no-cache

EXPOSE 5000

ENV PYTHONPATH=/app/src

ENV APP_VERSION=${APP_VERSION}

CMD ["uv", "run", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "info", "src.app:create_app()"]
