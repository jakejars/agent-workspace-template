---
id: meta-index
type: doctrine
status: draft
description: Instance-metadata map. Use when a sett is fresh or a token needs work. Not for principal identity (see workspace/10_identity/INDEX.md).
scope: workspace
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/AGENTS.md
---

# 00_meta — instantiation state

This chamber answers one question: **is this sett a template or a home
yet, and what is still blank?** It holds no knowledge about the
principal, the work, or the world — only the machinery that turns a
clone into an inhabited workspace.

The entrance checks only whether `.uninitialised` exists. If present, the
session runs `ONBOARDING.md`; ordinary work starts only after deletion.

## Files

| File | What |
|---|---|
| [`ONBOARDING.md`](ONBOARDING.md) | The instantiation walk: interview, fill, link, verify, delete the sentinel |
| [`placeholders.md`](placeholders.md) | The registry of every `<<TOKEN>>` used anywhere in the family, and the fill mechanism |
| `.uninitialised` | Sentinel — named, never linked: its deletion is the point, and a link to it would dead-link every instantiated sett. Present = not yet instantiated; deleted by the last step of onboarding, never earlier |

## Rules

1. **The sentinel is the only instantiation state.** No `initialised:`
   flag scattered across files, no "looks filled to me". Present or
   absent, one bit, one place.
2. **`placeholders.md` is the single source of truth for tokens.** A
   token that is not in that table does not exist; adding a token to a
   file means adding the row first. `build_catalog.py` enforces both
   halves — the row, and the file's `tokens: true` flag.
3. **This chamber is written once and then rarely.** After onboarding
   it is a reference, not working state. Onboarding is re-runnable
   (idempotent) but is not a place to record ongoing decisions — those
   go to `50_registers/` and `30_memory/journal/`.
4. **Nothing here is `load: always`.** Boot reads the sentinel's
   presence, not its content.
