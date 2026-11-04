export function createPavingSupport(data){
 if(!data)return null;const cell=data.cell||.4,bins=new Map(),triangles=data.triangles;
 for(let i=0;i<triangles.length;i++){const t=triangles[i],xs=t.map(p=>p[0]),ys=t.map(p=>p[1]);for(let x=Math.floor(Math.min(...xs)/cell);x<=Math.floor(Math.max(...xs)/cell);x++)for(let y=Math.floor(Math.min(...ys)/cell);y<=Math.floor(Math.max(...ys)/cell);y++){const key=x+','+y;if(!bins.has(key))bins.set(key,[]);bins.get(key).push(i);}}
 return {highest(bounds){const ids=new Set();for(let x=Math.floor(bounds[0]/cell);x<=Math.floor(bounds[1]/cell);x++)for(let y=Math.floor(bounds[2]/cell);y<=Math.floor(bounds[3]/cell);y++)for(const i of bins.get(x+','+y)||[])ids.add(i);let height=-Infinity;
  for(const i of ids){let polygon=triangles[i];for(const[axis,edge,sign]of [[0,bounds[0],1],[0,bounds[1],-1],[1,bounds[2],1],[1,bounds[3],-1]]){const next=[];for(let k=0;k<polygon.length;k++){const a=polygon[k],b=polygon[(k+1)%polygon.length],da=(a[axis]-edge)*sign,db=(b[axis]-edge)*sign;if(da>=-1e-8)next.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);next.push(a.map((v,j)=>v+(b[j]-v)*t));}}polygon=next;if(!polygon.length)break;}for(const p of polygon)height=Math.max(height,p[2]);}
  return Number.isFinite(height)?height:null;
 }};
}
