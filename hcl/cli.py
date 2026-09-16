import argparse
import asyncio
import json
import os
from pathlib import Path
from uuid import uuid4
from .bus import ThoughtBus
from .engine import Director, canonical, digest
from .models import Evidence
from .providers import NativeAgent, SupabaseStore


def export(bundle, root):
    if digest(bundle['payload']) != bundle['sha256']:
        raise ValueError('Bundle digest mismatch')
    folder = Path(root) / bundle['payload']['run_id']
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'bundle.json').write_bytes(canonical(bundle))
    body = bundle['payload']
    lines = ['# i Ecosystem — research disclosure draft', '', f"Status: {body['status']}", '', body['scope'], '', f"SHA-256: {bundle['sha256']}"]
    for attempt in body['history']:
        lines += ['', f"## Attempt {attempt['loop']}"]
        for artifact in attempt['artifacts']:
            lines += ['', '### '+artifact['title'], '', artifact['abstract'], '', artifact['description'], '', '#### Proposed claims']
            lines += [f"{c['number']}. {c['text']}" for c in artifact['claims']]
        lines += ['', '### Committee findings', '', json.dumps(attempt['reviews'], indent=2)]
    (folder/'disclosure.md').write_text('\n'.join(lines), encoding='utf-8')
    return folder

async def run(args):
    evidence = [Evidence.model_validate(e) for e in json.loads(Path(args.evidence).read_text(encoding='utf-8'))] if args.evidence else []
    run_id = str(uuid4())
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    agent = NativeAgent(os.environ.get('NATIVE_API_BASE','https://api.openai.com/v1'), os.environ.get('NATIVE_API_KEY',''), os.environ.get('NATIVE_MODEL',''))
    bus = ThoughtBus(root/'events.sqlite', run_id)
    store = None
    try:
        bundle = await Director(agent,bus,evidence,args.max_loops).run(args.directive)
        folder = export(bundle, root)
        print(f"{bundle['payload']['status']}: {folder}")
        if args.supabase:
            store = SupabaseStore(os.environ['SUPABASE_URL'],os.environ['SUPABASE_SECRET_KEY'])
            await store.save(run_id,bundle['payload'],bundle['sha256'])
            print('Supabase receipt stored')
        return 0 if bundle['payload']['status'] == 'REVIEW_READY' else 2
    finally:
        bus.close()
        await agent.close()
        if store:
            await store.close()

def main():
    parser = argparse.ArgumentParser(description='i Ecosystem evidence-bound Director')
    parser.add_argument('--directive',required=True)
    parser.add_argument('--evidence',help='JSON array of sourced Evidence records')
    parser.add_argument('--output',default='runs')
    parser.add_argument('--max-loops',type=int,default=4)
    parser.add_argument('--supabase',action='store_true')
    raise SystemExit(asyncio.run(run(parser.parse_args())))

if __name__ == '__main__':
    main()
