---
id: memory-facts
type: doctrine
status: draft
description: Promoted facts. Use when a journal observation has become stable. Not for taste (see workspace/30_memory/preferences/README.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/30_memory/INDEX.md
  - type: depends_on
    ref: workspace/30_memory/journal/README.md
fields:
  - name: support
    kind: list
    for: memory-fact
    required: true
  - name: claim
    values: [rule, experience, evidence, opinion]
    for: memory-fact
    required: true
  - name: verified_on
    kind: date
    for: memory-fact
    required: true
  - name: holds_while
    for: memory-fact
---

# facts/ — what is true, and how we know

One supported fact per `<slug>.md`, `type: memory-fact`.

## Required beyond the OKF core

```yaml
provenance: agent_proposed | promoted | authored | imported
support:                        # journal entries or artifacts
  - 30_memory/journal/2026-08-24-1412-registry-install-failed.md
claim: rule | experience | evidence | opinion
verified_on: YYYY-MM-DD         # when the fact was last checked true
holds_while: <condition>        # optional; the fact's expiry condition
```

- `support`: at least one journal/artifact ref.
- `claim`: `evidence` inspectable, `experience` counted, `rule` definitional;
  opinions belong in `preferences/`.
- `holds_while`: version/machine/contract condition; expiry makes it stale.

## Mutation rule

Changed assertions create a new fact with `supersedes`; demote but retain the
old and append a journal correction. Typos, wording, and `verified_on` refreshes
may edit in place.

## Boundaries

- Machine truth stays behind `70_seams/machine.md`.
- Principal facts become commons correction candidates through the shared seam.
- Repeatedly reviewed, cited facts may promote to `40_knowledge/canon/`.

## Promotion

Agents write visible, non-binding `draft` + `agent_proposed` facts. Human class-B
promotion changes provenance/status; agents never self-promote.
