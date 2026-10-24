"""mager-bench 2: repair small repositories, then handle a second work order."""
import argparse
import json
from pathlib import Path
from agent_bench_v2.tasks import TASKS, reference_sources, PHASE_SECONDS, RUN_SECONDS
from agent_bench_v2.grader import grade
from agent_bench_v2.runner import ROOT, fingerprint, lowest_effort, run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model')
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--level',type=int,choices=(1,2,3),default=1)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--smoke',action='store_true',help='One 30-second file-edit probe, unscored')
    parser.add_argument('--self-test',action='store_true',help='Check reference code locally; no model calls')
    parser.add_argument('--replay',type=Path,help='Regrade a saved artifact locally; no model calls')
    args=parser.parse_args()
    if not 0<=args.seed<2**32: parser.error('--seed must be uint32')
    if args.self_test:
        for task in TASKS:
            for phase in (1,2):
                score=grade(task['id'],reference_sources(task['id']),args.seed,args.level,phase)
                print(f"{task['id']} / {phase}: {score['passed']}/{score['total']}")
                if score['passed']!=score['total']:
                    print(json.dumps([c for c in score['cases'] if not c['passed']],indent=2))
                    return 1
        return 0
    if args.replay:
        from agent_bench_v2.evidence import validate
        validate(json.loads(args.replay.read_text()))
        print('Evidence verified and completed phases regraded')
        return 0
    if not args.model: parser.error('--model codex-cli/<id> is required')
    try: effort,_=lowest_effort(args.model)
    except (OSError,ValueError,KeyError) as exc: parser.error(str(exc))
    print(f'mager-bench 2.0: {1 if args.smoke else 6} sessions, 0 judges; effort={effort}; seed={args.seed}; level={args.level}')
    print(f'Budget: {30 if args.smoke else PHASE_SECONDS}s/session; {30 if args.smoke else RUN_SECONDS}s shared; 192 checks per full evaluation')
    print(f'Suite: {fingerprint()}')
    if args.dry_run: return 0
    if not args.output: parser.error('--output is required; dry-run first')
    path=args.output.resolve()
    if path.parent!=(ROOT/'runs/v2').resolve() or path.suffix!='.json' or path.exists():
        parser.error('Use a new .json file directly under runs/v2/')
    payload=run(args.model,path,args.seed,args.level,args.smoke)
    return 0 if payload['status']=='completed' else 1


if __name__=='__main__': raise SystemExit(main())
