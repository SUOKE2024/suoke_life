import { performanceMonitor, memoryOptimizer } from "./index";
import React, { useCallback, useMemo, useRef, useEffect } from "react";

/**
 * React组件性能优化工具
 * 提供组件渲染优化、状态管理优化、重渲染检测等功能
 */

export interface ComponentPerformanceData {
  componentName: string;
  renderCount: number;
  averageRenderTime: number;
  lastRenderTime: number;
  propsChanges: number;
  stateChanges: number;
  timestamp: number;
}

export interface RenderOptimizationSuggestion {
  type: "memo" | "callback" | "useMemo" | "state" | "props";
  severity: "low" | "medium" | "high";
  message: string;
  component: string;
}

/**
 * 组件性能优化器类
 */
export class ComponentOptimizer {
  private static instance: ComponentOptimizer;
  private componentData: Map<string, ComponentPerformanceData> = new Map();
  private renderTimers: Map<string, number> = new Map();

  private constructor() {}

  static getInstance(): ComponentOptimizer {
    if (!ComponentOptimizer.instance) {
      ComponentOptimizer.instance = new ComponentOptimizer();
    }
    return ComponentOptimizer.instance;
  }

  /**
   * 开始组件渲染计时
   */
  startRender(componentName: string): void {
    const startTime = performance.now();
    this.renderTimers.set(componentName, startTime);

    // 注册组件到内存优化器
    memoryOptimizer.registerComponent(componentName);
  }

  /**
   * 结束组件渲染计时
   */
  endRender(
    componentName: string,
    propsChanged: boolean = false,
    stateChanged: boolean = false
  ): void {
    const endTime = performance.now();
    const startTime = this.renderTimers.get(componentName);

    if (!startTime) {
      return;
    }

    const renderTime = endTime - startTime;
    this.renderTimers.delete(componentName);

    // 更新组件性能数据
    this.updateComponentData(
      componentName,
      renderTime,
      propsChanged,
      stateChanged
    );

    // 记录到性能监控器
    performanceMonitor.recordRender(componentName, renderTime);
  }

  /**
   * 更新组件性能数据
   */
  private updateComponentData(
    componentName: string,
    renderTime: number,
    propsChanged: boolean,
    stateChanged: boolean
  ): void {
    const existing = this.componentData.get(componentName);

    if (existing) {
      const newRenderCount = existing.renderCount + 1;
      const newAverageRenderTime =
        (existing.averageRenderTime * existing.renderCount + renderTime) /
        newRenderCount;

      this.componentData.set(componentName, {
        ...existing,
        renderCount: newRenderCount,
        averageRenderTime: newAverageRenderTime,
        lastRenderTime: renderTime,
        propsChanges: existing.propsChanges + (propsChanged ? 1 : 0),
        stateChanges: existing.stateChanges + (stateChanged ? 1 : 0),
        timestamp: Date.now(),
      });
    } else {
      this.componentData.set(componentName, {
        componentName,
        renderCount: 1,
        averageRenderTime: renderTime,
        lastRenderTime: renderTime,
        propsChanges: propsChanged ? 1 : 0,
        stateChanges: stateChanged ? 1 : 0,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * 获取组件性能数据
   */
  getComponentData(componentName?: string): ComponentPerformanceData[] {
    if (componentName) {
      const data = this.componentData.get(componentName);
      return data ? [data] : [];
    }
    return Array.from(this.componentData.values());
  }

  /**
   * 获取性能优化建议
   */
  getOptimizationSuggestions(): RenderOptimizationSuggestion[] {
    const suggestions: RenderOptimizationSuggestion[] = [];

    this.componentData.forEach((data, componentName) => {
      // 检查渲染频率
      if (data.renderCount > 50 && data.averageRenderTime > 16) {
        suggestions.push({
          type: "memo",
          severity: "high",
          message: `组件 ${componentName} 渲染频繁且耗时，建议使用 React.memo 优化`,
          component: componentName,
        });
      }

      // 检查渲染时间
      if (data.averageRenderTime > 50) {
        suggestions.push({
          type: "useMemo",
          severity: "medium",
          message: `组件 ${componentName} 渲染耗时较长，检查是否有复杂计算可以用 useMemo 优化`,
          component: componentName,
        });
      }

      // 检查props变化频率
      const propsChangeRate = data.propsChanges / data.renderCount;
      if (propsChangeRate < 0.3 && data.renderCount > 10) {
        suggestions.push({
          type: "props",
          severity: "medium",
          message: `组件 ${componentName} props变化频率低但重渲染频繁，检查props是否有不必要的引用变化`,
          component: componentName,
        });
      }

      // 检查状态变化频率
      const stateChangeRate = data.stateChanges / data.renderCount;
      if (stateChangeRate < 0.2 && data.renderCount > 10) {
        suggestions.push({
          type: "state",
          severity: "low",
          message: `组件 ${componentName} 状态变化频率低，考虑是否有不必要的状态更新`,
          component: componentName,
        });
      }
    });

    return suggestions;
  }

  /**
   * 清除组件数据
   */
  clearComponentData(componentName?: string): void {
    if (componentName) {
      this.componentData.delete(componentName);
      memoryOptimizer.unregisterComponent(componentName);
    } else {
      this.componentData.clear();
    }
  }

  /**
   * 获取性能统计
   */
  getPerformanceStats(): {
    totalComponents: number;
    averageRenderTime: number;
    slowestComponents: ComponentPerformanceData[];
    mostRenderedComponents: ComponentPerformanceData[];
    suggestions: RenderOptimizationSuggestion[];
  } {
    const components = Array.from(this.componentData.values());
    const totalComponents = components.length;

    const averageRenderTime =
      components.length > 0
        ? components.reduce((sum, comp) => sum + comp.averageRenderTime, 0) /
          components.length
        : 0;

    const slowestComponents = [...components]
      .sort((a, b) => b.averageRenderTime - a.averageRenderTime)
      .slice(0, 5);

    const mostRenderedComponents = [...components]
      .sort((a, b) => b.renderCount - a.renderCount)
      .slice(0, 5);

    const suggestions = this.getOptimizationSuggestions();

    return {
      totalComponents,
      averageRenderTime,
      slowestComponents,
      mostRenderedComponents,
      suggestions,
    };
  }
}

// 导出单例实例
export const componentOptimizer = ComponentOptimizer.getInstance();

/**
 * React Hook: 用于监控组件性能
 */
export const useComponentPerformance = (componentName: string) => {
  const renderCountRef = useRef(0);
  const propsRef = useRef<any>(null);
  const stateRef = useRef<any>(null);

  useEffect(() => {
    renderCountRef.current++;
    componentOptimizer.startRender(componentName);

    return () => {
      componentOptimizer.endRender(componentName);
    };
  });

  const trackPropsChange = useCallback((props: any) => {
    const propsChanged =
      JSON.stringify(props) !== JSON.stringify(propsRef.current);
    propsRef.current = props;
    return propsChanged;
  }, []);

  const trackStateChange = useCallback((state: any) => {
    const stateChanged =
      JSON.stringify(state) !== JSON.stringify(stateRef.current);
    stateRef.current = state;
    return stateChanged;
  }, []);

  return {
    renderCount: renderCountRef.current,
    trackPropsChange,
    trackStateChange,
  };
};

/**
 * React Hook: 优化的useCallback
 */
export const useOptimizedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList,
  debugName?: string
): T => {
  const callbackRef = useRef(callback);
  const depsRef = useRef(deps);

  // 检查依赖是否真的发生了变化
  const depsChanged = useMemo(() => {
    if (!depsRef.current || depsRef.current.length !== deps.length) {
      return true;
    }
    return deps.some((dep, index) => dep !== depsRef.current[index]);
  }, deps);

  if (depsChanged) {
    callbackRef.current = callback;
    depsRef.current = deps;

    if (debugName && __DEV__) {
      console.log(`useOptimizedCallback: ${debugName} dependencies changed`);
    }
  }

  return useCallback(callbackRef.current, deps);
};

/**
 * React Hook: 优化的useMemo
 */
export const useOptimizedMemo = <T>(
  factory: () => T,
  deps: React.DependencyList,
  debugName?: string
): T => {
  const valueRef = useRef<T | undefined>(undefined);
  const depsRef = useRef(deps);

  // 检查依赖是否真的发生了变化
  const depsChanged = useMemo(() => {
    if (!depsRef.current || depsRef.current.length !== deps.length) {
      return true;
    }
    return deps.some((dep, index) => dep !== depsRef.current[index]);
  }, deps);

  if (depsChanged || valueRef.current === undefined) {
    const startTime = performance.now();
    valueRef.current = factory();
    const endTime = performance.now();

    depsRef.current = deps;

    if (debugName && __DEV__) {
      console.log(
        `useOptimizedMemo: ${debugName} computed in ${(
          endTime - startTime
        ).toFixed(2)}ms`
      );
    }
  }

  return valueRef.current as T;
};

/**
 * 高阶组件：性能监控包装器
 */
export const withPerformanceMonitoring = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
): React.ComponentType<P> => {
  const displayName =
    componentName ||
    WrappedComponent.displayName ||
    WrappedComponent.name ||
    "Component";

  const MonitoredComponent = (props: P) => {
    const { trackPropsChange } = useComponentPerformance(displayName);

    useEffect(() => {
      trackPropsChange(props);
    }, [props, trackPropsChange]);

    return React.createElement(WrappedComponent, props);
  };

  MonitoredComponent.displayName = `withPerformanceMonitoring(${displayName})`;

  return MonitoredComponent;
};

// 便捷函数
export const getComponentPerformanceData = (componentName?: string) => {
  return componentOptimizer.getComponentData(componentName);
};

export const getComponentOptimizationSuggestions = () => {
  return componentOptimizer.getOptimizationSuggestions();
};

export const getComponentPerformanceStats = () => {
  return componentOptimizer.getPerformanceStats();
};

export const clearComponentPerformanceData = (componentName?: string) => {
  componentOptimizer.clearComponentData(componentName);
};
