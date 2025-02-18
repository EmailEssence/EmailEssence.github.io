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


# Activate the virtual environment by setting PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port
EXPOSE 8000

# Set the user to non-root
USER nonroot:nonroot

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]