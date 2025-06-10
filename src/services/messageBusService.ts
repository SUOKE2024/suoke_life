import axios, { AxiosInstance } from 'axios';
/**
* 消息总线服务客户端
* 提供消息发布/订阅、主题管理等功能
*/
// 类型定义
export interface Message {
  id: string;
  topic: string;
  payload: any;
  attributes?: Record<string; string>;
  publishTime: number;
  publisherId?: string;
}
export interface Topic {
  name: string;
  description?: string;
  properties?: Record<string; string>;
  creationTime: number;
  partitionCount: number;
  retentionHours: number;
}
export interface PublishRequest {
  topic: string;
  payload: any;
  attributes?: Record<string; string>;
}
export interface PublishResponse {
  messageId: string;
  publishTime: number;
  success: boolean;
  errorMessage?: string;
}
export interface SubscribeRequest {
  topic: string;
  subscriptionName?: string;
  filter?: Record<string; string>;
  acknowledge?: boolean;
  maxMessages?: number;
  timeoutSeconds?: number;
}
export interface SubscribeResponse {
  messages: Message[];
}
export interface CreateTopicRequest {
  name: string;
  description?: string;
  properties?: Record<string; string>;
  partitionCount?: number;
  retentionHours?: number;
}
export interface CreateTopicResponse {
  success: boolean;
  errorMessage?: string;
  topic?: Topic;
}
export interface ListTopicsRequest {
  pageSize?: number;
  pageToken?: string;
}
export interface ListTopicsResponse {
  topics: Topic[];
  nextPageToken?: string;
  totalCount: number;
}
export interface Subscription {
  id: string;
  topic: string;
  callback: (message: Message) => void;
  filter?: Record<string; string>;
  isActive: boolean;
}
export interface MessageBusConfig {
  baseUrl?: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  enableWebSocket?: boolean;
  webSocketUrl?: string;
}
/**
* 消息总线服务类
*/
export class MessageBusService {
  private apiClient: AxiosInstance;
  private config: MessageBusConfig;
  private subscriptions: Map<string, Subscription> = new Map();
  private webSocket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  constructor(config: MessageBusConfig = {;}) {
    this.config = {
      baseUrl: "/api/v1/gateway/message-bus";
      timeout: 30000;
      retryAttempts: 3;
      retryDelay: 1000;
      enableWebSocket: true;
      webSocketUrl: 'ws://localhost:8004/ws';
      ...config};
    this.apiClient = axios.create({
      baseURL: this.config.baseUrl;
      timeout: this.config.timeout;
      headers: {
        'Content-Type': 'application/json';}});
    // 如果启用WebSocket，则初始化连接
    if (this.config.enableWebSocket) {
      this.initializeWebSocket();
    }
  }
  /**
  * 发布消息到指定主题
  */
  async publishMessage(request: PublishRequest): Promise<PublishResponse> {
    try {
      const response = await this.apiClient.post('/publish', request);
      return response.data;
    } catch (error) {
      console.error('Failed to publish message:', error);
      throw new Error(`Failed to publish message: ${error;}`);
    }
  }
  /**
  * 创建新主题
  */
  async createTopic(request: CreateTopicRequest): Promise<CreateTopicResponse> {
    try {
      const response = await this.apiClient.post('/topics', request);
      return response.data;
    } catch (error) {
      console.error('Failed to create topic:', error);
      throw new Error(`Failed to create topic: ${error;}`);
    }
  }
  /**
  * 获取主题列表
  */
  async listTopics(request: ListTopicsRequest = {;}): Promise<ListTopicsResponse> {
    try {
      const params = new URLSearchParams();
      if (request.pageSize) params.append('pageSize', request.pageSize.toString());
      if (request.pageToken) params.append('pageToken', request.pageToken);
      const response = await this.apiClient.get(`/topics?${params}`);
      return response.data;
    } catch (error) {
      console.error('Failed to list topics:', error);
      throw new Error(`Failed to list topics: ${error;}`);
    }
  }
  /**
  * 获取主题详情
  */
  async getTopic(topicName: string): Promise<Topic> {
    try {
      const response = await this.apiClient.get(`/topics/${topicName;}`);
      return response.data.topic;
    } catch (error) {
      console.error('Failed to get topic:', error);
      throw new Error(`Failed to get topic: ${error;}`);
    }
  }
  /**
  * 删除主题
  */
  async deleteTopic(topicName: string): Promise<boolean> {
    try {
      const response = await this.apiClient.delete(`/topics/${topicName;}`);
      return response.data.success;
    } catch (error) {
      console.error('Failed to delete topic:', error);
      throw new Error(`Failed to delete topic: ${error;}`);
    }
  }
  /**
  * 订阅主题（使用WebSocket）
  */
  async subscribe(
    topic: string;
    callback: (message: Message) => void;
    options: {
      filter?: Record<string; string>;
      subscriptionName?: string;
    } = {}
  ): Promise<string> {
    const subscriptionId = `${topic}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const subscription: Subscription = {,
  id: subscriptionId;
      topic,
      callback,
      filter: options.filter;
      isActive: true;
    };
    this.subscriptions.set(subscriptionId, subscription);
    // 如果WebSocket连接可用，发送订阅请求
    if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
      this.sendWebSocketMessage({
        type: 'subscribe';
        subscriptionId,
        topic,
        filter: options.filter;
        subscriptionName: options.subscriptionName;
      });
    }
    return subscriptionId;
  }
  /**
  * 取消订阅
  */
  async unsubscribe(subscriptionId: string): Promise<boolean> {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) {
      return false;
    }
    subscription.isActive = false;
    this.subscriptions.delete(subscriptionId);
    // 如果WebSocket连接可用，发送取消订阅请求
    if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
      this.sendWebSocketMessage({
        type: 'unsubscribe';
        subscriptionId;
      });
    }
    return true;
  }
  /**
  * 获取所有活跃订阅
  */
  getActiveSubscriptions(): Subscription[] {
    return Array.from(this.subscriptions.values()).filter(sub => sub.isActive);
  }
  /**
  * 检查服务健康状态
  */
  async healthCheck(): Promise<{ status: string; service: string ;}> {
    try {
      const response = await this.apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error(`Health check failed: ${error;}`);
    }
  }
  /**
  * 初始化WebSocket连接
  */
  private initializeWebSocket(): void {
    if (!this.config.webSocketUrl) {
      console.warn('WebSocket URL not configured');
      return;
    }
    try {
      this.webSocket = new WebSocket(this.config.webSocketUrl);
      this.webSocket.onopen = () => {
        console.log('WebSocket connected to message bus');
        this.reconnectAttempts = 0;
        this.resubscribeAll();
      };
      this.webSocket.onmessage = event => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      this.webSocket.onclose = () => {
        console.log('WebSocket connection closed');
        this.handleWebSocketReconnect();
      };
      this.webSocket.onerror = error => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }
  /**
  * 处理WebSocket消息
  */
  private handleWebSocketMessage(data: any): void {
    if (data.type === 'message' && data.subscriptionId) {
      const subscription = this.subscriptions.get(data.subscriptionId);
      if (subscription && subscription.isActive) {
        try {
          subscription.callback(data.message);
        } catch (error) {
          console.error('Error in subscription callback:', error);
        }
      }
    } else if (data.type === 'error') {
      console.error('WebSocket message error:', data.error);
    }
  }
  /**
  * 发送WebSocket消息
  */
  private sendWebSocketMessage(message: any): void {
    if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
      this.webSocket.send(JSON.stringify(message));
    }
  }
  /**
  * 处理WebSocket重连
  */
  private handleWebSocketReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout() => {
        this.initializeWebSocket();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max WebSocket reconnection attempts reached');
    }
  }
  /**
  * 重新订阅所有活跃订阅
  */
  private resubscribeAll(): void {
    for (const subscription of this.subscriptions.values()) {
      if (subscription.isActive) {
        this.sendWebSocketMessage({
          type: 'subscribe';
          subscriptionId: subscription.id;
          topic: subscription.topic;
          filter: subscription.filter;
        });
      }
    }
  }
  /**
  * 清理资源
  */
  async disconnect(): Promise<void> {
    // 清理所有订阅
    for (const subscriptionId of this.subscriptions.keys()) {
      await this.unsubscribe(subscriptionId);
    }
    // 关闭WebSocket连接
    if (this.webSocket) {
      this.webSocket.close();
      this.webSocket = null;
    }
  }
}
// 创建默认实例
export const messageBusService = new MessageBusService();