@echo off
cd backend

echo Checking for UV installation...

:: Get current user's home directory and UV path
set "USER_HOME=%USERPROFILE%"
set "UV_PATH=%USER_HOME%\.local\bin"

:: Check if UV is installed
where uv >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo UV not found, installing...
    powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install.ps1; .\install.ps1"
    :: Clean up install script
    del install.ps1
    
    :: Add UV to PATH and update current session
    set "PATH=%PATH%;%UV_PATH%"
    setx PATH "%PATH%"
    
    :: Verify UV is now available
    where uv >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Error: UV installation failed or PATH not updated correctly
        exit /b 1
    )
)

echo UV is ready

:: Create virtual environment
echo Creating virtual environment...
"%UV_PATH%\uv.exe" venv

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Generate requirements file with all extras
echo Generating requirements from pyproject.toml...
uv pip compile --extra dev --extra docs --extra monitoring pyproject.toml > requirements-all.txt

:: Install all dependencies
echo Installing dependencies...
uv pip sync --python-version 3.12 requirements-all.txt

:: Run tests
echo Running tests...
pytest

ENDLOCAL