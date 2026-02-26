#!/usr/bin/env python3
"""
Aruni CLI — called by the AI during learning sessions.

Usage:
  python3 aruni.py due             <username>
  python3 aruni.py add             <username> <topic> <domain> <explanation> <question>
  python3 aruni.py update          <username> <row> <correct|wrong>
  python3 aruni.py session-start   <username> <domain>
  python3 aruni.py session-end     <username> <session_row> <topics_covered> <key_insights>
  python3 aruni.py status          <username>
"""

import os, sys
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
    # cols: topic(1) domain(2) explanation(3) questions(4) confidence(5)
    #       created_at(6) last_reviewed(7) next_review(8) times_reviewed(9)
    times = int(row[8]) + 1 if len(row) > 8 and row[8] else 1
    now = datetime.now()
    last_reviewed = now.strftime('%Y-%m-%d %H:%M')
    correct = result.lower().startswith('c')

    if correct:
        intervals = {1: 1, 2: 3, 3: 7, 4: 14}
        days = intervals.get(times, 30)
        if times >= 5:   confidence = 'High'
        elif times >= 3: confidence = 'Medium'
        else:            confidence = row[4] if len(row) > 4 and row[4] else 'Low'
    else:
        days = 1
        confidence = 'Low'

    next_date = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    ws.update_cell(row_num, 5, confidence)
    ws.update_cell(row_num, 7, last_reviewed)
    ws.update_cell(row_num, 8, next_date)
    ws.update_cell(row_num, 9, times)
    print(f"Updated row {row_num}: confidence={confidence}, next_review={next_date} (+{days}d), reviews={times}")


def cmd_add(username, topic, domain, explanation, question):
    """Add a new concept."""
    sh, ws = connect(username)
    now      = datetime.now()
    created  = now.strftime('%Y-%m-%d %H:%M')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    # cols: topic domain explanation questions confidence created_at last_reviewed next_review times_reviewed
    ws.append_row([topic, domain, explanation, question, 'Low', created, '', tomorrow, 0])
    print(f"Added: '{topic}' — next review tomorrow ({tomorrow})")


def cmd_session_start(username, domain):
    """Log session start. Prints the session row number for use with session-end."""
    sh, ws = connect(username)
    sessions = sh.worksheet('sessions')
    now = datetime.now()
    date     = now.strftime('%Y-%m-%d')
    start_time = now.strftime('%H:%M')
    # columns: user date start_time end_time duration_minutes domain concepts_covered key_insights open_questions
    sessions.append_row([username, date, start_time, '', '', domain, '', '', ''])
    all_rows = sessions.get_all_values()
    session_row = len(all_rows)  # 1-based row number of the row just added
    print(f"SESSION_START: row={session_row} time={start_time} date={date}")


def cmd_session_end(username, session_row, topics_covered, key_insights):
    """Complete a session log with end time, duration, and what was covered."""
    sh, ws = connect(username)
    sessions = sh.worksheet('sessions')
    session_row = int(session_row)
    row = sessions.row_values(session_row)

    now = datetime.now()
    end_time = now.strftime('%H:%M')

    # Calculate duration from start_time in col 3 (index 2)
    duration_minutes = ''
    if len(row) >= 3 and row[2]:
        try:
            date_str = row[1] if len(row) > 1 and row[1] else now.strftime('%Y-%m-%d')
            start_dt = datetime.strptime(f"{date_str} {row[2]}", '%Y-%m-%d %H:%M')
            duration_minutes = int((now - start_dt).total_seconds() / 60)
        except Exception:
            pass

    # cols: user(1) date(2) start_time(3) end_time(4) duration_minutes(5) domain(6) concepts_covered(7) key_insights(8) open_questions(9)
    sessions.update_cell(session_row, 4, end_time)
    sessions.update_cell(session_row, 5, duration_minutes)
    sessions.update_cell(session_row, 7, topics_covered)
    sessions.update_cell(session_row, 8, key_insights)
    print(f"Session complete: {duration_minutes} min | topics: {topics_covered}")


def cmd_status(username):
    """Show learning progress summary."""
    sh, ws = connect(username)
    rows = ws.get_all_records()
    today = datetime.now().strftime('%Y-%m-%d')
    due  = [r for r in rows if r.get('next_review') and str(r['next_review']) <= today]
    high = [r for r in rows if r.get('confidence') == 'High']
    med  = [r for r in rows if r.get('confidence') == 'Medium']
    low  = [r for r in rows if r.get('confidence') == 'Low']
    print(f"Learner  : {username}")
    print(f"Total    : {len(rows)} concepts")
    print(f"Due today: {len(due)}")
    print(f"High     : {len(high)} | Medium: {len(med)} | Low: {len(low)}")


COMMANDS = {
    'due':           (cmd_due,           ['username']),
    'update':        (cmd_update,        ['username', 'row', 'correct|wrong']),
    'add':           (cmd_add,           ['username', 'topic', 'domain', 'explanation', 'question']),
    'session-start': (cmd_session_start, ['username', 'domain']),
    'session-end':   (cmd_session_end,   ['username', 'session_row', 'topics_covered', 'key_insights']),
    'status':        (cmd_status,        ['username']),
}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage:")
        for cmd, (fn, args) in COMMANDS.items():
            print(f"  python3 aruni.py {cmd} {' '.join('<'+a+'>' for a in args)}")
        sys.exit(1)

    cmd = sys.argv[1]
    fn, args = COMMANDS[cmd]
    if len(sys.argv) < 2 + len(args):
        print(f"Usage: python3 aruni.py {cmd} {' '.join('<'+a+'>' for a in args)}")
        sys.exit(1)

    try:
        fn(*sys.argv[2:2+len(args)])
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
