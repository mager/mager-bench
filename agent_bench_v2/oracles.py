"""Independent Python state-machine specifications, never agent submissions."""
from copy import deepcopy
import heapq


def ledger(data):
    balances = dict(data['balances'])
    versions = dict.fromkeys(balances, 0)
    accepted, receipts = set(), []
    for event in data['events']:
        status = 'rejected'
        if event['id'] in accepted:
            status = 'duplicate'
        elif all(versions[k] == v for k, v in event.get('expected', {}).items()):
            draft, touched = dict(balances), set()
            for move in event.get('moves', [event]):
                a, b, amount = move['from'], move['to'], move['amount']
                if draft[a] < amount:
                    break
                draft[a] -= amount
                draft[b] += amount
                touched.update((a, b))
            else:
                balances = draft
                for account in touched:
                    versions[account] += 1
                accepted.add(event['id'])
                status = 'applied'
        receipts.append(dict(id=event['id'], status=status))
    return dict(balances=balances, versions=versions, receipts=receipts)


def build(data):
    nodes = {n['id']: deepcopy(n) for n in data['nodes']}
    cache, reports, serial = {}, [], 0
    for request in data['requests']:
        for change in request['changes']:
            nodes[change['id']].update(deepcopy(change))
        required, pending = set(), list(request['targets'])
        while pending:
            node = pending.pop()
            if node not in required:
                required.add(node)
                pending.extend(nodes[node]['deps'])
        waiting = {k: set(nodes[k]['deps']) for k in required}
        consumers = {k: set() for k in required}
        for k, deps in waiting.items():
            for dep in deps:
                consumers[dep].add(k)
        ready = [k for k in required if not waiting[k]]
        heapq.heapify(ready)
        order = []
        while ready:
            node = heapq.heappop(ready)
            order.append(node)
            for consumer in consumers[node]:
                waiting[consumer].remove(node)
                if not waiting[consumer]:
                    heapq.heappush(ready, consumer)
        if len(order) != len(required):
            reports.append(dict(error='cycle', built=[], cached=[]))
            continue
        report = dict(built=[], cached=[])
        for node in order:
            signature = (nodes[node]['revision'], tuple((d, cache[d][1]) for d in sorted(set(nodes[node]['deps']))))
            if node in cache and cache[node][0] == signature:
                report['cached'].append(node)
            else:
                serial += 1
                cache[node] = (signature, serial)
                report['built'].append(node)
        reports.append(report)
    return reports


def policy(data):
    roles = {r['id']: r for r in data['roles']}
    users = {u['id']: u for u in data['users']}
    output = []
    for query in data['queries']:
        if query['user'] not in users:
            output.append('deny')
            continue
        # Kahn elimination independently detects any reachable cycle.
        reached, todo = set(), list(users[query['user']]['roles'])
        while todo:
            role = todo.pop()
            if role not in reached:
                reached.add(role)
                todo.extend(roles[role]['parents'])
        edges = {r: set(roles[r]['parents']) for r in reached}
        remaining = set(reached)
        while remaining:
            leaves = {r for r in remaining if not (edges[r] & remaining)}
            if not leaves:
                break
            remaining -= leaves
        if remaining:
            output.append('deny')
            continue
        effects = []
        for role in reached:
            for rule in roles[role]['rules']:
                if (rule['tenant'] == query['tenant']
                    and rule['resource'] in ('*', query['resource'])
                    and rule['action'] in ('*', query['action'])
                    and ('until' not in rule or query['time'] < rule['until'])):
                    effects.append(rule['effect'])
        output.append('allow' if 'allow' in effects and 'deny' not in effects else 'deny')
    return output


ORACLES = {'event-ledger': ledger, 'build-cache': build, 'access-policy': policy}
