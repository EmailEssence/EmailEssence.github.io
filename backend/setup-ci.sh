#!/bin/bash
set -e

echo "Checking for UV installation..."
UV_PATH="$HOME/.local/bin"
if ! test -x "$UV_PATH/uv"; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if ! test -x "$UV_PATH/uv"; then
        echo "Error: UV installation failed at $UV_PATH/uv"
        exit 1
    fi
fi
echo "UV is ready at $UV_PATH/uv"

# Create virtual environment
echo "Creating virtual environment..."
"$UV_PATH/uv" venv

# Activate virtual environment (temporarily, just for path context for sed command)
echo "Activating virtual environment temporarily for shebang fix..."
source .venv/bin/activate

# Fix shebang line in uvicorn script (and potentially others if needed)
echo "Fixing shebang line in uvicorn..."
SHEBANG_LINE="#!/usr/bin/env python3"
SCRIPT_TO_FIX=".venv/bin/uvicorn"

echo "Checking if script exists: $SCRIPT_TO_FIX"
if test -f "$SCRIPT_TO_FIX"; then
  echo "Script $SCRIPT_TO_FIX exists."
  echo "Current shebang line (before sed):"
  head -n 1 "$SCRIPT_TO_FIX"

  sed -i "1s/^#!.*/$SHEBANG_LINE/" "$SCRIPT_TO_FIX"

  if [ $? -eq 0 ]; then # Check exit code of sed
    echo "sed command executed successfully."
  else
    echo "Error: sed command failed with exit code $?."
    exit 1 # Exit if sed fails
  fi

  echo "Shebang line in $SCRIPT_TO_FIX updated to: $SHEBANG_LINE"
  echo "New shebang line (after sed):"
  head -n 1 "$SCRIPT_TO_FIX"
else
  echo "Warning: Script $SCRIPT_TO_FIX not found, shebang fix skipped."
fi

# Deactivate virtual environment (no longer needed for shebang fix)
deactivate

# Activate virtual environment for dependency installation and run
echo "Activating virtual environment for dependency installation..."
source .venv/bin/activate

# Generate requirements file
echo "Generating requirements from pyproject.toml..."
"$UV_PATH/uv" pip compile --extra dev --extra docs --extra monitoring pyproject.toml > requirements-all.txt

# Install dependencies
echo "Installing dependencies..."
"$UV_PATH/uv" pip sync --python-version 3.12 requirements-all.txt

# Run tests
#echo "Running tests..."
#pytest