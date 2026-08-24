---
id: kit-capability
type: template
status: mature
description: Capability kit. Use when publishing or repacking a capability. Not for installed-state records (see workspace/60_capabilities/installed.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: workspace/70_seams/registry.md
---

# Kit — capability

**Copy to:** `registry/{{CAPABILITY_NAME}}/`
**Markers:** `{{CAPABILITY_NAME}}` `{{TODAY}}`

One `manifest.yml` plus verbatim `files/`; folder name is immutable identity.

```text
registry/{{CAPABILITY_NAME}}/
├── manifest.yml
└── files/
    └── <src paths referenced by manifest files[]>
```

## The manifest

Data, not OKF content; catalogued through its capability.

```yaml
name: {{CAPABILITY_NAME}}     # MUST equal the folder name
version: 1                    # integer, monotonic, +1 per pack
description: >
  <What it does, in one sentence.> Use when <the trigger>. Not for
  <the adjacent capability> (see registry/<other>/manifest.yml).
updated: {{TODAY}}

files:
  - src: <path under files/>
    target: 60_capabilities/{{CAPABILITY_NAME}}/<path>   # workspace-relative
    sha256: <64 hex of the bytes at files/<src>>

requires: []                  # capability names only, never paths
```

## A markdown payload file

Payload Markdown carries OKF frontmatter and publishes `draft`.

```markdown
---
id: cap-{{CAPABILITY_NAME}}
type: capability
status: draft
description: >
  <What this payload is.> Use when <the situation that invokes the
  capability>. Not for <the adjacent thing> (see <ref>).
scope: shared
load: drill
owner: shared
updated: {{TODAY}}
---

# {{CAPABILITY_NAME}}

<Effects and exclusions. No workspace-specific paths, names, or machine facts.>

## Effects

<Every external effect + autonomy class. Unstated means none.>

## Verification

<One verification command.>
```

## Rules

- Every `files[].src` exists; every payload appears once; every checksum matches.
- Targets are workspace-relative; reject absolute paths, `..`, `~`, and
  symlinked ancestors on install, pack, and verify.
- Version is a rising integer: payload changes require a bump; no-op bumps fail.
- Installation stays `untrusted` until human approval promotes it.
- Publish only with a new `registry/ledger.md` row.
