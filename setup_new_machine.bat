@echo off
:: Aruni Learning System - New Machine Setup (Windows)
:: Run this once in Command Prompt or PowerShell on any Windows machine.
:: Usage: setup_new_machine.bat

setlocal enabledelayedexpansion

set "ARUNI_DIR=%~dp0"
set "CREDS_FILE=%ARUNI_DIR%.aruni.key"
set "ENC_FILE=%ARUNI_DIR%.aruni.key.enc"
set "ENV_FILE=%ARUNI_DIR%.env"

echo.
echo +==================================================================+
echo ^|              ARUNI LEARNING SYSTEM -- SETUP                     ^|
echo +==================================================================+
echo.
echo   Developed by Ram Kalyan Medury
echo   Founder ^& CEO, Maxiom Wealth (since 2016)
echo   IIT / IIM alumnus ^| ex-CIO ICICI ^| ex-Fintech Leader, Infosys
echo.
echo ------------------------------------------------------------------
echo   BEFORE WE BEGIN -- PREREQUISITES
echo ------------------------------------------------------------------
echo   Make sure you have the following ready:
echo.
echo   [1] Python 3.8+      check with: python --version
echo       Download: https://www.python.org/downloads/
echo       IMPORTANT: check "Add Python to PATH" during install
echo.
echo   [2] Internet access  needed to sync your learning data
echo.
echo   [3] Aruni password   get it from whoever set up this system
echo       (shared via WhatsApp / iMessage -- NOT stored anywhere)
echo.
echo   [4] An AI assistant  you will choose one in Step 5 below
echo       Claude Code (Anthropic) ^| Gemini CLI (Google, free) ^| Codex (OpenAI)
echo ------------------------------------------------------------------
echo.
pause

:: ── 1. Python ─────────────────────────────────────────────────────────────
echo [ 1/5 ] Checking Python...
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
echo [ 2/5 ] Installing Python dependencies...
pip install -q gspread google-auth cryptography
if errorlevel 1 (
    echo   ERROR: pip install failed.
    echo   Try running as Administrator, or: pip install --user gspread google-auth cryptography
    pause
    exit /b 1
)
echo   OK: dependencies installed

:: ── 3. Access credentials ──────────────────────────────────────────────────
echo.
echo [ 3/5 ] Checking access credentials...
if not exist "%CREDS_FILE%" (
    if not exist "%ENC_FILE%" (
        echo   ERROR: Access file not found. Re-clone the repo and try again.
        pause
        exit /b 1
    )
    echo.
    set /p ARUNI_PASSWORD="  Enter Aruni password (get it from whoever set up this system): "
    python "%ARUNI_DIR%encrypt_creds.py" "%ARUNI_PASSWORD%"
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
echo   OK: Access granted!

:: ── 4. Config file ─────────────────────────────────────────────────────────
echo.
echo [ 4/5 ] Checking configuration...
if not exist "%ENV_FILE%" (
    copy "%ARUNI_DIR%.env.example" "%ENV_FILE%" >nul
    echo   Created configuration file
)

:: ── Verify connection ───────────────────────────────────────────────────────
echo.
echo   Verifying connection to your learning data...
python "%ARUNI_DIR%setup.py" status
if errorlevel 1 (
    echo.
    echo   ERROR: Could not connect to your learning data.
    echo   Re-run this script or contact whoever set up the system.
    pause
    exit /b 1
)

:: ── 5. Choose your AI ──────────────────────────────────────────────────────
echo.
echo [ 5/5 ] Choose your AI assistant:
echo.
echo   Press 1 -- Claude Code  (Anthropic ^| ~$20/mo or API key at claude.ai)
echo   Press 2 -- Gemini CLI   (Google    ^| FREE with your Google account)
echo   Press 3 -- Codex        (OpenAI    ^| API key at platform.openai.com)
echo   Press 4 -- Skip         (already installed / I will do this later)
echo.
set /p AI_CHOICE="  Your choice [1-4]: "
echo.

if "%AI_CHOICE%"=="1" goto claude_setup
if "%AI_CHOICE%"=="2" goto gemini_setup
if "%AI_CHOICE%"=="3" goto codex_setup
goto ai_skip

:claude_setup
echo   Setting up Claude Code...
where claude >nul 2>&1
if not errorlevel 1 (
    echo   OK: Claude Code already installed
) else (
    where npm >nul 2>&1
    if errorlevel 1 (
        echo   NOTE: npm not found. Install Node.js first: https://nodejs.org
        echo   Then run: npm install -g @anthropic-ai/claude-code
    ) else (
        npm install -g @anthropic-ai/claude-code
        echo   OK: Claude Code installed
    )
)
echo.
echo   To log in, run: claude
echo   You will be prompted to sign in with your Anthropic account.
set AI_CMD=claude
goto ai_done

:gemini_setup
echo   Setting up Gemini CLI...
where gemini >nul 2>&1
if not errorlevel 1 (
    echo   OK: Gemini CLI already installed
) else (
    where npm >nul 2>&1
    if errorlevel 1 (
        echo   NOTE: npm not found. Install Node.js first: https://nodejs.org
        echo   Then run: npm install -g @google/gemini-cli
    ) else (
        npm install -g @google/gemini-cli
        echo   OK: Gemini CLI installed
    )
)
echo.
echo   To log in, run: gemini
echo   A browser window will open -- sign in with your Google account.
echo   FREE tier available, no credit card needed.
set AI_CMD=gemini
goto ai_done

:codex_setup
echo   Setting up Codex (OpenAI)...
where codex >nul 2>&1
if not errorlevel 1 (
    echo   OK: Codex already installed
) else (
    where npm >nul 2>&1
    if errorlevel 1 (
        echo   NOTE: npm not found. Install Node.js first: https://nodejs.org
        echo   Then run: npm install -g @openai/codex
    ) else (
        npm install -g @openai/codex
        echo   OK: Codex installed
    )
)
echo.
echo   You need an OpenAI API key from: https://platform.openai.com/api-keys
echo   Then set it: set OPENAI_API_KEY=sk-...
echo   Add it to your system environment variables to make it permanent.
set AI_CMD=codex
goto ai_done

:ai_skip
echo   Skipped. You can install your AI assistant later.
echo   Options: claude ^| gemini ^| codex
set AI_CMD=your-ai-command

:ai_done

:: ── Done ───────────────────────────────────────────────────────────────────
echo.
echo +==================================================================+
echo ^|           ARUNI LEARNING SYSTEM -- READY!                       ^|
echo +==================================================================+
echo.
echo   Aruni is your personal Socratic learning companion, named after
echo   the Vedic sage Uddalaka Aruni -- who taught through questions and
echo   discovery, centuries before Socrates.
echo.
echo ------------------------------------------------------------------
echo   HOW TO START
echo ------------------------------------------------------------------
echo.
echo   Step 1 -- Add yourself as a learner (one time only):
echo              python setup.py add-user
echo.
echo   Step 2 -- Go to your learning folder:
echo              cd users\^<your-name^>
echo.
echo   Step 3 -- Launch your AI:
echo              %AI_CMD%
echo.
echo   Step 4 -- Say: 'I'm ready to learn'
echo              Aruni will guide you from there.
echo.
echo ------------------------------------------------------------------
echo   WHAT ARUNI DOES
echo ------------------------------------------------------------------
echo.
echo   * Teaches through questions, not lectures  (Socratic method)
echo   * Tracks every concept you learn           (automatic)
echo   * Reminds you when to review               (spaced repetition)
echo   * Sends a daily 7 AM email with your review questions
echo   * Works across laptops -- your progress follows you
echo   * Works with Claude, Gemini, Codex, or any future AI
echo.
echo ------------------------------------------------------------------
echo   USEFUL COMMANDS
echo ------------------------------------------------------------------
echo.
echo   python setup.py add-user         Add a new learner
echo   python setup.py status           Check system status
echo   python daily_email.py            Send today's review email now
echo.
echo   Things to say to Aruni during a session:
echo     'I'm ready to learn'    -- start a new topic
echo     'I'm ready to review'   -- review what's due today
echo     'How am I doing?'       -- see your progress
echo     'Teach me something new'-- explore a related concept
echo.
echo ------------------------------------------------------------------
echo   FAQ
echo ------------------------------------------------------------------
echo.
echo   Q: Where is my data stored?
echo      Securely in the cloud -- nothing sensitive on your laptop.
echo.
echo   Q: What if I switch laptops?
echo      Re-run this script. One password. Everything comes back.
echo.
echo   Q: Can multiple people use the same system?
echo      Yes -- each person has their own private learning space.
echo.
echo   Q: What if I forget the password?
echo      Ask whoever set up this system (they have the Aruni password).
echo.
echo ------------------------------------------------------------------
echo.
echo   Developed by Ram Kalyan Medury
echo   Founder ^& CEO, Maxiom Wealth (since 2016)
echo   IIT / IIM alumnus ^| ex-CIO ICICI ^| ex-Fintech Leader, Infosys
echo.
echo +==================================================================+
echo.
pause
