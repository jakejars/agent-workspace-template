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

Upgrade tools and `doctrine/schema.json` together: the old schema lacks `limits.stage_chars` and the skill/pipeline
fields. From an updated template checkout, set `TEMPLATE` to its absolute path and `INSTANCE` to the existing workspace
root containing `NAMESPACE.md`, then run this block:

```sh
(
    set -e
    python3 -B - "$TEMPLATE" "$INSTANCE" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "tools"))
from build_catalog import parse_frontmatter
from workspace_layout import WorkspaceLayout
instance = Path(sys.argv[2])
layout = WorkspaceLayout(instance)
for name, identifier in (("skills", "capabilities-skills"), ("pipelines", "pipelines-index")):
    shelf = layout.workspace_path("workspace/60_capabilities/" + name)
    if not shelf.exists() and not shelf.is_symlink():
        continue
    door = shelf / "README.md"
    try:
        fm = (parse_frontmatter(door.read_text(encoding="utf-8")) or {}) if door.is_file() else {}
    except (OSError, UnicodeError):
        fm = {}
    if shelf.is_symlink() or not shelf.is_dir() or door.is_symlink() or fm.get("id") != identifier or fm.get("type") != "doctrine":
        sys.exit(f"Upgrade stopped: {shelf}: rename the legacy capability and update links before retrying.")
ignore = instance / ".gitignore"
data = ignore.read_bytes()
if data and not data.endswith(b"\n"):
    ignore.write_bytes(data + b"\n")
PY
    cp -R "$TEMPLATE/tools/." "$INSTANCE/tools/"
    grep -vxF -f "$INSTANCE/.gitignore" "$TEMPLATE/.gitignore" >> "$INSTANCE/.gitignore" || true
    cp "$TEMPLATE/doctrine/schema.json" "$INSTANCE/doctrine/schema.json"
    cd "$INSTANCE"
    python3 tools/build_catalog.py --check
    python3 tools/skills.py check
    python3 tools/pipeline.py check
    python3 tools/check_loop.py
    python3 tools/context.py refresh
)
```

Conflicting `60_capabilities/skills` or `pipelines` stop the upgrade before any writes. First `git mv` the old
capability to a free name such as `legacy-skills` or `legacy-pipelines`, preserving its README and scripts. Update
inbound path links and script/manifest path references; keep its id and lockfile history, then retry.

Merge local tool, ignore, or schema customizations before replacing support files. Preserve instance content, readiness
receipts, and immutable journals; no refill or onboarding.

`SETT_ROOT` remains a fallback after `WORKSPACE_ROOT`. `.sett-private/` can
stay or be renamed; if both stores exist, tools warn and enforce their terms' union. A no-private-terms confirmation in
one never suppresses the other. To consolidate, the human preserves all terms in `.workspace-private/never-share.txt`,
then explicitly retires `.sett-private/`. Updated tools retain legacy compatibility imports. Both cache directories
remain disposable.

`tools/test_upgrade.py` builds a finalized last-Sett-release instance and executes this block, exercising gates, scrub,
write protection, context, and feature checks.

## The git-mv contract

Move with `git mv`; never delete/recreate. Example: `git mv 30_memory/facts/build-times.md 40_knowledge/canon/build-times.md`.

1. Keep pure move and body edit in separate commits.
2. Fix inbound path links with the move.
3. Change `updated` only for content changes.
4. Name any type/chamber reclassification in the commit.

## Ids do not move

Ids survive every path change; only path links move. Changing an id creates a new record and requires supersession.

## Supersession

Replacement frontmatter declares `id: postgres-over-sqlite-v2`, `supersedes: postgres-over-sqlite`, and `status: draft`.

Retain the old body unchanged; edit only frontmatter to demote below `mature` and add its redirect:

```yaml
related:
  - type: canonical
    ref: postgres-over-sqlite-v2
```

The validator requires the target and warns if a superseded record remains `mature`.

## Link or extract?

Link in place by default. Extract a member only when it genuinely needs an independent lifecycle: separate
history/versioning, ownership/permissions, release cadence, deployment, or when several workspaces depending on it makes
co-location materially awkward. Extraction is an operational decision, not a prerequisite for ordinary use.

## Extracting a member

Members are independently extractable: no direct sibling links; cross only through `70_seams/`. Family paths resolve
from the workspace root. Optional packs accept family-prefixed or extracted-root self-refs. To extract:

```sh
git subtree split -P workspace/ -b extract-workspace
git init ../my-workspace && cd ../my-workspace
git pull ../agent-workspace-template extract-workspace
```

1. Workspace copies `tools/`, `.githooks/`, `.gitignore`, `doctrine/`, `_templates/`, `LOOP.md`, `LICENSE`,
   and `NAMESPACE.md` into the new root. Optional packs copy `tools/`, `doctrine/schema.json`, `LICENSE`,
   and `NAMESPACE.md`; they copy no workspace-only support.
2. Demote affected seams to `stub`, then re-answer paths and controls from evidence.
3. Run validator and loop in the extracted root; regenerate catalogs only on demand.
4. Replace the origin member with a seam naming its new location.

Duplicated post-extraction ids share ancestry; later divergence is a merge problem, not an identity change.

## Existing instances adopting current-task context

Keep immutable history. The entrance now uses `boot_selector: explicit-task` and `boot_dynamic:
workspace/20_intent/active/*.md`. Add a current checkpoint to each task actually being continued; do not move historical
handovers into boot or infer current work from their timestamps. A task record is capped at 3,000 characters; link
detailed evidence instead of enlarging it.

Install the updated Git hooks, then run `tools/lifecycle.py start` and status. Existing runtime adapters must add the
neutral lifecycle events explicitly; new scripts on disk alone do not prove they fire. No daemon is introduced.

Existing finalized instances without a ready receipt need a deliberate setup audit; do not recreate the sentinel
automatically. Preserve their identity, private store, and journal. The new receipt records verified setup, never an
assumed successful migration. Historical handovers still require UTC `closed_at`; if uncertain, record the best evidence
and uncertainty.

## Pre-redesign exposure

Instances onboarded before the private-list redesign carry real never-share values in Git history. Adopting the gate does not purge them.
Options: rewrite history with `git filter-repo`, or accept the exposure and record it as a `50_registers/risks.md` entry.
