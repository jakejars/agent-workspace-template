---
id: kit-approval
type: template
status: mature
description: Approval-record kit. Use when recording a human answer to a class-B or class-C packet. Not for framing the request (see workspace/50_registers/decision-queue.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: workspace/80_governance/approvals/README.md
---

# Kit — approval

**Copy to:** `workspace/80_governance/approvals/{{TODAY}}-{{PACKET_ID}}.md`
**Markers:** `{{EXPIRY_DATE}}` `{{PACKET_ID}}` `{{TODAY}}`

One file per approval. An approval exists only in answer to a packet,
and it binds that packet's action text exactly as written. The full
format law is `workspace/80_governance/approvals/README.md`; this kit
is that law as a file.

```markdown
---
id: approval-{{PACKET_ID}}
type: approval
status: mature
description: >
  Approval of <the action, in one line>. Use when checking whether it
  is covered before taking it. Not for adjacent actions (see
  workspace/50_registers/decision-queue.md).
scope: workspace
what: <the exact action, copied verbatim from the packet>
packet: workspace/50_registers/decision-queue.md#{{PACKET_ID}}
class: C
granted_by: <the human, named>
granted: {{TODAY}}
expiry: {{EXPIRY_DATE}}
conditions: <any precondition that must still hold at execution time>
owner: human
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/50_registers/decision-queue.md
---

# Approval — {{PACKET_ID}}

## What this does not cover

Named exclusions, so the approval is not read wider than it was given.

- <the adjacent action a reader might assume is included>
```

## Rules

- Copy `what` from the packet unedited; rewording creates a different action.
- `granted_by` names a human. Agents never grant their own approval.
- Expiry is required; expired approval authorises nothing, including repeats.
- Withdrawal appends a new record; retain the old at `status: draft`.
- Every effect cites its approval id in the run record.
