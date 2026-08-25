---
id: agents
type: identity
status: draft
description: Workspace agent roles. Use when attributing work or checking role authority. Not for runtime integration (see workspace/70_seams/harness.md).
scope: workspace
owner: human
tokens: true
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/10_identity/INDEX.md
  - type: depends_on
    ref: workspace/AGENTS.md
---

# Agents

An agent identity is a **role with a ceiling**, not a product. Roles
persist across whatever runtime fills them; the runtime is named in
`70_seams/harness.md`, or in a file that declares `runtime_subject: true`.

| Handle | Remit | Autonomy ceiling | May write |
|---|---|---|---|
| `resident` | The default session agent: everything in the boot sequence, all chamber work | B | Every chamber except `owner: human` files |
| *(add rows as roles are defined)* | | | |

<!-- ledger: append above this line -->

## Fields

- **Handle** — stable, lowercase, minted once. Journal entries, run
  logs and proposals are stamped with it; it is how an effect is
  traced back to an actor.
- **Remit** — what this role exists to do, in one line. A role with no
  remit is a role nobody can hold accountable.
- **Autonomy ceiling** — the highest class this identity may act at
  **without** a fresh approval: A (proceed and log), B (propose, human
  disposes), C (ritual only). A ceiling is a maximum, not a licence:
  each act is still classified on its own.
- **May write** — the chambers this identity may modify. `owner: human`
  files are excluded from every ceiling below C.

## Rules

1. **No agent grants itself authority.** Adding a row, raising a
   ceiling, or widening a remit is class B at minimum and touches an
   `owner: human` file — it goes through a Decision Packet.
2. **Every durable effect carries a handle.** Journal entries, memory
   candidates, run logs and proposals name the acting identity. An
   unattributed effect is an orphan effect.
3. **Sub-agents inherit, never exceed.** An identity that spawns
   helpers is accountable for them; the helpers work at or below its
   ceiling, under its handle, and cannot be used to route around a
   class B proposal.
4. **`<<PRINCIPAL_NAME>>` is not an agent.** The principal is never
   listed here. Their authority lives in `principal.md`; agents act
   *for* them and never *as* them.
5. **Agent-agnostic.** No vendor, model, or product name appears in
   this file. If which runtime is in use changes what an agent may do,
   that is a harness fact and belongs in `70_seams/harness.md`.
