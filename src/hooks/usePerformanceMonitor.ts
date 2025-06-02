import { useCallback } from 'react';

interface PerformanceMonitorOptions {
  componentName?: string;
  trackRender?: boolean;
  trackMemory?: boolean;
  warnThreshold?: number;
  enableMemoryMonitoring?: boolean;
  threshold?: number;
}

interface PerformanceMonitor {
  recordRender: () => void;
  recordMemory: () => void;
  getMetrics: () => any;
}

// 性能监控 Hook
// 简化版本，用于基本的性能跟踪
export const usePerformanceMonitor = (
  options: PerformanceMonitorOptions = {}
): PerformanceMonitor => {
  const componentName = options.componentName || 'Unknown';
  
  const recordRender = useCallback(() => {
    if (options.trackRender) {
      console.debug(`[Performance] ${componentName} rendered`);
    }
  }, [componentName, options.trackRender]);

  const recordMemory = useCallback(() => {
    if (options.trackMemory || options.enableMemoryMonitoring) {
      console.debug(`[Performance] ${componentName} memory check`);
    }
  }, [componentName, options.trackMemory, options.enableMemoryMonitoring]);

  const getMetrics = useCallback(() => {
    return {
      componentName,
      timestamp: Date.now(),
    };
  }, [componentName]);

  return {
    recordRender,
    recordMemory,
    getMetrics,
  };
};