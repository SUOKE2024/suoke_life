/**
 * 索克生活智能体工厂
 * 基于README.md第1013-1063行的智能体描述实现统一的智能体创建和管理
 */

import { 
  AgentType, 
  XiaoaiAgent, 
  XiaokeAgent, 
  LaokeAgent, 
  SoerAgent,
  Agent,
  AgentStatus,
  AgentHealthStatus
} from '../types/agents';
import { 
  AGENT_CONFIGS, 
  AgentConfig, 
  DEFAULT_AGENT_CONFIG 
} from '../config/agents.config';

export interface AgentFactoryConfig {
  enableHealthMonitoring?: boolean;
  enableLoadBalancing?: boolean;
  enableFailover?: boolean;
  maxRetries?: number;
  timeoutMs?: number;
  healthCheckIntervalMs?: number;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

export interface AgentInstance {
  id: string;
  agent: Agent;
  config: AgentConfig;
  status: AgentStatus;
  healthStatus: AgentHealthStatus;
  createdAt: Date;
  lastActivity: Date;
  metrics: {
    totalRequests: number;
    successfulRequests: number;
    failedRequests: number;
    averageResponseTime: number;
    uptime: number;
  };
}

export class AgentFactory {
  private static instance: AgentFactory;
  private agents: Map<AgentType, AgentInstance> = new Map();
  private config: AgentFactoryConfig;
  private healthCheckInterval?: NodeJS.Timeout;

  private constructor(config: AgentFactoryConfig = {}) {
    this.config = { ...DEFAULT_AGENT_CONFIG, ...config };
    this.initializeHealthMonitoring();
  }

  public static getInstance(config?: AgentFactoryConfig): AgentFactory {
    if (!AgentFactory.instance) {
      AgentFactory.instance = new AgentFactory(config);
    }
    return AgentFactory.instance;
  }

  /**
   * 创建小艾智能体 - 首页聊天频道版主 & 四诊协调智能体
   */
  public async createXiaoaiAgent(): Promise<XiaoaiAgent> {
    const config = AGENT_CONFIGS[AgentType.XIAOAI];
    
    const xiaoaiAgent: XiaoaiAgent = {
      id: config.id,
      name: config.name,
      type: AgentType.XIAOAI,
      status: AgentStatus.IDLE,
      capabilities: config.capabilities,
      description: config.description,
      
      // 技术实现特性
      technicalFeatures: {
        multimodalLLM: true,          // 多模态大语言模型
        localModel: true,             // 轻量级本地模型
        visionRecognition: true,      // 视觉识别组件
        fourDiagnosisIntegration: true // 四诊合参模块集成
      }
    };

    await this.registerAgent(xiaoaiAgent, config);
    return xiaoaiAgent;
  }

  /**
   * 创建小克智能体 - SUOKE频道版主 & 服务管理智能体
   */
  public async createXiaokeAgent(): Promise<XiaokeAgent> {
    const config = AGENT_CONFIGS[AgentType.XIAOKE];
    
    const xiaokeAgent: XiaokeAgent = {
      id: config.id,
      name: config.name,
      type: AgentType.XIAOKE,
      status: AgentStatus.IDLE,
      capabilities: config.capabilities,
      description: config.description,
      
      // 技术实现特性
      technicalFeatures: {
        recommendationAlgorithm: true, // 推荐算法
        rcmSystem: true,              // RCM系统集成
        blockchainTraceability: true, // 区块链溯源
        apiGateway: true              // API网关
      }
    };

    await this.registerAgent(xiaokeAgent, config);
    return xiaokeAgent;
  }

  /**
   * 创建老克智能体 - 探索频道版主 & 知识传播智能体
   */
  public async createLaokeAgent(): Promise<LaokeAgent> {
    const config = AGENT_CONFIGS[AgentType.LAOKE];
    
    const laokeAgent: LaokeAgent = {
      id: config.id,
      name: config.name,
      type: AgentType.LAOKE,
      status: AgentStatus.IDLE,
      capabilities: config.capabilities,
      description: config.description,
      
      // 技术实现特性
      technicalFeatures: {
        knowledgeGraph: true,         // 知识图谱
        ragSystem: true,              // RAG系统
        learningTracking: true,       // 学习进度追踪
        arvrInteraction: true,        // AR/VR互动系统
        contentAudit: true            // 内容审核
      }
    };

    await this.registerAgent(laokeAgent, config);
    return laokeAgent;
  }

  /**
   * 创建索儿智能体 - LIFE频道版主 & 生活健康管理智能体
   */
  public async createSoerAgent(): Promise<SoerAgent> {
    const config = AGENT_CONFIGS[AgentType.SOER];
    
    const soerAgent: SoerAgent = {
      id: config.id,
      name: config.name,
      type: AgentType.SOER,
      status: AgentStatus.IDLE,
      capabilities: config.capabilities,
      description: config.description,
      
      // 技术实现特性
      technicalFeatures: {
        dataFusion: true,             // 多源异构数据融合
        edgeComputing: true,          // 边缘计算
        privacyProtection: true,      // 隐私保护
        reinforcementLearning: true,  // 强化学习
        emotionalComputing: true      // 情感计算
      }
    };

    await this.registerAgent(soerAgent, config);
    return soerAgent;
  }

  /**
   * 创建所有智能体
   */
  public async createAllAgents(): Promise<{
    xiaoai: XiaoaiAgent;
    xiaoke: XiaokeAgent;
    laoke: LaokeAgent;
    soer: SoerAgent;
  }> {
    const [xiaoai, xiaoke, laoke, soer] = await Promise.all([
      this.createXiaoaiAgent(),
      this.createXiaokeAgent(),
      this.createLaokeAgent(),
      this.createSoerAgent()
    ]);

    return { xiaoai, xiaoke, laoke, soer };
  }

  /**
   * 根据类型获取智能体
   */
  public getAgent(type: AgentType): AgentInstance | undefined {
    return this.agents.get(type);
  }

  /**
   * 获取所有智能体
   */
  public getAllAgents(): Map<AgentType, AgentInstance> {
    return new Map(this.agents);
  }

  /**
   * 获取智能体状态
   */
  public getAgentStatus(type: AgentType): AgentStatus | undefined {
    const instance = this.agents.get(type);
    return instance?.status;
  }

  /**
   * 获取智能体健康状态
   */
  public getAgentHealthStatus(type: AgentType): AgentHealthStatus | undefined {
    const instance = this.agents.get(type);
    return instance?.healthStatus;
  }

  /**
   * 更新智能体状态
   */
  public updateAgentStatus(type: AgentType, status: AgentStatus): void {
    const instance = this.agents.get(type);
    if (instance) {
      instance.status = status;
      instance.lastActivity = new Date();
    }
  }

  /**
   * 注册智能体实例
   */
  private async registerAgent(agent: Agent, config: AgentConfig): Promise<void> {
    const instance: AgentInstance = {
      id: agent.id,
      agent,
      config,
      status: AgentStatus.IDLE,
      healthStatus: 'healthy',
      createdAt: new Date(),
      lastActivity: new Date(),
      metrics: {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        averageResponseTime: 0,
        uptime: 0
      }
    };

    this.agents.set(agent.type, instance);
    
    // 初始化智能体
    await this.initializeAgent(instance);
  }

  /**
   * 初始化智能体
   */
  private async initializeAgent(instance: AgentInstance): Promise<void> {
    try {
      // 执行智能体初始化逻辑
      instance.status = AgentStatus.ACTIVE;
      instance.healthStatus = 'healthy';
      
      console.log(`智能体 ${instance.agent.name} (${instance.agent.type}) 初始化成功`);
    } catch (error) {
      instance.status = AgentStatus.ERROR;
      instance.healthStatus = 'unhealthy';
      
      console.error(`智能体 ${instance.agent.name} 初始化失败:`, error);
      throw error;
    }
  }

  /**
   * 初始化健康监控
   */
  private initializeHealthMonitoring(): void {
    if (!this.config.enableHealthMonitoring) {
      return;
    }

    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck();
    }, this.config.healthCheckIntervalMs);
  }

  /**
   * 执行健康检查
   */
  private async performHealthCheck(): Promise<void> {
    for (const [type, instance] of this.agents) {
      try {
        // 检查智能体响应性
        const startTime = Date.now();
        
        // 这里可以添加具体的健康检查逻辑
        // 例如：ping智能体服务、检查资源使用情况等
        
        const responseTime = Date.now() - startTime;
        
        // 更新健康状态
        if (responseTime < 1000) {
          instance.healthStatus = 'healthy';
        } else if (responseTime < 3000) {
          instance.healthStatus = 'degraded';
        } else {
          instance.healthStatus = 'unhealthy';
        }

        // 更新指标
        instance.metrics.uptime = Date.now() - instance.createdAt.getTime();
        
      } catch (error) {
        instance.healthStatus = 'unhealthy';
        instance.status = AgentStatus.ERROR;
        
        console.error(`智能体 ${instance.agent.name} 健康检查失败:`, error);
      }
    }
  }

  /**
   * 获取智能体性能指标
   */
  public getAgentMetrics(type: AgentType): AgentInstance['metrics'] | undefined {
    const instance = this.agents.get(type);
    return instance?.metrics;
  }

  /**
   * 获取所有智能体的性能报告
   */
  public getPerformanceReport(): Record<AgentType, AgentInstance['metrics']> {
    const report: Partial<Record<AgentType, AgentInstance['metrics']>> = {};
    
    for (const [type, instance] of this.agents) {
      report[type] = instance.metrics;
    }
    
    return report as Record<AgentType, AgentInstance['metrics']>;
  }

  /**
   * 销毁工厂实例
   */
  public destroy(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    
    this.agents.clear();
    AgentFactory.instance = null as any;
  }
}

// 导出单例实例
export const agentFactory = AgentFactory.getInstance(); 