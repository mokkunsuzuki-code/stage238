#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: $0 <payload> <output.asc> [fingerprint-or-email]"
  exit 1
fi

PAYLOAD="$1"
OUT="$2"
KEY_ID="${3:-}"

mkdir -p "$(dirname "$OUT")"

if [ -n "$KEY_ID" ]; then
  gpg --armor --local-user "$KEY_ID" --output "$OUT" --detach-sign "$PAYLOAD"
else
  gpg --armor --output "$OUT" --detach-sign "$PAYLOAD"
fi

echo "[OK] wrote GPG detached signature: $OUT"
