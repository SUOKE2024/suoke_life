  performanceMonitor,
PerformanceCategory;
} from "../monitoring/PerformanceMonitor"/;"/g"/;
/* 配 */"
*/"
export enum AgentType {"XIAOAI = 'XIAOAI', // 小艾 - 健康助手 & 首页聊天频道版主";
XIAOKE = 'XIAOKE', // 小克 - 中医诊断专家"
LAOKE = 'LAOKE', // 老克 - 资深健康顾问"/;"/g"/;
}
}
  SOER = 'SOER', // 索儿 - 生活方式指导师"}
}","
export enum TaskType {"HEALTH_CONSULTATION = 'HEALTH_CONSULTATION',';
DIAGNOSIS = 'DIAGNOSIS','
LIFESTYLE_GUIDANCE = 'LIFESTYLE_GUIDANCE','
EMERGENCY_RESPONSE = 'EMERGENCY_RESPONSE','
DATA_ANALYSIS = 'DATA_ANALYSIS','
USER_INTERACTION = 'USER_INTERACTION',
}
}
  KNOWLEDGE_SHARING = "KNOWLEDGE_SHARING"};
}
export enum TaskPriority {LOW = 1}MEDIUM = 2,;
HIGH = 3,
URGENT = 4,
}
}
  EMERGENCY = 5}
}","
export enum TaskStatus {"PENDING = 'PENDING',';
ASSIGNED = 'ASSIGNED','
IN_PROGRESS = 'IN_PROGRESS','
COMPLETED = 'COMPLETED','
FAILED = 'FAILED',
}
}
  CANCELLED = "CANCELLED"};
}
export interface AgentCapability {type: TaskType}proficiency: number; // 0-1之间，表示熟练度,/,/g,/;
  maxConcurrentTasks: number,
averageProcessingTime: number; // 毫秒,
}
}
  const specializations = string[]}
}
export interface AgentStatus {id: string}type: AgentType,;
isOnline: boolean,
currentLoad: number; // 0-1之间，表示当前负载,/,/g,/;
  capabilities: AgentCapability[],
activeTasks: string[],
lastHeartbeat: number,
performance: {successRate: number,
averageResponseTime: number,
}
}
  const totalTasksCompleted = number}
};
}
export interface Task {id: string}type: TaskType,;
priority: TaskPriority,
const status = TaskStatus;
assignedAgent?: AgentType;
  requesterUserId: string,
data: unknown,
metadata: {const createdAt = number;
assignedAt?: number;
startedAt?: number;
completedAt?: number;
estimatedDuration?: number;
}
}
    actualDuration?: number}
};
dependencies?: string[]; // 依赖的其他任务ID;
collaborators?: AgentType[]; // 需要协作的其他智能体
result?: unknown;
error?: unknown;
}
export interface CoordinationRule {id: string}name: string,;
condition: (task: Task, agents: Map<AgentType, AgentStatus>) => boolean;
action: (task: Task, agents: Map<AgentType, AgentStatus>) => AgentType | null;
}
}
  const priority = number}
}
export interface CollaborationRequest {id: string}fromAgent: AgentType,";
toAgent: AgentType,","
taskId: string,","
requestType: "CONSULTATION" | "HANDOVER" | "ASSISTANCE" | "KNOWLEDGE_SHARE,
data: unknown,","
timestamp: number,";
}
}
  const status = "PENDING" | "ACCEPTED" | "REJECTED" | "COMPLETED};
}
export class AgentCoordinator {private static instance: AgentCoordinator;
private agents: Map<AgentType, AgentStatus> = new Map();
private tasks: Map<string, Task> = new Map();
private coordinationRules: CoordinationRule[] = [];
private collaborationRequests: Map<string, CollaborationRequest> = new Map();
private taskQueue: Task[] = [];
private isRunning: boolean = false;
private coordinationInterval: NodeJS.Timeout | null = null;
private constructor() {this.setupDefaultRules()}
}
    this.initializeAgents()}
  }
  const public = static getInstance(): AgentCoordinator {if (!AgentCoordinator.instance) {}
      AgentCoordinator.instance = new AgentCoordinator()}
    }
    return AgentCoordinator.instance;
  }
  // 启动协调系统
const public = start(): void {if (this.isRunning) {}
      return}
    }
    this.isRunning = true;
this.coordinationInterval = setInterval() => {this.processTaskQueue()this.monitorAgentHealth();
}
      this.optimizeTaskDistribution()}
    }, 1000);
  }
  // 停止协调系统
const public = stop(): void {if (!this.isRunning) {}
      return}
    }
    this.isRunning = false;
if (this.coordinationInterval) {clearInterval(this.coordinationInterval)}
      this.coordinationInterval = null}
    }
  }
  // 提交任务
const public = async submitTask();
type: TaskType,
priority: TaskPriority,
requesterUserId: string,
data: unknown,
const options = {estimatedDuration?: numberdependencies?: string[];
}
      collaborators?: AgentType[]}
    } = {}
  ): Promise<string> {const taskId = this.generateTaskId()const: task: Task = {const id = taskId;
type,
priority,
const status = TaskStatus.PENDING;
requesterUserId,
data,
metadata: {createdAt: Date.now(),
}
        const estimatedDuration = options.estimatedDuration}
      }
dependencies: options.dependencies,
const collaborators = options.collaborators;
    };
this.tasks.set(taskId, task);
this.taskQueue.push(task);
this.sortTaskQueue();
    // 立即尝试分配任务
const await = this.processTaskQueue();
return taskId;
  }
  // 获取任务状态
const public = getTaskStatus(taskId: string): Task | null {}
    return this.tasks.get(taskId) || null}
  }
  // 取消任务
const public = cancelTask(taskId: string): boolean {const task = this.tasks.get(taskId)if (!task) {}
      return false}
    }
    if (task.status === TaskStatus.IN_PROGRESS) {// 通知智能体停止任务/;}}/g/;
      this.notifyAgentTaskCancellation(task)}
    }
    task.status = TaskStatus.CANCELLED;
this.removeFromQueue(taskId);
return true;
  }
  // 注册智能体
const public = registerAgent(agentStatus: AgentStatus): void {}
    this.agents.set(agentStatus.type, agentStatus)}
  }
  // 更新智能体状态
const public = updateAgentStatus();
agentType: AgentType,
const updates = Partial<AgentStatus>;
  ): void {const agent = this.agents.get(agentType)if (agent) {Object.assign(agent, updates)}
      agent.lastHeartbeat = Date.now()}
    }
  }
  // 智能体心跳
const public = agentHeartbeat();
agentType: AgentType,
const status = Partial<AgentStatus>;
  ): void {this.updateAgentStatus(agentType, {}      ...status,);
lastHeartbeat: Date.now(),
}
      const isOnline = true}
    });
  }
  // 任务完成通知/,/g,/;
  public: notifyTaskCompleted(taskId: string, result: unknown): void {const task = this.tasks.get(taskId)if (!task) {}
      return}
    }
    task.status = TaskStatus.COMPLETED;
task.result = result;
task.metadata.completedAt = Date.now();
if (task.metadata.startedAt) {task.metadata.actualDuration =}
        task.metadata.completedAt - task.metadata.startedAt}
    }
    // 更新智能体性能统计
this.updateAgentPerformance();
task.assignedAgent!,
true,
task.metadata.actualDuration || 0;
    );
    // 检查是否有依赖此任务的其他任务
this.checkDependentTasks(taskId);
  }
  // 任务失败通知/,/g,/;
  public: notifyTaskFailed(taskId: string, error: unknown): void {const task = this.tasks.get(taskId)if (!task) {}
      return}
    }
    task.status = TaskStatus.FAILED;
task.error = error;
task.metadata.completedAt = Date.now();
if (task.metadata.startedAt) {task.metadata.actualDuration =}
        task.metadata.completedAt - task.metadata.startedAt}
    }
    // 更新智能体性能统计
this.updateAgentPerformance();
task.assignedAgent!,
false,
task.metadata.actualDuration || 0;
    );
    // 尝试重新分配任务或寻找替代方案
this.handleTaskFailure(task);
  }
  // 请求智能体协作
const public = async requestCollaboration();
fromAgent: AgentType,"
toAgent: AgentType,","
taskId: string,","
requestType: CollaborationRequest["requestType"];",";
const data = unknown;
  ): Promise<string> {const requestId = this.generateRequestId()const: request: CollaborationRequest = {const id = requestId;
fromAgent,
toAgent,
taskId,
requestType,"
data,","
timestamp: Date.now(),";
}
      const status = "PENDING"};
    ;};
this.collaborationRequests.set(requestId, request);
    // 通知目标智能体
const await = this.notifyAgentCollaborationRequest(request);
return requestId;
  }
  // 响应协作请求
const public = respondToCollaboration();
requestId: string,
const accepted = boolean;
responseData?: unknown;
  ): void {const request = this.collaborationRequests.get(requestId)if (!request) {}
      return;}
    }","
request.status = accepted ? "ACCEPTED" : "REJECTED;"";
    // 通知请求方智能体
this.notifyAgentCollaborationResponse(request, accepted, responseData);
  }
  // 私有方法实现
private generateTaskId(): string {}
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  private generateRequestId(): string {}
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  private sortTaskQueue(): void {this.taskQueue.sort(a, b) => {}      // 优先级高的在前
if (a.priority !== b.priority) {}
        return b.priority - a.priority}
      }
      // 创建时间早的在前
return a.metadata.createdAt - b.metadata.createdAt;
    });
  }
  private async processTaskQueue(): Promise<void> {const availableTasks = this.taskQueue.filter(;}      (task) =>;
task.status === TaskStatus.PENDING && this.areDependenciesMet(task);
    );
for (const task of availableTasks) {const assignedAgent = await this.assignTask(task);
if (assignedAgent) {task.assignedAgent = assignedAgenttask.status = TaskStatus.ASSIGNED;
task.metadata.assignedAt = Date.now();
        // 从队列中移除
this.removeFromQueue(task.id);
        // 通知智能体
}
        const await = this.notifyAgentTaskAssignment(task)}
      }
    }
  }
  private async assignTask(task: Task): Promise<AgentType | null> {// 应用协调规则/for (const rule of this.coordinationRules.sort(a, b) => b.priority - a.priority;);/g/;
    )) {if (rule.condition(task, this.agents)) {}        assignedAgent: rule.action(task, this.agents);
if (assignedAgent && this.isAgentAvailable(assignedAgent)) {}
          return assignedAgent}
        }
      }
    }
    // 如果没有规则匹配，使用默认分配策略
return this.defaultTaskAssignment(task);
  }
  private defaultTaskAssignment(task: Task): AgentType | null {const availableAgents = Array.from(this.agents.entries())}
      .filter([_, agent]) => this.isAgentAvailable(agent.type))}
      .map([type, agent]) => ({  type, agent  }));
if (availableAgents.length === 0) {}
      return null}
    }
    // 根据任务类型和智能体能力进行匹配
const suitableAgents = availableAgents.filter({  agent  }) =>;
agent.capabilities.some(cap) => cap.type === task.type);
    );
if (suitableAgents.length === 0) {// 如果没有完全匹配的，选择负载最低的/return availableAgents.reduce(min, current) =>,/g/;
current.agent.currentLoad < min.agent.currentLoad ? current : min;
}
      ).type}
    }
    // 选择最适合的智能体（考虑熟练度和当前负载）
return suitableAgents.reduce(best, current) => {const currentCapability = current.agent.capabilities.find(;}        (cap) => cap.type === task.type;
      )!;
const bestCapability = best.agent.capabilities.find(;);
        (cap) => cap.type === task.type;
      )!;
const  currentScore =;
currentCapability.proficiency * (1 - current.agent.currentLoad);
const  bestScore =;
bestCapability.proficiency * (1 - best.agent.currentLoad);
}
      return currentScore > bestScore ? current : best}
    }).type;
  }
  private isAgentAvailable(agentType: AgentType): boolean {const agent = this.agents.get(agentType)if (!agent || !agent.isOnline) {}
      return false}
    }
    // 检查是否超过最大并发任务数
const maxTasks = Math.max(;);
      ...agent.capabilities.map(cap) => cap.maxConcurrentTasks);
    );
return agent.activeTasks.length < maxTasks;
  }
  private areDependenciesMet(task: Task): boolean {if (!task.dependencies || task.dependencies.length === 0) {}
      return true}
    }
    return task.dependencies.every(depId) => {const depTask = this.tasks.get(depId)}
      return depTask && depTask.status === TaskStatus.COMPLETED}
    });
  }
  private removeFromQueue(taskId: string): void {}
    this.taskQueue = this.taskQueue.filter(task) => task.id !== taskId)}
  }
  private monitorAgentHealth(): void {const now = Date.now()const healthTimeout = 30000; // 30秒
for (const [agentType, agent] of this.agents.entries()) {if (now - agent.lastHeartbeat > healthTimeout) {agent.isOnline = false;
        // 重新分配该智能体的任务
}
        this.reassignAgentTasks(agentType)}
      }
    }
  }
  private reassignAgentTasks(agentType: AgentType): void {const tasksToReassign = Array.from(this.tasks.values()).filter(;}      (task) =>;
task.assignedAgent === agentType &&;
        (task.status === TaskStatus.ASSIGNED ||;);
task.status === TaskStatus.IN_PROGRESS);
    );
for (const task of tasksToReassign) {task.status = TaskStatus.PENDING;
task.assignedAgent = undefined;
}
      this.taskQueue.push(task)}
    }
    this.sortTaskQueue();
  }
  private optimizeTaskDistribution(): void {// 检查负载均衡/const agents = Array.from(this.agents.values()).filter(;);/g/;
      (agent) => agent.isOnline;
}
    )}
    if (agents.length < 2) {return}
    const  avgLoad =;
agents.reduce(sum, agent) => sum + agent.currentLoad, 0) / agents.length;
const threshold = 0.3; // 负载差异阈值
for (const agent of agents) {if (agent.currentLoad > avgLoad + threshold) {}        // 尝试将一些任务转移给负载较低的智能体
};
this.redistributeTasks(agent.type)}
      }
    }
  }
  private redistributeTasks(overloadedAgentType: AgentType): void {}
    const overloadedAgent = this.agents.get(overloadedAgentType)}
    if (!overloadedAgent) {return}
    const tasksToRedistribute = overloadedAgent.activeTasks;
      .map(taskId) => this.tasks.get(taskId));
      .filter(task) => task && task.status === TaskStatus.ASSIGNED);
      .slice(0, Math.ceil(overloadedAgent.activeTasks.length * 0.2)); // 重分配20%的任务
for (const task of tasksToRedistribute) {if (task) {task.status = TaskStatus.PENDING;
task.assignedAgent = undefined;
}
        this.taskQueue.push(task)}
      }
    }
    this.sortTaskQueue();
  }
  private updateAgentPerformance();
agentType: AgentType,
success: boolean,
const duration = number;
  ): void {}
    const agent = this.agents.get(agentType)}
    if (!agent) {return}
    const perf = agent.performance;
const totalTasks = perf.totalTasksCompleted + 1;
    // 更新成功率
perf.successRate =;
      (perf.successRate * perf.totalTasksCompleted + (success ? 1 : 0)) /
totalTasks;
    // 更新平均响应时间
perf.averageResponseTime =;
      (perf.averageResponseTime * perf.totalTasksCompleted + duration) /
totalTasks;
    // 更新完成任务数
perf.totalTasksCompleted = totalTasks;
  }
  private checkDependentTasks(completedTaskId: string): void {const dependentTasks = Array.from(this.tasks.values()).filter(;}      (task) =>;
task.dependencies?.includes(completedTaskId) &&;
task.status === TaskStatus.PENDING;
    );
for (const task of dependentTasks) {if (this.areDependenciesMet(task)) {}        // 将任务重新加入队列
if (!this.taskQueue.includes(task)) {}};
this.taskQueue.push(task)}
        }
      }
    }
    this.sortTaskQueue();
  }
  private handleTaskFailure(task: Task): void {// 记录失败原因/errorHandler.logError(ErrorType.TASK_EXECUTION_ERROR, {)      taskId: task.id,)agentType: task.assignedAgent,);/g/;
}
      const error = task.error;)}
    });
    // 如果是关键任务，尝试重新分配
if (task.priority >= TaskPriority.HIGH) {task.status = TaskStatus.PENDINGtask.assignedAgent = undefined;
this.taskQueue.push(task);
}
      this.sortTaskQueue()}
    }
  }
  private async notifyAgentTaskAssignment(task: Task): Promise<void> {}
    // 实际实现中，这里会通过消息队列或直接调用通知智能体}
console.log(`Task ${task.id;} assigned to ${task.assignedAgent}`);````;```;
  }
  private notifyAgentTaskCancellation(task: Task): void {}
    // 实际实现中，这里会通知智能体取消任务}
console.log(`Task ${task.id;} cancelled for ${task.assignedAgent}`);````;```;
  }
  private async notifyAgentCollaborationRequest();
const request = CollaborationRequest;
  ): Promise<void> {// 实际实现中，这里会通知目标智能体有协作请求/;}}/g/;
    console.log()}
      `Collaboration request ${request.id} sent to ${request.toAgent}`````;```;
    );
  }
  private notifyAgentCollaborationResponse();
request: CollaborationRequest,
const accepted = boolean;
responseData?: unknown;
  ): void {// 实际实现中，这里会通知请求方智能体协作响应/;}}/g/;
    console.log()}
      `Collaboration request ${request.id} ${`;}``"`;```;
}
        accepted ? "accepted" : "rejected"};
      } by ${request.toAgent}``````;```;
    );
  }
  private setupDefaultRules(): void {// 紧急任务优先分配给小艾"/this.coordinationRules.push({")""id: "emergency_to_xiaoai,")"/g"/;
);
condition: (task) => task.priority === TaskPriority.EMERGENCY,
action: () => AgentType.XIAOAI,
}
      const priority = 100}
    });
    // 诊断任务优先分配给小克"
this.coordinationRules.push({)")""id: "diagnosis_to_xiaoke,");
);
condition: (task) => task.type === TaskType.DIAGNOSIS,
action: () => AgentType.XIAOKE,
}
      const priority = 90}
    });
    // 健康咨询分配给老克"
this.coordinationRules.push({)")""id: "consultation_to_laoke,");
);
condition: (task) => task.type === TaskType.HEALTH_CONSULTATION,
action: () => AgentType.LAOKE,
}
      const priority = 80}
    });
    // 生活指导分配给索儿"
this.coordinationRules.push({)")""id: "lifestyle_to_soer,");
);
condition: (task) => task.type === TaskType.LIFESTYLE_GUIDANCE,
action: () => AgentType.SOER,
}
      const priority = 80}
    });
  }
  private initializeAgents(): void {// 初始化四个智能体的基本状态/const  agentConfigs = [;]{type: AgentType.XIAOAI}const capabilities = [;]          {type: TaskType.USER_INTERACTION}proficiency: 0.95,,/g,/;
  maxConcurrentTasks: 10,
const averageProcessingTime = 1000;
}
}
          }
          {type: TaskType.EMERGENCY_RESPONSE}proficiency: 0.9,
maxConcurrentTasks: 5,
const averageProcessingTime = 500;
}
}
          }
];
        ];
      }
      {type: AgentType.XIAOKE}const capabilities = [;]{type: TaskType.DIAGNOSIS}proficiency: 0.92,
maxConcurrentTasks: 8,
const averageProcessingTime = 3000;
}
}
          }
          {type: TaskType.DATA_ANALYSIS}proficiency: 0.88,
maxConcurrentTasks: 6,
const averageProcessingTime = 2000;
}
}
          }
];
        ];
      }
      {type: AgentType.LAOKE}const capabilities = [;]{type: TaskType.HEALTH_CONSULTATION}proficiency: 0.94,
maxConcurrentTasks: 12,
const averageProcessingTime = 2500;
}
}
          }
          {type: TaskType.KNOWLEDGE_SHARING}proficiency: 0.91,
maxConcurrentTasks: 8,
const averageProcessingTime = 1500;
}
}
          }
];
        ];
      }
      {type: AgentType.SOER}const capabilities = [;]}
}
          ;};
];
        ];
      };
    ];
for (const config of agentConfigs) {}};
const: agentStatus: AgentStatus = {,}
  id: `agent_${config.type.toLowerCase(}`,````,```;
type: config.type,
isOnline: false,
currentLoad: 0,
capabilities: config.capabilities,
activeTasks: [],
lastHeartbeat: 0,
performance: {successRate: 0.95,
averageResponseTime: 2000,
}
          const totalTasksCompleted = 0}
        }
      };
this.agents.set(config.type, agentStatus);
    }
  }
  // 获取系统状态
const public = getSystemStatus() {return {}      isRunning: this.isRunning,
totalAgents: this.agents.size,onlineAgents: Array.from(this.agents.values()).filter(;);
        (agent) => agent.isOnline;
      ).length,totalTasks: this.tasks.size,queuedTasks: this.taskQueue.length,activeTasks: Array.from(this.tasks.values()).filter(;);
        (task) =>;
task.status === TaskStatus.IN_PROGRESS ||;
task.status === TaskStatus.ASSIGNED;
      ).length,completedTasks: Array.from(this.tasks.values()).filter(;);
        (task) => task.status === TaskStatus.COMPLETED;
      ).length,pendingCollaborations: Array.from(;)","
this.collaborationRequests.values();";
}
      ).filter(req) => req.status === "PENDING").length;"};
    };
  }
}","
export default AgentCoordinator;""