// 用户相关类型
export interface User {
  id: string;
  username: string;
  email: string;
  phone?: string;
  avatar?: string;
  profile: UserProfile;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile {
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  height?: number; // cm
  weight?: number; // kg
  constitution?: ConstitutionType;
  medicalHistory: string[];
  allergies: string[];
}

// 中医体质类型
export type ConstitutionType =
  | 'balanced' // 平和质
  | 'qi_deficiency' // 气虚质
  | 'yang_deficiency' // 阳虚质
  | 'yin_deficiency' // 阴虚质
  | 'phlegm_dampness' // 痰湿质
  | 'damp_heat' // 湿热质
  | 'blood_stasis' // 血瘀质
  | 'qi_stagnation' // 气郁质
  | 'special_diathesis'; // 特禀质

// 四诊数据类型
export interface DiagnosisData {
  id: string;
  userId: string;
  sessionId: string;
  type: DiagnosisType;
  data: any;
  result?: DiagnosisResult;
  createdAt: string;
}

export type DiagnosisType =
  | 'inspection'
  | 'auscultation'
  | 'inquiry'
  | 'palpation';

export interface DiagnosisResult {
  score: number;
  analysis: string;
  recommendations: string[];
  constitution?: ConstitutionType;
}

// 智能体类型
export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';

export interface AgentMessage {
  id: string;
  agentType: AgentType;
  content: string;
  type: 'text' | 'image' | 'audio' | 'file';
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface AgentResponse {
  success: boolean;
  data?: any;
  message?: string;
  error?: string;
}

// 健康数据类型
export interface HealthData {
  id: string;
  userId: string;
  type: HealthDataType;
  value: number | string | object;
  unit?: string;
  timestamp: string;
  source: 'manual' | 'device' | 'calculation';
}

export type HealthDataType =
  | 'heart_rate'
  | 'blood_pressure'
  | 'body_temperature'
  | 'sleep_quality'
  | 'stress_level'
  | 'mood'
  | 'exercise'
  | 'nutrition';

// 区块链相关类型
export interface HealthNFT {
  tokenId: string;
  owner: string;
  constitutionType: ConstitutionType;
  issueDate: string;
  expiryDate: string;
  verified: boolean;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// 导航类型
export type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  Register: undefined;
  Profile: undefined;
  Diagnosis: undefined;
  AgentChat: { agentType: AgentType };
  HealthDashboard: undefined;
  Settings: undefined;
};

// 状态管理类型
export interface RootState {
  auth: AuthState;
  user: UserState;
  agents: AgentsState;
  diagnosis: DiagnosisState;
  health: HealthState;
  ui: UIState;
}

export interface AuthState {
  isAuthenticated: boolean;
  token?: string;
  refreshToken?: string;
  user?: User;
  loading: boolean;
  error?: string;
}

export interface UserState {
  profile?: UserProfile;
  healthData: HealthData[];
  loading: boolean;
  error?: string;
}

export interface AgentsState {
  conversations: Record<AgentType, AgentMessage[]>;
  activeAgent?: AgentType;
  loading: boolean;
  error?: string;
}

export interface DiagnosisState {
  currentSession?: string;
  sessions: DiagnosisSession[];
  results: DiagnosisResult[];
  loading: boolean;
  error?: string;
}

export interface DiagnosisSession {
  id: string;
  userId: string;
  startTime: string;
  endTime?: string;
  status: 'active' | 'completed' | 'cancelled';
  data: Record<DiagnosisType, any>;
}

export interface HealthState {
  data: HealthData[];
  summary: HealthSummary;
  loading: boolean;
  error?: string;
}

export interface HealthSummary {
  overallScore: number;
  constitution: ConstitutionType;
  recommendations: string[];
  trends: Record<HealthDataType, 'improving' | 'stable' | 'declining'>;
}

export interface UIState {
  theme: 'light' | 'dark';
  language: 'zh' | 'en';
  notifications: Notification[];
  loading: boolean;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
  read: boolean;
}

// 网络请求配置
export interface RequestConfig {
  timeout?: number;
  retries?: number;
  cache?: boolean;
  headers?: Record<string, string>;
}

// 错误类型
export class AppError extends Error {
  public code: string;
  public details?: any;

  constructor(message: string, code: string, details?: any) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.details = details;
  }
}
