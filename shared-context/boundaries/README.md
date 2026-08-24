---
id: commons-boundaries-index
type: policy
status: draft
description: Shared confidentiality categories. Use when classifying commons material. Not for workspace-local literal terms (see never-share.md).
scope: shared
precedence: protected
owner: human
provenance: authored
updated: 2026-08-24
tokens: true
---

# Boundaries

This chamber states categories. It never stores literal private terms.

## The tiers

| Tier | Meaning | Enforcement |
|---|---|---|
| **never-share** | Leaves this machine under no approval. | Workspace-local private list plus human judgement |
| **sensitive** | May leave only inside an explicit, recorded approval naming this content. | Agent surfaces and asks; the approval is the record |
| **public** | Free to appear anywhere. | None |

Anything unclassified is **sensitive** until a human says otherwise.
Silence is not permission.

## Where the gate reads

Only the linked workspace's ignored
`.sett-private/never-share.txt`. Values are neither copied here nor
tracked anywhere.

## What files live here

| File | Holds |
|---|---|
| [`never-share.md`](never-share.md) | Never-share categories; no literal values |
| `sensitive.md` | Categories that need an approval, described — not enumerated as literals |
| `disclosure.md` | What may be said about the principal's work in public, and by whom |

`sensitive.md` and `disclosure.md` are created when there is something
true to put in them, and listed in the table in the same edit.

## Who may change this

<<PRINCIPAL_NAME>> only. No agent proposes an edit to this chamber and
no objection window applies — a boundary is not a majority decision. A
workspace that believes a term is missing or wrong files a candidate
in [`../calibration/README.md`](../calibration/README.md) and keeps
enforcing the current text meanwhile.

## Failure mode

An instantiated workspace with a missing, empty, tracked, or unreadable
private list blocks distribution. The fresh template is the only
zero-term state.
