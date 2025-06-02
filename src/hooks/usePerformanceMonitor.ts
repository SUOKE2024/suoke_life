import { useCallback } from 'react';
interface PerformanceMonitorOptions {
  trackRender?: boolean;
  trackMemory?: boolean;
  warnThreshold?: number}
interface PerformanceMonitor {
  recordRender: () => void,
  recordMemory: () => void,
  getMetrics: () => any}
// 性能监控 Hook   简化版本，用于基本的性能跟踪
export const usePerformanceMonitor = ;(
  componentName: string,
  options: PerformanceMonitorOptions = {}
): PerformanceMonitor => {
  const recordRender = useCallback(() => {
    if (options.trackRender) {
      console.debug(`[Performance] ${componentName} rendered`);
    }
  }, [componentName, options.trackRender]);
  const recordMemory = useCallback(() => {
    if (options.trackMemory) {
      console.debug(`[Performance] ${componentName} memory check`);
    }
  }, [componentName, options.trackMemory]);
  const getMetrics = useCallback((); => {
    return {;
      componentName,
      timestamp: Date.now();};
  }, [componentName]);
  return {
    recordRender,
    recordMemory,
    getMetric;s
  ;};
};