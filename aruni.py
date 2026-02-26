#!/usr/bin/env python3
"""
Aruni CLI — called by the AI during learning sessions.

Usage:
  python3 aruni.py due <username>
  python3 aruni.py add <username> <topic> <domain> <explanation> <question>
  python3 aruni.py update <username> <row> <correct|wrong>
  python3 aruni.py log <username> <domain> <topics_covered> <key_insights>
  python3 aruni.py status <username>
"""

import os, sys, json
from datetime import datetime, timedelta

ARUNI_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    cfg = {}
    env = os.path.join(ARUNI_DIR, '.env')
    if os.path.exists(env):
        for line in open(env):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def connect(username):
    import gspread
    from google.oauth2.service_account import Credentials
    cfg = load_config()
    key_path = cfg.get('ARUNI_KEY_PATH', os.path.join(ARUNI_DIR, '.aruni.key'))
    db_id    = cfg.get('ARUNI_DB', '')
    creds = Credentials.from_service_account_file(
        key_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(db_id)
    ws = sh.worksheet(username)
    return sh, ws


def cmd_due(username):
    """Show concepts due for review today."""
    sh, ws = connect(username)
    rows = ws.get_all_records()
    today = datetime.now().strftime('%Y-%m-%d')
    due = [r for r in rows if r.get('next_review') and str(r['next_review']) <= today]
    print(f"TODAY: {today}")
    print(f"TOTAL: {len(rows)} concepts | DUE: {len(due)}")
    if due:
        print()
        for i, r in enumerate(due):
            row_num = rows.index(r) + 2
            print(f"  [{i+1}] row={row_num} [{r.get('confidence','?')}] {r['topic']}")
            print(f"       Q: {r.get('questions','(no question)')}")
    else:
        print("Nothing due today — great work!")


def cmd_update(username, row_num, result):
    """Update a concept after review. result = 'correct' or 'wrong'."""
    sh, ws = connect(username)
    row_num = int(row_num)
    row = ws.row_values(row_num)
    # columns: topic(1) domain(2) explanation(3) questions(4) confidence(5)
    #          last_reviewed(6) next_review(7) times_reviewed(8)
    times = int(row[7]) + 1 if row[7] else 1
    today = datetime.now().strftime('%Y-%m-%d')
    correct = result.lower().startswith('c')

    if correct:
        intervals = {1: 1, 2: 3, 3: 7, 4: 14}
        days = intervals.get(times, 30)
        if times >= 5:   confidence = 'High'
        elif times >= 3: confidence = 'Medium'
        else:            confidence = row[4] if row[4] else 'Low'
    else:
        days = 1
        confidence = 'Low'

    next_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    ws.update_cell(row_num, 5, confidence)
    ws.update_cell(row_num, 6, today)
    ws.update_cell(row_num, 7, next_date)
    ws.update_cell(row_num, 8, times)
    print(f"Updated row {row_num}: confidence={confidence}, next_review={next_date} (+{days}d), reviews={times}")


def cmd_add(username, topic, domain, explanation, question):
    """Add a new concept."""
    sh, ws = connect(username)
    today    = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    ws.append_row([topic, domain, explanation, question, 'Low', today, tomorrow, 0])
    print(f"Added: '{topic}' — next review tomorrow ({tomorrow})")


def cmd_log(username, domain, topics_covered, key_insights):
    """Log a learning session."""
    sh, ws = connect(username)
    sessions = sh.worksheet('sessions')
    today = datetime.now().strftime('%Y-%m-%d')
    sessions.append_row([username, today, domain, topics_covered, key_insights, ''])
    print(f"Session logged for {username} on {today}")


def cmd_status(username):
    """Show learning progress summary."""
    sh, ws = connect(username)
    rows = ws.get_all_records()
    today = datetime.now().strftime('%Y-%m-%d')
    due   = [r for r in rows if r.get('next_review') and str(r['next_review']) <= today]
    high  = [r for r in rows if r.get('confidence') == 'High']
    med   = [r for r in rows if r.get('confidence') == 'Medium']
    low   = [r for r in rows if r.get('confidence') == 'Low']
    print(f"Learner : {username}")
    print(f"Total   : {len(rows)} concepts")
    print(f"Due today: {len(due)}")
    print(f"High    : {len(high)} | Medium: {len(med)} | Low: {len(low)}")


COMMANDS = {
    'due':    (cmd_due,    ['username']),
    'update': (cmd_update, ['username', 'row', 'correct|wrong']),
    'add':    (cmd_add,    ['username', 'topic', 'domain', 'explanation', 'question']),
    'log':    (cmd_log,    ['username', 'domain', 'topics_covered', 'key_insights']),
    'status': (cmd_status, ['username']),
}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage:")
        for cmd, (fn, args) in COMMANDS.items():
            print(f"  python3 aruni.py {cmd} {' '.join('<'+a+'>' for a in args)}")
        sys.exit(1)

    cmd  = sys.argv[1]
    fn, args = COMMANDS[cmd]
    required = 2 + len(args)
    if len(sys.argv) < required:
        print(f"Usage: python3 aruni.py {cmd} {' '.join('<'+a+'>' for a in args)}")
        sys.exit(1)

    try:
        fn(*sys.argv[2:2+len(args)])
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
