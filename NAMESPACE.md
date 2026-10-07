---
id: namespace
type: doctrine
status: draft
description: Reserved family paths. Use when checking whether a path has a meaning. Not for graph mechanics (see LOOP.md).
updated: 2026-10-07
related:
  - type: see_also
    ref: doctrine/filing.md
  - type: contrast_with
    ref: doctrine/INDEX.md
---

# Namespace

Reserved names are not required structure. Create a path only when content
needs it. The workspace root is the nearest ancestor containing this file. Marks:
`[c]` content, `[s]` reserved/optional, `[g]` generated/ignored.

```text
agent-workspace-template/
├── README.md  LOOP.md  NAMESPACE.md  AGENTS.md         [c]
├── CLAUDE.md  GEMINI.md  LICENSE  .gitignore          [c]
├── CATALOG.md  CATALOG.json                           [g]
├── .githooks/{pre-commit,post-commit,post-checkout,post-merge}                              [c]
│
├── doctrine/                                               [c]
│   ├── INDEX.md  schema.json
│   ├── frontmatter-spec.md  filing.md  naming.md  disclosure.md  lifecycle.md
│   └── seams.md  migrations.md  installation.md  gates.md  consumers.md
│
├── _templates/                                             [c]
│   ├── README.md  intent.md  run/README.md  skill/README.md  handover.md  seam.md
│   ├── decision.md  dead-end.md  procedure.md  board.md
│   └── memory-fact.md  preference.md  approval.md  capability.md
│       topic.md  specimen.md  capture.md
│
├── .github/workflows/gates.yml                             [c] CI
│
├── tools/                                                  [c]
│   ├── build_catalog.py  check_loop.py  journal_guard.py  workspace_layout.py
│   ├── scrub_check.py  agnostic_check.py  instantiate.py  workspace_setup.py
│   ├── new.py  doctor.py  lifecycle.py  context.py  check_staged.py  skills.py
│   ├── test_gates.py  test_gate_corrections.py  test_instance.py
│   ├── test_context.py  test_staged.py  test_onboarding.py  test_hooks.py
│   ├── test_new.py  test_skills.py
│   └── hooks/{shim.py,settings-example.json,install.py}
│
├── workspace/                    THE WORKSPACE — the instantiable member
│   ├── AGENTS.md                 [c] the entrance: constitution + boot
│   ├── CLAUDE.md  GEMINI.md      [c] pinned pointers
│   ├── 00_meta/                  instantiation state
│   │   ├── INDEX.md  ONBOARDING.md  placeholders.md  [c]
│   │   └── .uninitialised [c] · .initializing [s] · values.json [s] · ready.json [s]
│   ├── 10_identity/              who
│   │   └── INDEX.md  principal.md  organisation.md  agents.md  machines.md [c]
│   ├── 20_intent/                what is wanted
│   │   └── INDEX.md  active/ satisfied/ README.md [c] · <intent>.md [s] moves
│   ├── 30_memory/                what is known
│   │   ├── INDEX.md  journal/README.md (the door and its pattern)  [c]
│   │   ├── journal/YYYY-MM-DD-HHMM-slug.md [s] no OKF frontmatter; immutable
│   │   └── facts/ preferences/ procedures/ dead-ends/ README.md  [c]
│   ├── 40_knowledge/             what is understood
│   │   ├── INDEX.md  canon/ references/ decisions/ README.md    [c]
│   │   └── decisions/NNNN-slug.md [s] supersede-only; the numbered exception
│   ├── 50_registers/             what waits
│   │   ├── INDEX.md  decision-queue.md  open-loops.md  tensions.md  risks.md [c]
│   │   └── boards/               [s] rendered views; never a source of truth
│   ├── 60_capabilities/          what it can do
│   │   ├── INDEX.md  installed.md [c] the lockfile
│   │   └── skills/README.md [c] · <name>/SKILL.md [s] · scripts/ references/ assets/ [s]
│   ├── 70_seams/                 what it touches
│   │   ├── INDEX.md  SHARED.md  shared-context.md  registry.md  library.md [c]
│   │   ├── harness.md            [s] the seam whose subject is the runtime
│   │   └── machine.md  mcp.md  world.md  [s] unopened; egress default closed
│   ├── 80_governance/            what it may do
│   │   ├── INDEX.md  policies.md  autonomy.md  approvals/README.md  [c]
│   │   ├── boundaries.md         [c] confidentiality categories
│   │   └── approvals/<slug>.md   [s] one per approval, scoped, expiring
│   └── 90_runs/                  what it did
│       ├── INDEX.md              [c]
│       └── <run-id>/run.md  handover.md  [s] cites one intent · on continue
│
├── shared-context/               THE COMMONS — a governed store
│   ├── SHARED.md                 [c] the member entrance
│   ├── INDEX.md  CHANGES.md  roster.md  _meta/governance.md    [c]
│   ├── boundaries/  calibration/ [c] categories · proposed changes
│   └── identity/  operating-rules/  [c] README.md + <subject>.md [s]
│
├── registry/                     THE TOOLSHED — capability distribution
│   ├── README.md  ledger.md      [c]
│   └── <cap>/                    manifest.yml [g] + files/ [c]
│
└── library/                      THE SHELF — practice and taste, catalogued
    ├── LIBRARY.md  INDEX.md      [c] the door: route, trust, rights · the map
    ├── doctrine/  [c] filing-ladder.md · claims.md · media-and-rights.md
    ├── fields/README.md          [c] the field shelf
    │   └── <field>/INDEX.md      [s] field · <pillar>/INDEX.md pillar
    │       └── <topic>/README.md [s] topic — the unit of knowledge, plus
    │           ├── DEEP-DIVE-<slug>.md  RESOURCES.md  examples/<name>/ [s]
    │           └── specimens/<name>/NOTE.md [s] taste + rights · all on a cue
    ├── boards/README.md          [c] + <name>.md [s] views; link, never copy
    └── inbox/README.md           [c] + <slug>.md [s] captures, 60-second rule
```

Ignored: `.workspace-private/never-share.txt` holds literal terms; never tracked.
`.workspace-cache/` holds derived context/graph and lifecycle receipts. Root or
run-level `work/` and `artifacts/` hold ignored arbitrary-format outputs.

## Required spine

`workspace/AGENTS.md`, `workspace/70_seams/SHARED.md`, `doctrine/`, `tools/`,
`NAMESPACE.md`, and a door in every existing content directory. Reserved paths
may be absent.

## Adding to the namespace

Add a path only for imminent content that `doctrine/filing.md` cannot place.
