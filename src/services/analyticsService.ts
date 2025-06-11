
// 事件类型定义
export interface AnalyticsEvent {
  id: string;
  type: 'api_call' | 'error' | 'performance' | 'user_action' | 'system';
  timestamp: number;
  data: Record<string, any>;
  userId?: string;
  sessionId: string;
  service?: string;
  endpoint?: string;
}

// 性能指标
export interface PerformanceMetrics {
  responseTime: number;
  throughput: number;
  errorRate: number;
  cacheHitRate: number;
  memoryUsage: number;
  cpuUsage: number;
}

// 用户行为数据
export interface UserBehavior {
  userId: string;
  sessionId: string;
  actions: string[];
  duration: number;
  screens: string[];
  errors: number;
}

// 服务使用统计
export interface ServiceUsage {
  service: string;
  calls: number;
  errors: number;
  avgResponseTime: number;
  lastUsed: number;
}

// 分析配置
interface AnalyticsConfig {
  enabled: boolean;
  batchSize: number;
  flushInterval: number;
  maxEvents: number;
  enableUserTracking: boolean;
  enablePerformanceTracking: boolean;
  enableErrorTracking: boolean;
}

class AnalyticsService {
  private events: AnalyticsEvent[] = [];
  private sessionId: string;
  private userId?: string;
  private config: AnalyticsConfig;
  private flushTimer?: NodeJS.Timeout;
  private performanceObserver?: PerformanceObserver;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.config = {
      enabled: true,
      batchSize: 50,
      flushInterval: 30000, // 30秒
      maxEvents: 1000,
      enableUserTracking: true,
      enablePerformanceTracking: true,
      enableErrorTracking: true
    };
    this.initializePerformanceTracking();
    this.startFlushTimer();
  }

  // 生成会话ID
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 生成事件ID
  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 初始化性能跟踪
  private initializePerformanceTracking() {
    if (!this.config.enablePerformanceTracking || typeof PerformanceObserver === 'undefined') {
      return;
    }

    try {
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          this.trackEvent('performance', {
            name: entry.name,
            duration: entry.duration,
            startTime: entry.startTime,
            entryType: entry.entryType
          });
        });
      });
      this.performanceObserver.observe({ entryTypes: ["measure", "navigation", "resource"] });
    } catch (error) {
      console.warn('Performance tracking not supported:', error);
    }
  }

  // 启动定时刷新
  private startFlushTimer() {
    this.flushTimer = setInterval(() => {
      this.flush();
    }, this.config.flushInterval);
  }

  // 设置用户ID
  setUserId(userId: string) {
    this.userId = userId;
    this.trackEvent('user_action', {
      action: 'login',
      userId
    });
  }

  // 清除用户ID
  clearUserId() {
    if (this.userId) {
      this.trackEvent('user_action', {
        action: 'logout',
        userId: this.userId
      });
    }
    this.userId = undefined;
  }

  // 跟踪事件
  trackEvent(type: AnalyticsEvent['type'], data: Record<string, any>, service?: string, endpoint?: string) {
    if (!this.config.enabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type,
      timestamp: Date.now(),
      data,
      userId: this.userId,
      sessionId: this.sessionId,
      service,
      endpoint
    };

    this.events.push(event);

    // 如果事件过多，移除旧事件
    if (this.events.length > this.config.maxEvents) {
      this.events = this.events.slice(-this.config.maxEvents);
    }

    // 如果达到批次大小，立即刷新
    if (this.events.length >= this.config.batchSize) {
      this.flush();
    }
  }

  // 跟踪API调用
  trackApiCall(service: string, endpoint: string, method: string, responseTime: number, status: number) {
    this.trackEvent('api_call', {
      method,
      responseTime,
      status,
      success: status >= 200 && status < 300
    }, service, endpoint);
  }

  // 跟踪错误
  trackError(error: Error, context?: Record<string, any>) {
    if (!this.config.enableErrorTracking) return;

    this.trackEvent('error', {
      message: error.message,
      stack: error.stack,
      name: error.name,
      context
    });
  }

  // 跟踪用户行为
  trackUserAction(action: string, data?: Record<string, any>) {
    if (!this.config.enableUserTracking) return;

    this.trackEvent('user_action', {
      action,
      ...data
    });
  }

  // 跟踪页面访问
  trackPageView(screen: string, data?: Record<string, any>) {
    this.trackEvent('user_action', {
      action: 'page_view',
      screen,
      ...data
    });
  }

  // 获取性能指标
  getPerformanceMetrics(): PerformanceMetrics {
    const apiEvents = this.events.filter(e => e.type === 'api_call');
    const errorEvents = this.events.filter(e => e.type === 'error');
    
    const responseTimes = apiEvents.map(e => e.data.responseTime).filter(Boolean);
    const avgResponseTime = responseTimes.length > 0
      ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
      : 0;

    const errorRate = apiEvents.length > 0
      ? (errorEvents.length / apiEvents.length) * 100
      : 0;

    return {
      responseTime: avgResponseTime,
      throughput: apiEvents.length,
      errorRate,
      cacheHitRate: this.calculateCacheHitRate(),
      memoryUsage: this.getMemoryUsage(),
      cpuUsage: 0 // 浏览器环境无法获取CPU使用率
    };
  }

  // 计算缓存命中率
  private calculateCacheHitRate(): number {
    const cacheEvents = this.events.filter(e =>
      e.type === 'api_call' && e.data.fromCache !== undefined
    );

    if (cacheEvents.length === 0) return 0;

    const hits = cacheEvents.filter(e => e.data.fromCache).length;
    return (hits / cacheEvents.length) * 100;
  }

  // 获取内存使用情况
  private getMemoryUsage(): number {
    if (typeof performance !== 'undefined' && (performance as any).memory) {
      const memory = (performance as any).memory;
      return memory.usedJSHeapSize / memory.totalJSHeapSize * 100;
    }
    return 0;
  }

  // 获取用户行为数据
  getUserBehavior(): UserBehavior[] {
    const userSessions = new Map<string, UserBehavior>();
    
    this.events
      .filter(e => e.type === 'user_action' && e.userId)
      .forEach(event => {
        const key = `${event.userId}_${event.sessionId}`;
        if (!userSessions.has(key)) {
          userSessions.set(key, {
            userId: event.userId!,
            sessionId: event.sessionId,
            actions: [],
            duration: 0,
            screens: [],
            errors: 0
          });
        }

        const behavior = userSessions.get(key)!;
        behavior.actions.push(event.data.action);
        
        if (event.data.screen && !behavior.screens.includes(event.data.screen)) {
          behavior.screens.push(event.data.screen);
        }
      });

    return Array.from(userSessions.values());
  }

  // 获取服务使用统计
  getServiceUsage(): ServiceUsage[] {
    const serviceStats = new Map<string, ServiceUsage>();

    this.events
      .filter(e => e.type === 'api_call' && e.service)
      .forEach(event => {
        const service = event.service!;
        if (!serviceStats.has(service)) {
          serviceStats.set(service, {
            service,
            calls: 0,
            errors: 0,
            avgResponseTime: 0,
            lastUsed: 0
          });
        }

        const stats = serviceStats.get(service)!;
        stats.calls++;
        stats.lastUsed = Math.max(stats.lastUsed, event.timestamp);
        
        if (!event.data.success) {
          stats.errors++;
        }

        if (event.data.responseTime) {
          stats.avgResponseTime = (stats.avgResponseTime * (stats.calls - 1) + event.data.responseTime) / stats.calls;
        }
      });

    return Array.from(serviceStats.values());
  }

  // 刷新事件到服务器
  private async flush() {
    if (this.events.length === 0) return;

    const eventsToSend = [...this.events];
    this.events = [];

    try {
      // 这里应该发送到分析服务器
      console.log('Flushing analytics events:', eventsToSend.length);
      // await this.sendToServer(eventsToSend);
    } catch (error) {
      console.error('Failed to flush analytics events:', error);
      // 如果发送失败，将事件重新加入队列
      this.events.unshift(...eventsToSend);
    }
  }

  // 清理资源
  destroy() {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }

    this.flush();
  }
}

// 创建单例实例
export const analyticsService = new AnalyticsService();
export default analyticsService;