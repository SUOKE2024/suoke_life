/**
 * 索克生活智能体类型定义
 */

// 智能体类型枚举
export enum AgentType {
  XIAOAI = 'xiaoai',
  XIAOKE = 'xiaoke',
  LAOKE = 'laoke',
  SOER = 'soer'
}

// 智能体状态枚举
export enum AgentStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  OFFLINE = 'offline',
  ERROR = 'error'
}

// 智能体优先级枚举
export enum AgentPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// 智能体任务类型
export enum TaskType {
  DIAGNOSIS = 'diagnosis',
  CONSULTATION = 'consultation',
  RECOMMENDATION = 'recommendation',
  EDUCATION = 'education',
  MONITORING = 'monitoring',
  COMPANIONSHIP = 'companionship'
}

// 智能体能力接口
export interface AgentCapability {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  version: string;
}

// 智能体健康状态
export interface AgentHealth {
  status: AgentStatus;
  lastHeartbeat: Date;
  responseTime: number;
  errorCount: number;
  uptime: number;
}

// 智能体任务接口
export interface AgentTask {
  id: string;
  type: TaskType;
  priority: AgentPriority;
  payload: any;
  createdAt: Date;
  assignedTo: AgentType;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

// 智能体消息接口
export interface AgentMessage {
  id: string;
  from: AgentType;
  to: AgentType | AgentType[];
  type: 'request' | 'response' | 'notification' | 'broadcast';
  content: any;
  timestamp: Date;
  correlationId?: string;
}

// 智能体协作上下文
export interface CollaborationContext {
  sessionId: string;
  participants: AgentType[];
  primaryAgent: AgentType;
  scenario: string;
  sharedData: Record<string, any>;
  startTime: Date;
  endTime?: Date;
}

// 智能体性能指标
export interface AgentMetrics {
  agentType: AgentType;
  tasksCompleted: number;
  averageResponseTime: number;
  successRate: number;
  errorRate: number;
  throughput: number;
  lastUpdated: Date;
}

// 智能体事件类型
export type AgentEvent =
  | { type: 'agent_started'; agentType: AgentType; timestamp: Date }
  | { type: 'agent_stopped'; agentType: AgentType; timestamp: Date }
  | { type: 'task_assigned'; taskId: string; agentType: AgentType; timestamp: Date }
  | { type: 'task_completed'; taskId: string; agentType: AgentType; result: any; timestamp: Date }
  | { type: 'task_failed'; taskId: string; agentType: AgentType; error: string; timestamp: Date }
  | { type: 'collaboration_started'; sessionId: string; participants: AgentType[]; timestamp: Date }
  | { type: 'collaboration_ended'; sessionId: string; timestamp: Date }
  | { type: 'health_check'; agentType: AgentType; health: AgentHealth; timestamp: Date };

// 基础智能体接口
export interface Agent {
  getId(): string;
  getName(): string;
  getDescription(): string;
  getCapabilities(): AgentCapability[];
  getStatus(): AgentStatus;
  getMetrics(): AgentMetrics;
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
  processTask(task: AgentTask): Promise<any>;
}
