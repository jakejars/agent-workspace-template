#!/usr/bin/env python3
"""Validate native skills and optionally export copies to a user-chosen directory.

  python3 tools/skills.py check
  python3 tools/skills.py export --to <directory> [--trusted-only]

Gate API: check_skills(errors, layout=None) appends diagnostics and returns the
number of skill directories checked. It writes nothing and checks workspace
skills plus registry payloads marked kind: skill. Stdlib only.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
from workspace_layout import WorkspaceLayout, redact_private_diagnostic, refuse_unknown

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = WorkspaceLayout(ROOT)
PAYLOAD_DIRS = {"scripts", "references", "assets"}
MARKER = ".awt-skill-export.json"
MARKER_VERSION = 1


def _catalog():
    # Lazy import permits callers such as build_catalog to use this gate too.
    import build_catalog
    return build_catalog


def _label(path, layout):
    return path.relative_to(layout.root).as_posix()


def _symlink_ancestor(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            return candidate
    return None


def _source_mode(path, layout, errors, subject):
    try:
        return path.lstat().st_mode
    except FileNotFoundError:
        return None
    except OSError as exc:
        errors.append(f"{_label(path, layout)}: unreadable {subject} ({exc.__class__.__name__})")
        return None


def _metadata(text, rel, errors, expected_type):
    catalog = _catalog()
    fm = catalog.parse_frontmatter(text)
    if fm is None:
        errors.append(f"{rel}: missing or unterminated frontmatter")
        return None
    fm = catalog.materialize_defaults(fm)
    for key in catalog.REQUIRED:
        if not fm.get(key):
            errors.append(f"{rel}: missing required field '{key}'")
    if fm.get("type") != expected_type:
        errors.append(f"{rel}: type must be '{expected_type}'")
    for key in set(fm) & set(catalog.FIELD_RULES):
        if catalog.FIELD_RULES[key].get("kind") == "string" and not isinstance(fm[key], str):
            errors.append(f"{rel}: {key} must be a scalar string")
        catalog.check_rule_value(rel, key, fm[key], catalog.FIELD_RULES[key], errors)
    for key, rule in catalog.type_field_rules(expected_type).items():
        if key in fm and rule.get("kind") == "string" and not isinstance(fm[key], str):
            errors.append(f"{rel}: {key} must be a scalar string")
    catalog.check_type_fields(rel, fm, errors)
    catalog.check_constraints(rel, fm, errors)
    raw_description = fm.get("description", "")
    if expected_type == "skill" and isinstance(raw_description, str) and len(raw_description) > 1024:
        errors.append(f"{rel}: Agent Skills description exceeds 1024 characters")
    description = " ".join(str(raw_description).split())
    fm["description"] = description
    rule = catalog.FIELD_RULES.get("description", {})
    if rule.get("routing_pattern") and not re.search(rule["routing_pattern"], description):
        errors.append(f"{rel}: description must contain 'Use when … Not for … (see …)'")
    if len(description) > catalog.DESCRIPTION_CHARS:
        errors.append(f"{rel}: description is {len(description)} chars; schema limit is "
                      f"{catalog.DESCRIPTION_CHARS}")
    okf = fm.get("okf")
    if okf and str(okf).strip("'\"") != catalog.OKF_VERSION:
        errors.append(f"{rel}: okf does not match contract version '{catalog.OKF_VERSION}'")
    return fm


def _skill(path, name, layout, errors):
    """Validate one source and capture exactly the bytes that export may copy."""
    rel = _label(path, layout)
    _catalog().check_rule_value(rel, "name", name,
                               _catalog().type_field_rules("skill").get("name", {}), errors)
    if _symlink_ancestor(path):
        errors.append(f"{rel}: skill source has a symlink ancestor")
        return None
    payload = {}
    def walk_error(exc):
        raise exc
    try:
        for entry in sorted(path.iterdir()):
            if entry.name == "SKILL.md":
                if entry.is_symlink() or not entry.is_file():
                    errors.append(f"{rel}/SKILL.md: must be a regular file, never a symlink")
                continue
            if entry.name not in PAYLOAD_DIRS or not entry.is_dir():
                errors.append(f"{rel}/{entry.name}: only SKILL.md and scripts/, references/, assets/ are allowed")
        for base, dirs, files in os.walk(path, followlinks=False, onerror=walk_error):
            for filename in sorted(dirs + files):
                source = Path(base, filename)
                mode = source.lstat().st_mode
                if source.is_symlink():
                    errors.append(f"{_label(source, layout)}: symlinks are forbidden in skills")
                elif stat.S_ISREG(mode):
                    payload[source.relative_to(path).as_posix()] = (source.read_bytes(), stat.S_IMODE(mode))
                elif not stat.S_ISDIR(mode):
                    errors.append(f"{_label(source, layout)}: skill payload must contain regular files")
    except OSError as exc:
        errors.append(f"{rel}: unreadable skill ({exc.__class__.__name__})")
        return None
    if "SKILL.md" not in payload:
        errors.append(f"{rel}: missing regular SKILL.md")
        return None
    try:
        text = payload["SKILL.md"][0].decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"{rel}/SKILL.md: must be UTF-8 text")
        return None
    fm = _metadata(text, rel + "/SKILL.md", errors, "skill")
    if fm is None:
        return None
    if fm.get("name") != name:
        errors.append(f"{rel}/SKILL.md: name '{fm.get('name', '')}' must equal skill directory name '{name}'")
    return {"path": path, "name": name, "fm": fm, "payload": payload}


def _discover(layout, errors):
    sources, local = [], []
    shelf = layout.workspace_path("workspace/60_capabilities/skills")
    shelf_mode = (_source_mode(shelf, layout, errors, "skill shelf")
                  if layout.kind in {"family", "workspace"} else None)
    if shelf_mode is not None:
        if stat.S_ISLNK(shelf_mode) or _symlink_ancestor(shelf):
            errors.append(f"{_label(shelf, layout)}: skill shelf has a symlink ancestor")
        elif not stat.S_ISDIR(shelf_mode):
            errors.append(f"{_label(shelf, layout)}: skill shelf must be a directory")
        else:
            try:
                children = sorted(shelf.iterdir())
            except OSError as exc:
                errors.append(f"{_label(shelf, layout)}: unreadable skill shelf ({exc.__class__.__name__})")
                children = []
            for path in children:
                mode = _source_mode(path, layout, errors, "skill source")
                if mode is None:
                    continue
                if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
                    sources.append((path, path.name, True))
                elif path.name != "README.md":
                    errors.append(f"{_label(path, layout)}: skill shelf permits only README.md and skill directories")
    registry = layout.root if layout.member == "registry" else layout.root / "registry"
    registry_mode = _source_mode(registry, layout, errors, "registry")
    if registry_mode is not None and (stat.S_ISLNK(registry_mode) or _symlink_ancestor(registry)):
        errors.append(f"{_label(registry, layout)}: registry has a symlink ancestor")
    elif registry_mode is not None and stat.S_ISDIR(registry_mode):
        try:
            capabilities = sorted(registry.iterdir())
        except OSError as exc:
            errors.append(f"{_label(registry, layout)}: unreadable registry ({exc.__class__.__name__})")
            capabilities = []
        for capability in capabilities:
            mode = _source_mode(capability, layout, errors, "registry capability")
            if mode is None or not (stat.S_ISDIR(mode) or stat.S_ISLNK(mode)):
                continue
            manifest = capability / "manifest.yml"
            mode = _source_mode(manifest, layout, errors, "manifest")
            if mode is None or not (stat.S_ISREG(mode) or stat.S_ISLNK(mode)):
                continue
            if _symlink_ancestor(manifest):
                errors.append(f"{_label(manifest, layout)}: manifest has a symlink ancestor")
                continue
            try:
                fm = _catalog().parse_frontmatter("---\n" + manifest.read_text(encoding="utf-8") + "\n---\n") or {}
            except (OSError, UnicodeDecodeError):
                errors.append(f"{_label(manifest, layout)}: unreadable manifest")
                continue
            if fm.get("kind") == "skill":
                sources.append((capability / "files", capability.name, False))
    records = []
    for path, name, is_local in sources:
        record = _skill(path, name, layout, errors)
        if record:
            records.append({"rel": _label(path / "SKILL.md", layout), "fm": record["fm"]})
            if is_local:
                local.append(record)
    # Reuse governing door declarations so extensions remain schema-governed.
    doors = {}
    for record in records:
        directory = (layout.root / record["rel"]).parent
        for ancestor in (directory, *directory.parents):
            if not ancestor.is_relative_to(layout.root):
                break
            for filename in ("INDEX.md", "README.md"):
                door = ancestor / filename
                if not door.is_file() or door in doors:
                    continue
                try:
                    fm = _catalog().parse_frontmatter(door.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError):
                    continue
                if fm:
                    doors[door] = {"rel": _label(door, layout), "fm": fm}
    _catalog().check_fields([*doors.values(), *records], errors)
    return local, len(sources)


def check_skills(errors, layout=None):
    """Append native-format/house-metadata defects; return checked directory count."""
    layout = layout or LAYOUT
    refused = refuse_unknown(layout, "skills")
    if refused:
        errors.append(refused)
        return 0
    if _catalog().SCHEMA_ERROR:
        errors.append(_catalog().SCHEMA_ERROR)
        return 0
    return _discover(layout, errors)[1]


def _ledger(layout):
    path = layout.workspace_path("workspace/60_capabilities/installed.md")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    header, rows = None, {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if {"capability", "trust", "approval"}.issubset(cells):
            header = cells
            continue
        if header is None or len(cells) != len(header) or all(re.fullmatch(r"[-:]+", cell) for cell in cells):
            continue
        row = dict(zip(header, cells))
        rows.setdefault(row["capability"], row)  # ledger is explicitly newest first
    return rows


def _trusted(record, rows, layout):
    row = rows.get(record["name"], {})
    if row.get("trust") != "trusted":
        return False
    ref = row.get("approval", "")
    link = re.fullmatch(r"\[[^\]]*\]\(([^)]+)\)", ref)
    ref = link.group(1) if link else ref.strip("`")
    source = layout.physical_rel("workspace/60_capabilities/installed.md")
    rel, form = layout.resolve(source, ref)
    if form not in {"repo", "relative"} or rel is None:
        return False
    path = layout.root / rel
    if _symlink_ancestor(path) or not path.is_file():
        return False
    errors = []
    try:
        fm = _metadata(path.read_text(encoding="utf-8"), rel, errors, "approval")
    except (OSError, UnicodeDecodeError):
        return False
    return (not errors and fm is not None and fm.get("class") == "B"
            and fm.get("status") in {"draft", "mature"})


def _marker(record, layout):
    identity = hashlib.sha256(str(layout.root).encode("utf-8")).hexdigest()
    return {"version": MARKER_VERSION, "tool": "tools/skills.py",
            "source": identity, "name": record["name"]}


def _read_marker(output):
    marker = output / MARKER
    if marker.is_symlink() or not marker.is_file():
        return None
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _export_symlink(output):
    for base, dirs, files in os.walk(output, followlinks=False):
        if any(Path(base, name).is_symlink() for name in dirs + files):
            return True
    return False


def _destination(target, records, layout, errors, trusted_only=False):
    target = Path(os.path.abspath(os.path.expanduser(target)))
    removals = []
    if _symlink_ancestor(target):
        errors.append("export destination has a symlink ancestor")
        return target, removals
    protected = [layout.root / name for name in
                 ("workspace", "shared-context", "registry", "library", "doctrine", "tools",
                  "_templates", ".git", ".githooks", ".github", ".workspace-private",
                  ".sett-private", ".workspace-cache")]
    if layout.exact_workspace:
        protected += [layout.root / chamber for chamber in _catalog().CHAMBER_DIRS]
    if (target == layout.root or layout.root.is_relative_to(target)
            or any(target.is_relative_to(path) for path in protected)
            or layout.kind == "member" and target.is_relative_to(layout.root)):
        errors.append("export destination is inside or above source chambers, members, or support paths")
    if target.exists() and not target.is_dir():
        errors.append("export destination is not a directory")
    for record in records:
        output = target / record["name"]
        if not output.exists() and not output.is_symlink():
            continue
        if output.is_symlink() or not output.is_dir():
            errors.append(f"{output}: existing export is not a regular directory")
            continue
        owned = _read_marker(output) == _marker(record, layout)
        if not owned:
            errors.append(f"{output}: ownership marker absent or different; refusing to overwrite")
        if _export_symlink(output):
            errors.append(f"{output}: existing export contains a symlink")
    if trusted_only and target.is_dir():
        selected = {record["name"] for record in records}
        for output in sorted(target.iterdir()):
            if output.name in selected or output.is_symlink() or not output.is_dir():
                continue
            if _read_marker(output) != _marker({"name": output.name}, layout):
                continue  # other sources and user-owned directories stay untouched
            if _export_symlink(output):
                errors.append(f"{output}: existing export contains a symlink")
            removals.append(output)
    return target, removals


def export(target, trusted_only=False, layout=None):
    layout = layout or LAYOUT
    errors = []
    if _catalog().SCHEMA_ERROR:
        errors.append(_catalog().SCHEMA_ERROR)
        records = []
    else:
        records, _ = _discover(layout, errors)
    selected = records
    if trusted_only:
        rows = _ledger(layout)
        selected = [record for record in records if _trusted(record, rows, layout)]
    target, removals = _destination(target, selected, layout, errors, trusted_only)
    for error in errors:
        print(redact_private_diagnostic(layout.root, error), file=sys.stderr)
    if errors:
        return 1
    import scrub_check
    template_mode = (layout.kind == "family" and
                     layout.workspace_path("workspace/00_meta/.uninitialised").is_file())
    terms, error = scrub_check.load_terms(layout.root, template_mode)
    if error:
        print(redact_private_diagnostic(layout.root, f"skills: export scrub failed: {error}"), file=sys.stderr)
        return 1
    markers = {record["name"]: (json.dumps(_marker(record, layout), sort_keys=True) + "\n").encode("utf-8")
               for record in selected}
    items = [(record["name"] + "/" + rel, data, None)
             for record in selected for rel, (data, _mode) in record["payload"].items()]
    items += [(name + "/" + MARKER, data, None) for name, data in markers.items()]
    if scrub_check.scan_items(items, terms):
        return 1
    # All format, ownership, path, and egress checks precede the first write.
    try:
        if selected:
            target.mkdir(parents=True, exist_ok=True)
        for record in selected:
            output = target / record["name"]
            temporary = Path(tempfile.mkdtemp(prefix=".awt-export-", dir=target))
            backup = temporary / ".previous"
            try:
                staged = temporary / record["name"]
                staged.mkdir()
                for rel, (data, mode) in record["payload"].items():
                    destination = staged / rel
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
                    destination.chmod(mode)
                (staged / MARKER).write_bytes(markers[record["name"]])
                if output.exists():
                    output.rename(backup)
                try:
                    staged.rename(output)
                except OSError:
                    if backup.exists():
                        backup.rename(output)
                    raise
                if backup.exists():
                    shutil.rmtree(backup)
            finally:
                # If restoring fails too, retain the backup for recovery.
                if not backup.exists():
                    shutil.rmtree(temporary)
            print(redact_private_diagnostic(layout.root, f"exported {record['name']} → {output}"))
        for output in removals:
            shutil.rmtree(output)
            print(redact_private_diagnostic(layout.root, f"removed excluded owned export {output}"))
    except OSError as exc:
        print(redact_private_diagnostic(layout.root, f"skills: export failed ({exc.__class__.__name__}): {exc}"), file=sys.stderr)
        return 1
    skipped = len(records) - len(selected)
    print(redact_private_diagnostic(layout.root, f"skills: exported {len(selected)} skill(s); skipped {skipped}; removed {len(removals)}"))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="validate skills without writing")
    output = commands.add_parser("export", help="copy skills into an optional native directory")
    output.add_argument("--to", required=True, help="destination chosen by the user")
    output.add_argument("--trusted-only", action="store_true", help="export only human-promoted trusted skills")
    args = parser.parse_args(argv)
    refused = refuse_unknown(LAYOUT, "skills")
    if refused:
        print(refused, file=sys.stderr)
        return 2
    if args.command == "export":
        if LAYOUT.kind == "member":
            print("skills: export requires a workspace or family source checkout", file=sys.stderr)
            return 2
        return export(args.to, args.trusted_only)
    errors = []
    checked = check_skills(errors)
    for error in errors:
        print(redact_private_diagnostic(ROOT, error), file=sys.stderr)
    if errors:
        return 1
    print(f"skills: checked {checked} skill(s), clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
