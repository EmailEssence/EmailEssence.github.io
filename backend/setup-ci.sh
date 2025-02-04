#!/bin/bash

# Exit on error
set -e

echo "Checking for UV installation..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "UV already installed"
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install all dependencies including dev dependencies
echo "Installing dependencies..."
uv pip sync --python-version 3.12 --extra-index-url https://pypi.org/simple pyproject.toml

# Run tests
echo "Running tests..."
pytest

# The virtual environment will automatically deactivate when the script ends
echo "CI setup and testing complete!"
