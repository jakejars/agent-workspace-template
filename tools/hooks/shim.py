#!/usr/bin/env python3
"""Runtime adapter shim — the ONLY file that knows a vendor payload shape.

One runtime (Claude Code) wires its PreToolUse event to this shim; the shim
translates that runtime's hook payload into the neutral contract documented in
tools/journal_guard.py, runs the named guard in tools/, and passes stdout,
stderr and the exit code back. Policy lives in the guard, never here.

Translation (Claude Code PreToolUse → neutral contract):

    tool_name: Edit | MultiEdit | NotebookEdit  → op: modify
    tool_name: Write                            → op: create-or-overwrite
    tool_name: Bash                             → op: shell
    tool_input.file_path / .notebook_path       → path
    tool_input.command                          → command

Exit codes (typed):
  2  the guard blocked — Claude Code's own "deny" signal, passed straight through
  0  everything else, including a missing guard or a guard failure: fail OPEN,
     with the guard's advisory left on stderr

Wiring lives in .claude/settings.json — an operator-approved change; see
tools/hooks/settings-example.json.

usage: shim.py <guard-name>      # e.g. shim.py journal_guard  (payload on stdin)
"""
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]

OPS = {
    "Edit": "modify",
    "MultiEdit": "modify",
    "NotebookEdit": "modify",
    "Write": "create-or-overwrite",
    "Bash": "shell",
}


def neutral(data: dict) -> str:
    ti = data.get("tool_input") or {}
    return json.dumps({
        "op": OPS.get(data.get("tool_name") or "", ""),
        "path": ti.get("file_path") or ti.get("notebook_path") or "",
        "command": ti.get("command") or "",
    })


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: shim.py <guard-name>\n")
        return 0
    guard = TOOLS / f"{sys.argv[1]}.py"
    if not guard.is_file():
        sys.stderr.write(f"[shim] guard not found: {guard} — skipping (fail open)\n")
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    try:
        r = subprocess.run([sys.executable, str(guard)],
                           input=neutral(data if isinstance(data, dict) else {}),
                           text=True, capture_output=True)
    except Exception as e:
        sys.stderr.write(f"[shim] could not run {guard}: {e} — skipping (fail open)\n")
        return 0
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    return 2 if r.returncode == 2 else 0


if __name__ == "__main__":
    sys.exit(main())
