---
id: governance-index
type: doctrine
status: draft
description: Governance chamber map. Use when an action may be consequential. Not for the constitution (see AGENTS.md).
scope: workspace
owner: human
precedence: protected
updated: 2026-08-24
---

# 80_governance — permission, in writing

The entrance carries the constitution: the short list of what is never
done. This chamber carries everything below it — the graduated
permissions, the confidentiality floor, and the record of every answer
a human has given.

| File | Holds |
|---|---|
| [autonomy.md](autonomy.md) | The A/B/C table, keyed to reversibility — the full version of the entrance summary |
| [policies.md](policies.md) | The class-A allowlist: what proceeds without asking, and the standing rules |
| [boundaries.md](boundaries.md) | Confidentiality categories and local scrub contract |
| [approvals/README.md](approvals/README.md) | The approval record format, and the folder every answer lands in |

## How the four fit together

```text
an action is wanted
  → autonomy.md   which class? (reversibility decides, not importance)
  → policies.md   class A? then proceed and log. done.
  → 50_registers/decision-queue.md   class B or C: file the packet
  → approvals/    the human's answer lands here, bound to the packet
  → the run log   the effect records the approval it resolves to
boundaries.md sits across all of it: policy and the ignored local term
list bind every class.
```

## Standing rules

1. **When unsure of the class, it is B.** Uncertainty is not a
   licence; it is the definition of "propose".
2. **Never self-approve.** An agent may write a packet, apply a
   default, and continue with other work. It may never record its own
   approval, promote its own proposal, or read consent into silence.
3. **Approvals bind text, not vibes.** An approval covers the exact
   action as written in the packet. A changed action is a new packet.
4. **Approvals expire.** No expiry, no approval. An expired approval
   does not authorise a repeat of the same action.
5. **Class is a property of the effect, not the intent.** A helpful
   motive does not lower a class; an irreversible effect raises it.
6. **Governance files are `owner: human`.** An agent proposes changes
   to this chamber the same way it proposes anything else — and
   changes to the constitution or to boundaries are class C.
