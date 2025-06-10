import { AgentManager, AgentManagerConfig } from "./AgentManager";""/;,"/g"/;
import { AgentContext, AgentResponse, AgentType } from "./types";""/;"/g"/;
// 智能体系统统一入口/;/g/;
// 基于README.md描述的四智能体协作架构"/;"/g"/;
// 导出核心类型'/;,'/g'/;
export * from "./types";""/;"/g"/;
// 导出智能体实现'/;,'/g'/;
export { LaokeAgentImpl } from "./laoke/LaokeAgentImpl";""/;,"/g"/;
export { SoerAgentImpl } from "./soer/SoerAgentImpl";""/;,"/g"/;
export { XiaoaiAgentImpl } from "./xiaoai/XiaoaiAgentImpl";""/;,"/g"/;
export { XiaokeAgentImpl } from "./xiaoke/XiaokeAgentImpl";""/;"/g"/;
// 导出基础类'/;,'/g'/;
export { AgentBase } from "./base/AgentBase";""/;,"/g"/;
export { BaseAgent } from "./base/BaseAgent";""/;"/g"/;
// 导出协调器和管理器'/;,'/g'/;
export { AgentCoordinator, agentCoordinator } from "./AgentCoordinator";""/;,"/g"/;
export {AgentManager}type: AgentManagerConfig,;
type: AgentMetrics,';'';
}
  type: AgentStatus,'}'';'';
} from "./AgentManager";""/;"/g"/;
// 导入类型/;/g/;
/* 数 *//;/g/;
 *//;,/g/;
export const createAgent = async (agentType: AgentType): Promise<any> => {switch (agentType) {';}}'';
    const case = AgentType.XIAOAI:'}'';
const { XiaoaiAgentImpl ;} = await import('./xiaoai/XiaoaiAgentImpl');'/;,'/g'/;
return new XiaoaiAgentImpl();';,'';
const case = AgentType.XIAOKE: ';,'';
const { XiaokeAgentImpl ;} = await import('./xiaoke/XiaokeAgentImpl');'/;,'/g'/;
return new XiaokeAgentImpl();';,'';
const case = AgentType.LAOKE: ';,'';
const { LaokeAgentImpl ;} = await import('./laoke/LaokeAgentImpl');'/;,'/g'/;
return new LaokeAgentImpl();';,'';
const case = AgentType.SOER: ';,'';
const { SoerAgentImpl ;} = await import('./soer/SoerAgentImpl');'/;,'/g'/;
return new SoerAgentImpl();
const default = ;}
};
/* 统 *//;/g/;
 *//;,/g/;
export const initializeAgentSystem = async (config?: Partial<AgentManagerConfig>);
): Promise<AgentManager> => {;,}const manager = new AgentManager(config);
const await = manager.initialize();
}
  return manager;}
};
/* 务 *//;/g/;
 *//;,/g/;
export executeAgentTask: async (message: string,);
const context = AgentContext)';'';
): Promise<AgentResponse> => {'}'';
const { agentCoordinator ;} = await import('./AgentCoordinator');'/;,'/g'/;
return agentCoordinator.processCollaborativeTask(message, context);
};
/* 态 *//;/g/;
 *//;,/g/;
export const getAgentStatus = async (agentType?: AgentType): Promise<any> => {;,}const manager = new AgentManager();
const await = manager.initialize();
}
  return manager.getAgentStatus(agentType);}
};
/* 标 *//;/g/;
 *//;,/g/;
export const getAgentMetrics = async (agentType?: AgentType): Promise<any> => {;,}const manager = new AgentManager();
const await = manager.initialize();
}
  return manager.getMetrics(agentType);}
};
/* 统 *//;/g/;
 */'/;,'/g'/;
export const cleanupAgentSystem = async (): Promise<void> => {'}'';
const { agentCoordinator } = await import('./AgentCoordinator');'/;,'/g'/;
const await = agentCoordinator.shutdown();
};
/* 量 *//;/g/;
 *//;,/g/;
export const AGENT_CAPABILITIES = {';}  [AgentType.XIAOAI]: [;]';'';
    'ai_inference',';'';
    'voice_interaction',';'';
    'multimodal_analysis',';'';
    'medical_consultation',';'';
    'tongue_diagnosis',';'';
    'face_analysis',';'';
    'accessibility_service',';'';
    'sign_language',';'';
    'voice_guidance',';'';
    'health_record_management',';'';
];
  ],';'';
  [AgentType.XIAOKE]: [;]';'';
    'service_recommendation',';'';
    'doctor_matching',';'';
    'product_management',';'';
    'supply_chain',';'';
    'appointment_booking',';'';
    'subscription_management',';'';
    'agricultural_traceability',';'';
    'third_party_integration',';'';
    'shop_management',';'';
    'payment_processing',';'';
    'logistics_management',';'';
];
  ],';'';
  [AgentType.LAOKE]: [;]';'';
    'knowledge_retrieval',';'';
    'learning_path',';'';
    'content_management',';'';
    'education_system',';'';
    'game_npc',';'';
    'blog_management',';'';
    'knowledge_graph',';'';
    'rag_system',';'';
    'ar_vr_interaction',';'';
    'content_moderation',';'';
];
  ],';'';
  [AgentType.SOER]: [;]';'';
    'lifestyle_management',';'';
    'health_monitoring',';'';
    'sensor_integration',';'';
    'behavior_intervention',';'';
    'emotional_support',';'';
    'environment_sensing',';'';
    'personalized_recommendations',';'';
    'habit_tracking',';'';
    'wellness_coaching',';'';
    'data_fusion',';'';
}
];
  ],};
} as const;
/* 述 *//;/g/;
 *//;,/g/;
export const AGENT_ROLES = {[AgentType.XIAOAI]: {}';'';
';,'';
const primaryChannel = 'chat';';'';
}
}
  }
  [AgentType.XIAOKE]: {';}';,'';
const primaryChannel = 'suoke';';'';
}
}
  }
  [AgentType.LAOKE]: {';}';,'';
const primaryChannel = 'explore';';'';
}
}
  }
  [AgentType.SOER]: {';}';,'';
const primaryChannel = 'life';';'';
}
}
  }
} as const;
/* 射 *//;/g/;
 *//;,/g/;
export const AGENT_CHANNELS = {chat: AgentType.XIAOAI}suoke: AgentType.XIAOKE,;
explore: AgentType.LAOKE,;
}
  const life = AgentType.SOER;}
} as const;
/* 量 *//;/g/;
 */'/;,'/g'/;
export const COLLABORATION_MODES = {';,}SEQUENTIAL: 'sequential', // 顺序协作'/;,'/g,'/;
  PARALLEL: 'parallel', // 并行协作'/;,'/g,'/;
  HIERARCHICAL: 'hierarchical', // 层次协作'/;'/g'/;
}
  CONSENSUS: 'consensus', // 共识协作'}'';/;'/g'/;
;} as const;
/* 量 *//;/g/;
 */'/;,'/g'/;
export const TASK_TYPES = {';,}DIAGNOSIS: 'diagnosis';','';
RECOMMENDATION: 'recommendation';','';
EDUCATION: 'education';','';
LIFESTYLE: 'lifestyle';','';
EMERGENCY: 'emergency';','';'';
}
  const COORDINATION = 'coordination';'}'';'';
} as const;
/* 量 *//;/g/;
 */'/;,'/g'/;
export const TASK_PRIORITIES = {';,}LOW: 'low';','';
MEDIUM: 'medium';','';
HIGH: 'high';','';'';
}
  const CRITICAL = 'critical';'}'';'';
} as const;
/* 量 *//;/g/;
 */'/;,'/g'/;
export const AGENT_STATUSES = {';,}INITIALIZING: 'initializing';','';
ACTIVE: 'active';','';
INACTIVE: 'inactive';','';
ERROR: 'error';','';'';
}
  const MAINTENANCE = 'maintenance';'}'';'';
} as const;
/* 量 *//;/g/;
 */'/;,'/g'/;
export const HEALTH_STATUSES = {';,}HEALTHY: 'healthy';','';
DEGRADED: 'degraded';','';
UNHEALTHY: 'unhealthy';','';'';
}
  const OFFLINE = 'offline';'}'';'';
} as const;
/* 略 *//;/g/;
 *//;,/g/;
export const COLLABORATION_STRATEGIES = {// 诊断协作：小艾主导，其他智能体提供支持信息/;,}diagnosis: {primary: AgentType.XIAOAI,;,/g,/;
  supporting: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],;
}
    const mode = COLLABORATION_MODES.SEQUENTIAL;}
  }
  // 服务推荐：小克主导，小艾和索儿提供支持/;,/g,/;
  service_recommendation: {primary: AgentType.XIAOKE,;
supporting: [AgentType.XIAOAI, AgentType.SOER],;
}
    const mode = COLLABORATION_MODES.SEQUENTIAL;}
  }
  // 知识学习：老克主导，小艾提供AI支持/;,/g,/;
  knowledge_learning: {primary: AgentType.LAOKE,;
supporting: [AgentType.XIAOAI],;
}
    const mode = COLLABORATION_MODES.SEQUENTIAL;}
  }
  // 生活方式管理：索儿主导，其他提供专业支持/;,/g,/;
  lifestyle_management: {primary: AgentType.SOER,;
supporting: [AgentType.XIAOAI, AgentType.LAOKE],;
}
    const mode = COLLABORATION_MODES.SEQUENTIAL;}
  }
  // 紧急情况：所有智能体并行协作/;,/g,/;
  emergency: {primary: AgentType.XIAOAI,;
supporting: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],;
}
    const mode = COLLABORATION_MODES.PARALLEL;}
  }
} as const;
/* 置 *//;/g/;
 */'/;,'/g'/;
export const AGENT_SYSTEM_CONFIG = {';,}version: '1.0.0';','';
maxConcurrentTasks: 10,;
healthCheckInterval: 30000,';,'';
autoRestart: true,';,'';
logLevel: 'info' as const;','';
performanceMonitoring: true,;
resourceLimits: {memory: 512, // MB,/;/g/;
}
    cpu: 80, // 百分比}/;/g/;
  ;}
} as const;
/* 数 *//;/g/;
 *//;,/g/;
export const AgentSystemUtils = {/* 型 *//;}   *//;,/g/;
getAgentByChannel(channel: string): AgentType | undefined {;}}
    return AGENT_CHANNELS[channel as keyof typeof AGENT_CHANNELS];}
  }
  /* 表 *//;/g/;
   *//;,/g/;
getAgentCapabilities(agentType: AgentType): readonly string[] {}}
    return AGENT_CAPABILITIES[agentType] || [];}
  }
  /* 息 *//;/g/;
   *//;,/g/;
getAgentRole(agentType: AgentType) {}}
    return AGENT_ROLES[agentType];}
  }
  /* 力 *//;/g/;
   *//;,/g/;
hasCapability(agentType: AgentType, capability: string): boolean {}}
    return AGENT_CAPABILITIES[agentType]?.includes(capability) || false;}
  }
  /* 略 *//;/g/;
   *//;,/g/;
getCollaborationStrategy(taskType: string) {const return = COLLABORATION_STRATEGIES[;,]const taskType = as keyof typeof COLLABORATION_STRATEGIES;}}
];
    ];}
  }
  /* 文 *//;/g/;
   *//;,/g/;
validateContext(context: AgentContext): boolean {}}
    return !!(context.userId && context.sessionId);}
  }
  /* 文 *//;/g/;
   *//;,/g/;
createDefaultContext(userId: string, channel?: string): AgentContext {return {}}
      userId;}';,'';
sessionId: `session_${Date.now();}`,``'`;,```;
channel: channel || 'chat';','';
timestamp: new Date(),;
metadata: {;}
    };
  }
};
// 默认导出智能体系统主要接口/;,/g/;
export default {createAgent}initializeAgentSystem,;
executeAgentTask,;
getAgentStatus,;
getAgentMetrics,;
cleanupAgentSystem,;
AGENT_CAPABILITIES,;
AGENT_ROLES,;
AGENT_CHANNELS,;
COLLABORATION_MODES,;
TASK_TYPES,;
TASK_PRIORITIES,;
AGENT_STATUSES,;
HEALTH_STATUSES,;
COLLABORATION_STRATEGIES,;
AGENT_SYSTEM_CONFIG,;
}
  AgentSystemUtils,};
};';'';
''';