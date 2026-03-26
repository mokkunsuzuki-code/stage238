#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <fingerprint-or-email> <output.asc>"
  exit 1
fi

KEY_ID="$1"
OUT="$2"

mkdir -p "$(dirname "$OUT")"
gpg --armor --export "$KEY_ID" > "$OUT"

echo "[OK] exported GPG public key: $OUT"
