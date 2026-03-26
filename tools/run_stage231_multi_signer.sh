#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p keys
mkdir -p out/multi_signer

python3 - << 'PY'
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

signers = [
    "owner",
    "third_party",
    "researcher",
]

Path("keys").mkdir(parents=True, exist_ok=True)

for signer in signers:
    private_path = Path(f"keys/{signer}_private.pem")
    public_path = Path(f"keys/{signer}_public.pem")

    if private_path.exists() and public_path.exists():
        print(f"[OK] existing keys: {signer}")
        continue

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path.write_bytes(private_bytes)
    public_path.write_bytes(public_bytes)
    print(f"[OK] generated keys: {signer}")
PY

if [ -f out/checkpoint/checkpoint_payload.json ]; then
  cp out/checkpoint/checkpoint_payload.json out/multi_signer/payload.json
  echo "[OK] using payload from out/checkpoint/checkpoint_payload.json"
elif [ -f out/transparency/checkpoint.json ]; then
  cp out/transparency/checkpoint.json out/multi_signer/payload.json
  echo "[OK] using payload from out/transparency/checkpoint.json"
else
  python3 - << 'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

payload = {
    "log_id": "qsp-transparency-log",
    "tree_size": 0,
    "merkle_root": "demo-root-placeholder",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "note": "fallback demo payload for stage231 multi-signer",
}

path = Path("out/multi_signer/payload.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"[OK] wrote fallback payload: {path}")
PY
fi

python3 tools/multi_sign_checkpoint.py \
  --payload out/multi_signer/payload.json \
  --output out/multi_signer/signed_bundle.json \
  --signer owner keys/owner_private.pem \
  --signer third_party keys/third_party_private.pem \
  --signer researcher keys/researcher_private.pem

python3 tools/verify_multi_signatures.py \
  --bundle out/multi_signer/signed_bundle.json \
  --min-valid-signatures 3

echo "[OK] Stage231 multi-signer flow completed"
