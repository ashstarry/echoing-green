import {foxFloor} from './fox-path.mjs?v=cp50-friendly-fox-1d9659a79416';
const D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
export function foxBicycleGap(p,m){const dx=p[0]-m.p[0],dy=p[1]-m.p[1],c=Math.cos(m.yaw),n=Math.sin(m.yaw),u=dx*c+dy*n,v=-dx*n+dy*c;return Math.hypot(u-Math.max(-.75,Math.min(.75,u)),v);}
const obstacleGap=(p,a)=>a.bike?foxBicycleGap(p,a.bike)-.56:D(p,a.p)-(a.radius||.54);
const angle=(a,b)=>Math.atan2(Math.sin(b-a),Math.cos(b-a));
const graphs=new WeakMap();
function graph(data){let g=graphs.get(data);if(g)return g;if(data.adjacency){g={edges:data.adjacency};graphs.set(data,g);return g;}const origin=data.origin||data.nodes[0]||[0,0],key=p=>Math.round((p[0]-origin[0])/.16)+','+Math.round((p[1]-origin[1])/.16),grid=new Map(data.nodes.map((p,i)=>[key(p),i]));const edges=data.nodes.map((p,i)=>{const x=Math.round((p[0]-origin[0])/.16),y=Math.round((p[1]-origin[1])/.16),out=[];for(const dx of[-1,0,1])for(const dy of[-1,0,1]){if(!dx&&!dy)continue;const n=grid.get((x+dx)+','+(y+dy));if(n===undefined||Math.abs(data.nodes[n][2]-p[2])>.10)continue;if(dx&&dy&&(!grid.has((x+dx)+','+y)||!grid.has(x+','+(y+dy))))continue;out.push(n);}return out;});g={edges};graphs.set(data,g);return g;}
// A fox can take small sideways/backward steps through an existing lane. This
// fallback follows connected paving rather than requiring a car-like U-turn.
export function foxGroundGreeting(data,m,neighbors,people,minimum=.8){
 if(!neighbors.length)return null;const g=graph(data),nodes=data.nodes;const candidates=nodes.map((p,i)=>({p,i,d:D(p,m.p)})).filter(x=>x.d<.32).sort((a,b)=>a.d-b.d);let start=-1;for(const c of candidates){let safe=true;for(let n=1;n<=8&&safe;n++){const p=m.p.map((v,k)=>v+(c.p[k]-v)*n/8);if(foxFloor(data,p)===null){safe=false;break;}for(const a of people)if(Math.abs(a.p[2]-p[2])<1&&obstacleGap(p,a)<Math.min(0,obstacleGap(m.p,a)-.005)){safe=false;break;}}if(safe){start=c.i;break;}}if(start<0)return null;
 const blocked=new Set(nodes.flatMap((p,i)=>people.some(a=>Math.abs(a.p[2]-p[2])<1&&obstacleGap(p,a)<0&&obstacleGap(p,a)<obstacleGap(m.p,a)-.02)?[i]:[]));blocked.delete(start);
 const parent=new Int32Array(nodes.length).fill(-2),distance=new Float32Array(nodes.length),queue=[start];parent[start]=-1;
 for(let at=0;at<queue.length;at++)for(const n of g.edges[queue[at]])if(parent[n]===-2&&!blocked.has(n)){parent[n]=queue[at];distance[n]=distance[queue[at]]+D(nodes[n],nodes[queue[at]]);queue.push(n);}
 for(const neighbor of neighbors){const choices=[];for(let i=0;i<nodes.length;i++){if(parent[i]<0||D(nodes[i],m.p)<minimum)continue;const gap=D(nodes[i],neighbor.p);if(gap<.80||gap>1.03)continue;const prev=nodes[parent[i]],yaw=Math.atan2(nodes[i][1]-prev[1],nodes[i][0]-prev[0])+Math.PI,endYaw=Math.atan2(neighbor.p[1]-nodes[i][1],neighbor.p[0]-nodes[i][0])+Math.PI;choices.push({i,score:distance[i]+Math.abs(angle(yaw,endYaw))*.4+Math.abs(gap-.86),endYaw});}
  choices.sort((a,b)=>a.score-b.score);for(const c of choices.slice(0,4)){const path=[];for(let i=c.i;i>=0;i=parent[i])path.push(i);path.reverse();if(path.length>240)continue;const poses=[{p:m.p.slice(),yaw:m.yaw,d:0}];let length=0;for(const i of path){const p=nodes[i],prev=poses.at(-1),d=D(prev.p,p);if(d<.003)continue;length+=d;poses.push({p:p.slice(),yaw:Math.atan2(p[1]-prev.p[1],p[0]-prev.p[0])+Math.PI,d:length});}if(poses.length<2||length<minimum)continue;poses.at(-1).yaw=c.endYaw;return{route:{poses,length,reverse:false,maneuver:'paving'},neighbor};}
 }
 return null;
}
