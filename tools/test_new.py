#!/usr/bin/env python3
"""Regressions for the novice creation flow (tools/new.py) and root semantics.

  python3 tools/test_new.py

Each workspace-building test drives `tools/new.py` itself, so the wizard, the
orchestration and the gates are exercised the way a novice hits them. Layout
refusals are asserted at the SettLayout/refusal level and, where cheap, by
running the real command.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.dirname(TOOLS)

sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from sett_layout import SettLayout, refuse_unknown  # noqa: E402
import sett_setup  # noqa: E402


def new(*args):
    return subprocess.run(
        [sys.executable, os.path.join(SOURCE, "tools", "new.py"), *args],
        cwd=SOURCE, capture_output=True, text=True)


def run_tool(root, tool, *args):
    proc = subprocess.run([sys.executable, os.path.join(root, "tools", tool),
                           *args], cwd=root, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def build(home, name="demo-sett", privacy=("--no-private-terms",),
          *flags):
    args = [os.path.join(home, name),
            "--name", "Demo User",
            "--workspace-id", name,
            "--goal", "Build and maintain my project",
            "--hooks", "portable",
            "--non-interactive", *privacy, *flags]
    return subprocess.run(
        [sys.executable, os.path.join(SOURCE, "tools", "new.py"), *args],
        cwd=SOURCE, capture_output=True, text=True)


class NewWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = tempfile.mkdtemp(prefix="sett-new-")
        cls.result = build(cls.home)
        cls.root = Path(cls.home, "demo-sett")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.home, ignore_errors=True)

    def test_happy_path_exit_zero(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertIn("Sett workspace ready", self.result.stdout)
        self.assertIn("Read AGENTS.md", self.result.stdout)

    def test_generated_shape_is_extracted(self):
        for rel in ("AGENTS.md", "00_meta", "70_seams", "tools", "doctrine",
                    "NAMESPACE.md", "README.md", "20_intent"):
            self.assertTrue((self.root / rel).exists(), rel)
        self.assertFalse((self.root / "workspace").exists())
        body = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("boot_static", body)
        self.assertNotIn("Maintaining Sett", body)   # not the family entrance

    def test_optional_packs_absent_and_seams_closed(self):
        for pack in ("shared-context", "registry", "library"):
            self.assertFalse((self.root / pack).exists(), pack)
        for seam in ("shared-context.md", "registry.md", "library.md"):
            head = (self.root / "70_seams" / seam).read_text(encoding="utf-8")
            self.assertIn("status: stub", head.split("---", 2)[1], seam)

    def test_values_hold_identity_and_no_private_data(self):
        values = json.loads((self.root / "00_meta/values.json").read_text())
        self.assertEqual(values["PRINCIPAL_NAME"], "Demo User")
        self.assertEqual(values["WORKSPACE_ID"], "demo-sett")
        for empty in ("PRINCIPAL_EMAIL", "ORG_NAME", "MACHINE_FILE",
                      "WORKSPACE_PATH", "SHARED_CONTEXT_PATH",
                      "REGISTRY_PATH", "LIBRARY_PATH"):
            self.assertEqual(values.get(empty), "", empty)
        raw = (self.root / "00_meta/values.json").read_text()
        self.assertNotIn("never-share", raw.lower())

    def test_explicit_no_private_terms_confirmation(self):
        choice = self.root / ".sett-private/no-private-terms.json"
        self.assertEqual(choice.read_text(encoding="utf-8").strip(),
                         '{"version": 1, "confirmed": true}')
        self.assertFalse((self.root / ".sett-private/never-share.txt").exists())
        proc = subprocess.run(["git", "check-ignore", "-q",
                               ".sett-private/never-share.txt"],
                              cwd=self.root)
        self.assertEqual(proc.returncode, 0, ".sett-private is not ignored")

    def test_readiness_after_creation(self):
        self.assertFalse((self.root / "00_meta/.uninitialised").exists())
        self.assertFalse((self.root / "00_meta/.initializing").exists())
        receipt = json.loads((self.root / "00_meta/ready.json").read_text())
        self.assertEqual(receipt["version"], 1)
        self.assertEqual(receipt["hooks"], "portable")
        code, out = run_tool(self.root, "instantiate.py", "--check")
        self.assertEqual(code, 0, out)

    def test_hooks_installed_locally(self):
        code, out = run_tool(self.root, "hooks/install.py", "--check")
        self.assertEqual(code, 0, out)
        proc = subprocess.run(["git", "config", "--local", "core.hooksPath"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(proc.stdout.strip(), ".githooks")

    def test_first_intent_captures_the_goal(self):
        intents = [p for p in (self.root / "20_intent/active").glob("*.md")
                   if p.name != "README.md"]
        self.assertTrue(intents, "no active intent was created")
        text = intents[0].read_text(encoding="utf-8")
        self.assertIn("Build and maintain my project", text)
        self.assertIn("lifecycle: captured", text)
        self.assertNotIn("{{", text)
        self.assertNotIn("<preference>", text)
        head = text.split("---", 2)[1]
        self.assertIn("type: intent", head)
        self.assertIn("status: draft", head)

    def test_gates_and_doctor_pass_inside_the_instance(self):
        for tool, args in (("build_catalog.py", ("--check",)),
                           ("check_loop.py", ()),
                           ("scrub_check.py", ()),
                           ("agnostic_check.py", ()),
                           ("doctor.py", ())):
            code, out = run_tool(self.root, tool, *args)
            self.assertEqual(code, 0, f"{tool}: {out}")

    def test_source_checkout_untouched_by_creation(self):
        self.assertTrue((Path(SOURCE) / "workspace/00_meta/.uninitialised")
                        .is_file())
        self.assertFalse((Path(SOURCE) / "workspace/00_meta/values.json")
                         .exists())
        fixtures = (Path(SOURCE) / "tools/test_gates.py").read_text()
        self.assertIn("<<PRINCIPAL_NAME>>", fixtures)


class PrivacyTermsTests(unittest.TestCase):
    """The term path: stored only in the ignored store, never echoed."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="sett-new-terms-")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_private_terms_stay_out_of_tracked_output(self):
        term = "zz-" + "arcnine-private"      # constructed, never a fixture
        result = build(self.home, "terms-sett",
                       privacy=("--private-terms", term))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(term, result.stdout)
        self.assertNotIn(term, result.stderr)
        root = Path(self.home, "terms-sett")
        store = root / ".sett-private/never-share.txt"
        self.assertIn(term, store.read_text(encoding="utf-8"))
        self.assertFalse((root / ".sett-private/no-private-terms.json")
                         .exists())
        self.assertNotIn(term,
                         (root / "00_meta/values.json").read_text())
        code, out = run_tool(root, "scrub_check.py")
        self.assertEqual(code, 0, out)
        self.assertNotIn(term, out)           # diagnostics never print values

    def test_unusable_private_term_is_refused(self):
        result = build(self.home, "bad-terms",
                       privacy=("--private-terms", "n/a"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse((Path(self.home, "bad-terms")).exists())


class TopologyRefusalTests(unittest.TestCase):
    """Fail closed: ambiguous destinations are refused, nothing is created."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="sett-new-topo-"))

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_rejects_destination_inside_source_checkout(self):
        target = Path(SOURCE) / "my-workspace"
        result = new(str(target), "--non-interactive")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source checkout", result.stderr)
        self.assertFalse(target.exists())

    def test_rejects_nested_sett(self):
        outer = self.home / "outer"
        outer.mkdir()
        (outer / "NAMESPACE.md").write_text("# Namespace\n")
        (outer / "AGENTS.md").write_text("# x\n")
        (outer / "00_meta").mkdir()
        (outer / "70_seams").mkdir()
        result = new(str(outer / "inner"), "--non-interactive")
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertFalse((outer / "inner").exists())

    def test_rejects_non_empty_target_and_preserves_it(self):
        target = self.home / "occupied"
        target.mkdir()
        keeper = target / "keep-me.txt"
        keeper.write_text("mine\n")
        result = new(str(target), "--non-interactive")
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertEqual(keeper.read_text(), "mine\n")

    def test_rejects_filesystem_root(self):
        result = new("/", "--non-interactive")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_answers_refused_non_interactively(self):
        result = new(str(self.home / "partial"), "--non-interactive")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("--name", result.stderr)
        self.assertFalse((self.home / "partial").exists())


class LayoutSemanticsTests(unittest.TestCase):
    """Unknown layouts are never silently family roots (fail closed)."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="sett-layout-"))

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_plain_directory_is_unknown(self):
        plain = self.home / "plain"
        plain.mkdir()
        self.assertEqual(SettLayout(plain).kind, "unknown")
        self.assertEqual(SettLayout(plain).member, None)
        self.assertFalse(SettLayout(plain).is_sett_root)
        message = refuse_unknown(SettLayout(plain), "build_catalog")
        self.assertIn("not a Sett workspace or Sett source checkout", message)

    def test_container_of_setts_is_not_one_sett(self):
        container = self.home / "setts"
        for name in ("alpha", "beta"):
            member = container / name
            member.mkdir(parents=True)
            (member / "NAMESPACE.md").write_text("# Namespace\n")
            (member / "AGENTS.md").write_text("# entrance\n")
            (member / "00_meta").mkdir()
            (member / "70_seams").mkdir()
        self.assertEqual(SettLayout(container).kind, "unknown")

    def test_commands_refuse_a_copied_toolset_in_an_unknown_root(self):
        plain = self.home / "plain"
        tools = plain / "tools"
        tools.mkdir(parents=True)
        for name in ("sett_layout.py", "doctor.py", "scrub_check.py"):
            shutil.copy2(Path(TOOLS) / name, tools / name)
        proc = subprocess.run([sys.executable, str(tools / "doctor.py")],
                              cwd=plain, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("not a Sett workspace", proc.stderr)


class InteractiveParityTests(unittest.TestCase):
    """Piped answers take the same internal path as flags (sett_setup)."""

    def test_wizard_answers_via_stdin_build_the_same_workspace(self):
        home = tempfile.mkdtemp(prefix="sett-new-wizard-")
        try:
            target = os.path.join(home, "wizard-sett")
            answers = "\n".join([
                "Wanda",                 # what should your agent call you?
                "",                      # workspace id: dirname default
                "Water the garden",      # first objective
                "1",                     # no private terms
            ]) + "\n"
            proc = subprocess.run(
                [sys.executable, os.path.join(SOURCE, "tools", "new.py"),
                 target],
                input=answers, cwd=SOURCE, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0,
                             proc.stdout + proc.stderr)
            root = Path(target)
            values = json.loads((root / "00_meta/values.json").read_text())
            self.assertEqual(values["PRINCIPAL_NAME"], "Wanda")
            self.assertEqual(values["WORKSPACE_ID"], "wizard-sett")
            self.assertTrue((root / "00_meta/ready.json").is_file())
            intents = [p for p in (root / "20_intent/active").glob("*.md")
                       if p.name != "README.md"]
            self.assertTrue(intents)
            self.assertIn("Water the garden", intents[0].read_text())
            self.assertTrue((root / ".sett-private/no-private-terms.json")
                            .is_file())
        finally:
            shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
