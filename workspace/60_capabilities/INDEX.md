---
id: capabilities-index
type: doctrine
status: draft
description: Capabilities chamber map. Use when adding or verifying installed tools. Not for registry access (see workspace/70_seams/registry.md).
scope: workspace
owner: agent
updated: 2026-10-07
related:
  - type: depends_on
    ref: workspace/70_seams/registry.md
---

# 60_capabilities — what this workspace can do

A **capability** is a named unit of doing: a tool, a script, a
procedure package. It arrives from the toolshed through
[`../70_seams/registry.md`](../70_seams/registry.md), lands as files
in this workspace, and is recorded in the lockfile.

| File | Holds |
|---|---|
| [installed.md](installed.md) | The install lockfile: capability, version, sha256, date, trust state |
| [pipelines/README.md](pipelines/README.md) | Reusable staged processes and their small contracts |

## Three rules

1. **Capability is not implementation.** A capability is named by what
   it does, independent of what fulfils it. Two providers of the same
   capability compete under the same name; the lockfile records which
   one is installed.
2. **Installation is never promotion.** A freshly installed capability
   is `untrusted`: present, runnable when explicitly invoked, never
   load-bearing, never invoked automatically, never used in a class-A
   action. Trust is granted by a human, recorded as a new lockfile
   row, and can be withdrawn the same way.
3. **Checksums or it did not happen.** Every install verifies the
   file's sha256 against the source manifest before writing. A
   mismatch is a stop, not a warning — an unverified copy is never
   recorded as installed.

## Trust ladder

| State | Meaning |
|---|---|
| `untrusted` | Installed and verified. Runs only on explicit instruction. Default for everything new. |
| `probationary` | Human-approved for a named use, bounded by scope and expiry from the approval record. |
| `trusted` | Human-approved for general use inside its declared effects. Still never authorises a class-B or C action on its own. |
| `withdrawn` | Trust revoked or the capability removed. The row stays; the files may not. |

Promotion up this ladder is class B: the agent proposes with evidence
(what it was used for, what it touched, what it produced), the human
disposes, the approval record is referenced from the lockfile row.

## Local capabilities

A capability authored here, not pulled from the toolshed, is recorded
the same way with source `local`. When it is worth sharing, it is
packed back through the registry seam — version bumped, checksums
refreshed, ledger line appended. Nothing leaves the workspace by
copy-paste.
