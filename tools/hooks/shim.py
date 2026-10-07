#!/usr/bin/env python3
"""Runtime adapter shim — the ONLY file that knows a vendor payload shape.

The optional Claude Code example translates PreToolUse to journal_guard.py
and session/prompt/write/close events to lifecycle.py. Workspace behavior lives
in those neutral tools; event names and response envelopes live here.

Translation (Claude Code PreToolUse → neutral contract):

    tool_name: Edit | MultiEdit | NotebookEdit  → op: modify
    tool_name: Write                            → op: create-or-overwrite
    tool_name: Bash                             → op: shell
    tool_input.file_path / .notebook_path       → path
    tool_input.command                          → command

Journal guard exit codes:
  2  the guard blocked — Claude Code's own "deny" signal, passed straight through
  0  everything else, including a missing guard or a guard failure: fail OPEN,
     with the guard's advisory left on stderr

Lifecycle results provide context on start/prompt. A failed Stop returns 2
once so the agent can repair it; other failures are surfaced without blocking
prompt submission or entering a stop loop. See settings-example.json for
optional project wiring; this file does not install it.

usage: shim.py journal_guard|lifecycle  (payload on stdin)
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


def lifecycle(data):
    events = {"SessionStart": "start", "UserPromptSubmit": "prompt",
              "PostToolUse": "changed", "Stop": "close", "PreCompact": "close",
              "SessionEnd": "close"}
    event = data.get("hook_event_name")
    if event not in events:
        return 0
    payload = {"event": events[event]}
    if event == "UserPromptSubmit":
        payload["query"] = data.get("prompt", "")
    result = subprocess.run([sys.executable, str(TOOLS / "lifecycle.py"), "--json"],
                            input=json.dumps(payload), text=True, capture_output=True)
    if result.returncode:
        message = (result.stderr or result.stdout)[-2000:]
        if event == "Stop" and not data.get("stop_hook_active"):
            sys.stderr.write(message)
            return 2
        if event in {"SessionStart", "UserPromptSubmit"}:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                  "additionalContext": "Workspace context validation failed; do not use stale cached context. " + message}}))
        else:
            sys.stderr.write(message)
        return 0
    if event in {"SessionStart", "UserPromptSubmit"} and result.stdout.strip():
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                          "additionalContext": result.stdout.strip()}}))
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"journal_guard", "lifecycle"}:
        sys.stderr.write("usage: shim.py journal_guard|lifecycle\n")
        return 0
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict): data = {}
    except (ValueError, OSError):
        data = {}
    if sys.argv[1] == "lifecycle":
        return lifecycle(data)
    guard = TOOLS / "journal_guard.py"
    try:
        result = subprocess.run([sys.executable, str(guard)], input=neutral(data),
                                text=True, capture_output=True)
    except OSError as exc:
        sys.stderr.write(f"[shim] guard unavailable: {exc}; staged commit gate remains required\n")
        return 0
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return 2 if result.returncode == 2 else 0


if __name__ == "__main__":
    sys.exit(main())
