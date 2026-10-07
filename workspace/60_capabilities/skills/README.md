---
id: capabilities-skills
type: doctrine
status: draft
description: Agent Skills door. Use when packaging or exporting reusable task-cued behaviour. Not for ordinary procedures (see workspace/30_memory/procedures/README.md).
scope: workspace
owner: agent
updated: 2026-10-07
related:
  - type: canonical
    ref: workspace/60_capabilities/INDEX.md
  - type: composes_with
    ref: _templates/skill/README.md
  - type: see_also
    ref: doctrine/consumers.md
---

# skills/ — reusable behaviour in the Agent Skills format

One `<name>/SKILL.md` per skill, `type: skill`. The directory and frontmatter
`name` match; the [skill kit](_templates/skill/README.md) supplies the record.
Only `SKILL.md` sits at the skill root. Optional `scripts/`, `references/`,
and `assets/` hold material loaded when the skill calls for it.

[Pipeline](../pipelines/README.md) model stages may name a skill to reuse its behaviour.

<!-- lists: */SKILL.md -->
<!-- lists: */references/*.md -->
<!-- lists: */scripts/*.md -->
<!-- lists: */assets/*.md -->

These bounded patterns list skill records and supporting Markdown directly
inside the optional folders. Add a bounded pattern for deeper Markdown before
filing it; every supporting content file still follows house frontmatter rules.
Package documentation uses `type: capability`; other chamber records stay in
their own filing paths and may be linked as sources.

Skills are capabilities governed by the existing
[trust ladder](../INDEX.md) and [lockfile](../installed.md). New local skills
are `untrusted` + `agent_proposed`; registry installation verifies checksums
through the [registry seam](../../70_seams/registry.md) and never promotes.

Check with `python3 tools/skills.py check`. Export copies to a user-chosen
runtime directory: `python3 tools/skills.py export --to <dir>`.
Add `--trusted-only` to select skills whose newest lockfile row is `trusted`;
provenance alone never grants trust. See the
[consumer contract](doctrine/consumers.md) for output ownership and boundaries.
