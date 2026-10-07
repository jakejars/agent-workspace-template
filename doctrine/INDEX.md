---
id: doctrine-index
type: doctrine
status: draft
description: Doctrine map. Use when locating the rule behind a convention. Not for system flows (see LOOP.md).
updated: 2026-10-07
related:
  - type: see_also
    ref: LOOP.md
---

# Doctrine

Shared mechanics. [`schema.json`](schema.json) is executable; prose owns only
semantics. Members address doctrine from the workspace root and copy the required
subset when extracted ([migrations](migrations.md)).

| File | Owns the question |
|---|---|
| [`schema.json`](schema.json) | fields, vocabularies, defaults, filing, limits |
| [`frontmatter-spec.md`](frontmatter-spec.md) | metadata semantics and edge fields |
| [`filing.md`](filing.md) | deterministic placement and ambiguities |
| [`naming.md`](naming.md) | paths, ids, root resolution |
| [`disclosure.md`](disclosure.md) | load tiers and boot budgets |
| [`execution.md`](execution.md) | scripts, delegation, procedures, pipelines, and resumable state |
| [`seams.md`](seams.md) | boundary contracts and lifecycle |
| [`installation.md`](installation.md) | location, discovery, import |
| [`migrations.md`](migrations.md) | moves, supersession, extraction |
| [`lifecycle.md`](lifecycle.md) | agent-neutral event wiring and context commands |
| [`gates.md`](gates.md) | checks, failure, run times |
| [`consumers.md`](consumers.md) | non-agent read/write contract |

## What doctrine is not

Doctrine holds no principal, project, machine, or permission content. Workspace
chambers hold context; `80_governance/` holds authority.

## Changing doctrine

Human-owned. Proposals name the file, rule, and observed failure in a Decision
Packet. Correct isolated errors in place; supersede depended-on rules and demote
the old record below `mature`.
