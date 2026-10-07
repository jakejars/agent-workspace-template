---
id: templates-index
type: doctrine
status: draft
description: The kit shelf. Use when creating any new record and you want its required fields. Not for what the fields mean (see doctrine/frontmatter-spec.md).
owner: human
updated: 2026-10-07
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
---

# Kits

A kit is a fenced, valid OKF v0.2 example. A kit/prose conflict is a kit bug.

## The copy ritual

1. Pick the type's kit; if none fits, check the type table before inventing.
2. Copy only the fenced content to the named target.
3. Fill each per-record `{{marker}}`; markers are unregistered and untouched by
   instantiation. Registered `<<TOKEN>>` values are onboarding substitutions and
   require `tokens: true`. Kits and copied records carry no such token.
4. Mint a unique, never-reused kebab-case `id`; set `updated`.
5. Write `<scope>. Use when <cue>. Not for <boundary> (see <ref>).`
6. Link from the chamber door; build the catalog and run the loop check.

## Frontmatter you always fill

Fill `id`, `type`, `status`, `description`, `updated`. Kits include needed
optional fields (`scope`, `load`, `owner`, `provenance`, `related`); delete empty
ones. Agent records start `draft` + `agent_proposed`; their author never
promotes them.

## The shelf

| Kit | Type | Copies to |
|---|---|---|
| [`intent.md`](intent.md) | `intent` | `20_intent/active/` |
| [`memory-fact.md`](memory-fact.md) | `memory-fact` | `30_memory/facts/` |
| [`preference.md`](preference.md) | `preference` | `30_memory/preferences/` |
| [`procedure.md`](procedure.md) | `procedure` | `30_memory/procedures/` |
| [`skill/README.md`](skill/README.md) | `skill` | `60_capabilities/skills/<name>/SKILL.md` |
| [`pipeline/README.md`](pipeline/README.md) | `pipeline` + `stage` | `60_capabilities/pipelines/<slug>/` |
| [`dead-end.md`](dead-end.md) | `dead-end` | `30_memory/dead-ends/` |
| [`decision.md`](decision.md) | `decision` | `40_knowledge/decisions/` |
| [`board.md`](board.md) | `board` | `50_registers/boards/` |
| [`seam.md`](seam.md) | `seam` | `70_seams/` |
| [`run/README.md`](run/README.md) | `run` | `90_runs/<run-id>/run.md` |
| [`handover.md`](handover.md) | `handover` | `90_runs/<run-id>/` |
| [`approval.md`](approval.md) | `approval` | `80_governance/approvals/` |
| [`capability.md`](capability.md) | `capability` | `registry/<capability>/` |
| [`topic.md`](topic.md) | `topic` | `library/fields/<field>/<topic>/README.md` |
| [`specimen.md`](specimen.md) | `specimen` | `library/fields/<field>/<topic>/specimens/<name>/NOTE.md` |
| [`capture.md`](capture.md) | `knowledge` (a capture) | `library/inbox/<slug>.md` |

`doctrine` and `register` copy neighbouring shape. Journal entries use their
door's append-only, frontmatter-exempt format. Library captures are catalogued
documents and listed by the inbox door's glob.
