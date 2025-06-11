// 性别类型
export type Gender = "male" | "female" | "other";
// 体质类型
export type Constitution = | "balanced"";
  | "qi_deficiency"";
  | "yang_deficiency"";
  | "yin_deficiency"";
  | "phlegm_dampness"";
  | "damp_heat"";
  | "blood_stasis"";
  | "qi_stagnation"";
  | "special_constitution";
// 用户档案接口
export interface UserProfile {;}id: string;
name: string;
gender: Gender;
age: number;
height: number;
weight: number;
constitution: Constitution;
avatar?: string;
phone?: string;
email?: string;
createdAt: Date;
updatedAt: Date;
}
}
}
