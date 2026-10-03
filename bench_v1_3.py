"""Fast practical and algorithmic coding benchmark. ChatGPT subscription only; no model judges."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from everyday_v1_3.tasks import TASKS
from everyday_v1_3.grader import grade

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / 'runs/v1.3'
EFFORT_ORDER = ['none','minimal','low','medium','high','xhigh','max','ultra']
CALL_TIMEOUT_SECONDS = 90
OUTPUT_TOKEN_TARGET = 3072
GENERATION_BUDGET_SECONDS = 270

def fingerprint():
    h = hashlib.sha256()
    for name in ('everyday_v1_3/tasks.py','everyday_v1_3/grader.py','bench_v1_3.py','providers.py','requirements-v1.3.txt','requirements-v1.2.txt','everyday_v1_2/tasks.py'):
        h.update(name.encode() + b'\0' + (ROOT / name).read_bytes() + b'\0')
    return h.hexdigest()

def lowest_effort(model):
    cache = Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))) / 'models_cache.json'
    catalog = json.loads(cache.read_text())
    entry = next((m for m in catalog['models'] if m['slug'] == model.removeprefix('codex-cli/')), None)
    if entry is None: raise ValueError('Model missing from local Codex catalog; refresh it before running')
    levels = [item['effort'] for item in entry['supported_reasoning_levels']]
    if not levels or any(level not in EFFORT_ORDER for level in levels):
        raise ValueError('Unknown effort metadata; cannot verify lowest supported effort')
    return min(levels,key=EFFORT_ORDER.index), levels

def run(model, output, effort, levels):
    from providers import CodexCLIProvider, has_key
    payload = dict(benchmark_version='1.3',model=model,generated_at=datetime.now(timezone.utc).isoformat(),
        suite_sha256=fingerprint(),source='subscription',reasoning_effort=effort,supported_efforts=levels,
        effort_policy='lowest supported in local Codex catalog',output_token_target=OUTPUT_TOKEN_TARGET,
        call_timeout_seconds=CALL_TIMEOUT_SECONDS,generation_budget_seconds=GENERATION_BUDGET_SECONDS,status='running',score=None,tasks=[])
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f: json.dump(payload,f,indent=2)
    def save():
        temp = output.with_suffix('.tmp')
        temp.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
        temp.replace(output)
    started = time.perf_counter()
    try:
        if not has_key('codex-cli'): raise RuntimeError('ChatGPT CLI login required')
        provider = CodexCLIProvider(model.removeprefix('codex-cli/'),reasoning_effort=effort,timeout=CALL_TIMEOUT_SECONDS)
        remaining = GENERATION_BUDGET_SECONDS
        for task in TASKS:
            if remaining <= 0:
                payload.update(status='failed',error='Total generation waiting budget exhausted')
                break
            provider.timeout = min(CALL_TIMEOUT_SECONDS,remaining)
            row = dict(id=task['id'],prompt=task['prompt'],status='running',response='',score=None)
            payload['tasks'].append(row)
            save()
            called = time.perf_counter()
            try:
                row['response'] = provider.complete(task['prompt'],max_tokens=OUTPUT_TOKEN_TARGET)
                row['subject_elapsed_ms'] = round((time.perf_counter()-called)*1000)
                remaining -= (time.perf_counter()-called)
                row['score'] = grade(task['id'],row['response'])
                row['status'] = 'completed'
            except (RuntimeError, ValueError) as exc:
                row.update(status='failed',error=str(exc),subject_elapsed_ms=round((time.perf_counter()-called)*1000))
                payload.update(status='failed',error=str(exc))
                # Stop on transport/format failure; preserve remaining tasks as not run.
                break
            save()
        else:
            payload.update(status='completed',score=dict(passed=sum(t['score']['passed'] for t in payload['tasks']),total=60))
    except (Exception, KeyboardInterrupt) as exc:
        payload.update(status='failed',error=str(exc) or type(exc).__name__)
    payload['elapsed_ms'] = round((time.perf_counter()-started)*1000)
    if payload['status'] != 'completed':
        payload['score'] = None
        for row in payload['tasks']:
            if row['status'] == 'running': row.update(status='interrupted',error='Run interrupted')
    save()
    print(f"{payload['status']}: {output}")
    print(payload.get('error') or payload['score'])
    return 0 if payload['status'] == 'completed' else 1

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True)
    p.add_argument('--output')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if not a.model.startswith('codex-cli/') or not a.model.removeprefix('codex-cli/'):
        p.error('Only codex-cli/ ChatGPT subscription subjects are supported')
    try: effort,levels=lowest_effort(a.model)
    except (OSError,ValueError,KeyError) as exc: p.error(str(exc))
    print(f'mager-bench 1.3: 5 subject calls maximum, 0 judge calls, 60 checks')
    print(f'Effort: {effort} (lowest listed); 90s deadline/call; 270s total generation waiting; 3072-token prompted target')
    print(f'Suite: {fingerprint()}')
    if a.dry_run: return 0
    if not a.output: p.error('--output is required')
    output=Path(a.output).resolve()
    if output.parent != RUNS.resolve() or output.suffix != '.json' or output.exists():
        p.error('Use a new .json filename directly under runs/v1.3/')
    return run(a.model,output,effort,levels)

if __name__ == '__main__': raise SystemExit(main())
