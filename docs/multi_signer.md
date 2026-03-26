# Stage231: Multi-Signer

## Objective

This stage introduces distributed trust through multiple independent signatures.

Instead of relying on a single signer, the same checkpoint or proof payload can be signed by:

- Owner signer
- Third-party signer
- Researcher signer

This improves trust distribution and reduces dependence on one authority.

## Trust Model

Single signer:
- One key signs the evidence.
- Verification depends on one trust anchor.

Multi-signer:
- Multiple independent signers sign the same payload.
- Verification can require one, two, or all signatures.
- This creates distributed trust.

## What is Signed

The signed object is a canonical JSON payload, typically representing:

- log_id
- tree_size
- merkle_root
- generated_at_utc

## Outputs

Stage231 produces:

- `out/multi_signer/payload.json`
- `out/multi_signer/signed_bundle.json`
- verification result in terminal output

## Security Value

This stage does **not** create a new cryptographic primitive.

It adds:

- trust distribution
- signer separation
- stronger auditability
- clearer external review structure

## Example Roles

- owner: repository/project maintainer
- third_party: external auditor or operator
- researcher: academic or independent reviewer

## Verification Meaning

A verifier can check:

1. the payload hash
2. each signature independently
3. which signer signed
4. how many valid signatures exist

This enables policy choices such as:

- require at least 1 valid signature
- require at least 2 valid signatures
- require all signatures

## Conclusion

Stage231 upgrades:

single proof authenticity
→
multi-party attested authenticity

This is a trust-distribution step.
