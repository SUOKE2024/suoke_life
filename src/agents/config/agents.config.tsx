import { AgentType } from '../types/agents';
import React from 'react';
// 索克生活四智能体系统配置
// 基于README.md第1013-1063行的智能体描述
export interface AgentConfig {
  id: string;,
  name: string;
  type: AgentType;,
  description: string;
  channel: string;,
  role: string;
  capabilities: string[];,
  technicalFeatures: Record<string, boolean>;
  apiEndpoint: string;,
  port: number;
  enabled: boolean;,
  maxConcurrentTasks: number;
  responseTimeout: number;,
  retryAttempts: number;
}
// 小艾智能体配置 - 首页聊天频道版主 & 四诊协调智能体
export const XIAOAI_CONFIG: AgentConfig = {,
  id: 'xiaoai-001',
  name: '小艾',
  type: AgentType.XIAOAI,
  description:
    '索克生活APP首页（聊天频道）版主，为用户提供语音引导、交互、问诊，以及包括导盲、导医、手语识别等无障碍服务，统筹协调望诊、闻诊、问诊、切诊、算诊服务。',
  channel: '首页聊天频道',
  role: '四诊协调智能体',
  capabilities: [
    'voice_interaction', // 实时语音交互与多语种支持
    'dialect_recognition', // 方言识别
    'face_analysis', // 中医望诊面色分析
    'tongue_diagnosis', // 舌诊图像处理
    'intelligent_inquiry', // 智能问诊系统
    'constitution_screening', // 体质筛查
    'symptom_assessment', // 症状评估
    'health_consultation', // 健康咨询
    'calculation_diagnosis', // 算诊
    'medical_record_management', // 医疗记录自动整理
    'health_archive_management', // 健康档案管理
    'accessibility_services', // 无障碍服务
    'guide_services', // 导盲、导医服务
    'sign_language_recognition', // 手语识别
    'elderly_friendly_interface', // 老年友好界面
  ],
  technicalFeatures: {,
  multimodalLLM: true, // 多模态大语言模型 (GPT-4o / Gemini 1.5 Pro)
    localModel: true, // 轻量级本地模型 (Llama 3-8B)
    visionRecognition: true, // 视觉识别组件
    fourDiagnosisIntegration: true, // 四诊合参模块集成
    healthArchiveIntegration: true, // 健康档案系统集成
  },
  apiEndpoint: 'http://localhost:50053',
  port: 50053,
  enabled: true,
  maxConcurrentTasks: 10,
  responseTimeout: 30000,
  retryAttempts: 3,
};
// 小克智能体配置 - SUOKE频道版主 & 服务管理智能体
export const XIAOKE_CONFIG: AgentConfig = {,
  id: 'xiaoke-001',
  name: '小克',
  type: AgentType.XIAOKE,
  description:
    '索克生活APP SUOKE频道版主，负责索克生活服务订阅、优质农产品预（定）制、供应链管理、农事活动体验、第三方API服务集成、索克店铺管理等工作。',
  channel: 'SUOKE频道',
  role: '服务管理智能体',
  capabilities: [
    'doctor_matching', // 名医资源智能匹配
    'appointment_management', // 预约管理
    'service_subscription', // 医疗服务订阅
    'personalized_recommendation', // 个性化推荐
    'product_traceability', // 农产品溯源
    'custom_delivery', // 定制配送管理
    'third_party_api_integration', // 第三方API集成
    'insurance_integration', // 保险集成
    'payment_integration', // 支付集成
    'logistics_integration', // 物流集成
    'store_management', // 在线店铺管理
    'health_product_recommendation', // 健康商品推荐
  ],
  technicalFeatures: {,
  recommendationAlgorithm: true, // 推荐算法
    crmSystem: true, // CRM系统集成
    blockchainTraceability: true, // 区块链溯源
    apiGateway: true, // API网关
    paymentProcessing: true, // 支付处理
  },
  apiEndpoint: 'http://localhost:50054',
  port: 50054,
  enabled: true,
  maxConcurrentTasks: 15,
  responseTimeout: 25000,
  retryAttempts: 3,
};
// 老克智能体配置 - 探索频道版主 & 知识传播智能体
export const LAOKE_CONFIG: AgentConfig = {,
  id: 'laoke-001',
  name: '老克',
  type: AgentType.LAOKE,
  description:
    '索克生活APP探索频道版主，负责知识传播、知识培训和用户博客管理等工作，兼任索克游戏NPC。',
  channel: '探索频道',
  role: '知识传播智能体',
  capabilities: [
    'knowledge_retrieval', // 中医知识库RAG检索
    'personalized_learning', // 个性化学习路径
    'content_management', // 社区内容管理
    'knowledge_contribution', // 知识贡献奖励
    'health_education', // 健康教育课程
    'certification_system', // 认证系统
    'game_npc_roleplay', // 玉米迷宫NPC角色扮演
    'game_guidance', // 游戏引导
    'blog_management', // 用户博客管理
    'content_quality_assurance', // 内容质量保障
  ],
  technicalFeatures: {,
  knowledgeGraph: true, // 知识图谱
    ragSystem: true, // RAG系统
    learningTracking: true, // 学习进度追踪
    arvrInteraction: true, // AR/VR互动系统
    contentAudit: true, // 内容审核
    gamificationEngine: true, // 游戏化引擎
  },
  apiEndpoint: 'http://localhost:50055',
  port: 50055,
  enabled: true,
  maxConcurrentTasks: 12,
  responseTimeout: 20000,
  retryAttempts: 3,
};
// 索儿智能体配置 - LIFE频道版主 & 生活健康管理智能体
export const SOER_CONFIG: AgentConfig = {,
  id: 'soer-001',
  name: '索儿',
  type: AgentType.SOER,
  description:
    '索克生活APP LIFE频道版主，为用户提供生活（健康）管理、陪伴等服务，整合用户饮食起居、实时感知（通过手机、智能手表、运动装备、医疗装备等）等工作。',
  channel: 'LIFE频道',
  role: '生活健康管理智能体',
  capabilities: [
    'habit_cultivation', // 健康生活习惯培养
    'behavior_intervention', // 行为干预
    'diet_management', // 饮食管理
    'exercise_management', // 运动管理
    'sleep_management', // 睡眠管理
    'sensor_data_integration', // 多设备传感器数据整合
    'health_trend_analysis', // 健康趋势分析
    'environment_sensing', // 环境智能感知
    'emotion_sensing', // 情绪智能感知
    'dynamic_health_advice', // 动态健康建议
    'personalized_wellness_plan', // 个性化养生计划
    'execution_tracking', // 执行跟踪
    'health_companionship', // 身心健康陪伴
    'emotional_support', // 情感支持
    'stress_management', // 压力管理
    'emotional_counseling', // 情绪疏导
  ],
  technicalFeatures: {,
  dataFusion: true, // 多源异构数据融合
    edgeComputing: true, // 边缘计算
    privacyProtection: true, // 隐私保护
    reinforcementLearning: true, // 强化学习
    emotionalComputing: true, // 情感计算
    iotIntegration: true, // 物联网设备集成
  },
  apiEndpoint: 'http://localhost:50056',
  port: 50056,
  enabled: true,
  maxConcurrentTasks: 20,
  responseTimeout: 15000,
  retryAttempts: 3,
};
// 智能体配置映射
export const AGENT_CONFIGS: Record<AgentType, AgentConfig> = {
  [AgentType.XIAOAI]: XIAOAI_CONFIG,
  [AgentType.XIAOKE]: XIAOKE_CONFIG,
  [AgentType.LAOKE]: LAOKE_CONFIG,
  [AgentType.SOER]: SOER_CONFIG,
};
// 智能体协作配置
export interface CollaborationConfig {
  primaryAgent: AgentType;,
  supportingAgents: AgentType[];
  scenario: string;,
  description: string;
}
export const COLLABORATION_SCENARIOS: CollaborationConfig[] = [
  {
    primaryAgent: AgentType.XIAOAI,
    supportingAgents: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],
    scenario: 'comprehensive_health_assessment',
    description: '小艾主导的综合健康评估，整合四诊数据，其他智能体提供专业支持',
  },
  {
    primaryAgent: AgentType.XIAOKE,
    supportingAgents: [AgentType.XIAOAI, AgentType.SOER],
    scenario: 'personalized_service_recommendation',
    description: '小克主导的个性化服务推荐，基于小艾的健康评估和索儿的生活数据',
  },
  {
    primaryAgent: AgentType.LAOKE,
    supportingAgents: [AgentType.XIAOAI, AgentType.XIAOKE],
    scenario: 'health_education_and_training',
    description: '老克主导的健康教育培训，结合小艾的专业知识和小克的服务资源',
  },
  {
    primaryAgent: AgentType.SOER,
    supportingAgents: [AgentType.XIAOAI, AgentType.XIAOKE, AgentType.LAOKE],
    scenario: 'lifestyle_management_and_companionship',
    description: '索儿主导的生活管理和陪伴，整合其他智能体的专业能力',
  },
];
// 默认配置
export const DEFAULT_AGENT_CONFIG = {
  enableHealthMonitoring: true,
  enableLoadBalancing: true,
  enableFailover: true,
  maxRetries: 3,
  timeoutMs: 30000,
  healthCheckIntervalMs: 60000,
  logLevel: 'info' as const,
};
