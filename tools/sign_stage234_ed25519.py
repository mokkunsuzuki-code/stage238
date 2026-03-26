#!/usr/bin/env python3
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description="Sign payload with Stage234 Ed25519 private key.")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--private-key", required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload_path = Path(args.payload)
    private_key_path = Path(args.private_key)
    output_path = Path(args.output)

    payload = payload_path.read_bytes()
    private_key = serialization.load_pem_private_key(
        private_key_path.read_bytes(),
        password=None,
    )
    signature = private_key.sign(payload)

    sig_doc = {
        "version": 1,
        "algorithm": "Ed25519",
        "key_id": args.key_id,
        "payload_path": payload_path.as_posix(),
        "payload_sha256": sha256_bytes(payload),
        "signature_base64": base64.b64encode(signature).decode("ascii"),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sig_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[OK] wrote signature: {output_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
