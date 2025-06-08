/**
* 性能监控系统
* 监控应用性能指标并提供优化建议
*/
export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  category: 'network' | 'rendering' | 'memory' | 'cpu' | 'user_interaction';
  threshold?: number;
  status: 'good' | 'warning' | 'critical';
}
export interface PerformanceReport {
  timestamp: number;
  metrics: PerformanceMetric[];
  summary: {;
  score: number;
    issues: string[];
  recommendations: string[];
};
}
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetric[] = [];
  private observers: PerformanceObserver[] = [];
  private isMonitoring = false;
  private constructor() {
    this.setupPerformanceObservers();
  }
  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }
  /**
  * 开始性能监控
  */
  public startMonitoring(): void {
    if (this.isMonitoring) return;
    this.isMonitoring = true;
    this.collectInitialMetrics();
    this.startPeriodicCollection();
    console.log('🚀 性能监控已启动');
  }
  /**
  * 停止性能监控
  */
  public stopMonitoring(): void {
    this.isMonitoring = false;
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    console.log('⏹️ 性能监控已停止');
  }
  /**
  * 记录自定义性能指标
  */
  public recordMetric(
    name: string,
    value: number,
    unit: string,
    category: PerformanceMetric['category'],
    threshold?: number,
  ): void {
    const metric: PerformanceMetric = {
      name,
      value,
      unit,
      timestamp: Date.now(),
      category,
      threshold,
      status: this.getMetricStatus(value, threshold),
    };
    this.metrics.push(metric);
    this.trimMetrics();
  }
  /**
  * 测量函数执行时间
  */
  public async measureFunction<T>(
    name: string,
    fn: () => Promise<T> | T,
  ): Promise<T> {
    const startTime = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - startTime;
      this.recordMetric(
        `function_${name}`,
        duration,
        "ms",cpu',
        100, // 100ms threshold;
      );
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      this.recordMetric(
        `function_${name}_error`,
        duration,
        "ms",cpu',
      );
      throw error;
    }
  }
  /**
  * 测量API请求性能
  */
  public measureApiRequest(url: string, duration: number, status: number): void {
    this.recordMetric(
      `api_request_${this.getUrlPath(url)}`,
      duration,
      "ms",network',
      2000, // 2s threshold;
    );
    this.recordMetric(
      `api_status_${status}`,
      1,
      "count",network',
    );
  }
  /**
  * 获取性能报告
  */
  public getPerformanceReport(): PerformanceReport {
    const recentMetrics = this.metrics.filter(
      metric => Date.now() - metric.timestamp < 60000, // 最近1分钟
    );
    const score = this.calculatePerformanceScore(recentMetrics);
    const issues = this.identifyIssues(recentMetrics);
    const recommendations = this.generateRecommendations(issues);
    return {
      timestamp: Date.now(),
      metrics: recentMetrics,
      summary: {
        score,
        issues,
        recommendations,
      },
    };
  }
  /**
  * 获取关键性能指标
  */
  public getVitalMetrics(): {
    fcp: number; // First Contentful Paint,
  lcp: number; // Largest Contentful Paint;
    fid: number; // First Input Delay,
  cls: number; // Cumulative Layout Shift;
    ttfb: number; // Time to First Byte;
  } {
    const getLatestMetric = (name: string) => {
      const metric = this.metrics;
        .filter(m => m.name === name)
        .sort(a, b) => b.timestamp - a.timestamp)[0];
      return metric?.value || 0;
    };
    return {
      fcp: getLatestMetric('first_contentful_paint'),
      lcp: getLatestMetric('largest_contentful_paint'),
      fid: getLatestMetric('first_input_delay'),
      cls: getLatestMetric('cumulative_layout_shift'),
      ttfb: getLatestMetric('time_to_first_byte'),
    };
  }
  /**
  * 获取内存使用情况
  */
  public getMemoryUsage(): {
    used: number,
  total: number;
    percentage: number;
  } {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100,
      };
    }
    return { used: 0, total: 0, percentage: 0 };
  }
  /**
  * 设置性能观察器
  */
  private setupPerformanceObservers(): void {
    if (typeof PerformanceObserver === 'undefined') return;
    // 观察导航时间
    try {
      const navObserver = new PerformanceObserver(list) => {
        list.getEntries().forEach(entry) => {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.recordNavigationMetrics(navEntry);
          }
        });
      });
      navObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navObserver);
    } catch (e) {
      console.warn('Navigation observer not supported');
    }
    // 观察资源加载时间
    try {
      const resourceObserver = new PerformanceObserver(list) => {
        list.getEntries().forEach(entry) => {
          if (entry.entryType === 'resource') {
            this.recordResourceMetric(entry as PerformanceResourceTiming);
          }
        });
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    } catch (e) {
      console.warn('Resource observer not supported');
    }
    // 观察用户交互
    try {
      const interactionObserver = new PerformanceObserver(list) => {
        list.getEntries().forEach(entry) => {
          if (entry.entryType === 'event') {
            this.recordInteractionMetric(entry as PerformanceEventTiming);
          }
        });
      });
      interactionObserver.observe({ entryTypes: ['event'] });
      this.observers.push(interactionObserver);
    } catch (e) {
      console.warn('Event observer not supported');
    }
  }
  /**
  * 收集初始性能指标
  */
  private collectInitialMetrics(): void {
    // 收集内存使用情况
    const memoryUsage = this.getMemoryUsage();
    if (memoryUsage.total > 0) {
      this.recordMetric(
        'memory_usage',
        memoryUsage.percentage,
        "%",memory',
        80, // 80% threshold;
      );
    }
    // 收集连接信息
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      this.recordMetric(
        'network_downlink',
        connection.downlink,
        "Mbps",network',
      );
    }
  }
  /**
  * 开始定期收集
  */
  private startPeriodicCollection(): void {
    setInterval() => {
      if (!this.isMonitoring) return;
      this.collectInitialMetrics();
    }, 30000); // 每30秒收集一次
  }
  /**
  * 记录导航指标
  */
  private recordNavigationMetrics(entry: PerformanceNavigationTiming): void {
    this.recordMetric('dns_lookup', entry.domainLookupEnd - entry.domainLookupStart, "ms",network');
    this.recordMetric('tcp_connect', entry.connectEnd - entry.connectStart, "ms",network');
    this.recordMetric('request_response', entry.responseEnd - entry.requestStart, "ms",network');
    this.recordMetric('dom_loading', entry.domContentLoadedEventEnd - entry.domLoading, "ms",rendering');
    this.recordMetric('page_load', entry.loadEventEnd - entry.loadEventStart, "ms",rendering');
  }
  /**
  * 记录资源指标
  */
  private recordResourceMetric(entry: PerformanceResourceTiming): void {
    const duration = entry.responseEnd - entry.startTime;
    const resourceType = this.getResourceType(entry.name);
    this.recordMetric(
      `resource_${resourceType}`,
      duration,
      "ms",network',
      1000, // 1s threshold;
    );
  }
  /**
  * 记录交互指标
  */
  private recordInteractionMetric(entry: PerformanceEventTiming): void {
    this.recordMetric(
      `interaction_${entry.name}`,
      entry.duration,
      "ms",user_interaction',
      100, // 100ms threshold;
    );
  }
  /**
  * 获取指标状态
  */
  private getMetricStatus(value: number, threshold?: number): PerformanceMetric['status'] {
    if (!threshold) return 'good';
    if (value > threshold * 2) return 'critical';
    if (value > threshold) return 'warning';
    return 'good';
  }
  /**
  * 计算性能分数
  */
  private calculatePerformanceScore(metrics: PerformanceMetric[]): number {
    if (metrics.length === 0) return 100;
    const weights = {
      good: 1,
      warning: 0.7,
      critical: 0.3,
    };
    const totalWeight = metrics.reduce(sum, metric) => sum + weights[metric.status], 0);
    const maxWeight = metrics.length;
    return Math.round(totalWeight / maxWeight) * 100);
  }
  /**
  * 识别性能问题
  */
  private identifyIssues(metrics: PerformanceMetric[]): string[] {
    const issues: string[] = [];
    const criticalMetrics = metrics.filter(m => m.status === 'critical');
    const warningMetrics = metrics.filter(m => m.status === 'warning');
    if (criticalMetrics.length > 0) {
      issues.push(`发现 ${criticalMetrics.length} 个严重性能问题`);
    }
    if (warningMetrics.length > 0) {
      issues.push(`发现 ${warningMetrics.length} 个性能警告`);
    }
    // 检查特定问题
    const memoryMetric = metrics.find(m => m.name === 'memory_usage');
    if (memoryMetric && memoryMetric.value > 90) {
      issues.push('内存使用率过高');
    }
    const apiMetrics = metrics.filter(m => m.name.startsWith('api_request_'));
    const slowApis = apiMetrics.filter(m => m.value > 3000);
    if (slowApis.length > 0) {
      issues.push(`${slowApis.length} 个API请求响应过慢`);
    }
    return issues;
  }
  /**
  * 生成优化建议
  */
  private generateRecommendations(issues: string[]): string[] {
    const recommendations: string[] = [];
    if (issues.some(issue => issue.includes('内存'))) {
      recommendations.push('考虑优化内存使用，清理不必要的对象引用');
    }
    if (issues.some(issue => issue.includes('API'))) {
      recommendations.push('优化API请求，考虑使用缓存或请求合并');
    }
    if (issues.some(issue => issue.includes('严重'))) {
      recommendations.push('立即检查严重性能问题，可能影响用户体验');
    }
    if (recommendations.length === 0) {
      recommendations.push('性能表现良好，继续保持');
    }
    return recommendations;
  }
  /**
  * 获取URL路径
  */
  private getUrlPath(url: string): string {
    try {
      return new URL(url).pathname.replace(/\//g, '_').slice(1) || 'root';
    } catch {
      return 'unknown';
    }
  }
  /**
  * 获取资源类型
  */
  private getResourceType(url: string): string {
    const extension = url.split('.').pop()?.toLowerCase();
    if (["js",ts'].includes(extension || '')) return 'script';
    if (['css'].includes(extension || '')) return 'style';
    if (["png",jpg', "jpeg",gif', 'svg'].includes(extension || '')) return 'image';
    if (["woff",woff2', 'ttf'].includes(extension || '')) return 'font';
    return 'other';
  }
  /**
  * 清理旧指标
  */
  private trimMetrics(): void {
    const maxAge = 5 * 60 * 1000; // 5分钟
    const cutoff = Date.now() - maxAge;
    this.metrics = this.metrics.filter(metric => metric.timestamp > cutoff);
  }
}
// 导出单例实例
export const performanceMonitor = PerformanceMonitor.getInstance();