#!/bin/bash
set -e  # Exit immediately if a command fails

# Log function for standardized output
log() {
    local level="$1"
    local message="$2"
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] [$level] $message"
}

log "INFO" "Starting CI environment setup..."

# Ensure we're in the backend directory
if [[ $(basename "$PWD") != "backend" ]]; then
    log "INFO" "Changing to backend directory..."
    cd backend || { log "ERROR" "Failed to change directory"; exit 1; }
fi

# Create log directory if it doesn't exist
mkdir -p logs

# Install UV package manager
log "INFO" "Checking for UV installation..."
UV_PATH="$HOME/.local/bin"
if ! test -x "$UV_PATH/uv"; then
    log "INFO" "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if ! test -x "$UV_PATH/uv"; then
        log "ERROR" "UV installation failed at $UV_PATH/uv"
        exit 1
    fi
fi
log "INFO" "UV is ready at $UV_PATH/uv"

# Create virtual environment
log "INFO" "Creating virtual environment..."
"$UV_PATH/uv" venv || { log "ERROR" "Failed to create virtual environment"; exit 1; }

# Activate virtual environment
log "INFO" "Activating virtual environment..."
source .venv/bin/activate || { log "ERROR" "Failed to activate virtual environment"; exit 1; }

# Fix shebang lines in scripts to ensure portability
log "INFO" "Fixing shebang lines in scripts for portability..."
SHEBANG_LINE="#!/usr/bin/env python3"
SCRIPTS_TO_FIX=(".venv/bin/uvicorn" ".venv/bin/python" ".venv/bin/pip")

for SCRIPT_TO_FIX in "${SCRIPTS_TO_FIX[@]}"; do
    if test -f "$SCRIPT_TO_FIX"; then
        log "INFO" "Fixing shebang in $SCRIPT_TO_FIX"
        sed -i "1s/^#!.*/$SHEBANG_LINE/" "$SCRIPT_TO_FIX" || {
            log "WARNING" "Failed to fix shebang in $SCRIPT_TO_FIX"
        }
    else
        log "WARNING" "Script $SCRIPT_TO_FIX not found, skipping shebang fix"
    fi
done

# Generate requirements file from pyproject.toml
# For deployment, we only need prod dependencies, not dev extras
log "INFO" "Generating production requirements from pyproject.toml..."
"$UV_PATH/uv" pip compile pyproject.toml > requirements.txt || {
    log "ERROR" "Failed to generate requirements.txt"
    exit 1
}

# Generate full requirements with all extras for monitoring in production
log "INFO" "Generating comprehensive requirements with monitoring extras..."
"$UV_PATH/uv" pip compile --extra monitoring pyproject.toml > requirements-all.txt || {
    log "ERROR" "Failed to generate requirements-all.txt"
    exit 1
}

# Generate development requirements with testing tools (pytest, etc.)
log "INFO" "Generating development requirements with testing dependencies..."
"$UV_PATH/uv" pip compile --extra dev pyproject.toml > requirements-dev.txt || {
    log "ERROR" "Failed to generate requirements-dev.txt"
    exit 1
}

# Install ALL dependencies including development dependencies for CI
log "INFO" "Installing ALL dependencies including development dependencies..."
"$UV_PATH/uv" pip sync --python-version 3.12 requirements-all.txt requirements-dev.txt || {
    log "ERROR" "Failed to install dependencies"
    exit 1
}

# Verify critical dependencies are installed
log "INFO" "Verifying critical dependencies..."
python -c "import fastapi, uvicorn, motor" || {
    log "ERROR" "Critical dependency verification failed"
    exit 1
}

# Verify testing dependencies are installed
log "INFO" "Verifying testing dependencies..."
python -c "import pytest" || {
    log "ERROR" "Testing dependency verification failed"
    exit 1
}

log "INFO" "CI environment setup completed successfully"
