// Compressed life rhythm: readable variation, not real-world waiting times.
export const CADENCE={meal:[32,72],inside:[16,34],chat:[8,20],watch:[9,22],work:[10,26],rest:[6,16],stroll:[5,11],reaction:[.8,4.5],festivalPrepare:[12,20],festivalLinger:[9,18],trainDwell:[12,20],ambientFestivalGap:[160,240]};
export function stableUnit(id,cycle=0){let h=2166136261;for(const c of `${id}:${cycle}`){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}h^=h>>>16;return(h>>>0)/4294967296;}
export const varied=(range,id,cycle=0)=>range[0]+(range[1]-range[0])*stableUnit(id,cycle);
