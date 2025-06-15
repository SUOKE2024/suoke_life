/**
 * 索克生活智能体通信协议
 * 定义智能体间的标准通信机制和消息格式
 */

import { EventEmitter } from 'events';
import { 
  AgentType, 
  AgentEvent, 
  CollaborationMessage, 
  AgentContext 
} from '../interfaces/UnifiedAgentInterface';

// ============================================================================
// 通信协议接口
// ============================================================================

export interface AgentCommunicationProtocol extends EventEmitter {
  // 点对点通信
  sendMessage(targetAgentId: string, message: AgentMessage): Promise<MessageResult>;
  sendMessageSync(targetAgentId: string, message: AgentMessage, timeout?: number): Promise<AgentMessage>;
  
  // 广播通信
  broadcastMessage(message: AgentMessage, targetTypes?: AgentType[]): Promise<BroadcastResult>;
  
  // 事件订阅
  subscribeToEvents(eventTypes: string[], callback: EventCallback): string;
  unsubscribeFromEvents(subscriptionId: string): void;
  
  // 频道管理
  createChannel(channelId: string, participants: string[]): Promise<void>;
  joinChannel(channelId: string): Promise<void>;
  leaveChannel(channelId: string): Promise<void>;
  sendChannelMessage(channelId: string, message: AgentMessage): Promise<void>;
  
  // 连接管理
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;
  getConnectionStatus(): ConnectionStatus;
}

// ============================================================================
// 消息类型定义
// ============================================================================

export enum MessageType {
  // 基础消息类型
  REQUEST = 'request',
  RESPONSE = 'response',
  NOTIFICATION = 'notification',
  
  // 协作消息类型
  COLLABORATION_REQUEST = 'collaboration_request',
  COLLABORATION_RESPONSE = 'collaboration_response',
  COLLABORATION_UPDATE = 'collaboration_update',
  
  // 状态消息类型
  STATUS_UPDATE = 'status_update',
  HEARTBEAT = 'heartbeat',
  
  // 数据消息类型
  DATA_SHARE = 'data_share',
  KNOWLEDGE_SHARE = 'knowledge_share',
  
  // 控制消息类型
  COMMAND = 'command',
  CONTROL = 'control',
  
  // 错误消息类型
  ERROR = 'error',
  WARNING = 'warning'
}

export enum MessagePriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  URGENT = 3,
  CRITICAL = 4
}

export interface AgentMessage {
  id: string;
  type: MessageType;
  senderId: string;
  recipientId?: string;        // 单播时使用
  recipientIds?: string[];     // 多播时使用
  channelId?: string;          // 频道消息时使用
  
  // 消息内容
  subject?: string;
  content: any;
  attachments?: MessageAttachment[];
  
  // 消息属性
  priority: MessagePriority;
  timestamp: Date;
  expiresAt?: Date;
  requiresAck: boolean;
  correlationId?: string;      // 用于关联请求和响应
  
  // 上下文信息
  context?: AgentContext;
  metadata?: Record<string, any>;
  
  // 路由信息
  routingHints?: RoutingHint[];
  deliveryOptions?: DeliveryOptions;
}

export interface MessageAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  data: any;
  encoding?: string;
}

export interface RoutingHint {
  type: 'direct' | 'broadcast' | 'multicast' | 'anycast';
  targets?: string[];
  criteria?: Record<string, any>;
}

export interface DeliveryOptions {
  retryAttempts: number;
  retryDelay: number;
  timeout: number;
  persistMessage: boolean;
  requiresDeliveryConfirmation: boolean;
}

// ============================================================================
// 通信结果类型
// ============================================================================

export interface MessageResult {
  messageId: string;
  success: boolean;
  deliveredAt?: Date;
  error?: CommunicationError;
  deliveryConfirmation?: DeliveryConfirmation;
}

export interface BroadcastResult {
  messageId: string;
  totalTargets: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  results: MessageResult[];
}

export interface DeliveryConfirmation {
  messageId: string;
  recipientId: string;
  receivedAt: Date;
  processedAt?: Date;
  acknowledged: boolean;
}

export interface CommunicationError {
  code: string;
  message: string;
  details?: any;
  retryable: boolean;
  suggestedRetryDelay?: number;
}

// ============================================================================
// 连接和状态管理
// ============================================================================

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

export interface ConnectionConfig {
  endpoints: string[];
  authentication?: AuthenticationConfig;
  retryPolicy?: RetryPolicy;
  heartbeatInterval?: number;
  messageQueueSize?: number;
  compressionEnabled?: boolean;
  encryptionEnabled?: boolean;
}

export interface AuthenticationConfig {
  type: 'none' | 'token' | 'certificate' | 'oauth';
  credentials?: any;
  refreshToken?: string;
  expiresAt?: Date;
}

export interface RetryPolicy {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  jitterEnabled: boolean;
}

// ============================================================================
// 事件处理
// ============================================================================

export type EventCallback = (event: AgentEvent) => void | Promise<void>;

export interface EventSubscription {
  id: string;
  eventTypes: string[];
  callback: EventCallback;
  filter?: EventFilter;
  createdAt: Date;
}

export interface EventFilter {
  agentIds?: string[];
  agentTypes?: AgentType[];
  priority?: MessagePriority;
  timeRange?: {
    start: Date;
    end: Date;
  };
  customFilters?: Record<string, any>;
}

// ============================================================================
// 频道管理
// ============================================================================

export interface Channel {
  id: string;
  name: string;
  description?: string;
  type: 'public' | 'private' | 'direct';
  participants: string[];
  administrators: string[];
  createdAt: Date;
  settings: ChannelSettings;
  metadata?: Record<string, any>;
}

export interface ChannelSettings {
  maxParticipants?: number;
  messageRetention?: number;  // 消息保留时间(秒)
  allowBroadcast: boolean;
  requiresApproval: boolean;
  encryptionEnabled: boolean;
  loggingEnabled: boolean;
}

// ============================================================================
// 消息队列和缓冲
// ============================================================================

export interface MessageQueue {
  enqueue(message: AgentMessage): Promise<void>;
  dequeue(): Promise<AgentMessage | null>;
  peek(): Promise<AgentMessage | null>;
  size(): number;
  clear(): Promise<void>;
  
  // 优先级队列功能
  enqueuePriority(message: AgentMessage, priority: MessagePriority): Promise<void>;
  
  // 批量操作
  enqueueBatch(messages: AgentMessage[]): Promise<void>;
  dequeueBatch(count: number): Promise<AgentMessage[]>;
}

export interface MessageBuffer {
  store(message: AgentMessage): Promise<void>;
  retrieve(messageId: string): Promise<AgentMessage | null>;
  remove(messageId: string): Promise<void>;
  cleanup(olderThan: Date): Promise<number>;
  
  // 查询功能
  findByCorrelationId(correlationId: string): Promise<AgentMessage[]>;
  findBySender(senderId: string, limit?: number): Promise<AgentMessage[]>;
  findByRecipient(recipientId: string, limit?: number): Promise<AgentMessage[]>;
}

// ============================================================================
// 通信统计和监控
// ============================================================================

export interface CommunicationMetrics {
  messagesSent: number;
  messagesReceived: number;
  messagesDelivered: number;
  messagesFailed: number;
  
  averageDeliveryTime: number;
  averageProcessingTime: number;
  
  connectionUptime: number;
  reconnectionCount: number;
  
  bandwidthUsage: {
    sent: number;      // bytes
    received: number;  // bytes
  };
  
  errorsByType: Record<string, number>;
  messagesByType: Record<MessageType, number>;
  messagesByPriority: Record<MessagePriority, number>;
}

export interface CommunicationHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  connectionStatus: ConnectionStatus;
  lastHeartbeat?: Date;
  latency: number;
  packetLoss: number;
  issues: CommunicationIssue[];
}

export interface CommunicationIssue {
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  firstOccurred: Date;
  lastOccurred: Date;
  count: number;
  suggestedAction?: string;
}

// ============================================================================
// 安全和加密
// ============================================================================

export interface SecurityConfig {
  encryptionEnabled: boolean;
  encryptionAlgorithm?: string;
  keyRotationInterval?: number;
  
  authenticationRequired: boolean;
  authorizationEnabled: boolean;
  
  messageIntegrityCheck: boolean;
  nonRepudiationEnabled: boolean;
  
  auditLoggingEnabled: boolean;
  sensitiveDataMasking: boolean;
}

export interface MessageSecurity {
  encrypted: boolean;
  signed: boolean;
  checksum?: string;
  keyId?: string;
  signature?: string;
}

// ============================================================================
// 协议实现基类
// ============================================================================

export abstract class BaseCommunicationProtocol extends EventEmitter implements AgentCommunicationProtocol {
  protected config: ConnectionConfig;
  protected status: ConnectionStatus = ConnectionStatus.DISCONNECTED;
  protected subscriptions: Map<string, EventSubscription> = new Map();
  protected channels: Map<string, Channel> = new Map();
  protected messageQueue: MessageQueue;
  protected messageBuffer: MessageBuffer;
  protected metrics: CommunicationMetrics;
  
  constructor(config: ConnectionConfig) {
    super();
    this.config = config;
    this.initializeMetrics();
  }
  
  // 抽象方法，由具体实现类实现
  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;
  abstract sendMessage(targetAgentId: string, message: AgentMessage): Promise<MessageResult>;
  
  // 通用实现
  isConnected(): boolean {
    return this.status === ConnectionStatus.CONNECTED;
  }
  
  getConnectionStatus(): ConnectionStatus {
    return this.status;
  }
  
  subscribeToEvents(eventTypes: string[], callback: EventCallback): string {
    const subscriptionId = this.generateSubscriptionId();
    const subscription: EventSubscription = {
      id: subscriptionId,
      eventTypes,
      callback,
      createdAt: new Date()
    };
    
    this.subscriptions.set(subscriptionId, subscription);
    return subscriptionId;
  }
  
  unsubscribeFromEvents(subscriptionId: string): void {
    this.subscriptions.delete(subscriptionId);
  }
  
  protected generateSubscriptionId(): string {
    return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  protected initializeMetrics(): void {
    this.metrics = {
      messagesSent: 0,
      messagesReceived: 0,
      messagesDelivered: 0,
      messagesFailed: 0,
      averageDeliveryTime: 0,
      averageProcessingTime: 0,
      connectionUptime: 0,
      reconnectionCount: 0,
      bandwidthUsage: { sent: 0, received: 0 },
      errorsByType: {},
      messagesByType: {} as Record<MessageType, number>,
      messagesByPriority: {} as Record<MessagePriority, number>
    };
  }
  
  // 其他通用方法的默认实现...
  async sendMessageSync(targetAgentId: string, message: AgentMessage, timeout: number = 30000): Promise<AgentMessage> {
    throw new Error('Synchronous messaging not implemented');
  }
  
  async broadcastMessage(message: AgentMessage, targetTypes?: AgentType[]): Promise<BroadcastResult> {
    throw new Error('Broadcast messaging not implemented');
  }
  
  async createChannel(channelId: string, participants: string[]): Promise<void> {
    throw new Error('Channel management not implemented');
  }
  
  async joinChannel(channelId: string): Promise<void> {
    throw new Error('Channel management not implemented');
  }
  
  async leaveChannel(channelId: string): Promise<void> {
    throw new Error('Channel management not implemented');
  }
  
  async sendChannelMessage(channelId: string, message: AgentMessage): Promise<void> {
    throw new Error('Channel messaging not implemented');
  }
}

// ============================================================================
// 工厂函数
// ============================================================================

export interface CommunicationProtocolFactory {
  createProtocol(type: string, config: ConnectionConfig): AgentCommunicationProtocol;
  getSupportedProtocols(): string[];
}

// ============================================================================
// 导出
// ============================================================================

export {
  AgentCommunicationProtocol,
  BaseCommunicationProtocol,
  CommunicationProtocolFactory
};