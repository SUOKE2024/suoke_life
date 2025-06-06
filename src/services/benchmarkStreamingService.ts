import { getCurrentEnvConfig } from '../constants/config';

// 流式事件类型
export interface StreamEvent {
  type: 'benchmark_progress' | 'benchmark_complete' | 'benchmark_error' | 'system_status';
  data: any;
  timestamp: string;
}

// 流式配置
export interface StreamConfig {
  benchmark_id: string;
  model_id: string;
  total_samples: number;
}

// 事件监听器类型
export type EventListener = (event: StreamEvent) => void;

/**
 * 基准测试流式服务
 */
export class BenchmarkStreamingService {
  private ws: WebSocket | null = null;
  private baseUrl: string;
  private listeners: Map<string, EventListener[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;

  constructor() {
    const envConfig = getCurrentEnvConfig();
    const apiUrl = envConfig.API_BASE_URL || 'http://localhost:8000';
    this.baseUrl = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  }

  /**
   * 连接WebSocket
   */
  async connect(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {try {this.ws = new WebSocket(`${this.baseUrl}/ws/streaming`);

        this.ws.onopen = () => {
          console.log('WebSocket连接已建立');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onerror = error => {
          console.error('WebSocket连接错误:', error);
          this.isConnecting = false;
          reject(new Error('WebSocket连接失败'));
        };

        this.ws.onmessage = event => {
          try {
            const streamEvent: StreamEvent = JSON.parse(event.data);
            this.handleMessage(streamEvent);
          } catch (error) {
            console.error('解析WebSocket消息失败:', error);
          }
        };

        this.ws.onclose = event => {
          console.log('WebSocket连接已关闭:', event.code, event.reason);
          this.isConnecting = false;
          this.ws = null;

          // 自动重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
              console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
              this.connect().catch(console.error);
            }, this.reconnectDelay * this.reconnectAttempts);
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
    this.reconnectAttempts = this.maxReconnectAttempts; // 阻止自动重连
  }

  /**
   * 订阅事件
   */
  subscribeToEvents(eventTypes: string[]): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {command: 'subscribe',event_types: eventTypes;
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket未连接，无法订阅事件');
    }
  }

  /**
   * 取消订阅事件
   */
  unsubscribeFromEvents(eventTypes: string[]): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {command: 'unsubscribe',event_types: eventTypes;
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * 启动流式基准测试
   */
  startStreamingBenchmark(config: StreamConfig): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {command: 'start_benchmark',config;
      };
      this.ws.send(JSON.stringify(message));
    } else {
      throw new Error('WebSocket未连接，无法启动流式测试');
    }
  }

  /**
   * 停止流式基准测试
   */
  stopStreamingBenchmark(benchmarkId: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {command: 'stop_benchmark',benchmark_id: benchmarkId;
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * 添加事件监听器
   */
  addEventListener(eventType: string, listener: EventListener): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(listener);
  }

  /**
   * 移除事件监听器
   */
  removeEventListener(eventType: string, listener: EventListener): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(event: StreamEvent): void {
    const listeners = this.listeners.get(event.type);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(event);
        } catch (error) {
          console.error('事件监听器执行错误:', error);
        }
      });
    }

    // 通用事件监听器
    const allListeners = this.listeners.get('*');
    if (allListeners) {
      allListeners.forEach(listener => {
        try {
          listener(event);
        } catch (error) {
          console.error('通用事件监听器执行错误:', error);
        }
      });
    }
  }

  /**
   * 获取连接状态
   */
  getConnectionState(): string {
    if (!this.ws) return 'CLOSED';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'OPEN';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }

  /**
   * 检查是否已连接
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * 发送心跳包
   */
  sendHeartbeat(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {command: 'ping',timestamp: new Date().toISOString();
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * 启动心跳检测
   */
  startHeartbeat(interval: number = 30000): void {
    setInterval(() => {
      this.sendHeartbeat();
    }, interval);
  }
}

// 创建单例实例
export const benchmarkStreamingService = new BenchmarkStreamingService();
