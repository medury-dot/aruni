#!/usr/bin/env python3
"""
Aruni - Encrypt access credentials and data store ID for safe storage in git.

Run this once (or whenever credentials or sheet ID change):
    python3 encrypt_creds.py

You will be asked to set a password. Share that password with
new users via WhatsApp/iMessage. They enter it once during setup.

The encrypted bundle contains both the access key AND the data store ID.
Nothing sensitive is stored in plain text anywhere in the repo.
"""

import os
import sys
import json
import base64
import hashlib
import getpass

ARUNI_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(ARUNI_DIR, '.aruni.key')
ENC_FILE   = os.path.join(ARUNI_DIR, '.aruni.key.enc')
ENV_FILE   = os.path.join(ARUNI_DIR, '.env')


def make_fernet_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def load_env():
    if not os.path.exists(ENV_FILE):
        return
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ[k.strip()] = v.strip().strip('"').strip("'")


def save_env_var(key, value):
    lines = []
    found = False
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            found = True
            break
    if not found:
        lines.append(f'{key}={value}\n')
    with open(ENV_FILE, 'w') as f:
        f.writelines(lines)


def encrypt():
    from cryptography.fernet import Fernet

    if not os.path.exists(CREDS_FILE):
        print(f"ERROR: {CREDS_FILE} not found.")
        print("Place your service account JSON file there and try again.")
        sys.exit(1)

    load_env()
    sheet_id = os.environ.get('ARUNI_DB', '').strip()
    if not sheet_id:
        sheet_id = input("Enter the data store ID: ").strip()
        if not sheet_id:
            print("ERROR: Data store ID is required.")
            sys.exit(1)

    password = getpass.getpass("Set encryption password: ")
    confirm  = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("ERROR: Passwords do not match.")
        sys.exit(1)

    if len(password) < 4:
        print("ERROR: Password too short (minimum 4 characters).")
        sys.exit(1)

    with open(CREDS_FILE, 'rb') as fh:
        creds_bytes = fh.read()

    # Bundle: {"sheet_id": "...", "creds": {...}}
    bundle = json.dumps({
        "sheet_id": sheet_id,
        "creds": json.loads(creds_bytes.decode('utf-8'))
    }).encode('utf-8')

    f = Fernet(make_fernet_key(password))
    encrypted = f.encrypt(bundle)

    with open(ENC_FILE, 'wb') as fh:
        fh.write(encrypted)

    print()
    print("Credentials locked and ready.")
    print()
    print("Next steps:")
    print(f"  1. Commit and push: git add .aruni.key.enc && git commit -m 'update credentials' && git push")
    print("  2. Share the password with new users via WhatsApp/iMessage")
    print("  3. New users just run: bash setup_new_machine.sh")


def decrypt(password):
    """Called by setup_new_machine.sh -- not for direct use."""
    from cryptography.fernet import Fernet

    if not os.path.exists(ENC_FILE):
        print(f"ERROR: Access file not found. Re-clone the repo and try again.")
        sys.exit(1)

    try:
        f = Fernet(make_fernet_key(password))
        with open(ENC_FILE, 'rb') as fh:
            bundle = json.loads(f.decrypt(fh.read()).decode('utf-8'))

        # Write .aruni.key
        with open(CREDS_FILE, 'w') as fh:
            json.dump(bundle['creds'], fh, indent=2)

        # Write ARUNI_DB to .env
        save_env_var('ARUNI_DB', bundle['sheet_id'])
        save_env_var('ARUNI_KEY_PATH', CREDS_FILE)

        print("  OK: Access granted!")
    except Exception:
        print("  ERROR: Incorrect password. Please check with whoever shared the Aruni password.")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # Called by setup script: python3 encrypt_creds.py <password>
        decrypt(sys.argv[1])
    else:
        encrypt()
