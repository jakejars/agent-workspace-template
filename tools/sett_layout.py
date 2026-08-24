#!/usr/bin/env python3
"""Sett root layout and contained-path resolution. Stdlib only."""

import os
from pathlib import Path, PurePosixPath


MEMBERS = ("workspace", "shared-context", "registry", "library")


class SettLayout:
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
            self.kind = "family"
            self.member = None

    @property
    def exact_workspace(self):
        return self.kind == "workspace"

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
