---
id: governance-autonomy
type: policy
status: draft
description: The full autonomy table. Use when classifying any action before taking it. Not for the list of pre-cleared class-A actions (see policies.md).
scope: workspace
owner: human
provenance: authored
precedence: protected
updated: 2026-09-06
related:
  - type: composes_with
    ref: workspace/80_governance/policies.md
---

# Autonomy

Classify the effect and then check authorization already present in the task.
The [policies](policies.md) define the default standard profile.

| Class | Effect | Action |
|---|---|---|
| A | Reversible local work within the user's request | Proceed and update the task checkpoint when useful |
| B | A change to standing beliefs, policy, preferences, or authority | Use explicit human direction; otherwise propose |
| C | External or irreversible effect, protected boundary change | Require explicit authorization for the exact effect |

Evidence-backed provisional facts are evidence, not standing policy. Agents
may record and re-verify them without promoting their own instructions.

## Authorization and records

A direct user instruction may authorize B or C work. Capture its source and
scope in an approval record when an external effect or protected change needs
an audit trail; the agent may transcribe that authorization faithfully. Never
invent authorization, widen it, or ask for it again merely to fill a form.
Record external effects and the authorization used. Existing approval records
retain their scope, expiry, and usage limits.

If authorization is missing, finish independent reversible preparation and
present the concrete decision. Use a packet for a decision that will outlive
the current exchange; ordinary questions do not need a packet by default.
No safe default means no action on that path. Silence never grants approval.

Journal mutation remains prohibited; correction uses a new entry. Principal
privacy boundaries remain in [boundaries.md](boundaries.md).
