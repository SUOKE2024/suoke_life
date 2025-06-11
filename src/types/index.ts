// 索克生活 - 基础类型定义

// 用户相关类型
export interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  profile?: UserProfile;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile {
  firstName: string;
  lastName: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  phone?: string;
  address?: string;
  healthGoals?: string[];
  medicalHistory?: MedicalRecord[];
}

// 健康数据类型
export interface HealthData {
  id: string;
  userId: string;
  type: HealthDataType;
  value: number;
  unit: string;
  timestamp: string;
  source?: string;
  notes?: string;
}

export type HealthDataType = 
  | 'blood_pressure'
  | 'heart_rate'
  | 'weight'
  | 'height'
  | 'temperature'
  | 'blood_sugar'
  | 'sleep_duration'
  | 'steps'
  | 'calories';

// 医疗记录类型
export interface MedicalRecord {
  id: string;
  userId: string;
  type: 'diagnosis' | 'prescription' | 'test_result' | 'consultation';
  title: string;
  description: string;
  date: string;
  doctor?: string;
  hospital?: string;
  attachments?: string[];
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  code?: number;
}

// 分页类型
export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// 智能体类型
export interface Agent {
  id: string;
  name: string;
  type: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  status: 'active' | 'inactive' | 'busy';
  capabilities: string[];
  lastActive: string;
}

// 诊断相关类型
export interface DiagnosisSession {
  id: string;
  userId: string;
  agentId: string;
  type: 'look' | 'listen' | 'ask' | 'feel' | 'smell';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  startTime: string;
  endTime?: string;
  results?: DiagnosisResult[];
}

export interface DiagnosisResult {
  id: string;
  sessionId: string;
  category: string;
  findings: string[];
  confidence: number;
  recommendations: string[];
  timestamp: string;
}

// 通用工具类型
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// 错误类型
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

// 配置类型
export interface AppConfig {
  apiBaseUrl: string;
  enableAnalytics: boolean;
  enablePushNotifications: boolean;
  theme: 'light' | 'dark' | 'auto';
  language: string;
}

export default {
  User,
  UserProfile,
  HealthData,
  HealthDataType,
  MedicalRecord,
  ApiResponse,
  PaginationParams,
  PaginatedResponse,
  Agent,
  DiagnosisSession,
  DiagnosisResult,
  AppError,
  AppConfig,
}; 