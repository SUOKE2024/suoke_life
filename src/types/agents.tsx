import React from 'react';
// 索克生活四智能体系统类型定义   基于README.md第1013-1063行的智能体描述
// 智能体类型枚举
export enum AgentType {
  XIAOAI = 'xiaoai', // 小艾 - 首页聊天频道版主 & 四诊协调智能体
  XIAOKE = 'xiaoke', // 小克 - SUOKE频道版主 & 服务管理智能体
  LAOKE = 'laoke', // 老克 - 探索频道版主 & 知识传播智能体
  SOER = 'soer', // 索儿 - LIFE频道版主 & 生活健康管理智能体
}
// 智能体状态枚举
export enum AgentStatus {
  INITIALIZING = 'initializing',
  ACTIVE = 'active',
  BUSY = 'busy',
  IDLE = 'idle',
  MAINTENANCE = 'maintenance',
  ERROR = 'error',
  OFFLINE = 'offline'}
// 智能体健康状态枚举
export enum AgentHealthStatus {
  HEALTHY = 'healthy',
  WARNING = 'warning',
  CRITICAL = 'critical',
  UNKNOWN = 'unknown'}
// 消息类型枚举
export enum MessageType {
  TEXT = 'text',
  VOICE = 'voice',
  IMAGE = 'image',
  VIDEO = 'video',
  SENSOR_DATA = 'sensor_data',
  DIAGNOSTIC_DATA = 'diagnostic_data',
  COMMAND = 'command',
  NOTIFICATION = 'notification'}
// 基础智能体接口
export interface Agent {
  id: string;,
  name: string;
  type: AgentType;,
  description: string;
  channel: string;,
  role: string;
  capabilities: string[];,
  technicalFeatures: Record<string, boolean>;
  status: AgentStatus;,
  healthStatus: AgentHealthStatus;
  version: string;,
  createdAt: Date;
  lastActivity: Date;
}
// 小艾智能体接口 - 首页聊天频道版主 & 四诊协调智能体
export interface XiaoaiAgent extends Agent {
  type: AgentType.XIAOAI,
  capabilities: [
    'voice_interaction', // 实时语音交互与多语种支持
    'dialect_recognition', // 方言识别与地域化交流
    'tcm_looking_diagnosis', // 中医望诊（面色、舌象、体态分析）
    'tcm_inquiry_diagnosis', // 中医问诊（症状询问、病史收集）
    'accessibility_services', // 无障碍服务（导盲、导医、手语识别）
    'four_diagnosis_coordination', // 四诊协调统筹
    'medical_consultation', // 医疗咨询与健康指导
    'emergency_response', // 紧急情况响应
    'patient_education', // 患者教育与健康科普
    'appointment_scheduling' // 预约挂号与就医引导
  ];
  technicalFeatures: {,
  realTimeVoiceProcessing: boolean; // 实时语音处理,
    multiLanguageSupport: boolean; // 多语言支持,
    dialectRecognition: boolean; // 方言识别,
    tcmDiagnosisAI: boolean; // 中医诊断AI,
    accessibilityCompliance: boolean; // 无障碍标准合规,
    emergencyProtocols: boolean; // 紧急情况处理协议,
    patientPrivacyProtection: boolean; // 患者隐私保护,
    medicalKnowledgeBase: boolean; // 医学知识库集成
  };
}
// 小克智能体接口 - SUOKE频道版主 & 服务管理智能体
export interface XiaokeAgent extends Agent {
  type: AgentType.XIAOKE,
  capabilities: [
    'service_subscription_management', // 服务订阅管理
    'agricultural_product_customization', // 农产品个性化定制
    'supply_chain_optimization', // 供应链优化
    'product_traceability', // 产品溯源管理
    'third_party_api_integration', // 第三方API集成
    'payment_processing', // 支付处理
    'order_management', // 订单管理
    'customer_service', // 客户服务
    'inventory_management', // 库存管理
    'quality_assurance' // 质量保证
  ];
  technicalFeatures: {,
  subscriptionManagement: boolean; // 订阅管理系统,
    agriculturalDataAnalysis: boolean; // 农业数据分析,
    supplyChainTracking: boolean; // 供应链追踪,
    blockchainTraceability: boolean; // 区块链溯源,
    apiGatewayIntegration: boolean; // API网关集成,
    paymentGatewaySupport: boolean; // 支付网关支持,
    inventoryOptimization: boolean; // 库存优化,
    qualityControlSystems: boolean; // 质量控制系统
  };
}
// 老克智能体接口 - 探索频道版主 & 知识传播智能体
export interface LaokeAgent extends Agent {
  type: AgentType.LAOKE,
  capabilities: [
    'knowledge_retrieval', // 知识检索与问答
    'educational_content_creation', // 教育内容创作
    'interactive_learning', // 互动式学习
    'game_npc_interaction', // 游戏NPC交互
    'content_curation', // 内容策展
    'research_assistance', // 研究辅助
    'cultural_heritage_preservation', // 文化遗产保护
    'storytelling', // 故事讲述
    'knowledge_graph_navigation', // 知识图谱导航
    'personalized_learning_paths' // 个性化学习路径
  ];
  technicalFeatures: {,
  knowledgeGraphProcessing: boolean; // 知识图谱处理,
    naturalLanguageGeneration: boolean; // 自然语言生成,
    interactiveLearningPlatforms: boolean; // 互动学习平台,
    gameEngineIntegration: boolean; // 游戏引擎集成,
    contentManagementSystems: boolean; // 内容管理系统,
    researchDatabaseAccess: boolean; // 研究数据库访问,
    culturalDataPreservation: boolean; // 文化数据保存,
    personalizedRecommendations: boolean; // 个性化推荐
  };
}
// 索儿智能体接口 - LIFE频道版主 & 生活健康管理智能体
export interface SoerAgent extends Agent {
  type: AgentType.SOER,
  capabilities: [
    'lifestyle_health_management', // 生活方式健康管理
    'sensor_data_integration', // 传感器数据整合
    'emotional_support', // 情感支持与心理健康
    'wellness_plan_creation', // 健康计划制定
    'habit_tracking', // 习惯追踪
    'nutrition_guidance', // 营养指导
    'exercise_planning', // 运动规划
    'sleep_optimization', // 睡眠优化
    'stress_management', // 压力管理
    'social_wellness_coordination' // 社交健康协调
  ];
  technicalFeatures: {,
  iotSensorIntegration: boolean; // IoT传感器集成,
    healthDataAnalytics: boolean; // 健康数据分析,
    emotionalAISupport: boolean; // 情感AI支持,
    personalizedWellnessPlans: boolean; // 个性化健康计划,
    habitTrackingAlgorithms: boolean; // 习惯追踪算法,
    nutritionDatabaseAccess: boolean; // 营养数据库访问,
    fitnessAppIntegration: boolean; // 健身应用集成,
    sleepPatternAnalysis: boolean; // 睡眠模式分析,
    stressDetectionSystems: boolean; // 压力检测系统,
    socialWellnessMetrics: boolean; // 社交健康指标
  };
}
// 智能体消息接口
export interface AgentMessage {
  id: string;,
  fromAgent: AgentType;
  toAgent?: AgentType;
  userId: string;,
  sessionId: string;
  messageType: MessageType;,
  content: unknown;
  timestamp: Date;,
  priority: 'low' | 'normal' | 'high' | 'urgent';
  metadata?: Record<string, any>;
}
// 智能体响应接口
export interface AgentResponse {
  id: string;,
  agentType: AgentType;
  messageId: string;,
  userId: string;
  sessionId: string;,
  content: unknown;
  responseType: 'text' | 'voice' | 'action' | 'data' | 'error';,
  timestamp: Date;
  processingTime: number;
  confidence?: number;
  metadata?: Record<string, any>;
}
// 智能体协作接口
export interface AgentCollaboration {
  id: string;,
  initiatorAgent: AgentType;
  participantAgents: AgentType[];,
  collaborationType: 'consultation' | 'data_sharing' | 'task_delegation' | 'knowledge_exchange';
  status: 'pending' | 'active' | 'completed' | 'failed';,
  startTime: Date;
  endTime?: Date;
  result?: unknown;
}
// 智能体事件接口
export interface AgentEvent {
  id: string;,
  agentType: AgentType;
  eventType: 'status_change' | 'error' | 'collaboration_request' | 'task_completion';,
  timestamp: Date;
  data: unknown;,
  severity: 'info' | 'warning' | 'error' | 'critical';
}
// API响应接口
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string,
  message: string;
    details?: unknown;
  };
  timestamp: Date,
  requestId: string;
  agentType?: AgentType;
}
// 智能体配置接口
export interface AgentConfiguration {
  agentType: AgentType;,
  settings: Record<string, any>;
  capabilities: string[];,
  technicalFeatures: Record<string, boolean>;
  resourceLimits: {;,
  maxConcurrentSessions: number;
    maxMemoryUsage: number;,
  maxCpuUsage: number;
};
  lastUpdated: Date;
}
// 智能体性能指标接口
export interface AgentMetrics {
  agentType: AgentType;,
  timestamp: Date;
  performance: {;,
  responseTime: number;
    throughput: number;,
  errorRate: number;
    successRate: number;
};
  resources: {,
  cpuUsage: number;
    memoryUsage: number,
  networkUsage: number;
  };
  sessions: {,
  active: number;
    total: number,
  averageDuration: number;
  };
}
// 四诊聚合结果接口
export interface FourDiagnosisAggregationResult {
  sessionId: string;,
  userId: string;
  timestamp: Date;,
  diagnosisResults: {;
    looking: {;,
  faceColor: string;
      tongueImage: string;,
  bodyPosture: string;
      confidence: number;
};
    listening: {,
  voiceQuality: string;
      breathingPattern: string,
  heartRate: number;,
  confidence: number;
    };
    inquiry: {,
  symptoms: string[];
      medicalHistory: string[],
  lifestyle: Record<string, any>;
      confidence: number;
    };
    palpation: {,
  pulseType: string;
      pulseRate: number,
  bodyTemperature: number;,
  confidence: number;
    };
  };
  syndromeAnalysis: {,
  primarySyndrome: string;
    secondarySyndromes: string[],
  confidence: number;,
  recommendations: string[];
  };
  overallAssessment: {,
  healthScore: number;
    riskLevel: 'low' | 'medium' | 'high',
  urgency: 'routine' | 'priority' | 'urgent';,
  followUpRequired: boolean;
  };
}
// 导出所有类型
export type AnyAgent = XiaoaiAgent | XiaokeAgent | LaokeAgent | SoerAgent;