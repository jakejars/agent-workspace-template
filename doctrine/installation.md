---
id: installation
type: doctrine
status: draft
description: Workspace installation and discovery. Use when installing or locating a workspace. Not for instance setup (see workspace/00_meta/ONBOARDING.md).
owner: human
updated: 2026-10-07
related:
  - type: composes_with
    ref: doctrine/migrations.md
  - type: see_also
    ref: doctrine/seams.md
---

# Installation — location, discovery, import

The root is the nearest ancestor containing `NAMESPACE.md`; conventions below
aid discovery without constraining location.

## Where workspaces live

- Suggested workspace path: `~/workspaces/my-workspace/`.
- One commons per principal, linked by absolute path.
- A project-specific workspace may live at the project root.

Other locations are valid.

## Unsupported locations

A workspace root is the nearest ancestor containing `NAMESPACE.md`. Therefore:

- do not nest one workspace root inside another;
- do not create an instance inside the Agent Workspace Template source checkout;
- a directory that merely contains several sibling workspaces is not itself a workspace;
- sibling workspaces under a normal container such as `~/workspaces/` are valid;
- project-specific workspaces may live at a project root when that root is itself
  the workspace.

## Discovery

1. Inside a tree, walk upward to `NAMESPACE.md`.
2. Otherwise, optionally read `~/.workspace/roots`: one absolute root per line;
   `#` comments; stale entries skipped. Listing is explicit local disclosure.

No daemon, service, environment variable, or lockfile. Consumers validate
source, generate catalogs on demand, read data without execution, and write only
through seams.

## Import — data that predates the workspace

Try in order:

1. Leave source behind a named seam and cite it through references.
2. Capture only live material through library inbox, journal, or the correct
   chamber.
3. Convert file-by-file as linked `draft` + `imported`; preserve bodies and split
   oversized sources behind a door.

Import never promotes. Record the import as a run and journal its source/scope.
Never import secrets or third-party material without rights. Registry artifacts
still require manifest/checksum; library specimens still require rights.

## What this file refuses

Core includes no sync engine, watcher, source-specific connector, or background
indexer. Use a seam and the import ladder.
