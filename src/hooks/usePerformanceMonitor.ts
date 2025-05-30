import { useEffect, useRef } from "react";

/**
 * 组件性能监控Hook
 * 自动生成的性能优化工具
 */
export const usePerformanceMonitor = (componentName: string) => {
  const renderCountRef = useRef(0);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    startTimeRef.current = performance.now();
    renderCountRef.current += 1;
  });

  useEffect(() => {
    const endTime = performance.now();
    const renderTime = endTime - startTimeRef.current;

    if (renderTime > 16) {
      // 超过16ms
      console.warn(
        `⚠️  ${componentName} 渲染时间过长: ${renderTime.toFixed(2)}ms`
      );
    }

    if (renderCountRef.current > 5) {
      console.warn(
        `⚠️  ${componentName} 重渲染次数过多: ${renderCountRef.current}`
      );
    }
  });

  return {
    renderCount: renderCountRef.current,
    componentName,
  };
};

export default usePerformanceMonitor;
