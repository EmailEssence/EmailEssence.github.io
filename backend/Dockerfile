# Builder stage
FROM python:3.12-slim-bookworm AS builder

# Install uv (using the recommended copy method)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy ONLY the requirements files first
COPY backend/pyproject.toml backend/requirements*.txt ./

# Create a virtual environment
RUN uv venv

# Install dependencies into the virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    . .venv/bin/activate && uv pip install -r requirements.txt

# Copy the rest of the project
COPY backend/ ./

# Install the project itself into the virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    . .venv/bin/activate && uv pip install .

# Runner stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Create a non-root user and group
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the backend application code from builder stage (We still need this!)
COPY --from=builder /app .

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Activate the virtual environment by setting PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port
EXPOSE 8000

# Set the user to non-root
USER nonroot:nonroot

# Required Environment Variables (these should be set when running the container):
# - mongo_uri: MongoDB connection string
# - google_client_id: Google OAuth client ID
# - google_client_secret: Google OAuth client secret
# - email_account: Email account to use
# - openai_api_key: OpenAI API key
#
# Optional Environment Variables:
# - environment: The environment to run in (default: development)
# - summarizer_provider: AI provider for summarization (default: openai)
# - summarizer_model: Model to use for summarization (default: gpt-4o-mini)

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development mode can be enabled by overriding CMD when running the container:
# docker run --env-file .env -v ./backend:/app email-essence-backend uvicorn main:app --host 0.0.0.0 --port 8000 --reload
#
# NOTE ABOUT VOLUMES:
# When running with volume mounts (e.g., -v ./backend:/app), files in the container 
# will be overwritten by the host files. This is intentional for development to enable
# live code reloading, but means that any files generated during build that don't
# exist on the host will not be available at runtime. Keep this in mind especially
# when running in development mode.