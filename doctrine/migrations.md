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

Upgrade tools and `doctrine/schema.json` together: the old schema lacks
`limits.stage_chars` and the skill/pipeline fields. From an updated template
checkout, set `TEMPLATE` to its absolute path and `INSTANCE` to the existing
workspace root containing `NAMESPACE.md`, then run this block:

```sh
(
    set -e
    cp -R "$TEMPLATE/tools/." "$INSTANCE/tools/"
    cp "$TEMPLATE/.gitignore" "$INSTANCE/.gitignore"
    cp "$TEMPLATE/doctrine/schema.json" "$INSTANCE/doctrine/schema.json"
    cd "$INSTANCE"
    python3 tools/build_catalog.py --check
    python3 tools/skills.py check
    python3 tools/pipeline.py check
    python3 tools/check_loop.py
    python3 tools/context.py refresh
)
```

Merge local tool, ignore, or schema customizations before replacing support files.
Preserve instance content, readiness receipts, and immutable journals; no refill
or onboarding is required. Keep `.sett-private/` in place: tools enforce its terms,
and `SETT_ROOT` remains a fallback after `WORKSPACE_ROOT`. Renaming it to
`.workspace-private/` is optional; if both exist, the new directory wins and tools warn.
Updated tools include `workspace_layout.py`, `workspace_setup.py`, and their legacy
compatibility imports. Both `.sett-cache/` and `.workspace-cache/` remain disposable.

`tools/test_upgrade.py` builds a finalized last-Sett-release instance and executes this block,
exercising gates, scrub, write protection, context, and feature checks.

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
