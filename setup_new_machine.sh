#!/bin/bash
# Aruni Learning System - New Machine Setup
# Run this once on any Mac/Linux machine to get started.
# Usage: bash setup_new_machine.sh

set -e

ARUNI_DIR="$(cd "$(dirname "$0")" && pwd)"
CREDS_FILE="$ARUNI_DIR/google_creds.json"
ENV_FILE="$ARUNI_DIR/.env"

echo ""
echo "======================================"
echo "  Aruni Learning System - Setup"
echo "======================================"
echo ""

# ── 1. Python ──────────────────────────────────────────────────────────────
echo "[ 1/4 ] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 not found."
    echo "  Mac:   brew install python"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi
echo "  OK: $(python3 --version)"

# ── 2. Dependencies ─────────────────────────────────────────────────────────
echo ""
echo "[ 2/4 ] Installing Python dependencies..."
pip3 install -q gspread google-auth
echo "  OK: gspread and google-auth installed"

# ── 3. Google credentials ───────────────────────────────────────────────────
echo ""
echo "[ 3/4 ] Checking Google credentials..."
if [ ! -f "$CREDS_FILE" ]; then
    if [ ! -f "$ARUNI_DIR/google_creds.json.enc" ]; then
        echo "  ERROR: google_creds.json.enc not found. Re-clone the repo and try again."
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

# ── 4. .env file ─────────────────────────────────────────────────────────────
echo ""
echo "[ 4/4 ] Checking .env..."
if [ ! -f "$ENV_FILE" ]; then
    cp "$ARUNI_DIR/.env.example" "$ENV_FILE"
    echo "  Created .env (SHEET_ID pre-filled)"
fi

# ── Verify connection ─────────────────────────────────────────────────────────
echo ""
echo "  Verifying Google Sheet connection..."
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

load_env(os.path.join(os.path.dirname(os.path.abspath(__file__ if '__file__' in dir() else '.')), '.env'))

try:
    import gspread
    from google.oauth2.service_account import Credentials
    creds_path = os.environ.get('GOOGLE_CREDS_PATH', './google_creds.json')
    sheet_id   = os.environ.get('SHEET_ID', '')
    if not sheet_id:
        print("  ERROR: SHEET_ID not set in .env")
        sys.exit(1)
    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    tabs = [ws.title for ws in sh.worksheets()]
    print(f"  OK: Connected to '{sh.title}'")
    print(f"  Tabs: {', '.join(tabs)}")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)
PYEOF

# ── Done ───────────────────────────────────────────────────────────────────
echo ""
echo "======================================"
echo "  Setup complete!"
echo "======================================"
echo ""
echo "To add a new user:"
echo "  python3 setup.py add-user"
echo ""
echo "To start a learning session:"
echo "  cd users/<username> && claude    # Claude Code"
echo "  cd users/<username> && gemini    # Gemini CLI"
echo "  cd users/<username> && codex     # OpenAI Codex"
echo ""
