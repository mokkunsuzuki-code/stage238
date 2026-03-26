#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Stage234 Ed25519 key pair.")
    parser.add_argument("--private-key", required=True)
    parser.add_argument("--public-key", required=True)
    args = parser.parse_args()

    private_path = Path(args.private_key)
    public_path = Path(args.public_key)

    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)

    if private_path.exists() or public_path.exists():
        raise SystemExit("[ERROR] key path already exists; refusing to overwrite")

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    public_path.write_bytes(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))

    print(f"[OK] wrote private key: {private_path}")
    print(f"[OK] wrote public key:  {public_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
