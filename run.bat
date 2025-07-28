@echo off
echo Git Merge Conflict Resolver Backend - Development Commands
echo ========================================================

if "%1"=="install" (
    echo Installing dependencies...
    pip install -r requirements.txt
    goto :end
)

if "%1"=="setup" (
    echo Setting up development environment...
    pip install -r requirements.txt
    copy env.example .env
    echo Please edit .env file with your Supabase credentials
    goto :end
)

if "%1"=="test" (
    echo Running tests...
    python run_tests.py
    goto :end
)

if "%1"=="lint" (
    echo Running code linting...
    black src/ tests/ --check
    isort src/ tests/ --check-only
    flake8 src/ tests/
    goto :end
)

if "%1"=="format" (
    echo Formatting code...
    black src/ tests/
    isort src/ tests/
    goto :end
)

if "%1"=="clean" (
    echo Cleaning up cache files...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"
    if exist htmlcov rmdir /s /q htmlcov
    if exist .pytest_cache rmdir /s /q .pytest_cache
    if exist .coverage del .coverage
    goto :end
)

if "%1"=="run" (
    echo Starting development server...
    python start.py
    goto :end
)

if "%1"=="migrate" (
    echo Running database migrations...
    alembic upgrade head
    goto :end
)

if "%1"=="migration" (
    set /p message="Enter migration message: "
    echo Creating new migration...
    alembic revision --autogenerate -m "%message%"
    goto :end
)

echo Available commands:
echo   install   - Install dependencies
echo   setup     - Setup development environment
echo   test      - Run tests with coverage
echo   lint      - Run code linting
echo   format    - Format code with black and isort
echo   clean     - Clean up cache files
echo   run       - Start development server
echo   migrate   - Run database migrations
echo   migration - Create new migration
echo.
echo Usage: run.bat [command]

:end 