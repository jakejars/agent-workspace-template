#!/usr/bin/env python3
"""Block private terms in worktree or staged content.

Terms live in ignored `.workspace-private/never-share.txt`, one per line.
Legacy `.sett-private/never-share.txt` terms are also enforced when present.
`--staged` scans index blobs and validates staged `.gitignore` configuration;
unstaged divergence cannot affect its result. Diagnostics never print a term
or a path containing one.

usage: python3 tools/scrub_check.py [--staged] [--root <dir>]
       python3 tools/scrub_check.py --selftest
Exit: 0 clean, 1 match/config error, 2 usage.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from workspace_layout import (
    PRIVATE_DIR, PRIVATE_DIRS, WorkspaceLayout,
    private_directories, redact_private_diagnostic,
)

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = WorkspaceLayout(ROOT)
PRIVATE_TERMS = Path(".workspace-private/never-share.txt")
SENTINEL = LAYOUT.physical_rel("workspace/00_meta/.uninitialised")
RETIRED_STORE = "tools/scrub-terms.txt"
SKIP_DIRS = set(PRIVATE_DIRS) | {
    ".git", ".venv", "venv", "__pycache__",
    "node_modules", ".mypy_cache", ".workspace-cache", ".sett-cache", "work", "artifacts",
}


def git(root: Path, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=False
    )


def redact_path(path: str, patterns):
    return "<redacted-path>" if any(pat.search(path) for pat in patterns) else path


def redact_text(text: str, patterns):
    for pattern in patterns:
        text = pattern.sub("<redacted-term>", text)
    return text


def index_entries(root: Path, patterns=()):
    proc = git(root, "ls-files", "--stage", "-z")
    if proc.returncode:
        return None, "cannot read the Git index"
    entries = {}
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        try:
            head, path = raw.split(b"\t", 1)
            _mode, oid, stage = head.split(b" ", 2)
        except ValueError:
            return None, "malformed Git index entry"
        rel = os.fsdecode(path)
        if stage != b"0":
            return None, f"unmerged Git index entry: {redact_path(rel, patterns)}"
        entries[rel] = oid.decode("ascii")
    return entries, None


def index_blob(root: Path, oid: str):
    proc = git(root, "cat-file", "blob", oid)
    return proc.stdout if proc.returncode == 0 else None


def private_rule_active(text: str, directory=PRIVATE_DIR):
    """Require one auditable root ignore rule in the selected snapshot."""
    active = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line in {f"{directory}/", f"/{directory}/"}:
            active = True
        elif active and line.startswith("!"):
            active = False
    return active


def load_terms(root: Path, template_mode: bool, *, warn=True):
    terms = []
    for private in private_directories(root, warn=warn):
        store_terms, error = _load_store_terms(root, private, template_mode)
        if error:
            return None, error
        terms.extend(store_terms)
    return list(dict.fromkeys(terms)), None


def _load_store_terms(root: Path, private: Path, template_mode: bool):
    path = private / PRIVATE_TERMS.name
    rel = path.relative_to(root.resolve())
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        # An explicit human choice may declare that no literal terms exist.
        # It never overrides a present list or terms in another store.
        none = private / "no-private-terms.json"
        if none.exists():
            try:
                choice = json.loads(none.read_text(encoding="utf-8"))
                if choice == {"version": 1, "confirmed": True}:
                    return [], None
            except (OSError, ValueError):
                pass
            return None, redact_private_diagnostic(root, "invalid explicit no-private-terms declaration")
        if template_mode:
            return [], None
        return None, redact_private_diagnostic(root, f"missing ignored {rel}")
    except (OSError, UnicodeDecodeError):
        return None, redact_private_diagnostic(root, f"cannot read ignored {rel}")

    terms = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        term = raw.strip()
        if not term:
            continue
        if len(term) < 3 or term.casefold() in {
            "none", "n/a", "tbd", "todo", "unknown",
        }:
            return None, redact_private_diagnostic(root, (
                f"{rel}:{line_no}: unusable never-share term "
                "(value redacted)"
            ))
        terms.append(term)
    terms = list(dict.fromkeys(terms))
    if not terms and not template_mode:
        return None, redact_private_diagnostic(root, f"{rel} declares zero terms")
    return terms, None


def word_pattern(term: str):
    edge = (lambda c: r"\b" if c.isalnum() or c == "_" else "")
    return re.compile(edge(term[0]) + re.escape(term) + edge(term[-1]),
                      re.IGNORECASE)


def worktree_items(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath, name)
            rel = path.relative_to(root).as_posix()
            if rel == ".git":
                continue
            try:
                yield rel, path.read_bytes(), None
            except OSError:
                yield rel, None, "unreadable file"


def staged_items(root: Path, entries):
    for rel, oid in sorted(entries.items()):
        data = index_blob(root, oid)
        yield rel, data, None if data is not None else "unreadable index blob"


def scan_items(items, terms):
    pats = [word_pattern(term) for term in terms]
    hits = set()
    for rel, data, read_error in items:
        path_has_term = any(pat.search(rel) for pat in pats)
        shown = "<redacted-path>" if path_has_term else rel
        if path_has_term:
            hits.add((shown, "filename", "never-share term"))
        if read_error:
            hits.add((shown, "1", read_error))
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            hits.add((
                shown, "1",
                "tracked content must be text; keep binary media external "
                "through a seam link",
            ))
            continue
        if "\x00" in text:
            hits.add((
                shown, "1",
                "tracked content must be text; keep binary media external "
                "through a seam link",
            ))
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pat.search(line) for pat in pats):
                hits.add((shown, str(line_no), "never-share term"))

    if not hits:
        print(redact_text(
            f"scrub_check: clean — {len(terms)} private term(s), values redacted.",
            pats,
        ))
        return 0
    for path, where, message in sorted(hits):
        print(redact_text(f"{path}:{where}: {message}", pats))
    summary = (
        f"\nscrub_check: {len(hits)} hit(s) — values redacted; "
        "resolve before distribution.\n"
    )
    sys.stderr.write(redact_text(summary, pats))
    return 1


def scan(root: Path, staged: bool = False):
    root = Path(root).resolve()
    stores = private_directories(root)
    if staged:
        preliminary_terms, preliminary_error = load_terms(root, True, warn=False)
        if preliminary_error:
            sys.stderr.write(
                f"scrub_check: {preliminary_error}; values are never printed.\n"
            )
            return 1
        preliminary_patterns = [word_pattern(term) for term in preliminary_terms]
        entries, error = index_entries(root, preliminary_patterns)
        if error:
            sys.stderr.write(redact_text(
                f"scrub_check: {error}.\n", preliminary_patterns
            ))
            return 2
        if any(
            rel == directory or rel.startswith(directory + "/")
            for rel in entries
            for directory in PRIVATE_DIRS
        ):
            sys.stderr.write(redact_text(
                f"scrub_check: {PRIVATE_TERMS} must not be tracked; "
                "remove it from the index.\n",
                preliminary_patterns,
            ))
            return 1
        if RETIRED_STORE in entries:
            sys.stderr.write(redact_text(
                f"scrub_check: {RETIRED_STORE} is a retired tracked term "
                "store; remove it.\n",
                preliminary_patterns,
            ))
            return 1
        ignore_oid = entries.get(".gitignore")
        ignore = index_blob(root, ignore_oid) if ignore_oid else None
        try:
            ignore_text = ignore.decode("utf-8") if ignore is not None else ""
        except UnicodeDecodeError:
            ignore_text = ""
        for private in stores:
            if not private_rule_active(ignore_text, private.name):
                sys.stderr.write(redact_text(
                    "scrub_check: .gitignore in the Git index must contain an "
                    f"effective `{private.name}/` rule with no later negation.\n",
                    preliminary_patterns,
                ))
                return 1
        template_mode = SENTINEL in entries
        items = staged_items(root, entries)
    else:
        try:
            ignore_text = (root / ".gitignore").read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            ignore_text = ""
        for private in stores:
            if not private_rule_active(ignore_text, private.name):
                sys.stderr.write(redact_private_diagnostic(root,
                    "scrub_check: .gitignore must contain an effective "
                    f"`{private.name}/` rule with no later negation.\n"
                ))
                return 1
        template_mode = (root / SENTINEL).is_file()
        items = worktree_items(root)

    terms, error = load_terms(root, template_mode, warn=False)
    if error:
        sys.stderr.write(f"scrub_check: {error}; values are never printed.\n")
        return 1
    return scan_items(items, terms)


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".gitignore").write_text(".workspace-private/\n", encoding="utf-8")
        (root / "workspace/00_meta").mkdir(parents=True)
        (root / SENTINEL).touch()
        assert scan(root) == 0, "an uninitialised template needs no values"
        (root / SENTINEL).unlink()
        assert scan(root) == 1, "an instance with no private list fails"
        (root / PRIVATE_TERMS).parent.mkdir()
        (root / PRIVATE_TERMS).write_text(
            "zz-private-selftest\n", encoding="utf-8"
        )
        assert scan(root) == 0, "declared but unused term is clean"
        (root / "leak.md").write_text("zz-private-selftest\n", encoding="utf-8")
        assert scan(root) == 1, "an occurrence is a hit"
    print("scrub_check: selftest ok")
    return 0


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    if "--selftest" in argv:
        return selftest()
    args, root = list(argv), ROOT
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            sys.stderr.write(__doc__)
            return 2
        root = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    staged = "--staged" in args
    args = [arg for arg in args if arg != "--staged"]
    if args:
        sys.stderr.write(__doc__)
        return 2
    return scan(root, staged)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
