#!/bin/bash

# Move to backend directory if not already in
cd backend

echo "Checking for UV installation..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
else
    echo "UV already installed"
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies using pyproject.toml
echo "Installing dependencies..."
uv pip sync --python-version 3.12 pyproject.toml

echo "Setup complete!"