---
id: consumers
type: doctrine
status: draft
description: Consumer contract. Use when building a non-agent reader or shim. Not for seam mechanics (see doctrine/seams.md).
owner: human
runtime_subject: true
updated: 2026-10-07
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
| Root listed in `~/.workspace/roots` | Machine | This workspace is discoverable at all |
| `70_seams/<consumer>.md` open (`draft`+) | Workspace | This consumer may read this workspace |

Both default closed and remain independently reversible.

## The catalog is the index

Files are bounded semantic chunks with ids, status, edges, and routing
descriptions. Doors form the hierarchy; generated `CATALOG.json` is the flat
view. Derived indexes key on `(id, mtime)` and remain disposable.

## What a consumer never does

Never hold the sole copy, write outside drop zones, serve stale views as current,
execute content, bypass egress scrub, or treat discovery as permission.

## Optional skills export

Neutral skills live behind the
[skills door](workspace/60_capabilities/skills/README.md). A human chooses the
runtime output directory; for example, Claude Code uses `.claude/skills`,
while Codex can use `.agents/skills`:

```sh
python3 tools/skills.py check
python3 tools/skills.py export --to .claude/skills --trusted-only
python3 tools/skills.py export --to .agents/skills --trusted-only
```

Export copies files, never symlinks, and prints copied and skipped skills.
The selected payload passes the existing egress scrub before any write;
distribution remains text-only, including supporting files.
It never writes into workspace source chambers or edits runtime or account
settings. Each created skill directory carries an ownership marker; export
refuses to overwrite an existing directory without its own valid marker.
User files elsewhere in the destination remain untouched.
Re-export replaces owned copies. With `--trusted-only`, it also removes
previously owned copies from this source that no longer qualify, so withdrawn
skills do not remain discoverable in that output directory.

`--trusted-only` selects `trusted` skills using each capability's newest
[lockfile](workspace/60_capabilities/installed.md) row; it does not infer trust
from provenance and requires the referenced class-B promotion approval.
This filter reads trust state; the registry install contract and existing
lockfile drift audit still govern checksum verification. Without the filter,
export also copies untrusted skills for explicit
use. Export is neither promotion nor permission to invoke automatically;
the existing capability trust ladder and effect approvals still apply.
