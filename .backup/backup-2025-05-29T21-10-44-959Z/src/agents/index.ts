import type { 
import type { 
import type { XiaoaiAgent } from './xiaoai/types';
import type { XiaokeAgent } from './xiaoke/types';
import type { LaokeAgent } from './laoke/types';
import type { SoerAgent } from './soer/types';



/**
 * 智能体系统统一入口
 * 基于README.md描述的四智能体协作架构
 */

// 智能体类型定义
export type { XiaoaiAgent, UserProfile as XiaoaiUserProfile, ChatContext, VoiceResponse, FourDiagnosisResults } from './xiaoai/types';
export type { XiaokeAgent, UserProfile as XiaokeUserProfile, DoctorMatchingResult, ServiceRecommendation } from './xiaoke/types';
export type { LaokeAgent, UserProfile as LaokeUserProfile, KnowledgeSearchResult, PersonalizedLearningPath } from './laoke/types';
export type { SoerAgent, UserProfile as SoerUserProfile, LifestyleHabit, PersonalizedWellnessPlan } from './soer/types';

// 智能体协调器
export { 
  AgentCoordinator, 
  agentCoordinator,
  type AgentType, 
  type AgentTask, 
  type AgentCoordinationResult,
  type AgentHealthStatus,
  type SharedContext,
  type AgentInstance,
} from './AgentCoordinator';

// 智能体管理器
export { 
  AgentManager,
  type AgentManagerConfig,
  type AgentStatus,
  type AgentMetrics,
} from './AgentManager';

// 智能体实现
export { XiaoaiAgentImpl } from './xiaoai/XiaoaiAgentImpl';

// 导入类型以供内部使用
  AgentType, 
  AgentTask, 
  AgentCoordinationResult,
  agentCoordinator as coordinator,
} from './AgentCoordinator';
  AgentManagerConfig, 
  AgentStatus, 
  AgentMetrics, 
} from './AgentManager';

// 创建智能体实例的工厂函数
export const createAgent = async (agentType: AgentType): Promise<any> => {
  switch (agentType) {
    case 'xiaoai':
      const { XiaoaiAgentImpl } = await import('./xiaoai/XiaoaiAgentImpl');
      return new XiaoaiAgentImpl();
    case 'xiaoke':
    case 'laoke':
    case 'soer':
      // 其他智能体实现待完成
      throw new Error(`智能体 ${agentType} 的实现尚未完成`);
    default:
      throw new Error(`未知的智能体类型: ${agentType}`);
  }
};

// 初始化智能体系统
export const initializeAgentSystem = async (config?: Partial<AgentManagerConfig>) => {
  const { AgentManager } = await import('./AgentManager');
  const manager = new AgentManager(config);
  await manager.initialize();
  return manager;
};

// 执行智能体任务
export const executeAgentTask = async (task: AgentTask): Promise<AgentCoordinationResult> => {
  const { agentCoordinator } = await import('./AgentCoordinator');
  return agentCoordinator.coordinateTask(task);
};

// 获取智能体状态
export const getAgentStatus = async (agentType?: AgentType): Promise<Map<AgentType, AgentStatus>> => {
  const { AgentManager } = await import('./AgentManager');
  const manager = new AgentManager();
  return manager.getAgentStatus(agentType);
};

// 获取智能体指标
export const getAgentMetrics = (agentType?: AgentType): Map<AgentType, AgentMetrics> => {
  // 这里需要从管理器实例获取指标
  return new Map();
};

// 清理智能体系统
export const cleanupAgentSystem = async (): Promise<void> => {
  const { agentCoordinator } = await import('./AgentCoordinator');
  await agentCoordinator.cleanup();
};

// 智能体能力常量
export const AGENT_CAPABILITIES = {
  xiaoai: [
    'chat',
    'voice_interaction',
    'four_diagnosis',
    'health_analysis',
    'accessibility_services',
    'constitution_assessment',
    'medical_records',
    'multilingual_support',
    'tcm_diagnosis',
    'intelligent_inquiry',
    'algorithmic_diagnosis',
  ],
  xiaoke: [
    'service_recommendation',
    'doctor_matching',
    'product_management',
    'supply_chain',
    'appointment_booking',
    'subscription_management',
    'agricultural_traceability',
    'third_party_integration',
    'shop_management',
    'payment_processing',
    'logistics_management',
  ],
  laoke: [
    'knowledge_management',
    'education',
    'content_curation',
    'game_npc',
    'blog_management',
    'learning_paths',
    'tcm_knowledge_rag',
    'community_management',
    'certification_system',
    'content_quality_assurance',
    'maze_game_guidance',
  ],
  soer: [
    'lifestyle_management',
    'data_integration',
    'emotional_support',
    'habit_tracking',
    'environmental_sensing',
    'wellness_planning',
    'behavior_intervention',
    'multi_device_integration',
    'stress_management',
    'companionship',
    'crisis_support',
  ],
} as const;

// 智能体角色描述
export const AGENT_ROLES = {
  xiaoai: {
    name: '小艾',
    title: '健康助手 & 首页聊天频道版主',
    description: '专注于健康管理、中医四诊合参、智能问诊和无障碍服务',
    primaryChannel: 'chat',
    specialties: ['中医诊断', '健康分析', '语音交互', '无障碍服务'],
  },
  xiaoke: {
    name: '小克',
    title: 'SUOKE频道版主',
    description: '负责服务订阅、农产品预制、供应链管理等商业化服务',
    primaryChannel: 'suoke',
    specialties: ['名医匹配', '服务推荐', '供应链管理', '第三方集成'],
  },
  laoke: {
    name: '老克',
    title: '探索频道版主',
    description: '负责知识传播、培训和博物馆导览，兼任玉米迷宫NPC',
    primaryChannel: 'explore',
    specialties: ['知识管理', '教育培训', '内容策展', '游戏引导'],
  },
  soer: {
    name: '索儿',
    title: 'LIFE频道版主',
    description: '提供生活健康管理、陪伴服务和数据整合分析',
    primaryChannel: 'life',
    specialties: ['生活方式管理', '情感支持', '数据整合', '健康陪伴'],
  },
} as const;

// 智能体频道映射
export const AGENT_CHANNELS = {
  chat: 'xiaoai',
  suoke: 'xiaoke',
  explore: 'laoke',
  life: 'soer',
} as const;

// 协作模式常量
export const COLLABORATION_MODES = {
  SEQUENTIAL: 'sequential',      // 顺序协作
  PARALLEL: 'parallel',          // 并行协作
  HIERARCHICAL: 'hierarchical',  // 层次协作
  CONSENSUS: 'consensus',         // 共识协作
} as const;

// 任务类型常量
export const TASK_TYPES = {
  DIAGNOSIS: 'diagnosis',
  RECOMMENDATION: 'recommendation',
  EDUCATION: 'education',
  LIFESTYLE: 'lifestyle',
  EMERGENCY: 'emergency',
  COORDINATION: 'coordination',
} as const;

// 任务优先级常量
export const TASK_PRIORITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

// 智能体状态常量
export const AGENT_STATUSES = {
  INITIALIZING: 'initializing',
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  ERROR: 'error',
  MAINTENANCE: 'maintenance',
} as const;

// 健康状态常量
export const HEALTH_STATUSES = {
  HEALTHY: 'healthy',
  DEGRADED: 'degraded',
  UNHEALTHY: 'unhealthy',
  OFFLINE: 'offline',
} as const;

// 智能体协作策略
export const COLLABORATION_STRATEGIES = {
  // 诊断协作：小艾主导，其他智能体提供支持信息
  diagnosis: {
    primary: 'xiaoai',
    supporting: ['xiaoke', 'laoke', 'soer'],
    mode: COLLABORATION_MODES.HIERARCHICAL,
  },
  // 服务推荐：小克主导，小艾提供健康分析，索儿提供生活方式建议
  service_recommendation: {
    primary: 'xiaoke',
    supporting: ['xiaoai', 'soer'],
    mode: COLLABORATION_MODES.PARALLEL,
  },
  // 学习路径：老克主导，小艾提供健康知识，索儿提供生活习惯建议
  learning_path: {
    primary: 'laoke',
    supporting: ['xiaoai', 'soer'],
    mode: COLLABORATION_MODES.SEQUENTIAL,
  },
  // 生活方式管理：索儿主导，其他智能体提供专业建议
  lifestyle_management: {
    primary: 'soer',
    supporting: ['xiaoai', 'xiaoke', 'laoke'],
    mode: COLLABORATION_MODES.CONSENSUS,
  },
} as const;

// 系统元数据
export const AGENT_SYSTEM_METADATA = {
  version: '1.0.0',
  buildDate: new Date().toISOString(),
  description: '索克生活四智能体协作系统',
  architecture: 'distributed_autonomous_collaboration',
  supportedLanguages: ['zh-CN', 'zh-TW', 'en-US'],
  supportedDialects: ['普通话', '粤语', '闽南语', '上海话'],
  tcmIntegration: true,
  modernMedicineIntegration: true,
  blockchainSupport: true,
  multimodalSupport: true,
  accessibilityCompliant: true,
  privacyCompliant: true,
} as const;

// 默认配置
export const DEFAULT_AGENT_CONFIG = {
  enableLoadBalancing: true,
  enableFailover: true,
  enableHealthMonitoring: true,
  maxRetries: 3,
  timeoutMs: 30000,
  healthCheckIntervalMs: 60000,
  logLevel: 'info' as const,
} as const;

// 智能体能力检查函数
export const hasCapability = (agentType: AgentType, capability: string): boolean => {
  return (AGENT_CAPABILITIES[agentType] as readonly string[]).includes(capability);
};

// 获取智能体角色信息
export const getAgentRole = (agentType: AgentType) => {
  return AGENT_ROLES[agentType];
};

// 根据频道获取智能体
export const getAgentByChannel = (channel: keyof typeof AGENT_CHANNELS): AgentType => {
  return AGENT_CHANNELS[channel];
};

// 获取协作策略
export const getCollaborationStrategy = (taskType: string) => {
  return COLLABORATION_STRATEGIES[taskType as keyof typeof COLLABORATION_STRATEGIES];
};

// 验证智能体类型
export const isValidAgentType = (agentType: string): agentType is AgentType => {
  return ['xiaoai', 'xiaoke', 'laoke', 'soer'].includes(agentType);
};

// 验证任务类型
export const isValidTaskType = (taskType: string): boolean => {
  return Object.values(TASK_TYPES).includes(taskType as any);
};

// 验证任务优先级
export const isValidTaskPriority = (priority: string): boolean => {
  return Object.values(TASK_PRIORITIES).includes(priority as any);
};

// 创建任务ID
export const createTaskId = (prefix: string = 'task'): string => {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// 创建会话ID
export const createSessionId = (userId: string): string => {
  return `session-${userId}-${Date.now()}`;
};

// 格式化智能体状态
export const formatAgentStatus = (status: AgentStatus): string => {
  const uptime = Math.floor(status.uptime / 1000);
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  
  return `${status.agentType}: ${status.status} (${hours}h ${minutes}m, 负载: ${(status.currentLoad * 100).toFixed(1)}%)`;
};

// 计算系统健康度
export const calculateSystemHealth = (agentStatuses: Map<AgentType, AgentStatus>): number => {
  const statuses = Array.from(agentStatuses.values());
  const healthyCount = statuses.filter(s => s.status === 'active').length;
  return (healthyCount / statuses.length) * 100;
};

// 导出类型守卫
export const isXiaoaiAgent = (agent: any): agent is XiaoaiAgent => {
  return agent && typeof agent.chat === 'function' && typeof agent.performTCMDiagnosis === 'function';
};

export const isXiaokeAgent = (agent: any): agent is XiaokeAgent => {
  return agent && typeof agent.matchDoctors === 'function' && typeof agent.recommendServices === 'function';
};

export const isLaokeAgent = (agent: any): agent is LaokeAgent => {
  return agent && typeof agent.searchTCMKnowledge === 'function' && typeof agent.generatePersonalizedLearningPath === 'function';
};

export const isSoerAgent = (agent: any): agent is SoerAgent => {
  return agent && typeof agent.analyzeCurrentHabits === 'function' && typeof agent.provideEmotionalSupport === 'function';
}; 