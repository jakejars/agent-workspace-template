---
id: registry-contract
type: doctrine
status: draft
description: Toolshed contract. Use when publishing or installing a capability. Not for installed-state history (see ledger.md).
scope: shared
owner: human
updated: 2026-10-07
related:
  - type: composes_with
    ref: registry/ledger.md
  - type: see_also
    ref: registry/example-capability/manifest.yml
---

# The toolshed

An extractable store of checksummed, integer-versioned capabilities. It has no
workspace knowledge or external links; workspaces cross via their registry
seam. Installation copies bytes; separate human promotion grants trust.

## Capability folder shape

```text
registry/
├── README.md              this contract
├── ledger.md              append-only record of every publish and pack
└── <capability-name>/
    ├── manifest.yml       the governing record (fields below)
    └── files/             the payload, mirrored verbatim
        └── <src paths>    referenced by manifest files[].src
```

One folder per capability; its name is identity, so rename creates a new
capability. Fixed-shape folders have no local door and are pattern-listed here.

<!-- lists: */files/* --> <!-- lists: */files/scripts/* --> <!-- lists: */files/references/* --> <!-- lists: */files/assets/* --> The worked example is [`example-capability/manifest.yml`](example-capability/manifest.yml)
with its payload [`example-capability/files/README.md`](example-capability/files/README.md);
every event in this toolshed is a row in [`ledger.md`](ledger.md).

`manifest.yml` is uncatalogued data read by the checksum gate. Payload Markdown
is ordinary frontmatter-bearing content.

## Manifest fields

```yaml
name: kebab-case            # required; MUST equal the folder name
kind: capability            # optional; capability (default) | skill
version: 3                  # required; INTEGER, monotonic, +1 per pack
description: >              # required; "Use when … Not for … (see …)"
updated: YYYY-MM-DD         # required; ISO
files:                      # required; at least one entry
  - src: bin/tool.py        # relative to this capability's files/
    target: 60_capabilities/bin/tool.py   # workspace-relative
    sha256: <64 hex>        # of the bytes at files/<src>
requires: []                # optional; capability names, by name only
```

Validator-enforced: folder/name equality; integer version shape (no semver); exact
one-to-one `files[]` coverage; workspace-relative safe targets (no absolute,
`..`, or `~`); matching sha256. A future installer must additionally
check resolved targets and symlink ancestors.

For `kind: skill`, the folder name follows the Agent Skills name rules
(lowercase letters, digits and hyphens, at most 64 characters). The payload
root contains `SKILL.md` with matching `name` and `type: skill`; optional
`scripts/`, `references/` and `assets/` hold supporting files. Every target
must be `60_capabilities/skills/<name>/<src>`, preserving this package shape.
All payload bytes remain checksummed; a new install is `untrusted`, and
agent-authored skill metadata remains `agent_proposed` until human promotion.

## Install flow (registry → workspace)

```text
read manifest.yml — every requires: name in the lockfile, else stop
  → path-safety check on every target
  → verify sha256 of every files/<src>          mismatch = stop, no writes
  → for each target that exists:
       identical bytes  → skip (already installed)
       differing bytes  → REFUSE unless --yes    (see below)
  → copy files/<src> → <workspace>/<target>
  → record name + version + per-file sha256 in the workspace lockfile
```

Checks complete before writes; failure leaves the workspace byte-identical.

## Pack flow (workspace → registry)

```text
collect each target's current bytes from the workspace
  → unchanged everywhere?    stop: nothing to pack, no version burned
  → differing registry file  → REFUSE unless --yes
  → copy back into files/, recompute every sha256
  → version = version + 1, updated = today
  → print the ledger line; --write-ledger appends it to ledger.md
```

Payload changes require a bump; no-op bumps fail.

## Refuse-overwrite semantics

On differing existing bytes: stop unchanged and report every path. Only a human
may supply `--yes`; it covers one invocation. Agents may probe without it.

## Checksums and the catalog gate

The catalog gate recomputes manifests and rejects mismatches, missing/unlisted
payloads, invalid versions, and unsafe targets. Drifted capabilities are neither
installable nor catalogued.

## Publishing a new capability

Copy `_templates/capability.md` or `example-capability/`; replace payload,
rewrite manifest at version 1, run the gate, append a ledger row. Publish
`draft`; maturity is earned in use.
Package a skill from the skill kit through the workspace's registry seam,
using `kind: skill`; publication and installation grant no trust.

Install/pack flows and their flags above are a consumer contract, not shipped
commands. No installer or packer is included. Version monotonicity and no-op
bump detection require comparison with a prior manifest and are not enforced
by the current snapshot checksum validator.
