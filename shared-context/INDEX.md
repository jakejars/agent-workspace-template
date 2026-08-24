---
id: commons-index
type: doctrine
status: draft
description: The commons map. Use when looking for something in the commons or deciding which chamber. Not for the laws that govern reading the store (see shared-context/SHARED.md).
scope: shared
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: shared-context/SHARED.md
---

# The commons — what is where

The entrance is [`SHARED.md`](SHARED.md); it carries the two laws and refresh
boundary. This file is the map.

## Chambers

| Chamber | Holds | Owner |
|---|---|---|
| [`identity/`](identity/README.md) | Who the principal is: standing, low-churn facts | human |
| [`operating-rules/`](operating-rules/README.md) | How work is to be done, across all workspaces | human |
| [`boundaries/`](boundaries/README.md) | The confidentiality tiers, and the never-share list every workspace copies into its own governance chamber | human |
| [`calibration/`](calibration/README.md) | Correction candidates: what workspaces observed, awaiting disposal | shared |

## Files

| File | What |
|---|---|
| [`SHARED.md`](SHARED.md) | The entrance: source laws and refresh boundary |
| [`roster.md`](roster.md) | Which workspaces are linked, and the five-clause link-in contract |
| [`CHANGES.md`](CHANGES.md) | Append-only trailer per edit, with its objection-window state |
| [`_meta/governance.md`](_meta/governance.md) | Objection window, sign-off, override — how an edit binds |

<!-- lists: _meta/*.md -->

## Choosing a chamber

```text
a durable fact about the person or the org ──► identity/
how the principal wants work done ──────────► operating-rules/
what must never leave ──────────────────────► boundaries/
a workspace's observation, not yet disposed ► calibration/
anything true of one workspace only ────────► not the commons at all
```

A file that fits none of these does not belong here. The commons holds
the principal, not the work.

## Adding a file

Adding, removing, moving, or renaming any file in this store is a
structural change: a `CHANGES.md` trailer, the objection window, and
sign-off from **every** workspace on `roster.md`. The chamber README
that will hold the file lists it in the same edit — an unlisted file
is unreachable, and unreachable content in a governed store is content
nobody agreed to.
