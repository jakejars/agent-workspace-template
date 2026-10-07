#!/usr/bin/env python3
"""Validate per-entrance reachability.

Usage:
  python3 tools/check_loop.py            run the gate
  python3 tools/check_loop.py --graph    also print each file's hop distance
  python3 tools/check_loop.py --help     this text

Exit codes: 0 = the loop closes, 1 = violations, 2 = usage error.

Checks authored Markdown/frontmatter edges, three-hop disclosure, dead links,
orphans, member boundaries, and local door listings. `lists` globs cover
convention-named children. Catalogs never enter the graph. Relative targets
resolve from the source, then the nearest `NAMESPACE.md` root. Unreadable input
fails closed. Exit: 0 clean, 1 violation, 2 usage.
"""

import collections
import functools
import os
import re
import sys
from fnmatch import fnmatch

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_catalog import (ROOT, LAYOUT, LINK_RE, EXEMPT_PATHS,  # noqa: E402
                           content_files, parse_frontmatter, read_text,
                           resolve_ref, standalone_member, strip_fences)
from workspace_layout import refuse_unknown  # noqa: E402

ENTRANCE = "workspace/AGENTS.md"
MEMBER_ENTRANCES = {
    "workspace": ENTRANCE,
    "shared-context": "shared-context/SHARED.md",
    "registry": "registry/README.md",
    "library": "library/LIBRARY.md",
}
FAMILY_ENTRANCE = "AGENTS.md"
MAX_HOPS = 3
# Directory doors.
INDEX_NAMES = ("INDEX.md", "README.md", "AGENTS.md")
LISTS_RE = re.compile(r"<!--\s*lists:\s*(\S+)\s*-->")
# A glob segment carries a literal when something survives the wildcards.
LITERAL_RE = re.compile(r"[^*?\[\]]+")


def member_of(rel):
    return LAYOUT.member_of(rel)


def entrance_for(rel):
    if LAYOUT.exact_workspace:
        return "AGENTS.md"
    standalone = standalone_member()
    if standalone:
        return {
            "shared-context": "SHARED.md",
            "registry": "README.md",
            "library": "LIBRARY.md",
        }[standalone]
    member = member_of(rel)
    return MEMBER_ENTRANCES.get(member, FAMILY_ENTRANCE)


def is_seam_route(rel):
    member = member_of(rel)
    if not member:
        return False
    inside = rel[len(member) + 1:] if rel.startswith(member + "/") else rel
    return inside == "70_seams" or inside.startswith("70_seams/")


def max_hops(rel):
    """The public disclosure bound, uniform across members."""
    return MAX_HOPS


def link_targets(rel, text):
    """(line, raw, resolved path, form) for each local link."""
    for n, line in enumerate(strip_fences(text), 1):
        for raw in LINK_RE.findall(line):
            target_text = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
            if target_text.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "<<" in target_text:
                continue                    # <<TOKEN>>: unresolvable until instantiation
            target = target_text.split("#")[0]
            if not target:
                continue
            resolved, form = LAYOUT.resolve(rel, target)
            yield n, raw, resolved, form


def build_graph(errors):
    """(edges, files) — edges maps source path -> set of target paths."""
    files = content_files()
    edges = {}
    ids = {}
    texts = {}

    sources = list(files)
    # Frontmatter-exempt files still get their links checked.
    sources += [p for p in sorted(EXEMPT_PATHS)
                if os.path.isfile(os.path.join(ROOT, p))]

    for rel in sources:
        text = read_text(os.path.join(ROOT, rel), errors, rel)
        if text is None:
            continue                        # already an error; fail closed
        texts[rel] = text
        fm = parse_frontmatter(text) or {}
        if fm.get("id"):
            ids[str(fm["id"])] = rel

    for rel, text in texts.items():
        out = edges.setdefault(rel, set())
        for n, raw, target, form in link_targets(rel, text):
            if target is None:
                if form == "unsafe":
                    errors.append(
                        f"{rel}:{n}: link resolves outside the workspace root -> {raw}"
                    )
                else:
                    errors.append(f"{rel}:{n}: dead link -> {raw}")
                continue
            source_member, target_member = member_of(rel), member_of(target)
            if (source_member and target_member
                    and source_member != target_member
                    and not is_seam_route(rel)):
                errors.append(
                    f"{rel}:{n}: cross-member link -> {target} must route "
                    "through the source member's 70_seams/"
                )
            out.add(target)
        fm = (parse_frontmatter(text) or {}) if rel in files else {}
        for entry in fm.get("related") or []:
            if not isinstance(entry, dict):
                continue
            target, _ = resolve_ref(rel, entry.get("ref", ""), ids)
            if target:
                source_member, target_member = member_of(rel), member_of(target)
                if (source_member and target_member
                        and source_member != target_member
                        and not is_seam_route(rel)):
                    errors.append(
                        f"{rel}: cross-member related ref -> {target} must route "
                        "through the source member's 70_seams/"
                    )
                out.add(target)
            # unresolvable refs are build_catalog.py's error, not this gate's

    for rel in files:                       # pattern coverage is an edge too
        lister = pattern_lister(rel)
        if lister:
            edges.setdefault(lister, set()).add(rel)
    return edges, files


def distances(edges, start):
    """Plain BFS from one entrance. Every human-authored link is one hop."""
    dist = {start: 0} if os.path.isfile(os.path.join(ROOT, start)) else {}
    queue = collections.deque(dist)
    while queue:
        node = queue.popleft()
        for target in sorted(edges.get(node, ())):
            if target not in dist:
                dist[target] = dist[node] + 1
                queue.append(target)
    return dist


def index_of(dirpath):
    """The file that is a directory's door, or None."""
    for name in INDEX_NAMES:
        rel = f"{dirpath}/{name}" if dirpath else name
        if os.path.isfile(os.path.join(ROOT, rel)):
            return rel
    return None


@functools.lru_cache(maxsize=None)
def declared_globs(index):
    """The `<!-- lists: <glob> -->` patterns an index declares."""
    return tuple(LISTS_RE.findall(
        read_text(os.path.join(ROOT, index), [], index) or ""))


def valid_glob(glob):
    """True if a `lists` glob is bounded.

    Two bounds. Segment count fixes the depth, because `glob_covers` matches
    segment by segment and one `*` never crosses a `/`. And at least one
    segment must carry a literal — `*/files/*` is anchored by `files`,
    `*.md` by its extension. A glob of pure wildcards (`*`, `*/*`, `**`)
    claims a subtree the door cannot see, which is orphan detection switched
    off rather than a listing.
    """
    segments = glob.split("/")
    return (all(segments) and "**" not in segments
            and any(LITERAL_RE.search(segment) for segment in segments))


def glob_covers(inside, glob):
    """Segment-wise match: one `*` never crosses a `/`."""
    parts, pattern = inside.split("/"), glob.split("/")
    return (len(parts) == len(pattern)
            and all(fnmatch(part, seg) for part, seg in zip(parts, pattern)))


def check_globs(files, errors):
    """Every declared `lists` glob is bounded before any of them is trusted."""
    for rel in files:
        for glob in declared_globs(rel):
            if not valid_glob(glob):
                errors.append(
                    f"{rel}:1: `<!-- lists: {glob} -->` is unbounded — a glob "
                    "matches segment-wise and at least one segment must "
                    "carry a literal; `**` and all-wildcard globs are "
                    "refused (LOOP.md, reachability)")


def pattern_lister(rel):
    """The nearest ancestor index whose declared glob covers rel, or None.

    Pattern coverage is how a directory whose contents arrive by convention —
    journal entries, run folders — lists them without a line per file. The
    declaring index both lists and reaches them: one hop, same as a link.
    An unbounded glob covers nothing; `check_globs` has already refused it.
    """
    parts = rel.split("/")
    for depth in range(len(parts) - 1, -1, -1):
        index = index_of("/".join(parts[:depth]))
        if not index or index == rel:
            continue
        inside = "/".join(parts[depth:])
        if any(glob_covers(inside, glob) for glob in declared_globs(index)
               if valid_glob(glob)):
            return index
    return None


def index_coverage(edges, files, errors):
    """LOOP.md §8: a file is listed by the index of the directory it sits in.

    The nearest index above the file, walking up — its own directory's where
    there is one (that is what makes a sub-chamber list its own contents),
    the parent's for a directory that is a single file deep. A directory's
    own door is never asked to list itself: its parent's index lists it.
    """
    for rel in files:
        if pattern_lister(rel):
            continue
        parts = rel.split("/")
        start = len(parts) - 1 if parts[-1] not in INDEX_NAMES else len(parts) - 2
        index = None
        for depth in range(start, 0, -1):
            index = index_of("/".join(parts[:depth]))
            if index and index != rel:
                break
            index = None
        if index is None:
            continue                        # root-level: the doors answer for it
        if rel not in edges.get(index, set()):
            errors.append(f"{rel}:1: not listed in {index} — every file is "
                          "linked from its directory's INDEX.md/README.md, or "
                          "covered by a `<!-- lists: <glob> -->` declared there")


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode in ("-h", "--help"):
        print(__doc__)
        return 0
    if len(argv) > 2 or mode not in ("", "--graph"):
        sys.stderr.write(__doc__)
        return 2
    refused = refuse_unknown(LAYOUT, "check_loop")
    if refused:
        sys.stderr.write(refused + "\n")
        return 2

    errors, warnings = [], []
    edges, files = build_graph(errors)
    entrances = {entrance_for(rel) for rel in files}
    for door in sorted(entrances):
        if not os.path.isfile(os.path.join(ROOT, door)):
            errors.append(f"{door}:1: missing member entrance")
    distance_maps = {door: distances(edges, door) for door in entrances}
    check_globs(files, errors)
    index_coverage(edges, files, errors)

    for rel in files:
        door = entrance_for(rel)
        dist = distance_maps[door]
        if rel not in dist:
            errors.append(f"{rel}:1: orphan — no link or related ref reaches it "
                          f"from {door}")
        elif dist[rel] > max_hops(rel):
            errors.append(f"{rel}:1: {dist[rel]} disclosure hops from the nearest "
                          f"door (max {max_hops(rel)}) — link it from a chamber INDEX")

    if mode == "--graph":
        for rel in files:
            dist = distance_maps[entrance_for(rel)]
            print(f"{dist.get(rel, '-'):>3}  {rel}")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — "
              "the loop does not close.")
        return 1
    print(f"OK: {len(files)} content files, each within 3 hops of the "
          f"nearest door; no orphans, no dead links, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
