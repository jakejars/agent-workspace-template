---
id: frontmatter-spec
type: doctrine
status: draft
description: OKF v0.2 metadata contract. Use when authoring or validating content. Not for filing paths (see doctrine/filing.md).
updated: 2026-10-07
---

# Frontmatter — OKF v0.2

[`schema.json`](schema.json) is the sole executable source for fields,
vocabularies, defaults, type requirements, filing, and limits.
`tools/build_catalog.py` loads it and fails closed if it is absent or invalid.

Every content file opens with frontmatter. Its `id` survives moves; `type`
selects filing; `updated` dates content changes. Status means:

- `reserved`: named but empty;
- `stub`: intended, unopened;
- `draft`: usable with caveat;
- `mature`: citable.

`description` is the routing interface, normalized to one line and at most
180 characters: `<summary>. Use when <cue>. Not for <boundary> (see
<destination>)`, where `<summary>` is the subject phrase.

`load` controls disclosure, not importance. `owner` names change authority.
`precedence: protected` is an override floor. `provenance` is required on
durable content — memory, canon, decisions, policy — and `agent_proposed` is
provisional evidence, never self-granted policy or permissions. Factual use
requires source/scope/freshness checks. Human promotion is required for standing
authority and mature status, so nothing `agent_proposed` may be `mature`. Typed refs must resolve. Shared scope outranks
local only for shared truth; narrower workspace scopes otherwise win. `okf`
pins the contract version on files that travel; a mismatch fails.

Omit neutral schema defaults. Never omit ownership, protected precedence,
meaningful token use, a declared runtime subject, dates, or reserved status.

The workspace entrance alone declares ordinary boot inputs and caps. An
extracted optional-pack entrance may declare its token names locally.

## Pipeline contracts

`pipeline` defines a versioned process in `60_capabilities/pipelines/`; `stage`
defines one numbered contract beneath it. Stages declare `executor`, `output`,
and `checkpoint`; a script also declares `command`. Each contract is capped at
3,000 characters including frontmatter, matching the dynamic disclosure budget.
`tools/pipeline.py check` enforces the schema fields and stage shape.

A pipeline execution remains type `run`. Its `pipeline`, `pipeline_version`,
`pipeline_digest`, and `pipeline_stages` record the definition and stage plan
used at start. Output and checkpoint receipts are evidence, never permissions.

## Edge fields

A directory door (`INDEX.md` or `README.md`) may declare typed fields for its
subtree:

```yaml
fields:
  - name: confidence
    kind: number              # string | number | bool | date | list
    values: [a, b]            # optional vocabulary
    for: preference           # optional type restriction
    required: true            # requires for; draft/mature only
```

Unknown keys, wrong kinds, invalid values, and missing required fields fail.
Edge declarations extend the schema; they do not override it.

Exemptions are narrow: ignored catalogs, bounded runtime pointers, licences,
root `README.md`, and journal payloads.
