"""Seeded evaluation inputs. All expectations come from independent Python oracles."""
import hashlib
import random
from copy import deepcopy
from .oracles import ORACLES
from .tasks import LEVELS, CASES_PER_PHASE


def rng_for(task, seed, level, phase):
    raw = f'mager-bench/2.0/{task}/{seed}/{level}/{phase}'.encode()
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest(), 'big'))


def ledger_edges(phase):
    move = dict(id='x', **{'from': 'a', 'to': 'b', 'amount': 3})
    base = dict(balances={'a': 10, 'b': 0}, events=[])
    events = [[], [move], [move, move], [dict(move, amount=20), move],
              [move, dict(move, amount=100)], [dict(move, amount=10)],
              [dict(move, amount=11)], [move,dict(id='y', **{'from':'b','to':'a','amount':3})]]
    if phase == 2:
        batch = dict(id='batch', moves=[dict(move),dict(move, amount=20)])
        events = [[batch], [batch,dict(batch,moves=[dict(move)])],
                  [dict(id='batch',moves=[dict(move),dict(move)])],
                  [dict(move,expected={'a':1})], [move,dict(move,expected={'a':99})],
                  [dict(id='empty',moves=[]),dict(id='empty',moves=[])],
                  [move,dict(move,id='y',expected={'a':1,'b':1})],
                  [dict(id='net',moves=[dict(move),{'from':'b','to':'a','amount':3}])]]
    return [dict(deepcopy(base), events=deepcopy(e)) for e in events]


def ledger_random(rng, level, phase):
    size, steps = LEVELS[level]
    keys = [f'a{i:03}' for i in range(size)]
    balances = {k:rng.randrange(0,100) for k in keys}
    events = []
    for i in range(steps):
        a,b = rng.sample(keys,2)
        event = dict(id=f'e{rng.randrange(max(2,i+1)):04}', **{'from':a,'to':b,'amount':rng.randrange(1,80)})
        if phase == 2:
            if rng.random() < .6:
                moves = []
                for _ in range(rng.randrange(0,6)):
                    a,b = rng.sample(keys,2)
                    moves.append({'from':a,'to':b,'amount':rng.randrange(1,80)})
                event = dict(id=event['id'],moves=moves)
            if rng.random() < .4:
                event['expected'] = {rng.choice(keys):rng.randrange(0,4)}
        events.append(event)
    return dict(balances=balances,events=events)


def build_edges(phase):
    nodes = [dict(id='a',deps=[],revision=0),dict(id='b',deps=['a'],revision=0),dict(id='c',deps=['a','b'],revision=0),dict(id='z',deps=[],revision=0)]
    req = lambda targets=['c'],changes=[]: dict(targets=targets,changes=changes)
    requests = [[req()], [req(),req()], [req(),req(changes=[dict(id='a',revision=1)])],
                [req(),req(changes=[dict(id='z',revision=1)])], [req([])],
                [req(['b']),req(['c'])], [req(),req(changes=[dict(id='a',revision=0)])],
                [req(),req(changes=[dict(id='c',revision=1)]),req(changes=[dict(id='c',revision=0)])]]
    if phase == 2:
        requests = [[req(),req(changes=[dict(id='b',deps=[])])],
                    [req(),req(changes=[dict(id='c',deps=['b','a','b'])])],
                    [req(changes=[dict(id='a',deps=['c'])])],
                    [req(changes=[dict(id='z',deps=['z'])])],
                    [req(),req(changes=[dict(id='a',deps=['c'],revision=1)]),req(changes=[dict(id='a',deps=[])])],
                    [req([],[dict(id='a',deps=['a'])])],
                    [req(),req(changes=[dict(id='c',deps=['z'])])],
                    [req(),req(changes=[dict(id='b',deps=[])]),req(changes=[dict(id='b',deps=['a'])])]]
    result = [dict(nodes=deepcopy(nodes),requests=deepcopy(r)) for r in requests]
    # Exponentially many paths, but only 80 nodes.
    if phase == 1:
        graph = [dict(id=f'n{i:03}',deps=[] if i<2 else [f'n{((i//2)-1)*2:03}',f'n{((i//2)-1)*2+1:03}'],revision=0) for i in range(80)]
        result[-1] = dict(nodes=graph,requests=[req(['n078','n079']),req(['n079'])])
    return result


def build_random(rng, level, phase):
    size, steps = LEVELS[level]
    ids = [f'n{i:03}' for i in range(size)]
    nodes = [dict(id=k,deps=rng.sample(ids[:i],min(i,rng.randrange(0,5))),revision=0) for i,k in enumerate(ids)]
    requests = []
    for _ in range(max(8,steps//4)):
        changes = []
        for _ in range(rng.randrange(0,4)):
            change = dict(id=rng.choice(ids),revision=rng.randrange(0,4))
            if phase == 2 and rng.random() < .5:
                change['deps'] = rng.choices(ids,k=rng.randrange(0,4))
            changes.append(change)
        requests.append(dict(changes=changes,targets=rng.choices(ids,k=rng.randrange(0,4))))
    return dict(nodes=nodes,requests=requests)


def policy_edges(phase):
    allow = dict(effect='allow',tenant='t',resource='doc',action='read')
    query = dict(user='u',tenant='t',resource='doc',action='read',time=10)
    base = dict(roles=[dict(id='r',parents=[],rules=[allow]),dict(id='p',parents=[],rules=[])],users=[dict(id='u',roles=['r'])],queries=[query,dict(query,tenant='other'),dict(query,user='missing')])
    result = [deepcopy(base) for _ in range(8)]
    if phase == 1:
        result[1]['roles'][0]['rules'].append(dict(allow,effect='deny'))
        result[2]['roles'][0]['rules'][0].update(resource='*',action='*')
        result[3]['roles'][0]['rules'][0]['tenant'] = '*'
        result[4]['users'][0]['roles'] = []
        result[5]['users'][0]['roles'] = ['r','r']
        result[6]['roles'][0]['rules'][0]['resource'] = 'do'
        result[7]['roles'][1]['rules'] = [dict(allow,effect='deny')]
        result[7]['users'][0]['roles'] = ['r','p']
    else:
        result[0]['roles'][0]['rules'][0]['until'] = 10
        result[1]['roles'][0]['rules'].append(dict(allow,effect='deny',until=10))
        result[2]['roles'][1]['parents'] = ['r']
        result[2]['users'][0]['roles'] = ['p']
        result[3]['roles'][0]['parents'] = ['p']; result[3]['roles'][1]['parents'] = ['r']
        result[4]['roles'][1]['parents'] = ['p']  # unrelated cycle
        result[5]['roles'][0]['parents'] = ['p','p']; result[5]['roles'][1]['rules'] = [dict(allow,effect='deny')]
        result[6]['roles'][0]['rules'][0]['until'] = 11
        result[7]['roles'][0]['parents'] = ['r']
    return result


def policy_random(rng, level, phase):
    size, steps = LEVELS[level]
    ids = [f'r{i:03}' for i in range(size)]
    roles = []
    for i,k in enumerate(ids):
        rules = []
        for _ in range(rng.randrange(0,6)):
            rule = dict(effect=rng.choice(['allow','deny']),tenant=rng.choice(['a','b','*']),resource=rng.choice(['doc','bill','*']),action=rng.choice(['read','write','*']))
            if phase == 2 and rng.random()<.5:
                rule['until'] = rng.randrange(0,5)
            rules.append(rule)
        parents = rng.choices(ids[:i],k=rng.randrange(0,4)) if phase==2 and i else []
        roles.append(dict(id=k,parents=parents,rules=rules))
    if phase == 2 and rng.random()<.5:
        roles[rng.randrange(size)]['parents'].append(rng.choice(ids))
    users = [dict(id=f'u{i}',roles=rng.choices(ids,k=rng.randrange(0,4))) for i in range(8)]
    queries = [dict(user=f'u{rng.randrange(10)}',tenant=rng.choice(['a','b','*']),resource=rng.choice(['doc','bill']),action=rng.choice(['read','write']),time=rng.randrange(0,7)) for _ in range(steps)]
    # Every generated case includes one allow and one deny. Constant-deny code cannot pass.
    roles.append(dict(id='sentinel',parents=[],rules=[dict(effect='allow',tenant='sentinel',resource='doc',action='read')]))
    users.append(dict(id='sentinel',roles=['sentinel']))
    queries.extend([dict(user='sentinel',tenant='sentinel',resource='doc',action='read',time=0),dict(user='sentinel',tenant='sentinel',resource='doc',action='write',time=0)])
    return dict(roles=roles,users=users,queries=queries)


EDGES = {'event-ledger':ledger_edges,'build-cache':build_edges,'access-policy':policy_edges}
GENERATORS = {'event-ledger':ledger_random,'build-cache':build_random,'access-policy':policy_random}


def cases(task_id, seed=0, level=1, phase=1):
    if type(seed) is not int or not 0 <= seed < 2**32 or level not in LEVELS or phase not in (1,2):
        raise ValueError('seed must be uint32, level 1..3, phase 1..2')
    rng = rng_for(task_id,seed,level,phase)
    inputs = [('contract',x) for x in EDGES[task_id](phase)]
    if phase == 2:
        inputs += [('regression',x) for x in EDGES[task_id](1)]
    inputs += [('generated',GENERATORS[task_id](rng,level,phase)) for _ in range(CASES_PER_PHASE-len(inputs))]
    return [dict(id=f'{group}-{i:02}',group=group,input=x,expected=ORACLES[task_id](x)) for i,(group,x) in enumerate(inputs)]
