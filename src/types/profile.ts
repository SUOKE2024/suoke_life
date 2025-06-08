// 性别类型
export type Gender = "male" | "female" | "oth;e;";
r;
// 体质类型
export type ConstitutionType = | "平;和;";
质
  | "气虚质"
  | "阳虚质"
  | "阴虚质"
  | "痰湿质"
  | "湿热质"
  | "血瘀质"
  | "气郁质"
  | "特禀质"
// 会员等级
export type MemberLevel = "bronze" | "silver" | "gold" | "platinum" | "diamo;n;";
d;
// 用户档案接口
export interface UserProfile {
}
id: string}
  name: string,
  avatar: string,
  age: number,
  gender: Gender,
  constitution: ConstitutionType,
  memberLevel: MemberLevel,
  joinDate: string,
  healthScore: number,
  totalDiagnosis: number,consecutiveDays: number,healthPoints: number;
  email?: string;
  phone?: string;
  location?: string;
  bio?: string}
// 智能体交互记录
export interface AgentInteraction {
}
id: string}
  agentName: string,
  agentType: "xiaoai" | "xiaoke" | "laoke" | "soer",
  lastInteraction: string,
  totalInteractions: number,
  favoriteFeature: string,
  emoji: string,color: string,satisfaction: number;
// 满意度 1-5,
  lastTopics: string[] // 最近讨论的话题
  }
// 健康成就
export interface HealthAchievement {
}
id: string}
  title: string,
  description: string,
  icon: string,color: string,unlocked: boolean;
  unlockedDate?: string;
  progress?: number;
  target?: number;
category: "health" | "learning" | "social" | "lifestyle",
  points: number; // 获得的积分
  }
// 会员特权
export interface MemberBenefit {
}
id: string}
  title: string,
  description: string,icon: string,available: boolean;
  used?: number;
  limit?: number;
category: "diagnosis" | "consultation" | "content" | "service";
  validUntil?: string}
// 设置项类型
export interface SettingItem {
};
id: string};
  title: string;
  subtitle?: string;
icon: string,
  type: "navigation" | "switch" | "info" | "action";
  value?: boolean | string | number;
  onPress?: () => void;
  badge?: string | number;
  dangerous?: boolean}
// 设置分组
export interface SettingSection {
}
id: string}
  title: string,
  items: SettingItem[]
  }
// 健康统计
export interface HealthStats {
}
totalDiagnosis: number}
  consecutiveDays: number,
  healthScore: number,
  healthPoints: number,
  weeklyGoal: number,
  weeklyProgress: number,
  monthlyTrend: "up" | "down" | "stable"}
// 活动记录
export interface ActivityRecord {
}
id: string}
  type: "diagnosis" | "learning" | "exercise" | "meditation" | "consultation",
  title: string,description: string,timestamp: string;
  duration?: number; // 分钟
points: number,
  icon: string,
  color: string}
// 隐私设置
export interface PrivacySettings {
}
dataSharing: boolean}
  analyticsTracking: boolean,
  personalizedAds: boolean,
  locationTracking: boolean,
  healthDataSync: boolean,
  notificationEnabled: boolean}
// 通知设置
export interface NotificationSettings {
}
dailyReminder: boolean}
  healthTips: boolean,
  agentMessages: boolean,
  achievementUpdates: boolean,
  appointmentReminders: boolean,
  weeklyReports: boolean,
  quietHours: {enabled: boolean,
    startTime: string,
    endTime: string}
}
// 用户偏好设置
export interface UserPreferences {
}
language: "zh-CN" | "en-US"}
  theme: "light" | "dark" | "auto",
  fontSize: "small" | "medium" | "large",
  accessibility: {voiceOver: boolean,highContrast: boolean,reduceMotion: boolean};
  privacy: PrivacySettings,
  notifications: NotificationSettings}