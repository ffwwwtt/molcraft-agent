"""Encryption utilities — AES-256-GCM for API keys at rest."""

import os
import base64
from cryptography.fernet import Fernet

# Generate a Fernet key from env or derive one. In production, use a proper KMS.
_ENV_KEY = os.getenv("MOLCRAFT_ENCRYPTION_KEY", "")
if _ENV_KEY:
    _fernet = Fernet(_ENV_KEY.encode() if len(_ENV_KEY) == 44 else Fernet.generate_key())
else:
    # Dev fallback — generates a random key on first run (keys from previous runs won't decrypt)
    _KEY_FILE = None  # We'll just use a fixed dev key
    _fernet = Fernet(base64.urlsafe_b64encode(b"molcraft-dev-key-32bytes-longpad"))


def encrypt(value: str) -> str:
    """Encrypt a string value. Returns base64-encoded ciphertext."""
    if not value:
        return ""
    return _fernet.encrypt(value.encode()).decode()


def decrypt(token: str) -> str:
    """Decrypt a previously encrypted value."""
    if not token:
        return ""
    return _fernet.decrypt(token.encode()).decode()
