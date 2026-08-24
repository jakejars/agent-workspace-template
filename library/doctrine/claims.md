---
id: library-claims
type: doctrine
status: draft
description: The epistemic vocabulary. Use when writing or editing a topic, when stating a best practice. Not for where the material goes (see library/doctrine/filing-ladder.md).
owner: human
updated: 2026-08-24
review_after: 2027-08-24
related:
  - type: canonical
    ref: library/INDEX.md
  - type: composes_with
    ref: library/doctrine/filing-ladder.md
---

# Typed claims

Type actionable practice claims inline; explanatory prose may remain untyped.
Specimens express taste, borrowing bounds, and rights—not claims.

## The vocabulary

| Type | Means | Obligation |
|---|---|---|
| `rule:` | Always holds here | Violating it takes a written reason |
| `guideline:` | The default, with known exceptions | Name the exceptions |
| `opinion:` | Mine | State what it **holds while**, and what would change my mind |
| `experience:` | I did this | Name the setting and the rough scale (n) |
| `evidence:` | Sourced | A link or citation is required |

Vocabulary is closed.

## Canonical example

```markdown
- **rule:** handlers are idempotent — at-least-once delivery is assumed.
- **guideline:** start with the boring storage-backed queue; exception:
  measured volume past a few hundred jobs/sec, or multi-consumer fan-out.
- **opinion:** one queue per service beats one shared queue. Holds while
  teams deploy independently; revisit if the services merge.
- **experience:** ran this on one product for ~2 years, low thousands of
  jobs/day, no losses.
- **evidence:** the semantics are specified in the vendor's own docs —
  <link>.
```

## Quoting outward

Carry type, topic, and opinion conditions. Cite `draft` only with caveat and
`mature` normally; never cite `stub`/`reserved`.

## How it maps onto a topic

| Question | Usually |
|---|---|
| When should I use it / NOT use it | `guideline:` — with the exceptions named |
| What is my current opinion | `opinion:` — holds-while, not just a verdict |
| Where is it used for real | `evidence:` or `experience:` |
| What is it / how does it work | untyped prose; type nothing you would not act on |

Specimens instead use resonance, borrow/do-not-borrow bounds, and rights; see
`_templates/specimen.md`.

## Capture stays exempt

- **rule:** type claims during topic writing, never capture.
