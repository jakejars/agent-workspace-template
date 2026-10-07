#!/usr/bin/env python3
"""Validate schema-driven OKF frontmatter and build query catalogs.

Usage:
  python3 tools/build_catalog.py            validate + write CATALOG.md/.json
  python3 tools/build_catalog.py --check    validate source; write nothing
  python3 tools/build_catalog.py --stale    list entries past review_after
  python3 tools/build_catalog.py --help     this text

Exit codes: 0 clean, 1 violations, 2 usage. `doctrine/schema.json` owns field,
type, filing, default, and limit rules. Family-specific graph, token, boot, and
checksum contracts remain here. Missing inputs fail closed. Stdlib only.
"""

import datetime
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
from workspace_layout import WorkspaceLayout, refuse_unknown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = WorkspaceLayout(ROOT)
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "outputs", "work", "artifacts"}
SCHEMA_PATH = os.path.join(ROOT, "doctrine", "schema.json")


def load_schema():
    """Load the sole executable OKF rule source; report, never guess."""
    try:
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, ("doctrine/schema.json: unreadable canonical schema "
                    f"({exc.__class__.__name__}: {exc})")
    if not isinstance(schema, dict):
        return {}, "doctrine/schema.json: canonical schema must be an object"
    required = ("version", "required_fields", "defaults", "limits", "formats",
                "fields", "field_kinds", "type_fields", "filing",
                "constraints", "stale", "uncapped")
    missing = [key for key in required if key not in schema]
    if missing:
        return schema, ("doctrine/schema.json: canonical schema missing keys: "
                        + ", ".join(missing))

    def problem(message):
        return schema, "doctrine/schema.json: " + message

    for key in ("defaults", "limits", "formats", "fields", "type_fields",
                "filing", "uncapped"):
        if not isinstance(schema[key], dict):
            return problem(f"{key} must be an object")
    for key in ("required_fields", "field_kinds", "constraints"):
        if not isinstance(schema[key], list):
            return problem(f"{key} must be a list")
    if not isinstance(schema["version"], str) or not schema["version"]:
        return problem("version must be a non-empty string")
    for key in ("required_fields", "field_kinds"):
        if not all(isinstance(value, str) and value for value in schema[key]):
            return problem(f"{key} must be a list of non-empty strings")

    missing_defaults = [key for key in ("load", "tokens")
                        if key not in schema["defaults"]]
    if missing_defaults:
        return schema, ("doctrine/schema.json: canonical schema missing "
                        "materialized defaults: " + ", ".join(missing_defaults))
    if not isinstance(schema["defaults"]["load"], str):
        return problem("defaults.load must be a string")
    if not isinstance(schema["defaults"]["tokens"], bool):
        return problem("defaults.tokens must be a boolean")

    for key in (
        "description_chars", "prose_lines", "prose_chars",
        "boot_static_chars", "boot_dynamic_chars", "boot_total_chars",
        "handover_chars",
    ):
        value = schema["limits"].get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            return problem(f"limits.{key} must be a positive integer")

    for name, rule in schema["formats"].items():
        if not isinstance(name, str) or not isinstance(rule, dict):
            return problem(f"formats.{name} must be an object")
        for key in ("pattern", "message"):
            if not isinstance(rule.get(key), str) or not rule[key]:
                return problem(f"formats.{name}.{key} must be a non-empty string")
        try:
            re.compile(rule["pattern"])
        except re.error as exc:
            return problem(f"formats.{name}.pattern is invalid ({exc})")
        parser = rule.get("parse")
        if parser is not None:
            if not isinstance(parser, dict):
                return problem(f"formats.{name}.parse must be an object")
            for key in ("kind", "pattern"):
                if not isinstance(parser.get(key), str) or not parser[key]:
                    return problem(
                        f"formats.{name}.parse.{key} must be a non-empty string"
                    )
            if parser.get("result", "date") not in ("date", "datetime"):
                return problem(f"formats.{name}.parse.result must be date or datetime")

    def field_rule_problem(label, rule):
        if not isinstance(rule, dict):
            return f"{label} must be an object"
        for key in (
            "kind", "format", "pattern", "routing_pattern",
            "routing_ref_pattern", "message",
        ):
            if key in rule and not isinstance(rule[key], str):
                return f"{label}.{key} must be a string"
        for key in ("values", "routing_ref_forms", "relationship_values"):
            if key in rule and (not isinstance(rule[key], list)
                    or not all(isinstance(value, str) for value in rule[key])):
                suffix = (
                    "; stale exclude_statuses requires a status vocabulary"
                    if label == "fields.status" and key == "values" else ""
                )
                return f"{label}.{key} must be a list of strings{suffix}"
        for key in ("pattern", "routing_pattern", "routing_ref_pattern"):
            if key in rule:
                try:
                    re.compile(rule[key])
                except re.error as exc:
                    return f"{label}.{key} is invalid ({exc})"
        return None

    for name, rule in schema["fields"].items():
        if not isinstance(name, str) or not name:
            return problem("fields keys must be non-empty strings")
        issue = field_rule_problem(f"fields.{name}", rule)
        if issue:
            return problem(issue)

    for name, rule in schema["type_fields"].items():
        if not isinstance(name, str) or not isinstance(rule, dict):
            return problem(f"type_fields.{name} must be an object")
        fields = rule.get("fields", {})
        if not isinstance(fields, dict):
            return problem(f"type_fields.{name}.fields must be an object")
        for field, field_rule in fields.items():
            issue = field_rule_problem(
                f"type_fields.{name}.fields.{field}", field_rule
            )
            if issue:
                return problem(issue)
        for key in ("required", "required_all", "body_keys", "headings"):
            if key not in rule:
                continue
            if (not isinstance(rule[key], list)
                    or not all(isinstance(value, str) for value in rule[key])):
                return problem(f"type_fields.{name}.{key} must be a list of strings")
            if not rule[key]:
                return problem(f"type_fields.{name}.{key} must not be empty — "
                               "an empty list silently disables the check it drives")
        required_when = rule.get("required_when", {})
        if not isinstance(required_when, dict) or not all(
                isinstance(values, list)
                and all(isinstance(value, str) for value in values)
                for values in required_when.values()):
            return problem(f"type_fields.{name}.required_when must map to string lists")
        if any(isinstance(values, list) and not values
               for values in required_when.values()):
            return problem(f"type_fields.{name}.required_when must map to "
                           "non-empty string lists")

    filing = schema["filing"]
    for key, expected in {
        "chambers": list,
        "type_chambers": dict,
        "universal_types": list,
        "library": dict,
        "registry_allowed_types": list,
        "shared_context": dict,
    }.items():
        if not isinstance(filing.get(key), expected):
            label = "an object" if expected is dict else "a list"
            return problem(f"filing.{key} must be {label}")
    for key in ("chambers", "universal_types", "registry_allowed_types"):
        if not all(isinstance(value, str) for value in filing[key]):
            return problem(f"filing.{key} must be a list of strings")
    if not all(isinstance(key, str) and isinstance(value, str)
               for key, value in filing["type_chambers"].items()):
        return problem("filing.type_chambers must map strings to strings")
    library = filing["library"]
    for key, expected in (("types", list), ("family_prefix", str),
                          ("standalone_prefix", str)):
        if not isinstance(library.get(key), expected):
            label = "a list" if expected is list else "a string"
            return problem(f"filing.library.{key} must be {label}")
    if not all(isinstance(value, str) for value in library["types"]):
        return problem("filing.library.types must be a list of strings")
    shared = filing["shared_context"]
    if not isinstance(shared.get("family_prefix"), str):
        return problem("filing.shared_context.family_prefix must be a string")
    if not isinstance(shared.get("bindings"), list) or not all(
            isinstance(binding, dict)
            and isinstance(binding.get("pattern"), str)
            and isinstance(binding.get("types"), list)
            and all(isinstance(value, str) for value in binding["types"])
            for binding in shared.get("bindings", ())):
        return problem(
            "filing.shared_context.bindings must be pattern/string-list objects"
        )
    for index, binding in enumerate(shared["bindings"]):
        try:
            re.compile(binding["pattern"])
        except re.error as exc:
            return problem(
                f"filing.shared_context.bindings[{index}].pattern is invalid ({exc})"
            )

    for index, rule in enumerate(schema["constraints"]):
        if not isinstance(rule, dict):
            return problem(f"constraints[{index}] must be an object")
        for key in ("if", "then"):
            if not isinstance(rule.get(key), dict):
                return problem(f"constraints[{index}].{key} must be an object")
            if (not isinstance(rule[key].get("field"), str)
                    or not rule[key]["field"]):
                return problem(
                    f"constraints[{index}].{key}.field must be a non-empty string"
                )
        if "message" in rule and not isinstance(rule["message"], str):
            return problem(f"constraints[{index}].message must be a string")

    for key in ("types", "path_fragments"):
        value = schema["uncapped"].get(key)
        if not isinstance(value, list) or not all(
                isinstance(item, str) for item in value):
            return problem(f"uncapped.{key} must be a list of strings")

    stale = schema["stale"]
    if not isinstance(stale, dict):
        return schema, "doctrine/schema.json: stale must be an object"
    stale_keys = ("field", "comparison", "exclude_statuses",
                  "exclude_path_prefixes")
    missing_stale = [key for key in stale_keys if key not in stale]
    if missing_stale:
        return schema, ("doctrine/schema.json: stale missing keys: "
                        + ", ".join(missing_stale))
    field = stale["field"]
    if not isinstance(field, str) or not field:
        return schema, ("doctrine/schema.json: stale field must be a "
                        "non-empty string")
    fields = schema.get("fields", {})
    if (not isinstance(fields, dict) or field not in fields
            or not isinstance(fields[field], dict)):
        return schema, (f"doctrine/schema.json: stale field '{field}' is "
                        "not declared")
    format_name = fields[field].get("format") or (
        "date" if fields[field].get("kind") == "date" else ""
    )
    if not isinstance(format_name, str) or not format_name:
        return schema, (f"doctrine/schema.json: stale field '{field}' must "
                        "name a format")
    formats = schema.get("formats", {})
    format_rule = formats.get(format_name) if isinstance(formats, dict) else None
    if not isinstance(format_rule, dict):
        return schema, (f"doctrine/schema.json: stale field '{field}' names "
                        f"unknown format '{format_name}'")
    parser = format_rule.get("parse")
    if not isinstance(parser, dict):
        return schema, (f"doctrine/schema.json: stale field '{field}' format "
                        f"'{format_name}' must declare a parser object")
    if not isinstance(parser.get("kind"), str) or not parser["kind"]:
        return schema, (f"doctrine/schema.json: stale field '{field}' parser "
                        "kind must be a non-empty string")
    if parser["kind"] != "strptime":
        return schema, (f"doctrine/schema.json: stale field '{field}' names "
                        f"unsupported parser '{parser['kind']}'")
    if not isinstance(parser.get("pattern"), str) or not parser["pattern"]:
        return schema, (f"doctrine/schema.json: stale field '{field}' parser "
                        "pattern must be a non-empty string")
    comparison = stale["comparison"]
    if not isinstance(comparison, dict):
        return schema, "doctrine/schema.json: stale comparison must be an object"
    comparison_keys = ("operator", "reference")
    missing_comparison = [key for key in comparison_keys if key not in comparison]
    if missing_comparison:
        return schema, ("doctrine/schema.json: stale comparison missing keys: "
                        + ", ".join(missing_comparison))
    for key in comparison_keys:
        if not isinstance(comparison[key], str) or not comparison[key]:
            return schema, (f"doctrine/schema.json: stale comparison {key} "
                            "must be a non-empty string")
    operator, reference = comparison["operator"], comparison["reference"]
    if operator != "before" or reference != "today":
        return schema, ("doctrine/schema.json: unsupported stale comparison "
                        f"'{operator} {reference}'")
    statuses = stale["exclude_statuses"]
    if not isinstance(statuses, list) or not all(
            isinstance(value, str) for value in statuses):
        return schema, ("doctrine/schema.json: stale exclude_statuses must be "
                        "a list of strings")
    status_rule = fields.get("status", {})
    allowed_statuses = (status_rule.get("values", ())
                        if isinstance(status_rule, dict) else ())
    if not isinstance(allowed_statuses, list):
        return schema, ("doctrine/schema.json: stale exclude_statuses "
                        "requires a status vocabulary")
    for status in statuses:
        if status not in allowed_statuses:
            return schema, ("doctrine/schema.json: stale exclude_statuses "
                            f"names unknown status '{status}'")
    prefixes = stale["exclude_path_prefixes"]
    if not isinstance(prefixes, list) or not all(
            isinstance(value, str) and value for value in prefixes):
        return schema, ("doctrine/schema.json: stale exclude_path_prefixes must "
                        "be a list of non-empty strings")
    return schema, None


SCHEMA, SCHEMA_ERROR = load_schema()
if SCHEMA_ERROR:
    SCHEMA = {}
FIELD_RULES = SCHEMA.get("fields", {})
TYPE_RULES = SCHEMA.get("type_fields", {})
FILING = SCHEMA.get("filing", {})
DEFAULTS = SCHEMA.get("defaults", {})
FORMATS = SCHEMA.get("formats", {})
CONSTRAINTS = SCHEMA.get("constraints", ())
STALE_VALUE = SCHEMA.get("stale", {})
STALE = STALE_VALUE if isinstance(STALE_VALUE, dict) else {}

# Frontmatter exemptions.
EXEMPT = {"CATALOG.md", "CATALOG.json", "CLAUDE.md", "GEMINI.md",
          "LICENSE", "LICENSE.md"}
EXEMPT_PATHS = {"README.md"}
# Journal payloads are exempt; their doors are not.
JOURNAL_DIR = "30_memory/journal/"
JOURNAL_DOORS = {"INDEX.md", "README.md"}

REQUIRED = tuple(SCHEMA.get("required_fields", ()))
TYPES = set(FIELD_RULES.get("type", {}).get("values", ()))
REL_TYPES = set(FIELD_RULES.get("related", {}).get("relationship_values", ()))
RUN_DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-[a-z0-9][a-z0-9-]*$")

OKF_VERSION = str(SCHEMA.get("version", ""))

# Edge keys require a governing door declaration.
CORE_KEYS = set(FIELD_RULES)
FIELD_KINDS = set(SCHEMA.get("field_kinds", ()))
DOOR_NAMES = {"INDEX.md", "README.md"}

# --- schema-derived filing ------------------------------------------------
TYPE_CHAMBER = dict(FILING.get("type_chambers", {}))
UNIVERSAL_TYPES = set(FILING.get("universal_types", ()))
CHAMBER_DIRS = set(FILING.get("chambers", ()))

# Library types bind by tree prefix rather than chamber segment.
LIBRARY_TYPES = set(FILING.get("library", {}).get("types", ()))
LIBRARY_TREE = FILING.get("library", {}).get("family_prefix", "")
STANDALONE_LIBRARY_TREE = FILING.get("library", {}).get("standalone_prefix", "")
REGISTRY_TYPES = set(FILING.get("registry_allowed_types", ()))
SHARED_FILING = FILING.get("shared_context", {})
BOOT_ENTRANCE = LAYOUT.workspace_entrance()
BOOT_MANIFEST_KEYS = (
    "boot_static", "boot_dynamic", "boot_selector", "boot_static_cap",
    "boot_dynamic_cap", "boot_total_cap",
)

PLACEHOLDERS = LAYOUT.physical_rel("workspace/00_meta/placeholders.md")
TOKEN_RE = re.compile(r"<<([^<>\n]*)>>")
METASYNTACTIC = {"TOKEN"}
# The registry names tokens without consuming them.
TOKEN_UNFLAGGED = (LAYOUT.physical_rel("workspace/00_meta/"),)

PROSE_LINES = int(SCHEMA.get("limits", {}).get("prose_lines", 0))
PROSE_CHARS = int(SCHEMA.get("limits", {}).get("prose_chars", 0))
DESCRIPTION_CHARS = int(SCHEMA.get("limits", {}).get("description_chars", 0))
BOOT_STATIC_CHARS = int(SCHEMA.get("limits", {}).get("boot_static_chars", 0))
BOOT_DYNAMIC_CHARS = int(SCHEMA.get("limits", {}).get("boot_dynamic_chars", 0))
BOOT_TOTAL_CHARS = int(SCHEMA.get("limits", {}).get("boot_total_chars", 0))
HANDOVER_CHARS = int(SCHEMA.get("limits", {}).get("handover_chars", 0))
UNCAPPED_TYPES = set(SCHEMA.get("uncapped", {}).get("types", ()))
UNCAPPED_PATHS = tuple(SCHEMA.get("uncapped", {}).get("path_fragments", ()))

SEAM_HEADINGS = tuple(TYPE_RULES.get("seam", {}).get("headings", ()))
APPROVAL_FIELDS = set(TYPE_RULES.get("approval", {}).get("body_keys", ()))

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SHA_RE = re.compile(r"\b([0-9a-f]{64})\b")


def standalone_member():
    """Member name when an extracted optional member occupies the root."""
    return LAYOUT.member if LAYOUT.kind == "member" else None


# --- io / parsing ---------------------------------------------------------

def read_text(path, errors, relpath):
    """Read a file, or record an error and return None. Never silently skips."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{relpath}: unreadable ({exc.__class__.__name__}: {exc})")
        return None


def strip_fences(text):
    """Lines with fenced-code content blanked out. Line numbers preserved."""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def parse_frontmatter(text):
    """The restricted YAML dialect of doctrine/frontmatter-spec.md.

    Handles `key: value`, folded blocks (`>`, `|`), inline lists (`[a, b]`),
    and block sequences of scalars or of flat mappings (`related:`).
    Returns a dict, or None if frontmatter is absent or unterminated.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm, i = {}, 1
    while i < len(lines):
        if lines[i].strip() == "---":
            return fm
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), re.sub(r"\s+#.*$", "", m.group(2).strip())
        if val in (">", ">-", "|", "|-"):                       # folded block
            block, i = [], i + 1
            while (i < len(lines) and lines[i].strip() != "---"
                   and (lines[i].startswith("  ") or not lines[i].strip())):
                block.append(lines[i].strip())
                i += 1
            fm[key] = " ".join(b for b in block if b)
            continue
        if val.startswith("[") and val.endswith("]"):           # inline list
            fm[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        elif val:
            fm[key] = val
        else:                                                   # block sequence
            items, i = [], i + 1
            while i < len(lines) and lines[i].strip() != "---":
                line = lines[i]
                if not line.strip():
                    i += 1
                    continue
                if not line.startswith(" "):
                    break
                line = re.sub(r"\s+#.*$", "", line)
                dash = re.match(r"^\s*-\s*(.*)$", line)
                if dash:
                    item = dash.group(1).strip()
                    kv = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", item)
                    items.append({kv.group(1): kv.group(2).strip()} if kv else item)
                elif items and isinstance(items[-1], dict):
                    kv = re.match(r"^\s*([A-Za-z][\w-]*):\s*(.*)$", line)
                    if kv:
                        items[-1][kv.group(1)] = kv.group(2).strip()
                i += 1
            fm[key] = items
            continue
        i += 1
    return None                                                 # unterminated


def content_files():
    """Every content file in the family, repo-relative, sorted."""
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith("."))
        for fname in sorted(filenames):
            if not fname.endswith(".md") or fname in EXEMPT:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fname), ROOT)
            rel = rel.replace(os.sep, "/")
            if rel == "NAMESPACE.md" and standalone_member():
                continue                       # extracted-pack root marker
            if rel in EXEMPT_PATHS and not (
                    rel == "README.md" and standalone_member() == "registry"):
                continue
            if JOURNAL_DIR in rel and fname not in JOURNAL_DOORS:
                continue                    # raw journal payload: exempt
            found.append(rel)
    return sorted(found)


def token_registry(errors):
    """Every token with a row in placeholders.md. Missing registry = error."""
    if LAYOUT.kind == "member":
        member = standalone_member()
        door = {
            "shared-context": "SHARED.md",
            "registry": "README.md",
            "library": "LIBRARY.md",
        }.get(member, "")
        text = read_text(os.path.join(ROOT, door), errors, door) if door else None
        fm = parse_frontmatter(text) if text else {}
        declared = fm.get("declared_tokens", []) if fm else []
        if not isinstance(declared, list):
            errors.append(f"{door}: declared_tokens must be a list")
            declared = []
        return set(declared), f"{door} declared_tokens"
    text = read_text(os.path.join(ROOT, PLACEHOLDERS), errors, PLACEHOLDERS)
    if text is None:
        return set(), PLACEHOLDERS
    return ({n for n in TOKEN_RE.findall(text) if n and n not in METASYNTACTIC},
            PLACEHOLDERS)


def check_tokens(rel, text, fm, registry, registry_label, errors):
    """The token contract: registered, and only where the flag says so.

    Scanned form is the well-formed `<<NAME>>`; a bare `<<` is how doctrine
    names the marker in prose and carries no fill.
    """
    names = [n for n in TOKEN_RE.findall(text) if n not in METASYNTACTIC]
    if not names:
        return
    if (str(fm["tokens"]).lower() != "true"
            and not rel.startswith(TOKEN_UNFLAGGED)):
        errors.append(f"{rel}: holds {', '.join('<<%s>>' % n for n in sorted(set(names)))} "
                      f"but does not declare 'tokens: true' — the angle-bracket "
                      f"form triggers token semantics; declare the flag, use a "
                      f"{{{{marker}}}} for a per-artefact fill, or refer to the "
                      f"token by its bare name in prose (placeholders.md)")
    for name in sorted(set(names)):
        if name not in registry:
            errors.append(f"{rel}: <<{name}>> has no row in {registry_label} — "
                          "register it there or use a {{marker}} for a "
                          "per-artefact runtime fill")


def resolve_ref(rel, ref, ids):
    """Resolve a `related.ref` / `supersedes` target.

    Returns (repo-relative path or None, form) where form is one of:
    'id', 'repo' (repo-relative path — the spec's form), 'relative'
    (resolves only against the citing file's directory), 'text' (free
    prose naming something outside the repo), 'unsafe', or 'dead'.
    """
    if not ref:
        return None, "dead"
    normalized_ref = ref.replace("\\", "/")
    if (normalized_ref.startswith("/")
            or normalized_ref.startswith("./")
            or normalized_ref.startswith("../")):
        return LAYOUT.resolve(rel, ref)
    if " " in ref or "(" in ref:
        return None, "text"
    if ref in ids:
        target, form = LAYOUT.resolve(rel, ids[ref])
        return (target, "id") if target else (None, form)
    return LAYOUT.resolve(rel, ref)


def chamber_of(relpath):
    """The chamber a file sits in, or None if it sits outside every chamber.

    The DEEPEST chamber segment wins: boards/ sits inside 50_registers/, and a
    board belongs to boards/ (doctrine/filing.md).
    """
    found = None
    for seg in relpath.split("/")[:-1]:
        if seg in CHAMBER_DIRS:
            found = seg
    return found


def shared_context_path(relpath):
    """Path relative to the commons root in family or extracted layout."""
    if standalone_member() == "shared-context":
        return relpath
    prefix = SHARED_FILING.get("family_prefix", "")
    if prefix and relpath.startswith(prefix):
        return relpath[len(prefix):]
    return None


def check_shared_context_filing(rel, ftype, errors):
    """Apply schema path/type bindings for the commons member."""
    member_rel = shared_context_path(rel)
    if member_rel is None:
        return False
    for binding in SHARED_FILING.get("bindings", ()):
        if re.fullmatch(binding.get("pattern", r"(?!)"), member_rel):
            allowed = binding.get("types", ())
            if ftype not in allowed:
                expectation = (f"type '{allowed[0]}'" if len(allowed) == 1
                               else f"one of {sorted(allowed)}")
                errors.append(
                    f"{rel}: shared-context path '{member_rel}' requires "
                    f"{expectation}, not '{ftype}'"
                )
            return True
    errors.append(
        f"{rel}: shared-context path '{member_rel}' has no schema filing binding"
    )
    return True


def body_of(text):
    """Everything below the closing frontmatter fence."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[i + 1:]
    return []


# --- checks ---------------------------------------------------------------

JOURNAL_NAME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}-([01]\d|2[0-3])[0-5]\d-[a-z0-9]+(-[a-z0-9]+){0,4}\.md$")
JOURNAL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]([01]\d|2[0-3]):[0-5]\d$")
JOURNAL_KINDS = ("event", "correction", "digest")
JOURNAL_KEYS = {"date", "kind", "refs"}
# A run cites an entry by name, in a link or in backticks; either way the
# filename is what makes the citation checkable.
JOURNAL_ENTRY_RE = re.compile(
    r"30_memory/journal/(\d{4}-\d{2}-\d{2}-\d{4}-[a-z0-9-]+\.md)")


def check_journal(errors, ids=()):
    """The journal's own contract (30_memory/journal/README.md).

    Entries are exempt from OKF, not from shape. The journal is the only
    truth in the workspace and every other memory file is a projection of it, so
    an entry that cannot be dated, classified, or traced is worse than no
    entry: the projection rebuilds from it silently. Doors keep the OKF
    contract and are checked as ordinary content.
    """
    journal_rel = LAYOUT.physical_rel("workspace/30_memory/journal")
    journal = LAYOUT.workspace_path("workspace/30_memory/journal")
    if not os.path.isdir(journal):
        return
    for name in sorted(os.listdir(journal)):
        if not name.endswith(".md") or name in JOURNAL_DOORS:
            continue
        rel = f"{journal_rel}/{name}"
        if not JOURNAL_NAME_RE.match(name):
            errors.append(f"{rel}: name is not YYYY-MM-DD-HHMM-slug.md with a "
                          "kebab-case slug of at most five words")
        text = read_text(os.path.join(journal, name), errors, rel)
        if text is None:
            continue
        header = parse_frontmatter(text)
        if header is None:
            errors.append(f"{rel}: missing or unterminated entry header "
                          "(`date`, `kind`, optional `refs`)")
            continue
        extra = sorted(set(header) - JOURNAL_KEYS)
        if extra:
            errors.append(f"{rel}: entry header carries {', '.join(extra)} — "
                          "an entry holds date, kind and refs and nothing more")
        date = str(header.get("date", ""))
        if not JOURNAL_DATE_RE.match(date):
            errors.append(f"{rel}: date '{date}' is not YYYY-MM-DDTHH:MM local")
        kind = header.get("kind")
        if kind not in JOURNAL_KINDS:
            errors.append(f"{rel}: kind '{kind}' is not one of "
                          f"{' | '.join(JOURNAL_KINDS)}")
        refs = header.get("refs") or []
        if isinstance(refs, str):
            refs = [r.strip() for r in refs.split(",") if r.strip()]
        if not isinstance(refs, list):
            errors.append(f"{rel}: refs must be a list of ids or repo paths")
            refs = []
        if kind == "correction" and not refs:
            errors.append(f"{rel}: a correction must ref the entry it corrects")
        for ref in refs:
            ref = str(ref)
            if "/" not in ref:
                # A bare ref names a catalogued id or a sibling entry. Entries
                # carry no id and never reach the catalog, so a correction
                # citing the entry it corrects lands here, not in resolve().
                stem = ref[:-3] if ref.endswith(".md") else ref
                if ref in ids or os.path.isfile(os.path.join(journal, f"{stem}.md")):
                    continue
                errors.append(f"{rel}: refs -> {ref} names no id and no entry")
                continue
            target, form = LAYOUT.resolve(rel, ref)
            if not target and not ref.startswith("workspace/"):
                # Entries sit inside the workspace and cite it that way as
                # often as from the repo root; both are unambiguous.
                target, form = LAYOUT.resolve(rel, f"workspace/{ref}")
            if not target:
                errors.append(f"{rel}: refs -> {ref} does not resolve ({form})")


def check_sentinel(errors):
    """`00_meta/.uninitialised` routes every session into onboarding.

    It ships with the family and is deleted at the end of the walk, so it may
    legitimately sit beside a half-filled workspace and its birth journal
    when a fill checkpoint exists. Without that checkpoint the pairing means
    the sentinel came back after the walk, rerouting future sessions.
    """
    meta_rel = LAYOUT.physical_rel("workspace/00_meta")
    sentinel = os.path.join(ROOT, meta_rel, ".uninitialised")
    journal = LAYOUT.workspace_path("workspace/30_memory/journal")
    if not os.path.isfile(sentinel) or not os.path.isdir(journal):
        return
    entries = [n for n in os.listdir(journal)
               if n.endswith(".md") and n not in JOURNAL_DOORS]
    marker = os.path.join(ROOT, meta_rel, ".initializing")
    if entries and os.path.isfile(marker):
        try:
            with open(marker, encoding="utf-8") as handle:
                state = json.load(handle)
            if (state.get("version") == 1 and state.get("state") in {"filling", "filled"}
                    and isinstance(state.get("workspace_id"), str) and state["workspace_id"]
                    and state.get("started_on")):
                return
        except (OSError, ValueError, AttributeError):
            pass
    if entries:
        errors.append(f"{meta_rel}/.uninitialised: the sentinel is back in an "
                      f"instantiated workspace ({len(entries)} journal entr"
                      f"{'y' if len(entries) == 1 else 'ies'}) — onboarding is "
                      "over; delete it (00_meta/ONBOARDING.md step 7)")


def check_run_journal(errors):
    """Every run leaves a journal trace (90_runs/INDEX.md, closing a session).

    A run that changes something and journals nothing breaks the claim that
    every memory file is a projection of the journal. Traceability counts in
    either direction: an entry whose refs land inside the run folder, or a
    run.md naming an entry that exists. Both halves demand a real filename —
    naming the journal directory is not naming an entry.
    """
    runs_rel = LAYOUT.physical_rel("workspace/90_runs")
    journal_rel = LAYOUT.physical_rel("workspace/30_memory/journal")
    runs = LAYOUT.workspace_path("workspace/90_runs")
    journal = LAYOUT.workspace_path("workspace/30_memory/journal")
    if not os.path.isdir(runs):
        return
    refs_by_entry = []
    if os.path.isdir(journal):
        for name in sorted(os.listdir(journal)):
            if not name.endswith(".md") or name in JOURNAL_DOORS:
                continue
            rel = f"{journal_rel}/{name}"
            header = parse_frontmatter(read_text(os.path.join(journal, name), [], rel) or "")
            refs = (header or {}).get("refs") or []
            if isinstance(refs, str):
                refs = [r.strip() for r in refs.split(",") if r.strip()]
            if isinstance(refs, list):
                refs_by_entry.append((rel, [str(r) for r in refs]))
    for folder in sorted(os.listdir(runs)):
        run_md = os.path.join(runs, folder, "run.md")
        if not os.path.isfile(run_md):
            continue
        rel = f"{runs_rel}/{folder}/run.md"
        cited = JOURNAL_ENTRY_RE.findall(read_text(run_md, errors, rel) or "")
        if any(os.path.isfile(os.path.join(journal, name)) for name in cited):
            continue
        if any(ref.replace("\\", "/").split("/")[-2:-1] == [folder]
               for _, refs in refs_by_entry for ref in refs):
            continue
        errors.append(f"{rel}: no journal entry — name one under "
                      f"{JOURNAL_DIR} by filename, or have an entry ref this "
                      "run folder (90_runs/INDEX.md, closing a session)")


def check_registry(errors):
    """The checksum half of the registry contract (registry/README.md).

    Per manifest.yml: `name` equals the folder name, `version` is an integer,
    every `files[].src` exists under `files/`, every file under `files/`
    appears exactly once in `files[]`, every `target` is workspace-relative,
    and every `sha256` matches the bytes at `files/<src>`.
    """
    standalone = standalone_member() == "registry"
    reg = ROOT if standalone else os.path.join(ROOT, "registry")
    if not os.path.isdir(reg):
        return 0
    checked = 0
    for name in sorted(os.listdir(reg)):
        cap = os.path.join(reg, name)
        mpath = os.path.join(cap, "manifest.yml")
        if not os.path.isfile(mpath):
            continue
        mrel = f"{name}/manifest.yml" if standalone else f"registry/{name}/manifest.yml"
        text = read_text(mpath, errors, mrel)
        if text is None:
            continue
        # A manifest is the same restricted dialect as frontmatter, without
        # the fences; wrap it so one parser serves both.
        man = parse_frontmatter(f"---\n{text}\n---\n") or {}
        if man.get("name") != name:
            errors.append(f"{mrel}: name '{man.get('name')}' does not equal the "
                          f"folder name '{name}'")
        if not str(man.get("version", "")).isdigit():
            errors.append(f"{mrel}: version '{man.get('version')}' is not an "
                          "integer (semver is rejected)")
        entries = [e for e in (man.get("files") or []) if isinstance(e, dict)]
        if not entries:
            errors.append(f"{mrel}: files[] is empty — a capability carries a payload")
        files_dir = os.path.join(cap, "files")
        on_disk = set()
        for dirpath, dirnames, filenames in os.walk(files_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                on_disk.add(os.path.relpath(os.path.join(dirpath, fname),
                                            files_dir).replace(os.sep, "/"))
        claimed = []
        for entry in entries:
            src, target = entry.get("src", ""), entry.get("target", "")
            digest = entry.get("sha256", "")
            claimed.append(src)
            if not target or target.startswith(("/", "~")) or ".." in target.split("/"):
                errors.append(f"{mrel}: target '{target}' for '{src}' is not a "
                              "safe workspace-relative path")
            fpath = os.path.normpath(os.path.join(files_dir, src))
            if not src or not os.path.isfile(fpath):
                errors.append(f"{mrel}: files[].src '{src}' is missing under files/")
                continue
            if not SHA_RE.fullmatch(str(digest)):
                errors.append(f"{mrel}: '{src}' has no valid 64-hex sha256")
                continue
            with open(fpath, "rb") as fh:
                actual = hashlib.sha256(fh.read()).hexdigest()
            checked += 1
            if actual != digest:
                errors.append(f"{mrel}: checksum mismatch for files/{src} "
                              f"(manifest {digest[:12]}…, file {actual[:12]}…)")
        for stray in sorted(on_disk - set(claimed)):
            errors.append(f"registry/{name}/files/{stray}: payload file not "
                          "listed in manifest files[] — no strays")
        for src in sorted(s for s in claimed if claimed.count(s) > 1):
            errors.append(f"{mrel}: files[].src '{src}' listed more than once")
    return checked


def parse_inline_list(val):
    """A declaration's `values:` — the inline-list form, arriving as a string."""
    if isinstance(val, list):
        return val
    val = str(val).strip()
    if val.startswith("[") and val.endswith("]"):
        return [v.strip() for v in val[1:-1].split(",") if v.strip()]
    return [val] if val else []


def materialize_defaults(fm):
    """Return metadata with conservative schema defaults applied in memory."""
    materialized = dict(fm)
    for key, value in DEFAULTS.items():
        materialized.setdefault(key, value)
    return materialized


def type_field_rules(ftype):
    return TYPE_RULES.get(ftype, {}).get("fields", {})


def parse_format_value(format_name, val):
    """Parse a schema format once for validation and typed consumers."""
    rule = FORMATS.get(format_name)
    if not isinstance(rule, dict):
        return None, f"names unknown format '{format_name}'", True
    pattern = rule.get("pattern")
    if not isinstance(pattern, str) or not pattern:
        return None, f"format '{format_name}' has no pattern", True
    try:
        matched = re.fullmatch(pattern, str(val))
    except re.error as exc:
        return None, f"format '{format_name}' has invalid pattern ({exc})", True
    if not matched:
        return None, f"is not {rule.get('message', format_name)}", False
    parser = rule.get("parse")
    if parser is None:
        return str(val), None, False
    if not isinstance(parser, dict):
        return None, f"format '{format_name}' parse rule is not an object", True
    kind = parser.get("kind")
    if kind != "strptime":
        return None, f"format '{format_name}' names unsupported parser '{kind}'", True
    parse_pattern = parser.get("pattern")
    if not isinstance(parse_pattern, str) or not parse_pattern:
        return None, f"format '{format_name}' strptime parser has no pattern", True
    try:
        parsed = datetime.datetime.strptime(str(val), parse_pattern)
        if parser.get("result", "date") == "datetime":
            return parsed, None, False
        return parsed.date(), None, False
    except ValueError:
        return None, f"is not {rule.get('message', format_name)}", False


def check_rule_value(rel, key, val, rule, errors):
    """Validate one value against a schema field rule."""
    kind = rule.get("kind", "string")
    if kind == "number":
        try:
            float(str(val))
        except (TypeError, ValueError):
            errors.append(f"{rel}: {key} '{val}' is not a number")
    elif kind == "bool" and str(val).lower() not in ("true", "false"):
        errors.append(f"{rel}: {key} '{val}' is not true/false")
    elif kind == "list" and not isinstance(val, list):
        errors.append(f"{rel}: {key} is a scalar, not a list")
    allowed = rule.get("values", ())
    if allowed and not isinstance(val, list) and str(val) not in allowed:
        errors.append(f"{rel}: {key} '{val}' not in {sorted(allowed)}")
    format_name = rule.get("format") or ("date" if kind == "date" else "")
    if format_name:
        _, problem, schema_problem = parse_format_value(format_name, val)
        if problem:
            prefix = "doctrine/schema.json: " if schema_problem else f"{rel}: "
            subject = f"field '{key}' " if schema_problem else f"{key} '{val}' "
            errors.append(prefix + subject + problem)
    pattern = rule.get("pattern")
    if pattern and not re.fullmatch(pattern, str(val)):
        errors.append(f"{rel}: {key} '{val}' does not match schema pattern")


def check_constraints(rel, fm, errors):
    """Apply schema cross-field implications."""
    for rule in CONSTRAINTS:
        premise = rule.get("if", {})
        consequence = rule.get("then", {})
        if fm.get(premise.get("field")) != premise.get("equals"):
            continue
        field = consequence.get("field")
        actual = fm.get(field)
        if "not_equals" in consequence:
            failed = actual == consequence["not_equals"]
        else:
            failed = actual != consequence.get("equals")
        if failed:
            detail = f" (is '{actual if actual is not None else ''}')" if field else ""
            errors.append(f"{rel}: {rule.get('message', 'schema constraint failed')}"
                          f"{detail}")


def check_type_fields(rel, fm, errors):
    """Apply schema-owned fields and required fields for one content type."""
    ftype = fm.get("type", "")
    rule = TYPE_RULES.get(ftype, {})
    fields = rule.get("fields", {})
    for key, field_rule in fields.items():
        if key in fm:
            check_rule_value(rel, key, fm[key], field_rule, errors)
    if fm.get("status") in ("draft", "mature"):
        for key in rule.get("required", ()):
            if not fm.get(key):
                errors.append(
                    f"{rel}: missing required field '{key}' for type '{ftype}'"
                )
    for key in rule.get("required_when", {}).get(fm.get("status"), ()):
        if not fm.get(key):
            if ftype == "seam" and key == "verified_on":
                errors.append(
                    f"{rel}: a mature seam requires verified_on — maturity "
                    "is a verification event (doctrine/seams.md)"
                )
            else:
                errors.append(
                    f"{rel}: status '{fm.get('status')}' requires field '{key}' "
                    f"for type '{ftype}'"
                )
    for key in rule.get("required_all", ()):
        if not fm.get(key):
            errors.append(
                f"{rel}: missing required field '{key}' for type '{ftype}'"
            )


def check_fields(records, errors):
    """Rule 9: extended frontmatter keys are declared, not ambient.

    A door (INDEX.md / README.md) declares the extra keys files under its
    directory may carry: name, kind, an optional closed `values` vocabulary,
    an optional `for:` type, and `required: true` (which demands `for:`).
    An undeclared key is an error; a declared one is checked against its
    kind and vocabulary; a required one must be present on every draft or
    mature file of its type under the door.
    """
    decls = []                                    # (dir, name, entry, door)
    for rec in records:
        raw = rec["fm"].get("fields")
        if raw is None:
            continue
        rel = rec["rel"]
        if os.path.basename(rel) not in DOOR_NAMES:
            errors.append(f"{rel}: `fields:` declarations live on a door "
                          "(INDEX.md / README.md), nowhere else")
            continue
        dirname = os.path.dirname(rel)
        prefix = dirname + "/" if dirname else ""
        for entry in raw if isinstance(raw, list) else []:
            if not isinstance(entry, dict) or not entry.get("name"):
                errors.append(f"{rel}: fields entry '{entry}' has no name")
                continue
            kind = entry.get("kind", "string")
            if kind not in FIELD_KINDS:
                errors.append(f"{rel}: field '{entry['name']}' kind '{kind}' "
                              f"not in {sorted(FIELD_KINDS)}")
            ftype = entry.get("for", "")
            if ftype and ftype not in TYPES:
                errors.append(f"{rel}: field '{entry['name']}' is for "
                              f"'{ftype}', not a known type")
            if str(entry.get("required", "")).lower() == "true" and not ftype:
                errors.append(f"{rel}: field '{entry['name']}' is required "
                              "but names no `for:` type to require it of")
            decls.append((prefix, entry["name"], entry, rel))

    def governing(rel, ftype, name):
        """Matching declarations, deepest prefix (longest match) first."""
        matches = [d for d in decls
                   if rel.startswith(d[0]) and d[1] == name
                   and (not d[2].get("for") or d[2].get("for") == ftype)]
        matches.sort(key=lambda d: len(d[0]), reverse=True)
        return matches

    for rec in records:
        rel, fm = rec["rel"], rec["fm"]
        ftype = fm.get("type", "")
        known = CORE_KEYS | set(type_field_rules(ftype))
        for key in sorted(set(fm) - known):
            found = governing(rel, ftype, key)
            if not found:
                errors.append(f"{rel}: frontmatter key '{key}' is undeclared "
                              "— declare it in the owning door's `fields:` "
                              "block (doctrine/frontmatter-spec.md rule 9)")
                continue
            entry, val = found[0][2], fm[key]
            field_rule = dict(entry)
            field_rule["values"] = parse_inline_list(entry.get("values", ""))
            check_rule_value(rel, key, val, field_rule, errors)

    for prefix, name, entry, door in decls:
        if str(entry.get("required", "")).lower() != "true":
            continue
        for rec in records:
            if (rec["rel"].startswith(prefix)
                    and rec["fm"].get("type") == entry.get("for")
                    and rec["fm"].get("status") in ("draft", "mature")
                    and name not in rec["fm"]):
                errors.append(f"{rec['rel']}: missing required field '{name}' "
                              f"(declared for type '{entry.get('for')}' "
                              f"in {door})")

    for rec in records:
        check_type_fields(rec["rel"], rec["fm"], errors)


def check_boot_budget(records, errors):
    """Account for the ordinary boot declared by the entrance manifest."""
    for rec in records:
        if (rec["fm"].get("type") == "handover"
                and rec["chars"] > HANDOVER_CHARS):
            errors.append(
                f"{rec['rel']}: handover is {rec['chars']} chars; cap "
                f"{HANDOVER_CHARS}"
            )
    if LAYOUT.kind == "member":
        return {
            "static": 0, "dynamic": 0, "total": 0,
            "dynamic_source": "none", "static_cap": 0,
            "dynamic_cap": 0, "total_cap": 0,
        }
    by_rel = {rec["rel"]: rec for rec in records}
    entrance = by_rel.get(BOOT_ENTRANCE)
    if entrance is None:
        errors.append(f"{BOOT_ENTRANCE}: required boot entrance is missing")
        fm = {}
    else:
        fm = entrance["fm"]
    missing = [key for key in BOOT_MANIFEST_KEYS if not fm.get(key)]
    for key in missing:
        errors.append(f"{BOOT_ENTRANCE}: missing boot manifest field '{key}'")

    static_declared = fm.get("boot_static", [])
    if not isinstance(static_declared, list):
        errors.append(f"{BOOT_ENTRANCE}: boot_static must be a list")
        static_declared = []
    static_paths = [LAYOUT.physical_rel(rel) for rel in static_declared]
    if BOOT_ENTRANCE not in static_paths:
        errors.append(f"{BOOT_ENTRANCE}: boot_static must include the entrance")
    if len(static_paths) != len(set(static_paths)):
        errors.append(f"{BOOT_ENTRANCE}: boot_static contains duplicates")

    for rec in records:
        boot_keys = [key for key in BOOT_MANIFEST_KEYS if key in rec["fm"]]
        if rec["rel"] != BOOT_ENTRANCE and boot_keys:
            errors.append(
                f"{rec['rel']}: boot manifest fields belong only on "
                f"{BOOT_ENTRANCE}: {', '.join(boot_keys)}"
            )
        if (LAYOUT.member_of(rec["rel"]) == "workspace"
                and rec["fm"].get("load") == "always"
                and rec["rel"] not in static_paths):
            errors.append(
                f"{rec['rel']}: workspace load: always is absent from "
                f"{BOOT_ENTRANCE} boot_static"
            )

    def manifest_cap(key, schema_limit):
        try:
            value = int(str(fm.get(key, "")))
            if value <= 0:
                raise ValueError
        except (TypeError, ValueError):
            if fm.get(key):
                errors.append(f"{BOOT_ENTRANCE}: {key} must be a positive integer")
            return schema_limit
        if value != schema_limit:
            errors.append(
                f"{BOOT_ENTRANCE}: {key} must equal schema limit {schema_limit}, "
                f"not {value}"
            )
        return schema_limit

    static_cap = manifest_cap("boot_static_cap", BOOT_STATIC_CHARS)
    dynamic_cap = manifest_cap("boot_dynamic_cap", BOOT_DYNAMIC_CHARS)
    total_cap = manifest_cap("boot_total_cap", BOOT_TOTAL_CHARS)

    static = []
    for rel in static_paths:
        rec = by_rel.get(rel)
        if rec is None:
            errors.append(f"{rel}: required static boot file is missing")
        else:
            static.append(rec)
            if rec["fm"].get("load") != "always":
                errors.append(f"{rel}: static boot file must declare load: always")

    dynamic_glob = LAYOUT.physical_rel(str(fm.get("boot_dynamic", "")))
    selector = str(fm.get("boot_selector", ""))
    if selector and selector not in {"latest-closed-at", "explicit-task"}:
        errors.append(f"{BOOT_ENTRANCE}: unsupported boot_selector '{selector}'")
    dynamic_re = re.compile(
        "^" + re.escape(dynamic_glob).replace(r"\*", "[^/]*") + "$"
    )
    matches = sorted(
        (rec for rec in records if dynamic_re.match(rec["rel"])),
        key=lambda rec: rec["rel"],
    )
    if selector == "explicit-task":
        for rec in matches:
            if rec["fm"].get("type") == "intent" and rec["chars"] > dynamic_cap:
                errors.append(f"{rec['rel']}: current task is {rec['chars']} chars; cap {dynamic_cap}")
        # A structural check cannot infer which task the user selected. Runtime
        # context loading checks that specific task against the same budget.
        matches = []
    handovers = []
    for rec in matches:
        rel = rec["rel"]
        valid = True
        if rec["fm"].get("type") != "handover":
            errors.append(f"{rel}: boot_dynamic match must be type 'handover'")
            valid = False
        closed_at, problem, _ = parse_format_value(
            "utc_timestamp", rec["fm"].get("closed_at", "")
        )
        if problem or not isinstance(closed_at, datetime.datetime):
            valid = False
        run_dir = rel.rsplit("/", 2)[-2]
        run_match = RUN_DIR_RE.match(run_dir)
        if run_match:
            try:
                datetime.date.fromisoformat(run_match.group(1))
            except ValueError:
                run_match = None
        if not run_match:
            errors.append(
                f"{rel}: boot_dynamic run directory '{run_dir}' must be "
                "timestamp-first YYYY-MM-DD-<slug>"
            )
            valid = False
        if rec["chars"] > dynamic_cap and rec["fm"].get("type") != "handover":
            errors.append(
                f"{rel}: dynamic candidate is {rec['chars']} chars; cap "
                f"{dynamic_cap}"
            )
        if valid:
            by_id = {r["fm"].get("id"): r for r in records}
            pending = [rec]
            seen = set()
            while pending:
                current = pending.pop()
                if current["rel"] in seen: continue
                seen.add(current["rel"])
                if current["fm"].get("type") == "intent":
                    if (current["fm"].get("lifecycle") in {"satisfied", "abandoned", "superseded"}
                            or "/satisfied/" in current["rel"]):
                        valid = False
                    continue
                for edge in current["fm"].get("related", []):
                    ref = edge.get("ref") if isinstance(edge, dict) else None
                    target = by_id.get(ref) or by_rel.get(LAYOUT.physical_rel(ref or ""))
                    if target and target["fm"].get("type") in {"run", "intent"}:
                        pending.append(target)
            if valid:
                handovers.append((closed_at, rec["rel"], rec))
    selected = max(handovers, default=(None, None, None))[-1]
    static_chars = sum(rec["chars"] for rec in static)
    dynamic_chars = selected["chars"] if selected else 0
    total_chars = static_chars + dynamic_chars

    static_listing = ", ".join(
        f"{rec['rel']} ({rec['chars']})" for rec in static
    ) or "none"
    dynamic_source = selected["rel"] if selected else "none"
    if static_chars > static_cap:
        errors.append(
            f"static boot is {static_chars} chars; cap "
            f"{static_cap}: {static_listing}"
        )
    if dynamic_chars > dynamic_cap:
        errors.append(
            f"dynamic boot is {dynamic_chars} chars; cap "
            f"{dynamic_cap}: {dynamic_source}"
        )
    if total_chars > total_cap:
        errors.append(
            f"total boot is {total_chars} chars; cap "
            f"{total_cap}: static {static_chars} + "
            f"dynamic {dynamic_chars} ({dynamic_source})"
        )
    return {
        "static": static_chars,
        "dynamic": dynamic_chars,
        "total": total_chars,
        "dynamic_source": dynamic_source,
        "static_cap": static_cap,
        "dynamic_cap": dynamic_cap,
        "total_cap": total_cap,
    }


def validate(records, errors, warnings):
    """Rules 1-7 that need the whole corpus in hand (ids, refs, budget)."""
    check_fields(records, errors)
    ids = {}
    for rec in records:
        fid = rec["fm"].get("id")
        if not isinstance(fid, str) or not fid:
            continue
        if fid in ids:
            errors.append(f"{rec['rel']}: duplicate id '{fid}' "
                          f"(also {ids[fid]}) — ids are unique repo-wide")
        else:
            ids[fid] = rec["rel"]
    # File-relative refs resolve but do not survive a move; too common to
    # report one line each, too real to drop — one aggregate line.
    relative = []

    def check(rel, ref, label):
        _, form = resolve_ref(rel, ref, ids)
        if form == "dead":
            errors.append(f"{rel}: {label} '{ref}' does not resolve")
        elif form == "unsafe":
            errors.append(
                f"{rel}: {label} '{ref}' resolves outside the workspace root"
            )
        elif form == "text":
            # Free text naming something outside the repo (a superseded
            # external standard, say). Nothing to resolve it against.
            warnings.append(f"{rel}: {label} '{ref}' is free text, not a path "
                            "or id — nothing verifies it")
        elif form == "relative":
            relative.append(f"{rel} -> {ref}")

    for rec in records:
        rel, fm = rec["rel"], rec["fm"]
        for entry in fm.get("related") or []:
            if not isinstance(entry, dict):
                errors.append(f"{rel}: related entry '{entry}' is not type/ref")
                continue
            rtype, ref = entry.get("type", ""), entry.get("ref", "")
            if rtype and rtype not in REL_TYPES:
                errors.append(f"{rel}: related type '{rtype}' not in "
                              f"{sorted(REL_TYPES)}")
            if not ref:
                errors.append(f"{rel}: related entry has no ref")
            else:
                check(rel, ref, "related ref")
        sup = fm.get("supersedes")
        if isinstance(sup, str) and sup:
            check(rel, sup, "supersedes")

        desc_rule = FIELD_RULES.get("description", {})
        route_pattern = desc_rule.get("routing_ref_pattern", "")
        try:
            route_matches = list(re.finditer(
                route_pattern, fm.get("description", "")
            )) if route_pattern else []
        except re.error as exc:
            errors.append(
                "doctrine/schema.json: description routing_ref_pattern is "
                f"invalid ({exc})"
            )
            route_matches = []
        for route_match in route_matches:
            route_ref = route_match.group(1).strip()
            _, route_form = resolve_ref(rel, route_ref, ids)
            allowed_forms = desc_rule.get("routing_ref_forms", ())
            if route_form == "unsafe":
                errors.append(
                    f"{rel}: description route '{route_ref}' resolves outside "
                    "the workspace root"
                )
            elif route_form not in allowed_forms:
                errors.append(
                    f"{rel}: description route '{route_ref}' does not resolve "
                    f"as one of {sorted(allowed_forms)}"
                )

    if relative:
        warnings.append(f"{len(relative)} refs are file-relative, not "
                        "repo-relative paths or ids, so a move breaks them: "
                        + "; ".join(relative[:3])
                        + (f"; +{len(relative) - 3} more" if len(relative) > 3 else ""))

    return check_boot_budget(records, errors)


def collect_stale(records, today, errors):
    """Return overdue records under the schema-owned stale contract."""
    field = STALE.get("field")
    field_rule = FIELD_RULES.get(field) if isinstance(field, str) else None
    if not isinstance(field_rule, dict):
        errors.append(
            f"doctrine/schema.json: stale field '{field}' is not a core field"
        )
        return []
    format_name = field_rule.get("format") or (
        "date" if field_rule.get("kind") == "date" else ""
    )
    format_rule = FORMATS.get(format_name)
    if not format_name or not isinstance(format_rule, dict):
        errors.append(
            f"doctrine/schema.json: stale field '{field}' has no known format"
        )
        return []
    parser = format_rule.get("parse")
    if not isinstance(parser, dict) or parser.get("kind") != "strptime":
        errors.append(
            f"doctrine/schema.json: stale field '{field}' format "
            f"'{format_name}' has no supported comparable parser"
        )
        return []
    comparison = STALE.get("comparison")
    if not isinstance(comparison, dict):
        errors.append("doctrine/schema.json: stale comparison is not an object")
        return []
    operator = comparison.get("operator")
    reference = comparison.get("reference")
    if operator != "before" or reference != "today":
        errors.append(
            "doctrine/schema.json: unsupported stale comparison "
            f"'{operator} {reference}'"
        )
        return []
    excluded_statuses = STALE.get("exclude_statuses", ())
    excluded_prefixes = STALE.get("exclude_path_prefixes", ())
    if (not isinstance(excluded_statuses, list)
            or not all(isinstance(value, str) for value in excluded_statuses)
            or not isinstance(excluded_prefixes, list)
            or not all(isinstance(value, str) for value in excluded_prefixes)):
        errors.append(
            "doctrine/schema.json: stale exclusions must be string lists"
        )
        return []

    stale = []
    for rec in records:
        if rec["fm"].get("status") in excluded_statuses:
            continue
        if any(rec["rel"].startswith(prefix) for prefix in excluded_prefixes):
            continue
        raw = rec["fm"].get(field)
        if raw in (None, ""):
            continue
        parsed, problem, _ = parse_format_value(format_name, raw)
        if problem:
            continue  # scan already reports this field through the same parser
        if not isinstance(parsed, datetime.date):
            errors.append(
                f"doctrine/schema.json: stale field '{field}' format "
                f"'{format_name}' does not parse to a comparable date"
            )
            return []
        if parsed < today:
            stale.append((str(raw), rec["rel"]))
    return stale


def scan(errors, warnings):
    """Per-file validation. Returns the record list."""
    records = []
    if SCHEMA_ERROR:
        errors.append(SCHEMA_ERROR)
        return records
    registry, registry_label = token_registry(errors)
    for rel in content_files():
        path = os.path.join(ROOT, rel)
        text = read_text(path, errors, rel)
        if text is None:
            continue
        parsed = parse_frontmatter(text)
        if parsed is None:
            errors.append(f"{rel}: missing or unterminated OKF frontmatter")
            continue
        fm = materialize_defaults(parsed)

        for req in REQUIRED:                                        # rule 1
            if not fm.get(req):
                errors.append(f"{rel}: missing required field '{req}'")
        ftype, status = fm.get("type", ""), fm.get("status", "")
        for key in set(fm) & set(FIELD_RULES):
            check_rule_value(rel, key, fm[key], FIELD_RULES[key], errors)
        check_constraints(rel, fm, errors)

        check_tokens(rel, text, fm, registry, registry_label, errors)

        chamber = chamber_of(rel)                                   # rule 2
        standalone = standalone_member()
        library_tree = (STANDALONE_LIBRARY_TREE
                        if standalone == "library" else LIBRARY_TREE)
        if check_shared_context_filing(rel, ftype, errors):
            pass
        elif ftype in LIBRARY_TYPES:
            # Checked first: a field/pillar INDEX.md is a library door, not a
            # chamber INDEX, so the INDEX rule below must not claim it.
            if not rel.startswith(library_tree):
                errors.append(f"{rel}: type '{ftype}' belongs under "
                              f"{library_tree}, not here (doctrine/filing.md)")
        elif os.path.basename(rel) == "INDEX.md":
            if ftype and ftype not in UNIVERSAL_TYPES:
                errors.append(f"{rel}: chamber INDEX must be type doctrine or "
                              f"register, not '{ftype}'")
        elif rel.startswith("registry/") or standalone == "registry":
            # The toolshed is not a chamber: it holds capability payloads and
            # the ledgers that track them (doctrine/filing.md, registry table).
            if ftype and ftype not in REGISTRY_TYPES:
                errors.append(f"{rel}: registry/ holds type capability (payload) "
                              f"or doctrine/register (ledgers, doors), not "
                              f"'{ftype}' (doctrine/filing.md)")
        elif chamber and ftype not in UNIVERSAL_TYPES:
            want = TYPE_CHAMBER.get(ftype)
            if want and want != chamber:
                errors.append(f"{rel}: type '{ftype}' belongs in {want}/, "
                              f"not {chamber}/ (doctrine/filing.md)")

        desc = " ".join(str(fm.get("description", "")).split())    # rule 3
        fm["description"] = desc
        desc_rule = FIELD_RULES.get("description", {})
        route_pattern = desc_rule.get("routing_pattern", "")
        if route_pattern and not re.search(route_pattern, desc):
            errors.append(
                f"{rel}: description must match "
                "'<summary>. Use when … Not for … (see …)'"
            )
        if DESCRIPTION_CHARS and len(desc) > DESCRIPTION_CHARS:
            errors.append(
                f"{rel}: normalized description is {len(desc)} chars; "
                f"schema limit is {DESCRIPTION_CHARS}"
            )

        okf = fm.get("okf")
        if okf and str(okf).strip("'\"") != OKF_VERSION:
            errors.append(f"{rel}: okf '{okf}' does not match the enforced "
                          f"contract version '{OKF_VERSION}'")

        body = body_of(text)                                        # rule 6
        if ftype == "seam" and status in ("draft", "mature"):
            headings = []
            for line in strip_fences("\n".join(body)):
                match = re.match(r"^##\s+(.+?)\s*$", line)
                if match and match.group(1) in SEAM_HEADINGS:
                    headings.append(match.group(1))
            if tuple(headings) != SEAM_HEADINGS:
                errors.append(
                    f"{rel}: open seam must carry the five required seam "
                    f"headings in order: {', '.join(SEAM_HEADINGS)}"
                )

        if ftype == "approval":
            misplaced = set()
            for line in strip_fences("\n".join(body)):
                match = re.match(r"^\s*([a-z_]+)\s*:(?:\s|$)", line)
                if match and match.group(1) in APPROVAL_FIELDS:
                    misplaced.add(match.group(1))
            if misplaced:
                errors.append(
                    f"{rel}: approval fields must be inside frontmatter, not "
                    f"the body: {', '.join(sorted(misplaced))}"
                )

        if status == "reserved":
            # Headings are scaffolding, not content; anything else is body.
            content = [ln for ln in body if ln.strip()
                       and not ln.lstrip().startswith("#")]
            if len(content) > 1:
                errors.append(f"{rel}: status: reserved holds {len(content)} "
                              "body lines — reserved scaffolding is one line max")

        n_lines = text.count("\n") + 1                              # rule 7
        capped = (ftype not in UNCAPPED_TYPES
                  and not any(p in rel for p in UNCAPPED_PATHS))
        if capped and (n_lines > PROSE_LINES or len(text) > PROSE_CHARS):
            errors.append(f"{rel}: {n_lines} lines / {len(text)} chars exceeds "
                          f"{PROSE_LINES} lines / {PROSE_CHARS} chars — split "
                          "behind an INDEX (doctrine/frontmatter-spec.md rule 7); "
                          "the cap is the retrieval chunk size, not a style nit")

        records.append({"rel": rel, "fm": fm, "chars": len(text),
                        "lines": n_lines})
    return records


# --- output ---------------------------------------------------------------

def section_of(rel):
    parts = rel.split("/")
    for i, seg in enumerate(parts[:-1]):
        if seg in CHAMBER_DIRS:
            return "/".join(parts[:i + 1])
    return "/".join(parts[:-1]) or "(root)"


def render_md(records, today, boot):
    sections = {}
    for rec in records:
        sections.setdefault(section_of(rec["rel"]), []).append(rec)
    out = [
        "# Catalog",
        "",
        "Generated by `tools/build_catalog.py` — **do not hand-edit**.",
        "One line per entry: path — description `[status/load]`. Route by",
        "description, never by folder name. `reserved` and `stub` entries are",
        "scaffolding, not knowledge; `draft` carries a caveat; only `mature` is",
        "citable. Never bulk-read `drill` entries — follow the link that names them.",
        "",
    ]
    for section in sorted(sections):
        out += [f"## {section}", ""]
        for rec in sorted(sections[section], key=lambda r: r["rel"]):
            fm = rec["fm"]
            extras = []
            if fm.get("scope"):
                extras.append(f"scope: {fm['scope']}")
            if fm.get("provenance") == "agent_proposed":
                extras.append("agent_proposed — not load-bearing")
            if str(fm["tokens"]).lower() == "true":
                extras.append("tokens")
            if str(fm.get("runtime_subject", "")).lower() == "true":
                extras.append("runtime_subject")
            if fm.get("review_after"):
                extras.append(f"review: {fm['review_after']}")
            suffix = f" ({'; '.join(extras)})" if extras else ""
            out.append(f"- [`{rec['rel']}`]({rec['rel']}) — "
                       f"{fm.get('description', '')} "
                       f"`[{fm.get('status')}/{fm['load']}]`{suffix}")
        out.append("")
    out.append(
        f"*{len(records)} entries; boot static {boot['static']}/"
        f"{boot['static_cap']}, dynamic {boot['dynamic']}/"
        f"{boot['dynamic_cap']}, total {boot['total']}/"
        f"{boot['total_cap']} chars. Generated {today.isoformat()}.*"
    )
    return "\n".join(out) + "\n"


def render_json(records, today, boot):
    entries = [{
        "path": r["rel"],
        "id": r["fm"].get("id"),
        "type": r["fm"].get("type"),
        "status": r["fm"].get("status"),
        "load": r["fm"]["load"],
        "scope": r["fm"].get("scope"),
        "owner": r["fm"].get("owner"),
        "provenance": r["fm"].get("provenance"),
        "description": r["fm"].get("description"),
        "updated": r["fm"].get("updated"),
        "review_after": r["fm"].get("review_after"),
        "tokens": str(r["fm"]["tokens"]).lower() == "true",
        "related": [e for e in (r["fm"].get("related") or [])
                    if isinstance(e, dict)],
        "lines": r["lines"],
    } for r in sorted(records, key=lambda r: r["rel"])]
    return json.dumps({"generated": today.isoformat(),
                       "boot": {
                           "static_chars": boot["static"],
                           "static_budget": boot["static_cap"],
                           "dynamic_chars": boot["dynamic"],
                           "dynamic_budget": boot["dynamic_cap"],
                           "dynamic_source": boot["dynamic_source"],
                           "total_chars": boot["total"],
                           "total_budget": boot["total_cap"],
                       },
                       "entries": entries}, indent=2, ensure_ascii=False) + "\n"


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode in ("-h", "--help"):
        print(__doc__)
        return 0
    if len(argv) > 2 or mode not in ("", "--check", "--stale"):
        sys.stderr.write(__doc__)
        return 2
    refused = refuse_unknown(LAYOUT, "build_catalog")
    if refused:
        sys.stderr.write(refused + "\n")
        return 2

    errors, warnings = [], []
    records = scan(errors, warnings)
    if SCHEMA_ERROR:
        for error in errors:
            print(f"ERROR {error}")
        print(f"\n{len(errors)} error(s), 0 warning(s) — schema rejected.")
        return 1
    boot = validate(records, errors, warnings)
    n_sums = check_registry(errors)
    check_journal(errors, {r["fm"]["id"] for r in records
                          if isinstance(r.get("fm"), dict) and r["fm"].get("id")})
    check_run_journal(errors)
    check_sentinel(errors)
    today = datetime.date.today()

    if mode == "--stale":
        stale = collect_stale(records, today, errors)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        if errors:
            print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — "
                  "stale report not produced.")
            return 1
        for due, rel in sorted(stale):
            print(f"OVERDUE since {due}: {rel}")
        print(f"{len(stale)} overdue of {len(records)} entries.")
        return 0

    md = render_md(records, today, boot)
    js = render_json(records, today, boot)
    md_path = os.path.join(ROOT, "CATALOG.md")
    js_path = os.path.join(ROOT, "CATALOG.json")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — "
              "catalogs not written.")
        return 1
    if mode == "--check":
        print(f"OK: {len(records)} entries, {n_sums} checksum(s), "
              f"{len(warnings)} warning(s); source is catalogable; "
              f"boot static {boot['static']}/{boot['static_cap']}, "
              f"dynamic {boot['dynamic']}/{boot['dynamic_cap']} "
              f"({boot['dynamic_source']}), total {boot['total']}/"
              f"{boot['total_cap']} chars.")
        return 0
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(js_path, "w", encoding="utf-8") as fh:
        fh.write(js)
    print(f"CATALOG.md + CATALOG.json written: {len(records)} entries, "
          f"{n_sums} checksum(s), {len(warnings)} warning(s), "
          f"boot static {boot['static']}/{boot['static_cap']}, "
          f"dynamic {boot['dynamic']}/{boot['dynamic_cap']} "
          f"({boot['dynamic_source']}), total {boot['total']}/"
          f"{boot['total_cap']} chars.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
