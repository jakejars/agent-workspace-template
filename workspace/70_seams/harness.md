---
id: seam-harness
type: seam
status: stub
description: The seam to the agent runtime. Use when wiring a hook, diagnosing injected context. Not for MCP tool transports (see mcp.md).
scope: workspace
owner: human
updated: 2026-08-24
---

# Seam: harness (the agent runtime)

This seam is not open. Nothing crosses it. To open it, answer the five
questions in doctrine/seams.md from evidence.

This seam's subject is the agent runtime, so it may name one. Elsewhere a
file may too, but only by declaring `runtime_subject: true` in its
frontmatter; without that `agnostic_check.py` fails on the name.
Until it is answered, the workspace assumes no hooks fire and no
context is injected before `AGENTS.md` is read.
