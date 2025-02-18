#!/bin/bash
set -e

echo "Checking for UV installation..."

UV_PATH="$HOME/.local/bin" # Correct path within Render: /opt/render/.local/bin

# Check if UV is installed (using full path in case PATH isn't set yet)
if ! test -x "$UV_PATH/uv"; then # Check if executable exists and is executable
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Verify UV installation (using full path)
    if ! test -x "$UV_PATH/uv"; then
        echo "Error: UV installation failed at $UV_PATH/uv"
        exit 1
    fi
fi

echo "UV is ready at $UV_PATH/uv"

# Create virtual environment (using full path to uv)
echo "Creating virtual environment..."
"$UV_PATH/uv" venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Generate requirements file (using full path to uv)
echo "Generating requirements from pyproject.toml..."
"$UV_PATH/uv" pip compile --extra dev --extra docs --extra monitoring pyproject.toml > requirements-all.txt

# Install dependencies (using full path to uv)
echo "Installing dependencies..."
"$UV_PATH/uv" pip sync --python-version 3.12 requirements-all.txt

# Run tests
#echo "Running tests..."
#pytest