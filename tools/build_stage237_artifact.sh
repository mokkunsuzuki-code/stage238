#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p dist out/sbom

ARTIFACT="dist/stage237_source_bundle.tar.gz"
SHA_FILE="dist/stage237_source_bundle.tar.gz.sha256"

INCLUDE_PATHS=()

for p in README.md claims docs tools tests .github; do
  if [ -e "$p" ]; then
    INCLUDE_PATHS+=("$p")
  fi
done

shopt -s nullglob
for p in *.py *.sh; do
  INCLUDE_PATHS+=("$p")
done
shopt -u nullglob

if [ ${#INCLUDE_PATHS[@]} -eq 0 ]; then
  echo "[ERROR] no input files found for artifact"
  exit 1
fi

tar \
  --exclude=".git" \
  --exclude=".venv" \
  --exclude="__pycache__" \
  --exclude=".pytest_cache" \
  --exclude="dist" \
  --exclude="out/sbom" \
  -czf "$ARTIFACT" \
  "${INCLUDE_PATHS[@]}"

if [ ! -f "$ARTIFACT" ]; then
  echo "[ERROR] artifact was not created"
  exit 1
fi

shasum -a 256 "$ARTIFACT" | awk '{print $1}' > "$SHA_FILE"

echo "[OK] artifact: $ARTIFACT"
echo "[OK] sha256: $(cat "$SHA_FILE")"
