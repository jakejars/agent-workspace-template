---
id: memory-preferences
type: doctrine
status: draft
description: Promoted preferences. Use when recurring corrections should guide future work. Not for hard constraints (see workspace/80_governance/policies.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/30_memory/INDEX.md
  - type: contrast_with
    ref: workspace/80_governance/policies.md
fields:
  - name: confidence
    kind: number
    for: preference
    required: true
  - name: rule
    for: preference
    required: true
  - name: support
    kind: list
    for: preference
    required: true
---

# preferences/ — taste, scoped and earned

One evidence-backed correction pattern per `<slug>.md`, `type: preference`.

## Required beyond the OKF core

```yaml
scope: workspace | shared | project:<slug> | run:<id>
confidence: 0.0–1.0
rule: <what produced this>       # e.g. "≥3 consistent corrections"
support:                         # the corrections themselves
  - 30_memory/journal/2026-08-19-0930-shortened-summary.md
provenance: agent_proposed | promoted
```

- `scope`: shared wins shared-scope conflicts; otherwise most specific wins;
  protected floors override. Record ties/overrides.
- `confidence`: below ~0.5, observe rather than propose.
- `rule`: auditable derivation of confidence.
- `support`: counted journal corrections; disclose single-instance weakness.

## The consumption hop

Promoted preferences remain `cue`; distil universal rules into the bounded
shared boot view per `doctrine/disclosure.md`.

## Mutation rule

Contrary evidence edits confidence/support. Reversal creates a new preference
with `supersedes`; retain the old.

## Boundaries

Principal preferences are shared-scope commons candidates through the shared
seam; never silently contradict commons locally. Agents propose; humans promote
(Class B). Proposals never bind or use `load: always`.
