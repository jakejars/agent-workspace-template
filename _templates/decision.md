---
id: kit-decision
type: template
status: mature
description: Decision-record kit. Use when a settled choice constrains later work. Not for a choice awaiting human disposition (see workspace/50_registers/decision-queue.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: contrast_with
    ref: _templates/dead-end.md
---

# Kit — decision

**Copy to:** `workspace/40_knowledge/decisions/{{DECISION_ID}}-{{SLUG}}.md`
**Markers:** `{{DECISION_ID}}` `{{SLUG}}` `{{TODAY}}`

`{{DECISION_ID}}`: monotonic, never-reused `NNNN` (`doctrine/naming.md`).

```markdown
---
id: dec-{{DECISION_ID}}-{{SLUG}}
type: decision
status: draft
description: >
  <The choice, in one sentence.> Use when <the recurring question this
  settles> comes up again. Not for <the related question left open>
  (see workspace/50_registers/open-loops.md).
scope: workspace
load: cue
owner: human
provenance: agent_proposed
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/20_intent/active/<intent>.md
---

# {{DECISION_ID}} — <Short statement of the choice>

**Status:** proposed | accepted | superseded by `dec-<id>`
**Decided:** {{TODAY}} · **Decided by:** <human> · **Class:** A | B | C

## Context

<What forced the choice; constraints; null outcome. Max 2 paragraphs.>

## Options

| Option | For | Against |
|---|---|---|
| A — <name> | <the strongest point for it> | <the cost> |
| B — <name> | <...> | <...> |
| C — do nothing | <...> | <...> |

<Every reasonable option, including null; at least 2 real alternatives.>

## Choice

Option <X>.

## Rationale

<Why it beat each alternative; decisive constraint.>

## Consequences

- Accepted cost: <what this makes harder or slower>
- Now foreclosed: <what this decision rules out>
- Revisit when: <the condition, or "no expected trigger">

## Supersession

Newest first. Never rewrite; changes create a new decision with
`supersedes: dec-{{DECISION_ID}}-{{SLUG}}` and add a line here.

- {{TODAY}} — recorded.
```

## Rules

- Never edit accepted decisions; supersede them.
- Agents propose; humans accept. Keep agent records `proposed` and
  `agent_proposed`; class-B approval lives in `80_governance/approvals/`.
- Queue unanswered packets with an applied default so work continues.
