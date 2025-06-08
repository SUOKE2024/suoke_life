import React, { useEffect, useRef, useState, useCallback } from 'react';
import { InteractionManager, Dimensions } from 'react-native';
// 性能指标接口
interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  networkLatency: number;
  frameDrops: number;
  interactionDelay: number;
  bundleSize: number;
  cacheHitRate: number;
  errorCount: number;
  warningCount: number;
  timestamp: number;
}
// 性能阈值配置
interface PerformanceThresholds {
  renderTime: number;
  memoryUsage: number;
  networkLatency: number;
  frameDrops: number;
  interactionDelay: number;
}
// 性能优化建议
interface OptimizationSuggestion {
  type: 'render' | 'memory' | 'network' | 'interaction' | 'bundle';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  action: string;
  impact: string;
}
// 性能监控配置
interface PerformanceMonitorConfig {
  enabled: boolean;
  sampleRate: number;
  thresholds: PerformanceThresholds;
  reportInterval: number;
  maxSamples: number;
  enableDetailedLogging: boolean;
}
// 默认配置
const DEFAULT_CONFIG: PerformanceMonitorConfig = {,
  enabled: true,
  sampleRate: 0.1, // 10% 采样率
  thresholds: {,
  renderTime: 16, // 16ms (60fps)
    memoryUsage: 100 * 1024 * 1024, // 100MB;
    networkLatency: 1000, // 1s;
    frameDrops: 5,
    interactionDelay: 100, // 100ms;
  },
  reportInterval: 30000, // 30秒
  maxSamples: 100,
  enableDetailedLogging: false,
};
// 性能数据收集器
class PerformanceCollector {
  private static instance: PerformanceCollector;
  private metrics: PerformanceMetrics[] = [];
  private config: PerformanceMonitorConfig;
  private frameDropCounter = 0;
  private lastFrameTime = 0;
  private networkRequests: Map<string, number> = new Map();
  private errorCount = 0;
  private warningCount = 0;
  constructor(config: PerformanceMonitorConfig = DEFAULT_CONFIG) {
    this.config = config;
    this.setupGlobalErrorHandling();
  }
  static getInstance(config?: PerformanceMonitorConfig): PerformanceCollector {
    if (!PerformanceCollector.instance) {
      PerformanceCollector.instance = new PerformanceCollector(config);
    }
    return PerformanceCollector.instance;
  }
  private setupGlobalErrorHandling(): void {
    // 监听全局错误
    const originalError = console.error;
    console.error = (...args) => {
      this.errorCount++;
      originalError.apply(console, args);
    };
    const originalWarn = console.warn;
    console.warn = (...args) => {
      this.warningCount++;
      originalWarn.apply(console, args);
    };
  }
  // 记录渲染时间
  recordRenderTime(componentName: string, renderTime: number): void {
    if (!this.shouldSample()) return;
    const metric: PerformanceMetrics = {
      renderTime,
      memoryUsage: this.getMemoryUsage(),
      networkLatency: this.getAverageNetworkLatency(),
      frameDrops: this.frameDropCounter,
      interactionDelay: 0,
      bundleSize: 0,
      cacheHitRate: 0,
      errorCount: this.errorCount,
      warningCount: this.warningCount,
      timestamp: Date.now(),
    };
    this.addMetric(metric);
    if (this.config.enableDetailedLogging) {
      console.log(`[Performance] ${componentName} render time: ${renderTime}ms`);
    }
  }
  // 记录网络请求
  recordNetworkRequest(url: string, startTime: number, endTime: number): void {
    const latency = endTime - startTime;
    this.networkRequests.set(url, latency);
    if (latency > this.config.thresholds.networkLatency) {
      console.warn(`[Performance] Slow network request: ${url} (${latency}ms)`);
    }
  }
  // 记录交互延迟
  recordInteractionDelay(interactionType: string, delay: number): void {
    if (!this.shouldSample()) return;
    if (delay > this.config.thresholds.interactionDelay) {
      console.warn(`[Performance] Slow interaction: ${interactionType} (${delay}ms)`);
    }
  }
  // 记录帧丢失
  recordFrameDrop(): void {
    this.frameDropCounter++;
  }
  // 获取内存使用情况
  private getMemoryUsage(): number {
    // React Native 中获取内存使用情况的方法有限
    // 这里返回一个估算值
    return (performance as any)?.memory?.usedJSHeapSize || 0;
  }
  // 获取平均网络延迟
  private getAverageNetworkLatency(): number {
    if (this.networkRequests.size === 0) return 0;
        const latencies = Array.from(this.networkRequests.values());
    return latencies.reduce(sum, latency) => sum + latency, 0) / latencies.length;
  }
  // 判断是否应该采样
  private shouldSample(): boolean {
    return this.config.enabled && Math.random() < this.config.sampleRate;
  }
  // 添加性能指标
  private addMetric(metric: PerformanceMetrics): void {
    this.metrics.push(metric);
        // 限制样本数量
    if (this.metrics.length > this.config.maxSamples) {
      this.metrics.shift();
    }
  }
  // 获取性能报告
  getPerformanceReport(): {
    metrics: PerformanceMetrics[],
  averages: Partial<PerformanceMetrics>;
    suggestions: OptimizationSuggestion[];
  } {
    const averages = this.calculateAverages();
    const suggestions = this.generateOptimizationSuggestions(averages);
    return {
      metrics: this.metrics,
      averages,
      suggestions,
    };
  }
  // 计算平均值
  private calculateAverages(): Partial<PerformanceMetrics> {
    if (this.metrics.length === 0) return {};
    const sums = this.metrics.reduce(acc, metric) => ({
        renderTime: acc.renderTime + metric.renderTime,
        memoryUsage: acc.memoryUsage + metric.memoryUsage,
        networkLatency: acc.networkLatency + metric.networkLatency,
        frameDrops: acc.frameDrops + metric.frameDrops,
        interactionDelay: acc.interactionDelay + metric.interactionDelay,
        errorCount: acc.errorCount + metric.errorCount,
        warningCount: acc.warningCount + metric.warningCount,
      }),
      {
        renderTime: 0,
        memoryUsage: 0,
        networkLatency: 0,
        frameDrops: 0,
        interactionDelay: 0,
        errorCount: 0,
        warningCount: 0,
      }
    );
    const count = this.metrics.length;
    return {
      renderTime: sums.renderTime / count,
      memoryUsage: sums.memoryUsage / count,
      networkLatency: sums.networkLatency / count,
      frameDrops: sums.frameDrops / count,
      interactionDelay: sums.interactionDelay / count,
      errorCount: sums.errorCount / count,
      warningCount: sums.warningCount / count,
    };
  }
  // 生成优化建议
  private generateOptimizationSuggestions(averages: Partial<PerformanceMetrics>): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];
    // 渲染性能建议
    if (averages.renderTime && averages.renderTime > this.config.thresholds.renderTime) {
      suggestions.push({
      type: "render",
      severity: averages.renderTime > this.config.thresholds.renderTime * 2 ? 'high' : 'medium',
        message: `平均渲染时间 ${averages.renderTime.toFixed(2)}ms 超过阈值 ${this.config.thresholds.renderTime}ms`,
        action: '考虑使用 React.memo、useMemo 或 useCallback 优化组件渲染',
        impact: '提升用户界面响应速度和流畅度',
      });
    }
    // 内存使用建议
    if (averages.memoryUsage && averages.memoryUsage > this.config.thresholds.memoryUsage) {
      suggestions.push({
      type: "memory",
      severity: averages.memoryUsage > this.config.thresholds.memoryUsage * 2 ? 'critical' : 'high',
        message: `平均内存使用 ${(averages.memoryUsage / 1024 / 1024).toFixed(2)}MB 超过阈值`,
        action: '检查内存泄漏，优化图片加载，清理未使用的引用',
        impact: '减少应用崩溃风险，提升稳定性',
      });
    }
    // 网络延迟建议
    if (averages.networkLatency && averages.networkLatency > this.config.thresholds.networkLatency) {
      suggestions.push({
      type: "network",
      severity: 'medium',
        message: `平均网络延迟 ${averages.networkLatency.toFixed(2)}ms 较高`,
        action: '实施请求缓存、数据预加载或使用 CDN',
        impact: '提升数据加载速度和用户体验',
      });
    }
    // 交互延迟建议
    if (averages.interactionDelay && averages.interactionDelay > this.config.thresholds.interactionDelay) {
      suggestions.push({
      type: "interaction",
      severity: 'medium',
        message: `平均交互延迟 ${averages.interactionDelay.toFixed(2)}ms 较高`,
        action: '优化事件处理器，使用防抖或节流技术',
        impact: '提升用户交互响应速度',
      });
    }
    return suggestions;
  }
  // 清理数据
  clear(): void {
    this.metrics = [];
    this.frameDropCounter = 0;
    this.networkRequests.clear();
    this.errorCount = 0;
    this.warningCount = 0;
  }
}
// 增强的性能监控Hook;
export const useEnhancedPerformanceMonitor = ()
  componentName: string,
  config: Partial<PerformanceMonitorConfig> = {}
) => {
  const [performanceData, setPerformanceData] = useState<{
    metrics: PerformanceMetrics[],
  averages: Partial<PerformanceMetrics>;
    suggestions: OptimizationSuggestion[];
  }>({ metrics: [], averages: {}, suggestions: [] });
  const renderStartTime = useRef<number>(0);
  const collector = useRef<PerformanceCollector>();
  const reportTimer = useRef<NodeJS.Timeout>();
  // 初始化收集器
  useEffect(() => {
    const mergedConfig = { ...DEFAULT_CONFIG, ...config };
    collector.current = PerformanceCollector.getInstance(mergedConfig);
  }, [config]);
  // 记录渲染开始时间
  const startRenderMeasurement = useCallback() => {
    renderStartTime.current = Date.now();
  }, []);
  // 记录渲染结束时间
  const endRenderMeasurement = useCallback() => {
    if (renderStartTime.current > 0 && collector.current) {
      const renderTime = Date.now() - renderStartTime.current;
      collector.current.recordRenderTime(componentName, renderTime);
      renderStartTime.current = 0;
    }
  }, [componentName]);
  // 记录网络请求
  const recordNetworkRequest = useCallback(url: string, startTime: number, endTime: number) => {
    collector.current?.recordNetworkRequest(url, startTime, endTime);
  }, []);
  // 记录交互延迟
  const recordInteraction = useCallback(interactionType: string, startTime: number) => {
    const delay = Date.now() - startTime;
    collector.current?.recordInteractionDelay(interactionType, delay);
  }, []);
  // 获取性能报告
  const getPerformanceReport = useCallback() => {
    return collector.current?.getPerformanceReport() || { metrics: [], averages: {}, suggestions: [] };
  }, []);
  // 定期更新性能数据
  useEffect(() => {
    const mergedConfig = { ...DEFAULT_CONFIG, ...config };
        if (mergedConfig.enabled) {
      reportTimer.current = setInterval() => {
        const report = getPerformanceReport();
        setPerformanceData(report);
      }, mergedConfig.reportInterval);
    }
    return () => {
      if (reportTimer.current) {
        clearInterval(reportTimer.current);
      }
    };
  }, [config, getPerformanceReport]);
  // 组件挂载时开始测量
  useEffect(() => {
    startRenderMeasurement();
        // 使用 InteractionManager 确保在交互完成后测量
    const handle = InteractionManager.runAfterInteractions() => {
      endRenderMeasurement();
    });
    return () => {
      handle.cancel();
    };
  }, [startRenderMeasurement, endRenderMeasurement]);
  return {
    performanceData,
    startRenderMeasurement,
    endRenderMeasurement,
    recordNetworkRequest,
    recordInteraction,
    getPerformanceReport,
    clearData: () => collector.current?.clear(),
  };
};
// 性能监控装饰器
export const withPerformanceMonitoring = <P extends object>()
  WrappedComponent: React.ComponentType<P>,
  componentName?: string;
) => {
  const MonitoredComponent = (props: P) => {
    const name = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Unknown';
    const { startRenderMeasurement, endRenderMeasurement } = useEnhancedPerformanceMonitor(name);
    useEffect(() => {
      startRenderMeasurement();
      return () => {
        endRenderMeasurement();
      };
    }, [startRenderMeasurement, endRenderMeasurement]);
    return React.createElement(WrappedComponent, props);
  };
  MonitoredComponent.displayName = `withPerformanceMonitoring(${componentName || 'Component'})`;
  return MonitoredComponent;
};
export type { PerformanceMetrics, OptimizationSuggestion, PerformanceMonitorConfig };