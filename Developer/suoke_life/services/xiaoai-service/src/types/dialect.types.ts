/**
 * 方言相关类型定义
 */

/**
 * 方言信息
 */
export interface DialectInfo {
  code: string;
  name: string;
  region: {
    province: string;
    city?: string;
    county?: string[];
  };
  supportLevel: number;
  sampleStats?: {
    total: number;
    verified: number;
    pending: number;
    duration: number;
  };
  description?: string;
  culturalBackground?: string;
}

/**
 * 方言检测结果
 */
export interface DialectDetectionResult {
  success: boolean;
  detected: boolean;
  dialectCode: string;
  dialectName: string;
  confidence: number;
  message?: string;
  error?: string;
}

/**
 * 方言翻译结果
 */
export interface DialectTranslationResult {
  success: boolean;
  dialectCode?: string;
  dialectName?: string;
  original?: string;
  translated?: string;
  confidence?: number;
  culturalNotes?: string[];
  error?: string;
  message?: string;
}

/**
 * 方言学习进度
 */
export interface DialectLearningProgress {
  userId: string;
  dialectCode: string;
  dialectName: string;
  level: number;
  lessonsCompleted: number;
  totalLessons: number;
  lastPracticeDate: Date;
  nextGoal?: string;
}

/**
 * 方言学习计划
 */
export interface DialectLearningPlan {
  userId: string;
  dialectCode: string;
  dialectName: string;
  createdAt: Date;
  duration: string;
  difficulty: string;
  weeklyGoals: {
    week: number;
    focus: string;
    lessons: string[];
    practiceMinutes: number;
  }[];
  resources: {
    type: string;
    title: string;
    url: string;
  }[];
}

/**
 * 方言挑战活动信息
 */
export interface DialectChallenge {
  id: string;
  title: string;
  description: string;
  dialectCodes: string[];
  startDate: Date;
  endDate: Date;
  status: 'upcoming' | 'active' | 'completed' | 'cancelled';
  rewardPoints: number;
  participants: number;
  minSamplesRequired: number;
}