import json
import subprocess
import sys
from pathlib import Path


def test_stage231_multi_signer_flow():
    repo_root = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        ["bash", "tools/run_stage231_multi_signer.sh"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    bundle_path = repo_root / "out" / "multi_signer" / "signed_bundle.json"
    assert bundle_path.exists()

    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert data["type"] == "qsp-multi-signed-bundle"
    assert data["signature_count"] == 3
    assert len(data["signatures"]) == 3
