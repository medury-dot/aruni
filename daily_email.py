#!/usr/bin/env python3
"""
Aruni Daily Email - Sends review reminders to all users.

Reads the Google Sheet, finds concepts due for review, sends HTML emails.
Run manually:  python3 daily_email.py
Run for one:   python3 daily_email.py varnika
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime

ARUNI_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env():
    env_path = os.path.join(ARUNI_DIR, '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ[key.strip()] = value.strip().strip('"').strip("'")


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def get_sheet():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_path = os.environ.get('GOOGLE_CREDS_PATH', os.path.join(ARUNI_DIR, 'google_creds.json'))
    if not os.path.isabs(creds_path):
        creds_path = os.path.join(ARUNI_DIR, creds_path)
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(os.environ['SHEET_ID'])


def get_due_concepts(sh, username):
    """Get concepts due for review today from a user's tab"""
    ws = sh.worksheet(username)
    rows = ws.get_all_records()
    today = datetime.now().strftime('%Y-%m-%d')
    due = []
    for r in rows:
        nr = str(r.get('next_review', ''))
        if nr and nr <= today:
            due.append({
                'topic': r.get('topic', ''),
                'question': r.get('questions', ''),
                'confidence': r.get('confidence', 'Low'),
                'times_reviewed': r.get('times_reviewed', 0)
            })
    return due


def build_review_email(name, domain, concepts):
    today_display = datetime.now().strftime('%A, %B %d, %Y')
    colors = {'Low': '#e74c3c', 'Medium': '#f39c12', 'High': '#27ae60'}

    questions_html = ''
    for i, c in enumerate(concepts, 1):
        color = colors.get(c['confidence'], '#95a5a6')
        questions_html += f'''
        <div style="background:#f8f9fa;padding:16px;border-radius:8px;margin:12px 0;border-left:4px solid {color};">
            <strong>{i}. {c['topic']}</strong>
            <span style="background:{color};color:white;padding:2px 8px;border-radius:3px;font-size:12px;margin-left:8px;">{c['confidence']}</span>
            <br><br>{c['question'] or '(no question set)'}
            <br><small style="color:#999;">Reviewed {c['times_reviewed']} time(s)</small>
        </div>'''

    return f'''<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#333;">
        <h2 style="color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:8px;">Your Daily Review</h2>
        <p style="color:#666;">{today_display}</p>
        <p>Good morning {name}! You have <strong>{len(concepts)}</strong> concept(s) in <strong>{domain}</strong> ready for review.</p>
        <h3>Answer from memory (no peeking!):</h3>
        {questions_html}
        <div style="background:#e3f2fd;padding:16px;border-radius:8px;margin:24px 0;text-align:center;">
            <p style="margin:0;">Open your LLM and say: <strong>"I'm ready to review"</strong></p>
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
        <p style="font-size:11px;color:#aaa;text-align:center;">Aruni Learning System</p>
    </div>'''


def build_no_due_email(name, domain):
    today_display = datetime.now().strftime('%A, %B %d, %Y')
    return f'''<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#333;">
        <h2 style="color:#27ae60;">All caught up!</h2>
        <p style="color:#666;">{today_display}</p>
        <p>{name}, no concepts due for review today in <strong>{domain}</strong>.</p>
        <div style="background:#e8f5e9;padding:16px;border-radius:8px;margin:20px 0;">
            <p><strong>Ideas for today:</strong></p>
            <ul>
                <li>Open your LLM and say <strong>"Teach me something new"</strong></li>
                <li>Read something and discuss it with your LLM</li>
                <li>Ask a question you've been curious about</li>
            </ul>
        </div>
        <p style="font-size:11px;color:#aaa;text-align:center;">Aruni Learning System</p>
    </div>'''


def send_email(to_email, subject, html_body, sender_email, app_password):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr(('Aruni', sender_email))
    msg['To'] = to_email
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)


def process_user(sh, username, name, email, domain, sender_email, app_password):
    log(f"Processing {username} ({email})...")

    try:
        concepts = get_due_concepts(sh, username)
    except Exception as e:
        log(f"  ERROR reading tab '{username}': {e}")
        return False

    if concepts:
        subject = f"{len(concepts)} concept(s) to review - {domain}"
        body = build_review_email(name, domain, concepts)
    else:
        subject = f"All caught up! - {domain}"
        body = build_no_due_email(name, domain)

    try:
        send_email(email, subject, body, sender_email, app_password)
        log(f"  Sent to {email}: {len(concepts)} concepts due")
        return True
    except smtplib.SMTPAuthenticationError:
        log(f"  ERROR: Gmail auth failed. Check GMAIL_APP_PASSWORD in .env")
        log(f"  Generate one at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        log(f"  ERROR sending to {email}: {e}")
        return False


def main():
    load_env()

    app_password = os.environ.get('GMAIL_APP_PASSWORD', '')
    if not app_password:
        print("ERROR: GMAIL_APP_PASSWORD not set in .env")
        print("  1. Enable 2-Step Verification on your Google account")
        print("  2. Go to https://myaccount.google.com/apppasswords")
        print("  3. Create an app password, paste it in .env")
        sys.exit(1)

    sender_email = os.environ.get('SENDER_EMAIL', '')
    if not sender_email:
        print("ERROR: SENDER_EMAIL not set in .env")
        sys.exit(1)

    sh = get_sheet()
    config = sh.worksheet('config').get_all_records()

    # Filter to specific user if provided
    only_user = sys.argv[1] if len(sys.argv) > 1 else None

    sent = 0
    for user in config:
        username = user.get('user', '')
        if only_user and username != only_user:
            continue
        name = user.get('name', username)
        email = user.get('email', '')
        domain = user.get('domain', '')
        if not email:
            log(f"Skipping {username}: no email")
            continue
        if process_user(sh, username, name, email, domain, sender_email, app_password):
            sent += 1

    log(f"Done. {sent} email(s) sent.")


if __name__ == '__main__':
    main()
