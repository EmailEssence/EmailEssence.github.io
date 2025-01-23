# chmod +x setup.sh to make it executable

#!/bin/bash

# Move to backend directory
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

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

echo "Setup complete!"