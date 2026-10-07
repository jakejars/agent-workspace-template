#!/usr/bin/env python3
"""Focused regressions for integrity-gate corrections."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_gates import CLEAN, TOOLS, build, run


FAKE_TERM = "zz-private-correction-term"
PRIVATE_TERMS = ".workspace-private/never-share.txt"
SOURCE_ROOT = Path(__file__).resolve().parents[1]
FAMILY_SOURCE = (SOURCE_ROOT / "workspace/AGENTS.md").is_file()
OPTIONAL_SOURCE = all(
    (SOURCE_ROOT / name).is_dir()
    for name in ("shared-context", "registry", "library")
)
POINTER = (
    "Read [`AGENTS.md`](AGENTS.md) and follow it.\n"
    "This is a pinned pointer; `AGENTS.md` is authoritative.\n"
)


def write(root, rel, text):
    path = Path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


GIT_LOCATION_VARS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX",
    "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)


def isolated_git_env():
    env = os.environ.copy()
    for name in GIT_LOCATION_VARS:
        env.pop(name, None)
    return env


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False,
        env=isolated_git_env(),
    )


def init_repo(root):
    assert git(root, "init", "-q").returncode == 0
    assert git(root, "config", "user.email", "gate@example.invalid").returncode == 0
    assert git(root, "config", "user.name", "Gate Test").returncode == 0
    write(root, ".gitignore", ".workspace-private/\n")
    write(root, PRIVATE_TERMS, FAKE_TERM + "\n")
    assert git(root, "add", ".").returncode == 0
    committed = git(root, "commit", "-qm", "fixture")
    assert committed.returncode == 0, committed.stderr


def exact_workspace_extraction(root):
    """Materialize the documented subtree split plus its support contract."""
    source = Path(__file__).resolve().parents[1]
    root = Path(root)
    for child in (source / "workspace").iterdir():
        target = root / child.name
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)
    for name in ("tools", "doctrine", "_templates", ".githooks"):
        shutil.copytree(
            source / name,
            root / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for name in ("LOOP.md", "NAMESPACE.md", "LICENSE", ".gitignore"):
        shutil.copy2(source / name, root / name)


class GateCorrections(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def build_git_fixture(self):
        build(self.tmp, CLEAN)
        shutil.copy(Path(TOOLS, "journal_guard.py"), Path(self.tmp, "tools"))
        init_repo(self.tmp)

    def init_clean_repo(self):
        self.assertEqual(git(self.tmp, "init", "-q").returncode, 0)
        self.assertEqual(
            git(self.tmp, "config", "user.email", "gate@example.invalid").returncode,
            0,
        )
        self.assertEqual(
            git(self.tmp, "config", "user.name", "Gate Test").returncode, 0
        )
        self.assertEqual(git(self.tmp, "add", ".").returncode, 0)
        committed = git(self.tmp, "commit", "-qm", "clean fixture")
        self.assertEqual(committed.returncode, 0, committed.stderr)

    def test_staged_scrub_reads_index_not_worktree(self):
        # Index/worktree disagreement proves the commit snapshot is scanned.
        self.build_git_fixture()
        write(self.tmp, "notes.md", "clean\n")
        self.assertEqual(git(self.tmp, "add", "notes.md").returncode, 0)
        write(self.tmp, "notes.md", f"contains {FAKE_TERM}\n")
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 0, out)

        write(self.tmp, "notes.md", f"contains {FAKE_TERM}\n")
        self.assertEqual(git(self.tmp, "add", "notes.md").returncode, 0)
        write(self.tmp, "notes.md", "clean\n")
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)

    def test_scrub_falls_back_to_legacy_private_directory(self):
        # Removing legacy fallback would silently stop checking old instances.
        self.build_git_fixture()
        Path(self.tmp, ".workspace-private").rename(
            Path(self.tmp, ".sett-private")
        )
        write(self.tmp, ".gitignore", ".workspace-private/\n.sett-private/\n")
        self.assertEqual(git(self.tmp, "add", ".gitignore").returncode, 0)
        for args in ((), ("--staged",)):
            code, out = run(self.tmp, "scrub_check.py", *args)
            self.assertEqual(code, 0, out)
        write(self.tmp, "notes.md", f"contains {FAKE_TERM}\n")
        self.assertEqual(git(self.tmp, "add", "notes.md").returncode, 0)
        for args in ((), ("--staged",)):
            code, out = run(self.tmp, "scrub_check.py", *args)
            self.assertEqual(code, 1, out)
            self.assertIn("never-share term", out)
            self.assertNotIn(FAKE_TERM, out)

    def test_scrub_prefers_new_private_directory_and_warns(self):
        # The new store must win even when the old store has different terms.
        self.build_git_fixture()
        legacy_term = "zz-legacy-private-term"
        write(self.tmp, ".sett-private/never-share.txt", legacy_term + "\n")
        write(self.tmp, ".gitignore", ".workspace-private/\n.sett-private/\n")
        write(self.tmp, "notes.md", legacy_term + "\n")
        self.assertEqual(git(self.tmp, "add", ".gitignore", "notes.md").returncode, 0)
        for args in ((), ("--staged",)):
            code, out = run(self.tmp, "scrub_check.py", *args)
            self.assertEqual(code, 0, out)
            self.assertIn("warning", out.lower())
            self.assertIn(".workspace-private", out)
        write(self.tmp, "notes.md", FAKE_TERM + "\n")
        self.assertEqual(git(self.tmp, "add", "notes.md").returncode, 0)
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertNotIn(FAKE_TERM, out)

    def test_scrub_reads_legacy_no_private_terms_declaration(self):
        self.build_git_fixture()
        Path(self.tmp, PRIVATE_TERMS).unlink()
        Path(self.tmp, ".workspace-private").rename(Path(self.tmp, ".sett-private"))
        write(self.tmp, ".sett-private/no-private-terms.json", '{"version":1,"confirmed":true}\n')
        write(self.tmp, ".gitignore", ".sett-private/\n")
        self.assertEqual(git(self.tmp, "add", ".gitignore").returncode, 0)
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 0, out)

    def test_staged_scrub_rejects_tracked_legacy_private_store(self):
        self.build_git_fixture()
        write(self.tmp, ".sett-private/never-share.txt", FAKE_TERM + "\n")
        write(self.tmp, ".gitignore", ".workspace-private/\n.sett-private/\n")
        self.assertEqual(git(self.tmp, "add", ".gitignore").returncode, 0)
        self.assertEqual(git(self.tmp, "add", "-f", ".sett-private/never-share.txt").returncode, 0)
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertIn("must not be tracked", out)
        self.assertNotIn(FAKE_TERM, out)

    def test_context_fingerprint_reads_legacy_private_directory(self):
        # Changing legacy private rules must invalidate cached scrub results.
        import context as routing
        previous_root = routing.ROOT
        routing.ROOT = Path(self.tmp)
        try:
            write(self.tmp, ".sett-private/never-share.txt", "zz-first-private-term\n")
            before = routing.fingerprint()
            write(self.tmp, ".sett-private/never-share.txt", "zz-second-private-term\n")
            self.assertNotEqual(routing.fingerprint(), before)
        finally:
            routing.ROOT = previous_root

    def test_legacy_tool_imports_keep_working(self):
        # Existing callers can keep the old module, class and helper names.
        proc = subprocess.run(
            [sys.executable, "-c", (
                "import sett_setup, workspace_setup, sett_layout, workspace_layout; "
                "assert sett_setup.SetupError is workspace_setup.SetupError; "
                "assert sett_setup.first_sett_ancestor is workspace_setup.first_workspace_ancestor; "
                "assert sett_setup.contains_sett_root is workspace_setup.contains_workspace_root; "
                "layout = sett_layout.SettLayout('.'); "
                "assert isinstance(layout, workspace_layout.WorkspaceLayout); "
                "assert layout.is_sett_root == layout.is_workspace_root"
            )],
            cwd=SOURCE_ROOT / "tools", capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_doctor_warns_when_both_private_directories_exist(self):
        self.build_git_fixture()
        shutil.copy(Path(TOOLS, "doctor.py"), Path(self.tmp, "tools"))
        write(self.tmp, ".sett-private/never-share.txt", "zz-legacy-private-term\n")
        write(self.tmp, ".gitignore", ".workspace-private/\n.sett-private/\n")
        _, out = run(self.tmp, "doctor.py")
        self.assertIn("warning", out.lower())
        self.assertIn("using .workspace-private/", out)
        self.assertNotIn(FAKE_TERM, out)

    def test_private_conflict_warning_redacts_terms_matching_directory_names(self):
        # Even public path names must be redacted when configured as private.
        import contextlib
        import io
        import context as routing
        self.build_git_fixture()
        shutil.copy(Path(TOOLS, "doctor.py"), Path(self.tmp, "tools"))
        write(self.tmp, ".sett-private/never-share.txt", "zz-legacy-private-term\n")
        previous_root = routing.ROOT
        routing.ROOT = Path(self.tmp)
        try:
            for terms in (".workspace-private\n", "xx\n.workspace-private\n"):
                with self.subTest(terms=terms):
                    write(self.tmp, PRIVATE_TERMS, terms)
                    captured = io.StringIO()
                    with contextlib.redirect_stderr(captured):
                        routing.fingerprint()
                    _, doctor_output = run(self.tmp, "doctor.py")
                    _, scrub_output = run(self.tmp, "scrub_check.py")
                    _, staged_output = run(self.tmp, "scrub_check.py", "--staged")
                    for output in (captured.getvalue(), doctor_output, scrub_output, staged_output):
                        self.assertIn("warning", output.lower())
                        self.assertNotIn(".workspace-private", output)
                        self.assertIn("<redacted-term>", output)
        finally:
            routing.ROOT = previous_root

    def test_staged_scrub_reads_staged_ignore_configuration(self):
        # Staged ignore rules, not later worktree edits, define commit safety.
        self.build_git_fixture()
        write(self.tmp, ".gitignore", "")
        self.assertEqual(git(self.tmp, "add", ".gitignore").returncode, 0)
        write(self.tmp, ".gitignore", ".workspace-private/\n")
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertIn(".gitignore", out)

        write(self.tmp, ".gitignore", ".workspace-private/\n!*\n")
        self.assertEqual(git(self.tmp, "add", ".gitignore").returncode, 0)
        write(self.tmp, ".gitignore", ".workspace-private/\n")
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertIn(".gitignore", out)

    def test_scrub_diagnostic_redacts_term(self):
        self.build_git_fixture()
        write(self.tmp, "notes.md", f"contains {FAKE_TERM}\n")
        self.assertEqual(git(self.tmp, "add", "notes.md").returncode, 0)
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertNotIn(FAKE_TERM, out)
        self.assertIn("never-share term", out)

        write(self.tmp, f"{FAKE_TERM}.md", "clean\n")
        self.assertEqual(git(self.tmp, "add", f"{FAKE_TERM}.md").returncode, 0)
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertNotIn(FAKE_TERM, out)

    def test_hash_prefixed_private_term_is_not_a_comment(self):
        self.build_git_fixture()
        hash_term = "#zz-private-hashtag"
        write(self.tmp, PRIVATE_TERMS, hash_term + "\n")
        write(self.tmp, "notes.md", "contains " + hash_term + "\n")
        self.assertEqual(git(self.tmp, "add", "notes.md").returncode, 0)
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertIn("never-share term", out)
        self.assertNotIn(hash_term, out)

    def test_unmerged_confidential_path_is_redacted_before_other_gates(self):
        # Scrub must fail before any path-reporting gate can expose this name.
        self.build_git_fixture()
        rel = f"workspace/{FAKE_TERM}-conflict.md"
        write(self.tmp, rel, "conflict\n")
        oid = git(self.tmp, "hash-object", "-w", rel).stdout.strip()
        staged = subprocess.run(
            ["git", "update-index", "--index-info"],
            cwd=self.tmp,
            input=(
                f"100644 {oid} 1\t{rel}\n"
                f"100644 {oid} 2\t{rel}\n"
            ),
            capture_output=True,
            text=True,
            check=False,
            env=isolated_git_env(),
        )
        self.assertEqual(staged.returncode, 0, staged.stderr)

        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 2, out)
        self.assertIn("<redacted-path>", out)
        self.assertNotIn(FAKE_TERM, out)

        hook = Path(__file__).resolve().parents[1] / ".githooks/pre-commit"
        hook_text = hook.read_text(encoding="utf-8").replace(
            '    "tools/test_gate_corrections.py"\n', ""
        )
        fixture_hook = Path(self.tmp, "pre-commit")
        fixture_hook.write_text(hook_text, encoding="utf-8")
        proc = subprocess.run(
            ["sh", str(fixture_hook)], cwd=self.tmp, capture_output=True,
            text=True, check=False, env=isolated_git_env(),
        )
        output = proc.stdout + proc.stderr
        self.assertNotEqual(proc.returncode, 0, output)
        self.assertIn("<redacted-path>", output)
        self.assertNotIn(FAKE_TERM, output)

    def test_staged_scrub_rejects_tracked_private_store(self):
        self.build_git_fixture()
        self.assertEqual(
            git(self.tmp, "add", "-f", PRIVATE_TERMS).returncode, 0
        )
        code, out = run(self.tmp, "scrub_check.py", "--staged")
        self.assertEqual(code, 1, out)
        self.assertIn("must not be tracked", out)
        self.assertNotIn(FAKE_TERM, out)

    def test_journal_control_exemptions_are_exact_basenames(self):
        self.build_git_fixture()
        journal = "workspace/30_memory/journal"
        for name in ("INDEX.md", "README.md", "MYREADME.md"):
            write(self.tmp, f"{journal}/{name}", "original\n")
        self.assertEqual(git(self.tmp, "add", journal).returncode, 0)
        self.assertEqual(git(self.tmp, "commit", "-qm", "journal").returncode, 0)

        for name in ("INDEX.md", "README.md"):
            write(self.tmp, f"{journal}/{name}", "control update\n")
        self.assertEqual(git(self.tmp, "add", journal).returncode, 0)
        code, out = run(self.tmp, "journal_guard.py", "--staged")
        self.assertEqual(code, 0, out)

        write(self.tmp, f"{journal}/MYREADME.md", "forbidden update\n")
        self.assertEqual(git(self.tmp, "add", journal).returncode, 0)
        code, out = run(self.tmp, "journal_guard.py", "--staged")
        self.assertEqual(code, 2, out)
        self.assertIn("MYREADME.md", out)

    def test_journal_type_change_is_rejected(self):
        self.build_git_fixture()
        rel = "workspace/30_memory/journal/2026-08-24-entry.md"
        write(self.tmp, rel, "original\n")
        self.assertEqual(git(self.tmp, "add", rel).returncode, 0)
        self.assertEqual(git(self.tmp, "commit", "-qm", "journal").returncode, 0)
        Path(self.tmp, rel).unlink()
        os.symlink("replacement.md", Path(self.tmp, rel))
        self.assertEqual(git(self.tmp, "add", rel).returncode, 0)
        status = git(self.tmp, "diff", "--cached", "--name-status").stdout
        self.assertTrue(status.startswith("T"), status)
        code, out = run(self.tmp, "journal_guard.py", "--staged")
        self.assertEqual(code, 2, out)
        self.assertIn(rel, out)

    def test_journal_guard_blocks_agent_writes_to_private_store(self):
        self.build_git_fixture()
        guard = Path(self.tmp, "tools/journal_guard.py")

        def ask(payload):
            proc = subprocess.run(
                [sys.executable, str(guard)], cwd=self.tmp,
                input=json.dumps(payload), capture_output=True, text=True,
                env=isolated_git_env(),
            )
            return proc.returncode, proc.stdout + proc.stderr

        for private_terms in (PRIVATE_TERMS, ".sett-private/never-share.txt"):
            for op in ("modify", "create-or-overwrite"):
                code, out = ask({"op": op, "path": private_terms})
                self.assertEqual(code, 2, out)
                self.assertIn("human-only", out)

            code, out = ask({"op": "shell", "command": f"echo leak >> {private_terms}"})
            self.assertEqual(code, 2, out)

        code, out = ask({"op": "create-or-overwrite", "path": "notes.md"})
        self.assertEqual(code, 0, out)

    def test_pointer_exceptions_are_bounded_and_structural(self):
        files = dict(CLEAN)
        for rel in ("CLAUDE.md", "GEMINI.md", "workspace/CLAUDE.md",
                    "workspace/GEMINI.md"):
            files[rel] = POINTER
        build(self.tmp, files)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 0, out)

        write(self.tmp, "workspace/CLAUDE.md", POINTER + "Extra instructions.\n")
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn("pinned pointer", out)

        write(self.tmp, "workspace/CLAUDE.md", POINTER)
        write(self.tmp, "nested/CLAUDE.md", "Use " + "cla" "ude" + " here.\n")
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn("nested/CLAUDE.md", out)

        Path(self.tmp, "nested/CLAUDE.md").unlink()
        write(self.tmp, ".hidden/runtime.md", "Use " + "cla" "ude" + " here.\n")
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn(".hidden/runtime.md", out)

    def test_runtime_declaration_is_bounded_and_reciprocal(self):
        # The opt-in lives in frontmatter, covers only its own file, and
        # obliges the file that claims it to name what it claims.
        vendor = "cla" "ude"
        prose = f"\nThe runner is {vendor}.\n"
        seam = CLEAN["workspace/70_seams/INDEX.md"]
        declaring = seam.replace("---\n", "---\nruntime_subject: true\n", 1)

        files = dict(CLEAN)
        files["workspace/70_seams/INDEX.md"] = seam + prose
        build(self.tmp, files)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)            # undeclared: still a leak

        write(self.tmp, "workspace/70_seams/INDEX.md", declaring + prose)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 0, out)
        self.assertEqual(run(self.tmp, "build_catalog.py", "--check")[0], 0)

        write(self.tmp, "workspace/70_seams/INDEX.md", declaring)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)            # declared, names nothing
        self.assertIn("names no runtime", out)

        write(self.tmp, "workspace/70_seams/INDEX.md",
              seam + "\nruntime_subject: true\n" + prose)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)            # body cannot forge frontmatter
        self.assertIn("vendor agent name", out)

        write(self.tmp, "workspace/70_seams/INDEX.md", declaring + prose)
        write(self.tmp, "notes.txt", declaring + prose)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)            # markdown only
        self.assertIn("notes.txt", out)

        Path(self.tmp, "notes.txt").unlink()
        write(self.tmp, ".hidden/neighbour.md", prose)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)            # exemption is per-file
        self.assertIn(".hidden/neighbour.md", out)

        Path(self.tmp, ".hidden/neighbour.md").unlink()
        write(self.tmp, "workspace/70_seams/INDEX.md",
              seam.replace("---\n", "---\nruntime_subject: yes\n", 1) + prose)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)            # the flag is schema-checked
        self.assertIn("runtime_subject", out)

    def test_runtime_name_inside_web_url_is_scanned(self):
        # Filesystem-path blanking must not erase ordinary URLs.
        files = dict(CLEAN)
        files["workspace/70_seams/INDEX.md"] += (
            "\nReference: https://example.invalid/" + "cla" "ude.\n"
        )
        build(self.tmp, files)
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn("vendor agent name", out)

    def test_runtime_scan_excludes_only_git_ignored_scratch(self):
        self.build_git_fixture()
        write(self.tmp, ".gitignore", ".workspace-private/\n.local-scratch/\n")
        write(
            self.tmp, ".local-scratch/review.diff",
            "mentions " + "cla" "ude" + "\n",
        )
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 0, out)

        write(self.tmp, ".hidden/source.md", "uses " + "cla" "ude" + "\n")
        code, out = run(self.tmp, "agnostic_check.py", "--root", self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn(".hidden/source.md", out)

    def test_runtime_scan_root_is_not_hijacked_by_git_environment(self):
        # Hook Git variables must not redirect fixture or extracted roots.
        build(self.tmp, dict(CLEAN))
        env = os.environ.copy()
        env["GIT_DIR"] = git(
            Path(__file__).resolve().parents[1], "rev-parse", "--git-dir"
        ).stdout.strip()
        proc = subprocess.run(
            [sys.executable, str(Path(self.tmp, "tools/agnostic_check.py")),
             "--root", self.tmp],
            capture_output=True, text=True, check=False, env=env,
        )
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, output)

    def test_library_depth_is_capped_at_three_hops(self):
        files = dict(CLEAN)
        files["library/fields/README.md"] = files[
            "library/fields/README.md"
        ].replace(
            "\n- [typography-layout]"
            "(design/interface-design/typography-layout/README.md)\n",
            "\n",
        )
        build(self.tmp, files)
        self.assertEqual(run(self.tmp, "build_catalog.py")[0], 0)
        code, out = run(self.tmp, "check_loop.py")
        self.assertEqual(code, 1, out)
        self.assertIn("max 3", out)

    def test_validation_and_reachability_do_not_require_catalog_outputs(self):
        build(self.tmp, dict(CLEAN))

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)
        self.assertFalse(Path(self.tmp, "CATALOG.md").exists())
        self.assertFalse(Path(self.tmp, "CATALOG.json").exists())

        code, out = run(self.tmp, "check_loop.py")
        self.assertEqual(code, 0, out)

    def test_catalog_outputs_are_ignored_and_untracked(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("CATALOG.md", "CATALOG.json"):
            tracked = git(root, "ls-files", "--error-unmatch", name)
            self.assertNotEqual(tracked.returncode, 0, name)
            ignored = git(root, "check-ignore", "-q", "--no-index", name)
            self.assertEqual(ignored.returncode, 0, name)

    def test_static_boot_budget_counts_the_required_shared_view(self):
        files = dict(CLEAN)
        files["workspace/70_seams/SHARED.md"] = """---
id: workspace-shared-boot
type: doctrine
status: mature
description: >
  Shared boot view. Use when starting a workspace session. Not for seam
  mechanics (see shared-context.md).
updated: 2026-08-24
---

# Shared boot view

""" + "x" * 7000
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("static boot", out)
        self.assertIn("7000", out)

    def test_boot_manifest_drives_validator_accounting(self):
        files = dict(CLEAN)
        files["workspace/AGENTS.md"] = files["workspace/AGENTS.md"].replace(
            "boot_static: [workspace/AGENTS.md, workspace/70_seams/SHARED.md]",
            "boot_static: [workspace/AGENTS.md, workspace/70_seams/SHARED.md, workspace/boot-probe.md]",
        )
        files["workspace/boot-probe.md"] = """---
id: boot-probe
type: doctrine
status: mature
description: >
  Boot probe. Use when testing boot accounting. Not for work routing
  (see workspace/AGENTS.md).
load: always
updated: 2026-08-24
---

# Probe

""" + "x" * 7000
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("workspace/boot-probe.md", out)
        self.assertIn("static boot", out)

    def test_boot_manifest_caps_drive_validator_accounting(self):
        files = dict(CLEAN)
        files["workspace/AGENTS.md"] = files["workspace/AGENTS.md"].replace(
            "boot_static_cap: 7000", "boot_static_cap: 600"
        )
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("boot_static_cap must equal schema limit 7000", out)
        self.assertIn("not 600", out)

    def test_schema_owns_fixed_boot_caps_and_all_handover_caps(self):
        files = dict(CLEAN)
        files["workspace/AGENTS.md"] = files["workspace/AGENTS.md"].replace(
            "boot_static_cap: 7000", "boot_static_cap: 70000"
        ).replace(
            "boot_dynamic_cap: 3000", "boot_dynamic_cap: 30000"
        ).replace(
            "boot_total_cap: 10000", "boot_total_cap: 100000"
        )
        files["workspace/90_runs/2026-08-24-archived/archive.md"] = """---
id: handover-archived
type: handover
status: draft
description: Archived handover. Use when testing caps. Not for continuation (see workspace/AGENTS.md).
closed_at: 2026-08-24T10:00:00Z
updated: 2026-08-24
---

# Archived handover

""" + "x" * 3100
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("must equal schema limit 7000", out)
        self.assertIn("must equal schema limit 3000", out)
        self.assertIn("must equal schema limit 10000", out)
        self.assertIn("archive.md: handover is", out)
        self.assertIn("cap 3000", out)

    def test_repository_instance_entrance_declares_only_bounded_boot(self):
        root = SOURCE_ROOT
        entrance = root / ("workspace/AGENTS.md" if FAMILY_SOURCE else "AGENTS.md")
        text = entrance.read_text(encoding="utf-8")
        frontmatter, body = text.split("---", 2)[1:]
        self.assertIn(
            "boot_static: [workspace/AGENTS.md, workspace/70_seams/SHARED.md]",
            frontmatter,
        )
        self.assertIn("boot_dynamic: workspace/20_intent/active/*.md", frontmatter)
        self.assertIn("boot_selector: explicit-task", frontmatter)
        self.assertIn("boot_static_cap: 7000", frontmatter)
        self.assertIn("boot_dynamic_cap: 3000", frontmatter)
        self.assertIn("boot_total_cap: 10000", frontmatter)
        boot = body.split("## Start and select", 1)[1].split("## ", 1)[0]
        for forbidden in (
            "CATALOG", "shared-context.md", "decision-queue.md",
            "open-loops.md", "shared-context/", "registry/", "library/",
        ):
            self.assertNotIn(forbidden, boot)

    @unittest.skipUnless(FAMILY_SOURCE, "family-maintenance entrance is absent")
    def test_repository_maintenance_entrance_never_starts_onboarding(self):
        root = SOURCE_ROOT
        text = (root / "AGENTS.md").read_text(encoding="utf-8")
        body = text.split("---", 2)[2]
        self.assertIn("template family", body)
        self.assertNotIn("ONBOARDING", body)
        self.assertNotIn(".uninitialised", body)
        positions = [
            body.index(target)
            for target in ("README.md", "LOOP.md", "doctrine/INDEX.md", "NAMESPACE.md")
        ]
        self.assertEqual(positions, sorted(positions))

        # The README's maintenance paragraph must not route a maintainer
        # into the instance walk; the two modes never combine.
        readme = (root / "README.md").read_text(encoding="utf-8")
        paragraphs = [p for p in readme.split("\n\n")
                      if "Maintaining the template" in p]
        self.assertEqual(len(paragraphs), 1, "README names the maintenance mode once")
        maintenance = paragraphs[0]
        self.assertIn("AGENTS.md", maintenance)
        self.assertNotIn("ONBOARDING", maintenance)
        self.assertNotIn(".uninitialised", maintenance)
        self.assertNotIn("workspace/00_meta", maintenance)

    def test_non_manifest_routing_never_claims_ordinary_boot(self):
        root = SOURCE_ROOT
        offenders = []
        workspace_root = root / "workspace" if FAMILY_SOURCE else root
        for base in (workspace_root, root / "_templates"):
            for path in base.rglob("*.md"):
                normalized = " ".join(path.read_text(encoding="utf-8").split()).lower()
                if any(phrase in normalized for phrase in (
                    "at boot to see", "use at boot", "handover at boot",
                    "boot step 1 reads this chamber",
                )):
                    offenders.append(str(path.relative_to(root)))
        self.assertEqual(offenders, [])

    @unittest.skipUnless(OPTIONAL_SOURCE, "optional source packs are absent")
    def test_standalone_members_validate_from_their_own_entrance(self):
        source_root = SOURCE_ROOT
        for name in ("shared-context", "registry", "library"):
            with self.subTest(member=name):
                member_tmp = Path(self.tmp, name)
                shutil.copytree(source_root / name, member_tmp)
                shutil.copy2(source_root / "NAMESPACE.md", member_tmp)
                shutil.copy2(source_root / "LICENSE", member_tmp)
                build(member_tmp, {})
                code, out = run(member_tmp, "build_catalog.py", "--check")
                self.assertEqual(code, 0, out)
                entries = len(list((source_root / name).rglob("*.md")))
                self.assertIn(f"OK: {entries} entries", out)
                code, out = run(member_tmp, "check_loop.py")
                self.assertEqual(code, 0, out)

                if name == "shared-context":
                    shared = member_tmp / "SHARED.md"
                    original = shared.read_text(encoding="utf-8")
                    shared.write_text(
                        original + "\nUndeclared: <<NOT_A_DECLARED_PACK_TOKEN>>.\n",
                        encoding="utf-8",
                    )
                    code, out = run(member_tmp, "build_catalog.py", "--check")
                    self.assertEqual(code, 1, out)
                    self.assertIn("has no row in SHARED.md declared_tokens", out)
                    shared.write_text(original, encoding="utf-8")
                    index = member_tmp / "INDEX.md"
                    index.write_text(
                        index.read_text(encoding="utf-8")
                        + "\nUnflagged: <<PRINCIPAL_NAME>>.\n",
                        encoding="utf-8",
                    )
                    code, out = run(member_tmp, "build_catalog.py", "--check")
                    self.assertEqual(code, 1, out)
                    self.assertIn("does not declare 'tokens: true'", out)

    def test_dynamic_boot_budget_counts_the_selected_handover(self):
        files = dict(CLEAN)
        files["workspace/90_runs/2026-08-24-probe/handover.md"] = """---
id: handover-probe
type: handover
status: draft
description: >
  Probe handover. Use when continuing the probe. Not for session entry
  (see workspace/AGENTS.md).
updated: 2026-08-24
closed_at: 2026-08-24T10:00:00Z
---

# Handover

""" + "x" * 3000
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("dynamic boot", out)
        self.assertIn("3000", out)

    def test_dynamic_boot_match_wrong_type_is_rejected_and_capped(self):
        # A glob match cannot escape accounting by lying about its type.
        files = dict(CLEAN)
        files["workspace/90_runs/2026-08-24-wrong/handover.md"] = """---
id: wrong-dynamic-type
type: doctrine
status: draft
description: >
  Wrong dynamic type. Use when testing boot validation. Not for real work
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Wrong type

""" + "x" * 3000
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("boot_dynamic match must be type 'handover'", out)
        self.assertIn("dynamic candidate", out)
        self.assertIn("cap 3000", out)

    def test_malformed_dynamic_run_cannot_take_newest_precedence(self):
        # Only timestamp-first run directories may participate in selection.
        files = dict(CLEAN)
        for run_id in ("2026-08-24-valid", "zz-malformed"):
            files[f"workspace/90_runs/{run_id}/handover.md"] = f"""---
id: handover-{run_id}
type: handover
status: draft
description: >
  Dynamic fixture. Use when continuing this fixture. Not for session entry
  (see workspace/AGENTS.md).
updated: 2026-08-24
closed_at: 2026-08-24T10:00:00Z
---

# {run_id}
"""
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("timestamp-first", out)
        self.assertIn("zz-malformed", out)

    def test_boot_accounting_is_reported_without_catalog_outputs(self):
        files = dict(CLEAN)
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)
        self.assertIn("boot static ", out)
        self.assertIn("/7000", out)
        self.assertIn("dynamic 0/3000", out)
        self.assertIn("total ", out)
        self.assertIn("/10000", out)

    def test_instance_boot_selects_newest_handover_within_budget(self):
        files = dict(CLEAN)
        closed = {
            "2026-08-23-old": "2026-08-23T18:00:00Z",
            "2026-08-24-current": "2026-08-24T18:00:00Z",
        }
        for run_id in ("2026-08-23-old", "2026-08-24-current"):
            files[f"workspace/90_runs/{run_id}/handover.md"] = f"""---
id: handover-{run_id}
type: handover
status: draft
description: >
  Probe handover. Use when continuing the probe. Not for session entry
  (see workspace/AGENTS.md).
updated: 2026-08-24
closed_at: {closed[run_id]}
---

# Handover {run_id}
"""
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)
        self.assertIn(
            "dynamic ",
            out,
        )
        self.assertIn(
            "(workspace/90_runs/2026-08-24-current/handover.md)",
            out,
        )

    def test_same_day_dynamic_selection_uses_closed_at_not_slug_order(self):
        files = dict(CLEAN)
        for run_id, closed_at in (
            ("2026-08-24-a-later", "2026-08-24T22:00:00Z"),
            ("2026-08-24-z-earlier", "2026-08-24T08:00:00Z"),
        ):
            files[f"workspace/90_runs/{run_id}/handover.md"] = f"""---
id: handover-{run_id}
type: handover
status: draft
description: Probe handover. Use when continuing the probe. Not for session entry (see workspace/AGENTS.md).
closed_at: {closed_at}
updated: 2026-08-24
---

# {run_id}
"""
        build(self.tmp, files)

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)
        self.assertIn(
            "(workspace/90_runs/2026-08-24-a-later/handover.md)", out
        )

    def test_handover_requires_utc_closed_at(self):
        files = dict(CLEAN)
        files["workspace/90_runs/2026-08-24-probe/handover.md"] = """---
id: handover-probe
type: handover
status: draft
description: Probe handover. Use when continuing the probe. Not for session entry (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Probe
"""
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("missing required field 'closed_at'", out)

        handover = Path(
            self.tmp, "workspace/90_runs/2026-08-24-probe/handover.md"
        )
        handover.write_text(
            handover.read_text(encoding="utf-8").replace(
                "status: draft", "status: reserved"
            ),
            encoding="utf-8",
        )
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("missing required field 'closed_at'", out)

        handover.write_text(
            handover.read_text(encoding="utf-8").replace(
                "status: reserved", "status: draft"
            ).replace(
                "updated: 2026-08-24",
                "closed_at: 2026-08-24 10:00\nupdated: 2026-08-24",
            ),
            encoding="utf-8",
        )
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("closed_at", out)
        self.assertIn("UTC", out)

    @unittest.skipUnless(FAMILY_SOURCE, "already running in an extracted workspace")
    def test_exact_workspace_subtree_layout_passes_all_production_gates(self):
        exact_workspace_extraction(self.tmp)
        # This models a live instance — it has runs and a journal — so the
        # onboarding sentinel is gone and the private store is armed, exactly
        # as they are once the walk finishes.
        Path(self.tmp, "00_meta/.uninitialised").unlink(missing_ok=True)
        write(self.tmp, PRIVATE_TERMS, "zz-private-" + "subtree-term\n")
        write(
            self.tmp,
            "90_runs/2026-08-24-extracted/handover.md",
            """---
id: handover-extracted
type: handover
status: draft
description: Extracted handover. Use when continuing extraction QA. Not for durable truth (see 90_runs/INDEX.md).
closed_at: 2026-08-24T12:00:00Z
updated: 2026-08-24
---

# Extracted handover
""",
        )
        write(
            self.tmp,
            "30_memory/journal/2026-08-24-1200-extracted.md",
            "---\ndate: 2026-08-24T12:00\nkind: event\n---\n\n"
            "Extraction fixture.\n",
        )
        self.init_clean_repo()

        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)
        match = re.search(
            r"boot static (\d+)/7000, dynamic (\d+)/3000 .* total (\d+)/10000",
            out,
        )
        self.assertIsNotNone(match, out)
        self.assertGreater(int(match.group(1)), 0, out)
        self.assertEqual(int(match.group(2)), 0, out)
        self.assertEqual(match.group(1), match.group(3), out)
        for tool, args in (
            ("check_loop.py", ()),
            ("scrub_check.py", ()),
            ("scrub_check.py", ("--staged",)),
            ("agnostic_check.py", ()),
            ("journal_guard.py", ("--staged",)),
        ):
            with self.subTest(tool=tool, args=args):
                code, gate_out = run(self.tmp, tool, *args)
                self.assertEqual(code, 0, gate_out)

        write(
            self.tmp,
            "30_memory/journal/2026-08-24-1200-extracted.md",
            "mutated closed journal entry\n",
        )
        self.assertEqual(
            git(
                self.tmp,
                "add",
                "30_memory/journal/2026-08-24-1200-extracted.md",
            ).returncode,
            0,
        )
        code, out = run(self.tmp, "journal_guard.py", "--staged")
        self.assertEqual(code, 2, out)
        self.assertIn("staged mutation", out)

    @unittest.skipUnless(FAMILY_SOURCE, "already running in an extracted workspace")
    def test_extracted_instance_armed_private_store_passes_scrub(self):
        # Built from parts so the literal term is absent from the copied
        # tools/ sources (unlike FAKE_TERM, which appears in this file).
        term = "zz-private-" + "armed-instance-term"
        exact_workspace_extraction(self.tmp)
        Path(self.tmp, "00_meta/.uninitialised").unlink(missing_ok=True)
        write(self.tmp, PRIVATE_TERMS, term + "\n")
        self.init_clean_repo()

        for args in ((), ("--staged",)):
            with self.subTest(args=args):
                code, out = run(self.tmp, "scrub_check.py", *args)
                self.assertEqual(code, 0, out)

        Path(self.tmp, PRIVATE_TERMS).unlink()
        for args in ((), ("--staged",)):
            with self.subTest(args=args):
                code, out = run(self.tmp, "scrub_check.py", *args)
                self.assertEqual(code, 1, out)
                self.assertIn("missing ignored", out)

    def test_catalog_references_cannot_escape_the_workspace_root(self):
        files = dict(CLEAN)
        build(self.tmp, files)
        outside = Path(self.tmp).parent / (Path(self.tmp).name + "-outside.md")
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        harness = Path(self.tmp, "workspace/70_seams/harness.md")
        original = harness.read_text(encoding="utf-8")
        probes = (
            str(outside),
            "../../../" + outside.name,
        )
        for ref in probes:
            with self.subTest(ref=ref):
                harness.write_text(
                    original.replace("ref: seams-index", f"ref: {ref}"),
                    encoding="utf-8",
                )
                code, out = run(self.tmp, "build_catalog.py", "--check")
                self.assertEqual(code, 1, out)
                self.assertIn("outside the workspace root", out)

        spaced = outside.with_name(outside.stem + " spaced.md")
        spaced.write_text("outside\n", encoding="utf-8")
        self.addCleanup(lambda: spaced.unlink(missing_ok=True))
        harness.write_text(
            original.replace("ref: seams-index", f"ref: {spaced}"),
            encoding="utf-8",
        )
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("outside the workspace root", out)

        escape = Path(self.tmp, "workspace/70_seams/escape.txt")
        escape.symlink_to(outside)
        harness.write_text(
            original.replace("ref: seams-index", "ref: workspace/70_seams/escape.txt"),
            encoding="utf-8",
        )
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("outside the workspace root", out)

        outside_id = outside.with_name(outside.stem + "-id.md")
        outside_id.write_text(
            """---
id: escaped-by-id
type: seam
status: draft
description: Escaped seam. Use when testing containment. Not for real work (see workspace/70_seams/INDEX.md).
updated: 2026-08-24
---

# Escape

## What crosses
Nothing.
## Direction
None.
## Inspect point
None.
## Control point
None.
## What never crosses
Everything.
""",
            encoding="utf-8",
        )
        self.addCleanup(lambda: outside_id.unlink(missing_ok=True))
        escape_id = Path(self.tmp, "workspace/70_seams/escape-id.md")
        escape_id.symlink_to(outside_id)
        harness.write_text(
            original.replace("ref: seams-index", "ref: escaped-by-id"),
            encoding="utf-8",
        )
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("outside the workspace root", out)

    def test_loop_links_cannot_escape_the_workspace_root(self):
        files = dict(CLEAN)
        build(self.tmp, files)
        outside = Path(self.tmp).parent / (Path(self.tmp).name + "-loop.md")
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        library = Path(self.tmp, "library/LIBRARY.md")
        original = library.read_text(encoding="utf-8")
        for target in (str(outside), f"<{outside}>", "../../" + outside.name):
            with self.subTest(target=target):
                library.write_text(
                    original + f"\n[escape]({target})\n", encoding="utf-8"
                )
                code, out = run(self.tmp, "check_loop.py")
                self.assertEqual(code, 1, out)
                self.assertIn("outside the workspace root", out)

        escape = Path(self.tmp, "library/escape.txt")
        escape.symlink_to(outside)
        library.write_text(original + "\n[escape](escape.txt)\n", encoding="utf-8")
        code, out = run(self.tmp, "check_loop.py")
        self.assertEqual(code, 1, out)
        self.assertIn("outside the workspace root", out)

    def test_tracked_binary_content_is_rejected_without_echoing_bytes(self):
        files = dict(CLEAN)
        build(self.tmp, files)
        write(self.tmp, ".gitignore", ".workspace-private/\n")
        Path(self.tmp, "workspace/00_meta/.uninitialised").touch()
        Path(self.tmp, "library/media.png").write_bytes(
            b"\x89PNG\r\n\x1a\n\x00private-binary-payload\xff"
        )
        code, out = run(self.tmp, "scrub_check.py")
        self.assertEqual(code, 1, out)
        self.assertIn("tracked content must be text", out)
        self.assertIn("seam", out)
        self.assertNotIn("private-binary-payload", out)

    def test_precommit_checks_integrity_without_running_development_suites(self):
        self.build_git_fixture()
        write(self.tmp, "tools/test_gate_corrections.py", "raise AssertionError('development suite should not run in an ordinary commit')\n")
        self.assertEqual(git(self.tmp, "add", "tools/test_gate_corrections.py").returncode, 0)
        hook = Path(__file__).resolve().parents[1] / ".githooks/pre-commit"
        result = subprocess.run(["sh", str(hook)], cwd=self.tmp,
                                capture_output=True, text=True, env=isolated_git_env())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reachability_is_local_to_each_member_entrance(self):
        # Per-member BFS prevents another entrance masking this disconnect.
        files = dict(CLEAN)
        files["shared-context/SHARED.md"] = """---
id: shared-entrance
type: doctrine
status: draft
description: >
  The shared entrance. Use when entering the commons. Not for workspace work
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Shared
"""
        files["shared-context/INDEX.md"] = """---
id: shared-index
type: doctrine
status: draft
description: >
  The shared index. Use when routing in the commons. Not for workspace work
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Shared index

- [door](SHARED.md)
- [identity](identity/README.md)
"""
        files["shared-context/identity/README.md"] = """---
id: shared-identity-index
type: identity
status: draft
description: >
  Shared identity. Use when routing identity. Not for workspace work
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Identity

- [note](note.md)
"""
        files["shared-context/identity/note.md"] = """---
id: shared-note
type: identity
status: draft
description: >
  A shared note. Use when testing reachability. Not for workspace work
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Note
"""
        build(self.tmp, files)
        self.assertEqual(run(self.tmp, "build_catalog.py")[0], 0)
        code, out = run(self.tmp, "check_loop.py")
        self.assertEqual(code, 1, out)
        self.assertIn("shared-context/SHARED.md", out)

    def test_direct_cross_member_link_is_rejected(self):
        files = dict(CLEAN)
        files["library/LIBRARY.md"] += (
            "\nDirect: [workspace](../workspace/70_seams/INDEX.md).\n"
        )
        build(self.tmp, files)
        self.assertEqual(run(self.tmp, "build_catalog.py")[0], 0)
        code, out = run(self.tmp, "check_loop.py")
        self.assertEqual(code, 1, out)
        self.assertIn("cross-member link", out)

    def test_draft_seam_requires_all_five_headings(self):
        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace("\n## Control point\n", "\n## Controls\n")
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py")
        self.assertEqual(code, 1, out)
        self.assertIn("five required seam headings", out)

    def test_approval_fields_after_frontmatter_are_rejected_explicitly(self):
        # Body-shaped YAML must not acquire approval authority as metadata.
        files = dict(CLEAN)
        files["workspace/80_governance/approvals/README.md"] = """---
id: approval-index
type: doctrine
status: draft
description: >
  Approval records. Use when checking approval. Not for session entry
  (see workspace/AGENTS.md).
updated: 2026-08-24
fields:
  - name: what
    for: approval
    required: true
  - name: packet
    for: approval
    required: true
  - name: class
    for: approval
    required: true
  - name: granted_by
    for: approval
    required: true
  - name: granted
    kind: date
    for: approval
    required: true
  - name: expiry
    kind: date
    for: approval
    required: true
---

# Approvals

<!-- lists: *.md -->
"""
        files["workspace/80_governance/approvals/2026-08-24-probe.md"] = """---
id: approval-probe
type: approval
status: mature
description: >
  Approval for a probe. Use when running the probe. Not for other actions
  (see README.md).
scope: workspace
updated: 2026-08-24
---

# Approval

what: run the probe
packet: DP-1
class: B
granted_by: A Human
granted: 2026-08-24
expiry: 2026-08-25
"""
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py")
        self.assertEqual(code, 1, out)
        self.assertIn("approval fields must be inside frontmatter", out)

    def test_canonical_schema_exists_and_drives_description_limit(self):
        source_root = Path(__file__).resolve().parents[1]
        schema_source = source_root / "doctrine/schema.json"
        self.assertTrue(schema_source.is_file())
        build(self.tmp, dict(CLEAN))
        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["limits"]["description_chars"] = 40
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("description", out)
        self.assertIn("40", out)

    def test_schema_drives_core_field_vocabulary(self):
        build(self.tmp, dict(CLEAN))
        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["fields"]["status"]["values"].remove("draft")
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("status 'draft'", out)

    def test_description_contract_is_normalized_and_bounded(self):
        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace(
            "The agent runtime seam. Use when wiring hooks. Not for all seams (see "
            "workspace/70_seams/INDEX.md).",
            "A " + "x" * 181
            + ".   Use when   wiring hooks. Not for all seams (see "
            "workspace/70_seams/INDEX.md).",
        )
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("description", out)
        self.assertIn("180", out)

        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace(
            "Not for all seams (see workspace/70_seams/INDEX.md).",
            "Not for all seams.",
        )
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("Not for", out)
        self.assertIn("(see", out)

        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace(
            "The agent runtime seam. Use when wiring hooks.",
            "The  agent runtime seam. Use when   wiring hooks.",
        )
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py")
        self.assertEqual(code, 0, out)
        catalog = json.loads(Path(self.tmp, "CATALOG.json").read_text())
        entry = next(
            item for item in catalog["entries"]
            if item["path"] == "workspace/70_seams/harness.md"
        )
        self.assertNotIn("  ", entry["description"])

    def test_description_routes_resolve_in_family(self):
        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace(
            "(see workspace/70_seams/INDEX.md).",
            "(see workspace/70_seams/INDEX.md); not for missing probes "
            "(see workspace/70_seams/missing-route.md).",
        )
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("description route", out)
        self.assertIn("missing-route.md", out)

    @unittest.skipUnless(OPTIONAL_SOURCE, "optional source packs are absent")
    def test_description_routes_resolve_after_member_extraction(self):
        source_root = SOURCE_ROOT
        probes = {
            "shared-context": "identity/README.md",
            "registry": "ledger.md",
            "library": "LIBRARY.md",
        }
        for member, rel in probes.items():
            with self.subTest(member=member):
                member_root = Path(self.tmp, member)
                shutil.copytree(source_root / member, member_root)
                shutil.copy2(source_root / "NAMESPACE.md", member_root)
                shutil.copy2(source_root / "LICENSE", member_root)
                build(member_root, {})
                target = member_root / rel
                target.write_text(
                    re.sub(
                        r"\(see [^)]+\)",
                        "(see missing-route.md)",
                        target.read_text(encoding="utf-8"),
                        count=1,
                    ),
                    encoding="utf-8",
                )
                code, out = run(member_root, "build_catalog.py", "--check")
                self.assertEqual(code, 1, out)
                self.assertIn("description route", out)
                self.assertIn("missing-route.md", out)

    def test_schema_drives_stale_field_format_and_comparison(self):
        files = dict(CLEAN)
        topic = (
            "library/fields/design/interface-design/typography-layout/README.md"
        )
        for rel in (topic, "library/inbox/2026-08-24-a-capture.md"):
            files[rel] = files[rel].replace(
                "review_after: 2020-01-01", "review_after: 01/01/2020"
            )
        build(self.tmp, files)
        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["formats"]["day-first"] = {
            "pattern": r"^\d{2}/\d{2}/\d{4}$",
            "message": "DD/MM/YYYY",
            "parse": {"kind": "strptime", "pattern": "%d/%m/%Y"},
        }
        schema["fields"]["review_after"]["format"] = "day-first"
        schema["stale"] = {
            "field": "review_after",
            "comparison": {"operator": "before", "reference": "today"},
            "exclude_statuses": ["reserved"],
            "exclude_path_prefixes": ["library/inbox/"],
        }
        schema_path.write_text(json.dumps(schema), encoding="utf-8")

        code, out = run(self.tmp, "build_catalog.py", "--stale")
        self.assertEqual(code, 0, out)
        self.assertIn(topic, out)

        schema["stale"]["comparison"]["operator"] = "sideways"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--stale")
        self.assertEqual(code, 1, out)
        self.assertIn("unsupported stale comparison", out)

    def test_malformed_stale_schema_fails_closed_without_traceback(self):
        # Shape-check every stale member before runtime consumption.
        build(self.tmp, dict(CLEAN))
        schema_path = Path(self.tmp, "doctrine/schema.json")
        original = json.loads(schema_path.read_text(encoding="utf-8"))
        valid = original["stale"]
        cases = (
            ("null", None, "stale must be an object"),
            ("list", [], "stale must be an object"),
            (
                "missing-field",
                {key: value for key, value in valid.items() if key != "field"},
                "stale missing keys: field",
            ),
            (
                "field-type",
                {**valid, "field": ["review_after"]},
                "stale field must be a non-empty string",
            ),
            (
                "unknown-field",
                {**valid, "field": "not_declared"},
                "stale field 'not_declared' is not declared",
            ),
            (
                "comparison-list",
                {**valid, "comparison": []},
                "stale comparison must be an object",
            ),
            (
                "missing-reference",
                {**valid, "comparison": {"operator": "before"}},
                "stale comparison missing keys: reference",
            ),
            (
                "reference-type",
                {
                    **valid,
                    "comparison": {"operator": "before", "reference": []},
                },
                "stale comparison reference must be a non-empty string",
            ),
            (
                "statuses-type",
                {**valid, "exclude_statuses": "reserved"},
                "stale exclude_statuses must be a list of strings",
            ),
            (
                "unknown-status",
                {**valid, "exclude_statuses": ["unknown"]},
                "stale exclude_statuses names unknown status 'unknown'",
            ),
            (
                "prefix-value",
                {**valid, "exclude_path_prefixes": [""]},
                "stale exclude_path_prefixes must be a list of non-empty strings",
            ),
        )
        for label, stale, expected in cases:
            with self.subTest(case=label):
                schema = json.loads(json.dumps(original))
                schema["stale"] = stale
                schema_path.write_text(json.dumps(schema), encoding="utf-8")
                code, out = run(self.tmp, "build_catalog.py", "--stale")
                self.assertEqual(code, 1, out)
                self.assertNotIn("Traceback", out)
                self.assertIn(expected, out)

        schema = json.loads(json.dumps(original))
        schema["fields"]["review_after"]["format"] = "not_declared"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--stale")
        self.assertEqual(code, 1, out)
        self.assertNotIn("Traceback", out)
        self.assertIn("stale field 'review_after' names unknown format", out)

        schema = json.loads(json.dumps(original))
        schema["formats"]["date"]["parse"]["kind"] = "not_supported"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--stale")
        self.assertEqual(code, 1, out)
        self.assertNotIn("Traceback", out)
        self.assertIn(
            "stale field 'review_after' names unsupported parser 'not_supported'",
            out,
        )

        schema = json.loads(json.dumps(original))
        schema["fields"]["status"]["values"] = None
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--stale")
        self.assertEqual(code, 1, out)
        self.assertNotIn("Traceback", out)
        self.assertIn("stale exclude_statuses requires a status vocabulary", out)

    def test_all_schema_container_shapes_fail_closed_without_traceback(self):
        build(self.tmp, dict(CLEAN))
        schema_path = Path(self.tmp, "doctrine/schema.json")
        original = json.loads(schema_path.read_text(encoding="utf-8"))
        cases = (
            ("required_fields", None),
            ("defaults", None),
            ("limits", None),
            ("formats", None),
            ("fields", None),
            ("field_kinds", None),
            ("type_fields", None),
            ("filing", None),
            ("constraints", None),
            ("uncapped", None),
        )
        for section, value in cases:
            with self.subTest(section=section):
                schema = json.loads(json.dumps(original))
                schema[section] = value
                schema_path.write_text(json.dumps(schema), encoding="utf-8")
                code, out = run(self.tmp, "build_catalog.py", "--check")
                self.assertEqual(code, 1, out)
                self.assertNotIn("Traceback", out)
                self.assertIn(f"{section} must be", out)

        nested = (
            ("limits", "description_chars", None),
            ("fields", "status", None),
            ("type_fields", "approval", None),
            ("formats", "date", None),
            ("filing", "library", None),
            ("uncapped", "types", None),
        )
        for section, member, value in nested:
            with self.subTest(section=section, member=member):
                schema = json.loads(json.dumps(original))
                schema[section][member] = value
                schema_path.write_text(json.dumps(schema), encoding="utf-8")
                code, out = run(self.tmp, "build_catalog.py", "--check")
                self.assertEqual(code, 1, out)
                self.assertNotIn("Traceback", out)
                self.assertIn(f"{section}.{member}", out)

        deep = (
            (
                ("fields", "description", "routing_ref_forms"),
                None,
                "fields.description.routing_ref_forms",
            ),
            (
                ("type_fields", "approval", "fields", "what"),
                None,
                "type_fields.approval.fields.what",
            ),
            (("filing", "chambers", 0), None, "filing.chambers"),
            (
                ("constraints", 0, "if", "field"),
                None,
                "constraints[0].if.field",
            ),
            (
                ("formats", "date", "parse"),
                [],
                "formats.date.parse",
            ),
            (
                ("filing", "shared_context", "bindings", 0, "pattern"),
                "[",
                "bindings[0].pattern is invalid",
            ),
        )
        for path, value, expected in deep:
            with self.subTest(path=path):
                schema = json.loads(json.dumps(original))
                target = schema
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = value
                schema_path.write_text(json.dumps(schema), encoding="utf-8")
                code, out = run(self.tmp, "build_catalog.py", "--check")
                self.assertEqual(code, 1, out)
                self.assertNotIn("Traceback", out)
                self.assertIn(expected, out)

    def test_type_fields_empty_lists_are_rejected(self):
        # An empty list silently disables the check it drives; reject it.
        build(self.tmp, dict(CLEAN))
        schema_path = Path(self.tmp, "doctrine/schema.json")
        original = json.loads(schema_path.read_text(encoding="utf-8"))
        cases = (
            (("type_fields", "approval", "required"), "type_fields.approval.required"),
            (("type_fields", "approval", "body_keys"), "type_fields.approval.body_keys"),
            (("type_fields", "handover", "required_all"),
             "type_fields.handover.required_all"),
            (("type_fields", "seam", "headings"), "type_fields.seam.headings"),
        )
        for path, expected in cases:
            with self.subTest(path=path):
                schema = json.loads(json.dumps(original))
                target = schema
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = []
                schema_path.write_text(json.dumps(schema), encoding="utf-8")
                code, out = run(self.tmp, "build_catalog.py", "--check")
                self.assertEqual(code, 1, out)
                self.assertNotIn("Traceback", out)
                self.assertIn(expected, out)

        schema = json.loads(json.dumps(original))
        schema["type_fields"]["seam"]["required_when"]["mature"] = []
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertNotIn("Traceback", out)
        self.assertIn("type_fields.seam.required_when", out)

    def test_minor_contract_wording_is_unambiguous(self):
        root = SOURCE_ROOT
        migrations = (root / "doctrine/migrations.md").read_text(encoding="utf-8")
        self.assertIn("old body unchanged", migrations)
        self.assertIn("closed_at", migrations)
        topic = (root / "_templates/topic.md").read_text(encoding="utf-8")
        self.assertIn("library/fields/{{FIELD}}/{{TOPIC}}/README.md", topic)
        seams_path = root / (
            "workspace/70_seams/INDEX.md" if FAMILY_SOURCE else "70_seams/INDEX.md"
        )
        seams = seams_path.read_text(encoding="utf-8")
        self.assertIn("doctrine/schema.json", seams)
        self.assertNotIn("declared in this door's frontmatter", seams)
        media_path = root / "library/doctrine/media-and-rights.md"
        if media_path.is_file():
            media = media_path.read_text(encoding="utf-8")
            self.assertIn("tracked workspace content is text-only", media.lower())

    def test_schema_drives_type_to_chamber_routing(self):
        build(self.tmp, dict(CLEAN))
        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["filing"]["type_chambers"]["seam"] = "40_knowledge"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("belongs in 40_knowledge/", out)

    @unittest.skipUnless(OPTIONAL_SOURCE, "shared-context source pack is absent")
    def test_schema_drives_shared_context_filing_family_and_extracted(self):
        source_root = SOURCE_ROOT

        build(self.tmp, dict(CLEAN))
        placeholders = Path(self.tmp, "workspace/00_meta/placeholders.md")
        placeholders.write_text(
            placeholders.read_text(encoding="utf-8")
            + "\n| `<<WORKSPACE_ID>>` | fixture |\n"
            + "| `<<WORKSPACE_PATH>>` | fixture |\n"
            + "| `<<SHARED_CONTEXT_PATH>>` | fixture |\n"
            + "| `<<OBJECTION_WINDOW_HOURS>>` | fixture |\n",
            encoding="utf-8",
        )
        shutil.copytree(
            source_root / "shared-context", Path(self.tmp, "shared-context")
        )
        identity = Path(self.tmp, "shared-context/identity/README.md")
        identity.write_text(
            identity.read_text(encoding="utf-8").replace(
                "type: identity", "type: policy"
            ),
            encoding="utf-8",
        )
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("shared-context/identity/README.md", out)
        self.assertIn("requires type 'identity'", out)

        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        identity_rule = next(
            rule for rule in schema["filing"]["shared_context"]["bindings"]
            if rule["pattern"] == "^identity/.*\\.md$"
        )
        identity_rule["types"] = ["policy"]
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)

        extracted = Path(self.tmp, "extracted-shared")
        shutil.copytree(source_root / "shared-context", extracted)
        shutil.copy2(source_root / "NAMESPACE.md", extracted)
        shutil.copy2(source_root / "LICENSE", extracted)
        build(extracted, {})
        identity = extracted / "identity/README.md"
        identity.write_text(
            identity.read_text(encoding="utf-8").replace(
                "type: identity", "type: policy"
            ),
            encoding="utf-8",
        )
        code, out = run(extracted, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("identity/README.md", out)
        self.assertIn("requires type 'identity'", out)

    def test_schema_drives_cross_field_constraints(self):
        files = dict(CLEAN)
        files["library/inbox/2026-08-24-a-capture.md"] = files[
            "library/inbox/2026-08-24-a-capture.md"
        ].replace("status: draft", "status: draft\nload: always")
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("load: always requires status: mature", out)

        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["constraints"][0]["if"]["equals"] = "disabled"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)

    def test_schema_drives_field_format_assignment(self):
        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace("updated: 2026-08-24", "updated: soon")
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("updated 'soon' is not YYYY-MM-DD", out)

        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["formats"]["word"] = {
            "pattern": "^(soon|\\d{4}-\\d{2}-\\d{2})$",
            "message": "word or date",
        }
        schema["fields"]["updated"]["format"] = "word"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)

    def test_schema_defaults_are_materialized_in_catalogs(self):
        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"
        ].replace("status: draft\n", "status: draft\n")
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py")
        self.assertEqual(code, 0, out)
        catalog = json.loads(Path(self.tmp, "CATALOG.json").read_text())
        entry = next(
            item for item in catalog["entries"]
            if item["path"] == "workspace/70_seams/harness.md"
        )
        self.assertEqual(entry["load"], "cue")
        self.assertIs(entry["tokens"], False)

        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["defaults"]["load"] = "drill"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py")
        self.assertEqual(code, 0, out)
        catalog = json.loads(Path(self.tmp, "CATALOG.json").read_text())
        entry = next(
            item for item in catalog["entries"]
            if item["path"] == "workspace/70_seams/harness.md"
        )
        self.assertEqual(entry["load"], "drill")

    def test_schema_type_requirements_apply_without_door_duplication(self):
        files = dict(CLEAN)
        files["workspace/80_governance/approvals/README.md"] = """---
id: approval-index
type: doctrine
status: draft
description: Approval records. Use when checking approval. Not for session entry (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Approvals

- [probe](probe.md)
"""
        files["workspace/80_governance/approvals/probe.md"] = """---
id: approval-probe
type: approval
status: mature
description: Probe approval. Use when running the probe. Not for other actions (see README.md).
scope: workspace
what: run probe
packet: DP-1
class: B
granted_by: Human
granted: 2026-08-24
updated: 2026-08-24
---

# Approval
"""
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("missing required field 'expiry'", out)

        schema_path = Path(self.tmp, "doctrine/schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["type_fields"]["approval"]["required"].remove("expiry")
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 0, out)

    def test_deepest_door_governs_a_shared_field_name(self):
        # Two doors in one lineage declare 'risk' for type seam; the
        # deeper door (narrower values) must win, not scan order.
        files = dict(CLEAN)
        files["workspace/70_seams/INDEX.md"] = files[
            "workspace/70_seams/INDEX.md"
        ].replace(
            "fields:\n  - name: verified_on\n    kind: date\n    for: seam\n",
            "fields:\n  - name: verified_on\n    kind: date\n    for: seam\n"
            "  - name: risk\n    kind: string\n    values: [low, high]\n"
            "    for: seam\n",
        )
        files["workspace/70_seams/sub/INDEX.md"] = """---
id: seams-sub-index
type: doctrine
status: draft
description: >
  A nested seam door. Use when a subtree needs a narrower rule. Not for
  the chamber map (see ../INDEX.md).
updated: 2026-08-24
fields:
  - name: risk
    kind: string
    values: [low]
    for: seam
---

# Sub seams

- [deep](deep.md)
"""
        files["workspace/70_seams/sub/deep.md"] = """---
id: seam-sub-deep
type: seam
status: draft
description: >
  A nested seam. Use when testing door precedence. Not for the chamber
  door (see INDEX.md).
updated: 2026-08-24
risk: high
---

# Deep

## What crosses
Nothing.
## Direction
None.
## Inspect point
None.
## Control point
None.
## What never crosses
Everything.
"""
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("risk 'high' not in", out)

    def test_approval_body_key_detection_allows_space_before_colon(self):
        files = dict(CLEAN)
        files["workspace/80_governance/approvals/README.md"] = """---
id: approval-index
type: doctrine
status: draft
description: Approval records. Use when checking approval. Not for session entry (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Approvals

- [probe](probe.md)
"""
        files["workspace/80_governance/approvals/probe.md"] = """---
id: approval-probe
type: approval
status: mature
description: Probe approval. Use when running the probe. Not for other actions (see README.md).
scope: workspace
what: run probe
packet: DP-1
class: B
granted_by: Human
granted: 2026-08-24
expiry: 2026-08-25
updated: 2026-08-24
---

# Approval

what   : shadowed value
"""
        build(self.tmp, files)
        code, out = run(self.tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("approval fields must be inside frontmatter", out)

    @unittest.skipUnless(OPTIONAL_SOURCE, "library source pack is absent")
    def test_optional_pack_validation_requires_canonical_schema(self):
        source_root = SOURCE_ROOT
        member_tmp = Path(self.tmp, "library-pack")
        shutil.copytree(source_root / "library", member_tmp)
        shutil.copy2(source_root / "NAMESPACE.md", member_tmp)
        shutil.copy2(source_root / "LICENSE", member_tmp)
        build(member_tmp, {})
        schema_path = member_tmp / "doctrine/schema.json"
        self.assertTrue(schema_path.is_file())
        schema_path.unlink()
        code, out = run(member_tmp, "build_catalog.py", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("doctrine/schema.json", out)

    def test_every_kit_example_satisfies_the_description_rule(self):
        """A kit whose own example the validator rejects teaches the defect.

        The example frontmatter lives inside a fence, so `strip_fences` hides
        it from the ordinary pass; nothing else would ever catch the drift.
        """
        sys.path.insert(0, str(SOURCE_ROOT / "tools"))
        import build_catalog

        pattern = build_catalog.FIELD_RULES["description"]["routing_pattern"]
        kits = sorted(SOURCE_ROOT.glob("_templates/*.md"))
        kits += sorted(SOURCE_ROOT.glob("_templates/*/*.md"))
        checked = 0
        for kit in kits:
            for block in re.findall(r"```markdown\n(.*?)```", kit.read_text(),
                                    re.S):
                example = build_catalog.parse_frontmatter(block)
                desc = " ".join(str((example or {}).get("description", "")).split())
                if not desc:
                    continue
                checked += 1
                with self.subTest(kit=kit.name):
                    self.assertRegex(desc, pattern)
        self.assertGreater(checked, 5)

    @unittest.skipUnless(FAMILY_SOURCE, "family layout holds the token registry")
    def test_tool_fixtures_keep_their_registered_token_literals(self):
        """Instantiation must not eat the tokens the negative tests plant.

        `tools/` declares no `tokens: true`, so it is not a consumer — but a
        family-wide grep-and-replace would still hit it, and an
        `<<PRINCIPAL_NAME>>` turned into a name silently converts two planted
        defects into clean text while the suite keeps reporting pass.
        """
        registered = set(re.findall(
            r"<<([A-Z][A-Z_]+)>>",
            (SOURCE_ROOT / "workspace/00_meta/placeholders.md").read_text()))
        self.assertIn("PRINCIPAL_NAME", registered)
        for name in ("test_gates.py", "test_gate_corrections.py"):
            text = (SOURCE_ROOT / "tools" / name).read_text()
            planted = set(re.findall(r"<<([A-Z][A-Z_]+)>>", text)) & registered
            with self.subTest(fixture=name):
                self.assertTrue(
                    planted,
                    f"tools/{name} carries no registered token literal — "
                    "instantiation has substituted the planted defect away")

    def test_every_kit_lists_exactly_the_markers_it_uses(self):
        """A kit's `Markers:` line is its interface; drift makes it a lie.

        The filer reads that line to know what to supply. A marker used in
        the record or the destination but missing from the line is a step
        nobody performs; a listed marker nothing uses is a question nobody
        needs to answer.
        """
        copy_to = re.compile(r"\*\*Copy to:\*\*\s*\n?\s*`([^`]+)`")
        marker = re.compile(r"\{\{([A-Z_]+)\}\}")
        kits = sorted(SOURCE_ROOT.glob("_templates/*.md"))
        kits += sorted(SOURCE_ROOT.glob("_templates/*/*.md"))
        checked = 0
        for kit in kits:
            text = kit.read_text()
            fence = re.search(r"```markdown\n(.*?)```", text, re.S)
            destination = copy_to.search(text)
            line = re.search(r"^\*\*Markers:\*\*.*$", text, re.M)
            if not (fence and destination):
                continue
            checked += 1
            with self.subTest(kit=kit.name):
                self.assertIsNotNone(line, "a kit with a destination lists its markers")
                used = set(marker.findall(fence.group(1) + destination.group(1)))
                self.assertEqual(used, set(marker.findall(line.group(0))))
        self.assertGreaterEqual(checked, 14)


if __name__ == "__main__":
    unittest.main(verbosity=2)
