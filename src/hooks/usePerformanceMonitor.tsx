import { log } from '../services/Logger';
import React from 'react';
import { useEffect, useRef, useCallback, useState } from 'react';
interface PerformanceConfig {
  trackRender?: boolean;
  trackMemory?: boolean;
  warnThreshold?: number; // ms;
  sampleRate?: number; // 0-1;
}
interface PerformanceMetrics {
  renderTime: number;
  memoryUsage?: number;
  componentName: string;
  timestamp: number;
}
interface UsePerformanceMonitorReturn {
  recordRender: () => void;
  getMetrics: () => PerformanceMetrics[];
  clearMetrics: () => void;
  averageRenderTime: number;
}
export const usePerformanceMonitor = (
  componentName: string,
  config: PerformanceConfig = {},
): UsePerformanceMonitorReturn => {
  const {
    trackRender = true,
    trackMemory = false,
    warnThreshold = 16, // 60fps = 16.67ms per frame;
    sampleRate = 1.0,
  } = config;
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([]);
  const metricsRef = useRef<PerformanceMetrics[]>([]);
  // 记录渲染开始时间
  useEffect() => {
    if (trackRender && Math.random() < sampleRate) {
      renderStartTime.current = performance.now();
    }
  });
  // 记录渲染结束时间
  useEffect() => {
    if (trackRender && renderStartTime.current > 0) {
      const renderTime = performance.now() - renderStartTime.current;
      const metric: PerformanceMetrics = {
        renderTime,
        componentName,
        timestamp: Date.now(),
      };
      // 添加内存使用信息（如果支持）
      if (trackMemory && 'memory' in performance) {
        const memoryInfo = (performance as any).memory;
        metric.memoryUsage = memoryInfo.usedJSHeapSize;
      }
      // 更新指标
      metricsRef.current = [...metricsRef.current.slice(-99), metric]; // 保留最近100条记录
      setMetrics(metricsRef.current);
      // 性能警告
      if (renderTime > warnThreshold) {
        console.warn(
          `🐌 Performance Warning: ${componentName} render took ${renderTime.toFixed(2)}ms (threshold: ${warnThreshold}ms)`,
        );
      }
      // 重置计时器
      renderStartTime.current = 0;
    }
  });
  // 手动记录渲染
  const recordRender = useCallback() => {
    if (trackRender) {
      const renderTime = performance.now() - (renderStartTime.current || performance.now());
      const metric: PerformanceMetrics = {,
  renderTime: Math.max(0, renderTime),
        componentName,
        timestamp: Date.now(),
      };
      if (trackMemory && 'memory' in performance) {
        const memoryInfo = (performance as any).memory;
        metric.memoryUsage = memoryInfo.usedJSHeapSize;
      }
      metricsRef.current = [...metricsRef.current.slice(-99), metric];
      setMetrics(metricsRef.current);
    }
  }, [componentName, trackRender, trackMemory]);
  // 获取指标
  const getMetrics = useCallback() => {
    return metricsRef.current;
  }, []);
  // 清除指标
  const clearMetrics = useCallback() => {
    metricsRef.current = [];
    setMetrics([]);
  }, []);
  // 计算平均渲染时间
  const averageRenderTime = metrics.length > 0;
    ? metrics.reduce(sum, metric) => sum + metric.renderTime, 0) / metrics.length;
    : 0;
  // 开发环境下的性能报告
  useEffect() => {
    if (__DEV__ && metrics.length > 0 && metrics.length % 10 === 0) {
      const recentMetrics = metrics.slice(-10);
      const avgRenderTime = recentMetrics.reduce(sum, m) => sum + m.renderTime, 0) / 10;
      const maxRenderTime = Math.max(...recentMetrics.map(m => m.renderTime));
      console.log(`📊 Performance Report for ${componentName}:`, {
        averageRenderTime: `${avgRenderTime.toFixed(2)}ms`,
        maxRenderTime: `${maxRenderTime.toFixed(2)}ms`,
        totalSamples: metrics.length,
        memoryUsage: trackMemory && 'memory' in performance;
          ? `${(performance as any).memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB`
          : 'N/A',
      });
    }
  }, [metrics, componentName, trackMemory]);
  return {
    recordRender,
    getMetrics,
    clearMetrics,
    averageRenderTime,
  };
};
// 高阶组件版本
export const withPerformanceMonitor = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName: string,
  config: PerformanceConfig = {},
) => {
  const WithPerformanceMonitor = (props: P) => {
    usePerformanceMonitor(componentName, config);
    return <WrappedComponent {...props} />;
  };
  WithPerformanceMonitor.displayName = `withPerformanceMonitor(${WrappedComponent.displayName || WrappedComponent.name})`;
  return WithPerformanceMonitor;
};