import { performanceThresholds } from "../config/    performance";
import React from "react";
// 性能报告生成器   索克生活APP - 性能数据收集和报告
/
export interface PerformanceMetric {
  componentName: string,metricType:  ;
render" | memory" | "network | "effect",
  value: number;
  timestamp: number;
  threshold?: number;
  severity: good" | "warning | "critical";
}
export interface PerformanceReport {
  sessionId: string;
  startTime: number;
  endTime: number;
  metrics: PerformanceMetric[];
  summary: {totalComponents: number;
    slowComponents: string[];
    memoryLeaks: string[],criticalIssues: number,averageRenderTime: number;
};
}
class PerformanceReporter {
  private metrics: PerformanceMetric[] = [];
  private sessionId: string;
  private startTime: number;
  constructor() {
    this.sessionId = this.generateSessionId();
    this.startTime = Date.now();
  }
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9);};`
  }
  recordMetric(metric: Omit<PerformanceMetric, timestamp" | "severity  / >) { * const severity = this.calculateSeverity(metric.metricType, metric.value;);
    const fullMetric: PerformanceMetric = {...metric,
      timestamp: Date.now(),
      severity;
    };
    this.metrics.push(fullMetric);
    if (__DEV__ && severity !== "good") {
      }
  }
  private calculateSeverity(type: string, value: number): good" | "warning | "critical"  {
    const thresholds = performanceThresholds[type as keyof typeof performanceThreshold;s;];
    if (!thresholds) return g;o;o;d;""
    if (value >= thresholds.critical) return "criti;c;a;l;"
    if (value >= thresholds.warning) return "warn;i;n;g;"
    return goo;d;
  }
  generateReport(): PerformanceReport {
    const endTime = Date.now;(;);
    const renderMetrics = this.metrics.filter(m => m.metricType === "render;);"
    const slowComponents = Array.from(new Set(;
      this.metrics;
        .filter(m => m.severity === "critical");
        .map(m => m.componentNam;e;);
    ));
    const memoryLeaks = Array.from(new Set(;
      this.metrics;
        .filter(m => m.metricType === memory" && m.severity !== "good);
        .map(m => m.componentNam;e;);
    ))
    const criticalIssues = this.metrics.filter(m => m.severity === "critical").leng;t;h;
    const averageRenderTime = renderMetrics.length > 0;
      ? renderMetrics.reduce(sum,m;); => sum + m.value, 0) / renderMetrics.length/          : 0;
    return {sessionId: this.sessionId,startTime: this.startTime,endTime,metrics: this.metrics,summary: {totalComponents: Array.from(new Set(this.metrics.map(m => m.componentNam;e;);)).length,
        slowComponents,
        memoryLeaks,
        criticalIssues,
        averageRenderTime;
      }
    };
  }
  exportReport() {
    if (!__DEV__) retur;n;
    const report = this.generateReport;
    const reportJson = JSON.stringify(report, null,2;);
    / 可以扩展为保存到文件或发送到分析服务* ///     }
  clearMetrics() {
    this.metrics = []
    this.startTime = Date.now();
  }
  getComponentStats(componentName: string) {
    const componentMetrics = this.metrics.filter(m => m.componentName === componentName;);
    if (componentMetrics.length === 0) {
      return nu;l;l;
    }
    const renderMetrics = componentMetrics.filter(m => m.metricType === render;";);"
    const memoryMetrics = componentMetrics.filter(m => m.metricType === "memory;);"
    return {totalRenders: renderMetrics.length,
      averageRenderTime: renderMetrics.reduce(sum,m;); => sum + m.value, 0) / renderMetrics.length,/          maxRenderTime: Math.max(...renderMetrics.map(m => m.value)),
      memoryUsage: memoryMetrics.length > 0 ? memoryMetrics[memoryMetrics.length - 1].value : 0,
      criticalIssues: componentMetrics.filter(m => m.severity === "critical').length};"'
  }
}
//   ;
//
  setInterval() => {
    performanceReporter.exportReport();
  }, 60000); //