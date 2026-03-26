#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p out/signatures keys/private keys/public gpg_pubkeys

MANIFEST="out/signatures/stage234_release_manifest.json"
ED25519_PRIVATE="keys/private/stage234_ed25519_private.pem"
ED25519_PUBLIC="keys/public/stage234_ed25519_public.pem"
ED25519_SIG="out/signatures/stage234_release_manifest.ed25519.sig.json"
GPG_SIG="out/signatures/stage234_release_manifest.json.asc"
GPG_PUB="gpg_pubkeys/stage234_maintainer_public.asc"

echo "[INFO] running existing Stage233 flow first"
if [ -x ./tools/run_stage233_external.sh ]; then
  ./tools/run_stage233_external.sh
else
  echo "[WARN] tools/run_stage233_external.sh not found or not executable"
fi

if [ ! -f "$ED25519_PRIVATE" ] && [ ! -f "$ED25519_PUBLIC" ]; then
  python3 tools/generate_stage234_ed25519_keypair.py \
    --private-key "$ED25519_PRIVATE" \
    --public-key "$ED25519_PUBLIC"
fi

python3 tools/build_stage234_release_manifest.py \
  --output "$MANIFEST" \
  README.md \
  docs/stage234_real_keys.md \
  external_signatures/config.yaml \
  tools/run_stage233_external.sh \
  tools/build_stage234_release_manifest.py \
  tools/generate_stage234_ed25519_keypair.py \
  tools/sign_stage234_ed25519.py \
  tools/verify_stage234_ed25519.py \
  tools/export_stage234_gpg_public_key.sh \
  tools/sign_stage234_gpg_detached.sh \
  tools/verify_stage234_gpg_detached.sh \
  tools/run_stage234_real_keys.sh

python3 tools/sign_stage234_ed25519.py \
  --payload "$MANIFEST" \
  --private-key "$ED25519_PRIVATE" \
  --key-id "stage234_local_ed25519" \
  --output "$ED25519_SIG"

python3 tools/verify_stage234_ed25519.py \
  --payload "$MANIFEST" \
  --signature "$ED25519_SIG" \
  --public-key "$ED25519_PUBLIC"

if command -v gpg >/dev/null 2>&1; then
  if [ -n "${STAGE234_GPG_KEY_ID:-}" ]; then
    bash tools/export_stage234_gpg_public_key.sh "$STAGE234_GPG_KEY_ID" "$GPG_PUB"
    bash tools/sign_stage234_gpg_detached.sh "$MANIFEST" "$GPG_SIG" "$STAGE234_GPG_KEY_ID"
    bash tools/verify_stage234_gpg_detached.sh "$MANIFEST" "$GPG_SIG" "$GPG_PUB"
  else
    echo "[WARN] STAGE234_GPG_KEY_ID is not set; skipping GPG signing"
    echo '[WARN] example: export STAGE234_GPG_KEY_ID="your_gpg_fingerprint_or_email"'
  fi
else
  echo "[WARN] gpg command not found; skipping GPG signing"
fi

echo "[OK] Stage234 real-key flow completed"
echo "[OK] manifest: $MANIFEST"
echo "[OK] Ed25519 public key: $ED25519_PUBLIC"
echo "[OK] Ed25519 signature: $ED25519_SIG"
if [ -f "$GPG_SIG" ]; then
  echo "[OK] GPG signature: $GPG_SIG"
fi
