import { AgentType, AgentContext, AgentResponse } from "./types";
import { AgentManager, AgentManagerConfig } from "./AgentManager";
// 智能体系统统一入口
// 基于README.md描述的四智能体协作架构
// 导出核心类型
export * from "./types";
// 导出智能体实现
export { XiaoaiAgentImpl } from "./xiaoai/XiaoaiAgentImpl";
export { XiaokeAgentImpl } from "./xiaoke/XiaokeAgentImpl";
export { LaokeAgentImpl } from "./laoke/LaokeAgentImpl";
export { SoerAgentImpl } from "./soer/SoerAgentImpl";
// 导出基础类
export { AgentBase } from "./base/AgentBase";
// 导出协调器和管理器
export { AgentCoordinator, agentCoordinator } from "./AgentCoordinator";
export {
  AgentManager,
  type AgentManagerConfig,
  type AgentStatus,
  type AgentMetrics;
} from "./AgentManager";
// 导入类型
/**
* 创建智能体实例的工厂函数
*/
export const createAgent = async (agentType: AgentType): Promise<any> => {switch (agentType) {case AgentType.XIAOAI:const { XiaoaiAgentImpl } = await import("./xiaoai/XiaoaiAgentImpl");
      return new XiaoaiAgentImpl();
    case AgentType.XIAOKE:
      const { XiaokeAgentImpl } = await import("./xiaoke/XiaokeAgentImpl");
      return new XiaokeAgentImpl();
    case AgentType.LAOKE:
      const { LaokeAgentImpl } = await import("./laoke/LaokeAgentImpl");
      return new LaokeAgentImpl();
    case AgentType.SOER:
      const { SoerAgentImpl } = await import("./soer/SoerAgentImpl");
      return new SoerAgentImpl();
    default:
      throw new Error(`未知的智能体类型: ${agentType}`);
  }
};
/**
* 初始化智能体系统
*/
export const initializeAgentSystem = async (;)
  config?: Partial<AgentManagerConfig>
): Promise<AgentManager> => {
  const manager = new AgentManager(config);
  await manager.initialize();
  return manager;
};
/**
* 执行智能体任务
*/
export const executeAgentTask = async (;)
  message: string,
  context: AgentContext;
): Promise<AgentResponse> => {
  const { agentCoordinator } = await import("./AgentCoordinator");
  return agentCoordinator.coordinateTask(message, context);
};
/**
* 获取智能体状态
*/
export const getAgentStatus = async (agentType?: AgentType): Promise<any> => {const manager = new AgentManager();
  await manager.initialize();
  return manager.getAgentStatus(agentType);
};
/**
* 获取智能体指标
*/
export const getAgentMetrics = async (agentType?: AgentType): Promise<any> => {const manager = new AgentManager();
  await manager.initialize();
  return manager.getMetrics(agentType);
};
/**
* 清理智能体系统
*/
export const cleanupAgentSystem = async (): Promise<void> => {const { agentCoordinator } = await import("./AgentCoordinator");
  await agentCoordinator.shutdown();
};
/**
* 智能体能力常量
*/
export const AGENT_CAPABILITIES = {
  [AgentType.XIAOAI]: [
    "ai_inference",voice_interaction",
    "multimodal_analysis",medical_consultation",
    "tongue_diagnosis",face_analysis",
    "accessibility_service",sign_language",
    "voice_guidance",health_record_management"
  ],
  [AgentType.XIAOKE]: [
    "service_recommendation",doctor_matching",
    "product_management",supply_chain",
    "appointment_booking",subscription_management",
    "agricultural_traceability",third_party_integration",
    "shop_management",payment_processing",
    "logistics_management"
  ],
  [AgentType.LAOKE]: [
    "knowledge_retrieval",learning_path",
    "content_management",education_system",
    "game_npc",blog_management",
    "knowledge_graph",rag_system","ar_vr_interaction",content_moderation";
  ],[AgentType.SOER]: [;
    "lifestyle_management",health_monitoring","sensor_integration",behavior_intervention","emotional_support",environment_sensing","personalized_recommendations",habit_tracking","wellness_coaching",data_fusion";
  ];
} as const;
/**
* 智能体角色描述
*/
export const AGENT_ROLES = {
  [AgentType.XIAOAI]: {
      name: "小艾",
      title: "AI推理专家 & 首页聊天频道版主",
    description: "专注于AI推理、语音交互、多模态分析、医疗咨询和无障碍服务",
    primaryChannel: "chat",
    specialties: ["AI推理", "语音交互", "中医诊断", "无障碍服务"]
  },
  [AgentType.XIAOKE]: {
      name: "小克",
      title: "SUOKE频道版主",
    description: "负责服务订阅、农产品预制、供应链管理等商业化服务",
    primaryChannel: "suoke",
    specialties: ["名医匹配", "服务推荐", "供应链管理", "第三方集成"];
  },[AgentType.LAOKE]: {
      name: "老克",
      title: "探索频道版主",description: "负责知识传播、培训和博物馆导览，兼任玉米迷宫NPC",primaryChannel: "explore",specialties: ["知识管理", "教育培训", "内容策展", "游戏引导"];
  },[AgentType.SOER]: {
      name: "索儿",
      title: "LIFE频道版主",description: "提供生活健康管理、陪伴服务和数据整合分析",primaryChannel: "life",specialties: ["生活方式管理", "情感支持", "数据整合", "健康陪伴"];
  };
} as const;
/**
* 智能体频道映射
*/
export const AGENT_CHANNELS = {chat: AgentType.XIAOAI,suoke: AgentType.XIAOKE,explore: AgentType.LAOKE,life: AgentType.SOER;
} as const;
/**
* 协作模式常量
*/
export const COLLABORATION_MODES = {SEQUENTIAL: "sequential", // 顺序协作;
  PARALLEL: "parallel", // 并行协作;
  HIERARCHICAL: "hierarchical", // 层次协作;
  CONSENSUS: "consensus", // 共识协作;
} as const;
/**
* 任务类型常量
*/
export const TASK_TYPES = {
      DIAGNOSIS: "diagnosis",
      RECOMMENDATION: "recommendation",EDUCATION: "education",LIFESTYLE: "lifestyle",EMERGENCY: "emergency",COORDINATION: "coordination";
} as const;
/**
* 任务优先级常量
*/
export const TASK_PRIORITIES = {
      LOW: "low",
      MEDIUM: "medium",HIGH: "high",CRITICAL: "critical";
} as const;
/**
* 智能体状态常量
*/
export const AGENT_STATUSES = {
      INITIALIZING: "initializing",
      ACTIVE: "active",INACTIVE: "inactive",ERROR: "error",MAINTENANCE: "maintenance";
} as const;
/**
* 健康状态常量
*/
export const HEALTH_STATUSES = {
      HEALTHY: "healthy",
      DEGRADED: "degraded",UNHEALTHY: "unhealthy",OFFLINE: "offline";
} as const;
/**
* 智能体协作策略
*/
export const COLLABORATION_STRATEGIES = {
  // 诊断协作：小艾主导，其他智能体提供支持信息
  diagnosis: {,
  primary: AgentType.XIAOAI,
    supporting: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],
    mode: COLLABORATION_MODES.SEQUENTIAL;
  },
  // 服务推荐：小克主导，小艾和索儿提供支持
  service_recommendation: {,
  primary: AgentType.XIAOKE,
    supporting: [AgentType.XIAOAI, AgentType.SOER],
    mode: COLLABORATION_MODES.SEQUENTIAL;
  },
  // 知识学习：老克主导，小艾提供AI支持
  knowledge_learning: {,
  primary: AgentType.LAOKE,supporting: [AgentType.XIAOAI],mode: COLLABORATION_MODES.SEQUENTIAL;
  },// 生活方式管理：索儿主导，其他提供专业支持;
  lifestyle_management: {primary: AgentType.SOER,supporting: [AgentType.XIAOAI, AgentType.LAOKE],mode: COLLABORATION_MODES.SEQUENTIAL;
  },// 紧急情况：所有智能体并行协作;
  emergency: {primary: AgentType.XIAOAI,supporting: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],mode: COLLABORATION_MODES.PARALLEL;
  };
} as const;
/**
* 智能体系统配置
*/
export const AGENT_SYSTEM_CONFIG = {
      version: "1.0.0",
      maxConcurrentTasks: 10,healthCheckInterval: 30000,autoRestart: true,logLevel: "info" as const,performanceMonitoring: true,resourceLimits: {memory: 512, // MB;
    cpu: 80, // 百分比;
  };
} as const;
/**
* 智能体系统工具函数
*/
export const AgentSystemUtils = {/**;
  * 根据频道获取对应的智能体类型;
  */;
  getAgentByChannel(channel: string): AgentType {return (;)
      AGENT_CHANNELS[channel as keyof typeof AGENT_CHANNELS] || AgentType.XIAOAI;
    );
  },
  /**
  * 获取智能体的能力列表
  */
  getAgentCapabilities(agentType: AgentType): readonly string[] {
    return AGENT_CAPABILITIES[agentType] || [];
  },
  /**
  * 获取智能体的角色信息
  */
  getAgentRole(agentType: AgentType) {
    return AGENT_ROLES[agentType];
  },
  /**
  * 检查智能体是否支持特定能力
  */
  hasCapability(agentType: AgentType, capability: string): boolean {
    return AGENT_CAPABILITIES[agentType]?.includes(capability) || false;
  },
  /**
  * 获取协作策略
  */
  getCollaborationStrategy(taskType: string) {
    return COLLABORATION_STRATEGIES[;
      taskType as keyof typeof COLLABORATION_STRATEGIES;
    ];
  },
  /**
  * 验证智能体上下文
  */
  validateContext(context: AgentContext): boolean {
    return !!(context && context.userId);
  },
  /**
  * 创建默认上下文
  */
  createDefaultContext(userId: string, channel?: string): AgentContext {
    return {userId,sessionId: `session_${Date.now()}`,currentChannel: channel || "chat",timestamp: new Date();
    };
  }
};
// 默认导出智能体系统主要接口
export default {
  createAgent,
  initializeAgentSystem,
  executeAgentTask,
  getAgentStatus,
  getAgentMetrics,
  cleanupAgentSystem,
  AgentSystemUtils,
  AGENT_CAPABILITIES,
  AGENT_ROLES,
  AGENT_CHANNELS,
  COLLABORATION_STRATEGIES,
  AGENT_SYSTEM_CONFIG;
};