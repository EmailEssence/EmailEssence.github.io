@echo off

cd backend

echo Checking for UV installation...

:: Check if UV is installed
where uv >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo UV not found, installing...
    powershell -Command "Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install.ps1; .\install.ps1"
    :: Clean up install script
    del install.ps1
) ELSE (
    echo UV already installed
)

:: Create virtual environment
echo Creating virtual environment...
uv venv

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
uv pip install -r requirements.txt

echo Setup complete!

cmd /k