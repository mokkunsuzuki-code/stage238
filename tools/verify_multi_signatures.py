#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_public_key_from_pem_str(pem_text: str) -> Ed25519PublicKey:
    return serialization.load_pem_public_key(pem_text.encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Verify multi-signer bundle")
    parser.add_argument("--bundle", required=True, help="Path to signed bundle JSON")
    parser.add_argument("--min-valid-signatures", type=int, default=1, help="Minimum required valid signatures")
    args = parser.parse_args()

    bundle = load_json(Path(args.bundle))
    payload = bundle["payload"]
    expected_sha256 = bundle["payload_sha256"]
    payload_bytes = canonical_json_bytes(payload)
    actual_sha256 = hashlib.sha256(payload_bytes).hexdigest()

    if expected_sha256 != actual_sha256:
        print("[ERROR] payload_sha256 mismatch")
        print(f"expected: {expected_sha256}")
        print(f"actual  : {actual_sha256}")
        sys.exit(1)

    valid_count = 0
    for item in bundle.get("signatures", []):
        signer_id = item["signer_id"]
        signature = base64.b64decode(item["signature_b64"])
        public_key = load_public_key_from_pem_str(item["public_key_pem"])

        try:
            public_key.verify(signature, payload_bytes)
            valid_count += 1
            print(f"[OK] valid signature: {signer_id}")
        except InvalidSignature:
            print(f"[ERROR] invalid signature: {signer_id}")

    print(f"[OK] valid_count: {valid_count}")

    if valid_count < args.min_valid_signatures:
        print(
            f"[ERROR] verification policy failed: "
            f"required={args.min_valid_signatures}, valid={valid_count}"
        )
        sys.exit(1)

    print("[OK] multi-signer verification passed")


if __name__ == "__main__":
    main()
