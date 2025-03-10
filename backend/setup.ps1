# PowerShell setup script for local development

# Helper functions for formatted output
function Print-Step {
    param([string]$message)
    Write-Host "==>" -ForegroundColor Green -NoNewline
    Write-Host " $message"
}

function Print-Warning {
    param([string]$message)
    Write-Host "WARNING:" -ForegroundColor Yellow -NoNewline
    Write-Host " $message"
}

function Print-Error {
    param([string]$message)
    Write-Host "ERROR:" -ForegroundColor Red -NoNewline
    Write-Host " $message"
    return $false
}

# Move to backend directory if not already in
if ((Get-Item -Path ".").Name -ne "backend") {
    Print-Step "Changing to backend directory..."
    try {
        Set-Location -Path "backend"
    } catch {
        Print-Error "Failed to change to backend directory"
        exit 1
    }
}

Print-Step "Setting up development environment..."

# Check if UV is installed
Print-Step "Checking for UV installation..."
$uvInstalled = $null
try {
    $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
} catch {
    # Ignore error
}

if (-not $uvInstalled) {
    Print-Step "UV not found, installing..."
    try {
        Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install.ps1
        .\install.ps1
        # Clean up install script
        Remove-Item install.ps1
        Print-Step "UV installation complete"
        
        # Add to current session path if needed
        $uvPath = Join-Path $env:USERPROFILE ".local\bin"
        if ($env:PATH -notlike "*$uvPath*") {
            $env:PATH = "$env:PATH;$uvPath"
        }
    } catch {
        Print-Error "Failed to install UV: $_"
        exit 1
    }
} else {
    Print-Step "UV already installed"
}

# Create virtual environment
Print-Step "Creating virtual environment..."
try {
    uv venv
} catch {
    Print-Error "Failed to create virtual environment: $_"
    exit 1
}

# Activate virtual environment
Print-Step "Activating virtual environment..."
try {
    # PowerShell activation
    .\.venv\Scripts\Activate.ps1
} catch {
    Print-Error "Failed to activate virtual environment: $_"
    exit 1
}

# Generate development requirements with dev extras
Print-Step "Generating development requirements..."
try {
    uv pip compile --extra dev pyproject.toml > requirements-dev.txt
} catch {
    Print-Error "Failed to generate requirements file: $_"
    exit 1
}

# Install dependencies from the generated requirements file
Print-Step "Installing development dependencies..."
try {
    uv pip sync --python-version 3.12 requirements-dev.txt
} catch {
    Print-Error "Failed to install dependencies: $_"
    exit 1
}

# Check for .env file
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Print-Warning "No .env file found. Creating from .env.example..."
        Copy-Item ".env.example" ".env"
        Print-Step "Please update the .env file with your credentials."
    } else {
        Print-Warning "No .env or .env.example file found. You may need to create one manually."
    }
}

Print-Step "Setup complete! Your development environment is ready."
Print-Step "To start the application in development mode, run: 'uvicorn main:app --reload'"

# Keep the window open
Read-Host -Prompt "Press Enter to exit" 