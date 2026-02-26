#!/bin/bash
# Aruni Learning System - New Machine Setup
# Run this once on any Mac/Linux machine to get started.
# Usage: bash setup_new_machine.sh

set -e

ARUNI_DIR="$(cd "$(dirname "$0")" && pwd)"
CREDS_FILE="$ARUNI_DIR/.aruni.key"
ENC_FILE="$ARUNI_DIR/.aruni.key.enc"
ENV_FILE="$ARUNI_DIR/.env"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              ARUNI LEARNING SYSTEM — SETUP                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Developed by Ram Kalyan Medury"
echo "  Founder & CEO, Maxiom Wealth (since 2016)"
echo "  IIT / IIM alumnus | ex-CIO ICICI | ex-Fintech Leader, Infosys"
echo ""
echo "──────────────────────────────────────────────────────────────────"
echo "  BEFORE WE BEGIN — PREREQUISITES"
echo "──────────────────────────────────────────────────────────────────"
echo "  Make sure you have the following ready:"
echo ""
echo "    [1] Python 3.8+      → check with: python3 --version"
echo "        Mac:   brew install python"
echo "        Linux: sudo apt install python3 python3-pip"
echo ""
echo "    [2] Internet access  → needed to sync your learning data"
echo ""
echo "    [3] Aruni password   → get it from whoever set up this system"
echo "        (shared via WhatsApp / iMessage — NOT stored anywhere)"
echo ""
echo "    [4] An AI assistant  → you will choose one in Step 5 below"
echo "        Claude Code (Anthropic)  |  Gemini CLI (Google, free)  |  Codex (OpenAI)"
echo "──────────────────────────────────────────────────────────────────"
echo ""
read -p "  All set? Press Enter to continue, or Ctrl+C to exit..."
echo ""

# ── 1. Python ──────────────────────────────────────────────────────────────
echo "[ 1/5 ] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ERROR: Python 3 not found."
    echo "  Mac:   brew install python"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi
echo "  OK: $(python3 --version)"

# ── 2. Dependencies ─────────────────────────────────────────────────────────
echo ""
echo "[ 2/5 ] Installing Python dependencies..."
pip3 install -q gspread google-auth cryptography
echo "  OK: dependencies installed"

# ── 3. Access credentials ───────────────────────────────────────────────────
echo ""
echo "[ 3/5 ] Checking access credentials..."
if [ ! -f "$CREDS_FILE" ]; then
    if [ ! -f "$ENC_FILE" ]; then
        echo "  ERROR: Access file not found. Re-clone the repo and try again."
        exit 1
    fi
    echo ""
    echo "  Enter the Aruni password (get it from whoever set up this system):"
    read -s -p "  Password: " ARUNI_PASSWORD
    echo ""
    python3 "$ARUNI_DIR/encrypt_creds.py" "$ARUNI_PASSWORD"
    if [ ! -f "$CREDS_FILE" ]; then
        exit 1
    fi
fi
echo "  OK: Access granted!"

# ── 4. Config file ─────────────────────────────────────────────────────────
echo ""
echo "[ 4/5 ] Checking configuration..."
if [ ! -f "$ENV_FILE" ]; then
    cp "$ARUNI_DIR/.env.example" "$ENV_FILE"
    echo "  Created configuration file"
fi

# ── Verify connection ─────────────────────────────────────────────────────────
echo ""
echo "  Verifying connection to your learning data..."
python3 - <<'PYEOF'
import os, sys

def load_env(path):
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.join(os.path.dirname(os.path.abspath('.')), '.env'))
# also try current dir
load_env('.env')

try:
    import gspread
    from google.oauth2.service_account import Credentials
    creds_path = os.environ.get('ARUNI_KEY_PATH', './.aruni.key')
    sheet_id   = os.environ.get('ARUNI_DB', '')
    if not sheet_id:
        print("  ERROR: Data store ID not configured in .env")
        sys.exit(1)
    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    tabs = [ws.title for ws in sh.worksheets()]
    print(f"  OK: Connected to your learning data")
    print(f"  Learners: {', '.join(t for t in tabs if t not in ['config','sessions'])}")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)
PYEOF

# ── 5. Choose your AI ──────────────────────────────────────────────────────
echo ""
echo "[ 5/5 ] Choose your AI assistant:"
echo ""
echo "  Press 1 — Claude Code  (Anthropic | needs account at claude.ai, ~$20/mo or API key)"
echo "  Press 2 — Gemini CLI   (Google    | FREE with your Google account)"
echo "  Press 3 — Codex        (OpenAI    | needs account + API key at platform.openai.com)"
echo "  Press 4 — Skip         (already installed / I'll do this later)"
echo ""
read -p "  Your choice [1-4]: " AI_CHOICE
echo ""

AI_READY=false

case "$AI_CHOICE" in
  1)
    echo "  Setting up Claude Code..."
    if command -v claude &>/dev/null; then
        echo "  OK: Claude Code already installed"
        AI_READY=true
    else
        if ! command -v npm &>/dev/null; then
            echo "  NOTE: npm not found. Install Node.js first: https://nodejs.org"
            echo "  Then run: npm install -g @anthropic-ai/claude-code"
        else
            npm install -g @anthropic-ai/claude-code && AI_READY=true
            echo "  OK: Claude Code installed"
        fi
    fi
    echo ""
    echo "  Sign in: launch claude and follow the prompts to log in with your Anthropic account."
    AI_CMD="claude"
    ;;
  2)
    echo "  Setting up Gemini CLI..."
    if command -v gemini &>/dev/null; then
        echo "  OK: Gemini CLI already installed"
        AI_READY=true
    else
        if ! command -v npm &>/dev/null; then
            echo "  NOTE: npm not found. Install Node.js first: https://nodejs.org"
            echo "  Then run: npm install -g @google/gemini-cli"
        else
            npm install -g @google/gemini-cli && AI_READY=true
            echo "  OK: Gemini CLI installed"
        fi
    fi
    echo ""
    echo "  Sign in: a browser window will open when you first launch gemini."
    echo "  FREE tier available — no credit card needed."
    AI_CMD="gemini"
    ;;
  3)
    echo "  Setting up Codex (OpenAI)..."
    if command -v codex &>/dev/null; then
        echo "  OK: Codex already installed"
        AI_READY=true
    else
        if ! command -v npm &>/dev/null; then
            echo "  NOTE: npm not found. Install Node.js first: https://nodejs.org"
            echo "  Then run: npm install -g @openai/codex"
        else
            npm install -g @openai/codex && AI_READY=true
            echo "  OK: Codex installed"
        fi
    fi
    echo ""
    echo "  API key required: get one at https://platform.openai.com/api-keys"
    echo "  Then run:  export OPENAI_API_KEY=sk-..."
    echo "  Add that line to your ~/.zshrc or ~/.bashrc to make it permanent."
    AI_CMD="codex"
    ;;
  *)
    echo "  Skipped. You can install your AI assistant later."
    echo "  Options: claude | gemini | codex"
    AI_CMD=""
    ;;
esac

# ── Done ───────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║            ARUNI LEARNING SYSTEM — READY!                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Aruni is your personal Socratic learning companion, named after"
echo "  the Vedic sage Uddalaka Aruni — who taught through questions and"
echo "  discovery, centuries before Socrates."
echo ""
echo "──────────────────────────────────────────────────────────────────"
echo "  HOW TO START"
echo "──────────────────────────────────────────────────────────────────"
echo ""
echo "  Step 1 — Add yourself as a learner (one time only):"
echo "             python3 setup.py add-user"
echo ""
echo "  Step 2 — Go to your learning folder:"
echo "             cd users/<your-name>"
echo ""
echo "  Step 3 — Launch your AI:"
echo "             $AI_CMD"
echo ""
echo "  Step 4 — Say:  'I'm ready to learn'"
echo "             Aruni will guide you from there."
echo ""
echo "──────────────────────────────────────────────────────────────────"
echo "  WHAT ARUNI DOES"
echo "──────────────────────────────────────────────────────────────────"
echo ""
echo "  * Teaches through questions, not lectures  (Socratic method)"
echo "  * Tracks every concept you learn           (automatic)"
echo "  * Reminds you when to review               (spaced repetition)"
echo "  * Sends a daily 7 AM email with your review questions"
echo "  * Works across laptops — your progress follows you"
echo "  * Works with Claude, Gemini, Codex, or any future AI"
echo ""
echo "──────────────────────────────────────────────────────────────────"
echo "  USEFUL COMMANDS"
echo "──────────────────────────────────────────────────────────────────"
echo ""
echo "  python3 setup.py add-user         Add a new learner"
echo "  python3 setup.py status           Check system status"
echo "  python3 daily_email.py            Send today's review email now"
echo ""
echo "  Things to say to Aruni during a session:"
echo "    'I'm ready to learn'    →  start a new topic"
echo "    'I'm ready to review'   →  review what's due today"
echo "    'How am I doing?'       →  see your progress"
echo "    'Teach me something new'→  explore a related concept"
echo ""
echo "──────────────────────────────────────────────────────────────────"
echo "  FAQ"
echo "──────────────────────────────────────────────────────────────────"
echo ""
echo "  Q: Where is my data stored?"
echo "     Securely in the cloud — nothing sensitive on your laptop."
echo ""
echo "  Q: What if I switch laptops?"
echo "     Re-run this script. One password. Everything comes back."
echo ""
echo "  Q: Can multiple people use the same system?"
echo "     Yes — each person has their own private learning space."
echo ""
echo "  Q: Do I need internet?"
echo "     Only when starting or ending a session."
echo ""
echo "  Q: What if I forget the password?"
echo "     Ask whoever set up this system (they have the Aruni password)."
echo ""
echo "──────────────────────────────────────────────────────────────────"
echo ""
echo "  Developed by Ram Kalyan Medury"
echo "  Founder & CEO, Maxiom Wealth (since 2016)"
echo "  IIT / IIM alumnus | ex-CIO ICICI | ex-Fintech Leader, Infosys"
echo ""
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# ── Launch AI now? ────────────────────────────────────────────────────────
if [ "$AI_READY" = true ] && [ -n "$AI_CMD" ]; then
    read -p "  Launch $AI_CMD now? [y/n]: " LAUNCH_NOW
    echo ""
    if [ "$LAUNCH_NOW" = "y" ] || [ "$LAUNCH_NOW" = "Y" ]; then
        echo "  Starting $AI_CMD..."
        echo "  (Say 'I'm ready to learn' to begin)"
        echo ""
        exec "$AI_CMD"
    else
        echo "  When ready, run:  cd users/<your-name> && $AI_CMD"
        echo ""
    fi
elif [ -n "$AI_CMD" ]; then
    echo "  Once $AI_CMD is installed, run:  cd users/<your-name> && $AI_CMD"
    echo ""
fi
