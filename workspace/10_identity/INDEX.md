---
id: identity-index
type: register
status: draft
description: Identity chamber map. Use when routing identity or attribution. Not for current intent (see workspace/20_intent/INDEX.md).
scope: workspace
tokens: true
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/AGENTS.md
---

# 10_identity — who

Four files, one subject each. Everything else in the sett references
these and repeats none of them.

| File | Answers |
|---|---|
| [`principal.md`](principal.md) | Who this sett serves; how to address and contact them |
| [`organisation.md`](organisation.md) | Whose work this is; what is org and what is personal |
| [`machines.md`](machines.md) | Which machines this sett runs on, and where each machine's truth lives |
| [`agents.md`](agents.md) | Which agent identities work here, with what remit and autonomy ceiling |

## Rules

1. **One canonical home per identity truth.** A fact stated here is
   referenced everywhere else, never copied. A copy is a fork waiting
   to drift.
2. **Machine truth is referenced, never duplicated.** Hardware,
   toolchain and installed-app facts live in `<<MACHINE_FILE>>` on the
   machine itself. `machines.md` holds the pointer and the role, not
   the specs.
3. **Shared outranks local.** Where a commons is linked, its identity
   records bind; observations made here become correction candidates
   for the commons, never silent local overrides.
4. **Pronouns unstated means `they`.** Never guess, never infer from a
   name, never ask twice.
5. **`owner: human`.** These files are filled at onboarding and edited
   by proposal after it. An agent that believes a field is wrong files
   a Decision Packet; it does not correct the field.
6. **Agent-agnostic.** `agents.md` describes roles and remits. The
   runtime that happens to fill a role is named in `70_seams/harness.md`,
   or in a file that declares `runtime_subject: true` — never here.
