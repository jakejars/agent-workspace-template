---
id: consumers
type: doctrine
status: draft
description: Consumer contract. Use when building a non-agent reader or shim. Not for seam mechanics (see doctrine/seams.md).
owner: human
updated: 2026-08-24
related:
  - type: composes_with
    ref: doctrine/installation.md
  - type: depends_on
    ref: doctrine/seams.md
---

# Consumers — the contract for everything that is not the agent

Files are the API. Every trusted non-agent reader obeys:

1. **Read as data.** Generate `CATALOG.json` only for flat queries; never execute
   content. Caches are disposable views keyed by source state, never sole truth.
2. **Write through drop zones.** Journal-shaped entries, library `inbox/`, or
   commons `calibration/INBOX.md`; always proposed, never promotion or direct
   human-owned edits.
3. **Cross through a seam.** Name the consumer in `70_seams/`; apply scrub to
   every outbound copy.

Cache policy: `always` only if the entrance lists it, `cue` prefetchable,
`drill` only after an explicit relevant link.

## The context shim

A local context shim may route descriptions, prefetch cue files, shape captures,
or propose filing. It discovers roots via [`installation.md`](installation.md),
uses generated query catalogs, and ships as a registry capability. It never
promotes, and every caller can bypass it to read source cold.

## Installed is not allowed

| Switch | Level | Meaning |
|---|---|---|
| Root listed in `~/.sett/roots` | Machine | This sett is discoverable at all |
| `70_seams/<consumer>.md` open (`draft`+) | Workspace | This consumer may read this workspace |

Both default closed and remain independently reversible.

## The catalog is the index

Files are bounded semantic chunks with ids, status, edges, and routing
descriptions. Doors form the hierarchy; generated `CATALOG.json` is the flat
view. Derived indexes key on `(id, mtime)` and remain disposable.

## What a consumer never does

Never hold the sole copy, write outside drop zones, serve stale views as current,
execute content, bypass egress scrub, or treat discovery as permission.
