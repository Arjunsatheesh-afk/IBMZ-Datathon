"""
vault.py - reviewer-only re-identification with an audit trail.

The vault maps a token to the AES-GCM encrypted original ID. Format of each value (hex):
    12-byte nonce | 16-byte tag | ciphertext
Analysts only ever see tokens. A Reviewer may call reidentify(), which needs the AES key,
a reviewer name and a written reason, and ALWAYS writes an audit line (the raw ID is never
written to the log, only the token).
"""
import json
import time

from Crypto.Cipher import AES


def load_vault(path):
    with open(path) as fh:
        return json.load(fh)


def load_key(path):
    with open(path, "rb") as fh:
        return fh.read()


def decrypt_id(blob_hex, aes_key):
    b = bytes.fromhex(blob_hex)
    return AES.new(aes_key, AES.MODE_GCM, nonce=b[:12]).decrypt_and_verify(b[28:], b[12:28]).decode()


def _audit(path, entry):
    with open(path, "a") as fh:
        fh.write(json.dumps(entry) + "\n")


def reidentify(token, reviewer, reason, vault, aes_key, audit_path="audit_log.jsonl"):
    """Return the original ID for a token, or None. Always writes an audit entry."""
    entry = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "reviewer": (reviewer or "").strip(),
        "token": token,
        "reason": (reason or "").strip(),
    }
    if not entry["reviewer"] or not entry["reason"]:
        entry["result"] = "denied_missing_reviewer_or_reason"
        _audit(audit_path, entry)
        raise ValueError("A reviewer name and a reason are required")
    blob = vault.get(token)
    if blob is None:
        entry["result"] = "token_not_in_vault"
        _audit(audit_path, entry)
        return None
    try:
        raw = decrypt_id(blob, aes_key)
    except ValueError:
        entry["result"] = "decrypt_failed"
        _audit(audit_path, entry)
        return None
    entry["result"] = "reidentified"
    _audit(audit_path, entry)
    return raw
