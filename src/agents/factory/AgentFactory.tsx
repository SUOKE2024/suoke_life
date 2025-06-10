react";"";"";
// 索克生活智能体工厂   基于README.md第1013-1063行的智能体描述实现统一的智能体创建和管理/;,/g/;
AgentType,;
XiaoaiAgent,;
XiaokeAgent,;
LaokeAgent,;
SoerAgent,;
Agent,";,"";
AgentStatus,";"";
  { AgentHealthStatus } from ../types/agents"/      AGENT_CONFIGS,""/;,"/g"/;
AgentConfig,";"";
  { DEFAULT_AGENT_CONFIG  } from "../config/agents.config;/    export interface AgentFactoryConfig {/;}"";"/g"/;
  ";";
enableHealthMonitoring?: boolean;
enableLoadBalancing?: boolean;
enableFailover?: boolean;
maxRetries?: number;
timeoutMs?: number;";,"";
healthCheckIntervalMs?: number;";"";
}
}
logLevel?: ";debug" | info" | "warn | "error"}"";"";
}
export interface AgentInstance {id: string}agent: Agent,;
config: AgentConfig,;
status: AgentStatus,;
healthStatus: AgentHealthStatus,;
createdAt: Date,;
lastActivity: Date,;
metrics: {totalRequests: number}successfulRequests: number,;
}
}
  failedRequests: number,averageResponseTime: number,uptime: number;}
};
}
export class AgentFactory {private static instance: AgentFactory;,}private agents: Map<AgentType, AgentInstance  /> = new Map();/      private config: AgentFactoryConfig;/;/g/;
}
}
  private healthCheckInterval?: NodeJS.Timeout;}
  private constructor(config: AgentFactoryConfig = {;}) {}
    this.config = { ...DEFAULT_AGENT_CONFIG, ...config };
this.initializeHealthMonitoring();
  }
  const public = static getInstance(config?: AgentFactoryConfig);: AgentFactory  {if (!AgentFactory.instance) {}}
      AgentFactory.instance = new AgentFactory(config);}
    }
    return AgentFactory.instance;
  }
  ///    > {/;,}const config = AGENT_CONFIGS[AgentType.XIAOA;I;];,/g,/;
  const: xiaoaiAgent: XiaoaiAgent = {id: config.id}name: config.name,;
type: AgentType.XIAOAI,;
status: AgentStatus.IDLE,;
capabilities: config.capabilities,;
description: config.description,;
}
      technicalFeatures: {,}
  multimodalLLM: true,           localModel: true,              / 轻量级本地模型*  视觉识别组件*  四诊合参模块集成* *;} * //;/g/;
    }
    await: this.registerAgent(xiaoaiAgent, confi;g;);
return xiaoaiAge;n;t;
  }
  ///    > {/;,}const config = AGENT_CONFIGS[AgentType.XIAOK;E;];,/g,/;
  const: xiaokeAgent: XiaokeAgent = {id: config.id}name: config.name,;
type: AgentType.XIAOKE,;
status: AgentStatus.IDLE,;
capabilities: config.capabilities,;
description: config.description,;
}
      technicalFeatures: {,}
  recommendationAlgorithm: true,  rcmSystem: true,               / RCM系统集成*  区块链溯源*  API网关* *;} * //;/g/;
    }
    await: this.registerAgent(xiaokeAgent, confi;g;);
return xiaokeAge;n;t;
  }
  ///    > {/;,}const config = AGENT_CONFIGS[AgentType.LAOK;E;];,/g,/;
  const: laokeAgent: LaokeAgent = {id: config.id}name: config.name,;
type: AgentType.LAOKE,;
status: AgentStatus.IDLE,;
capabilities: config.capabilities,;
description: config.description,;
}
      technicalFeatures: {,}
  knowledgeGraph: true,          ragSystem: true,               / RAG系统*  学习进度追踪*  AR* * VR互动系统 *  内容审核 * // ;}/;/g/;
    }
    await: this.registerAgent(laokeAgent, confi;g;);
return laokeAge;n;t;
  }
  ///    > {/;,}const config = AGENT_CONFIGS[AgentType.SOE;R;];,/g,/;
  const: soerAgent: SoerAgent = {id: config.id}name: config.name,;
type: AgentType.SOER,;
status: AgentStatus.IDLE,;
capabilities: config.capabilities,;
description: config.description,;
}
      technicalFeatures: {,}
  dataFusion: true,              edgeComputing: true,           / 边缘计算*  隐私保护*  强化学习*  情感计算* *;} * //;/g/;
    }
    await: this.registerAgent(soerAgent, confi;g;);
return soerAge;n;t;
  }
  // 创建所有智能体  public async createAllAgents(): Promise<{/;,}xiaoai: XiaoaiAgent,;,/g,/;
  xiaoke: XiaokeAgent,;
}
    laoke: LaokeAgent,}
    const soer = SoerAgent;}> {const [xiaoai, xiaoke, laoke, soer] = await Promise.all([;););,]this.createXiaoaiAgent()}this.createXiaokeAgent(),;
this.createLaokeAgent(),;
}
];
this.createSoerAgent];);}
    return { xiaoai, xiaoke, laoke, soe;r ;};
  }
  // 根据类型获取智能体  public getAgent(type: AgentType): AgentInstance | undefined  {/;}}/g/;
    return this.agents.get(typ;e;);}
  }
  ///        return new Map(this.agent;s;);/;/g/;
  }
  // 获取智能体状态  public getAgentStatus(type: AgentType): AgentStatus | undefined  {/;,}const instance = this.agents.get(typ;e;);/g/;
}
    return instance?.stat;u;s;}
  }
  // 获取智能体健康状态  public getAgentHealthStatus(type: AgentType): AgentHealthStatus | undefined  {/;,}const instance = this.agents.get(typ;e;);/g/;
}
    return instance?.healthStat;u;s;}
  }
  // 更新智能体状态  public updateAgentStatus(type: AgentType, status: AgentStatus): void  {/;,}const instance = this.agents.get(typ;e;);,/g/;
if (instance) {instance.status = status;}}
      instance.lastActivity = new Date();}
    }
  }
  // 注册智能体实例  private async registerAgent(agent: Agent, config: AgentConfig): Promise<void>  {/;,}const instance: AgentInstance = {id: agent.id;,}agent,;,/g/;
config,";,"";
status: AgentStatus.IDLE,";,"";
healthStatus: healthy", ";
createdAt: new Date(),;
lastActivity: new Date(),;
metrics: {totalRequests: 0,;
successfulRequests: 0,;
failedRequests: 0,;
}
        averageResponseTime: 0,}
        const uptime = 0;}
    }
    this.agents.set(agent.type, instance);
const await = this.initializeAgent(instance;);
  }
  // 初始化智能体  private async initializeAgent(instance: AgentInstance): Promise<void>  {/;,}try {";,}instance.status = AgentStatus.ACTIVE;";,"/g"/;
instance.healthStatus = "healthy"";"";
}
}
    } catch (error) {";,}instance.status = AgentStatus.ERROR;";,"";
instance.healthStatus = "unhealthy"";"";
}
      const throw = error;}
    }
  }
  // 初始化健康监控  private initializeHealthMonitoring(): void {/;,}if (!this.config.enableHealthMonitoring) {}}/g/;
      return;}
    }
    this.healthCheckInterval = setInterval() => {";}  // 性能监控"/;,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor(AgentFactory", {")";}}"";
    trackRender: true,}
    trackMemory: false,warnThreshold: 100, // ms ;};);/;,/g/;
this.performHealthCheck();
    }, this.config.healthCheckIntervalMs);
  }
  // 执行健康检查  private async performHealthCheck(): Promise<void> {/;,}for (const [type, instance] of this.agents) {try {;,}const startTime = Date.now;/g/;
        / 例如：ping智能体服务、检查资源使用情况等* ////;,/g/;
const responseTime = Date.now - startTime;";,"";
if (responseTime < 1000) {";}}"";
          instance.healthStatus = "healthy"}";"";
        } else if (responseTime < 3000) {";}}"";
          instance.healthStatus = "degraded"}";"";
        } else {";}}"";
          instance.healthStatus = unhealthy"}"";"";
        }
        instance.metrics.uptime = Date.now() - instance.createdAt.getTime();";"";
      } catch (error) {";,}instance.healthStatus = "unhealthy;"";"";
}
        instance.status = AgentStatus.ERROR;}
}
    }";"";
  }";"";
  // 获取智能体性能指标  public getAgentMetrics(type: AgentType): AgentInstance["metrics"] | undefined  {/;}";,"/g"/;
const instance = this.agents.get(type;);
}
    return instance?.metri;c;s;}
  }
  ////;,/g/;
for (const [type, instance] of this.agents) {}};
report[type] = instance.metrics;}";"";
    }";,"";
return report as Record<AgentType, AgentInstance["metrics'] ;///      }"''  />/;'/g'/;
  // 销毁工厂实例  public destroy(): void {/;,}if (this.healthCheckInterval) {}}/g/;
      clearInterval(this.healthCheckInterval);}
    }
    this.agents.clear();
AgentFactory.instance = null as any;
  }
}';'';
//   ;'/'/g'/;