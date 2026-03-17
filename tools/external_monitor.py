#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"failed to load json: {path} ({e})")


def find_checkpoints(history_dir: Path) -> list[Path]:
    if not history_dir.exists():
        return []
    files = sorted(history_dir.glob("checkpoint*.json"))
    return [p for p in files if p.is_file()]


def extract_root(obj: dict) -> str | None:
    for key in ("merkle_root", "root", "tree_root"):
        v = obj.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def extract_count(obj: dict) -> int | None:
    for key in ("entry_count", "entries", "leaf_count"):
        v = obj.get(key)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return None


def extract_signature(obj: dict) -> str | None:
    for key in ("signature", "signed_root", "checkpoint_signature"):
        v = obj.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def build_history_report(history_files: list[Path]) -> tuple[list[dict], list[str], list[str]]:
    rows = []
    errors = []
    warnings = []

    prev_count = None

    for path in history_files:
        try:
            obj = load_json(path)
        except Exception as e:
            errors.append(str(e))
            continue

        root = extract_root(obj)
        count = extract_count(obj)
        sig = extract_signature(obj)

        row = {
            "file": str(path),
            "sha256": sha256_file(path),
            "merkle_root": root,
            "entry_count": count,
            "has_signature_field": bool(sig),
            "status": "ok",
        }

        if root is None:
            row["status"] = "error"
            errors.append(f"{path}: missing merkle_root/root/tree_root")
        if count is None:
            row["status"] = "error"
            errors.append(f"{path}: missing entry_count/entries/leaf_count")

        if prev_count is not None and count is not None:
            if count < prev_count:
                row["status"] = "error"
                errors.append(
                    f"{path}: entry_count decreased ({count} < {prev_count})"
                )
            elif count == prev_count:
                warnings.append(f"{path}: entry_count unchanged ({count})")

        prev_count = count if count is not None else prev_count
        rows.append(row)

    return rows, errors, warnings


def read_root_txt(root_file: Path) -> str | None:
    if not root_file.exists():
        return None
    text = root_file.read_text(encoding="utf-8").strip()
    return text or None


def compare_latest_with_current(
    history_rows: list[dict],
    current_checkpoint: Path | None,
    root_file: Path | None,
) -> tuple[list[str], list[str], dict]:
    errors = []
    warnings = []
    current = {
        "current_checkpoint_root": None,
        "root_txt_root": None,
        "latest_history_root": None,
        "current_checkpoint_entry_count": None,
        "latest_history_entry_count": None,
    }

    if not history_rows:
        warnings.append("no history rows found")
        return errors, warnings, current

    latest = history_rows[-1]
    latest_root = latest.get("merkle_root")
    latest_count = latest.get("entry_count")

    current["latest_history_root"] = latest_root
    current["latest_history_entry_count"] = latest_count

    if current_checkpoint is not None and current_checkpoint.exists():
        try:
            cp = load_json(current_checkpoint)
            cp_root = extract_root(cp)
            cp_count = extract_count(cp)
            current["current_checkpoint_root"] = cp_root
            current["current_checkpoint_entry_count"] = cp_count

            if cp_root is None:
                errors.append(f"{current_checkpoint}: missing merkle root")
            elif latest_root is not None and cp_root != latest_root:
                errors.append(
                    "latest history root does not match current checkpoint root "
                    f"({latest_root} != {cp_root})"
                )

            if cp_count is not None and latest_count is not None and cp_count != latest_count:
                errors.append(
                    "latest history entry_count does not match current checkpoint entry_count "
                    f"({latest_count} != {cp_count})"
                )
        except Exception as e:
            errors.append(str(e))
    else:
        warnings.append("current checkpoint file not found; skipped current checkpoint comparison")

    if root_file is not None and root_file.exists():
        rt = read_root_txt(root_file)
        current["root_txt_root"] = rt
        if rt is None:
            errors.append(f"{root_file}: empty root.txt")
        elif latest_root is not None and rt != latest_root:
            errors.append(
                f"latest history root does not match root.txt ({latest_root} != {rt})"
            )
    else:
        warnings.append("root.txt not found; skipped root.txt comparison")

    return errors, warnings, current


def main() -> int:
    parser = argparse.ArgumentParser(
        description="External monitor for transparency checkpoints/history"
    )
    parser.add_argument(
        "--history-dir",
        default="out/transparency/history",
        help="Directory containing checkpoint history files",
    )
    parser.add_argument(
        "--current-checkpoint",
        default="out/transparency/checkpoint.json",
        help="Path to current checkpoint.json",
    )
    parser.add_argument(
        "--root-file",
        default="out/transparency/root.txt",
        help="Path to root.txt",
    )
    parser.add_argument(
        "--output",
        default="out/monitor/monitor_report.json",
        help="Path to write monitor report JSON",
    )

    args = parser.parse_args()

    history_dir = Path(args.history_dir)
    current_checkpoint = Path(args.current_checkpoint)
    root_file = Path(args.root_file)
    output = Path(args.output)

    history_files = find_checkpoints(history_dir)

    history_rows, history_errors, history_warnings = build_history_report(history_files)
    compare_errors, compare_warnings, current = compare_latest_with_current(
        history_rows,
        current_checkpoint,
        root_file,
    )

    errors = history_errors + compare_errors
    warnings = history_warnings + compare_warnings

    report = {
        "tool": "external_monitor.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "history_dir": str(history_dir),
            "current_checkpoint": str(current_checkpoint),
            "root_file": str(root_file),
        },
        "summary": {
            "history_files_found": len(history_files),
            "ok": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "history": history_rows,
        "current_comparison": current,
        "errors": errors,
        "warnings": warnings,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if len(errors) == 0:
        print(f"[OK] wrote: {output}")
        print(f"[OK] history files: {len(history_files)}")
        print("[OK] external monitor passed")
        return 0
    else:
        print(f"[OK] wrote: {output}")
        print(f"[NG] error count: {len(errors)}")
        for e in errors:
            print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
