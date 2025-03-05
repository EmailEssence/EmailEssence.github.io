#!/bin/bash
set -e  # Exit immediately if a command fails

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# Move to backend directory if not already in
if [[ $(basename "$PWD") != "backend" ]]; then
    print_step "Changing to backend directory..."
    cd backend || { print_error "Failed to change to backend directory"; exit 1; }
fi

print_step "Setting up development environment..."

# Check if UV is installed
print_step "Checking for UV installation..."
if ! command -v uv &> /dev/null; then
    print_step "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh || { print_error "Failed to install UV"; exit 1; }
    source "$HOME/.local/bin/env" || { print_warning "Failed to source UV environment, please run: source $HOME/.local/bin/env"; }
    print_step "UV installation complete"
else
    print_step "UV already installed"
fi

# Create virtual environment
print_step "Creating virtual environment..."
uv venv || { print_error "Failed to create virtual environment"; exit 1; }

# Activate virtual environment
print_step "Activating virtual environment..."
source .venv/bin/activate || { print_error "Failed to activate virtual environment"; exit 1; }

# Generate development requirements with dev extras
print_step "Generating development requirements..."
uv pip compile --extra dev pyproject.toml > requirements-dev.txt || { 
    print_error "Failed to generate requirements file"; 
    exit 1; 
}

# Install dependencies from the generated requirements file
print_step "Installing development dependencies..."
uv pip sync --python-version 3.12 requirements-dev.txt || { 
    print_error "Failed to install dependencies"; 
    exit 1; 
}

# Check for .env file
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        print_warning "No .env file found. Creating from .env.example..."
        cp .env.example .env
        print_step "Please update the .env file with your credentials."
    else
        print_warning "No .env or .env.example file found. You may need to create one manually."
    fi
fi

print_step "${GREEN}Setup complete! Your development environment is ready.${NC}"
print_step "To start the application in development mode, run: 'uvicorn main:app --reload'"