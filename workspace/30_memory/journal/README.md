---
id: memory-journal
type: doctrine
status: draft
description: Append-only event journal. Use when recording or correcting an event. Not for promoted knowledge (see workspace/30_memory/facts/README.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/30_memory/INDEX.md
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
---

# journal/ — the append-only record

One file per event. Nothing else in the sett is truth; every other
memory file is a projection that can be rebuilt from these entries.

## Naming

```text
30_memory/journal/YYYY-MM-DD-HHMM-slug.md
```

<!-- lists: *.md -->

Local time, 24-hour, zero-padded. Slug is kebab-case, ≤5 words, names
the event, not the feeling: `2026-08-24-1412-registry-install-failed`.
Collisions take the next minute — never overwrite a filename.

## Entry header

Journal entries are exempt from the OKF contract
(`doctrine/frontmatter-spec.md`, exemptions). They carry this minimal
header and nothing more:

```yaml
---
date: 2026-08-24T14:12         # ISO, local, minute resolution
kind: event | correction | digest
refs: [<id-or-path>, ...]      # optional; what this entry is about
---
```

- **date** — when the event happened, not when it was written.
- **kind** — `event` for something that occurred; `correction` for a
  retraction or override of an earlier entry (which stays); `digest`
  for the one terse entry a session appends at close.
- **refs** — ids, or repo- or workspace-relative paths: the intent, run,
  decision, approval, or earlier journal entry this concerns. Every path
  must resolve. `correction` entries must ref the entry they correct.

Exemption is from OKF, not from shape: `build_catalog.py` checks the
name, the three keys and nothing more, the `kind`, and every ref.

Below the header the body is free prose. Terse and factual: what
happened, what was observed, what it means. No template, no headings
required.

## The immutability law

Existing entries are never edited, moved, renamed, or deleted. This is
constitutional (`workspace/AGENTS.md`, law 2), not a style rule.

- **Wrong entry?** Write a `correction` entry that refs it. Both stand;
  the later one wins.
- **Guard** — `tools/journal_guard.py` blocks any edit, overwrite,
  move, or delete of an existing entry at tool-use time (exit 2).
  A git pre-commit hook is the runtime-independent backstop. Tool-time
  blocking needs the `PreToolUse` hook wired (`00_meta/ONBOARDING.md`
  step 6); unwired, the first refusal arrives at commit.
- Do not fight the guard. A guard failure means the edit was wrong,
  not that the guard was.

Git history is the tamper-evidence; the guard is the prevention.

## When to write one

Every durable event, as it happens — not batched at session end:
a decision made, an approval used, an external effect, a surprise, a
failure, a capability installed, an intent satisfied. Capture is
ceremony-free: sixty seconds, one file, no permission needed
(Class A). Promotion out of the journal is the deliberate part.

Entries are never pruned. Aggressive expiry elsewhere in the chamber
is safe precisely because the journal is permanent.
