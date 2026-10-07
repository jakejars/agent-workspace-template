#!/usr/bin/env python3
"""Exercise actual Git hook dispatch and neutral lifecycle wiring."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import test_context

class HookTests(unittest.TestCase):
    def setUp(self):
        test_context.ContextTests.setUp(self)
        src=Path(__file__).resolve().parents[1]
        shutil.copytree(src/'.githooks',self.root/'.githooks')
        shutil.copytree(src/'tools/hooks',self.root/'tools/hooks')
        (self.root/'workspace/00_meta/.uninitialised').touch()
        self.git('init','-q')
        self.git('config','user.name','Hook Fixture')
        self.git('config','user.email','hook@example.invalid')

    def git(self,*args):
        return subprocess.run(['git',*args],cwd=self.root,capture_output=True,text=True)

    def test_git_commit_and_checkout_fire_refresh_with_receipts(self):
        p=subprocess.run([sys.executable,str(self.root/'tools/hooks/install.py')],cwd=self.root,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.git('add','-A')
        p=self.git('commit','-qm','fixture')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        data=json.loads((self.root/'.workspace-cache/lifecycle.json').read_text())
        self.assertEqual(data['commit']['exit_code'],0)
        p=self.git('checkout','-qb','check-hooks')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        data=json.loads((self.root/'.workspace-cache/lifecycle.json').read_text())
        self.assertEqual(data['checkout']['exit_code'],0)
        p=self.root/'workspace/70_seams/SHARED.md'
        p.write_text(p.read_text()+'\nA verified fixture note.\n')
        self.git('add','-A')
        result=self.git('commit','-qm','branch change')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.git('checkout','-').returncode,0)
        result=self.git('merge','--ff-only','check-hooks')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        data=json.loads((self.root/'.workspace-cache/lifecycle.json').read_text())
        self.assertEqual(data['merge']['exit_code'],0)


    def test_installer_preserves_another_hooks_directory(self):
        self.git('config','core.hooksPath','custom-hooks')
        p=subprocess.run([sys.executable,str(self.root/'tools/hooks/install.py')],cwd=self.root,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(self.git('config','--get','core.hooksPath').stdout.strip(),'custom-hooks')

    def test_adapter_start_and_close_follow_neutral_protocol(self):
        shim=self.root/'tools/hooks/shim.py'
        def send(event):
            return subprocess.run([sys.executable,str(shim),'lifecycle'],cwd=self.root,
                input=json.dumps({'hook_event_name':event}),capture_output=True,text=True)
        p=send('SessionStart')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['hookSpecificOutput']['hookEventName'],'SessionStart')
        p=send('Stop')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(p.stdout.strip(),'')
        self.assertIn('close',json.loads((self.root/'.workspace-cache/lifecycle.json').read_text()))

    def test_adapter_intervals_and_failure_diagnostics(self):
        shim = self.root/'tools/hooks/shim.py'
        settings = json.loads((self.root/'tools/hooks/settings-example.json').read_text())
        events = {'SessionStart':'start', 'UserPromptSubmit':'prompt',
                  'PostToolUse':'changed', 'Stop':'close', 'PreCompact':'close',
                  'SessionEnd':'close'}
        def send(event, **extra):
            return subprocess.run([sys.executable, str(shim), 'lifecycle'], cwd=self.root,
                input=json.dumps({'hook_event_name':event, 'prompt':'fixture', **extra}),
                capture_output=True, text=True)
        for event, neutral in events.items():
            with self.subTest(event=event):
                self.assertIn(event, settings['hooks'])
                result = send(event)
                self.assertEqual(result.returncode, 0, result.stderr)
                receipts = json.loads((self.root/'.workspace-cache/lifecycle.json').read_text())
                self.assertEqual(receipts[neutral]['exit_code'], 0)
                if event in {'SessionStart','UserPromptSubmit'}:
                    self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['hookEventName'], event)
        source = self.root/'workspace/AGENTS.md'
        source.write_text(source.read_text()+'\n[broken](absent.md)\n')
        result = send('Stop')
        self.assertEqual(result.returncode, 2, result.stdout+result.stderr)
        self.assertIn('dead link', result.stderr)
        self.assertEqual(send('Stop', stop_hook_active=True).returncode, 0)
        result = send('UserPromptSubmit')
        self.assertEqual(result.returncode, 0)
        self.assertIn('validation failed', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])
        receipts = json.loads((self.root/'.workspace-cache/lifecycle.json').read_text())
        self.assertEqual(receipts['close']['exit_code'], 1)

if __name__=='__main__': unittest.main()
