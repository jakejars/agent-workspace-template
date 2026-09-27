---
id: machines
type: identity
status: draft
description: Machine identities and roles. Use when work depends on which machine is in use. Not for live machine truth (see workspace/70_seams/machine.md).
scope: workspace
owner: human
tokens: true
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/10_identity/INDEX.md
---

# Machines

This file is a **pointer table, not an inventory**. Hardware,
toolchain, installed apps and per-machine TODOs live in the machine's
own truth file and are read from there at the moment they are needed.
Copying a spec into this sett creates a second truth that starts
drifting the day the machine changes.

| Machine | Role | Truth file | Notes |
|---|---|---|---|
| *primary* | Where this sett lives and sessions run | `<<MACHINE_FILE>>` | — |
| *(add rows as machines join)* | | | |

<!-- ledger: append above this line -->

## Rules

1. **Reference, never duplicate.** No CPU, RAM, disk, OS version,
   installed-tool list, or version number is written in this sett. If
   you need one, read `<<MACHINE_FILE>>` through
   `70_seams/machine.md`.
2. **Absolute paths only.** A machine truth file is reached by absolute
   path; it is outside the sett and outside every member.
3. **Paths are machine-scoped.** Any absolute path recorded anywhere in
   this sett — commons, toolshed, project directories — is true on
   exactly one machine unless a row here says otherwise. A path that
   resolves on the wrong machine is the failure mode this table exists
   to make visible.
4. **Optional reference.** An empty machine path means unconfigured. Inspect
   current machine facts with authorized read-only tools when needed; record
   provisional evidence and scope rather than inventing a machine profile.
   If a configured path is missing, report the stale pointer and continue
   work that does not depend on it.
5. **Multi-machine is not sync.** This sett has no cross-device
   protocol. Two machines running the same sett is two setts unless a
   human keeps them together deliberately.
