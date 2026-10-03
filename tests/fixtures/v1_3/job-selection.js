function solve({jobs,budget,cooldown}) {
 const sorted=[...jobs].sort((a,b)=>a.end-b.end || (a.id<b.id?-1:1));
 const empty={ids:[],profit:0,cost:0},dp=[Array(budget+1).fill(empty)];
 const cmpIds=(a,b)=>{for(let i=0;i<Math.min(a.length,b.length);i++){if(a[i]!==b[i])return a[i]<b[i]?-1:1;}return a.length-b.length;};
 const better=(a,b)=>a.profit!==b.profit?(a.profit>b.profit?a:b):a.cost!==b.cost?(a.cost<b.cost?a:b):a.ids.length!==b.ids.length?(a.ids.length<b.ids.length?a:b):cmpIds(a.ids,b.ids)<=0?a:b;
 for(let i=0;i<sorted.length;i++){
  const j=sorted[i];let before=i-1;
  while(before>=0 && sorted[before].end+cooldown>j.start)before--;
  const row=[];
  for(let b=0;b<=budget;b++){
   let best=dp[i][b];
   if(j.cost<=b){const previous=dp[before+1][b-j.cost];best=better(best,{ids:[...previous.ids,j.id],profit:previous.profit+j.profit,cost:previous.cost+j.cost});}
   row.push(best);
  }
  dp.push(row);
 }
 return dp[sorted.length][budget];
}
