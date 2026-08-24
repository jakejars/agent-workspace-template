---
id: placeholders
type: register
status: draft
description: Instantiation token registry. Use when filling or adding a token. Not for the setup sequence (see ONBOARDING.md).
scope: workspace
owner: human
tokens: true
updated: 2026-08-24
related:
  - type: composes_with
    ref: workspace/00_meta/ONBOARDING.md
---

# Placeholder registry

`<<TOKEN>>`: filled once from onboarding; this family-wide table is canonical.
`{{marker}}`: filled per artifact by its writer; never registered or
instantiated. Token consumers set `tokens: true`; substitution touches only
those files, and the validator rejects unflagged use.

## The tokens

| Token | Fills | Supplied by | Example | Appears in |
|---|---|---|---|---|
| `<<PRINCIPAL_NAME>>` | The human this sett serves — the name used in prose and in handovers | Interview | `Jane Okoro` | `10_identity/`, `shared-context/**`, `_templates/preference.md` |
| `<<PRINCIPAL_LEGAL_NAME>>` | Optional never-share match value; omit if withheld or identical to the public working name | Interview | `Jane Adaeze Okoro` | ignored `.sett-private/never-share.txt` only |
| `<<PRINCIPAL_EMAIL>>` | The principal's identifying address — attribution and filtering only, never a send target | Interview | `jane@example.com` | `10_identity/principal.md` |
| `<<ORG_NAME>>` | The organisation whose work this sett does; `—` if purely personal | Interview | `Example Ltd` | `10_identity/organisation.md` |
| `<<CLIENT_CODENAME>>` | Optional never-share match value for client work; omit when unused | Interview | `bluebird` | ignored `.sett-private/never-share.txt` only |
| `<<MACHINE_FILE>>` | Absolute path to this machine's truth file (hardware, toolchain, installed apps) — referenced, never copied. Must resolve **outside the sett root**, or the gates treat it as contract-bound content | Interview, verified to exist | `/Users/jane/MAC.md` | `10_identity/machines.md`, `10_identity/INDEX.md` |
| `<<WORKSPACE_ID>>` | The kebab-case name this workspace is known by in the commons roster and changelog | Interview | `okoro-consulting` | `shared-context/roster.md`, `shared-context/CHANGES.md` |
| `<<WORKSPACE_PATH>>` | Absolute path to this workspace, as the commons records it | Interview, verified to exist | `/Users/jane/sett/workspace` | `shared-context/roster.md` |
| `<<SHARED_CONTEXT_PATH>>` | Absolute path to the commons this workspace refreshes from; empty = unlinked | Interview | `/Users/jane/shared-context` | `70_seams/shared-context.md`, `shared-context/SHARED.md`, `shared-context/roster.md` |
| `<<REGISTRY_PATH>>` | Absolute path to the capability toolshed; empty = no registry linked | Interview | `/Users/jane/registry` | `70_seams/registry.md` |
| `<<LIBRARY_PATH>>` | Absolute path to a linked external knowledge library; empty = no library linked | Interview, default empty | `/Users/jane/library` | `70_seams/library.md` |
| `<<OBJECTION_WINDOW_HOURS>>` | Hours a commons edit or a promotion stands before it binds | Interview, default `48` | `48` | `70_seams/shared-context.md`, `shared-context/SHARED.md`, `shared-context/CHANGES.md`, `shared-context/_meta/governance.md` |

<!-- ledger: append above this line -->

Generic `<<TOKEN>>` is never filled or flagged. Add rows above the marker before
use. Corrections append another row for the same token; newest wins.

Registered tokens also appear as literals in `tools/` test fixtures, where they
are the defect a negative test plants. Substituting them there leaves the suite
green while it no longer tests anything. `tools/` is never a consumer.

## Fill mechanism

1. Ask/read back each row in order; write confirmed non-secret answers once to
   `00_meta/values.json` as `{"TOKEN":"value"}`.
2. From the sett root, grep, replace, and re-grep one exact token at a time —
   **only in files declaring `tokens: true`**. Nothing else is a consumer.
   This file is the one exception: it declares the flag because it displays
   every token, and filling it would delete the registry it is.
3. Verify no `<<` survives in a consumer; `build_catalog.py` enforces the same
   registration/flag contract.

Absolute paths preserve extraction. Empty shared-context, registry, or library
paths close that seam at `status: stub`.
