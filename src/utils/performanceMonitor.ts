import { EventEmitter } from 'events';
// 性能指标接口
interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}
// API性能指标
interface ApiPerformanceMetric extends PerformanceMetric {
  url: string,
  method: string;
  statusCode?: number;
  duration: number,
  success: boolean;
}
// 用户交互指标
interface UserInteractionMetric extends PerformanceMetric {
  screen: string,
  action: string;
  duration: number;
}
// 内存使用指标
interface MemoryMetric extends PerformanceMetric {
  usedJSHeapSize: number,
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}
// 性能监控器类
class PerformanceMonitor {
  private eventEmitter: EventEmitter;
  private metrics: PerformanceMetric[] = [];
  private apiMetrics: ApiPerformanceMetric[] = [];
  private userInteractionMetrics: UserInteractionMetric[] = [];
  private memoryMetrics: MemoryMetric[] = [];
  private isEnabled: boolean = true;
  constructor() {
    this.eventEmitter = new EventEmitter();
    this.startMemoryMonitoring();
  }
  // 设置监控状态
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }
  // 记录API请求性能
  recordApiRequest(
    url: string,
    method: string,
    duration: number,
    statusCode?: number,
    success: boolean = true,
  ): void {
    if (!this.isEnabled) return;
    const metric: ApiPerformanceMetric = {,
  name: 'api_request',
      value: duration,
      timestamp: Date.now(),
      url: this.extractEndpoint(url),
      method,
      statusCode,
      duration,
      success,
      tags: {,
  endpoint: this.extractEndpoint(url),
        method,
        status: statusCode?.toString() || 'unknown',
      },
    };
    this.apiMetrics.push(metric);
    this.metrics.push(metric);
    this.eventEmitter.emit('metric_recorded', metric);
    // 保持最近100条记录
    if (this.apiMetrics.length > 100) {
      this.apiMetrics.shift();
    }
    // 慢请求警告
    if (duration > 3000) {
      this.eventEmitter.emit('slow_api_request', metric);
    }
  }
  // 记录用户交互性能
  recordUserInteraction(screen: string, action: string, duration: number): void {
    if (!this.isEnabled) return;
    const metric: UserInteractionMetric = {,
  name: 'user_interaction',
      value: duration,
      timestamp: Date.now(),
      screen,
      action,
      duration,
      tags: {
        screen,
        action,
      },
    };
    this.userInteractionMetrics.push(metric);
    this.metrics.push(metric);
    this.eventEmitter.emit('metric_recorded', metric);
    // 保持最近100条记录
    if (this.userInteractionMetrics.length > 100) {
      this.userInteractionMetrics.shift();
    }
    // 慢交互警告
    if (duration > 1000) {
      this.eventEmitter.emit('slow_user_interaction', metric);
    }
  }
  // 开始内存监控
  private startMemoryMonitoring(): void {
    if (typeof window !== 'undefined' && 'performance' in window && 'memory' in (window.performance as any)) {
      setInterval() => {
        this.recordMemoryUsage();
      }, 30000); // 每30秒记录一次
    }
  }
  // 记录内存使用
  private recordMemoryUsage(): void {
    if (!this.isEnabled) return;
    const memory = (performance as any).memory;
    if (memory) {
      const metric: MemoryMetric = {,
  name: 'memory_usage',
        value: memory.usedJSHeapSize,
        timestamp: Date.now(),
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit,
        tags: {,
  type: 'heap',
        },
      };
      this.memoryMetrics.push(metric);
      this.metrics.push(metric);
      this.eventEmitter.emit('metric_recorded', metric);
      // 保持最近100条记录
      if (this.memoryMetrics.length > 100) {
        this.memoryMetrics.shift();
      }
      // 内存使用过高警告
      const usagePercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
      if (usagePercent > 80) {
        this.eventEmitter.emit('high_memory_usage', metric);
      }
    }
  }
  // 获取API性能统计
  getApiPerformanceStats(): {
    averageResponseTime: number,
  successRate: number;
    slowRequestsCount: number,
  totalRequests: number;
    errorRate: number;
  } {
    if (this.apiMetrics.length === 0) {
      return {
        averageResponseTime: 0,
        successRate: 0,
        slowRequestsCount: 0,
        totalRequests: 0,
        errorRate: 0,
      };
    }
    const totalDuration = this.apiMetrics.reduce(sum, metric) => sum + metric.duration, 0);
    const successfulRequests = this.apiMetrics.filter(metric => metric.success).length;
    const slowRequests = this.apiMetrics.filter(metric => metric.duration > 3000).length;
    return {
      averageResponseTime: totalDuration / this.apiMetrics.length,
      successRate: (successfulRequests / this.apiMetrics.length) * 100,
      slowRequestsCount: slowRequests,
      totalRequests: this.apiMetrics.length,
      errorRate: (this.apiMetrics.length - successfulRequests) / this.apiMetrics.length) * 100,
    };
  }
  // 获取用户交互性能统计
  getUserInteractionStats(): {
    averageInteractionTime: number,
  slowInteractionsCount: number;
    totalInteractions: number,
  screenStats: Record<string, { count: number; averageTime: number }>;
  } {
    if (this.userInteractionMetrics.length === 0) {
      return {
        averageInteractionTime: 0,
        slowInteractionsCount: 0,
        totalInteractions: 0,
        screenStats: {},
      };
    }
    const totalDuration = this.userInteractionMetrics.reduce(sum, metric) => sum + metric.duration,
      0,
    );
    const slowInteractions = this.userInteractionMetrics.filter(
      metric => metric.duration > 1000,
    ).length;
    // 按屏幕统计
    const screenStats: Record<string, { count: number; averageTime: number }> = {};
    this.userInteractionMetrics.forEach(metric => {
      if (!screenStats[metric.screen]) {
        screenStats[metric.screen] = { count: 0, averageTime: 0 };
      }
      screenStats[metric.screen].count++;
    });
    // 计算每个屏幕的平均时间
    Object.keys(screenStats).forEach(screen => {
      const screenMetrics = this.userInteractionMetrics.filter(m => m.screen === screen);
      const screenTotalTime = screenMetrics.reduce(sum, m) => sum + m.duration, 0);
      screenStats[screen].averageTime = screenTotalTime / screenMetrics.length;
    });
    return {
      averageInteractionTime: totalDuration / this.userInteractionMetrics.length,
      slowInteractionsCount: slowInteractions,
      totalInteractions: this.userInteractionMetrics.length,
      screenStats,
    };
  }
  // 获取内存使用统计
  getMemoryStats(): {
    currentUsage: number,
  averageUsage: number;
    peakUsage: number,
  usagePercent: number;
  } {
    if (this.memoryMetrics.length === 0) {
      return {
        currentUsage: 0,
        averageUsage: 0,
        peakUsage: 0,
        usagePercent: 0,
      };
    }
    const latest = this.memoryMetrics[this.memoryMetrics.length - 1];
    const totalUsage = this.memoryMetrics.reduce(sum, metric) => sum + metric.usedJSHeapSize, 0);
    const peakUsage = Math.max(...this.memoryMetrics.map(metric => metric.usedJSHeapSize));
    return {
      currentUsage: latest.usedJSHeapSize,
      averageUsage: totalUsage / this.memoryMetrics.length,
      peakUsage,
      usagePercent: (latest.usedJSHeapSize / latest.jsHeapSizeLimit) * 100,
    };
  }
  // 生成性能报告
  generatePerformanceReport(): {
    timestamp: number,
  api: ReturnType<typeof this.getApiPerformanceStats>;
    userInteraction: ReturnType<typeof this.getUserInteractionStats>,
  memory: ReturnType<typeof this.getMemoryStats>;
    recommendations: string[];
  } {
    const apiStats = this.getApiPerformanceStats();
    const interactionStats = this.getUserInteractionStats();
    const memoryStats = this.getMemoryStats();
    const recommendations: string[] = [];
    // 生成建议
    if (apiStats.averageResponseTime > 2000) {
      recommendations.push('API响应时间较慢，建议优化网络请求或后端性能');
    }
    if (apiStats.errorRate > 5) {
      recommendations.push('API错误率较高，建议检查网络连接和错误处理');
    }
    if (interactionStats.averageInteractionTime > 500) {
      recommendations.push('用户交互响应时间较慢，建议优化UI渲染性能');
    }
    if (memoryStats.usagePercent > 70) {
      recommendations.push('内存使用率较高，建议检查内存泄漏和优化内存使用');
    }
    return {
      timestamp: Date.now(),
      api: apiStats,
      userInteraction: interactionStats,
      memory: memoryStats,
      recommendations,
    };
  }
  // 清除所有指标
  clearMetrics(): void {
    this.metrics = [];
    this.apiMetrics = [];
    this.userInteractionMetrics = [];
    this.memoryMetrics = [];
  }
  // 添加事件监听器
  on(event: string, listener: (...args: any[]) => void): void {
    this.eventEmitter.on(event, listener);
  }
  // 移除事件监听器
  off(event: string, listener: (...args: any[]) => void): void {
    this.eventEmitter.off(event, listener);
  }
  // 提取API端点名称
  private extractEndpoint(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.pathname.split('/').slice(0, 3).join('/'); // 取前3段路径
    } catch {
      return url.split('?')[0]; // 如果不是完整URL，去掉查询参数
    }
  }
}
// 创建全局性能监控实例
export const performanceMonitor = new PerformanceMonitor();
// 导出类型
export type { PerformanceMetric, ApiPerformanceMetric, UserInteractionMetric, MemoryMetric };
// 导出性能监控装饰器
export function measurePerformance(
  target: any,
  propertyName: string,
  descriptor: PropertyDescriptor,
) {
  const method = descriptor.value;
  descriptor.value = async function (this: any, ...args: any[]) {
    const startTime = Date.now();
    try {
      const result = await method.apply(this, args);
      const duration = Date.now() - startTime;
      performanceMonitor.recordUserInteraction(target.constructor.name, propertyName, duration);
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      performanceMonitor.recordUserInteraction(
        target.constructor.name,
        `${propertyName}_error`,
        duration,
      );
      throw error;
    }
  };
  return descriptor;
}