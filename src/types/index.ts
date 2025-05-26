// 索克生活通用类型定义

// 四诊类型
export type DiagnosisType = 'inspection' | 'auscultation' | 'inquiry' | 'palpation';

// 用户体质类型
export type ConstitutionType = 
  | '平和质'
  | '气虚质' 
  | '阳虚质'
  | '阴虚质'
  | '痰湿质'
  | '湿热质'
  | '血瘀质'
  | '气郁质'
  | '特禀质';

// 季节类型
export type SeasonType = '春季' | '夏季' | '秋季' | '冬季';

// 服务状态
export type ServiceStatus = 'available' | 'unavailable' | 'maintenance';

// 健康数据类型
export interface HealthData {
  id: string;
  userId: string;
  type: 'vital_signs' | 'symptoms' | 'diagnosis' | 'treatment';
  data: any;
  timestamp: number;
  source: string;
}

// 用户基本信息
export interface UserBasicInfo {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  constitution: ConstitutionType;
  location?: string;
}

// API响应基础类型
// 修复ApiResponse类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: number;
}

// 分页数据类型
export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// 错误类型
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: number;
}

// 导出所有类型
export * from '../agents/xiaoai/types'; 
// Redux State Types
export interface RootState {
  auth: AuthState;
  user: UserState;
  health: HealthState;
  diagnosis: DiagnosisState;
  agents: AgentsState;
  ui: UIState;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  loading: boolean;
  error: string | null;
}

export interface UserState {
  profile: UserProfile | null;
  healthData: HealthData[];
  loading: boolean;
  error: string | null;
}

export interface HealthState {
  data: HealthData[];
  summary: HealthSummary | null;
  trends: any[];
  loading: boolean;
  error: string | null;
}

export interface DiagnosisState {
  sessions: DiagnosisSession[];
  currentSession: string | null;
  loading: boolean;
  error: string | null;
}

export interface AgentsState {
  conversations: { [agentType: string]: AgentMessage[] };
  activeAgent: AgentType | null;
  loading: boolean;
  error: string | null;
}

export interface UIState {
  theme: 'light' | 'dark';
  notifications: Notification[];
  loading: boolean;
  error: string | null;
}

// User Types
export interface User {
  id: string;
  email: string;
  username: string;
  profile: UserProfile;
  createdAt: string;
  updatedAt: string;
}

// Health Types
export interface HealthSummary {
  overallScore: number;
  constitution: ConstitutionType;
  recommendations: string[];
  lastUpdated: string;
}

export type HealthDataType = 'vitals' | 'symptoms' | 'lifestyle' | 'medication';

// Diagnosis Types
export interface DiagnosisSession {
  id: string;
  type: DiagnosisType;
  status: 'active' | 'completed' | 'cancelled';
  data: DiagnosisData;
  result?: DiagnosisResult;
  createdAt: string;
  updatedAt: string;
}

export interface DiagnosisData {
  symptoms: string[];
  images: string[];
  audio: string[];
  notes: string;
}

export interface DiagnosisResult {
  constitution: ConstitutionType;
  recommendations: string[];
  confidence: number;
  analysis: string;
}

// Agent Types
export interface AgentMessage {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: string;
  agentType: AgentType;
}

export interface AgentResponse {
  message: string;
  suggestions?: string[];
  actions?: string[];
}

// Notification Types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  timestamp: string;
}
