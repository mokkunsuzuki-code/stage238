# Stage234: Real-Key Signing Layer (Ed25519 / GPG)

Stage234 adds real signing keys on top of the existing Stage233 verification structure.

## What changes in Stage234

This stage does not replace the existing verification pipeline.

It adds a real-world signing layer so that published artifacts can be verified
with persistent keys.

## Why this matters

- Tamper resistance becomes practical, not just conceptual.
- GitHub publication becomes meaningful because published manifests and signatures can be verified independently.
- Researcher review becomes stronger because verification no longer depends only on unsigned local files.

## Security note

Do not commit private keys.
Only public keys and signatures should be published.
