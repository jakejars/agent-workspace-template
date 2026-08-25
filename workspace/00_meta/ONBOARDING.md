---
id: onboarding
type: doctrine
status: draft
description: Instance setup walk. Use when `.uninitialised` exists. Not for token definitions (see placeholders.md).
scope: workspace
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/00_meta/placeholders.md
  - type: depends_on
    ref: workspace/AGENTS.md
---

# Onboarding — the instantiation walk

While `00_meta/.uninitialised` exists, do only these seven idempotent steps;
restart an interrupted walk at 1. Door: [`INDEX.md`](INDEX.md).

## 1. Interview

Ask one question per [`placeholders.md`](placeholders.md) row, in order; never
batch or infer answers.

- Offer defaults aloud; never assume them. Accept alternatives.
- Empty closes shared-context, registry, or library seams; for legal name or
  client codename it omits that scrub term. Never substitute `—`.
- Verify paths exist. `<<MACHINE_FILE>>` must resolve outside the sett root.
- Read every answer back. Do not ask or guess pronouns; unstated = `they`.

Write substitution answers to `00_meta/values.json`, except never-share
answers: write those only to ignored `.sett-private/never-share.txt`; never print or commit it.

### When you cannot ask

Written answers count; cite their source in the birth journal. If nobody can
answer:

1. Apply documented defaults.
2. Open one `50_registers/open-loops.md` row naming outstanding tokens,
   applied defaults, and uninstantiated state.
3. Stop before step 2; do not write identity or delete the sentinel.

## 2. Fill the workspace

```sh
python3 tools/instantiate.py          # fill; --check audits an instance
```

It applies `values.json` per `placeholders.md`, token-by-token, in files
declaring `tokens: true` and nowhere else, closes any seam whose path was left
empty, completes steps 3 and 7, and refuses if an answer is missing. Do it by
hand only if you cannot run Python — and then touch no file without the flag,
because a family-wide replace also rewrites the `tools/` test fixtures.

## 3. Instantiate the other members

Fill linked optional members. For commons, complete this workspace's roster row
(both dates today) and replace the fabricated `CHANGES.md` trailer with the
instantiation change; keep the library example topic. Verify family-wide that
no `<<` remains in a `tokens: true` file; a survivor means missing registration
or a missing flag. Tokens outside a consumer — doctrine prose, `tools/`
fixtures — stay as they are.

## 4. Link the seams

- Shared context: verify path; if linked, distil human-approved shared truth to
  `70_seams/SHARED.md`; otherwise keep it free of shared principal facts.
- Registry: verify path. Linking installs nothing; installation remains a
  separate human-gated act in `60_capabilities/`.
- Library: verify path, readable `LIBRARY.md` and catalog, and gates exit 0.
  It never boots; unlinked knowledge stays in `40_knowledge/`.
- Consumer: if enabled, list this root in `~/.sett/roots` and open its seam;
  otherwise leave both closed. Either answer is reversible.

## 5. Seed identity and first intent

Fill `10_identity/` only from interview answers. Reference `<<MACHINE_FILE>>`;
never copy hardware facts. Copy the intent kit into `20_intent/active/` and
record the first intent in the principal's words.

## 6. Install the hooks and run the gates

Two hooks, not one. The commit hook is the backstop; the runtime hook is the
prevention, and without it an agent can edit a journal entry and only learn at
commit that it was forbidden. Wiring it is the principal's act: copy the
`PreToolUse` block from `tools/hooks/settings-example.json` into this
workspace's runtime settings, then answer `70_seams/harness.md`, which
otherwise stands as "no hooks fire". Declining is a valid answer; record it in
the seam.

```sh
git config core.hooksPath .githooks   # once per clone; enables pre-commit
python3 tools/scrub_check.py --staged # scan the Git index; redact matches
python3 tools/build_catalog.py --check # validate source without query outputs
python3 tools/check_loop.py           # prove every file is reachable, no orphans
python3 tools/agnostic_check.py       # no undeclared vendor agent name anywhere
```

Run at the sett root. Fix every failure; link orphans from the chamber door,
never delete them. Generate ignored query outputs only on demand. Full suite:
`doctrine/gates.md`.

## 7. Delete the sentinel

Only now delete `00_meta/.uninitialised`; append one birth journal entry naming
the instance, links, and first intent. The sentinel never comes back: beside a
written journal it is a gate error, because it re-routes every later session
into this walk.

## Checklist

- [ ] Every token answered and read back, or defaults + open-loops row
- [ ] `values.json` written; no `<<` survives in any `tokens: true`
      file, and none was touched outside one; `CHANGES.md`'s example
      trailer replaced
- [ ] Member seams true (linked and verified, or explicitly stub);
      the consumer question answered
- [ ] `10_identity/` filled from the interview; first intent
      captured in `20_intent/active/`
- [ ] `core.hooksPath` set; the runtime `PreToolUse` hook wired or
      declined in `70_seams/harness.md`; every gate exits 0
- [ ] `.uninitialised` deleted, and instantiation journalled
