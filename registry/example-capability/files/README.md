---
id: example-capability
type: capability
status: draft
description: Capability example. Use when learning manifest and payload structure. Not for registry rules (see registry/README.md).
load: drill
scope: shared
owner: shared
updated: 2026-08-24
---

# Example capability

This file is the entire payload of `example-capability`. It exists so
that a manifest can point at something real, so the catalog gate has a
checksum to verify, and so a first install can be run end to end
before anything that matters is published.

A real payload would be a tool, a procedure, a hook, or a doctrine
file — whatever the capability actually is. The rules it obeys are the
same either way:

- every payload file appears exactly once in the manifest's `files[]`;
- every payload file that is markdown carries OKF v0.2 frontmatter and
  publishes at `status: draft`;
- the payload knows nothing about any particular workspace — no
  absolute paths, no principal names, no machine facts. What varies
  per workspace is read from that workspace at run time, never baked
  in at publish.

Installing this capability copies this file to the `target` named in
the manifest and records the version and checksum in the installing
workspace's lockfile. It changes nothing else, and it grants nothing:
an installed capability is available, not approved.

Deleting this folder from a fork is expected once a real capability
exists.
