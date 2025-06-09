/**
* 性能监控服务
* 监控API网关和应用的性能指标
*/
export interface PerformanceMetrics {
  // API性能指标
  apiResponseTime: number;,
  apiSuccessRate: number;,
  apiErrorRate: number;,
  apiThroughput: number;
  // 网络性能指标
  networkLatency: number;,
  networkBandwidth: number;,
  connectionQuality: 'excellent' | 'good' | 'fair' | 'poor';
  // 应用性能指标
  memoryUsage: number;,
  cpuUsage: number;,
  batteryLevel: number;,
  storageUsage: number;
  // 用户体验指标
  screenLoadTime: number;,
  interactionResponseTime: number;,
  errorCount: number;,
  crashCount: number;
}
export interface PerformanceAlert {
  id: string;,
  type: 'warning' | 'error' | 'critical';,
  metric: keyof PerformanceMetrics;,
  value: number;,
  threshold: number;,
  message: string;,
  timestamp: Date;,
  resolved: boolean;
}
class PerformanceMonitor {
  private metrics: PerformanceMetrics;
  private alerts: PerformanceAlert[] = [];
  private isMonitoring = false;
  constructor() {
    this.metrics = this.getInitialMetrics();
  }
  /**
  * 开始性能监控
  */
  startMonitoring(): void {
    this.isMonitoring = true;
    console.log('性能监控已启动');
  }
  /**
  * 停止性能监控
  */
  stopMonitoring(): void {
    this.isMonitoring = false;
    console.log('性能监控已停止');
  }
  /**
  * 获取当前性能指标
  */
  getCurrentMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }
  /**
  * 记录API调用性能
  */
  recordApiCall(duration: number, success: boolean): void {
    this.metrics.apiResponseTime = duration;
    if (success) {
      this.metrics.apiSuccessRate = Math.min(100, this.metrics.apiSuccessRate + 0.1);
    } else {
      this.metrics.apiErrorRate = Math.min(100, this.metrics.apiErrorRate + 0.1);
      this.metrics.errorCount++;
    }
  }
  /**
  * 记录屏幕加载时间
  */
  recordScreenLoad(screenName: string, loadTime: number): void {
    this.metrics.screenLoadTime = loadTime;
    console.log(`屏幕 ${screenName} 加载时间: ${loadTime}ms`);
  }
  private getInitialMetrics(): PerformanceMetrics {
    return {
      apiResponseTime: 0,
      apiSuccessRate: 100,
      apiErrorRate: 0,
      apiThroughput: 0,
      networkLatency: 0,
      networkBandwidth: 0,
      connectionQuality: 'good',
      memoryUsage: 0,
      cpuUsage: 0,
      batteryLevel: 100,
      storageUsage: 0,
      screenLoadTime: 0,
      interactionResponseTime: 0,
      errorCount: 0,
      crashCount: 0;
    };
  }
}
// 创建全局实例
export const performanceMonitor = new PerformanceMonitor();
// 导出类型和实例
export default PerformanceMonitor;