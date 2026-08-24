---
id: governance-boundaries
type: policy
status: draft
description: The confidentiality tiers. Use when content leaves the workspace. Not for permission to act (see autonomy.md).
scope: workspace
owner: human
provenance: authored
precedence: protected
updated: 2026-08-24
---

# Boundaries — what never leaves

This policy defines categories, not literal values. Real never-share
terms exist only in ignored `.sett-private/never-share.txt`, one per
line. This file is human-owned; loosening it is class C.

## Tier 1 — never leaves the machine

Never in output, exports, commits, tool calls, logs, or external
prompts. Includes credentials and the private terms named locally.

## Tier 2 — never leaves the family

May appear in workspace-local files and in the commons; never in a
public remote, a published artefact, or anything crossing
[`../70_seams/world.md`](../70_seams/world.md).

- *(none yet — add backticked terms here)*

## Tier 3 — never leaves without attribution stripped

May be shared as content with identifying detail removed. Names,
locations, and dates that make an otherwise shareable fact
identifying.

- *(none yet — add backticked terms here)*

**Tiers 2 and 3 are human judgement, not machine enforcement.** The
gate derives from tier 1 only. Two mechanised tiers with different
consequences was a contract nothing could implement honestly; one
blocking tier that actually blocks is worth more than three that
describe an intention. If a term needs to be stopped by a tool, it is
tier 1.

## Machine gate

`tools/scrub_check.py` reads the ignored private list. `--staged`
reads Git index blobs and staged `.gitignore`, never unstaged file
content. Hits identify location and class but redact values. An
instantiated workspace fails if the private list is missing, empty,
tracked, unreadable, or contains an unusable term. The uninitialised
template may have no real terms.

## Changing the list

The list is untracked: no Git history, no tamper evidence.
`tools/journal_guard.py` blocks agent writes to `.sett-private/`.
Editing the list is class C — a human act outside the runtime.

## What the gate cannot catch

Paraphrase, inference, and identifying combinations. The gate is a
floor; class C still governs ambiguous disclosure.
