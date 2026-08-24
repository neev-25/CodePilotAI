@echo off
echo ===========================
echo  CodePilot AI - Frontend
echo ===========================

REM Check if .env.local exists
if not exist ".env.local" (
    echo [WARNING] .env.local not found. Using defaults (backend at http://127.0.0.1:8000).
    echo To override, copy .env.example to .env.local and edit NEXT_PUBLIC_API_BASE_URL.
    echo.
)

echo [INFO] Starting Next.js frontend on http://localhost:3000
npm run dev

pause
