#!/usr/bin/env python3
"""
Aruni - Encrypt google_creds.json for safe storage in git.

Run this once (or whenever the service account key changes):
    python3 encrypt_creds.py

You will be asked to set a password. Share that password with
new users via WhatsApp/iMessage. They enter it once during setup.
"""

import os
import sys
import base64
import hashlib
import getpass

ARUNI_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(ARUNI_DIR, 'google_creds.json')
ENC_FILE   = os.path.join(ARUNI_DIR, 'google_creds.json.enc')

def make_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt():
    from cryptography.fernet import Fernet

    if not os.path.exists(CREDS_FILE):
        print(f"ERROR: {CREDS_FILE} not found.")
        sys.exit(1)

    password = getpass.getpass("Set encryption password: ")
    confirm  = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("ERROR: Passwords do not match.")
        sys.exit(1)

    if len(password) < 4:
        print("ERROR: Password too short (minimum 4 characters).")
        sys.exit(1)

    f = Fernet(make_key(password))
    with open(CREDS_FILE, 'rb') as fh:
        encrypted = f.encrypt(fh.read())
    with open(ENC_FILE, 'wb') as fh:
        fh.write(encrypted)

    print()
    print(f"Encrypted -> google_creds.json.enc")
    print()
    print("Next steps:")
    print("  1. Commit and push: git add google_creds.json.enc && git commit -m 'update encrypted creds' && git push")
    print("  2. Share the password with new users via WhatsApp/iMessage")
    print("  3. New users just run: bash setup_new_machine.sh")

def decrypt(password):
    """Called by setup_new_machine.sh -- not for direct use."""
    from cryptography.fernet import Fernet

    if not os.path.exists(ENC_FILE):
        print(f"ERROR: {ENC_FILE} not found.")
        sys.exit(1)

    try:
        f = Fernet(make_key(password))
        with open(ENC_FILE, 'rb') as fh:
            decrypted = f.decrypt(fh.read())
        with open(CREDS_FILE, 'wb') as fh:
            fh.write(decrypted)
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
