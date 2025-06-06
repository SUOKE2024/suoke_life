import { log } from "../services/Logger";

import React from "react";
import { useEffect, useRef, useState } from "react";

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage?: number;
  componentName: string;
}

interface UsePerformanceMonitorOptions {
  componentName: string;
  enableMemoryMonitoring?: boolean;
  threshold?: number; // 渲染时间阈值(ms)
}

export const usePerformanceMonitor = (;
  options: UsePerformanceMonitorOptions
) => {
  const {
    componentName,
    enableMemoryMonitoring = false,
    threshold = 16
  } = options;
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);

  useEffect(() => {
    renderStartTime.current = performance.now();
  });

  useEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;
    const newMetrics: PerformanceMetrics = {
      renderTime,
      componentName
    };

    // 获取内存使用情况（如果支持）
    if (enableMemoryMonitoring && "memory" in performance) {
      newMetrics.memoryUsage = (performance as any).memory?.usedJSHeapSize;
    }

    setMetrics(newMetrics);

    // 如果渲染时间超过阈值，记录警告
    if (renderTime > threshold) {
      log.warn(
        `组件 ${componentName} 渲染时间过长: ${renderTime.toFixed(2)}ms`,
        {
          renderTime,
          threshold,
          memoryUsage: newMetrics.memoryUsage
        }
      );
    }

    // 在开发环境记录性能指标
    if (process.env.NODE_ENV === "development") {
      log.debug(`组件 ${componentName} 性能指标`, newMetrics);
    }
  });

  return metrics;
};

// 高阶组件版本
export const withPerformanceMonitor = <P extends object>(;
  WrappedComponent: React.ComponentType<P>,
  options: UsePerformanceMonitorOptions
) => {
  const WithPerformanceMonitor = (props: P) => {usePerformanceMonitor(options);
    return <WrappedComponent {...props} />;
  };

  WithPerformanceMonitor.displayName = `withPerformanceMonitor(${
    WrappedComponent.displayName || WrappedComponent.name
  })`;
  return WithPerformanceMonitor;
};
