#!/usr/bin/env python3
"""Agent Workspace Template root layout and contained-path resolution. Stdlib only."""

import os
import re
import sys
from pathlib import Path, PurePosixPath


MEMBERS = ("workspace", "shared-context", "registry", "library")
PRIVATE_DIR = ".workspace-private"
# Legacy instances keep their human-managed private store until renamed.
LEGACY_PRIVATE_DIR = ".sett-private"
PRIVATE_DIRS = (PRIVATE_DIR, LEGACY_PRIVATE_DIR)
PRIVATE_CONFLICT_WARNING = (
    f"warning: both {PRIVATE_DIR}/ and {LEGACY_PRIVATE_DIR}/ exist; "
    "enforcing combined terms. To consolidate, preserve all terms in "
    f"{PRIVATE_DIR}/never-share.txt, then explicitly retire {LEGACY_PRIVATE_DIR}/."
)


def private_directories(root, *, warn=True):
    """Return every existing private store, or the default configuration path."""
    root = Path(root).resolve()
    stores = []
    for name in PRIVATE_DIRS:
        private = root / name
        try:
            private.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            # Keep inaccessible stores selected so policy loading fails closed.
            pass
        stores.append(private)
    if warn and len(stores) == 2:
        warning = PRIVATE_CONFLICT_WARNING
        for private in stores:
            try:
                warning = _redact_private_diagnostic(private, warning)
            except FileNotFoundError:
                pass
            except (OSError, UnicodeDecodeError):
                warning = (
                    "warning: both private stores exist; enforcing combined terms. "
                    "To consolidate, preserve all terms in one store, then explicitly "
                    "retire the other."
                )
        print(redact_private_diagnostic(root, warning), file=sys.stderr)
    return stores or [root / PRIVATE_DIR]


def private_directory(root, *, warn=True):
    """Preferred configuration path; confidentiality uses every private store."""
    return private_directories(root, warn=warn)[0]


def _redact_private_diagnostic(private, message):
    """Redact raw terms too: invalid configuration must not expose values."""
    text = (private / "never-share.txt").read_text(encoding="utf-8")
    terms = {line.strip() for line in text.splitlines() if line.strip()}
    if not terms:
        return message
    pattern = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
    return re.sub(pattern, "<redacted-term>", message, flags=re.IGNORECASE)


def redact_private_diagnostic(root, message):
    for private in private_directories(root, warn=False):
        try:
            message = _redact_private_diagnostic(private, message)
        except (OSError, UnicodeDecodeError):
            pass
    return message

NOT_A_WORKSPACE = (
    "this directory is not a workspace or Agent Workspace Template source checkout. Run the "
    "command from the cloned template source repository, or open an existing "
    "workspace and run `python3 tools/doctor.py`."
)


def refuse_unknown(layout, command):
    """Return an error line when `layout` did not recognize a Agent Workspace Template root.

    An unrecognized layout is never silently treated as a family checkout:
    commands that require a Agent Workspace Template root fail closed on it.
    """
    if layout.kind != "unknown":
        return None
    return f"{command}: {NOT_A_WORKSPACE}"


class WorkspaceLayout:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if (self.root / "workspace/AGENTS.md").is_file():
            self.kind = "family"
            self.member = None
        elif ((self.root / "AGENTS.md").is_file()
              and (self.root / "00_meta").is_dir()
              and (self.root / "70_seams").is_dir()):
            self.kind = "workspace"
            self.member = "workspace"
        elif (self.root / "SHARED.md").is_file():
            self.kind = "member"
            self.member = "shared-context"
        elif (self.root / "LIBRARY.md").is_file():
            self.kind = "member"
            self.member = "library"
        elif (self.root / "README.md").is_file() and not any(
                (self.root / name).is_dir() for name in MEMBERS):
            self.kind = "member"
            self.member = "registry"
        else:
            # An unrecognized layout is never silently a family checkout.
            self.kind = "unknown"
            self.member = None

    @property
    def exact_workspace(self):
        return self.kind == "workspace"

    @property
    def is_workspace_root(self):
        """True for any recognized Agent Workspace Template root: family, workspace, or member."""
        return self.kind in {"family", "workspace", "member"}

    def workspace_path(self, rel):
        """Physical path for a canonical path inside workspace/."""
        rel = self.physical_rel(rel)
        return self.root / rel

    def physical_rel(self, rel):
        """Map a canonical member-prefixed path into this root."""
        rel = str(rel).replace(os.sep, "/")
        while rel.startswith("./"):
            rel = rel[2:]
        prefix = f"{self.member}/" if self.member else ""
        if self.kind in {"workspace", "member"} and prefix and rel.startswith(prefix):
            return rel[len(prefix):]
        return rel

    def canonical_rel(self, rel):
        """Map a physical extracted-member path to its family form."""
        rel = str(rel).replace(os.sep, "/")
        if self.kind in {"workspace", "member"} and self.member:
            return f"{self.member}/{rel}"
        return rel

    def member_of(self, rel):
        """Logical member containing a physical repo-relative path."""
        if self.exact_workspace:
            first = str(rel).split("/", 1)[0]
            if first in {"doctrine", "tools", "_templates", ".githooks"}:
                return None
            if first in {"LOOP.md", "NAMESPACE.md", "LICENSE", ".gitignore"}:
                return None
            return "workspace"
        first = str(rel).split("/", 1)[0]
        if first in MEMBERS:
            return first
        return self.member if self.kind == "member" else None

    def workspace_entrance(self):
        return "AGENTS.md" if self.exact_workspace else "workspace/AGENTS.md"

    def _contained(self, rel):
        """Return (physical rel, state): found, missing, or unsafe."""
        pure = PurePosixPath(str(rel).replace(os.sep, "/"))
        if pure.is_absolute():
            return None, "unsafe"
        lexical = Path(os.path.normpath(str(self.root / Path(*pure.parts))))
        try:
            lexical.relative_to(self.root)
        except ValueError:
            return None, "unsafe"
        cursor = self.root
        try:
            for part in lexical.relative_to(self.root).parts:
                if part not in os.listdir(cursor):
                    return None, "missing"
                candidate = cursor / part
                if candidate.is_symlink():
                    try:
                        candidate.resolve(strict=True).relative_to(self.root)
                    except (OSError, RuntimeError, ValueError):
                        return None, "unsafe"
                cursor = candidate
        except OSError:
            return None, "missing"
        if not lexical.exists():
            return None, "missing"
        try:
            resolved = lexical.resolve(strict=True)
            resolved.relative_to(self.root)
        except (OSError, RuntimeError, ValueError):
            return None, "unsafe"
        return lexical.relative_to(self.root).as_posix(), "found"

    def resolve(self, source_rel, ref):
        """Resolve a path reference without permitting root or symlink escape.

        Returns `(physical_rel, form)`; form is repo, relative, dead, or unsafe.
        Member-prefixed refs are mapped only for an extracted member.
        """
        if not ref:
            return None, "dead"
        raw = str(ref).replace("\\", "/")
        if PurePosixPath(raw).is_absolute():
            return None, "unsafe"

        explicit_relative = raw == "." or raw.startswith("./") or raw.startswith("../")
        candidates = []
        if not explicit_relative:
            mapped = self.physical_rel(raw)
            candidates.append((mapped, "repo"))
        base = PurePosixPath(str(source_rel).replace(os.sep, "/")).parent
        candidates.append((str(base / raw), "relative"))

        saw_unsafe = False
        seen = set()
        for candidate, form in candidates:
            normalized = candidate.replace("\\", "/")
            key = (normalized, form)
            if key in seen:
                continue
            seen.add(key)
            found, state = self._contained(normalized)
            if state == "found":
                return found, form
            if state == "unsafe":
                saw_unsafe = True
        return None, "unsafe" if saw_unsafe else "dead"
