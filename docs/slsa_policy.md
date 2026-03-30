# Stage238 SLSA Policy

## Purpose

This repository moves from single-workflow attestation to a reusable-workflow policy model.

The goal is to reduce build drift and make provenance generation policy-bound rather than ad hoc.

## Policy Rules

1. All official build provenance must be generated through the reusable workflow:
   - `.github/workflows/reusable-slsa-build.yml`

2. Caller workflows must not reimplement build-provenance logic independently.

3. The reusable workflow is the policy boundary for:
   - artifact build
   - SBOM generation
   - artifact upload
   - provenance attestation
   - SBOM attestation

4. Required GitHub Actions permissions:
   - `contents: read`
   - `id-token: write`
   - `attestations: write`

5. Expected outputs:
   - source bundle artifact
   - SHA256 digest file
   - SPDX SBOM
   - GitHub build provenance attestation
   - GitHub SBOM attestation

## Security Meaning

This does not prove all SLSA requirements by itself.
It improves governance by forcing builds through a reusable, centralized workflow.

## Verification View

Reviewers should verify:

- the caller workflow only invokes the reusable workflow
- the reusable workflow performs the build
- attestation steps are centralized
- artifacts and SBOM are produced consistently
