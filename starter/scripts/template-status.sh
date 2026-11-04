#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# template-status.sh [--brief]: says whether a newer template version exists, and what it changes.
# Finds the template from TEMPLATE_DIR in scripts/local/template.env (written at setup), then
# $AGENT_WORKSPACE_TEMPLATE, then the usual checkout places. No template found: says nothing.
root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
TEMPLATE_DIR=""
[[ -f "$root/scripts/local/template.env" ]] && . "$root/scripts/local/template.env"
for d in "$TEMPLATE_DIR" "${AGENT_WORKSPACE_TEMPLATE:-}" "$HOME/Projects/agent-workspace-template" \
         "$HOME/Templates/agent-workspace-template"; do
  [[ -n "$d" && -x "$d/bin/workspace" ]] && exec "$d/bin/workspace" status "$root" "$@"
done
exit 0
