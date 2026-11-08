// One shared focus for fireworks and every resident's gaze (Blender Z-up).
export const FIREWORK_FOCUS=[-4.6,2.8,6.8];
export const EVENT_GAZE_PITCH=-.46;

export function needsClearPromenade(kind){return ['festival','market','supper','reunion','quiet','tea_service','umbrella_walk','leaf_sweep','parcel_handoff'].includes(kind)||!!kind?.startsWith('paper_');}
