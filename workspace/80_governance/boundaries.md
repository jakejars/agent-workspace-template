---
id: governance-boundaries
type: policy
status: draft
description: The confidentiality tiers. Use when content leaves the workspace. Not for permission to act (see autonomy.md).
scope: workspace
owner: human
provenance: authored
precedence: protected
updated: 2026-10-07
---

# Boundaries — what never leaves

This policy defines categories, not literal values. Real never-share
terms exist only in ignored `.workspace-private/never-share.txt`, one per
line, or the legacy `.sett-private/never-share.txt`. This file is human-owned;
loosening it is class C.

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

`tools/scrub_check.py` reads the ignored private lists. When both stores exist,
it warns and enforces the union of their terms. `--staged`
reads Git index blobs and staged `.gitignore`, never unstaged file
content. Hits identify location and class but redact values. An
instantiated workspace fails if any present private list is empty,
tracked, unreadable, or contains an unusable term. The uninitialised
template may have no real terms.

## Changing the list

The list is untracked: no Git history, no tamper evidence.
`tools/journal_guard.py` blocks agent writes to `.workspace-private/`.
Editing the list is class C — a human act outside the runtime.
To consolidate two stores, preserve their combined terms in
`.workspace-private/never-share.txt`, then have the human explicitly retire
`.sett-private/`.

## What the gate cannot catch

Paraphrase, inference, and identifying combinations. The gate is a
floor; class C still governs ambiguous disclosure.

Derived `.workspace-cache/` and ignored working artifacts are not a distribution
channel. Context routing scrubs source before producing suggestions. Artifacts
require separate review before export; never assume ignore rules permit egress.

If the human explicitly has no literal terms to configure, they may write
`{"version":1,"confirmed":true}` to ignored `.workspace-private/no-private-terms.json`
and omit the list. Missing configuration is never interpreted as this choice.
This disables literal matching only; confidentiality and authorization rules
still apply. Within each store, a present list takes precedence, and an invalid
list still fails.
A confirmation in one store never suppresses terms in the other.
