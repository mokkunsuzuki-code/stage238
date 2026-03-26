#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description="Build Stage234 release manifest.")
    parser.add_argument("--output", required=True)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    files = []
    for raw in sorted(args.paths):
        p = Path(raw)
        if not p.is_file():
            raise SystemExit(f"[ERROR] file not found: {p}")
        files.append({
            "path": p.as_posix(),
            "sha256": sha256_file(p),
            "size": p.stat().st_size,
        })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "version": 1,
        "type": "stage234_release_manifest",
        "files": files,
    }, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    print(f"[OK] wrote manifest: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
