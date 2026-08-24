---
id: seam-registry
type: seam
status: draft
description: Registry seam. Use when installing or updating a capability. Not for the local lockfile (see workspace/60_capabilities/installed.md).
scope: workspace
owner: human
tokens: true
updated: 2026-08-24
related:
  - type: composes_with
    ref: workspace/60_capabilities/installed.md
---

# Seam: registry (the toolshed)

Linked toolshed: `<<REGISTRY_PATH>>`. Empty closes external install/pack.
Transport is filesystem-only.

## What crosses

- In: manifest (name, integer version, targets, sha256) plus named payload.
- Out: locally authored or improved capability with version bump, checksums,
  and ledger row.

## Direction

Both; one capability per human-initiated act, never bulk/automatic.

## Inspect point

- Local lockfile: version, checksum, trust, date.
- Toolshed ledger: publication, workspace, date.
- Recorded-vs-disk checksum drift check.

## Control point

- Verify checksums before writes; mismatch stops.
- Allow only workspace-relative targets; reject absolute, traversal, tilde, and
  symlinked ancestors.
- Refuse differing-file overwrite; default keeps local.
- Install/pack are class B.
- Installation yields `untrusted`; trust needs a later approved lockfile row and
  resets on update unless approval covers future versions.

## What never crosses

- Secrets, credentials, tokens, `.env`, principal data, journals, memory, runs,
  or never-share content.
- Any file lacking verified checksum.
