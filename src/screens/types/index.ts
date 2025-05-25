// 重新导出所有类型
export type { AgentType, AgentInfo } from '../components/AgentCard';
export type { Message } from '../components/ChatMessage';
export type { HealthData } from '../components/HealthCard';
export type { TabItem } from '../components/TabSelector';

// 导入类型用于内部使用
import type { AgentType } from '../components/AgentCard';
import type { Message } from '../components/ChatMessage';

// 屏幕相关类型
export interface ScreenProps {
  navigation?: any;
  route?: any;
}

// 健康管理相关类型
export interface HealthMetrics {
  heartRate: number;
  bloodPressure: {
    systolic: number;
    diastolic: number;
  };
  weight: number;
  bloodSugar: number;
  sleepQuality: number;
  steps: number;
}

// 用户体质类型
export type ConstitutionType = 
  | 'balanced'        // 平和质
  | 'qi_deficiency'   // 气虚质
  | 'yang_deficiency' // 阳虚质
  | 'yin_deficiency'  // 阴虚质
  | 'phlegm_dampness' // 痰湿质
  | 'damp_heat'       // 湿热质
  | 'blood_stasis'    // 血瘀质
  | 'qi_stagnation'   // 气郁质
  | 'special_diathesis'; // 特禀质

// 四诊类型
export type DiagnosisType = 'inspection' | 'auscultation' | 'inquiry' | 'palpation';

// 诊断结果
export interface DiagnosisResult {
  type: DiagnosisType;
  result: string;
  confidence: number;
  recommendations: string[];
  timestamp: Date;
}

// 健康计划
export interface HealthPlan {
  id: string;
  title: string;
  description: string;
  duration: number; // 天数
  tasks: HealthTask[];
  progress: number; // 0-100
  createdAt: Date;
  updatedAt: Date;
}

// 健康任务
export interface HealthTask {
  id: string;
  title: string;
  description: string;
  type: 'exercise' | 'diet' | 'medication' | 'lifestyle';
  frequency: 'daily' | 'weekly' | 'monthly';
  completed: boolean;
  dueDate?: Date;
}

// 聊天会话
export interface ChatSession {
  id: string;
  title: string;
  agent: import('../components/AgentCard').AgentType;
  messages: import('../components/ChatMessage').Message[];
  createdAt: Date;
  updatedAt: Date;
}

// 用户偏好设置
export interface UserPreferences {
  language: 'zh' | 'en';
  theme: 'light' | 'dark' | 'auto';
  notifications: {
    enabled: boolean;
    healthReminders: boolean;
    agentMessages: boolean;
    systemUpdates: boolean;
  };
  privacy: {
    dataSharing: boolean;
    analytics: boolean;
    personalization: boolean;
  };
} 