FROM python:3.13-slim

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy SILO
COPY . /app

# install dependencies
WORKDIR /app
RUN uv sync --frozen --no-cache

RUN useradd -m -u 1000 silo && chown -R silo:silo /app
USER silo

CMD ["/app/.venv/bin/fastapi", "run", "src/silo/main.py", "--port", "8000", "--host", "0.0.0.0"]