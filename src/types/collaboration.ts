/* 型 *//;/g/;
 *//;/g/;

// 中医体质类型枚举/;,/g/;
export enum ConstitutionType {BALANCED = 'balanced', // 平和质'/;,}QI_DEFICIENCY = 'qi_deficiency', // 气虚质'/;,'/g'/;
YANG_DEFICIENCY = 'yang_deficiency', // 阳虚质'/;,'/g'/;
YIN_DEFICIENCY = 'yin_deficiency', // 阴虚质'/;,'/g'/;
PHLEGM_DAMPNESS = 'phlegm_dampness', // 痰湿质'/;,'/g'/;
DAMP_HEAT = 'damp_heat', // 湿热质'/;,'/g'/;
BLOOD_STASIS = 'blood_stasis', // 血瘀质'/;,'/g'/;
QI_STAGNATION = 'qi_stagnation', // 气郁质'/;'/g'/;
}
}
  SPECIAL_DIATHESIS = 'special_diathesis', // 特禀质'}''/;'/g'/;
}

// 智能体类型'/;,'/g'/;
export enum AgentType {';,}XIAOAI = 'xiaoai', // 小艾 - 健康助手'/;,'/g'/;
XIAOKE = 'xiaoke', // 小克 - 诊断专家'/;,'/g'/;
LAOKE = 'laoke', // 老克 - 治疗顾问'/;'/g'/;
}
}
  SOER = 'soer', // 索儿 - 生活管家'}''/;'/g'/;
}

// 任务优先级/;,/g/;
export enum TaskPriority {LOW = 1}MEDIUM = 2,;
HIGH = 3,;
}
}
  CRITICAL = 4}
}

// 任务状态'/;,'/g'/;
export enum TaskStatus {';,}PENDING = 'pending',';,'';
IN_PROGRESS = 'in_progress',';,'';
COMPLETED = 'completed',';,'';
FAILED = 'failed',';'';
}
}
  CANCELLED = 'cancelled'}'';'';
}

// 协作状态'/;,'/g'/;
export enum CollaborationStatus {';,}IDLE = 'idle',';,'';
ACTIVE = 'active',';,'';
WAITING = 'waiting',';,'';
COMPLETED = 'completed',';'';
}
}
  ERROR = 'error'}'';'';
}

// 消息类型'/;,'/g'/;
export enum MessageType {';,}REQUEST = 'request',';,'';
RESPONSE = 'response',';,'';
NOTIFICATION = 'notification',';'';
}
}
  ERROR = 'error'}'';'';
}

// 智能体协作接口/;,/g/;
export interface AgentCollaboration {id: string}initiator: AgentType,;
participants: AgentType[],;
status: CollaborationStatus,;
context: CollaborationContext,;
messages: CollaborationMessage[],;
createdAt: Date,;
}
}
  const updatedAt = Date;}
}

// 协作上下文/;,/g/;
export interface CollaborationContext {userId: string}sessionId: string,';,'';
task: string,';,'';
priority: 'low' | 'medium' | 'high';','';'';
}
}
  metadata: Record<string, any>;}
}

// 协作消息/;,/g/;
export interface CollaborationMessage {id: string}from: AgentType,;
to: AgentType[],;
type: MessageType,;
content: any,;
}
}
  const timestamp = Date;}
}

// 协作任务/;,/g/;
export interface CollaborationTask {id: string}title: string,;
description: string,;
requiredCapabilities: string[],;
priority: TaskPriority,;
status: TaskStatus,;
const createdAt = Date;
updatedAt?: Date;
completedAt?: Date;
const assignedAgents = string[];
result?: any;
}
}
  metadata?: Record<string; any>;}
}

// 体质分析结果/;,/g/;
export interface ConstitutionAnalysis {primaryType: ConstitutionType}secondaryTypes: ConstitutionType[],;
confidence: number,;
characteristics: string[],;
recommendations: string[],;
}
}
  const analysisDate = Date;}
}

// 症状数据/;,/g/;
export interface SymptomData {name: string}severity: number; // 1-10,/;,/g,/;
  duration: string,;
const frequency = string;
}
}
  description?: string;}
}

// 生命体征/;,/g/;
export interface VitalSigns {;,}heartRate?: number;
bloodPressure?: {systolic: number,;}}
}
  const diastolic = number;}
  };
temperature?: number;
weight?: number;
height?: number;
}

// 生活方式数据/;,/g/;
export interface LifestyleData {sleepHours: number}exerciseFrequency: number,;
dietType: string,;
stressLevel: number,;
smokingStatus: boolean,;
}
}
  const alcoholConsumption = string;}
}

// 健康数据接口/;,/g/;
export interface HealthData {userId: string}constitution: ConstitutionAnalysis,;
symptoms: SymptomData[],;
vitalSigns: VitalSigns,;
lifestyle: LifestyleData,;
}
}
  const timestamp = Date;}
}

// 诊断结果/;,/g/;
export interface DiagnosisResult {tcmDiagnosis: {syndrome: string,;
pattern: string,;
constitution: ConstitutionType,;
meridians: string[],;
organs: string[],;
pathogenesis: string,;
treatmentPrinciple: string,;
}
}
  const confidence = number;}
  };
modernDiagnosis: {primaryDiagnosis: string,;
differentialDiagnosis: string[],';,'';
icdCodes: string[],';,'';
severity: 'mild' | 'moderate' | 'severe';','';
prognosis: string,;
recommendedTests: string[],;
}
  const confidence = number;}
  };
const confidence = number;
}

// 治疗结果/;,/g/;
export interface TreatmentResult {plan: {const tcmTreatment = {;,}herbalFormula?: string;
acupuncturePoints?: string[];
massageTechniques?: string[];
}
}
      dietaryTherapy?: string[];}
    };
const modernTreatment = {medications?: string[];,}procedures?: string[];
}
      lifestyleModifications?: string[];}
    };
duration: string,;
const targetConstitution = ConstitutionType;
  };
validation: {safetyCheck: boolean,;
drugInteractions: string[],;
contraindications: string[],';,'';
suggestedAdjustments: string[],';'';
}
  const approvalStatus = 'approved' | 'needs_modification' | 'rejected';'}'';'';
  };
const adjustments = string[];
}

// 协作结果/;,/g/;
export interface CollaborationResult {;,}analysis?: any;
diagnosis?: DiagnosisResult;
treatment?: TreatmentResult;
lifestyle?: any;
confidence: number,;
recommendations: string[],;
}
}
  const timestamp = Date;}
}';'';
''';