# Stage229: Signed Fail Evidence (Ed25519)

## Overview

Stage229 introduces **cryptographic authenticity** to fail evidence.

Failures are no longer just recorded and hashed —  
they are now **digitally signed and independently verifiable**.

This transforms the system from:

- verifiable logs → **cryptographic evidence**

---

## Core Pipeline


Attack
↓
Fail detection
↓
Log persistence
↓
SHA256 (Integrity)
↓
Ed25519 Signature (Authenticity)
↓
Transparency Log (Merkle Tree)
↓
Independent Verification


---

## What This Stage Achieves

### Before (Stage228)
- Fail logs persisted
- SHA256 ensures integrity
- Tampering detectable

### After (Stage229)
- Evidence is **signed**
- Proven origin (authenticity)
- Non-repudiation
- Third-party verifiable

---

## Cryptographic Properties

| Property        | Status |
|----------------|--------|
| Integrity      | ✅ SHA256 |
| Authenticity   | ✅ Ed25519 |
| Non-repudiation| ✅ Signature |
| Transparency   | ✅ Merkle Tree |

---

## Evidence Structure

Example:

```json
{
  "version": 1,
  "type": "fail_evidence",
  "log_file": "out/failures/downgrade_fail.log",
  "sha256": "...",
  "size_bytes": 147,
  "line_count": 4,
  "status": "signed",
  "signature": "...",
  "public_key": "-----BEGIN PUBLIC KEY-----..."
}
Quick Start

Run the full pipeline:

bash tools/run_stage229_signed_fail_evidence.sh
Verification
Verify evidence integrity
python3 tools/verify_fail_evidence.py \
  --index out/fail_evidence/index.json
Verify signatures
python3 tools/verify_signature.py \
  --evidence out/fail_evidence/*.evidence.json
Verify transparency log
python3 tools/verify_transparency_log.py \
  --log out/transparency/transparency_log.json \
  --tree out/transparency/merkle_tree.json \
  --root out/transparency/root.txt
Security Model
Guarantees
Evidence cannot be modified without detection
Evidence origin is cryptographically provable
Anyone can verify independently
Non-goals
Not a full protocol security proof
Does not prevent attacks
Focus is evidence integrity + authenticity
Key Management
Private keys are never committed
Public keys are included for verification
.gitignore enforces secret protection
Project Position

Stage229 represents the transition from:

Forensic evidence → Cryptographic evidence system

This is a foundational step toward:

reproducible security proofs
verifiable incident evidence
research-grade validation pipelines
License

MIT License

© 2025 Motohiro Suzuki
EOF