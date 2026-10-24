"""Subscription-only Codex execution. No provider fallback or retry loop."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from importlib.metadata import version as package_version
from . import VERSION
from .tasks import TASKS, PHASE_SECONDS, RUN_SECONDS, prompt
from .workspace import prepare, write_order, snapshot, integrity_errors
from .grader import grade

ROOT = Path(__file__).resolve().parents[1]
EFFORTS = ['none','minimal','low','medium','high','xhigh','max','ultra']


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def fingerprint():
    paths = [ROOT/'bench_v2.py',ROOT/'requirements-v2.txt']
    paths += sorted((ROOT/'agent_bench_v2').rglob('*.py'))
    paths += sorted((ROOT/'agent_bench_v2').rglob('*.js'))
    h = hashlib.sha256()
    for path in paths:
        h.update(path.relative_to(ROOT).as_posix().encode()+b'\0'+path.read_bytes()+b'\0')
    return h.hexdigest()


def environment():
    # Inherit only runtime essentials, never API keys, gateways, or workload identity.
    allowed = ('PATH','HOME','USER','LOGNAME','TMPDIR','LANG','LC_ALL','SYSTEMROOT','CODEX_HOME')
    return {key:os.environ[key] for key in allowed if key in os.environ}


def lowest_effort(model):
    if not model.startswith('codex-cli/') or not model.removeprefix('codex-cli/'):
        raise ValueError('Use an explicit codex-cli/<model>')
    home = Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    data = json.loads((home/'models_cache.json').read_text())
    entry = next((m for m in data['models'] if m['slug']==model.removeprefix('codex-cli/')),None)
    if not entry: raise ValueError('Model is absent from the local catalog; no substitution')
    levels = [r['effort'] for r in entry['supported_reasoning_levels']]
    if not levels or any(level not in EFFORTS for level in levels): raise ValueError('Unknown effort metadata')
    return min(levels,key=EFFORTS.index),levels


def preflight():
    env = environment()
    login = subprocess.run(['codex','login','status'],env=env,capture_output=True,text=True,timeout=15)
    if login.returncode or 'Logged in using ChatGPT' not in login.stdout+login.stderr:
        raise RuntimeError('ChatGPT login required. Run codex login. API authentication is not allowed.')
    def ver(command):
        return subprocess.check_output(command,env=env,text=True,timeout=15).strip()
    return dict(codex=ver(['codex','--version']),node=ver(['node','--version']),
                python=platform.python_version(),quickjs=package_version('quickjs'),
                system=platform.system(),machine=platform.machine())


def command(model,effort,workspace,answer):
    argv = ['codex','exec','--ephemeral','--ignore-user-config','--ignore-rules',
            '--skip-git-repo-check','--sandbox','workspace-write','--cd',str(workspace),
            '--model',model.removeprefix('codex-cli/'),'--json','--color','never',
            '--output-last-message',str(answer)]
    settings = [f'model_reasoning_effort="{effort}"','model_provider="openai"',
                'forced_login_method="chatgpt"','approval_policy="never"',
                'sandbox_workspace_write.network_access=false','web_search="disabled"',
                'project_doc_max_bytes=0','features.multi_agent=false','features.apps=false']
    for setting in settings: argv.extend(['-c',setting])
    return argv+['-']


def invoke(model,effort,workspace,directory,phase,timeout):
    answer = directory/f'answer-{phase}.txt'
    out,err = directory/f'events-{phase}.jsonl',directory/f'stderr-{phase}.txt'
    argv = command(model,effort,workspace,answer)
    started = time.monotonic()
    failure = None
    with out.open('w') as stdout,err.open('w') as stderr:
        process = subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,
                                   env=environment(),text=True,start_new_session=True)
        try:
            process.communicate('Read WORK_ORDER.md and complete it in this repository. Run the tests.\n',timeout=timeout)
        except (subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
            os.killpg(process.pid,signal.SIGKILL)
            process.wait()
            failure = 'Generation budget exhausted' if isinstance(exc,subprocess.TimeoutExpired) else 'Interrupted'
    events = []
    if out.stat().st_size > 8*1024*1024:
        failure = 'CLI event log exceeded 8 MiB'
    else:
        for line in out.read_text().splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: failure = 'Invalid CLI JSON event'
    final = answer.read_text() if answer.is_file() and answer.stat().st_size<=128*1024 else ''
    completed = [e for e in events if e.get('type')=='turn.completed']
    errors = [e for e in events if e.get('type') in ('turn.failed','error')]
    if process.returncode or not completed or errors or not final.strip():
        failure = failure or 'Codex call failed or did not complete'
    return dict(status='failed' if failure else 'completed',error=failure,
                elapsed_ms=round((time.monotonic()-started)*1000),events=events,
                stderr=err.read_text()[-16000:],response=final,
                usage=completed[-1].get('usage',{}) if completed else {},
                command_count=sum(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' for e in events))


def save(path,payload):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    temp.replace(path)


def patch(before,after):
    chunks = []
    for name in sorted(set(before)|set(after)):
        chunks.extend(difflib.unified_diff(before.get(name,'').splitlines(True),after.get(name,'').splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    return ''.join(chunks)


def run(model,output,seed,level,smoke=False):
    effort,levels = lowest_effort(model)
    payload = dict(benchmark_version=VERSION,kind='preflight' if smoke else 'evaluation',
                   source='chatgpt-subscription',model=model,reasoning_effort=effort,supported_efforts=levels,
                   seed=seed,level=level,suite_sha256=fingerprint(),
                   generated_at=datetime.now(timezone.utc).isoformat(),
                   phase_seconds=PHASE_SECONDS,budget_seconds=RUN_SECONDS,
                   status='running',score=None,tasks=[])
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f: json.dump(payload,f,indent=2)
    started=time.monotonic()
    remaining=RUN_SECONDS
    try:
        payload['runtime']=preflight();save(output,payload)
        if smoke:
            with tempfile.TemporaryDirectory(prefix='mager-v2-smoke-') as temp:
                directory=Path(temp);workspace=directory/'repo';workspace.mkdir()
                (workspace/'WORK_ORDER.md').write_text('Create probe.txt containing exactly OK. Read it with a shell command. Reply OK. Do not access other paths.')
                result=invoke(model,effort,workspace,directory,0,30)
                payload['probe']=result
                remaining-=result['elapsed_ms']/1000
                valid=(workspace/'probe.txt').is_file() and (workspace/'probe.txt').read_text().strip()=='OK'
                if result['status']!='completed' or not valid: raise RuntimeError(result.get('error') or 'CLI file-edit probe failed')
        else:
            for task in TASKS:
                with tempfile.TemporaryDirectory(prefix='mager-v2-task-') as temp:
                    directory=Path(temp);workspace=directory/'repo'
                    locked=prepare(workspace,task['id'])
                    before=snapshot(workspace)
                    row=dict(id=task['id'],phases=[]);payload['tasks'].append(row)
                    for phase in (1,2):
                        if remaining<=0: raise RuntimeError('Total generation budget exhausted')
                        write_order(workspace,task['id'],phase)
                        order=dict(phase=phase,prompt=prompt(task['id'],phase),status='running',score=None)
                        row['phases'].append(order);save(output,payload)
                        result=invoke(model,effort,workspace,directory,phase,min(PHASE_SECONDS,remaining))
                        remaining-=result['elapsed_ms']/1000
                        order.update(result)
                        try:
                            after=snapshot(workspace)
                            integrity=integrity_errors(workspace,locked)
                        except (ValueError,OSError,UnicodeError) as exc:
                            after={};integrity=[str(exc)]
                        order.update(sources=after,source_sha256=digest(after),diff=patch(before,after),integrity_errors=integrity)
                        if result['status']!='completed':
                            save(output,payload)
                            raise RuntimeError(result['error'])
                        score=grade(task['id'],after,seed,level,phase)
                        if integrity:
                            score['passed']=0
                            for case in score['cases']: case.update(passed=False,error='Workspace integrity violation')
                        order['score']=score
                        before=after;save(output,payload)
                        print(f"{task['id']} / {phase}: {score['passed']}/{score['total']} ({result['elapsed_ms']/1000:.1f}s)",flush=True)
            phases=[p for t in payload['tasks'] for p in t['phases']]
            payload['score']=dict(passed=sum(p['score']['passed'] for p in phases),total=192,
                                 tasks_passed=sum(all(p['score']['passed']==p['score']['total'] for p in t['phases']) for t in payload['tasks']),tasks_total=3)
        payload['status']='completed'
    except (Exception,KeyboardInterrupt) as exc:
        payload.update(status='failed',score=None,error=str(exc) or type(exc).__name__)
        for task in payload['tasks']:
            for phase in task['phases']:
                if phase['status']=='running' or (phase['status']=='completed' and phase['score'] is None):
                    phase.update(status='failed',error=payload['error'],score=None)
    payload.update(elapsed_ms=round((time.monotonic()-started)*1000),generation_ms=round((RUN_SECONDS-remaining)*1000))
    save(output,payload)
    print(f"{payload['status']}: {output}",flush=True)
    return payload
