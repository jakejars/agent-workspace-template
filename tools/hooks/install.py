#!/usr/bin/env python3
"""Install or inspect project-local, runtime-neutral Git lifecycle hooks.

No account settings are changed. An existing non-Sett hooksPath is preserved.
Run lifecycle.py status separately for evidence of actual event invocation.
"""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
NAMES=('pre-commit','post-commit','post-checkout','post-merge')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    p=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=ROOT,capture_output=True,text=True)
    if p.returncode or Path(p.stdout.strip()).resolve()!=ROOT:
        print('Run from a Sett Git root; no configuration changed.',file=sys.stderr)
        return 1
    p=subprocess.run(['git','config','--get','core.hooksPath'],cwd=ROOT,capture_output=True,text=True)
    existing=p.stdout.strip()
    if existing and Path(existing if Path(existing).is_absolute() else ROOT/existing).resolve()!=ROOT/'.githooks':
        print('Another hooks directory is configured; preserve it and chain the Sett commands manually.',file=sys.stderr)
        return 1
    missing=[n for n in NAMES if not (ROOT/'.githooks'/n).is_file()]
    if missing:
        print('Missing shipped Git hooks: '+', '.join(missing),file=sys.stderr)
        return 1
    if args.check:
        if not existing or any(not (ROOT/'.githooks'/n).stat().st_mode & 0o111 for n in NAMES):
            print('Git hooks are not installed and executable.',file=sys.stderr)
            return 1
    else:
        for n in NAMES:
            p=ROOT/'.githooks'/n
            p.chmod(p.stat().st_mode|0o111)
        p=subprocess.run(['git','config','--local','core.hooksPath','.githooks'],cwd=ROOT)
        if p.returncode: return p.returncode
    print('Git hooks configured: staged validation before commit; context refresh after commit, checkout, and merge. '
          'No runtime session hooks were installed. Check lifecycle.py status for observed events.')
    return 0

if __name__=='__main__': sys.exit(main())
