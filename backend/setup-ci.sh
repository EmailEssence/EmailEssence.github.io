#!/bin/bash
set -e

# cd backend

echo "Checking for UV installation..."

# Set UV path
UV_PATH="$HOME/.local/bin"
mkdir -p "$UV_PATH"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add UV to PATH if not already there
    if [[ ":$PATH:" != *":$UV_PATH:"* ]]; then
        export PATH="$PATH:$UV_PATH"
        echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
    fi

    # Verify UV installation
    if ! command -v uv &> /dev/null; then
        echo "Error: UV installation failed or PATH not updated correctly"
        exit 1
    fi
fi

echo "UV is ready"

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Generate requirements file
echo "Generating requirements from pyproject.toml..."
uv pip compile --extra dev --extra docs --extra monitoring pyproject.toml > requirements-all.txt

# Install dependencies
echo "Installing dependencies..."
uv pip sync --python-version 3.12 requirements-all.txt

# Run tests
echo "Running tests..."
pytest