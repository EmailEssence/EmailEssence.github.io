#!/bin/bash

# Exit on error
set -e

# Move to backend directory
cd backend

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

# Install dependencies with additional test requirements
echo "Installing dependencies..."
uv pip install -r requirements.txt -r requirements-test.txt

# Run tests
echo "Running tests..."
pytest

# The virtual environment will automatically deactivate when the script ends
echo "CI setup and testing complete!"