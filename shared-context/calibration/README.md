---
id: commons-calibration-index
type: register
status: draft
description: Calibration inbox. Use when a workspace finds a shared-rule exception. Not for promoted facts (see shared-context/identity/README.md).
scope: shared
owner: shared
updated: 2026-08-24
tokens: true
related:
  - type: canonical
    ref: shared-context/_meta/governance.md
---

# Calibration

The sole agent-write inbox for observations about <<PRINCIPAL_NAME>>. Candidates
never bind; file contradictions here while continuing to follow current commons.

## Candidate format

One `YYYY-MM-DD-<slug>.md`, `register` + `agent_proposed`, listed newest-first in
[`INBOX.md`](INBOX.md).

```yaml
observed:   what happened, in one line, factual
evidence:   where it is recorded — journal entry id, run id, date
target:     the file this would change (identity/… or operating-rules/…)
proposal:   the exact edit, quoted, not a description of an edit
confidence: low | medium | high — and what would raise it
filed_by:   <workspace-id> from roster.md
```

Both `evidence` and exact `proposal` are required.

## Lifecycle

```text
filed ──► triaged ──► promoted   the edit lands under the objection
  │          │                   window; candidate closes naming the
  │          │                   CHANGES.md trailer that carried it
  │          ├──────► rejected   with one line of why — the why is the
  │          │                   point, it stops the refile
  │          └──────► parked     true but not actionable; carries a
  │                              review date
  └── superseded by a later candidate on the same target
```

Only humans move `filed`; agents never promote, flip provenance, or edit another
candidate. Corrections supersede.

## Filing rules

1. File only a contradiction with identity or operating rules.
2. Check [`INBOX.md`](INBOX.md); duplicate instances supersede as new evidence.
3. Cite rather than copy secrets, boundary terms, or raw source.
4. Filing grants no authority; current commons governs until binding.

## Why this chamber exists

This inbox shares observations without unilateral commons edits.
