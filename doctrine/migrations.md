---
id: migrations
type: doctrine
status: draft
description: Moving things without breaking them. Use when refiling, renaming, replacing. Not for choosing the destination chamber (see doctrine/filing.md).
updated: 2026-10-07
related:
  - type: depends_on
    ref: doctrine/naming.md
  - type: see_also
    ref: doctrine/gates.md
---

# Migrations

## Agent Workspace Template rename

When adopting the updated toolset and `.gitignore`, an existing workspace
renames `.sett-private/` to `.workspace-private/`,
`tools/sett_layout.py` to `tools/workspace_layout.py`, and
`tools/sett_setup.py` to `tools/workspace_setup.py`. Nothing else is required.
The old directory and module names continue to work through compatibility.
If both private directories exist, `.workspace-private/` wins and tools warn.

## The git-mv contract

Move with `git mv`; never delete/recreate.

```sh
git mv 30_memory/facts/build-times.md 40_knowledge/canon/build-times.md
```

1. Keep pure move and body edit in separate commits.
2. Fix inbound path links with the move.
3. Change `updated` only for content changes.
4. Name any type/chamber reclassification in the commit.

## Ids do not move

Ids survive every path change; only path links move. Changing an id creates a
new record and requires supersession.

## Supersession

Replacement frontmatter:

```yaml
id: postgres-over-sqlite-v2
supersedes: postgres-over-sqlite
status: draft
```

Retain the old body unchanged; edit only frontmatter to demote below `mature`
and add its redirect:

```yaml
related:
  - type: canonical
    ref: postgres-over-sqlite-v2
```

The validator requires the target and warns if a superseded record remains
`mature`.

## Link or extract?

Link in place by default. Extract a member only when it genuinely needs an
independent lifecycle: separate history/versioning, ownership/permissions,
release cadence, deployment, or when several workspaces depending on it makes
co-location materially awkward. Extraction is an operational decision, not a
prerequisite for ordinary use.

## Extracting a member

Members are independently extractable: no direct sibling links; cross only
through `70_seams/`. Family paths resolve from the workspace root. Optional packs
accept family-prefixed or extracted-root self-refs.

To extract:

```sh
git subtree split -P workspace/ -b extract-workspace
git init ../my-workspace && cd ../my-workspace
git pull ../agent-workspace-template extract-workspace
```

Then:

1. Workspace copies `tools/`, `.githooks/`, `.gitignore`, `doctrine/`,
   `_templates/`, `LOOP.md`, `LICENSE`, and `NAMESPACE.md` into the new root.
   Optional packs copy `tools/`, `doctrine/schema.json`, `LICENSE`, and
   `NAMESPACE.md`; they copy no workspace-only support.
2. Demote affected seams to `stub`, then re-answer paths and controls from
   evidence.
3. Run validator and loop in the extracted root; regenerate catalogs only on
   demand.
4. Replace the origin member with a seam naming its new location.

Duplicated post-extraction ids share ancestry; later divergence is a merge
problem, not an identity change.

## Existing instances adopting current-task context

Keep immutable history. The entrance now uses `boot_selector: explicit-task`
and `boot_dynamic: workspace/20_intent/active/*.md`. Add a current checkpoint
to each task actually being continued; do not move historical handovers into
boot or infer current work from their timestamps. A task record is capped at
3,000 characters; link detailed evidence instead of enlarging it.

Install the updated Git hooks, then run `tools/lifecycle.py start` and status.
Existing runtime adapters must add the neutral lifecycle events explicitly;
new scripts on disk alone do not prove they fire. No daemon is introduced.

Existing finalized instances without a ready receipt need a deliberate setup
audit; do not recreate the sentinel automatically. Preserve their identity,
private store, and journal. The new receipt records verified setup, never an
assumed successful migration. Historical handovers still require UTC
`closed_at`; if uncertain, record the best evidence and uncertainty.

## Pre-redesign exposure

Instances onboarded before the private-list redesign carry real
never-share values in Git history. Adopting the gate does not purge them.
Options: rewrite history with `git filter-repo`, or accept the exposure
and record it as a `50_registers/risks.md` entry.
