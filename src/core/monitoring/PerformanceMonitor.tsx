import { usePerformanceMonitor } from "../../hooks/usePerformanceMonitor";

import React from "react";

// 索克生活 - 性能监控系统 - 提供性能指标收集、分析、报告和优化建议

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  category: PerformanceCategory;
  tags?: Record<string, string>;
  threshold?: {
    warning: number;
    critical: number;
  };
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

export interface PerformanceReport {
  id: string;
  timestamp: number;
  duration: number;
  metrics: PerformanceMetric[];
  summary: {
    totalMetrics: number;
    warningCount: number;
    criticalCount: number;
    averageResponseTime: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  recommendations: string[];
  trends: {
    improving: string[];
    degrading: string[];
    stable: string[];
  };
}

export interface PerformanceThreshold {
  category: PerformanceCategory;
  metricName: string;
  warning: number;
  critical: number;
  unit: string;
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, PerformanceMetric[]> = new Map();
  private thresholds: Map<string, PerformanceThreshold> = new Map();
  private listeners: Array<(metric: PerformanceMetric) => void> = [];
  private isMonitoring: boolean = false;
  private monitoringInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.setupDefaultThresholds();
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // 开始性能监控
  public startMonitoring(intervalMs: number = 5000): void {
    if (this.isMonitoring) {
      return;
    }
    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.collectSystemMetrics();
    }, intervalMs);
  }

  // 停止性能监控
  public stopMonitoring(): void {
    if (!this.isMonitoring) {
      return;
    }
    this.isMonitoring = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  // 记录性能指标
  public recordMetric(
    name: string,
    value: number,
    category: PerformanceCategory,
    unit: string = "ms",
    tags?: Record<string, string>
  ): void {
    const metric: PerformanceMetric = {
      name,
      value,
      unit,
      timestamp: Date.now(),
      category,
      tags,
      threshold: this.getThreshold(name);
    };

    // 存储指标
    const key = `${category}_${name}`;
    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }
    const metricHistory = this.metrics.get(key)!;
    metricHistory.push(metric);

    // 保持最近1000条记录
    if (metricHistory.length > 1000) {
      metricHistory.shift();
    }

    // 检查阈值
    this.checkThreshold(metric);

    // 通知监听器
    this.notifyListeners(metric);
  }

  // 测量函数执行时间
  public async measureAsync<T>(
    name: string,
    category: PerformanceCategory,
    fn: () => Promise<T>,
    tags?: Record<string, string>
  ): Promise<T> {
    const startTime = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - startTime;
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "success"
      });
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "error"
      });
      throw error;
    }
  }

  // 测量同步函数执行时间
  public measure<T>(
    name: string,
    category: PerformanceCategory,
    fn: () => T,
    tags?: Record<string, string>
  ): T {
    const startTime = performance.now();
    try {
      const result = fn();
      const duration = performance.now() - startTime;
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "success"
      });
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      this.recordMetric(name, duration, category, "ms", {
        ...tags,
        status: "error"
      });
      throw error;
    }
  }

  // 生成性能报告
  public generateReport(timeRangeMs: number = 3600000): PerformanceReport {
    const now = Date.now();
    const startTime = now - timeRangeMs;
    const allMetrics: PerformanceMetric[] = [];
    let warningCount = 0;
    let criticalCount = 0;
    let totalResponseTime = 0;
    let responseTimeCount = 0;

    // 收集指定时间范围内的指标
    for (const [key, metricHistory] of this.metrics.entries()) {
      const recentMetrics = metricHistory.filter(;
        (m) => m.timestamp >= startTime;
      );
      allMetrics.push(...recentMetrics);

      // 统计警告和严重问题
      recentMetrics.forEach((metric) => {
        if (metric.threshold) {
          if (metric.value >= metric.threshold.critical) {
            criticalCount++;
          } else if (metric.value >= metric.threshold.warning) {
            warningCount++;
          }
        }

        // 计算平均响应时间
        if (
          metric.category === PerformanceCategory.NETWORK ||
          metric.category === PerformanceCategory.AGENT
        ) {
          totalResponseTime += metric.value;
          responseTimeCount++;
        }
      });
    }

    const averageResponseTime =
      responseTimeCount > 0 ? totalResponseTime / responseTimeCount : 0;

    // 生成趋势分析
    const trends = this.analyzeTrends(timeRangeMs);

    // 生成优化建议
    const recommendations = this.generateRecommendations(allMetrics);

    const report: PerformanceReport = {
      id: `report_${now}`,
      timestamp: now,
      duration: timeRangeMs,
      metrics: allMetrics,
      summary: {
        totalMetrics: allMetrics.length,
        warningCount,
        criticalCount,
        averageResponseTime,
        memoryUsage: this.getCurrentMemoryUsage(),
        cpuUsage: this.getCurrentCpuUsage();
      },
      recommendations,
      trends
    };

    return report;
  }

  // 私有方法实现
  private setupDefaultThresholds(): void {
    // 设置默认阈值
    this.setThreshold(
      "api_response",
      PerformanceCategory.NETWORK,
      1000,
      3000,
      "ms"
    );
    this.setThreshold("memory_usage", PerformanceCategory.MEMORY, 80, 95, "%");
    this.setThreshold("cpu_usage", PerformanceCategory.CPU, 70, 90, "%");
  }

  private setThreshold(
    metricName: string,
    category: PerformanceCategory,
    warning: number,
    critical: number,
    unit: string
  ): void {
    this.thresholds.set(metricName, {
      category,
      metricName,
      warning,
      critical,
      unit
    });
  }

  private getThreshold(
    metricName: string
  ): { warning: number; critical: number } | undefined {
    const threshold = this.thresholds.get(metricName);
    return threshold;
      ? { warning: threshold.warning, critical: threshold.critical };
      : undefined;
  }

  private checkThreshold(metric: PerformanceMetric): void {
    if (metric.threshold) {
      if (metric.value >= metric.threshold.critical) {
        console.warn(
          `Critical performance issue: ${metric.name} = ${metric.value}${metric.unit}`
        );
      } else if (metric.value >= metric.threshold.warning) {
        console.warn(
          `Performance warning: ${metric.name} = ${metric.value}${metric.unit}`
        );
      }
    }
  }

  private notifyListeners(metric: PerformanceMetric): void {
    this.listeners.forEach((listener) => {
      try {
        listener(metric);
      } catch (error) {
        console.error("Error in performance metric listener:", error);
      }
    });
  }

  private collectSystemMetrics(): void {
    // 收集系统指标的实现
    this.recordMetric(
      "memory_usage",
      this.getCurrentMemoryUsage(),
      PerformanceCategory.MEMORY,
      "%"
    );
    this.recordMetric(
      "cpu_usage",
      this.getCurrentCpuUsage(),
      PerformanceCategory.CPU,
      "%"
    );
  }

  private getCurrentMemoryUsage(): number {
    // 获取当前内存使用率的实现
    if (typeof performance !== "undefined" && (performance as any).memory) {
      const memory = (performance as any).memory;
      return (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100;
    }
    return 0;
  }

  private getCurrentCpuUsage(): number {
    // 获取当前CPU使用率的实现（简化版）
    return Math.random() * 100; // 实际实现需要使用系统API
  }

  private analyzeTrends(timeRangeMs: number): {
    improving: string[];
    degrading: string[];
    stable: string[];
  } {
    // 趋势分析的实现
    return {improving: [],degrading: [],stable: [];
    };
  }

  private generateRecommendations(metrics: PerformanceMetric[]): string[] {
    // 生成优化建议的实现
    const recommendations: string[] = [];

    // 分析指标并生成建议
    const highMemoryMetrics = metrics.filter(;
      (m) => m.category === PerformanceCategory.MEMORY && m.value > 80;
    );

    if (highMemoryMetrics.length > 0) {
      recommendations.push("考虑优化内存使用，清理不必要的对象引用");
    }

    return recommendations;
  }

  // 公共方法
  public addListener(listener: (metric: PerformanceMetric) => void): void {
    this.listeners.push(listener);
  }

  public removeListener(listener: (metric: PerformanceMetric) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  public getMetrics(category?: PerformanceCategory): PerformanceMetric[] {
    const allMetrics: PerformanceMetric[] = [];

    for (const [key, metricHistory] of this.metrics.entries()) {
      if (!category || key.startsWith(category)) {
        allMetrics.push(...metricHistory);
      }
    }

    return allMetrics.sort((a, b) => b.timestamp - a.timestamp);
  }

  public clearMetrics(): void {
    this.metrics.clear();
  }
}

// React组件
export const PerformanceMonitorComponent: React.FC = () => {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor({trackRender: true,trackMemory: false,warnThreshold: 100, // ms;
  });

  return <div>{// 性能监控UI组件}</div>;
};

export default PerformanceMonitor;
