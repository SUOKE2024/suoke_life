/* 义 *//;/g/;
 *//;/g/;
// 智能体类型枚举/;,/g/;
export enum AgentType {XIAOAI = 'xiaoai',';,}XIAOKE = 'xiaoke',';,'';
LAOKE = 'laoke',';'';
}
}
  SOER = 'soer',}'';'';
}
// 智能体状态枚举'/;,'/g'/;
export enum AgentStatus {';,}IDLE = 'idle',';,'';
BUSY = 'busy',';,'';
OFFLINE = 'offline',';'';
}
}
  ERROR = 'error',}'';'';
}
// 智能体优先级枚举'/;,'/g'/;
export enum AgentPriority {';,}LOW = 'low',';,'';
NORMAL = 'normal',';,'';
HIGH = 'high',';'';
}
}
  CRITICAL = 'critical',}'';'';
}
// 智能体任务类型'/;,'/g'/;
export enum TaskType {';,}DIAGNOSIS = 'diagnosis',';,'';
CONSULTATION = 'consultation',';,'';
RECOMMENDATION = 'recommendation',';,'';
EDUCATION = 'education',';,'';
MONITORING = 'monitoring',';'';
}
}
  COMPANIONSHIP = 'companionship',}'';'';
}
// 智能体能力接口/;,/g/;
export interface AgentCapability {id: string}name: string,;
description: string,;
enabled: boolean,;
}
}
  const version = string;}
}
// 智能体健康状态/;,/g/;
export interface AgentHealth {status: AgentStatus}lastHeartbeat: Date,;
responseTime: number,;
errorCount: number,;
}
}
  const uptime = number;}
}
// 智能体任务接口/;,/g/;
export interface AgentTask {id: string}type: TaskType,;
priority: AgentPriority,;
payload: any,;
createdAt: Date,';,'';
assignedTo: AgentType,';,'';
const status = 'pending' | 'processing' | 'completed' | 'failed';';,'';
result?: any;
}
}
  error?: string;}
}
// 智能体消息接口/;,/g/;
export interface AgentMessage {id: string}from: AgentType,';,'';
to: AgentType | AgentType[],';,'';
type: 'request' | 'response' | 'notification' | 'broadcast';','';
content: any,;
const timestamp = Date;
}
}
  correlationId?: string;}
}
// 智能体协作上下文/;,/g/;
export interface CollaborationContext {sessionId: string}participants: AgentType[],;
primaryAgent: AgentType,;
scenario: string,;
sharedData: Record<string, any>;
const startTime = Date;
}
}
  endTime?: Date;}
}
// 智能体性能指标/;,/g/;
export interface AgentMetrics {agentType: AgentType}tasksCompleted: number,;
averageResponseTime: number,;
successRate: number,;
errorRate: number,;
throughput: number,;
}
}
  const lastUpdated = Date;}
}
// 智能体事件类型'/;,'/g'/;
export type AgentEvent =';'';
  | { type: 'agent_started'; agentType: AgentType; timestamp: Date ;}';'';
  | { type: 'agent_stopped'; agentType: AgentType; timestamp: Date ;}';'';
  | {';,}type: 'task_assigned';','';
taskId: string,;
agentType: AgentType,;
}
      const timestamp = Date;}
    }';'';
  | {';,}type: 'task_completed';','';
taskId: string,;
agentType: AgentType,;
result: any,;
}
      const timestamp = Date;}
    }';'';
  | {';,}type: 'task_failed';','';
taskId: string,;
agentType: AgentType,;
error: string,;
}
      const timestamp = Date;}
    }';'';
  | {';,}type: 'collaboration_started';','';
sessionId: string,;
participants: AgentType[],;
}
      const timestamp = Date;}';'';
    }';'';
  | { type: 'collaboration_ended'; sessionId: string; timestamp: Date ;}';'';
  | {';,}type: 'health_check';','';
agentType: AgentType,;
health: AgentHealth,;
}
      const timestamp = Date;}
    };
// 基础智能体接口/;,/g/;
export interface Agent {;,}getId(): string;
getName(): string;
getDescription(): string;
getCapabilities(): AgentCapability[];
getStatus(): AgentStatus;
getMetrics(): AgentMetrics;
initialize(): Promise<void>;
shutdown(): Promise<void>;
}
}
  processTask(task: AgentTask): Promise<any>;}
}';'';
''';