#!/usr/bin/env python3
"""
Aruni Learning System - Setup Script

Named after Uddalaka Aruni, the Vedic sage who taught through questions.

Commands:
    python3 setup.py init              Initialize data store and folder structure
    python3 setup.py add-user          Add a new learner (interactive)
    python3 setup.py regenerate USER   Re-generate prompt files for a user
    python3 setup.py status            Show all users and their learning stats
    python3 setup.py migrate USER FILE Import concepts from a Notion export JSON
"""

import os
import sys
import json
from datetime import datetime, timedelta

ARUNI_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(ARUNI_DIR, '.env')
TEMPLATE_PATH = os.path.join(ARUNI_DIR, 'admin', 'prompt_template.md')
USERS_DIR = os.path.join(ARUNI_DIR, 'users')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

CONFIG_HEADERS = ['user', 'name', 'email', 'domain', 'learning_goal', 'start_date', 'custom_instructions']
KB_HEADERS = ['topic', 'domain', 'explanation', 'questions', 'confidence', 'last_reviewed', 'next_review', 'times_reviewed']
SESSIONS_HEADERS = ['user', 'date', 'domain', 'concepts_covered', 'key_insights', 'open_questions']


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_env():
    """Load .env without requiring python-dotenv"""
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ[key.strip()] = value.strip().strip('"').strip("'")


def save_env_var(key, value):
    """Append or update a variable in .env"""
    lines = []
    found = False
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            found = True
            break
    if not found:
        lines.append(f'{key}={value}\n')
    with open(ENV_PATH, 'w') as f:
        f.writelines(lines)
    os.environ[key] = value


def check_dependencies():
    """Check if gspread and google-auth are installed"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        return True
    except ImportError:
        print("Missing dependencies. Install them with:")
        print(f"  pip install -r {os.path.join(ARUNI_DIR, 'requirements.txt')}")
        print()
        print("Or simply:")
        print("  pip install gspread google-auth")
        return False


def get_gspread_client():
    """Authenticate and return gspread client"""
    from google.oauth2.service_account import Credentials
    import gspread

    creds_path = os.environ.get('ARUNI_KEY_PATH', os.path.join(ARUNI_DIR, '.aruni.key'))
    # Resolve relative paths from ARUNI_DIR
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(ARUNI_DIR, creds_path)

    if not os.path.exists(creds_path):
        print(f"ERROR: Access credentials not found at: {creds_path}")
        print()
        print("Run setup_new_machine.sh (Mac/Linux) or setup_new_machine.bat (Windows)")
        print("and enter the Aruni password when prompted.")
        sys.exit(1)

    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds), creds_path


def get_sheet():
    """Get the Aruni data store"""
    gc, _ = get_gspread_client()
    sheet_id = os.environ.get('ARUNI_DB')
    if not sheet_id:
        print("ERROR: No ARUNI_DB in .env. Run 'python3 setup.py init' first.")
        sys.exit(1)
    return gc.open_by_key(sheet_id)


def read_config_tab(sh):
    """Read all users from config tab, return list of dicts"""
    try:
        config_ws = sh.worksheet('config')
        return config_ws.get_all_records()
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init():
    """Create data store with config and sessions tabs"""
    load_env()

    if not check_dependencies():
        sys.exit(1)

    import gspread

    gc, creds_path = get_gspread_client()
    sheet_id = os.environ.get('ARUNI_DB')

    if sheet_id:
        print(f"Sheet already exists: https://docs.google.com/spreadsheets/d/{sheet_id}")
        try:
            sh = gc.open_by_key(sheet_id)
            print(f"Title: {sh.title}")
        except Exception as e:
            print(f"WARNING: Could not open sheet: {e}")
            print("Check ARUNI_DB in .env or delete it and re-run init.")
            sys.exit(1)
    else:
        print("Creating data store: 'Aruni Learning System'...")
        sh = gc.create('Aruni Learning System')
        sheet_id = sh.id
        save_env_var('ARUNI_DB', sheet_id)
        print(f"Created! ID: {sheet_id}")

    # Ensure config tab
    try:
        config_ws = sh.worksheet('config')
        print("'config' tab exists")
    except gspread.exceptions.WorksheetNotFound:
        config_ws = sh.add_worksheet('config', rows=100, cols=len(CONFIG_HEADERS))
        config_ws.update([CONFIG_HEADERS], 'A1')
        print("Created 'config' tab")

    # Ensure sessions tab
    try:
        sessions_ws = sh.worksheet('sessions')
        print("'sessions' tab exists")
    except gspread.exceptions.WorksheetNotFound:
        sessions_ws = sh.add_worksheet('sessions', rows=1000, cols=len(SESSIONS_HEADERS))
        sessions_ws.update([SESSIONS_HEADERS], 'A1')
        print("Created 'sessions' tab")

    # Remove default Sheet1 if empty
    try:
        sheet1 = sh.worksheet('Sheet1')
        if not sheet1.get_all_values() or sheet1.get_all_values() == [[]]:
            sh.del_worksheet(sheet1)
            print("Removed empty 'Sheet1'")
    except Exception:
        pass

    # Ensure users dir
    os.makedirs(USERS_DIR, exist_ok=True)

    # Print service account email for sharing
    with open(creds_path) as f:
        sa_info = json.load(f)
    sa_email = sa_info.get('client_email', '(unknown)')

    print()
    print("=" * 60)
    print("SHEET INITIALIZED SUCCESSFULLY")
    print("=" * 60)
    print(f"URL:  https://docs.google.com/spreadsheets/d/{sheet_id}")
    print(f"Service account: {sa_email}")
    print()
    print("IMPORTANT: Share this sheet with yourself!")
    print(f"  Open the URL above > Share > Add '{sa_email}'")
    print("  (The service account owns it, so share with your Google")
    print("  account to see it in your Drive.)")
    print()
    print("Next step: python3 setup.py add-user")


def cmd_add_user():
    """Add a new learner interactively"""
    load_env()

    if not check_dependencies():
        sys.exit(1)

    import gspread

    sh = get_sheet()

    print()
    print("--- Add New Learner ---")
    print()

    username = input("  Username (lowercase, no spaces, used as tab name): ").strip().lower().replace(' ', '_')
    if not username:
        print("ERROR: Username cannot be empty")
        sys.exit(1)

    name = input(f"  Display name [{username.title()}]: ").strip()
    if not name:
        name = username.title()

    email = input("  Email (for daily review emails & sheet sharing): ").strip()

    domain = input("  What are they learning? (e.g., 'Organic Chemistry', 'Indian History'): ").strip()

    goal = input("  Learning goal (e.g., 'JEE prep', 'Deep understanding for exam'): ").strip()

    print()
    print("  Custom instructions are domain-specific additions to the teaching prompt.")
    print("  Examples: 'Always relate concepts to real Indian companies'")
    print("            'Use NCERT Grade 9 textbook as reference'")
    print("            'Focus on problem-solving, not theory'")
    custom = input("  Custom instructions (press Enter to skip): ").strip()

    start_date = datetime.now().strftime('%Y-%m-%d')

    # Add to config tab
    config_ws = sh.worksheet('config')
    config_ws.append_row([username, name, email, domain, goal, start_date, custom])
    print(f"  Added {username} to config tab")

    # Create user tab
    try:
        sh.worksheet(username)
        print(f"  Tab '{username}' already exists")
    except gspread.exceptions.WorksheetNotFound:
        user_ws = sh.add_worksheet(username, rows=1000, cols=len(KB_HEADERS))
        user_ws.update([KB_HEADERS], 'A1')
        print(f"  Created tab '{username}'")

    # Share sheet with user
    if email:
        try:
            sh.share(email, perm_type='user', role='writer')
            print(f"  Sheet shared with {email}")
        except Exception as e:
            print(f"  NOTE: Could not auto-share with {email}: {e}")
            print(f"  Please share the sheet manually with {email}")

    # Generate prompt files
    sheet_id = os.environ.get('ARUNI_DB')
    creds_path = os.environ.get('ARUNI_KEY_PATH', os.path.join(ARUNI_DIR, '.aruni.key'))
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(ARUNI_DIR, creds_path)

    user_dir = os.path.join(USERS_DIR, username)
    generate_prompts(username, name, domain, goal, custom, sheet_id, creds_path, user_dir)

    print()
    print("=" * 60)
    print(f"USER '{username}' ADDED SUCCESSFULLY")
    print("=" * 60)
    print()
    print(f"Prompt files generated in: {user_dir}/")
    print(f"  CLAUDE.md   - for Claude Code")
    print(f"  GEMINI.md   - for Gemini CLI")
    print(f"  AGENTS.md   - for OpenAI Codex CLI")
    print()
    print("HOW TO USE:")
    print()
    print(f"  Claude Code:  cd {user_dir} && claude")
    print(f"  Gemini CLI:   cd {user_dir} && gemini")
    print(f"  Codex CLI:    cd {user_dir} && codex")
    print()
    print(f'  Then just say: "I\'m ready to review" or "Teach me something new"')
    print()
    sheet_id = os.environ.get('ARUNI_DB')
    print(f"  Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")


def generate_prompts(username, name, domain, goal, custom_instructions, sheet_id, creds_path, user_dir):
    """Generate CLAUDE.md, GEMINI.md, AGENTS.md for a user"""
    os.makedirs(user_dir, exist_ok=True)

    # Read template
    with open(TEMPLATE_PATH) as f:
        template = f.read()

    # Fill in placeholders
    custom_block = ""
    if custom_instructions:
        custom_block = f"\n## Domain-Specific Instructions\n\n{custom_instructions}\n"

    rendered = (template
        .replace('__NAME__', name)
        .replace('__USERNAME__', username)
        .replace('__DOMAIN__', domain)
        .replace('__GOAL__', goal)
        .replace('__ARUNI_DB__', sheet_id or 'NOT_SET')
        .replace('__CREDS_PATH__', creds_path)
        .replace('__CUSTOM_INSTRUCTIONS__', custom_block))

    # Write all three variants (same content, different filenames)
    for filename in ['CLAUDE.md', 'GEMINI.md', 'AGENTS.md']:
        filepath = os.path.join(user_dir, filename)
        with open(filepath, 'w') as f:
            f.write(rendered)

    print(f"  Generated prompt files in {user_dir}/")


def cmd_regenerate(username):
    """Re-generate prompt files for an existing user"""
    load_env()

    if not check_dependencies():
        sys.exit(1)

    sh = get_sheet()
    users = read_config_tab(sh)

    user_data = None
    for u in users:
        if u.get('user') == username:
            user_data = u
            break

    if not user_data:
        print(f"ERROR: User '{username}' not found in config tab")
        print(f"Available users: {', '.join(u.get('user', '?') for u in users)}")
        sys.exit(1)

    sheet_id = os.environ.get('ARUNI_DB')
    creds_path = os.environ.get('ARUNI_KEY_PATH', os.path.join(ARUNI_DIR, '.aruni.key'))
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(ARUNI_DIR, creds_path)

    user_dir = os.path.join(USERS_DIR, username)
    generate_prompts(
        username,
        user_data.get('name', username.title()),
        user_data.get('domain', ''),
        user_data.get('learning_goal', ''),
        user_data.get('custom_instructions', ''),
        sheet_id,
        creds_path,
        user_dir
    )
    print(f"Regenerated prompt files for '{username}' in {user_dir}/")


def cmd_status():
    """Show all users and their learning stats"""
    load_env()

    if not check_dependencies():
        sys.exit(1)

    sh = get_sheet()
    users = read_config_tab(sh)
    today = datetime.now().strftime('%Y-%m-%d')

    if not users:
        print("No users found. Run 'python3 setup.py add-user' first.")
        return

    sheet_id = os.environ.get('ARUNI_DB')
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
    print()
    print(f"{'User':<15} {'Domain':<30} {'Total':<7} {'Due':<5} {'Low':<5} {'Med':<5} {'High':<5}")
    print("-" * 75)

    for u in users:
        username = u.get('user', '')
        domain = u.get('domain', '')[:28]
        try:
            ws = sh.worksheet(username)
            rows = ws.get_all_records()
        except Exception:
            print(f"{username:<15} {'(tab not found)':<30}")
            continue

        total = len(rows)
        due = sum(1 for r in rows if r.get('next_review') and str(r['next_review']) <= today)
        low = sum(1 for r in rows if r.get('confidence') == 'Low')
        med = sum(1 for r in rows if r.get('confidence') == 'Medium')
        high = sum(1 for r in rows if r.get('confidence') == 'High')

        print(f"{username:<15} {domain:<30} {total:<7} {due:<5} {low:<5} {med:<5} {high:<5}")

    print()


def cmd_migrate(username, json_path):
    """Import concepts from a Notion export JSON into a user's tab"""
    load_env()

    if not check_dependencies():
        sys.exit(1)

    if not os.path.exists(json_path):
        print(f"ERROR: File not found: {json_path}")
        sys.exit(1)

    sh = get_sheet()

    try:
        ws = sh.worksheet(username)
    except Exception:
        print(f"ERROR: Tab '{username}' not found. Run 'python3 setup.py add-user' first.")
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    concepts = data.get('knowledge_base', [])
    if not concepts:
        print("No concepts found in export file.")
        return

    rows_to_add = []
    for c in concepts:
        rows_to_add.append([
            c.get('topic', ''),
            c.get('domain', ''),
            c.get('explanation', ''),
            c.get('question', c.get('questions', '')),
            c.get('confidence', 'Low'),
            c.get('last_reviewed', ''),
            c.get('next_review', ''),
            c.get('times_reviewed', 0)
        ])

    if rows_to_add:
        # Append all rows after the header
        ws.append_rows(rows_to_add)
        print(f"Imported {len(rows_to_add)} concepts into '{username}' tab")
    else:
        print("No concepts to import.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_help():
    print("Aruni Learning System - Setup")
    print()
    print("Usage:")
    print("  python3 setup.py init                  Create data store (first time)")
    print("  python3 setup.py add-user              Add a new learner (interactive)")
    print("  python3 setup.py regenerate <user>     Re-generate prompt files")
    print("  python3 setup.py status                Show all users and stats")
    print("  python3 setup.py migrate <user> <file> Import from Notion export JSON")
    print()
    print("First time? Run these in order:")
    print("  1. pip install gspread google-auth")
    print("  2. Set up Google service account (setup.py init will guide you)")
    print("  3. python3 setup.py init")
    print("  4. python3 setup.py add-user")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1]

    if command == 'init':
        cmd_init()
    elif command == 'add-user':
        cmd_add_user()
    elif command == 'regenerate':
        if len(sys.argv) < 3:
            print("Usage: python3 setup.py regenerate <username>")
            sys.exit(1)
        cmd_regenerate(sys.argv[2])
    elif command == 'status':
        cmd_status()
    elif command == 'migrate':
        if len(sys.argv) < 4:
            print("Usage: python3 setup.py migrate <username> <notion_export.json>")
            sys.exit(1)
        cmd_migrate(sys.argv[2], sys.argv[3])
    elif command in ['help', '--help', '-h']:
        print_help()
    else:
        print(f"Unknown command: {command}")
        print()
        print_help()
        sys.exit(1)
