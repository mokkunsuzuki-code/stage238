# Stage230: Signed Evidence Bundle for Surface-Level Proof

## Overview

Stage230 introduces a **Signed Evidence Bundle** for QSP.

Up to Stage229, the project provided multiple verifiable security artifacts:

- fail evidence
- transparency log artifacts
- signed checkpoints
- proof artifacts
- monitoring outputs
- claim documents

Stage230 moves from **point-by-point proof** to **surface-level proof** by collecting those artifacts into a single deterministic manifest and signing that manifest with Ed25519.

This means the project no longer says only:

- "there are several pieces of evidence"

It can now say:

- "there is one signed evidence surface that binds those pieces together"

---

## What Stage230 Adds

Stage230 adds:

- deterministic evidence bundle manifest generation
- SHA256 hashing of each referenced file
- Ed25519 signature over the canonical bundle payload
- signature verification
- referenced-file integrity verification
- reproducible execution script
- automated test for end-to-end bundle generation and verification

---

## Security Meaning

The Signed Evidence Bundle lets a reviewer verify:

1. the bundle payload was not modified
2. the payload was signed by the expected signer
3. every referenced file still matches its recorded SHA256 hash

This strengthens the project from isolated evidence verification to **signed evidence binding**.

---

## Repository Structure

```text
docs/
  signed_evidence_bundle.md

tools/
  build_signed_evidence_bundle.py
  verify_signed_evidence_bundle.py
  run_stage230_signed_bundle.sh

tests/
  test_signed_evidence_bundle.py

out/bundle/
  evidence_bundle_payload.json
  evidence_bundle_signature.json
  evidence_bundle_summary.json
Requirements
Python 3.10+
cryptography
pytest

Example:

python3 -m pip install cryptography pytest
Key Generation

Generate an Ed25519 signing keypair:

mkdir -p keys

python3 - << 'EOF'
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

with open("keys/checkpoint_signing_private.pem", "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

with open("keys/checkpoint_signing_public.pem", "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

print("[OK] key pair generated")
EOF
Quick Start

Run the Stage230 signed bundle flow:

bash tools/run_stage230_signed_bundle.sh

Expected outputs:

out/bundle/evidence_bundle_payload.json
out/bundle/evidence_bundle_signature.json
out/bundle/evidence_bundle_summary.json

Example verification output:

[OK] bundle_id: qsp-stage230-signed-evidence-bundle
[OK] file_count: 32
[OK] signature verified
[OK] verified_files: 32
[OK] Stage230 signed evidence bundle complete
Run Tests
pytest -q
Verification Model

Stage230 verifies a signed evidence surface in this order:

Evidence Files
    ↓
Deterministic Manifest
    ↓
SHA256 Binding
    ↓
Ed25519 Signature
    ↓
Independent Verification

This provides a stronger review surface for external researchers, implementers, and auditors.

Why This Matters

Stage229 preserved individual evidence artifacts.

Stage230 binds them together cryptographically.

That is the key evolution:

Stage229 = evidence exists
Stage230 = evidence exists as one signed verification surface

This improves:

integrity
reviewer clarity
external reproducibility
auditability
security communication
Notes
The public key may be committed for verification.
The private key must never be committed.
Generated bundle outputs should remain untracked.
This repository is not a full cryptographic security proof of a deployed protocol.
It is a reproducible verification framework for signed security evidence binding.
License

MIT License

Copyright (c) 2025 Motohiro Suzuki