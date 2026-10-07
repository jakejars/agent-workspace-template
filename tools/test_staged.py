#!/usr/bin/env python3
"""The commit gate must validate the index, independent of working-tree repairs."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
from test_gates import CLEAN, build

class StagedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        build(self.tmp.name,CLEAN)
        for name in ('check_staged.py','journal_guard.py'):
            p=Path(__file__).parent/name
            if p.exists(): shutil.copy2(p,self.root/'tools'/name)
        (self.root/'.gitignore').write_text('.workspace-private/\n')
        (self.root/'workspace/00_meta/.uninitialised').touch()
        self.git('init','-q')
        self.git('config','user.name','Gate Fixture')
        self.git('config','user.email','fixture@example.invalid')
        self.git('add','-A')
        self.git('-c','core.hooksPath=/dev/null','commit','-qm','baseline')

    def git(self,*args):
        p=subprocess.run(['git',*args],cwd=self.root,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        return p.stdout

    def gate(self):
        return subprocess.run([sys.executable,str(self.root/'tools/check_staged.py')],cwd=self.root,text=True,capture_output=True)

    def test_invalid_staged_metadata_cannot_hide_behind_repaired_worktree(self):
        p=self.root/'workspace/70_seams/SHARED.md'
        original=p.read_text()
        p.write_text(original.replace('status: mature','status: broken'))
        self.git('add',str(p))
        p.write_text(original)
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('status',result.stdout+result.stderr)

    def test_valid_index_ignores_unstaged_broken_metadata(self):
        p=self.root/'workspace/70_seams/SHARED.md'
        p.write_text(p.read_text().replace('status: mature','status: broken'))
        result=self.gate()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_staged_symlink_cannot_escape_snapshot(self):
        (self.root/'escape').symlink_to('../outside')
        self.git('add','escape')
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('symlink',result.stdout+result.stderr)

    def test_initial_commit_and_index_graph_are_checked(self):
        p=self.root/'workspace/AGENTS.md'
        original=p.read_text()
        p.write_text(original+'\n[broken](absent.md)\n')
        self.git('add',str(p))
        p.write_text(original)
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('dead link',result.stdout+result.stderr)

if __name__=='__main__': unittest.main()
