from pathlib import Path
import sys

caller = Path(".github/workflows/stage238-slsa-policy.yml")
reusable = Path(".github/workflows/reusable-slsa-build.yml")
policy_doc = Path("docs/slsa_policy.md")

missing = [str(p) for p in [caller, reusable, policy_doc] if not p.exists()]
if missing:
    print("[NG] missing files:")
    for m in missing:
        print(" -", m)
    sys.exit(1)

caller_text = caller.read_text()
reusable_text = reusable.read_text()

checks = [
    ("caller uses reusable workflow", "uses: ./.github/workflows/reusable-slsa-build.yml" in caller_text),
    ("reusable uses workflow_call", "workflow_call:" in reusable_text),
    ("reusable has attest-build-provenance", "actions/attest-build-provenance@v2" in reusable_text),
    ("reusable has attest-sbom", "actions/attest-sbom@v2" in reusable_text),
    ("reusable has id-token permission", "id-token: write" in reusable_text),
    ("reusable has attestations permission", "attestations: write" in reusable_text),
]

failed = False
for label, ok in checks:
    if ok:
        print(f"[OK] {label}")
    else:
        print(f"[NG] {label}")
        failed = True

sys.exit(1 if failed else 0)
