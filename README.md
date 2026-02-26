# Aruni Learning System

*Developed by Ram Kalyan Medury, Founder & CEO, Maxiom Wealth (since 2016).
IIT / IIM alumnus | ex-CIO ICICI | ex-Fintech Leader, Infosys.
ram@maxiomwealth.com | +91-9550290118*

---

Aruni is an AI-powered **Socratic learning companion**, named after the Vedic sage **Uddalaka Aruni** — who taught his son through questions and discovery in the Chandogya Upanishad, centuries before Socrates.

You just talk. Aruni teaches, tracks, and reminds. Everything is automatic.

---

## What Aruni Does

| Feature | How it works |
|---|---|
| **Teaches through questions** | Socratic method — never just lectures |
| **Tracks every concept** | Saved automatically, no data entry ever |
| **Spaced repetition** | Reviews scheduled at 1 → 3 → 7 → 14 → 30 days |
| **Daily 7 AM email** | Reminds you what to review — no laptop needed |
| **Works across laptops** | All progress lives in the cloud |
| **Any AI assistant** | Claude, Gemini, Codex — your choice |
| **Session tracking** | Start time, end time, duration — all logged |

---

## Before You Begin — Prerequisites

| Requirement | Check | Install |
|---|---|---|
| **Python 3.8+** | `python3 --version` | [python.org/downloads](https://www.python.org/downloads/) — tick "Add Python to PATH" on Windows |
| **Internet access** | — | Needed to sync your learning data |
| **Aruni password** | — | Get it from whoever invited you (via WhatsApp / iMessage) |
| **An AI assistant** | — | The setup script will help you install one (Claude / Gemini / Codex) |

> You do **not** need any Google account, API keys, or cloud credentials.
> One password unlocks everything — the setup script handles the rest.

---

## Setup — New Machine (Run Once)

**Mac / Linux:**
```bash
git clone https://github.com/medury-dot/aruni.git
cd aruni
bash setup_new_machine.sh
```

**Windows:**
```
git clone https://github.com/medury-dot/aruni.git
cd aruni
setup_new_machine.bat
```

The script will walk you through:
1. Checking Python is installed
2. Installing required packages
3. Unlocking credentials with the Aruni password
4. Verifying your connection to the learning data
5. Installing your preferred AI (Claude / Gemini / Codex)
6. Adding you as a learner
7. Launching your first session

---

## Daily Use

After setup, this is all you ever do:

```bash
cd users/<your-name>
claude        # or: gemini / codex
```

Aruni will immediately check what's due and greet you. Just talk naturally:

| Say this | What happens |
|---|---|
| *"I'm ready to learn"* | Aruni picks a topic and teaches you |
| *"I'm ready to review"* | Aruni quizzes you on what's due today |
| *"How am I doing?"* | Progress summary across all concepts |
| *"Teach me something new"* | Explores a new concept in your domain |
| *"Let's discuss [topic]"* | Deep dive via Socratic dialogue |

Everything — saving concepts, logging the session, scheduling reviews — happens automatically in the background.

---

## What Gets Tracked (Automatically)

**Every concept you learn:**
- Topic, domain, full explanation, recall question
- Confidence level (Low / Medium / High)
- Created at (date + time)
- Last reviewed (date + time)
- Next review date
- Number of times reviewed

**Every session:**
- Date, start time, end time, duration (minutes)
- Topics covered, key insights

**Your profile:**
- Name, email, domain, learning goal
- Date and time you joined

---

## FAQ

**Where is my data stored?**
Securely in the cloud — always accessible, never on your laptop. You can even view and edit it directly if you want.

**What if I switch laptops?**
`git clone` the repo and run `setup_new_machine.sh`. One password. Everything comes back.

**Can I use different AI assistants on different days?**
Yes — Claude on Monday, Gemini on Tuesday. All data is shared, nothing is lost.

**Do I need internet during a session?**
Only at the start (to check what's due) and end (to save what you learned).

**What if I forget the Aruni password?**
Ask whoever invited you — they have it.

**How does the daily email work?**
An automated script runs every morning at 7 AM inside the cloud — no laptop, no cron job needed.

**Can multiple people use the same system?**
Yes — each learner has their own private space, all on the same shared system.

---

## Admin Commands

*Only needed by whoever manages the system — not by learners.*

```bash
python3 setup.py add-user                    # Add a new learner
python3 setup.py regenerate <username>       # Rebuild a user's prompt files
python3 setup.py status                      # Check system status
python3 admin/daily_email.py                 # Send today's review email now
python3 admin/encrypt_creds.py               # Re-encrypt credentials (if key changes)
```

---

## Repository Structure

```
aruni/
├── README.md                 This file
├── setup.py                  Admin CLI
├── aruni.py                  Data helper (called by AI during sessions)
├── setup_new_machine.sh      One-time setup — Mac / Linux
├── setup_new_machine.bat     One-time setup — Windows
├── .aruni.key.enc            Encrypted credentials bundle (safe to share)
├── .env.example              Config template
├── users/
│   ├── <username>/
│   │   ├── CLAUDE.md         Prompt loaded by Claude Code
│   │   ├── GEMINI.md         Prompt loaded by Gemini CLI
│   │   └── AGENTS.md         Prompt loaded by OpenAI Codex
└── admin/                    Admin tools — learners don't need these
    ├── encrypt_creds.py
    ├── daily_email.py
    ├── email_trigger.gs
    ├── prompt_template.md
    └── requirements.txt
```

---

*Aruni — teaching through questions since the age of the Upanishads.*
