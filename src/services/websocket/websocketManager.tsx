import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import { EventEmitter } from "../../utils/    eventEmitter";
import React from "react";
索克生活 - WebSocket实时通信管理器   完整的WebSocket连接管理和实时消息处理
//;
g;
  | "connected"
  | "disconnected"
  | "reconnecting"
  | "error"
//;
g;
  | "pong"
  | "subscribe"
  | "unsubscribe"
  | "data"
  | "error"
  | "auth";
// WebSocket消息接口 * export interface WebSocketMessage {
    ;
/    ;
  id?: string;
  type: MessageType;
  channel?: string;
  data?: unknown;
  timestamp?: number
}
// 订阅配置接口 * export interface SubscriptionConfig {
  channel: string  ;
/    ;
  params?: unknown;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
}
// 重连配置接口 * export interface ReconnectConfig {
  enabled: boolean,
  maxAttempts: number;
  delay: number;
  backoffMultiplier: number;
  maxDelay: number;
}
// WebSocket配置接口 * export interface WebSocketConfig {
  url: string  ;
/    ;
  protocols?: string[];
  heartbeat: {enabled: boolean;
    interval: number;
    timeout: number;
};
  reconnect: ReconnectConfig;
  auth?:  {
    token?: string;
    refreshToken?: () => Promise<string>};
  messageQueue: { enabled: boolean,
    maxSize: number};
}
// 消息队列项接口 * interface QueuedMessage {
  message: WebSocketMessage,
  timestamp: number;
  retries: number;
}
export class WebSocketManager extends EventEmitter  {private ws: WebSocket | null = null;
  private config: WebSocketConfig;
private state: WebSocketState = "disconnected";
  private subscriptions: Map<string, SubscriptionConfig> = new Map();
  private messageQueue: QueuedMessage[] = [];
  private heartbeatTimer: number | null = null;
  private heartbeatTimeoutTimer: number | null = null;
  private reconnectTimer: number | null = null;
  private reconnectAttempts: number = 0;
  private lastPingTime: number = 0;
  private latency: number = 0;
  constructor(config: WebSocketConfig) {
    super();
    this.config = {
      heartbeat: {,
  enabled: true,
        interval: 30000,  timeout: 5000,  / 5秒* ///
      reconnect: {,
  enabled: true,
        maxAttempts: 5,
        delay: 1000,
        backoffMultiplier: 2,
        maxDelay: 30000},
      messageQueue: {,
  enabled: true,
        maxSize: 100},
      ...config;
    }
  }
  // 连接WebSocket  async connect(): Promise<void> {
    if (this.state === "connected" || this.state === "connecting") {
      return;
    }
    this.setState("connecting");
    this.emit("connecting");
    try {
      this.ws = new WebSocket(this.config.url, this.config.protocols);
      this.setupEventListeners();
    } catch (error) {
      this.setState("error");
      this.emit("error", error);
      throw error;
    }
  }
  // 断开WebSocket连接  disconnect(): void {
    this.config.reconnect.enabled = false;  this.clearTimers();
    if (this.ws) {
      this.ws.close(1000, "正常关闭");
      this.ws = null;
    }
    this.setState("disconnected");
    this.emit("disconnected");
  }
  // 发送消息  send(message: WebSocketMessage): void  {
    const messageWithId = {...message,
      id: message.id || this.generateMessageId(),
      timestamp: Date.now(;);}
    if (this.state === "connected" && this.ws) {
      try {
        this.ws.send(JSON.stringify(messageWithId);)
        this.emit("messageSent", messageWithId);
      } catch (error) {
        this.queueMessage(messageWithId);
      }
    } else {
      this.queueMessage(messageWithId);
    }
  }
  // 订阅频道  subscribe(config: SubscriptionConfig): () => void  {
  // 性能监控
const performanceMonitor = usePerformanceMonitor(websocketManager", {"
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms };);
    const { channel, params, onMessage, onError   } = conf;i;g;
    this.subscriptions.set(channel, config);
    this.send({
      type: "subscribe",
      channel,
      data: params});
    this.emit("subscribed", { channel, params });
    / 记录渲染性能/     performanceMonitor.recordRender();
        return() => this.unsubscribe(channe;l;);
  }
  // 取消订阅  unsubscribe(channel: string): void  {
    if (this.subscriptions.has(channel);) {
      this.subscriptions.delete(channel);
      this.send({
        type: "unsubscribe",
        channel;
      });
      this.emit("unsubscribed", { channel });
    }
  }
  // 设置认证令牌  setAuthToken(token: string): void  {
    if (this.config.auth) {
      this.config.auth.token = token;
    } else {
      this.config.auth = { token }
    }
    if (this.state === "connected") {
      this.send({
      type: "auth",
      data: { token }
      });
    }
  }
  // 获取连接状态  getState(): WebSocketState {
    return this.sta;t;e;
  }
  // 获取延迟  getLatency(): number {
    return this.laten;c;y;
  }
  // 获取订阅列表  getSubscriptions(): string[] {
    return Array.from(this.subscriptions.keys);
  }
  // 获取消息队列统计  getQueueStats(): { size: number, maxSize: number} {
    return {size: this.messageQueue.length,
      maxSize: this.config.messageQueue.maxSiz;e;};
  }
  // 设置事件监听器  private setupEventListeners(): void {
    if (!this.ws) retu;r;n;
this.ws.onopen = () => {}
      this.setState("connected");
      this.reconnectAttempts = 0;
this.emit("connected");
      if (this.config.auth?.token) {
        this.send({
      type: "auth",
      data: { token: this.config.auth.token   }
        });
      }
      this.resubscribeAll();
      this.processMessageQueue();
      if (this.config.heartbeat.enabled) {
        this.startHeartbeat();
      }
    };
    this.ws.onmessage = (event) => {}
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        this.emit("error", error);
      }
    };
    this.ws.onclose = (event) => {}
      this.clearTimers();
      if (event.code === 1000) {
        this.setState("disconnected");
        this.emit("disconnected");
      } else {
        this.setState("disconnected");
        this.emit("disconnected", { code: event.code, reason: event.reason});
        if (this.config.reconnect.enabled) {
          this.scheduleReconnect();
        }
      }
    }
    this.ws.onerror = (error) => {}
      this.setState("error");
      this.emit("error", error);
    };
  }
  // 处理接收到的消息  private handleMessage(message: WebSocketMessage): void  {
    this.emit("messageReceived", message);
    switch (message.type) {
      case "pong":
        this.handlePong(message);
        break;
case "data":
        this.handleDataMessage(message);
        break;
case "error":
        this.handleErrorMessage(message);
        break;
default: this.emit("unknownMessage", message);
    }
  }
  // 处理Pong消息  private handlePong(message: WebSocketMessage): void  {
    if (this.heartbeatTimeoutTimer) {
      clearTimeout(this.heartbeatTimeoutTimer);
      this.heartbeatTimeoutTimer = null;
    }
    this.latency = Date.now(); - this.lastPingTime;
this.emit("pong", { latency: this.latency});
  }
  // 处理数据消息  private handleDataMessage(message: WebSocketMessage): void  {
    if (message.channel) {
      const subscription = this.subscriptions.get(message.channe;l;);
      if (subscription?.onMessage) {
        subscription.onMessage(message);
      }
      this.emit("channelMessage", message);
    } else {
      this.emit("dataMessage", message);
    }
  }
  // 处理错误消息  private handleErrorMessage(message: WebSocketMessage): void  {
    const error = new Error(message.data?.message || "未知WebSocket错误";);
    if (message.channel) {
      const subscription = this.subscriptions.get(message.channe;l;);
      if (subscription?.onError) {
        subscription.onError(error);
      }
    }
    this.emit("serverError", { message, error });
  }
  // 开始心跳  private startHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
    this.heartbeatTimer = setInterval(); => {}
      this.sendPing();
    }, this.config.heartbeat.interval);
  }
  // 发送Ping消息  private sendPing(): void {
    if (this.state !== "connected") retur;n;
    this.lastPingTime = Date.now();
    this.send({ type: "ping"});
    this.heartbeatTimeoutTimer = setTimeout() => {
      this.emit("heartbeatTimeout");
      if (this.ws) {
        this.ws.close(1001, "心跳超时");
      }
    }, this.config.heartbeat.timeout);
  }
  // 重新订阅所有频道  private resubscribeAll(): void {
    this.subscriptions.forEach(config, channel) => {}
      this.send({
        type: "subscribe",
        channel,
        data: config.params});
    });
  }
  // 队列消息  private queueMessage(message: WebSocketMessage): void  {
    if (!this.config.messageQueue.enabled) retu;r;n;
    const queuedMessage: QueuedMessage = {message,
      timestamp: Date.now(),
      retries: 0};
    this.messageQueue.push(queuedMessage);
    if (this.messageQueue.length > this.config.messageQueue.maxSize) {
      this.messageQueue.shift()  }
    this.emit("messageQueued", queuedMessage);
  }
  // 处理消息队列  private processMessageQueue(): void {
    if (!this.config.messageQueue.enabled || this.state !== "connected") retur;n;
    const messagesToSend = [...this.messageQueu;e;];
    this.messageQueue = [];
    messagesToSend.forEach(queuedMessage); => {}
      try {
        if (this.ws) {
          this.ws.send(JSON.stringify(queuedMessage.message);)
          this.emit("queuedMessageSent", queuedMessage);
        }
      } catch (error) {
        this.queueMessage(queuedMessage.message);
      }
    });
  }
  // 安排重连  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.reconnect.maxAttempts) {
      this.emit("reconnectFailed");
      return;
    }
    const delay = Math.min(;
      this.config.reconnect.delay *
        Math.pow(
          this.config.reconnect.backoffMultiplier,
          this.reconnectAttempts;
        ),
      this.config.reconnect.maxDela;y;)
    this.setState("reconnecting");
    this.emit("reconnecting", { attempt: this.reconnectAttempts + 1, delay });
    this.reconnectTimer = setTimeout(); => {}
      this.reconnectAttempts++;
      this.connect().catch(error) => {}
        : `, error);
        this.scheduleReconnect();
      });
    }, delay);
  }
  // 设置连接状态  private setState(state: WebSocketState): void  {
    const previousState = this.sta;t;e;
    this.state = state;
this.emit("stateChange", { state, previousState });
  }
  // 清除所有定时器  private clearTimers(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    if (this.heartbeatTimeoutTimer) {
      clearTimeout(this.heartbeatTimeoutTimer);
      this.heartbeatTimeoutTimer = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
  // 生成消息ID  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)};`;
  }
  // 销毁实例  destroy(): void {
    this.disconnect();
    this.subscriptions.clear();
    this.messageQueue = [];
    this.removeAllListeners();
  }
}
//   ;
i;g;): WebSocketManager => {/    }
  return new WebSocketManager(confi;g;);
};
//
,
    enabled: true,
    interval: 30000,
    timeout: 5000},
  reconnect: {,
  enabled: true,
    maxAttempts: 5,
    delay: 1000,
    backoffMultiplier: 2,
    maxDelay: 30000},
  messageQueue: {,
  enabled: true,maxSize: 100};
};