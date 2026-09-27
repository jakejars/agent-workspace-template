---
id: seam-harness
type: seam
status: stub
description: The seam to the agent runtime. Use when wiring a hook, diagnosing injected context. Not for MCP tool transports (see mcp.md).
scope: workspace
owner: human
updated: 2026-09-06
---

# Seam: harness

This seam is not open. Nothing crosses it until this workspace's actual
runtime configuration is inspected. The template never claims session hooks
are installed merely because an adapter example exists.

The core protocol is agent agnostic: `tools/lifecycle.py` accepts start,
prompt, changed, close, and status, by CLI or neutral JSON. Git hooks are
installed separately using `tools/hooks/install.py`; inspect actual invocation
receipts with lifecycle status. See `doctrine/lifecycle.md` for intervals.

An optional Claude Code adapter example lives in `tools/hooks/`. To use it,
merge the example's event hooks into project settings and exercise each event.
Other runtimes call the same neutral protocol with their own adapters.

When opening this seam, answer the five questions from observed evidence:
which context crosses, its direction, the real receipts, the runtime's
configuration/disable control, and the private material excluded. Keep any
unsupported event explicitly unwired and retain the portable start/close calls.
