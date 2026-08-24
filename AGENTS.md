---
id: repo-entrance
type: doctrine
status: draft
description: Family-maintenance entrance. Use when changing this template repository. Not for instance work (see workspace/AGENTS.md).
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: doctrine/INDEX.md
  - type: contrast_with
    ref: workspace/AGENTS.md
---

# Maintaining Sett

This is the template family, not an instantiated workspace. Do not run the
workspace boot, onboarding, journal, or handover sequence here.

## Before writing

Read in order: [`README.md`](README.md), [`LOOP.md`](LOOP.md),
[`doctrine/INDEX.md`](doctrine/INDEX.md), [`NAMESPACE.md`](NAMESPACE.md).

## Binding rules

Use the canonical rule, without restating it:

- metadata and limits: [`doctrine/frontmatter-spec.md`](doctrine/frontmatter-spec.md)
- filing and root paths: [`doctrine/filing.md`](doctrine/filing.md),
  [`doctrine/naming.md`](doctrine/naming.md)
- reachability and member boundaries: [`LOOP.md`](LOOP.md),
  [`doctrine/seams.md`](doctrine/seams.md)
- moves and supersession: [`doctrine/migrations.md`](doctrine/migrations.md)
- required checks: [`doctrine/gates.md`](doctrine/gates.md)

Every new content file must be linked by its local door in the same change.
Instantiation values use registered `<<TOKEN>>` markers, never real local
values. Protected laws and human-owned doctrine change only with human
direction; otherwise use the proposal process in `doctrine/INDEX.md`.

## Done

Run the full gates. Then verify a fresh instance starting only at
`workspace/AGENTS.md` can reach the change without prior path knowledge.
