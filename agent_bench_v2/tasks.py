"""Public contracts. Evaluation inputs are generated outside the agent workspace."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES_PER_PHASE = 32
PHASE_SECONDS = 120
RUN_SECONDS = 600
LEVELS = {1: (8, 24), 2: (32, 96), 3: (128, 384)}
COMMON = """Work in this repository. Implement synchronous CommonJS JavaScript.
The entry point is src/index.js, exporting { solve }. solve(input) must return a
JSON-serializable value. Use only relative .js modules within src/. No packages,
filesystem, network, timers, process, eval, or async in submitted source.
Submit at most 24 .js files totaling at most 128 KiB.
You may inspect files, edit code, add tests, and run node --test. Change src/ and
test/ only. Do not change the existing test/smoke.test.js. Each hidden case runs
in a fresh QuickJS context with 32 MiB memory and 500 ms CPU time. Object key
order does not matter; array order does. Numbers are safe integers. All inputs
satisfy the stated contract. No Internet or external tools are needed.
Finish by describing the change briefly. The code on disk is the submission.
"""

TASKS = [
    {
        "id": "event-ledger", "title": "Repair an event ledger",
        "summary": "Duplicate events, balance checks, atomic batches.",
        "phases": [
            """Repair the ledger. Input: {balances: {account: nonnegative integer},
events: [{id, from, to, amount}]}. Accounts and event IDs are nonempty ASCII
identifiers. from and to name distinct existing accounts; amount is positive.
Start each account version at zero. Process events in order. An accepted
transfer debits from, credits to, and increments both account versions once.
Reject insufficient funds with no state change. Remember only accepted IDs:
a repeated accepted ID is duplicate, even with a different payload, and changes
nothing. Rejected IDs may be retried. Return {balances, versions, receipts},
where receipts has one {id, status} per event, status applied/duplicate/rejected.
Input must not be mutated. Empty input collections are valid.""",
            """Extend the same ledger without breaking transfers. Events may now
be batches {id, moves:[{from,to,amount}], expected?:{account:version}}. Transfers
may also have expected. Duplicate detection happens first. For a new ID, reject
if any expected version differs from the current version. Execute moves in
order on a draft: if any move lacks funds, reject the WHOLE event without balance
or version changes and do not reserve its ID. On success, increment each touched
account's version once per event, even if touched many times or its final balance
is unchanged. An empty batch is accepted, reserves its ID, and changes no versions.
Use the same return shape. Existing single transfers retain their behavior.""",
        ],
    },
    {
        "id": "build-cache", "title": "Fix an incremental build",
        "summary": "Cache invalidation, dependency changes, cycles.",
        "phases": [
            """Repair a build cache. Input: {nodes:[{id,deps:[id],revision:integer}],
requests:[{changes:[{id,revision}],targets:[id]}]}. IDs are unique ASCII
identifiers; references exist. Only nodes reachable backward from targets are
required. deps may repeat. Begin with an empty cache. Apply changes in order
before each build. Build the required subgraph in the lexicographically smallest
topological order (smallest currently ready ID each step). A node is cached only
if its last successful build used the same revision, same distinct dependencies,
and same last successful build of each dependency. Otherwise rebuild it. A
rebuilt dependency forces its consumers to rebuild. Store only each node's last
successful build, not all historical revisions. Ignore unrelated changes.
Return one {built:[ids],cached:[ids]} per request; both lists follow build order.
Empty targets returns empty lists. No nodes are added or removed. Phase-one
inputs are DAGs. Avoid enumerating paths through shared dependencies.""",
            """Extend the build system. A change can now set revision, deps, or
both. Dependency order and duplicate entries do not affect cache identity.
Cycles can exist. If the REQUIRED subgraph contains a cycle, return
{error:'cycle',built:[],cached:[]} for that request and do not update any build
cache. Definitions from changes still persist, so a later request can fix the
cycle. Ignore unrelated cycles. All previous behavior remains required. A
changed dependency set invalidates that node even when revisions are equal.""",
        ],
    },
    {
        "id": "access-policy", "title": "Extend a permission engine",
        "summary": "Tenant isolation, deny rules, inherited roles.",
        "phases": [
            """Repair access decisions. Input: {roles:[{id,parents:[],rules:[
{effect:'allow'|'deny',tenant,resource,action}]}], users:[{id,roles:[id]}],
queries:[{user,tenant,resource,action,time:integer}]}. IDs are unique ASCII
identifiers. All assigned roles exist, but a query user may not exist. Return
an array of 'allow'/'deny', one per query. A rule matches only if tenant is EXACT
and resource and action each equal the query or are the whole-string wildcard
'*'. No substring or prefix matching. Any matching deny overrides ALL matching
allows. Otherwise allow iff at least one allow matches. Unknown users and no
matching rules deny. Role assignment order and duplicates do not matter.
Phase one has no inheritance or expiry. Do not mutate input.""",
            """Extend the engine. Roles may inherit parents (all IDs exist,
duplicates allowed). Collect all rules transitively, sharing ancestors safely.
If ANY cycle is reachable from a user's assigned roles, deny every query for
that user, even when a direct allow matches. Ignore unrelated cycles. Rules
can have until:integer: they match only when query.time < until. Missing until
means no expiry. Expired deny rules do not override active allows. Tenants
still match exactly, including a literal '*' tenant. All phase-one rules remain
required. Avoid enumerating paths in shared inheritance graphs.""",
        ],
    },
]


def task_by_id(task_id):
    return next(t for t in TASKS if t['id'] == task_id)


def prompt(task_id, phase):
    task = task_by_id(task_id)
    return COMMON + '\nWORK ORDER ' + str(phase) + '\n' + '\n\n'.join(task['phases'][:phase])


def reference_sources(task_id):
    return {
        'src/index.js': 'module.exports = require("./engine.js");\n',
        'src/engine.js': (ROOT / 'reference' / (task_id + '.js')).read_text(),
    }
