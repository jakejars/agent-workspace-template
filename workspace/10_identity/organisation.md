---
id: organisation
type: identity
status: draft
description: Workspace organisation. Use when work belongs to an entity rather than a person. Not for the principal (see principal.md).
scope: workspace
owner: human
tokens: true
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/10_identity/INDEX.md
  - type: see_also
    ref: workspace/10_identity/principal.md
---

# Organisation

| Field | Value |
|---|---|
| Name | `<<ORG_NAME>>` |
| Principal's role | *unfilled* |
| Entity kind | *unfilled — company, sole trader, project, none* |
| Public presence | *unfilled — sites, handles this sett may be asked to produce for* |

If this sett does purely personal work, `<<ORG_NAME>>` is `—` and the
rest of this file stays unfilled. An empty organisation is a real
answer; a guessed one is a liability.

## The org/personal line

Every artefact this sett produces belongs to exactly one side of the
line, and the side is decided **before** the work, not at publication:

| | Organisational | Personal |
|---|---|---|
| Attribution | `<<ORG_NAME>>` | `<<PRINCIPAL_NAME>>` |
| Intent | names the org in its scope | scope stays `workspace` |
| Egress | governed by the org's obligations as well as the workspace's | workspace boundaries only |

When an intent does not say which side it sits on, it is a class B
question: ask, do not assume. Mis-attributed output is not fixable
after it leaves.

## What never crosses

Organisational identity is a name this sett may write; it is not
authority this sett may exercise. No agent in this sett may sign,
contract, invoice, represent, or publish **as** `<<ORG_NAME>>` without
a recorded approval naming that specific act. Never-share terms in
`80_governance/boundaries.md` bind regardless of which side of the
line the work sits on.
