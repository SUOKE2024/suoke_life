/**
 * 索克生活项目 - 协作类型定义
 * 定义智能体协作和中医体质相关的类型
 */

// 中医体质类型枚举
export enum ConstitutionType {
  BALANCED = 'balanced', // 平和质
  QI_DEFICIENCY = 'qi_deficiency', // 气虚质
  YANG_DEFICIENCY = 'yang_deficiency', // 阳虚质
  YIN_DEFICIENCY = 'yin_deficiency', // 阴虚质
  PHLEGM_DAMPNESS = 'phlegm_dampness', // 痰湿质
  DAMP_HEAT = 'damp_heat', // 湿热质
  BLOOD_STASIS = 'blood_stasis', // 血瘀质
  QI_STAGNATION = 'qi_stagnation', // 气郁质
  SPECIAL_DIATHESIS = 'special_diathesis', // 特禀质
}

// 智能体类型
export enum AgentType {
  XIAOAI = 'xiaoai', // 小艾 - 健康助手
  XIAOKE = 'xiaoke', // 小克 - 诊断专家
  LAOKE = 'laoke', // 老克 - 治疗顾问
  SOER = 'soer', // 索儿 - 生活管家
}

// 任务优先级
export enum TaskPriority {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4
}

// 任务状态
export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 协作状态
export enum CollaborationStatus {
  IDLE = 'idle',
  ACTIVE = 'active',
  WAITING = 'waiting',
  COMPLETED = 'completed',
  ERROR = 'error'
}

// 消息类型
export enum MessageType {
  REQUEST = 'request',
  RESPONSE = 'response',
  NOTIFICATION = 'notification',
  ERROR = 'error'
}

// 智能体协作接口
export interface AgentCollaboration {
  id: string;
  initiator: AgentType;
  participants: AgentType[];
  status: CollaborationStatus;
  context: CollaborationContext;
  messages: CollaborationMessage[];
  createdAt: Date;
  updatedAt: Date;
}

// 协作上下文
export interface CollaborationContext {
  userId: string;
  sessionId: string;
  task: string;
  priority: 'low' | 'medium' | 'high';
  metadata: Record<string, any>;
}

// 协作消息
export interface CollaborationMessage {
  id: string;
  from: AgentType;
  to: AgentType[];
  type: MessageType;
  content: any;
  timestamp: Date;
}

// 协作任务
export interface CollaborationTask {
  id: string;
  title: string;
  description: string;
  requiredCapabilities: string[];
  priority: TaskPriority;
  status: TaskStatus;
  createdAt: Date;
  updatedAt?: Date;
  completedAt?: Date;
  assignedAgents: string[];
  result?: any;
  metadata?: Record<string; any>;
}

// 体质分析结果
export interface ConstitutionAnalysis {
  primaryType: ConstitutionType;
  secondaryTypes: ConstitutionType[];
  confidence: number;
  characteristics: string[];
  recommendations: string[];
  analysisDate: Date;
}

// 症状数据
export interface SymptomData {
  name: string;
  severity: number; // 1-10;,
  duration: string;
  frequency: string;
  description?: string;
}

// 生命体征
export interface VitalSigns {
  heartRate?: number;
  bloodPressure?: {
    systolic: number;
  diastolic: number;
  };
  temperature?: number;
  weight?: number;
  height?: number;
}

// 生活方式数据
export interface LifestyleData {
  sleepHours: number;
  exerciseFrequency: number;
  dietType: string;
  stressLevel: number;
  smokingStatus: boolean;
  alcoholConsumption: string;
}

// 健康数据接口
export interface HealthData {
  userId: string;
  constitution: ConstitutionAnalysis;
  symptoms: SymptomData[];
  vitalSigns: VitalSigns;
  lifestyle: LifestyleData;
  timestamp: Date;
}

// 诊断结果
export interface DiagnosisResult {
  tcmDiagnosis: {,
  syndrome: string;
  pattern: string;
  constitution: ConstitutionType;
  meridians: string[];
  organs: string[];
  pathogenesis: string;
  treatmentPrinciple: string;
  confidence: number;
  };
  modernDiagnosis: {,
  primaryDiagnosis: string;
  differentialDiagnosis: string[];
  icdCodes: string[];
  severity: 'mild' | 'moderate' | 'severe';
  prognosis: string;
  recommendedTests: string[];
  confidence: number;
  };
  confidence: number;
}

// 治疗结果
export interface TreatmentResult {
  plan: {,
  tcmTreatment: {
      herbalFormula?: string;
      acupuncturePoints?: string[];
      massageTechniques?: string[];
      dietaryTherapy?: string[];
    };
    modernTreatment: {
      medications?: string[];
      procedures?: string[];
      lifestyleModifications?: string[];
    };
    duration: string;
  targetConstitution: ConstitutionType;
  };
  validation: {,
  safetyCheck: boolean;
  drugInteractions: string[];
  contraindications: string[];
  suggestedAdjustments: string[];
  approvalStatus: 'approved' | 'needs_modification' | 'rejected';
  };
  adjustments: string[];
}

// 协作结果
export interface CollaborationResult {
  analysis?: any;
  diagnosis?: DiagnosisResult;
  treatment?: TreatmentResult;
  lifestyle?: any;
  confidence: number;
  recommendations: string[];
  timestamp: Date;
}
