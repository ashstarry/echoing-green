const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const angle=(a,b)=>Math.atan2(Math.sin(b-a),Math.cos(b-a));
const forward=yaw=>[-Math.cos(yaw),-Math.sin(yaw)];
const grids=new WeakMap();
export function foxFloor(data,p){let cached=grids.get(data);if(!cached){const origin=data.origin||data.nodes[0]||[0,0];cached={origin,grid:new Map(data.nodes.map(n=>[Math.round((n[0]-origin[0])/.16)+','+Math.round((n[1]-origin[1])/.16),n]))};grids.set(data,cached);}const {origin,grid}=cached,x=Math.round((p[0]-origin[0])/.16),y=Math.round((p[1]-origin[1])/.16);let best=null,d=Infinity;for(let i=-1;i<=1;i++)for(let j=-1;j<=1;j++){const n=grid.get((x+i)+','+(y+j));if(n&&dist(p,n)<d){best=n;d=dist(p,n);}}if(d<.135)return best[2];
 if(p[0]>=4.0&&p[0]<=5.16&&p[1]>=1.48&&p[1]<=1.90)return .624;return null;}

export function foxCurve(data,start,yaw,end,endYaw,handle){const a=forward(yaw),b=forward(endYaw),p1=[start[0]+a[0]*handle,start[1]+a[1]*handle],p2=[end[0]-b[0]*handle,end[1]-b[1]*handle],out=[];let length=0,lastYaw=yaw;
 for(let i=0;i<=48;i++){const t=i/48,u=1-t,p=[u*u*u*start[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t*t*t*end[0],u*u*u*start[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t*t*t*end[1]];if(foxFloor(data,p)===null)return null;const dx=3*u*u*(p1[0]-start[0])+6*u*t*(p2[0]-p1[0])+3*t*t*(end[0]-p2[0]),dy=3*u*u*(p1[1]-start[1])+6*u*t*(p2[1]-p1[1])+3*t*t*(end[1]-p2[1]);if(Math.hypot(dx,dy)<.025)return null;const heading=lastYaw+angle(lastYaw,Math.atan2(dy,dx)+Math.PI),step=i?dist(p,out.at(-1).p):0,turn=Math.abs(heading-lastYaw);if(i&&turn/Math.max(.0001,step)>4.5)return null;length+=step;out.push({p:[p[0],p[1],start[2]+(end[2]-start[2])*(t*t*(3-2*t))],yaw:heading,d:length});lastYaw=heading;}
 if(length<.65||length>3.8)return null;return{poses:out,length,reverse:false};}
export function foxBackstep(data,start,yaw,maxDistance=.27){const f=forward(yaw),poses=[{p:start.slice(),yaw,d:0}];for(let i=1;i<=Math.floor(maxDistance/.045);i++){const p=[start[0]-f[0]*i*.045,start[1]-f[1]*i*.045,start[2]];if(foxFloor(data,p)===null)break;poses.push({p,yaw,d:i*.045});}return poses.length>=5?{poses,length:poses.at(-1).d,reverse:true}:null;}
export function foxPathPose(path,d){const poses=path.poses;let i=1;while(i<poses.length-1&&poses[i].d<d)i++;const a=poses[i-1],b=poses[i],u=Math.max(0,Math.min(1,(d-a.d)/(b.d-a.d||1)));return{p:a.p.map((v,k)=>v+(b.p[k]-v)*u),yaw:a.yaw+angle(a.yaw,b.yaw)*u,curvature:Math.abs(angle(a.yaw,b.yaw))/Math.max(.001,b.d-a.d)};}
// A translated, foot-driven arc creates a new heading at a garden edge.
// It never turns the root about a stationary centre.
export function foxTurnArc(data,start,yaw,side,radius,angle=Math.PI){
 const f=forward(yaw),n=[-f[1],f[0]],poses=[];let length=0;
 for(let i=0;i<=48;i++){
  const a=angle*i/48,p=[start[0]+f[0]*radius*Math.sin(a)+n[0]*side*radius*(1-Math.cos(a)),start[1]+f[1]*radius*Math.sin(a)+n[1]*side*radius*(1-Math.cos(a))],floor=foxFloor(data,p);
  if(floor===null||Math.abs(floor-start[2])>.12)return null;p.push(start[2]);if(i)length+=dist(p,poses.at(-1).p);poses.push({p,yaw:yaw+side*a,d:length});
 }
 return {poses,length,reverse:false,maneuver:'turn'};
}
