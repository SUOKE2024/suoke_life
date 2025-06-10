// 生活建议类型
export interface LifeSuggestion {
  id: string;
  title: string;
  description: string;
  category: "diet" | "exercise" | "sleep" | "mental" | "social" | "work";
  priority: "high" | "medium" | "low";
  icon: string;
  color: string;
  completed: boolean;
  timeEstimate: string;
  benefits?: string[];
  steps?: string[];
}

// 健康指标类型
export interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  target: number;
  icon: string;
  color: string;
  trend: "up" | "down" | "stable";
  suggestion: string;
  history?: HealthMetricHistory[];
}

// 健康指标历史记录
export interface HealthMetricHistory {
  date: string;
  value: number;
}

// 生活计划类型
export interface LifePlan {
  id: string;
  title: string;
  description: string;
  progress: number;
  duration: string;
  category: string;
  icon: string;
  color: string;
  nextAction: string;
  startDate: string;
  endDate: string;
  milestones?: PlanMilestone[];
  rewards?: string[];
}

// 计划里程碑
export interface PlanMilestone {
  id: string;
  title: string;
  description: string;
  targetDate: string;
  completed: boolean;
  completedDate?: string;
}

// 生活习惯类型
export interface LifeHabit {
  id: string;
  name: string;
  description: string;
  category: "health" | "productivity" | "wellness" | "social";
  frequency: "daily" | "weekly" | "monthly";
  streak: number;
  bestStreak: number;
  icon: string;
  color: string;
  reminder?: HabitReminder;
}

// 习惯提醒
export interface HabitReminder {
  enabled: boolean;
  time: string;
  days: number[]; // 0-6, 0为周日
  message: string;
}

// 生活目标类型
export interface LifeGoal {
  id: string;
  title: string;
  description: string;
  category: "health" | "career" | "relationship" | "personal";
  priority: "high" | "medium" | "low";
  progress: number;
  targetDate: string;
  status: "active" | "completed" | "paused" | "cancelled";
  subGoals?: SubGoal[];
}

// 子目标
export interface SubGoal {
  id: string;
  title: string;
  completed: boolean;
  completedDate?: string;
}

// 生活评估类型
export interface LifeAssessment {
  id: string;
  date: string;
  overallScore: number;
  categories: {
    health: number;
    work: number;
    relationships: number;
    personal: number;
    financial: number;
  };
  notes?: string;
  improvements?: string[];
}

// 生活建议配置
export interface SuggestionConfig {
  categories: string[];
  priorities: string[];
  timePreferences: string[];
  excludedCategories?: string[];
}

// 生活数据统计
export interface LifeStats {
  totalSuggestions: number;
  completedSuggestions: number;
  activePlans: number;
  completedPlans: number;
  currentStreak: number;
  longestStreak: number;
  averageScore: number;
  improvementRate: number;
}