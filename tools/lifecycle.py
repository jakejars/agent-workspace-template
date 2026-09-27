#!/usr/bin/env python3
"""Agent-neutral lifecycle bridge. No runtime payloads or account settings.

start: validate graph and surface bounded active-task cues
prompt --query TEXT [--task ID]: route relevant context (never choose a task)
changed: cheap dirty hint after a write, no validation or output
close: validate and refresh only when sources changed
status: distinguish local Git configuration from observed event receipts
Any runtime may call these commands. stdin --json accepts event/query/task.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
import context as routing

ROOT=routing.ROOT
RECEIPTS=ROOT/'.sett-cache/lifecycle.json'
DIRTY=ROOT/'.sett-cache/dirty'


def receipts():
    try:
        data=json.loads(RECEIPTS.read_text())
        return data if isinstance(data,dict) else {}
    except (OSError,ValueError):
        return {}


def record(event,code,rebuilt=False):
    data=receipts()
    data[event]={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'exit_code':code,'refreshed':rebuilt}
    routing.atomic_write(RECEIPTS,json.dumps(data,indent=2)+'\n')


def status():
    r=subprocess.run(['git','config','--get','core.hooksPath'],cwd=ROOT,capture_output=True,text=True)
    configured=r.stdout.strip() if r.returncode==0 else 'not configured'
    lines=[f'Git hooks configured: {configured}',
           'Runtime lifecycle wiring: caller-specific; receipts below prove invocation, not future wiring.']
    for event, info in sorted(receipts().items()):
        lines.append(f"{event}: observed {info['observed_at']}; exit {info['exit_code']}; refreshed={info['refreshed']}")
    if not receipts():
        lines.append('No lifecycle events observed.')
    return '\n'.join(lines)


def dispatch(event,query='',task=None):
    if event=='status':
        return status()
    if event=='changed':
        DIRTY.parent.mkdir(parents=True,exist_ok=True)
        DIRTY.touch()
        record(event,0)
        return ''
    try:
        data,rebuilt=routing.refresh()
        if DIRTY.exists():
            DIRTY.unlink()
        record(event,0,rebuilt)
        if event in {'start','prompt'}:
            return routing.show(data,task,query)
        return ''
    except (OSError,ValueError,KeyError,TypeError):
        record(event,1)
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('event',nargs='?',choices=['start','prompt','changed','close','status','checkout','merge','commit'])
    parser.add_argument('--query',default='')
    parser.add_argument('--task')
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.json:
            payload=json.load(sys.stdin)
            if not isinstance(payload,dict):
                raise ValueError('Expected a lifecycle object.')
            event=payload.get('event')
            query=payload.get('query','')
            task=payload.get('task')
        else:
            event,query,task=args.event,args.query,args.task
        if event not in {'start','prompt','changed','close','status','checkout','merge','commit'}:
            parser.error('Select a lifecycle event.')
        if not isinstance(query,str) or (task is not None and not isinstance(task,str)):
            raise ValueError('query and task must be strings.')
        output=dispatch(event,query,task)
        if output:
            print(output)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(f'lifecycle: {exc}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
