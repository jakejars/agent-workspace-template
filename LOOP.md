---
id: loop
type: doctrine
status: draft
description: Sett flows and reachability. Use when wiring a seam or tracing lifecycle. Not for filing rules (see doctrine/filing.md).
updated: 2026-08-24
related:
  - type: see_also
    ref: doctrine/INDEX.md
---

# Loop

## Session

```text
workspace/AGENTS.md
  → frontmatter boot_static, in order
  → boot_selector match from boot_dynamic, if any
  → task-cued links and descriptions
  → durable event: journal append
  → continuing work: bounded handover
  → session-close gates
  ↺ next session
```

Onboarding is an instance-initialisation exception, not ordinary boot.
Catalogs are ignored query outputs, never boot or reachability inputs.

## Content lifecycles

```text
capture → agent_proposed → human promotion → canonical
correction → new record → supersedes old record
intent → run → outcome → satisfied | abandoned | superseded
consequential proposal → packet → approval → effect → run evidence
```

Journal events never mutate. Decisions and promoted memory hold durable truth;
registers hold unresolved state. External effects resolve to policy or explicit
approval.

## Family exchange

Optional members do not load during ordinary workspace boot.

| Member | Workspace crossing |
|---|---|
| commons | Explicit refresh distils approved shared truth into `70_seams/SHARED.md`; corrections return as candidates |
| registry | Install by manifest and checksum; installation is not promotion |
| library | Query and cite on demand; capture reusable material back to its inbox |

Every crossing is described by one `70_seams/` file answering: what crosses,
direction, inspect point, control point, and what never crosses.

## Reachability

`tools/check_loop.py` enforces, independently from each member entrance:

- every content file is reachable within three human-authored link or
  `related` hops;
- no orphan, dead link, or direct member-to-member link;
- every directory door lists adjacent content, or declares a bounded
  machine-significant `lists` pattern — matched segment by segment, so one
  `*` never crosses a `/`, and refused outright if no segment carries a
  literal;
- workspace outputs such as journal and handover remain reachable.

`tools/build_catalog.py` holds the journal to its own contract — entry name,
header keys, kind, resolvable refs — and refuses a run that no entry traces.

Catalog links do not count. `tools/test_gates.py` and
`tools/test_gate_corrections.py` plant violations to prove failure direction.
