#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p out/sbom

if ! command -v syft >/dev/null 2>&1; then
  echo "[ERROR] syft is not installed."
  echo "Install example:"
  echo "  brew install syft"
  exit 1
fi

syft . -o spdx-json=out/sbom/stage237_repo.spdx.json

echo "[OK] wrote: out/sbom/stage237_repo.spdx.json"
