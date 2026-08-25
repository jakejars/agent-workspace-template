#!/usr/bin/env python3
"""Reject runtime names outside pointers, adapter wiring, harness seam, this
term-list gate, and markdown that declares `runtime_subject: true`. Scan
tracked and non-ignored files, including dotdirs; match case-insensitive terms
not flanked by letters. A declaring file must name a runtime; a declaration
that names none is itself a leak. Exit: 0 clean, 1 leak, 2 usage.
Usage: python3 tools/agnostic_check.py [--root <dir>]
"""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from sett_layout import SettLayout

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = SettLayout(ROOT)

POINTERS = {
    "CLAUDE.md", "GEMINI.md", "workspace/CLAUDE.md", "workspace/GEMINI.md",
}
POINTER_TEXT = (
    "Read [`AGENTS.md`](AGENTS.md) and follow it.\n"
    "This is a pinned pointer; `AGENTS.md` is authoritative.\n"
)
MAX_POINTER_BYTES = 160

ALLOWED = {
    "tools/hooks/shim.py",
    "tools/hooks/settings-example.json",
    LAYOUT.physical_rel("workspace/70_seams/harness.md"),
    "tools/agnostic_check.py",
}

VENDOR_TERMS = ["claude", "gemini", "codex", "gpt", "copilot"]

# A markdown file whose subject is the runtime says so in its own frontmatter.
# The declaration is reciprocal: it exempts the file from the scan and obliges
# it to name a runtime. Only frontmatter counts, so prose cannot forge it, and
# only `.md`, so adapter code stays on ALLOWED where the schema can see it.
DECLARATION = "runtime_subject"

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".mypy_cache", "venv"}

# Pointer filenames are exempt; prose is not.
POINTER_FILENAMES = re.compile(r"\b(CLAUDE|GEMINI)\.md\b")

# Paths may contain vendor terms; prose may not.
PATH_TOKEN = re.compile(
    r"(?:(?<![\w.:-])(?:~/|\.\.?/)|(?<![\w.:/-])/(?!/))"
    r"[^\s`'\")\]]+"
)


def allowed(rel: str) -> bool:
    return rel in ALLOWED


def declares(rel: str, text: str) -> bool:
    """True only for `<key>: true`, trailing blanks allowed, at column 0 of a
    terminated frontmatter."""
    lines = text.split("\n")
    if not rel.endswith(".md") or not lines or lines[0].strip() != "---":
        return False
    found = False
    for line in lines[1:]:
        if line.strip() == "---":
            return found
        found = found or line.rstrip() == DECLARATION + ": true"
    return False                                        # unterminated: no opt-in


def files(root: Path):
    git_env = os.environ.copy()
    for name in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX",
        "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    ):
        git_env.pop(name, None)
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, capture_output=True, check=False, env=git_env,
    )
    if listed.returncode == 0:
        for raw in sorted(path for path in listed.stdout.split(b"\0") if path):
            yield os.fsdecode(raw)
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            rel = Path(dirpath, name).relative_to(root).as_posix()
            if rel != ".git":
                yield rel


def scan(root: Path):
    pats = {t: re.compile(r"(?<![A-Za-z])" + t + r"(?![A-Za-z])", re.IGNORECASE)
            for t in VENDOR_TERMS}
    leaks = []
    for rel in files(root):
        if rel in POINTERS:
            try:
                data = (root / rel).read_bytes()
            except OSError:
                leaks.append(f"{rel}:1: pinned pointer is unreadable")
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = ""
            if len(data) > MAX_POINTER_BYTES or text != POINTER_TEXT:
                leaks.append(
                    f"{rel}:1: pinned pointer must be the canonical "
                    f"{len(POINTER_TEXT.encode('utf-8'))}-byte body"
                )
            continue
        if allowed(rel):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            leaks.append(f"{rel}:1: unreadable text; cannot prove runtime-neutral")
            continue
        hits = []
        for lineno, raw in enumerate(text.splitlines(), start=1):
            line = PATH_TOKEN.sub("", POINTER_FILENAMES.sub("", raw))
            for term, pat in pats.items():
                if pat.search(line):
                    hits.append(f"{rel}:{lineno}: vendor agent name '{term}'")
        if not declares(rel, text):
            leaks.extend(hits)
        elif not hits:
            leaks.append(f"{rel}:1: declares '{DECLARATION}: true' but names "
                         f"no runtime — drop the declaration")
    if not leaks:
        print("agnostic_check: clean — no runtime named outside the adapter layer.")
        return 0
    for line in sorted(set(leaks)):
        print(line)
    sys.stderr.write(
        f"\nagnostic_check: {len(set(leaks))} leak(s) — move runtime detail into "
        f"workspace/70_seams/harness.md or the adapter files in tools/hooks/, "
        f"or declare '{DECLARATION}: true' where the runtime is the subject.\n")
    return 1


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    args, root = list(argv), ROOT
    if "--root" in args:
        index = args.index("--root")
        if index + 1 >= len(args):
            sys.stderr.write(__doc__)
            return 2
        root = Path(args[index + 1]).resolve()
        del args[index:index + 2]
    if args:
        sys.stderr.write(__doc__)
        return 2
    return scan(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
