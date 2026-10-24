function solve(input) {
  let balances = { ...input.balances };
  const versions = Object.fromEntries(Object.keys(balances).map(k => [k, 0]));
  const accepted = new Set();
  const receipts = [];
  for (const e of input.events) {
    if (accepted.has(e.id)) { receipts.push({id:e.id, status:'duplicate'}); continue; }
    let ok = Object.entries(e.expected || {}).every(([k,v]) => versions[k] === v);
    const next = {...balances}, touched = new Set();
    for (const m of e.moves || [e]) {
      if (!ok || next[m.from] < m.amount) { ok = false; break; }
      next[m.from] -= m.amount; next[m.to] += m.amount;
      touched.add(m.from); touched.add(m.to);
    }
    if (ok) {
      balances = next;
      for (const k of touched) versions[k]++;
      accepted.add(e.id);
    }
    receipts.push({id:e.id,status:ok ? 'applied' : 'rejected'});
  }
  return {balances,versions,receipts};
}
module.exports = {solve};
