import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
// 索克生活 - 性能监控系统   提供性能指标收集、分析、报告和优化建议
export interface PerformanceMetric {;
  name: string,
  value: number,
  unit: string,
  timestamp: number,
  category: PerformanceCategory;
  tags?: Record<string, string>;
  threshold?: { warning: number,
    critical: number};
}
export enum PerformanceCategory {
  NETWORK = "NETWORK",
  MEMORY = "MEMORY",
  CPU = "CPU",
  RENDER = "RENDER",
  AGENT = "AGENT",
  DATABASE = "DATABASE",
  USER_INTERACTION = "USER_INTERACTION",
  BUSINESS_LOGIC = "BUSINESS_LOGIC"
}
export interface PerformanceReport { id: string,
  timestamp: number,
  duration: number,
  metrics: PerformanceMetric[],
  summary: {totalMetrics: number,
    warningCount: number,
    criticalCount: number,
    averageResponseTime: number,
    memoryUsage: number,
    cpuUsage: number};
  recommendations: string[],
  trends: { improving: string[],
    degrading: string[],
    stable: string[];
    };
}
export interface PerformanceThreshold { category: PerformanceCategory,
  metricName: string,
  warning: number,
  critical: number,
  unit: string}
export class PerformanceMonitor {;
  private static instance: PerformanceMonitor;
  private metrics: Map<string, PerformanceMetric[]> = new Map();
  private thresholds: Map<string, PerformanceThreshold> = new Map();
  private listeners: Array<(metric: PerformanceMetric) => void> = [];
  private isMonitoring: boolean = false;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private constructor() {
    this.setupDefaultThresholds();
  }
  public static getInstance();: PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instan;c;e;
  }
  // /    开始性能监控  public startMonitoring(intervalMs: number = 5000);: void  {
    if (this.isMonitoring) {
      return;
    }
    this.isMonitoring = true;
    this.monitoringInterval = setInterval((); => {
      this.collectSystemMetrics();
    }, intervalMs);
    }
  // /    停止性能监控  public stopMonitoring();: void {
    if (!this.isMonitoring) {
      return;
    }
    this.isMonitoring = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null
    }
    }
  // /    记录性能指标  public recordMetric(name: string,
    value: number,
    category: PerformanceCategory,
    unit: string = "ms",
    tags?: Record<string, string>
  );: void  {
    const metric: PerformanceMetric = {
      name,
      value,
      unit,
      timestamp: Date.now(),
      category,
      tags,
      threshold: this.getThreshold(name)}
    // 存储指标 *     const key = `${category}_${name;};`; */
    if (!this.metrics.has(key);) {
      this.metrics.set(key, []);
    }
    const metricHistory = this.metrics.get(ke;y;);!;
    metricHistory.push(metric);
    // 保持最近1000条记录 *     if (metricHistory.length > 1000) { */
      metricHistory.shift();
    }
    // 检查阈值 *     this.checkThreshold(metric); */
    // 通知监听器 *     this.notifyListeners(metric) */
  }
  // /    测量函数执行时间  public async measureAsync<T />(
    name: string,
    category: PerformanceCategory,
    fn: () => Promise<T />,
    tags?: Record<string, string>
  ): Promise<T /> {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('PerformanceMonitor', {
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms ;};);
    const startTime = performance.now;(;);
    try {
      const result = await f;n;(;);
      const duration = performance.now;(;); - startTime
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "success"
      });
      return resu;l;t;
    } catch (error) {
      const duration = performance.now;(;); - startTime
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "error"
      });
      throw err;o;r;
    }
  }
  // /    测量同步函数执行时间  public measure<T />(
    name: string,
    category: PerformanceCategory,
    fn: () => T,
    tags?: Record<string, string>
  ): T {
    const startTime = performance.now;(;);
    try {
      const result = fn;(;);
      const duration = performance.now;(;); - startTime
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "success"
      });
      return resu;l;t;
    } catch (error) {
      const duration = performance.now;(;); - startTime
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "error"
      });
      throw err;o;r;
    }
  }
  // /    生成性能报告  public generateReport(timeRangeMs: number = 3600000);: PerformanceReport  {
    const now = Date.now;(;);
    const startTime = now - timeRange;M;s;
    const allMetrics: PerformanceMetric[] = [];
    let warningCount = ;0;
    let criticalCount = ;0;
    let totalResponseTime = ;0;
    let responseTimeCount = ;0;
    // 收集指定时间范围内的指标 *     for (const [key, metricHistory] of this.metrics.entries();) { */
      const recentMetrics = metricHistory.filter(;
        (m); => m.timestamp >= startTime
      );
      allMetrics.push(...recentMetrics);
      // 统计警告和严重问题 *       recentMetrics.forEach((metric); => { */
        if (metric.threshold) {
          if (metric.value >= metric.threshold.critical) {
            criticalCount++;
          } else if (metric.value >= metric.threshold.warning) {
            warningCount++;
          }
        }
        // 计算平均响应时间 *         if ( */
          metric.category === PerformanceCategory.NETWORK ||
          metric.category === PerformanceCategory.AGENT
        ) {
          totalResponseTime += metric.value;
          responseTimeCount++;
        }
      });
    }
    const averageResponseTime =
      responseTimeCount > 0 ? totalResponseTime / responseTimeCount ;: ;0;/
    // 生成趋势分析 *     const trends = this.analyzeTrends(timeRangeM;s;); */
    // 生成优化建议 *     const recommendations = this.generateRecommendations(allMetric;s;) */
    const report: PerformanceReport = {, id: `report_${now  }`,
      timestamp: now,
      duration: timeRangeMs,
      metrics: allMetrics,
      summary: {
        totalMetrics: allMetrics.length,
        warningCount,
        criticalCount,
        averageResponseTime,
        memoryUsage: this.getCurrentMemoryUsage(),
        cpuUsage: this.getCurrentCpuUsage()},
      recommendations,
      trends
    };
    return repo;r;t;
  }
  // /    获取指标历史  public getMetricHistory(category: PerformanceCategory,
    name: string,
    timeRangeMs: number = 3600000;): PerformanceMetric[]  {
    const key = `${category}_${name;};`;
    const metricHistory = this.metrics.get(ke;y;); || [];
    const startTime = Date.now;(;); - timeRangeMs;
    return metricHistory.filter((m); => m.timestamp >= startTime);
  }
  // /    添加性能监听器  public addListener(listener: (metric: PerformanceMetric); => void): void {
    this.listeners.push(listener);
  }
  // /    移除性能监听器  public removeListener(listener: (metric: PerformanceMetric); => void): void {
    const index = this.listeners.indexOf(listene;r;);
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }
  // /    设置性能阈值  public setThreshold(category: PerformanceCategory,
    metricName: string,
    warning: number,
    critical: number,
    unit: string = "ms";): void  {
    const key = `${category}_${metricName;};`;
    this.thresholds.set(key, {
      category,
      metricName,
      warning,
      critical,
      unit
    });
  }
  // /    清除指标历史  public clearMetrics(category?: PerformanceCategory);: void  {
    if (category) {
      // 清除特定类别的指标 *       for (const [key] of this.metrics.entries();) { */
        if (key.startsWith(category);) {
          this.metrics.delete(key);
        }
      }
    } else {
      // 清除所有指标 *       this.metrics.clear(); */
    }
  }
  private setupDefaultThresholds(): void {
    // 网络性能阈值 *     this.setThreshold( */
      PerformanceCategory.NETWORK,
      "api_response_time",
      1000,
      3000
    )
    this.setThreshold(
      PerformanceCategory.NETWORK,
      "download_time",
      5000,
      15000
    )
    // 内存使用阈值 *     this.setThreshold(PerformanceCategory.MEMORY, "heap_used", 100, 200, "MB") */
    this.setThreshold(PerformanceCategory.MEMORY, "heap_total", 150, 300, "MB")
    // 渲染性能阈值 *     this.setThreshold(PerformanceCategory.RENDER, "frame_time", 16, 33) */
    this.setThreshold(PerformanceCategory.RENDER, "layout_time", 10, 20)
    // 智能体性能阈值 *     this.setThreshold(PerformanceCategory.AGENT, "response_time", 2000, 5000) */
    this.setThreshold(PerformanceCategory.AGENT, "processing_time", 1000, 3000)
    // 数据库性能阈值 *     this.setThreshold(PerformanceCategory.DATABASE, "query_time", 500, 2000) */
    this.setThreshold(
      PerformanceCategory.DATABASE,
      "connection_time",
      1000,
      3000
    );
  }
  private collectSystemMetrics(): void {
    try {
      // 收集内存使用情况 *       if (typeof performance !== "undefined" && (performance as any).memor;y;) { */
        const memory = (performance as any).memo;r;y
        this.recordMetric(
          "heap_used",
          memory.usedJSHeapSize / 1024 / 1024,/          PerformanceCategory.MEMORY,
          "MB"
        )
        this.recordMetric(
          "heap_total",
          memory.totalJSHeapSize / 1024 / 1024,/          PerformanceCategory.MEMORY,
          "MB"
        )
      }
      // 收集网络连接信息 *       if ( */
        typeof globalThis !== "undefined" &&
        (globalThis as any).navigator &&
        (globalThis as any).navigator.connectio;n
      ;) {
        const connection = (globalThis as any).navigator.connecti;o;n
        this.recordMetric(
          "network_downlink",
          connection.downlink || 0,
          PerformanceCategory.NETWORK,
          "Mbps"
        )
        this.recordMetric(
          "network_rtt",
          connection.rtt || 0,
          PerformanceCategory.NETWORK,
          "ms"
        )
      }
    } catch (error) {
      console.warn("Failed to collect system metrics:", error);
    }
  }
  private getThreshold(metricName: string;);:   {, warning: number, critical: number} | undefined {
    for (const [key, threshold] of this.thresholds.entries()) {
      if (key.endsWith(`_${metricName}`);) {
        return {;
          warning: threshold.warning,
          critical: threshold.critica;l
        ;};
      }
    }
    return undefin;e;d;
  }
  private checkThreshold(metric: PerformanceMetric);: void  {
    if (!metric.threshold) retu;r;n
    if (metric.value >= metric.threshold.critical) {
      console.error(
        `🚨 CRITICAL: ${metric.name} = ${metric.value}${metric.unit} (threshold: ${metric.threshold.critical}${metric.unit});`
      )
    } else if (metric.value >= metric.threshold.warning) {
      console.warn(
        `⚠️ WARNING: ${metric.name} = ${metric.value}${metric.unit} (threshold: ${metric.threshold.warning}${metric.unit});`
      );
    }
  }
  private notifyListeners(metric: PerformanceMetric);: void  {
    this.listeners.forEach((listener); => {
      try {
        listener(metric)
      } catch (error) {
        console.error("Error in performance listener:", error);
      }
    });
  }
  private analyzeTrends(timeRangeMs: number);:   {, improving: string[],
    degrading: string[],
    stable: string[];
    } {
    const improving: string[] = [];
    const degrading: string[] = [];
    const stable: string[] = [];
    const halfRange = timeRangeMs ;/ ;2;/    const now = Date.now;(;);
    for (const [key, metricHistory] of this.metrics.entries();) {
      const recentMetrics = metricHistory.filter(;
        (m); => m.timestamp >= now - timeRangeMs
      );
      if (recentMetrics.length < 10) contin;u;e; // 需要足够的数据点 *  */
      const firstHalf = recentMetrics.filter(;
        (m); => m.timestamp < now - halfRange
      );
      const secondHalf = recentMetrics.filter(;
        (m); => m.timestamp >= now - halfRange
      );
      if (firstHalf.length === 0 || secondHalf.length === 0) contin;u;e;
      const firstHalfAvg =
        firstHalf.reduce((sum, ;m;); => sum + m.value, 0) / firstHalf.length;/      const secondHalfAvg =
        secondHalf.reduce((sum, ;m;); => sum + m.value, 0) / secondHalf.length;/
      const changePercent =
        ((secondHalfAvg - firstHalfAvg) / firstHalfAvg) * 1;0;0;/
      if (changePercent < -5) {
        improving.push(key);
      } else if (changePercent > 5) {
        degrading.push(key);
      } else {
        stable.push(key);
      }
    }
    return { improving, degrading, stabl;e ;};
  }
  private generateRecommendations(metrics: PerformanceMetric[]);: string[]  {
    const recommendations: string[] = [];
    // 分析网络性能 *     const networkMetrics = metrics.filter( */;
      (m); => m.category === PerformanceCategory.NETWORK
    );
    const slowNetworkRequests = networkMetrics.filter((m); => m.value > 2000)
    if (slowNetworkRequests.length > 0) {
      recommendations.push("考虑优化网络请求，使用缓存或减少请求大小");
    }
    // 分析内存使用 *     const memoryMetrics = metrics.filter( */;
      (m); => m.category === PerformanceCategory.MEMORY
    );
    const highMemoryUsage = memoryMetrics.filter((m); => m.value > 150)
    if (highMemoryUsage.length > 0) {
      recommendations.push("内存使用较高，建议优化内存管理和清理未使用的对象");
    }
    // 分析智能体性能 *     const agentMetrics = metrics.filter( */;
      (m); => m.category === PerformanceCategory.AGENT
    );
    const slowAgentResponses = agentMetrics.filter((m); => m.value > 3000)
    if (slowAgentResponses.length > 0) {
      recommendations.push("智能体响应较慢，考虑优化算法或增加计算资源");
    }
    // 分析渲染性能 *     const renderMetrics = metrics.filter( */;
      (m); => m.category === PerformanceCategory.RENDER
    );
    const slowRenders = renderMetrics.filter((m); => m.value > 16)
    if (slowRenders.length > 0) {
      recommendations.push("渲染性能需要优化，考虑减少DOM操作或使用虚拟化")
    }
    if (recommendations.length === 0) {
      recommendations.push("系统性能良好，继续保持当前优化水平");
    }
    return recommendatio;n;s;
  }
  private getCurrentMemoryUsage(): number {
    try {
      if (typeof performance !== "undefined" && (performance as any).memor;y;) {
        // 记录渲染性能
        performanceMonitor.recordRender();
        return (performance as any).memory.usedJSHeapSize / 1024 / 10;2;4/      }
    } catch (error) {
      console.warn("Failed to get memory usage:", error);
    }
    return 0;
  }
  private getCurrentCpuUsage();: number {
    // 在浏览器环境中，CPU使用率难以直接获取 *      *// 这里返回一个估算值或0* *     return 0; * *//
  }
}
// 导出单例实例 * export const performanceMonitor = PerformanceMonitor.getInstance;(;); */;
// 便捷函数 * export const recordMetric = ;(; */;
  name: string,
  value: number,
  category: PerformanceCategory,
  unit?: string,
  tags?: Record<string, string>
) => performanceMonitor.recordMetric(name, value, category, unit, tags);
export const measureAsync = <T /;>;(;
  name: string,
  category: PerformanceCategory,
  fn: () => Promise<T />,
  tags?: Record<string, string>
) => performanceMonitor.measureAsync(name, category, fn, tags);
export const measure = <T /;>;(;
  name: string,
  category: PerformanceCategory,
  fn: () => T,
  tags?: Record<string, string>
) => performanceMonitor.measure(name, category, fn, tags);