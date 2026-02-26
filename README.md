# Aruni Learning System

*Developed by Ram Kalyan Medury, Founder & CEO, Maxiom Wealth (since 2016). IIT / IIM alumnus, ex-CIO ICICI, ex-Fintech Leader Infosys.*

---

Aruni is an AI-powered Socratic learning companion, named after the Vedic sage **Uddalaka Aruni** who taught his son through questions and discovery in the Chandogya Upanishad — the Socratic method, centuries before Socrates.

It works with any LLM: **Claude Code**, **Gemini CLI**, **OpenAI Codex**, or any future AI assistant. All learning data is stored securely in the cloud — nothing sensitive on your laptop.

---

## Prerequisites

Before running the setup script, make sure you have the following:

| Requirement | How to check | Install |
|---|---|---|
| **Python 3.8+** | `python3 --version` | [python.org/downloads](https://www.python.org/downloads/) (check "Add Python to PATH" on Windows) |
| **pip** | `pip3 --version` | Comes with Python |
| **Internet access** | — | Required to sync learning data |
| **The Aruni password** | — | Get it from whoever set up this system (shared via WhatsApp/iMessage) |

> **You do NOT need** any API keys, cloud accounts, or credentials — everything is already bundled (encrypted) in this repo. One password unlocks it all.

---

## Setup (New Machine)

**Mac / Linux:**
```bash
bash setup_new_machine.sh
```

**Windows:**
```
setup_new_machine.bat
```

The script will:
1. Check Python is installed
2. Install required Python packages
3. Ask for the Aruni password to unlock credentials
4. Set up your local configuration
5. Verify the connection to your learning data
6. Guide you to install your preferred AI assistant
7. Show a full usage guide

---

## Quick Start

```bash
# Add yourself as a learner (one time)
python3 setup.py add-user

# Start a learning session
cd users/<your-name>
claude        # Claude Code
gemini        # Gemini CLI
codex         # OpenAI Codex
```

Then just say: **"I'm ready to learn"** — Aruni takes it from there.

---

## What Aruni Does

- **Teaches through questions**, not lectures (Socratic method)
- **Tracks every concept** you learn (automatic, no data entry)
- **Spaced repetition**: schedules reviews at 1 → 3 → 7 → 14 → 30 days
- **Daily 7 AM email**: reminds you what to review today (no laptop needed)
- **Multi-user**: each person has their own private learning space
- **LLM-agnostic**: works with Claude, Gemini, Codex, or any future AI

---

## Useful Commands

```bash
python3 setup.py status           # Check system status
python3 setup.py add-user         # Add a new learner
python3 daily_email.py            # Send today's review email (all users)
python3 daily_email.py <name>     # Send email for one learner
python3 encrypt_creds.py          # Re-encrypt credentials (admin only)
```

**During a session, try saying:**
- `"I'm ready to learn"` — Start a new topic
- `"I'm ready to review"` — Review concepts due today
- `"How am I doing?"` — See your progress summary
- `"Teach me something new"` — Explore a related concept

---

## FAQ

**Where is my data stored?**
Securely in the cloud — visible, editable, and yours forever. Nothing sensitive is on your laptop.

**What if I switch laptops?**
Just run `setup_new_machine.sh` on the new machine. One password, that's all.

**Can multiple people use the same system?**
Yes — each learner has their own private learning space.

**Do I need internet during a session?**
Only when starting or ending a session to sync your data.

**What if I forget the Aruni password?**
Ask whoever set up this system — they have the password.

**How do daily reminder emails work?**
An automated script runs inside the data store at 7 AM daily — no laptop, no cron job needed.

---

## Repository Structure

```
aruni/
├── setup.py                  Main CLI (init, add-user, status, migrate)
├── setup_new_machine.sh      One-time setup for Mac/Linux
├── setup_new_machine.bat     One-time setup for Windows
├── encrypt_creds.py          Encrypt/decrypt access credentials (admin only)
├── daily_email.py            Python fallback for daily emails
├── email_trigger.gs          Automated daily email script
├── prompt_template.md        Universal teaching prompt template
├── requirements.txt          Python dependencies
├── .env.example              Environment variable template
├── .aruni.key.enc            Encrypted access bundle (safe to commit)
└── users/
    ├── varnika/
    │   ├── CLAUDE.md         Prompt for Claude Code
    │   ├── GEMINI.md         Prompt for Gemini CLI
    │   └── AGENTS.md         Prompt for OpenAI Codex
    └── ram/
        ├── CLAUDE.md
        ├── GEMINI.md
        └── AGENTS.md
```

---

*Aruni — teaching through questions since the age of the Upanishads.*
