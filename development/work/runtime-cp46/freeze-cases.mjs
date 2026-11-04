import{writeFileSync}from'node:fs';
import{WISH_SUGGESTIONS}from'../../app/runtime-cp46/src/wish-suggestions.mjs';
const cases=WISH_SUGGESTIONS.flatMap((w,i)=>['zh','en'].map(lang=>({id:`G${String(i+1).padStart(2,'0')}-${lang}`,group:'grey-language',name:w.id,text:w[lang],expected:w.items.map(x=>[x.target,x.action]),split:'curated'})));
const rows=[
 ['D01','今天有点累，想让这里陪我缓一缓。','quiet'],
 ['D02','闻起来像刚出炉的面包。','food'],
 ['D03','有人陪着，就是好天气。','company'],
 ['D04','把说不出口的想念，交给晚风吧。','paper'],
 ['D05','今晚的空气有一点甜。','warm'],
 ['D06','让孩子们有一首属于他们的小曲子。','music'],
 ['D07','小狐狸也想交个朋友。','fox'],
 ['D08','春天应该不只在花店里。','spring'],
 ['D09','屋檐在滴答，街上该有伞了。','rain'],
 ['D10','白色的小纸片，慢慢落满冬天。','snow'],
 ['D11','把今天变成值得庆祝的一天。','celebrate'],
 ['D12','留一盏灯，有人要回来了。','home'],
 ['D13','清晨，大家又有新的事情可以做了。','dawn'],
 ['D14','有点饿了，街边能热闹起来吗？','food'],
 ['D15','I could use a quiet moment after today.','quiet'],
 ['D16','This evening smells like warm bread.','food'],
 ['D17','Could the children keep the guitarist company?','music'],
 ['D18','A little fox could use a friend.','fox'],
 ['D19','Let a small patch of rain follow that cloud.','cloud'],
 ['D20','A tiny celebration, just because we are here.','celebrate'],
 ['H01','这一天像一封没有寄出的信。','paper'],
 ['H02','给夜色一点可以握在手里的温度。','warm'],
 ['H03','风里该有点小孩子的快乐。','children'],
 ['H04','想在陌生的地方被温柔地招呼一下。','company'],
 ['H05','让每个角落都像刚刚醒过来。','fresh'],
 ['H06','The day has been heavy. Let the town breathe.','quiet'],
 ['H07','I miss the light from a kitchen window.','warm'],
 ['H08','A little tune, a few small listeners, and no big crowd.','music'],
 ['H09','What a lovely place. Hello, little neighbors!','greeting'],
 ['H10','Could somebody show the fish a little kindness?','pond'],
 ['E01','什么都不要改变，保持现在这样。','preserve'],
 ['E02','If it snowed, what would happen? Please do not change anything.','preserve'],
 ['E03','不要下雨，给街坊递一杯茶吧。','tea-no-rain'],
 ['E04','不要放烟花，大家一起准备点好吃的。','food-no-fireworks'],
 ['E05','造一艘宇宙飞船，带全镇飞走。','honest-unsupported'],
 ['E06','让那艘小舟自己开到桥边。','no-sailing'],
 ['E07','Let the empty boat sail by itself.','no-sailing'],
 ['E08','你好呀！','greeting'],
 ['E09','asdf qwer 123','greeting'],
 ['E10','下雨了，而且大家去夜市排队。','rain-priority']
];
for(const[id,text,expected]of rows)cases.push({id,group:'free-language',text,expectation:expected,split:id.startsWith('H')?'held-out':id.startsWith('E')?'boundary':'development'});
writeFileSync('outputs/runtime-checkpoint-46/frozen-language-cases.json',JSON.stringify(cases,null,2));
writeFileSync('outputs/runtime-checkpoint-46/frozen-grey-cases.json',JSON.stringify(WISH_SUGGESTIONS,null,2));
console.log({grey:WISH_SUGGESTIONS.length,language:cases.length});
