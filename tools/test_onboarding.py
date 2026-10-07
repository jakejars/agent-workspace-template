#!/usr/bin/env python3
"""Focused regressions for the two-phase onboarding lifecycle."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_instance  # noqa: E402


class OnboardingLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="workspace-onboarding-")
        self.root = os.path.join(self.home, "my-workspace")
        os.makedirs(self.root)
        test_instance.clone_source(self.root)
        test_instance.answer_interview(self.root, self.home)

    def tearDown(self):
        shutil.rmtree(self.home)

    def run_instantiation(self, *args):
        return test_instance.run(self.root, "instantiate.py", *args)

    def fill(self):
        code, out = self.run_instantiation("--date", test_instance.TODAY)
        self.assertEqual(code, 0, out)

    def add_first_intent(self):
        for kit, record, destination in test_instance.kits(self.root):
            if kit.endswith("intent.md"):
                test_instance.place(self.root, kit, record, destination)
                return
        self.fail("intent kit was not found")

    def test_fill_keeps_sentinel_and_check_refuses_unfinished_workspace(self):
        """Catches deterministic fill incorrectly claiming readiness."""
        self.fill()

        sentinel = Path(self.root, "workspace/00_meta/.uninitialised")
        marker = Path(self.root, "workspace/00_meta/.initializing")
        self.assertTrue(sentinel.is_file())
        self.assertEqual(
            json.loads(marker.read_text(encoding="utf-8")),
            {
                "version": 1,
                "state": "filled",
                "workspace_id": "okoro-consulting",
                "started_on": test_instance.TODAY,
            },
        )
        code, out = self.run_instantiation("--check")
        self.assertEqual(code, 1, out)
        self.assertIn("finalize", out.lower())

    def test_finalize_requires_first_active_intent(self):
        """Catches removal of onboarding markers before intent exists."""
        self.fill()

        code, out = self.run_instantiation("--finalize", "--hooks", "portable")

        self.assertEqual(code, 1, out)
        self.assertIn("first active intent", out.lower())
        self.assertTrue(Path(self.root, "workspace/00_meta/.uninitialised").is_file())
        self.assertTrue(Path(self.root, "workspace/00_meta/.initializing").is_file())

    def test_finalize_requires_explicit_hook_disposition(self):
        """Catches silent assumptions about runtime or portable hook wiring."""
        self.fill()
        self.add_first_intent()

        code, out = self.run_instantiation("--finalize")

        self.assertEqual(code, 1, out)
        self.assertIn("--hooks", out)
        self.assertTrue(Path(self.root, "workspace/00_meta/.uninitialised").is_file())

    def test_failed_finalize_leaves_both_markers_for_retry(self):
        """Catches a gate failure turning an interrupted setup into a ready one."""
        self.fill()
        self.add_first_intent()
        Path(self.root, "workspace/20_intent/active/broken.md").write_text(
            "# Missing required frontmatter\n", encoding="utf-8"
        )

        code, out = self.run_instantiation("--finalize", "--hooks", "portable")

        self.assertEqual(code, 1, out)
        self.assertIn("finalization gate", out.lower())
        self.assertTrue(Path(self.root, "workspace/00_meta/.uninitialised").is_file())
        self.assertTrue(Path(self.root, "workspace/00_meta/.initializing").is_file())

    def test_explicit_empty_private_policy_can_finalize_without_fabricated_term(self):
        self.fill()
        test_instance.seed_journal(self.root)
        test_instance.file_every_kit(self.root)
        test_instance.work_a_session(self.root)
        Path(self.root, ".workspace-private/never-share.txt").unlink()
        Path(self.root, ".workspace-private/no-private-terms.json").write_text('{"version":1,"confirmed":true}\n')
        code,out=self.run_instantiation("--finalize","--hooks","portable")
        self.assertEqual(code,0,out)
        code,out=self.run_instantiation("--check")
        self.assertEqual(code,0,out)

    def test_ready_receipt_is_validated_instead_of_trusted_by_existence(self):
        self.fill()
        test_instance.seed_journal(self.root)
        test_instance.file_every_kit(self.root)
        test_instance.work_a_session(self.root)
        self.assertEqual(self.run_instantiation("--finalize","--hooks","portable")[0],0)
        Path(self.root,"workspace/00_meta/ready.json").write_text('{"version":99}')
        code,out=self.run_instantiation("--check")
        self.assertNotEqual(code,0,out)
        self.assertIn('receipt',out)

    def test_interrupted_fill_can_finish_remaining_tokens(self):
        self.fill()
        marker=Path(self.root,"workspace/00_meta/.initializing")
        state=json.loads(marker.read_text())
        state['state']='filling'
        marker.write_text(json.dumps(state))
        principal=Path(self.root,"workspace/10_identity/principal.md")
        principal.write_text(principal.read_text().replace('Jane Okoro','<<PRINCIPAL_NAME>>'))
        code,out=self.run_instantiation()
        self.assertEqual(code,0,out)
        self.assertNotIn('<<PRINCIPAL_NAME>>',principal.read_text())
        self.assertTrue(Path(self.root,"workspace/00_meta/.uninitialised").exists())

    def test_interrupted_finalize_is_detected_and_can_resume(self):
        self.fill()
        test_instance.seed_journal(self.root)
        test_instance.file_every_kit(self.root)
        test_instance.work_a_session(self.root)
        marker = Path(self.root, "workspace/00_meta/.initializing")
        state = marker.read_text()
        self.assertEqual(self.run_instantiation("--finalize", "--hooks", "portable")[0], 0)
        # Reproduce an interruption after the sentinel was removed but before
        # the fill checkpoint was removed.
        marker.write_text(state)
        code, out = self.run_instantiation("--check")
        self.assertNotEqual(code, 0, out)
        code, out = self.run_instantiation("--finalize", "--hooks", "portable")
        self.assertEqual(code, 0, out)
        self.assertFalse(marker.exists())
        self.assertEqual(self.run_instantiation("--check")[0], 0)

    def test_minimal_fill_only_requires_name_and_workspace_id(self):
        """Catches optional identity and family links blocking local use."""
        values = Path(self.root, "workspace/00_meta/values.json")
        values.write_text(
            '{"PRINCIPAL_NAME":"Jane Okoro","WORKSPACE_ID":"local-notes"}\n',
            encoding="utf-8",
        )

        code, out = self.run_instantiation(
            "--minimal", "--date", test_instance.TODAY
        )

        self.assertEqual(code, 0, out)
        saved = json.loads(values.read_text(encoding="utf-8"))
        self.assertEqual(saved["PRINCIPAL_EMAIL"], "")
        self.assertEqual(saved["ORG_NAME"], "")
        self.assertEqual(saved["MACHINE_FILE"], "")
        self.assertEqual(saved["WORKSPACE_PATH"], "")
        self.assertTrue(Path(self.root, "workspace/00_meta/.uninitialised").is_file())


if __name__ == "__main__":
    unittest.main()
