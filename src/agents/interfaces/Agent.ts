/* 举 *//;/g/;
 *//;,/g/;
export enum AgentStatus {ACTIVE = 'active',';,}INACTIVE = 'inactive',';,'';
BUSY = 'busy',';,'';
ERROR = 'error',';'';
}
}
  MAINTENANCE = 'maintenance',}'';'';
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentBehavior {/* 务 *//;}   */;/;,/g/;
processTask(taskId: string, params: any): Promise<any>;

  /* 态 *//;/g/;
   *//;,/g/;
getStatus(): AgentStatus;

  /* 态 *//;/g/;
   *//;,/g/;
updateStatus(status: AgentStatus): void;

  /* 表 *//;/g/;
   *//;,/g/;
getCapabilities(): string[];

  /* 力 *//;/g/;
   *//;/g/;
}
}
  hasCapability(capability: string): boolean;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentCommunication {/* 体 *//;}   */;/;,/g/;
sendMessage(targetAgentId: string, message: AgentMessage): Promise<void>;

  /* 息 *//;/g/;
   *//;,/g/;
receiveMessage(message: AgentMessage): Promise<AgentResponse>;

  /* 息 *//;/g/;
   *//;,/g/;
broadcast(message: AgentMessage): Promise<void>;

  /* 件 *//;/g/;
   *//;,/g/;
subscribe(eventType: string, callback: (event: any) => void): void;

  /* 阅 *//;/g/;
   *//;/g/;
}
}
  unsubscribe(eventType: string): void;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentMessage {id: string}const fromAgentId = string;
toAgentId?: string;
type: MessageType,;
content: any,;
timestamp: Date,;
const priority = MessagePriority;
}
}
  metadata?: Record<string; any>;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentResponse {messageId: string}agentId: string,;
const success = boolean;
data?: any;
error?: string;
}
}
  const timestamp = Date;}
}

/* 举 *//;/g/;
 */'/;,'/g'/;
export enum MessageType {';,}TASK_REQUEST = 'task_request',';,'';
TASK_RESPONSE = 'task_response',';,'';
COLLABORATION_INVITE = 'collaboration_invite',';,'';
COLLABORATION_ACCEPT = 'collaboration_accept',';,'';
COLLABORATION_DECLINE = 'collaboration_decline',';,'';
STATUS_UPDATE = 'status_update',';,'';
DATA_SHARE = 'data_share',';,'';
NOTIFICATION = 'notification',';'';
}
}
  HEARTBEAT = 'heartbeat',}'';'';
}

/* 举 *//;/g/;
 *//;,/g/;
export enum MessagePriority {LOW = 1}NORMAL = 2,;
HIGH = 3,;
}
}
  URGENT = 4,}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentLearning {/* 习 *//;}   */;/;,/g/;
learnFromExperience(experience: Experience): Promise<void>;

  /* 库 *//;/g/;
   *//;,/g/;
updateKnowledge(knowledge: Knowledge): Promise<void>;

  /* 计 *//;/g/;
   *//;,/g/;
getLearningStats(): LearningStats;

  /* 能 *//;/g/;
   *//;/g/;
}
}
  evaluatePerformance(): PerformanceMetrics;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface Experience {taskId: string}action: string,;
context: any,;
outcome: any,;
feedback: number; // -1 到 1 的反馈分数,/;/g/;
}
}
  const timestamp = Date;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface Knowledge {';,}domain: string,';,'';
type: 'fact' | 'rule' | 'pattern' | 'case';','';
content: any,;
confidence: number,;
source: string,;
}
}
  const timestamp = Date;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface LearningStats {totalExperiences: number}successRate: number,;
averageFeedback: number,;
knowledgeBaseSize: number,;
}
}
  const lastLearningTime = Date;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface PerformanceMetrics {accuracy: number}responseTime: number,;
throughput: number,;
errorRate: number,;
userSatisfaction: number,;
}
}
  const timestamp = Date;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentConfig {id: string}name: string,;
type: AgentType,;
capabilities: string[],;
maxConcurrentTasks: number,;
timeout: number,;
retryAttempts: number,;
learningEnabled: boolean,;
communicationConfig: CommunicationConfig,;
}
}
  const resourceLimits = ResourceLimits;}
}

/* 举 *//;/g/;
 */'/;,'/g'/;
export enum AgentType {';,}XIAOAI = 'xiaoai',';,'';
XIAOKE = 'xiaoke',';,'';
LAOKE = 'laoke',';'';
}
}
  SOER = 'soer',}'';'';
}

/* 口 *//;/g/;
 */'/;,'/g'/;
export interface CommunicationConfig {';,}protocol: 'grpc' | 'rest' | 'websocket';','';
endpoint: string,;
timeout: number,;
retryPolicy: RetryPolicy,;
}
}
  const authentication = AuthConfig;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface RetryPolicy {';,}maxAttempts: number,';,'';
backoffStrategy: 'linear' | 'exponential';','';
initialDelay: number,;
}
}
  const maxDelay = number;}
}

/* 口 *//;/g/;
 */'/;,'/g'/;
export interface AuthConfig {';,}const type = 'none' | 'token' | 'certificate';';'';
}
}
  credentials?: any;}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface ResourceLimits {maxMemoryMB: number}maxCpuPercent: number,;
maxDiskMB: number,;
}
}
  const maxNetworkMbps = number;}
}

/* 口 *//;/g/;
 */'/;,'/g'/;
export interface HealthStatus {';,}status: 'healthy' | 'warning' | 'critical';','';
uptime: number,;
memoryUsage: number,;
cpuUsage: number,;
const lastCheck = Date;
}
}
  issues?: string[];}
}

/* 口 *//;/g/;
 *//;,/g/;
export interface AgentMonitoring {/* 态 *//;}   */;/;,/g/;
getHealthStatus(): HealthStatus;

  /* 标 *//;/g/;
   *//;,/g/;
getMetrics(): PerformanceMetrics;

  /* 值 *//;/g/;
   *//;/g/;
}
}
  setThresholds(thresholds: Record<string, number>): void;}
}

export default {AgentStatus}AgentType,;
MessageType,;
}
  MessagePriority,};
};';'';
''';