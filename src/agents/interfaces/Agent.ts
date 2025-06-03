active","
  INACTIVE = inactive","
  BUSY = "busy,"
  ERROR = "error",
  MAINTENANCE = maintenance""
}
/**////
 * 智能体行为接口
export interface AgentBehavior {
  /**////
   * 处理任务;
   ;
  processTask(taskId: string, params: any): Promise<any>;
  /**////
   * 获取状态
  getStatus(): AgentStatus;
  /**////
   * 更新状态
  updateStatus(status: AgentStatus): void;
  /**////
   * 获取能力列表
  getCapabilities(): string[];
  /**////
   * 检查是否支持某个能力
  hasCapability(capability: string): boolean;
}
/**////
 * 智能体通信接口
export interface AgentCommunication {
  /**////
   * 发送消息给其他智能体;
   ;
  sendMessage(targetAgentId: string, message: AgentMessage): Promise<void>;
  /**////
   * 接收消息
  receiveMessage(message: AgentMessage): Promise<AgentResponse>;
  /**////
   * 广播消息
  broadcast(message: AgentMessage): Promise<void>;
  /**////
   * 订阅事件
  subscribe(eventType: string, callback: (event: any) => void): void;
  /**////
   * 取消订阅
  unsubscribe(eventType: string): void;
}
/**////
 * 智能体消息接口
export interface AgentMessage {;
  id: string;
  fromAgentId: string;
  toAgentId?: string;
  type: MessageType;
  content: any;
  timestamp: Date;
  priority: MessagePriority;
  metadata?: Record<string, any>;
}
/**////
 * 智能体响应接口
export interface AgentResponse {;
  messageId: string;
  agentId: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: Date;
}
/**////
 * 消息类型枚举
export enum MessageType {
  TASK_REQUEST = "task_request,"
  TASK_RESPONSE = "task_response",
  COLLABORATION_INVITE = collaboration_invite","
  COLLABORATION_ACCEPT = "collaboration_accept,"
  COLLABORATION_DECLINE = "collaboration_decline",
  STATUS_UPDATE = status_update","
  DATA_SHARE = "data_share,"
  NOTIFICATION = "notification",
  HEARTBEAT = heartbeat""
}
/**////
 * 消息优先级枚举
export enum MessagePriority {
  LOW = 1,
  NORMAL = 2,;
  HIGH = 3,;
  URGENT = 4;
}
/**////
 * 智能体学习接口
export interface AgentLearning {
  /**////
   * 从经验中学习;
   ;
  learnFromExperience(experience: Experience): Promise<void>;
  /**////
   * 更新知识库
  updateKnowledge(knowledge: Knowledge): Promise<void>;
  /**////
   * 获取学习统计
  getLearningStats(): LearningStats;
  /**////
   * 评估性能
  evaluatePerformance(): PerformanceMetrics;
}
/**////
 * 经验接口
export interface Experience {;
  taskId: string;
  action: string;
  context: any;
  outcome: any;
  feedback: number; //////     -1 到 1 的反馈分数
timestamp: Date;
}
/**////
 * 知识接口
export interface Knowledge {;
  domain: string;
  type: "fact | "rule" | pattern" | "case;"
  content: any;
  confidence: number;
  source: string;
  timestamp: Date;
}
/**////
 * 学习统计接口
export interface LearningStats {;
  totalExperiences: number;
  successRate: number;
  averageFeedback: number;
  knowledgeBaseSize: number;
  lastLearningTime: Date;
}
/**////
 * 性能指标接口
export interface PerformanceMetrics {;
  accuracy: number;
  responseTime: number;
  throughput: number;
  errorRate: number;
  userSatisfaction: number;
  timestamp: Date;
}
/**////
 * 智能体配置接口
export interface AgentConfig {;
  id: string;
  name: string;
  type: AgentType;
  capabilities: string[];
  maxConcurrentTasks: number;
  timeout: number;
  retryAttempts: number;
  learningEnabled: boolean;
  communicationConfig: CommunicationConfig;
  resourceLimits: ResourceLimits;
}
/**////
 * 智能体类型枚举
export enum AgentType {
  XIAOAI = "xiaoai",
  XIAOKE = xiaoke", "
  LAOKE = "laoke,"
  SOER = "soer"
}
/**////
 * 通信配置接口;
export interface CommunicationConfig {;
  protocol: grpc" | "rest | "websocket";
  endpoint: string;
  timeout: number;
  retryPolicy: RetryPolicy;
  authentication: AuthConfig;
}
/**////
 * 重试策略接口
export interface RetryPolicy {;
  maxAttempts: number;
  backoffStrategy: linear" | "exponential;
  initialDelay: number;
  maxDelay: number;
}
/**////
 * 认证配置接口
export interface AuthConfig {;
  type: "none" | token" | "certificate;
  credentials?: any;
}
/**////
 * 资源限制接口
export interface ResourceLimits {;
  maxMemoryMB: number;
  maxCpuPercent: number;
  maxDiskMB: number;
  maxNetworkMbps: number;
}
/**////
 * 智能体监控接口
export interface AgentMonitoring {
  /**////
   * 获取健康状态;
   ;
  getHealthStatus(): HealthStatus;
  /**////
   * 获取性能指标
  getMetrics(): AgentMetrics;
  /**////
   * 获取日志
  getLogs(level?: LogLevel, limit?: number): LogEntry[];
  /**////
   * 设置告警规则
  setAlertRule(rule: AlertRule): void;
}
/**////
 * 健康状态接口
export interface HealthStatus {;
  status: "healthy" | degraded" | "unhealthy;
  checks: HealthCheck[];
  lastCheckTime: Date;
}
/**////
 * 健康检查接口
export interface HealthCheck {;
  name: string;
  status: "pass" | fail" | "warn;
  message?: string;
  duration: number;
}
/**////
 * 智能体指标接口
export interface AgentMetrics {;
  tasksProcessed: number;
  averageResponseTime: number;
  errorCount: number;
  memoryUsage: number;
  cpuUsage: number;
  networkUsage: number;
  timestamp: Date;
}
/**////
 * 日志级别枚举
export enum LogLevel {
  DEBUG = "debug",
  INFO = info","
  WARN = "warn,"
  ERROR = "error",
  FATAL = fatal""
}
/**////
 * 日志条目接口;
export interface LogEntry {;
  level: LogLevel;
  message: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}
/**////
 * 告警规则接口
export interface AlertRule {;
  name: string;
  condition: string;
  threshold: number;
  action: "log | "notify" | restart";
  enabled: boolean;
}
export default {
  AgentStatus,;
  AgentType,;
  MessageType,;
  MessagePriority,;
  LogLevel;
};
  */////