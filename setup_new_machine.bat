@echo off
:: Aruni Learning System - New Machine Setup (Windows)
:: Run this once in Command Prompt or PowerShell on any Windows machine.
:: Usage: setup_new_machine.bat

setlocal enabledelayedexpansion

set "ARUNI_DIR=%~dp0"
set "CREDS_FILE=%ARUNI_DIR%google_creds.json"
set "ENV_FILE=%ARUNI_DIR%.env"

echo.
echo ======================================
echo   Aruni Learning System - Setup
echo ======================================
echo.

:: ── 1. Python ─────────────────────────────────────────────────────────────
echo [ 1/4 ] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found.
    echo   Download from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   OK: %%i

:: ── 2. Dependencies ────────────────────────────────────────────────────────
echo.
echo [ 2/4 ] Installing Python dependencies...
pip install -q gspread google-auth
if errorlevel 1 (
    echo   ERROR: pip install failed.
    echo   Try running as Administrator, or: pip install --user gspread google-auth
    pause
    exit /b 1
)
echo   OK: gspread and google-auth installed

:: ── 3. Google credentials ──────────────────────────────────────────────────
echo.
echo [ 3/4 ] Checking Google credentials...
if not exist "%CREDS_FILE%" (
    echo.
    echo   google_creds.json not found.
    echo.
    echo   You need the service account key file.
    echo   Get it from whoever manages the Aruni system
    echo   and copy it to:
    echo.
    echo     %CREDS_FILE%
    echo.
    pause
    if not exist "%CREDS_FILE%" (
        echo   ERROR: File still not found. Exiting.
        exit /b 1
    )
)
echo   OK: google_creds.json found

:: ── 4. .env file ───────────────────────────────────────────────────────────
echo.
echo [ 4/4 ] Checking .env...
if not exist "%ENV_FILE%" (
    copy "%ARUNI_DIR%.env.example" "%ENV_FILE%" >nul
    echo   Created .env (SHEET_ID pre-filled)
)

:: ── Verify connection ───────────────────────────────────────────────────────
echo.
echo   Verifying Google Sheet connection...
python "%ARUNI_DIR%setup.py" status
if errorlevel 1 (
    echo.
    echo   ERROR: Could not connect to Google Sheet.
    echo   Check SHEET_ID and google_creds.json, then re-run.
    pause
    exit /b 1
)

:: ── Done ───────────────────────────────────────────────────────────────────
echo.
echo ======================================
echo   Setup complete!
echo ======================================
echo.
echo To add a new user:
echo   python setup.py add-user
echo.
echo To start a learning session, cd into the user folder and run your LLM:
echo   cd users\varnika
echo   claude         (Claude Code)
echo   gemini         (Gemini CLI)
echo   codex          (OpenAI Codex)
echo.
pause
