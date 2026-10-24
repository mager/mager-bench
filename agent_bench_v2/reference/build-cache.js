function solve(input) {
  const nodes = new Map(input.nodes.map(n => [n.id,{...n,deps:[...n.deps]}]));
  const cache = new Map(); let epoch = 0;
  return input.requests.map(request => {
    for (const change of request.changes) Object.assign(nodes.get(change.id), change);
    const needed = new Set(), active = new Set(); let cycle = false;
    function visit(id) {
      if (active.has(id)) { cycle = true; return; }
      if (needed.has(id)) return;
      needed.add(id); active.add(id);
      for (const dep of nodes.get(id).deps) visit(dep);
      active.delete(id);
    }
    request.targets.forEach(visit);
    if (cycle) return {error:'cycle',built:[],cached:[]};
    const todo = new Set(needed), order = [], done = new Set();
    while (todo.size) {
      const id = [...todo].sort().find(k => nodes.get(k).deps.every(d => done.has(d)));
      todo.delete(id); done.add(id); order.push(id);
    }
    const built = [], cached = [];
    for (const id of order) {
      const n = nodes.get(id);
      const signature = JSON.stringify([n.revision,[...new Set(n.deps)].sort().map(d=>[d,cache.get(d).epoch])]);
      if (cache.has(id) && cache.get(id).signature === signature) cached.push(id);
      else { cache.set(id,{signature,epoch:++epoch}); built.push(id); }
    }
    return {built,cached};
  });
}
module.exports = {solve};
