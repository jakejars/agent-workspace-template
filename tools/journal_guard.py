#!/usr/bin/env python3
"""Block mutation of existing `30_memory/journal/` entries; allow new entries.
Also blocks any agent write to `.workspace-private/` — humans edit that store
outside the runtime; agents never touch it.

Neutral stdin contract:

    {"op": "modify" | "create-or-overwrite" | "shell",
     "path": "<file>", "command": "<shell line>"}

`modify` and `create-or-overwrite` require `path`; `shell` requires `command`.
Exit: 0 allow, 2 block, 1 guard failure (fail open).
Root: `$WORKSPACE_ROOT`, then legacy `$SETT_ROOT`, then the tool location.
Use `--selftest`; runtime payload translation belongs in `tools/hooks/shim.py`.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
from workspace_layout import PRIVATE_DIRS, WorkspaceLayout

ROOT = Path(os.environ.get("WORKSPACE_ROOT") or os.environ.get("SETT_ROOT")
            or Path(__file__).resolve().parents[1])
LAYOUT = WorkspaceLayout(ROOT)
JOURNAL_ROOT = Path(LAYOUT.physical_rel("workspace/30_memory/journal"))

STRUCTURE = {"INDEX.md", "README.md", ".gitkeep"}

PRIVATE_ROOTS = tuple(Path(name) for name in PRIVATE_DIRS)

# The enforcement layer is not workspace content. An agent that can edit the
# gates, the constitution, or the onboarding sentinel can edit its way out of
# every other rule, so those three are sealed the same way the private store
# is. Family maintenance edits them from the repo, where no runtime hook runs.
SEALED = ("tools", "workspace/AGENTS.md", "workspace/00_meta/.uninitialised",
          "workspace/00_meta/.initializing", "workspace/00_meta/ready.json")

JOURNAL_PATH_RE = re.compile(r"30_memory/journal")
PRIVATE_PATH_PATTERN = "(?:" + "|".join(re.escape(name) for name in PRIVATE_DIRS) + ")"
PRIVATE_PATH_RE = re.compile(PRIVATE_PATH_PATTERN)
SEALED_PATH_RE = re.compile(r"(?:^|[\s/'\"])tools/|AGENTS\.md|\.uninitialised")
DESTRUCTIVE_CMD_RE = (
    re.compile(r"\b(rm|mv|cp|dd|truncate|shred|rsync|install|ln|sed)\b"),
    re.compile(r"\btee\b"),
)
JOURNAL_OVERWRITE_RE = re.compile(r"(?<!>)>(?!>)\s*[^|&;]*30_memory/journal")  # '>>' is fine
PRIVATE_OVERWRITE_RE = re.compile(r">>?\s*[^|&;]*" + PRIVATE_PATH_PATTERN)  # any redirect blocks


def is_journal_entry(path: str) -> bool:
    """True if `path` names an entry (not structure) inside a journal chamber."""
    raw = Path(path).expanduser()
    p = raw if raw.is_absolute() else Path(LAYOUT.physical_rel(raw.as_posix()))
    if not p.is_absolute():
        p = ROOT / p
    try:
        rel = p.resolve().relative_to(ROOT.resolve())
        rel.relative_to(JOURNAL_ROOT)
    except ValueError:
        return False
    return rel != JOURNAL_ROOT and p.name not in STRUCTURE


def is_private_path(path: str) -> bool:
    """True if `path` resolves inside the human-only `.workspace-private/` store."""
    raw = Path(path).expanduser()
    p = raw if raw.is_absolute() else ROOT / raw
    try:
        rel = p.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    return any(rel == private or private in rel.parents for private in PRIVATE_ROOTS)


def is_sealed_path(path: str) -> bool:
    """True if `path` is enforcement machinery rather than workspace content."""
    raw = Path(path).expanduser()
    p = raw if raw.is_absolute() else ROOT / Path(LAYOUT.physical_rel(raw.as_posix()))
    try:
        rel = p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return False
    for sealed in SEALED:
        sealed = LAYOUT.physical_rel(sealed)
        if rel == sealed or rel.startswith(f"{sealed}/"):
            return True
    return False


def exists(path: str) -> bool:
    raw = Path(path).expanduser()
    p = raw if raw.is_absolute() else Path(LAYOUT.physical_rel(raw.as_posix()))
    if not p.is_absolute():
        p = ROOT / p
    return p.exists()


def verdict(data: dict):
    """Return None to allow, or a block reason. Pure — the selftest drives it."""
    op = data.get("op") or ""
    path = data.get("path") or ""
    command = data.get("command") or ""

    if op in ("modify", "create-or-overwrite"):
        if path and is_private_path(path):
            return (f"Private term stores are human-only; an agent tool never writes there "
                    f"({path}).")
        if path and is_sealed_path(path):
            return (f"The gates, the entrance and the onboarding sentinel are "
                    f"human-only; an agent tool never writes there ({path}). "
                    f"Propose the change instead.")
        if path and is_journal_entry(path) and exists(path):
            return (f"30_memory/journal/ is append-only and immutable. Refusing to "
                    f"{'modify' if op == 'modify' else 'overwrite'} an existing entry "
                    f"({path}). A correction or retraction is a NEW entry.")
    elif op == "shell":
        # A tripwire, not a sandbox: shell evasion is unbounded (globs, interpreters).
        # ponytail: pattern tripwire; add a commit-time guard if evasion shows up.
        if PRIVATE_PATH_RE.search(command) and (
                any(r.search(command) for r in DESTRUCTIVE_CMD_RE)
                or PRIVATE_OVERWRITE_RE.search(command)):
            return "Private term stores are human-only; refusing a shell command that writes there."
        if SEALED_PATH_RE.search(command) and (
                any(r.search(command) for r in DESTRUCTIVE_CMD_RE)
                or re.search(r">>?\s*[^|&;]*(tools/|AGENTS\.md|\.uninitialised)",
                             command)):
            return ("Refusing a shell command that writes to the gates, the "
                    "entrance, or the onboarding sentinel — those are human-only.")
        if JOURNAL_PATH_RE.search(command) and (
                any(r.search(command) for r in DESTRUCTIVE_CMD_RE)
                or JOURNAL_OVERWRITE_RE.search(command)):
            return ("Refusing a shell command that may delete, move, or overwrite journal "
                    "entries (30_memory/journal/ is append-only). Append a NEW entry "
                    "instead ('>>' is fine).")
    return None


def staged_verdict(root: Path):
    """Block staged mutations of journal entries, using exact control names."""
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-status", "-z", "-M",
         "--diff-filter=MDRT"],
        cwd=root, capture_output=True, text=True,
    )
    if proc.returncode:
        sys.stderr.write("[journal_guard] could not read the Git index\n")
        return 1
    fields = proc.stdout.split("\0")
    journals = (PurePosixPath("workspace/30_memory/journal"),
                PurePosixPath("30_memory/journal"))
    blocked = []
    i = 0
    while i < len(fields) and fields[i]:
        status = fields[i]
        i += 1
        count = 2 if status.startswith(("R", "C")) else 1
        paths = fields[i:i + count]
        i += count
        for path in paths:
            # Git paths use the family or extracted root, regardless of worktree.
            rel = PurePosixPath(path)
            if (rel.name not in STRUCTURE
                    and any(journal in rel.parents for journal in journals)):
                blocked.append(path)
    if not blocked:
        return 0
    for path in sorted(set(blocked)):
        sys.stderr.write(
            f"[journal_guard] {path}: staged mutation of an existing journal "
            "entry is forbidden\n"
        )
    return 2


def selftest():
    j = "workspace/30_memory/journal/2026-08-24-x.md"
    real = str(Path(__file__).resolve().parents[1] / "README.md")  # exists, unsealed
    assert is_journal_entry(j)
    assert not is_journal_entry("workspace/30_memory/journal/INDEX.md")
    assert not is_journal_entry("workspace/30_memory/facts/x.md")
    assert verdict({"op": "modify", "path": j}) is None, "absent entry = creation, allowed"
    assert verdict({"op": "modify", "path": real}) is None, "outside journal, allowed"
    assert verdict({"op": "create-or-overwrite", "path": j}) is None
    assert verdict({"op": "shell", "command": "rm workspace/30_memory/journal/a.md"})
    assert verdict({"op": "shell", "command": "echo x >> workspace/30_memory/journal/a.md"}) is None
    assert is_private_path(".workspace-private/never-share.txt")
    assert not is_private_path("workspace/AGENTS.md")
    assert verdict({"op": "modify", "path": ".workspace-private/never-share.txt"})
    assert verdict({"op": "create-or-overwrite", "path": ".workspace-private/x.txt"})
    assert verdict({"op": "shell", "command": "echo x >> .workspace-private/never-share.txt"})
    assert verdict({"op": "shell", "command": "cat .workspace-private/never-share.txt"}) is None
    assert is_sealed_path("tools/build_catalog.py")
    assert is_sealed_path("workspace/AGENTS.md")
    assert is_sealed_path("workspace/00_meta/.uninitialised")
    assert not is_sealed_path("workspace/00_meta/placeholders.md")
    assert verdict({"op": "modify", "path": "tools/test_gates.py"})
    assert verdict({"op": "create-or-overwrite", "path": "workspace/AGENTS.md"})
    assert verdict({"op": "create-or-overwrite",
                    "path": "workspace/00_meta/.uninitialised"})
    assert verdict({"op": "shell",
                    "command": "touch workspace/00_meta/.uninitialised"}) is None
    assert verdict({"op": "shell", "command": "sed -i '' s/a/b/ tools/check_loop.py"})
    assert verdict({"op": "shell", "command": "echo x > tools/check_loop.py"})
    assert verdict({"op": "shell", "command": "python3 tools/check_loop.py"}) is None
    assert verdict({"op": "unknown-op", "path": j}) is None
    # existence gate: a real file whose path sits in a journal chamber
    old = globals()["ROOT"]
    old_journal = globals()["JOURNAL_ROOT"]
    try:
        globals()["ROOT"] = Path(__file__).resolve().parent
        globals()["JOURNAL_ROOT"] = Path("30_memory/journal")
        fake = globals()["ROOT"] / globals()["JOURNAL_ROOT"] / "e.md"
        fake.parent.mkdir(parents=True, exist_ok=True)
        fake.write_text("x")
        assert verdict({"op": "modify", "path": str(fake)}), "existing entry must block"
        fake.unlink()
        fake.parent.rmdir()
        fake.parent.parent.rmdir()
    finally:
        globals()["ROOT"] = old
        globals()["JOURNAL_ROOT"] = old_journal
    print("journal_guard: selftest ok")
    return 0


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if args == ["--staged"]:
        return staged_verdict(ROOT)
    if args:
        sys.stderr.write(__doc__)
        return 1
    try:
        data = json.load(sys.stdin)
        reason = verdict(data if isinstance(data, dict) else {})
    except Exception as e:  # fail OPEN: never wedge the agent on the guard's own bug
        sys.stderr.write(f"[journal_guard] could not evaluate ({e}) — allowing (fail open)\n")
        return 1
    if reason:
        sys.stderr.write(f"[journal_guard] {reason}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
