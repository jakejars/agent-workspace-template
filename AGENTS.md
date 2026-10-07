---
id: repo-entrance
type: doctrine
status: draft
description: Family-maintenance entrance. Use when changing this template repository. Not for instance work (see workspace/AGENTS.md).
owner: human
updated: 2026-10-07
related:
  - type: canonical
    ref: doctrine/INDEX.md
  - type: contrast_with
    ref: workspace/AGENTS.md
---

# Maintaining Agent Workspace Template

This is the template family: the template/source repository, not an
instantiated workspace. Do not onboard it as an instance, and do not run the
workspace boot, onboarding, journal, or handover sequence here. To create a
user workspace, run `python3 tools/new.py` with a destination outside this
checkout.

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
