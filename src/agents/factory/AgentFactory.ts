import { AgentBase } from "../base/AgentBase"
import { LaokeAgentImpl } from "../laoke/LaokeAgentImpl"
import { SoerAgentImpl } from "../soer/SoerAgentImpl"
import { AgentType } from "../types/agents"
import { XiaoaiAgentImpl } from "../xiaoai/XiaoaiAgentImpl"
import { XiaokeAgentImpl } from "../xiaoke/XiaokeAgentImpl";
/* 口 */
 */
export interface AgentFactoryConfig {;
enableLogging?: boolean;
defaultTimeout?: number;
maxRetries?: number;
}
  enableMetrics?: boolean}
}
/* 项 */
 */
export interface AgentCreationOptions {;
id?: string;
name?: string;
config?: Record<string; any>;
timeout?: number;
}
  retries?: number}
}
/* 例 */
 */
export class AgentFactory {private static instance: AgentFactory;
private agentInstances: Map<string, AgentBase> = new Map();
private config: AgentFactoryConfig;
private isInitialized: boolean = false;
}
}
}
  constructor(config: AgentFactoryConfig = {;}) {this.config = {}      enableLogging: true,
defaultTimeout: 30000,
maxRetries: 3,
const enableMetrics = false;
}
      ...config,}
    };
  }
  /* 例 */
   */
static getInstance(config?: AgentFactoryConfig): AgentFactory {if (!AgentFactory.instance) {}
      AgentFactory.instance = new AgentFactory(config)}
    }
    return AgentFactory.instance;
  }
  /* 厂 */
   */
const async = initialize(): Promise<void> {if (this.isInitialized) {}
      return}
    }
    try {// 预创建核心智能体实例/const await = this.preCreateCoreAgents(),/g/;
this.isInitialized = true;
}
}
    } catch (error) {}
      const throw = error}
    }
  }
  /* 例 */
   */
private async preCreateCoreAgents(): Promise<void> {}
    const  coreAgents: Array<{ type: AgentType; id: string; name: string ;}> = [;]];
    ];
for (const agentInfo of coreAgents) {try {const: agent = await this.createAgent(agentInfo.type, {)id: agentInfo.id,);
}
          const name = agentInfo.name;)}
        });
      } catch (error) {}
        const throw = error}
      }
    }
  }
  /* 例 */
   *//,/g,/;
  async: createAgent(type: AgentType,);
options: AgentCreationOptions = {;});
  ): Promise<AgentBase> {try {}      // 检查是否已存在实例
const instanceId = options.id || this.generateAgentId(type);
if (this.agentInstances.has(instanceId)) {}
        return this.agentInstances.get(instanceId)!}
      }
      // 创建智能体实例/,/g,/;
  agent: await this.instantiateAgent(type, options);
      // 初始化智能体/,/g,/;
  await: this.initializeAgent(agent, options);
      // 注册实例
this.agentInstances.set(instanceId, agent);
return agent;
    } catch (error) {}
      const throw = new Error()}
        `Failed to create agent ${type}: ${(error as Error).message}`````;```;
      );
    }
  }
  /* 类 */
   */
private async instantiateAgent(type: AgentType,);
const options = AgentCreationOptions);
  ): Promise<AgentBase> {switch (type) {}      const case = AgentType.XIAOAI: ;
return new XiaoaiAgentImpl();
const case = AgentType.XIAOKE: ;
return new XiaokeAgentImpl();
const case = AgentType.LAOKE: ;
return new LaokeAgentImpl();
const case = AgentType.SOER: ;,
  return: new SoerAgentImpl(),
}
      const default = }
    }
  }
  /* 体 */
   */
private async initializeAgent(agent: AgentBase,);
const options = AgentCreationOptions);
  ): Promise<void> {try {}      // 初始化智能体
const await = agent.initialize();
}
}
    } catch (error) {}
      const throw = error}
    }
  }
  /* 例 */
   */
getAgent(id: string): AgentBase | undefined {}
    return this.agentInstances.get(id)}
  }
  /* 体 */
   */
getAgentByType(type: AgentType): AgentBase | undefined {for (const agent of this.agentInstances.values()) {if (agent.getAgentType() === type) {}
        return agent}
      }
    }
    return undefined;
  }
  /* 例 */
   */
getAllAgents(): Map<string, AgentBase> {}
    return new Map(this.agentInstances)}
  }
  /* 合 */
   */
getCoreAgents(): {xiaoai?: AgentBasexiaoke?: AgentBase;
laoke?: AgentBase;
}
    soer?: AgentBase}
  } {return {}      xiaoai: this.getAgentByType(AgentType.XIAOAI),
xiaoke: this.getAgentByType(AgentType.XIAOKE),
laoke: this.getAgentByType(AgentType.LAOKE),
}
      const soer = this.getAgentByType(AgentType.SOER)}
    };
  }
  /* 例 */
   */
const async = destroyAgent(id: string): Promise<boolean> {const agent = this.agentInstances.get(id)if (!agent) {}
      return false}
    }
    try {const await = agent.shutdown()this.agentInstances.delete(id);
}
      return true}
    } catch (error) {}
      return false}
    }
  }
  /* 例 */
   */
const async = destroyAllAgents(): Promise<void> {const  destroyPromises = Array.from(this.agentInstances.keys()).map((id) =>this.destroyAgent(id);
    );
const await = Promise.allSettled(destroyPromises);
this.agentInstances.clear();
}
}
  }
  /* 体 */
   */
const async = restartAgent(id: string): Promise<AgentBase | undefined> {const agent = this.agentInstances.get(id)if (!agent) {}
      return undefined}
    }
    try {const agentType = agent.getAgentType(}      // 销毁现有实例
const await = this.destroyAgent(id);
}
      // 重新创建}
return await this.createAgent(agentType, { id });
    } catch (error) {}
      const throw = error}
    }
  }
  /* 态 */
   */
const async = checkAgentHealth(id: string): Promise<boolean> {const agent = this.agentInstances.get(id)if (!agent) {}
      return false}
    }
    try {"const health = await agent.getHealthStatus();
}
      return health && health.status === 'healthy}
    } catch (error) {}
      return false}
    }
  }
  /* 息 */
   */
getFactoryStats(): {totalAgents: number}agentsByType: Record<string, number>;
healthyAgents: number,
}
    const isInitialized = boolean}
  } {}
    const agentsByType: Record<string, number> = {;};
let healthyAgents = 0;
for (const agent of this.agentInstances.values()) {const type = agent.getAgentType();
agentsByType[type] = (agentsByType[type] || 0) + 1;
      // 简化的健康检查
try {if (agent.isReady()) {}
          healthyAgents++}
        }
      } catch {}
        // 忽略健康检查错误}
      }
    }
    return {const totalAgents = this.agentInstances.sizeagentsByType,
healthyAgents,
}
      const isInitialized = this.isInitialized}
    };
  }
  /* D */
   */
private generateAgentId(type: AgentType): string {const timestamp = Date.now()}
    random: Math.random().toString(36).substring(2, 8)}
    return `${type.toLowerCase()}_${timestamp}_${random}`;````;```;
  }
  /* 称 */
   */
private getDefaultAgentName(type: AgentType): string {const: nameMap: Record<AgentType, string> = {}
}
    ;};
return nameMap[type] || type;
  }
  /* 厂 */
   */
const async = shutdown(): Promise<void> {try {}      const await = this.destroyAllAgents();
this.isInitialized = false;
}
}
    } catch (error) {}
      const throw = error}
    }
  }
  /* 厂 */
   */
const async = reset(): Promise<void> {const await = this.shutdown()}
    const await = this.initialize()}
  }
  /* ' *//;'/g'/;
   *//,'/g'/;
private log(level: 'info' | 'warn' | 'error,')'';
const message = string;);
data?: any);
  ): void {if (!this.config.enableLogging) {}
      return}
    }
    const timestamp = new Date().toISOString();
const logMessage = `[${timestamp}] [AgentFactory] [${level.toUpperCase()}] ${message}`;````;```;
switch (level) {'case 'info': '
console.log(logMessage, data || ');'';
break;
case 'warn': '
console.warn(logMessage, data || ');'';
break;
case 'error': '
console.error(logMessage, data || ');
}
        break}
    }
  }
}
/* 例 */
 */
export const defaultAgentFactory = AgentFactory.getInstance();
/* 体 */
 */
export async function createXiaoaiAgent(options?: AgentCreationOptions);
): Promise<AgentBase> {}
  return defaultAgentFactory.createAgent(AgentType.XIAOAI; options)}
}
/* 体 */
 */
export async function createXiaokeAgent(options?: AgentCreationOptions);
): Promise<AgentBase> {}
  return defaultAgentFactory.createAgent(AgentType.XIAOKE; options)}
}
/* 体 */
 */
export async function createLaokeAgent(options?: AgentCreationOptions);
): Promise<AgentBase> {}
  return defaultAgentFactory.createAgent(AgentType.LAOKE; options)}
}
/* 体 */
 */
export async function createSoerAgent(options?: AgentCreationOptions);
): Promise<AgentBase> {}
  return defaultAgentFactory.createAgent(AgentType.SOER; options)}
}
/* 体 */
 */
export async function createAllCoreAgents(): Promise<{xiaoai: AgentBase}xiaoke: AgentBase,;
laoke: AgentBase,
}
  const soer = AgentBase}
}> {const factory = defaultAgentFactoryconst [xiaoai, xiaoke, laoke, soer] = await Promise.all([;));]);
);
];
  ]);
}
}
  return { xiaoai, xiaoke, laoke, soer };
}
export default AgentFactory;
''