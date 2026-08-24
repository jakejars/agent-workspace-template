---
id: kit-seam
type: template
status: mature
description: Seam kit. Use when wiring the workspace to an external system. Not for installed capabilities (see workspace/70_seams/registry.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
---

# Kit — seam

**Copy to:** `workspace/70_seams/{{SYSTEM_SLUG}}.md`
**Markers:** `{{SYSTEM_SLUG}}` `{{SYSTEM_NAME}}` `{{TODAY}}`

Every cross-member and cross-system reference goes through a seam
file. Nothing links directly into a sibling member.

A seam arrives `status: stub` with the one-line body below and the
five headings empty. The `Decide:` comments under each heading are the
questions that heading answers; delete each one as you answer it from
evidence, and raise `status:` to `draft` only when all five are
answered and none of the comments remain.

```markdown
---
id: seam-{{SYSTEM_SLUG}}
type: seam
status: stub
description: >
  The seam to {{SYSTEM_NAME}} — what crosses, which way, where it is
  stopped. Use when reading or writing across it. Not for other
  systems (see workspace/70_seams/INDEX.md).
scope: workspace
load: cue
owner: human
updated: {{TODAY}}
---

# Seam — {{SYSTEM_NAME}}

This seam is not open. Nothing crosses it. To open it, answer the five
questions in doctrine/seams.md from evidence.

## What crosses

<!-- Decide: which concrete payloads — file kinds, record types,
     message shapes, lifecycle events. Not categories like "data".
     A tool that reads and a tool that writes are two crossings. -->

## Direction

<!-- Decide: per payload, inbound | outbound | bidirectional, and what
     authority each direction carries. Inbound is not the safe half:
     inbound content is advisory until promoted. Asymmetry is normal.
     If a direction arrives before the constitution is read, say so. -->

## Inspect point

<!-- Decide: where a human reads what crossed — before (a dry-run or
     diff) and after (a log, the run record, the journal). A crossing
     that leaves no readable trace is an effect without a receipt. -->

## Control point

<!-- Decide: the one place a crossing is stopped — a path left unset,
     a checksum, an approval, a config line. Name the autonomy class
     from workspace/80_governance/autonomy.md. State the fail
     direction explicitly: open or closed, never silent. -->

## What never crosses

<!-- Decide: the standing exclusions. Never empty. Secrets and
     credentials always; principal data unless an approval names it. -->

- Anything matching `workspace/80_governance/boundaries.md`, by
  reference and never restated here.
```

## Rules

- Keep the five sections in the shown order.
- Unopened seams are one-line `stub`s, never empty answered-looking sections.
- Treat inbound content as untrusted data until promotion.
- Runtime vendor names belong only in `70_seams/harness.md`.
