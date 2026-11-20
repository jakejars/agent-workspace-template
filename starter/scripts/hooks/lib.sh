# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# lib.sh: shared by the agent hooks. Each agent sends its hook event as JSON on stdin in its own
# shape; this reads it once and sets the same variables for all of them:
#   HARNESS  claude | codex | agy | qsh | other (from $AGENT_HARNESS, set in each agent's hook config;
#            qsh sends Claude Code's event shape)
#   ROOT     the project root          KIND   shell | write | other
#   CMD      the shell command         FILES  the paths a write touches, one per line
#   TEXTS    a temp file with every string the action carries (checked for private terms)
#   EVENT_JSON  the raw event
HARNESS="${AGENT_HARNESS:-claude}"
EVENT_JSON=""; [[ -t 0 ]] || EVENT_JSON="$(cat)"  # run by hand: no event
TEXTS="$(mktemp)"; trap 'rm -f "$TEXTS"' EXIT
eval "$(python3 -I -c '
import json, os, re, shlex, sys
try: d = json.loads(sys.argv[1] or "{}")
except ValueError: d = {}
if not isinstance(d, dict): d = {}
tc = d.get("toolCall") if isinstance(d.get("toolCall"), dict) else {}
name = d.get("tool_name") or d.get("toolName") or tc.get("name") or ""
inp = d.get("tool_input") or d.get("toolInput") or d.get("input") or tc.get("args") or {}
if isinstance(inp, str):
    try: inp = json.loads(inp)
    except ValueError: inp = {"command": inp}
if not isinstance(inp, dict): inp = {}
cmd = inp.get("command") or inp.get("CommandLine") or inp.get("cmd") or ""
if isinstance(cmd, list): cmd = " ".join(map(str, cmd))
files = [inp.get(k) for k in ("file_path", "path", "filePath", "TargetFile", "notebook_path")]
files += [e.get("file_path") for e in inp.get("edits") or [] if isinstance(e, dict)]
patch = inp.get("patch") or inp.get("input") or (cmd if "*** Begin Patch" in str(cmd) else "")
files += re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", str(patch), re.M)
files = [f.strip() for f in files if isinstance(f, str) and f.strip()]
if "*** Begin Patch" in str(cmd): cmd = ""
kind = "shell" if cmd else ("write" if files else "other")
def strings(x):
    if isinstance(x, str): yield x
    elif isinstance(x, dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x, list):
        for v in x: yield from strings(v)
with open(sys.argv[2], "w") as f: f.write("\n".join(strings(inp)))
ws = d.get("workspacePaths") or []
cwd = d.get("cwd") or inp.get("Cwd") or (ws[0] if ws else "") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
for k, v in (("TOOL", name), ("KIND", kind), ("CMD", cmd), ("FILES", "\n".join(files)), ("START", cwd)):
    print(k + "=" + shlex.quote(str(v)))
' "$EVENT_JSON" "$TEXTS")"
ROOT="$(git -C "$START" rev-parse --show-toplevel 2>/dev/null || echo "$START")"
cd "$ROOT" || exit 0

get() {  # get <dotted.path>: one field of the raw event
  python3 -I -c '
import json, sys
d = json.loads(sys.argv[2] or "{}")
for k in sys.argv[1].split("."):
    d = d.get(k) if isinstance(d, dict) else None
print("" if d is None else (d if isinstance(d, str) else json.dumps(d)))' "$1" "$EVENT_JSON"
}
rel() {  # rel <path>: the path relative to the project root, or empty when it is outside
  python3 -I -c '
import os, sys
p = os.path.realpath(os.path.join(sys.argv[2], os.path.expanduser(sys.argv[1]))); r = os.path.realpath(sys.argv[2])
print(os.path.relpath(p, r) if p == r or p.startswith(r + os.sep) else "")' "$1" "$ROOT"
}
private_terms() {  # private_terms <file>: line numbers in .scrub-patterns of the terms found
  [[ -f .scrub-patterns ]] || return 0  # (numbers, never the terms, so they don't spread further)
  local n=0 p
  while IFS= read -r p || [[ -n "$p" ]]; do
    n=$((n + 1)); [[ "$p" =~ ^[[:space:]]*(#|$) ]] && continue
    grep -qiF -- "$p" "$1" && echo "$n"
  done < .scrub-patterns
  return 0
}
template_owned() {  # template_owned <relative path>: true for files that template upgrades replace
  case "$1" in
    scripts/local/*|scripts/ceilings.json) return 1 ;;
    scripts/*.sh|scripts/hooks/*|scripts/TEMPLATE_VERSION|.githooks/*) return 0 ;;
  esac
  return 1
}
harness_owned() {  # harness_owned <relative path>: true for what a learning harness writes (see .harness/README.md)
  case "$1" in .harness|.harness/*) return 0 ;; esac
  return 1
}
owner_limit() {  # owner_limit <relative path>: true for the files that set the limits the gate enforces
  case "$1" in scripts/local/limits.env|scripts/ceilings.json) return 0 ;; esac
  return 1
}
section() {  # section <file> <heading>: the non-empty lines of one "## heading" section
  awk -v h="## $2" '$0 == h {on = 1; next} /^## / {on = 0} on && NF' "$1" 2>/dev/null
}
task_state() {  # active | blocked | done, from the State: line of build-notes/task.md (active when unset)
  local s; s="$(sed -n 's/^State: *\([a-z]*\).*/\1/p' build-notes/task.md 2>/dev/null | head -1)"
  case "$s" in blocked|done) echo "$s" ;; *) echo active ;; esac
}
blocked_reason() {  # the filled-in lines under "Open or risky" in task.md (placeholders in <...> skipped)
  section build-notes/task.md "Open or risky" | grep -v '^[[:space:]]*<' || true
}
say() {  # say <text>: add text to the agent's context (session start)
  if [[ "$HARNESS" == agy ]]; then
    python3 -I -c 'import json,sys; print(json.dumps({"injectSteps":[{"systemMessage":{"systemMessage":sys.argv[1]}}]}))' "$1"
  else printf '%s\n' "$1"; fi
}
block() {  # block <reason>: stop the action (or the stop) and tell the agent why
  if [[ "$HARNESS" == agy ]]; then
    local d=deny; [[ "${HOOK_EVENT:-}" == stop ]] && d=continue
    python3 -I -c 'import json,sys; print(json.dumps({"decision":sys.argv[1],"reason":sys.argv[2]}))' "$d" "$*"
    exit 0
  fi
  echo "$*" >&2; exit 2  # Claude Code and Codex: exit 2 blocks, stderr is the reason
}
