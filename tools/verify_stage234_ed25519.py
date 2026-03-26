#!/usr/bin/env python3
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Stage234 Ed25519 signature.")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--signature", required=True)
    parser.add_argument("--public-key", required=True)
    args = parser.parse_args()

    payload_path = Path(args.payload)
    signature_path = Path(args.signature)
    public_key_path = Path(args.public_key)

    payload = payload_path.read_bytes()
    sig_doc = json.loads(signature_path.read_text(encoding="utf-8"))

    actual_sha256 = sha256_bytes(payload)
    expected_sha256 = sig_doc["payload_sha256"]
    if actual_sha256 != expected_sha256:
        raise SystemExit(
            f"[ERROR] payload sha256 mismatch: expected={expected_sha256} actual={actual_sha256}"
        )

    public_key = serialization.load_pem_public_key(public_key_path.read_bytes())
    signature = base64.b64decode(sig_doc["signature_base64"])

    try:
        public_key.verify(signature, payload)
    except InvalidSignature as exc:
        raise SystemExit("[ERROR] invalid Ed25519 signature") from exc

    print("[OK] Stage234 Ed25519 signature verified")
    print(f"[OK] key_id: {sig_doc['key_id']}")
    print(f"[OK] payload_sha256: {actual_sha256}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
