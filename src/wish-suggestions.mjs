// Curated examples use the same finite executor as the activity buttons.
// Rotation changes only the grey hint; it never performs an activity on its own.
const macro=(target,action)=>({kind:'macro',target,action});
const object=(target,action)=>({kind:'object',target,action});
const resident=(target,action)=>({kind:'resident',target,action});
export const WISH_PERIOD_MS=18000;
export const WISH_SUGGESTIONS=[
 ['tea','让一双手被一杯热茶暖一暖。','Warm a neighbor’s hands with a cup of tea.',[macro('craft','tea')],'component.restaurant_steamer'],
 ['paper','把思念挂在树上，留一张随风的纸笺。','Leave a little wish in the lantern tree.',[macro('paper','hang')],'tree.lantern_tree'],
 ['umbrella','这把伞，分一半给身旁的人吧。','Share an umbrella and a little walk.',[macro('craft','umbrella')]],
 ['homecoming','留一盏灯，等晚归的人。','Leave a light for someone coming home.',[macro('neighborhood','homecoming'),macro('light','warm')],'component.home_welcome_door'],
 ['boat','让小船看看池塘另一边，再慢慢回来。','Let the boat drift across the pond and back.',[object('boat.pond_boat','cruise')],'boat.pond_boat'],
 ['spring','让春天走进街角，花也伸个懒腰。','Let spring unfold in the corners of town.',[macro('neighborhood','spring'),macro('breeze','gentle')],'tree.lantern_tree'],
 ['fox','小狐狸，去和附近的街坊打个招呼吧。','Let the little fox say hello to a neighbor.',[object('animal.garden_fox','greet')],'animal.garden_fox'],
 ['laundry','让小布巾也闻一闻晚风。','Hang little cloths in the evening breeze.',[macro('craft','laundry')]],
 ['cloud','小云去街巷走走，只落一小片雨。','Let a little cloud wander with a tiny shower.',[macro('cloud','wander')],'weather.cp02_paper_cloud'],
 ['prepare','一起准备一个值得开心的晚上。','Prepare a lovely evening together.',[macro('neighborhood','prepare')],'tree.lantern_tree'],
 ['snack','揭开蒸笼，递一份热腾腾的点心。','Lift the steamer lid and offer a warm treat.',[macro('craft','snack')],'component.restaurant_steamer'],
 ['leaves','秋天落在脚边，替晚风收拾一下吧。','Gather the little leaves the breeze left behind.',[macro('craft','leaves')]],
 ['memory','把这个温柔的片刻，留作一件小纪念。','Keep a little memento of this gentle moment.',[macro('craft','remember')],'component.restaurant_steamer'],
 ['reopen','雨停了，把生活重新摆回街边。','After the rain, bring street life back outside.',[macro('weather','clear'),macro('neighborhood','reopen')]],
 ['music','让琴声把街坊牵到树下。','Let a little guitar music draw neighbors together.',[macro('music','play'),macro('street','gather')],'resident.musician'],
 ['parcel','一份小礼物，托电车捎给街坊。','Let the tram carry a little gift to a neighbor.',[macro('journey','deliver')],'tram.tram_car_front'],
 ['pond','给池塘里的小鱼儿一点心意。','Let a neighbor feed the little pond fish.',[resident('resident.water_visitor','feed_pond')],'resident.water_visitor'],
 ['night','纸灯沿街亮起，留一晚温柔的光。','Let paper lanterns brighten a gentle night.',[macro('day_phase','night'),macro('light','warm')],'tree.lantern_tree']
].map(([id,zh,en,items,focus])=>({id,zh,en,items,focus}));
export function createWishRotation(now=0){let index=0,nextAt=now+WISH_PERIOD_MS;
 return{current:()=>WISH_SUGGESTIONS[index],interact(time){nextAt=time+WISH_PERIOD_MS;},tick(time,{typed=false,focused=false,pending=false,hidden=false}={}){if(typed||focused||pending||hidden){nextAt=time+WISH_PERIOD_MS;return false;}if(time<nextAt)return false;index=(index+1)%WISH_SUGGESTIONS.length;nextAt=time+WISH_PERIOD_MS;return true;},capture(value,locale){const text=String(value||'').trim();if(text)return{source:'words',text};const hint=WISH_SUGGESTIONS[index];return{source:'suggestion',id:hint.id,text:hint[locale==='zh'?'zh':'en'],items:hint.items.map(x=>({...x})),focus:hint.focus};}};
}
