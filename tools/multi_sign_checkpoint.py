#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_private_key(path: Path) -> Ed25519PrivateKey:
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=None)


def main():
    parser = argparse.ArgumentParser(description="Sign a payload with multiple Ed25519 signers")
    parser.add_argument("--payload", required=True, help="Path to payload JSON")
    parser.add_argument("--output", required=True, help="Path to output signed bundle JSON")
    parser.add_argument(
        "--signer",
        action="append",
        nargs=2,
        metavar=("SIGNER_ID", "PRIVATE_KEY_PEM"),
        required=True,
        help="Signer id and private key path. Repeat for multiple signers.",
    )
    args = parser.parse_args()

    payload_path = Path(args.payload)
    output_path = Path(args.output)

    payload = load_json(payload_path)
    payload_bytes = canonical_json_bytes(payload)
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()

    signatures = []
    for signer_id, private_key_path in args.signer:
        key = load_private_key(Path(private_key_path))
        public_key = key.public_key()
        signature = key.sign(payload_bytes)

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        signatures.append(
            {
                "signer_id": signer_id,
                "private_key_path": private_key_path,
                "signature_b64": base64.b64encode(signature).decode("ascii"),
                "public_key_pem": public_pem,
            }
        )

    bundle = {
        "type": "qsp-multi-signed-bundle",
        "version": 1,
        "payload_sha256": payload_sha256,
        "payload": payload,
        "signature_count": len(signatures),
        "signatures": signatures,
    }

    save_json(output_path, bundle)

    print(f"[OK] wrote: {output_path}")
    print(f"[OK] payload_sha256: {payload_sha256}")
    print(f"[OK] signature_count: {len(signatures)}")


if __name__ == "__main__":
    main()
