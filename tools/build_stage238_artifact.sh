#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/artifacts"
mkdir -p "$OUT_DIR"

ARTIFACT="$OUT_DIR/stage238-source-bundle.tar.gz"

tar \
  --exclude=".git" \
  --exclude="out" \
  --exclude="__pycache__" \
  --exclude=".pytest_cache" \
  -czf "$ARTIFACT" \
  -C "$ROOT_DIR" \
  .

echo "[OK] built artifact: $ARTIFACT"
shasum -a 256 "$ARTIFACT" | tee "$OUT_DIR/stage238-source-bundle.sha256"
