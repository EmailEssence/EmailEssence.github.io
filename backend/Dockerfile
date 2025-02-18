# Builder stage
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app/backend

# Copy only necessary backend files (relative to /backend)
COPY pyproject.toml requirements.txt requirements-dev.txt requirements-all.txt README.md /app/backend/
COPY app /app/backend/app
COPY main.py config.py database.py /app/backend/

# Install uv package manager
RUN pip install uv

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt .

# Runner stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Create a non-root user and group
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the backend application code
COPY --from=builder /app/backend .

# Expose the port
EXPOSE 8000

# Set the user to non-root
USER nonroot:nonroot

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]