function solve(input) {
  const roles = new Map(input.roles.map(r => [r.id,r]));
  const users = new Map(input.users.map(u => [u.id,u]));
  return input.queries.map(q => {
    if (!users.has(q.user)) return 'deny';
    const done = new Set(), active = new Set(), rules = []; let cycle = false;
    function walk(id) {
      if (active.has(id)) { cycle = true; return; }
      if (done.has(id)) return;
      active.add(id);
      const role = roles.get(id);
      role.parents.forEach(walk); rules.push(...role.rules);
      active.delete(id); done.add(id);
    }
    users.get(q.user).roles.forEach(walk);
    if (cycle) return 'deny';
    const matched = rules.filter(r => r.tenant === q.tenant &&
      (r.resource === '*' || r.resource === q.resource) &&
      (r.action === '*' || r.action === q.action) &&
      (r.until === undefined || q.time < r.until));
    return matched.some(r=>r.effect === 'allow') && !matched.some(r=>r.effect === 'deny') ? 'allow' : 'deny';
  });
}
module.exports = {solve};
