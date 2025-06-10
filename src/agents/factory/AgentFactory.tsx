react";
// 索克生活智能体工厂   基于README.md第1013-1063行的智能体描述实现统一的智能体创建和管理
AgentType,
  XiaoaiAgent,
  XiaokeAgent,
  LaokeAgent,
  SoerAgent,
  Agent,
  AgentStatus,
  { AgentHealthStatus } from ../types/agents"/      AGENT_CONFIGS,"
  AgentConfig,
  { DEFAULT_AGENT_CONFIG  } from "../config/agents.config;/    export interface AgentFactoryConfig {
  ";
  enableHealthMonitoring?: boolean;
  enableLoadBalancing?: boolean;
  enableFailover?: boolean;
  maxRetries?: number;
  timeoutMs?: number;
  healthCheckIntervalMs?: number;
logLevel?: ";debug" | info" | "warn | "error"
}
export interface AgentInstance {
  id: string;
  agent: Agent;
  config: AgentConfig;
  status: AgentStatus;
  healthStatus: AgentHealthStatus;
  createdAt: Date;
  lastActivity: Date;
  metrics: {totalRequests: number;
  successfulRequests: number;
  failedRequests: number,averageResponseTime: number,uptime: number;
};
}
export class AgentFactory   {private static instance: AgentFactory;
  private agents: Map<AgentType, AgentInstance /> = new Map();/      private config: AgentFactoryConfig;
  private healthCheckInterval?: NodeJS.Timeout;
  private constructor(config: AgentFactoryConfig = {;}) {
    this.config = { ...DEFAULT_AGENT_CONFIG, ...config };
    this.initializeHealthMonitoring();
  }
  public static getInstance(config?: AgentFactoryConfig);: AgentFactory  {
    if (!AgentFactory.instance) {
      AgentFactory.instance = new AgentFactory(config);
    }
    return AgentFactory.instance;
  }
  ///    > {
    const config = AGENT_CONFIGS[AgentType.XIAOA;I;];
    const xiaoaiAgent: XiaoaiAgent = {id: config.id;
      name: config.name;
      type: AgentType.XIAOAI;
      status: AgentStatus.IDLE;
      capabilities: config.capabilities;
      description: config.description;
      technicalFeatures: {,
  multimodalLLM: true,           localModel: true,              / 轻量级本地模型*  视觉识别组件*  四诊合参模块集成* *;} * /
    }
    await this.registerAgent(xiaoaiAgent, confi;g;);
    return xiaoaiAge;n;t;
  }
  ///    > {
    const config = AGENT_CONFIGS[AgentType.XIAOK;E;];
    const xiaokeAgent: XiaokeAgent = {id: config.id;
      name: config.name;
      type: AgentType.XIAOKE;
      status: AgentStatus.IDLE;
      capabilities: config.capabilities;
      description: config.description;
      technicalFeatures: {,
  recommendationAlgorithm: true,  rcmSystem: true,               / RCM系统集成*  区块链溯源*  API网关* *;} * /
    }
    await this.registerAgent(xiaokeAgent, confi;g;);
    return xiaokeAge;n;t;
  }
  ///    > {
    const config = AGENT_CONFIGS[AgentType.LAOK;E;];
    const laokeAgent: LaokeAgent = {id: config.id;
      name: config.name;
      type: AgentType.LAOKE;
      status: AgentStatus.IDLE;
      capabilities: config.capabilities;
      description: config.description;
      technicalFeatures: {,
  knowledgeGraph: true,          ragSystem: true,               / RAG系统*  学习进度追踪*  AR* * VR互动系统 *  内容审核 * // ;}
    }
    await this.registerAgent(laokeAgent, confi;g;);
    return laokeAge;n;t;
  }
  ///    > {
    const config = AGENT_CONFIGS[AgentType.SOE;R;];
    const soerAgent: SoerAgent = {id: config.id;
      name: config.name;
      type: AgentType.SOER;
      status: AgentStatus.IDLE;
      capabilities: config.capabilities;
      description: config.description;
      technicalFeatures: {,
  dataFusion: true,              edgeComputing: true,           / 边缘计算*  隐私保护*  强化学习*  情感计算* *;} * /
    }
    await this.registerAgent(soerAgent, confi;g;);
    return soerAge;n;t;
  }
  // 创建所有智能体  public async createAllAgents(): Promise<{ xiaoai: XiaoaiAgent;
    xiaoke: XiaokeAgent;
    laoke: LaokeAgent;
    soer: SoerAgent;}> {
    const [xiaoai, xiaoke, laoke, soer] = await Promise.all([;)
      this.createXiaoaiAgent(),
      this.createXiaokeAgent(),
      this.createLaokeAgent(),
      this.createSoerAgent];);
    return { xiaoai, xiaoke, laoke, soe;r ;};
  }
  // 根据类型获取智能体  public getAgent(type: AgentType): AgentInstance | undefined  {
    return this.agents.get(typ;e;);
  }
  ///        return new Map(this.agent;s;);
  }
  // 获取智能体状态  public getAgentStatus(type: AgentType): AgentStatus | undefined  {
    const instance = this.agents.get(typ;e;);
    return instance?.stat;u;s;
  }
  // 获取智能体健康状态  public getAgentHealthStatus(type: AgentType): AgentHealthStatus | undefined  {
    const instance = this.agents.get(typ;e;);
    return instance?.healthStat;u;s;
  }
  // 更新智能体状态  public updateAgentStatus(type: AgentType, status: AgentStatus): void  {
    const instance = this.agents.get(typ;e;);
    if (instance) {
      instance.status = status;
      instance.lastActivity = new Date();
    }
  }
  // 注册智能体实例  private async registerAgent(agent: Agent, config: AgentConfig): Promise<void>  {
    const instance: AgentInstance = {id: agent.id;
      agent,
      config,
      status: AgentStatus.IDLE;
      healthStatus: healthy", "
      createdAt: new Date();
      lastActivity: new Date();
      metrics: {,
  totalRequests: 0;
        successfulRequests: 0;
        failedRequests: 0;
        averageResponseTime: 0;
        uptime: 0;}
    }
    this.agents.set(agent.type, instance);
    await this.initializeAgent(instance;);
  }
  // 初始化智能体  private async initializeAgent(instance: AgentInstance): Promise<void>  {
    try {
      instance.status = AgentStatus.ACTIVE;
      instance.healthStatus = "healthy"

    } catch (error) {
      instance.status = AgentStatus.ERROR;
      instance.healthStatus = "unhealthy"
      throw error;
    }
  }
  // 初始化健康监控  private initializeHealthMonitoring(): void {
    if (!this.config.enableHealthMonitoring) {
      return;
    }
    this.healthCheckInterval = setInterval() => {
  // 性能监控
const performanceMonitor = usePerformanceMonitor(AgentFactory", {")
    trackRender: true;
    trackMemory: false,warnThreshold: 100, // ms ;};);
      this.performHealthCheck();
    }, this.config.healthCheckIntervalMs);
  }
  // 执行健康检查  private async performHealthCheck(): Promise<void> {
    for (const [type, instance] of this.agents) {
      try {
        const startTime = Date.now;
        / 例如：ping智能体服务、检查资源使用情况等* ///
        const responseTime = Date.now - startTime;
        if (responseTime < 1000) {
          instance.healthStatus = "healthy"
        } else if (responseTime < 3000) {
          instance.healthStatus = "degraded"
        } else {
          instance.healthStatus = unhealthy""
        }
        instance.metrics.uptime = Date.now() - instance.createdAt.getTime();
      } catch (error) {
        instance.healthStatus = "unhealthy;"
        instance.status = AgentStatus.ERROR;
}
    }
  }
  // 获取智能体性能指标  public getAgentMetrics(type: AgentType): AgentInstance["metrics"] | undefined  {
    const instance = this.agents.get(type;);
    return instance?.metri;c;s;
  }
  ///
    for (const [type, instance] of this.agents) {
      report[type] = instance.metrics;
    }
    return report as Record<AgentType, AgentInstance["metrics'] ;///      }"'
  // 销毁工厂实例  public destroy(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    this.agents.clear();
    AgentFactory.instance = null as any;
  }
}
//   ;