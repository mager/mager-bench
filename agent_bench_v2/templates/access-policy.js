// Rules are currently evaluated in assignment order.
function solve(input) {
  return input.queries.map(q=>{
    const user=input.users.find(u=>u.id===q.user);if(!user)return 'deny';
    for(const id of user.roles){
      const role=input.roles.find(r=>r.id===id);
      for(const r of role.rules){
        if(r.tenant===q.tenant && (r.resource==='*'||r.resource===q.resource) &&
          (r.action==='*'||r.action===q.action))return r.effect;
      }
    }
    return 'deny';
  });
}
module.exports={solve};
