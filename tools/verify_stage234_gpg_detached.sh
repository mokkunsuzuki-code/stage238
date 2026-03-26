#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <payload> <signature.asc> <public-key.asc>"
  exit 1
fi

PAYLOAD="$1"
SIG="$2"
PUBKEY="$3"

TMP_GNUPG="$(mktemp -d)"
trap 'rm -rf "$TMP_GNUPG"' EXIT
chmod 700 "$TMP_GNUPG"

gpg --homedir "$TMP_GNUPG" --import "$PUBKEY" >/dev/null 2>&1
gpg --homedir "$TMP_GNUPG" --verify "$SIG" "$PAYLOAD"

echo "[OK] Stage234 GPG detached signature verified"
