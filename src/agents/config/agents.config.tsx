import { AgentType } from "../types/agents";
// 索克生活四智能体系统配置
// 基于README.md第1013-1063行的智能体描述
export interface AgentConfig {id: string}name: string,;
type: AgentType,
description: string,
channel: string,
role: string,
capabilities: string[],
technicalFeatures: Record<string, boolean>;
apiEndpoint: string,
port: number,
enabled: boolean,
maxConcurrentTasks: number,
responseTimeout: number,
}
}
  const retryAttempts = number}
}
// 小艾智能体配置 - 首页聊天频道版主 & 四诊协调智能体"
export const XIAOAI_CONFIG: AgentConfig = {,'id: 'xiaoai-001,'';
type: AgentType.XIAOAI,
const description =
const capabilities = [;]'
    'voice_interaction', // 实时语音交互与多语种支持'/;'/g'/;
    'dialect_recognition', // 方言识别'/;'/g'/;
    'face_analysis', // 中医望诊面色分析'/;'/g'/;
    'tongue_diagnosis', // 舌诊图像处理'/;'/g'/;
    'intelligent_inquiry', // 智能问诊系统'/;'/g'/;
    'constitution_screening', // 体质筛查'/;'/g'/;
    'symptom_assessment', // 症状评估'/;'/g'/;
    'health_consultation', // 健康咨询'/;'/g'/;
    'calculation_diagnosis', // 算诊'/;'/g'/;
    'medical_record_management', // 医疗记录自动整理'/;'/g'/;
    'health_archive_management', // 健康档案管理'/;'/g'/;
    'accessibility_services', // 无障碍服务'/;'/g'/;
    'guide_services', // 导盲、导医服务'/;'/g'/;
    'sign_language_recognition', // 手语识别'/;'/g'/;
    'elderly_friendly_interface', // 老年友好界面'/;'/g'/;
];
  ],
technicalFeatures: {multimodalLLM: true, // 多模态大语言模型 (GPT-4o / Gemini 1.5 Pro)/,/g,/;
  localModel: true, // 轻量级本地模型 (Llama 3-8B)/,/g,/;
  visionRecognition: true, // 视觉识别组件/,/g,/;
  fourDiagnosisIntegration: true, // 四诊合参模块集成
}
    healthArchiveIntegration: true, // 健康档案系统集成}'/;'/g'/;
  ;},'
apiEndpoint: 'http://localhost:50053,''/,'/g,'/;
  port: 50053,
enabled: true,
maxConcurrentTasks: 10,
responseTimeout: 30000,
const retryAttempts = 3;
};
// 小克智能体配置 - SUOKE频道版主 & 服务管理智能体'/,'/g'/;
export const XIAOKE_CONFIG: AgentConfig = {,'id: 'xiaoke-001,'';
type: AgentType.XIAOKE,
const description =
const capabilities = [;]'
    'doctor_matching', // 名医资源智能匹配'/;'/g'/;
    'appointment_management', // 预约管理'/;'/g'/;
    'service_subscription', // 医疗服务订阅'/;'/g'/;
    'personalized_recommendation', // 个性化推荐'/;'/g'/;
    'product_traceability', // 农产品溯源'/;'/g'/;
    'custom_delivery', // 定制配送管理'/;'/g'/;
    'third_party_api_integration', // 第三方API集成'/;'/g'/;
    'insurance_integration', // 保险集成'/;'/g'/;
    'payment_integration', // 支付集成'/;'/g'/;
    'logistics_integration', // 物流集成'/;'/g'/;
    'store_management', // 在线店铺管理'/;'/g'/;
    'health_product_recommendation', // 健康商品推荐'/;'/g'/;
];
  ],
technicalFeatures: {recommendationAlgorithm: true, // 推荐算法/,/g,/;
  crmSystem: true, // CRM系统集成/,/g,/;
  blockchainTraceability: true, // 区块链溯源/,/g,/;
  apiGateway: true, // API网关
}
    paymentProcessing: true, // 支付处理}'/;'/g'/;
  ;},'
apiEndpoint: 'http://localhost:50054,''/,'/g,'/;
  port: 50054,
enabled: true,
maxConcurrentTasks: 15,
responseTimeout: 25000,
const retryAttempts = 3;
};
// 老克智能体配置 - 探索频道版主 & 知识传播智能体'/,'/g'/;
export const LAOKE_CONFIG: AgentConfig = {,'id: 'laoke-001,'';
type: AgentType.LAOKE,
const description =
const capabilities = [;]'
    'knowledge_retrieval', // 中医知识库RAG检索'/;'/g'/;
    'personalized_learning', // 个性化学习路径'/;'/g'/;
    'content_management', // 社区内容管理'/;'/g'/;
    'knowledge_contribution', // 知识贡献奖励'/;'/g'/;
    'health_education', // 健康教育课程'/;'/g'/;
    'certification_system', // 认证系统'/;'/g'/;
    'game_npc_roleplay', // 玉米迷宫NPC角色扮演'/;'/g'/;
    'game_guidance', // 游戏引导'/;'/g'/;
    'blog_management', // 用户博客管理'/;'/g'/;
    'content_quality_assurance', // 内容质量保障'/;'/g'/;
];
  ],
technicalFeatures: {knowledgeGraph: true, // 知识图谱/,/g,/;
  ragSystem: true, // RAG系统/,/g,/;
  learningTracking: true, // 学习进度追踪/,/g,/;
  arvrInteraction: true, // AR/VR互动系统/,/g,/;
  contentAudit: true, // 内容审核
}
    gamificationEngine: true, // 游戏化引擎}'/;'/g'/;
  ;},'
apiEndpoint: 'http://localhost:50055,''/,'/g,'/;
  port: 50055,
enabled: true,
maxConcurrentTasks: 12,
responseTimeout: 20000,
const retryAttempts = 3;
};
// 索儿智能体配置 - LIFE频道版主 & 生活健康管理智能体'/,'/g'/;
export const SOER_CONFIG: AgentConfig = {,'id: 'soer-001,'';
type: AgentType.SOER,
const description =
const capabilities = [;]'
    'habit_cultivation', // 健康生活习惯培养'/;'/g'/;
    'behavior_intervention', // 行为干预'/;'/g'/;
    'diet_management', // 饮食管理'/;'/g'/;
    'exercise_management', // 运动管理'/;'/g'/;
    'sleep_management', // 睡眠管理'/;'/g'/;
    'sensor_data_integration', // 多设备传感器数据整合'/;'/g'/;
    'health_trend_analysis', // 健康趋势分析'/;'/g'/;
    'environment_sensing', // 环境智能感知'/;'/g'/;
    'emotion_sensing', // 情绪智能感知'/;'/g'/;
    'dynamic_health_advice', // 动态健康建议'/;'/g'/;
    'personalized_wellness_plan', // 个性化养生计划'/;'/g'/;
    'execution_tracking', // 执行跟踪'/;'/g'/;
    'health_companionship', // 身心健康陪伴'/;'/g'/;
    'emotional_support', // 情感支持'/;'/g'/;
    'stress_management', // 压力管理'/;'/g'/;
    'emotional_counseling', // 情绪疏导'/;'/g'/;
];
  ],
technicalFeatures: {dataFusion: true, // 多源异构数据融合/,/g,/;
  edgeComputing: true, // 边缘计算/,/g,/;
  privacyProtection: true, // 隐私保护/,/g,/;
  reinforcementLearning: true, // 强化学习/,/g,/;
  emotionalComputing: true, // 情感计算
}
    iotIntegration: true, // 物联网设备集成}'/;'/g'/;
  ;},'
apiEndpoint: 'http://localhost:50056,''/,'/g,'/;
  port: 50056,
enabled: true,
maxConcurrentTasks: 20,
responseTimeout: 15000,
const retryAttempts = 3;
};
// 智能体配置映射
export const AGENT_CONFIGS: Record<AgentType, AgentConfig> = {[AgentType.XIAOAI]: XIAOAI_CONFIG,}  [AgentType.XIAOKE]: XIAOKE_CONFIG,;
  [AgentType.LAOKE]: LAOKE_CONFIG,
}
  [AgentType.SOER]: SOER_CONFIG,};
;};
// 智能体协作配置
export interface CollaborationConfig {primaryAgent: AgentType}supportingAgents: AgentType[],;
scenario: string,
}
}
  const description = string}
}
export const COLLABORATION_SCENARIOS: CollaborationConfig[] = [;]{primaryAgent: AgentType.XIAOAI,';}],'';
supportingAgents: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],'
const scenario = 'comprehensive_health_assessment';
}
}
  }
  {primaryAgent: AgentType.XIAOKE,'supportingAgents: [AgentType.XIAOAI, AgentType.SOER],'
const scenario = 'personalized_service_recommendation';
}
}
  }
  {primaryAgent: AgentType.LAOKE,'supportingAgents: [AgentType.XIAOAI, AgentType.SOER],'
const scenario = 'knowledge_based_health_education';
}
}
  }
  {primaryAgent: AgentType.SOER,'supportingAgents: [AgentType.XIAOAI, AgentType.XIAOKE],'
const scenario = 'lifestyle_health_management';
}
}
  }
];
// 默认智能体配置
export const DEFAULT_AGENT_CONFIG = {timeout: 30000}retries: 3,;
maxConcurrentTasks: 10,
healthCheckInterval: 60000,
}
  const logLevel = 'info' as const;'}
};
''