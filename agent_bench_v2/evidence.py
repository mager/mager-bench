"""Strict regrading before any result is published."""
from . import VERSION
from .tasks import TASKS, PHASE_SECONDS, RUN_SECONDS, prompt
from .runner import fingerprint, digest, EFFORTS
from .grader import grade


def require(condition,message):
    if not condition: raise ValueError(message)


def validate(run):
    require(run['benchmark_version']==VERSION,'Version mismatch')
    historical_probe=run['kind']=='preflight' and run['status']=='failed'
    require(historical_probe or run['suite_sha256']==fingerprint(),'Suite mismatch')
    require(run['kind'] in ('preflight','evaluation'),'Unknown artifact kind')
    require(run['source']=='chatgpt-subscription' and run['model'].startswith('codex-cli/'),'Subscription source required')
    levels=run['supported_efforts']
    require(bool(levels) and all(e in EFFORTS for e in levels),'Invalid catalog evidence')
    require(run['reasoning_effort']==min(levels,key=EFFORTS.index),'Effort must be lowest supported')
    require(type(run['seed']) is int and 0<=run['seed']<2**32 and type(run['level']) is int and run['level'] in (1,2,3),'Invalid cohort')
    require(run['phase_seconds']==PHASE_SECONDS and run['budget_seconds']==RUN_SECONDS,'Budget mismatch')
    require(run['status'] in ('completed','failed'),'Unfinished run')
    require(isinstance(run['elapsed_ms'],int) and run['elapsed_ms']>=0,'Invalid elapsed time')
    if run['kind']=='preflight':
        require(run['score'] is None and run['tasks']==[],'Preflight must remain unscored')
        return
    require(len(run['tasks'])<=len(TASKS),'Too many tasks')
    failed=False
    for index,row in enumerate(run['tasks']):
        task=TASKS[index]
        require(row['id']==task['id'] and 1<=len(row['phases'])<=2,'Task order mismatch')
        for phase_index,phase in enumerate(row['phases'],1):
            require(not failed,'Run continued after failure')
            require(phase['phase']==phase_index and phase['prompt']==prompt(task['id'],phase_index),'Work order mismatch')
            if phase['status']=='completed':
                require(phase['source_sha256']==digest(phase['sources']),'Source hash mismatch')
                require(any(e.get('type')=='turn.completed' for e in phase['events']) and not any(e.get('type') in ('error','turn.failed') for e in phase['events']),'Missing successful CLI completion')
                require(bool(phase['response'].strip()),'Missing final response')
                require(0<=phase['elapsed_ms']<=(PHASE_SECONDS+5)*1000,'Phase exceeded budget')
                expected=grade(task['id'],phase['sources'],run['seed'],run['level'],phase_index)
                if phase.get('integrity_errors'):
                    expected['passed']=0
                    for case in expected['cases']: case.update(passed=False,error='Workspace integrity violation')
                require(phase['score']==expected,'Regraded score mismatch')
            else:
                require(phase['status']=='failed' and phase.get('error') and phase['score'] is None,'Invalid failed phase')
                failed=True
        if index<len(run['tasks'])-1:
            require(len(row['phases'])==2,'Skipped phase')
    if run['status']=='completed':
        require(run['generation_ms']==sum(p['elapsed_ms'] for t in run['tasks'] for p in t['phases']),'Generation time mismatch')
        require(len(run['tasks'])==3 and all(len(t['phases'])==2 for t in run['tasks']) and not failed,'Missing completed work')
        score=dict(passed=sum(p['score']['passed'] for t in run['tasks'] for p in t['phases']),total=192,
                   tasks_passed=sum(all(p['score']['passed']==32 for p in t['phases']) for t in run['tasks']),tasks_total=3)
        require(run['score']==score,'Overall score mismatch')
        require(run['generation_ms']<=RUN_SECONDS*1000+5000,'Run exceeded shared budget')
    else:
        require(run['score'] is None and run.get('error'),'Failed run must be unscored')
