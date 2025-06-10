';'';
// 索克生活四智能体系统类型定义   基于README.md第1013-1063行的智能体描述/;/g/;
// 智能体类型枚举'/;,'/g'/;
export enum AgentType {';,}XIAOAI = 'xiaoai', // 小艾 - 首页聊天频道版主 & 四诊协调智能体'/;,'/g'/;
XIAOKE = 'xiaoke', // 小克 - SUOKE频道版主 & 服务管理智能体'/;,'/g'/;
LAOKE = 'laoke', // 老克 - 探索频道版主 & 知识传播智能体'/;'/g'/;
}
}
  SOER = 'soer', // 索儿 - LIFE频道版主 & 生活健康管理智能体'}''/;'/g'/;
}
// 智能体状态枚举'/;,'/g'/;
export enum AgentStatus {';,}INITIALIZING = 'initializing',';,'';
ACTIVE = 'active',';,'';
BUSY = 'busy',';,'';
IDLE = 'idle',';,'';
MAINTENANCE = 'maintenance',';'';
}
}
  ERROR = 'error',}';,'';
OFFLINE = 'offline'}';'';
// 智能体健康状态枚举'/;,'/g'/;
export enum AgentHealthStatus {';,}HEALTHY = 'healthy',';,'';
WARNING = 'warning',';'';
}
}
  CRITICAL = 'critical',}';,'';
UNKNOWN = 'unknown'}';'';
// 消息类型枚举'/;,'/g'/;
export enum MessageType {';,}TEXT = 'text',';,'';
VOICE = 'voice',';,'';
IMAGE = 'image',';,'';
VIDEO = 'video',';,'';
SENSOR_DATA = 'sensor_data',';,'';
DIAGNOSTIC_DATA = 'diagnostic_data',';'';
}
}
  COMMAND = 'command',}';,'';
NOTIFICATION = 'notification'}';'';
// 基础智能体接口/;,/g/;
export interface Agent {id: string}name: string,;
type: AgentType,;
description: string,;
channel: string,;
role: string,;
capabilities: string[],;
technicalFeatures: Record<string, boolean>;
status: AgentStatus,;
healthStatus: AgentHealthStatus,;
version: string,;
createdAt: Date,;
}
}
  const lastActivity = Date;}
}
// 小艾智能体接口 - 首页聊天频道版主 & 四诊协调智能体/;,/g/;
export interface XiaoaiAgent extends Agent {type: AgentType.XIAOAI,';,}const capabilities = [;]';'';
    'voice_interaction', // 实时语音交互与多语种支持'/;'/g'/;
    'dialect_recognition', // 方言识别与地域化交流'/;'/g'/;
    'tcm_looking_diagnosis', // 中医望诊（面色、舌象、体态分析）'/;'/g'/;
    'tcm_inquiry_diagnosis', // 中医问诊（症状询问、病史收集）'/;'/g'/;
    'accessibility_services', // 无障碍服务（导盲、导医、手语识别）'/;'/g'/;
    'four_diagnosis_coordination', // 四诊协调统筹'/;'/g'/;
    'medical_consultation', // 医疗咨询与健康指导'/;'/g'/;
    'emergency_response', // 紧急情况响应'/;'/g'/;
    'patient_education', // 患者教育与健康科普'/;'/g'/;
    'appointment_scheduling' // 预约挂号与就医引导';/;'/g'/;
];
  ];
technicalFeatures: {realTimeVoiceProcessing: boolean; // 实时语音处理,/;,/g,/;
  multiLanguageSupport: boolean; // 多语言支持,/;,/g,/;
  dialectRecognition: boolean; // 方言识别,/;,/g,/;
  tcmDiagnosisAI: boolean; // 中医诊断AI,/;,/g,/;
  accessibilityCompliance: boolean; // 无障碍标准合规,/;,/g,/;
  emergencyProtocols: boolean; // 紧急情况处理协议,/;,/g,/;
  patientPrivacyProtection: boolean; // 患者隐私保护,/;/g/;
}
    const medicalKnowledgeBase = boolean; // 医学知识库集成}/;/g/;
  };
}
// 小克智能体接口 - SUOKE频道版主 & 服务管理智能体/;,/g/;
export interface XiaokeAgent extends Agent {type: AgentType.XIAOKE,';,}const capabilities = [;]';'';
    'service_subscription_management', // 服务订阅管理'/;'/g'/;
    'agricultural_product_customization', // 农产品个性化定制'/;'/g'/;
    'supply_chain_optimization', // 供应链优化'/;'/g'/;
    'product_traceability', // 产品溯源管理'/;'/g'/;
    'third_party_api_integration', // 第三方API集成'/;'/g'/;
    'payment_processing', // 支付处理'/;'/g'/;
    'order_management', // 订单管理'/;'/g'/;
    'customer_service', // 客户服务'/;'/g'/;
    'inventory_management', // 库存管理'/;'/g'/;
    'quality_assurance' // 质量保证';/;'/g'/;
];
  ];
technicalFeatures: {subscriptionManagement: boolean; // 订阅管理系统,/;,/g,/;
  agriculturalDataAnalysis: boolean; // 农业数据分析,/;,/g,/;
  supplyChainTracking: boolean; // 供应链追踪,/;,/g,/;
  blockchainTraceability: boolean; // 区块链溯源,/;,/g,/;
  apiGatewayIntegration: boolean; // API网关集成,/;,/g,/;
  paymentGatewaySupport: boolean; // 支付网关支持,/;,/g,/;
  inventoryOptimization: boolean; // 库存优化,/;/g/;
}
    const qualityControlSystems = boolean; // 质量控制系统}/;/g/;
  };
}
// 老克智能体接口 - 探索频道版主 & 知识传播智能体/;,/g/;
export interface LaokeAgent extends Agent {type: AgentType.LAOKE,';,}const capabilities = [;]';'';
    'knowledge_retrieval', // 知识检索与问答'/;'/g'/;
    'educational_content_creation', // 教育内容创作'/;'/g'/;
    'interactive_learning', // 互动式学习'/;'/g'/;
    'game_npc_interaction', // 游戏NPC交互'/;'/g'/;
    'content_curation', // 内容策展'/;'/g'/;
    'research_assistance', // 研究辅助'/;'/g'/;
    'cultural_heritage_preservation', // 文化遗产保护'/;'/g'/;
    'storytelling', // 故事讲述'/;'/g'/;
    'knowledge_graph_navigation', // 知识图谱导航'/;'/g'/;
    'personalized_learning_paths' // 个性化学习路径';/;'/g'/;
];
  ];
technicalFeatures: {knowledgeGraphProcessing: boolean; // 知识图谱处理,/;,/g,/;
  naturalLanguageGeneration: boolean; // 自然语言生成,/;,/g,/;
  interactiveLearningPlatforms: boolean; // 互动学习平台,/;,/g,/;
  gameEngineIntegration: boolean; // 游戏引擎集成,/;,/g,/;
  contentManagementSystems: boolean; // 内容管理系统,/;,/g,/;
  researchDatabaseAccess: boolean; // 研究数据库访问,/;,/g,/;
  culturalDataPreservation: boolean; // 文化数据保存,/;/g/;
}
    const personalizedRecommendations = boolean; // 个性化推荐}/;/g/;
  };
}
// 索儿智能体接口 - LIFE频道版主 & 生活健康管理智能体/;,/g/;
export interface SoerAgent extends Agent {type: AgentType.SOER,';,}const capabilities = [;]';'';
    'lifestyle_health_management', // 生活方式健康管理'/;'/g'/;
    'sensor_data_integration', // 传感器数据整合'/;'/g'/;
    'emotional_support', // 情感支持与心理健康'/;'/g'/;
    'wellness_plan_creation', // 健康计划制定'/;'/g'/;
    'habit_tracking', // 习惯追踪'/;'/g'/;
    'nutrition_guidance', // 营养指导'/;'/g'/;
    'exercise_planning', // 运动规划'/;'/g'/;
    'sleep_optimization', // 睡眠优化'/;'/g'/;
    'stress_management', // 压力管理'/;'/g'/;
    'social_wellness_coordination' // 社交健康协调';/;'/g'/;
];
  ];
technicalFeatures: {iotSensorIntegration: boolean; // IoT传感器集成,/;,/g,/;
  healthDataAnalytics: boolean; // 健康数据分析,/;,/g,/;
  emotionalAISupport: boolean; // 情感AI支持,/;,/g,/;
  personalizedWellnessPlans: boolean; // 个性化健康计划,/;,/g,/;
  habitTrackingAlgorithms: boolean; // 习惯追踪算法,/;,/g,/;
  nutritionDatabaseAccess: boolean; // 营养数据库访问,/;,/g,/;
  fitnessAppIntegration: boolean; // 健身应用集成,/;,/g,/;
  sleepPatternAnalysis: boolean; // 睡眠模式分析,/;,/g,/;
  stressDetectionSystems: boolean; // 压力检测系统,/;/g/;
}
    const socialWellnessMetrics = boolean; // 社交健康指标}/;/g/;
  };
}
// 智能体消息接口/;,/g/;
export interface AgentMessage {id: string}const fromAgent = AgentType;
toAgent?: AgentType;
userId: string,;
sessionId: string,;
messageType: MessageType,;
content: unknown,';,'';
timestamp: Date,';,'';
const priority = 'low' | 'normal' | 'high' | 'urgent';';'';
}
}
  metadata?: Record<string; any>;}
}
// 智能体响应接口/;,/g/;
export interface AgentResponse {id: string}agentType: AgentType,;
messageId: string,;
userId: string,;
sessionId: string,';,'';
content: unknown,';,'';
responseType: 'text' | 'voice' | 'action' | 'data' | 'error';','';
timestamp: Date,;
const processingTime = number;
confidence?: number;
}
}
  metadata?: Record<string; any>;}
}
// 智能体协作接口/;,/g/;
export interface AgentCollaboration {id: string}initiatorAgent: AgentType,';,'';
participantAgents: AgentType[],';,'';
collaborationType: 'consultation' | 'data_sharing' | 'task_delegation' | 'knowledge_exchange';','';
status: 'pending' | 'active' | 'completed' | 'failed';','';
const startTime = Date;
endTime?: Date;
}
}
  result?: unknown;}
}
// 智能体事件接口/;,/g/;
export interface AgentEvent {id: string,';,}agentType: AgentType,';,'';
eventType: 'status_change' | 'error' | 'collaboration_request' | 'task_completion';','';
timestamp: Date,';,'';
data: unknown,';'';
}
}
  const severity = 'info' | 'warning' | 'error' | 'critical';'}'';'';
}
// API响应接口/;,/g/;
export interface ApiResponse<T> {;,}const success = boolean;
data?: T;
error?: {code: string}const message = string;
}
    details?: unknown;}
  };
timestamp: Date,;
const requestId = string;
agentType?: AgentType;
}
// 智能体配置接口/;,/g/;
export interface AgentConfiguration {agentType: AgentType}settings: Record<string, any>;
capabilities: string[],;
technicalFeatures: Record<string, boolean>;
resourceLimits: {maxConcurrentSessions: number,;
maxMemoryUsage: number,;
}
}
  const maxCpuUsage = number;}
};
const lastUpdated = Date;
}
// 智能体性能指标接口/;,/g/;
export interface AgentMetrics {agentType: AgentType}timestamp: Date,;
performance: {responseTime: number,;
throughput: number,;
errorRate: number,;
}
}
  const successRate = number;}
};
resources: {cpuUsage: number,;
memoryUsage: number,;
}
  const networkUsage = number;}
  };
sessions: {active: number,;
total: number,;
}
  const averageDuration = number;}
  };
}
// 四诊聚合结果接口/;,/g/;
export interface FourDiagnosisAggregationResult {sessionId: string}userId: string,;
timestamp: Date,;
diagnosisResults: {looking: {faceColor: string,;
tongueImage: string,;
bodyPosture: string,;
}
}
  const confidence = number;}
};
listening: {voiceQuality: string,;
breathingPattern: string,;
heartRate: number,;
}
  const confidence = number;}
    };
inquiry: {symptoms: string[],;
medicalHistory: string[],;
lifestyle: Record<string, any>;
}
      const confidence = number;}
    };
palpation: {pulseType: string,;
pulseRate: number,;
bodyTemperature: number,;
}
  const confidence = number;}
    };
  };
syndromeAnalysis: {primarySyndrome: string,;
secondarySyndromes: string[],;
confidence: number,;
}
  const recommendations = string[];}
  };
overallAssessment: {,';,}healthScore: number,';,'';
riskLevel: 'low' | 'medium' | 'high';','';
urgency: 'routine' | 'priority' | 'urgent';','';'';
}
  const followUpRequired = boolean;}
  };
}
// 导出所有类型'/;,'/g'/;
export type AnyAgent = XiaoaiAgent | XiaokeAgent | LaokeAgent | SoerAgent;