---
id: seams-index
type: doctrine
status: draft
description: Seams chamber map. Use when touching anything outside the workspace. Not for permission after crossing (see workspace/80_governance/INDEX.md).
scope: workspace
owner: human
updated: 2026-08-24
---

# 70_seams — every edge of this workspace

Nothing outside this workspace is touched without a seam file. A seam
file is not documentation of a system; it is the contract for
crossing into it. **An unopened seam is a closed seam** — if the file
says `status: stub`, the crossing has not been designed and the agent
does not improvise one.

Cross-member references also go here: chambers never link into a
sibling member by relative path. The seam file holds the path.

## The five questions, in order

Every seam file answers exactly these, under these headings:

1. **What crosses** — the concrete payload. Files, records, calls.
2. **Direction** — in, out, or both, per payload. Asymmetry is normal.
3. **Inspect point** — where a human or a gate can see what crossed,
   after the fact. No inspect point means no seam.
4. **Control point** — where a crossing is stopped or narrowed, before
   it happens. Which flag, which file, which approval.
5. **What never crosses** — the standing exclusions. Always includes
   the never-share tiers in
   [`../80_governance/boundaries.md`](../80_governance/boundaries.md).

## The seams

| Seam | System | Status |
|---|---|---|
| [harness.md](harness.md) | The agent runtime: hooks, session files, injected context | stub |
| [SHARED.md](SHARED.md) | Compact shared-scope view for ordinary boot | mature |
| [shared-context.md](shared-context.md) | The commons — source for refreshing the compact view | draft |
| [registry.md](registry.md) | The toolshed — checksummed capability distribution | draft |
| [machine.md](machine.md) | Machine truth: hardware, toolchain, installed software | stub |
| [library.md](library.md) | The library — reference knowledge cited in, captures out | draft |
| [mcp.md](mcp.md) | MCP servers this workspace consumes or serves | stub |
| [world.md](world.md) | Network, email, publishing — governed egress. Default: closed | stub |

A seam reaching `mature` records the date its answers were verified in
`verified_on:` ([schema](doctrine/schema.json)); the validator refuses
`status: mature` without it. See `doctrine/seams.md`, lifecycle.

## Opening a seam

Opening a seam is class B at minimum, and class C where it creates an
external effect (see `../80_governance/autonomy.md`). The order is
always: answer question 5 first (what never crosses), then 4 (the
control point), then the rest. A seam designed from "what crosses"
outward ends up with no floor.
