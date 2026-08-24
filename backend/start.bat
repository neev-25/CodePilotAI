@echo off
echo ===========================
echo  CodePilot AI - Backend
echo ===========================

REM Check if .env exists, prompt user if not
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please copy .env.example to .env and add your GEMINI_API_KEY.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start backend server
echo [INFO] Starting FastAPI backend on http://localhost:8000
python -m uvicorn main:app --reload --port 8000

pause
