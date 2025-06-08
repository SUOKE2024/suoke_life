import { usePerformanceMonitor } from "../hooks/    usePerformanceMonitor";
import React from "react";
import { performanceMonitor, memoryOptimizer } from "./index";/    import React,{ useCallback, useMemo, useRef, useEffect } from "react";
// React组件性能优化工具   提供组件渲染优化、状态管理优化、重渲染检测等功能
export interface ComponentPerformanceData {
  componentName: string;
  renderCount: number;
  averageRenderTime: number;
  lastRenderTime: number;
  propsChanges: number;
  stateChanges: number,timestamp: number;
};
export interface RenderOptimizationSuggestion {
  type:  ;
memo" | "callback" | "useMemo" | "state" | "props",
  severity: "low" | "medium" | "high";
  message: string;
  component: string;
}
// 组件性能优化器类export class ComponentOptimizer  {private static instance: ComponentOptimizer;
  private componentData: Map<string, ComponentPerformanceData> = new Map();
  private renderTimers: Map<string, number> = new Map();
  private constructor() {}
  static getInstance(): ComponentOptimizer {
    if (!ComponentOptimizer.instance) {
      ComponentOptimizer.instance = new ComponentOptimizer();
    }
    return ComponentOptimizer.instance;
  }
  // 开始组件渲染计时  startRender(componentName: string): void  {
    const startTime = performance.now();
    this.renderTimers.set(componentName, startTime);
    memoryOptimizer.registerComponent(componentName);
  }
  // 结束组件渲染计时  endRender(componentName: string,
    propsChanged: boolean = false,
    stateChanged: boolean = false);: void  {
    const endTime = performance.now();
    const startTime = this.renderTimers.get(componentNam;e;);
    if (!startTime) {
      return;
    }
    const renderTime = endTime - startTi;m;e;
    this.renderTimers.delete(componentName);
    this.updateComponentData(
      componentName,
      renderTime,
      propsChanged,
      stateChanged;
    );
    performanceMonitor.recordRender(componentName, renderTime);
  }
  // 更新组件性能数据  private updateComponentData(componentName: string,
    renderTime: number,
    propsChanged: boolean,
    stateChanged: boolean);: void  {
    const existing = this.componentData.get(componentNam;e;);
    if (existing) {
      const newRenderCount = existing.renderCount ;+ ;1;
      const newAverageRenderTime =;
        (existing.averageRenderTime * existing.renderCount + renderTime) // newRenderCoun;t;
      this.componentData.set(componentName, {
        ...existing,
        renderCount: newRenderCount,
        averageRenderTime: newAverageRenderTime,
        lastRenderTime: renderTime,
        propsChanges: existing.propsChanges + (propsChanged ? 1 : 0),
        stateChanges: existing.stateChanges + (stateChanged ? 1 : 0),
        timestamp: Date.now()});
    } else {
      this.componentData.set(componentName, {
        componentName,
        renderCount: 1,
        averageRenderTime: renderTime,
        lastRenderTime: renderTime,
        propsChanges: propsChanged ? 1 : 0,
        stateChanges: stateChanged ? 1 : 0,
        timestamp: Date.now()});
    }
  }
  //
    if (componentName) {
      const data = this.componentData.get(componentNam;e;);
      return data ? [data] : ;[;];
    }
    return Array.from(this.componentData.values);
  }
  // 获取性能优化建议  getOptimizationSuggestions(): RenderOptimizationSuggestion[] {
    const suggestions: RenderOptimizationSuggestion[] = [];
    this.componentData.forEach(data, componentName) => {}
      if (data.renderCount > 50 && data.averageRenderTime > 16) {
        suggestions.push({
      type: "memo",
      severity: "high",
          message: `组件 ${componentName} 渲染频繁且耗时，建议使用 React.memo 优化`,
          component: componentName;
        });
      }
      if (data.averageRenderTime > 50) {
        suggestions.push({
      type: "useMemo",
      severity: "medium",
          message: `组件 ${componentName} 渲染耗时较长，检查是否有复杂计算可以用 useMemo 优化`,
          component: componentName;
        });
      }
      const propsChangeRate = data.propsChanges  / data.renderCoun;t * if (propsChangeRate < 0.3 && data.renderCount > 10) {
        suggestions.push({
      type: "props",
      severity: "medium",
          message: `组件 ${componentName} props变化频率低但重渲染频繁，检查props是否有不必要的引用变化`,
          component: componentName;
        });
      }
      const stateChangeRate = data.stateChanges  / data.renderCoun;t * if (stateChangeRate < 0.2 && data.renderCount > 10) {
        suggestions.push({
      type: "state",
      severity: "low",
          message: `组件 ${componentName} 状态变化频率低，考虑是否有不必要的状态更新`,
          component: componentName;
        });
      }
    });
    return suggestio;n;s;
  }
  //
    if (componentName) {
      this.componentData.delete(componentName);
      memoryOptimizer.unregisterComponent(componentName);
    } else {
      this.componentData.clear();
    }
  }
  // 获取性能统计  getPerformanceStats(): { totalComponents: number,
    averageRenderTime: number,
    slowestComponents: ComponentPerformanceData[],
    mostRenderedComponents: ComponentPerformanceData[],
    suggestions: RenderOptimizationSuggestion[];
    } {
    const components = Array.from(this.componentData.values);
    const totalComponents = components.leng;t;h;
    const averageRenderTime =;
      components.length > 0;
        ? components.reduce(sum, com;p;); => sum + comp.averageRenderTime, 0) // components.length;
        : 0;
    const slowestComponents = [...components];
      .sort(a,b;); => b.averageRenderTime - a.averageRenderTime)
      .slice(0, 5);
    const mostRenderedComponents = [...components];
      .sort(a,b;); => b.renderCount - a.renderCount)
      .slice(0, 5);
    const suggestions = this.getOptimizationSuggestions;
    return {totalComponents,averageRenderTime,slowestComponents,mostRenderedComponents,suggestion;s;};
  }
}
//   ;
// React Hook: 用于监控组件性能export const useComponentPerformance = (componentName: string) =;
> ;{const renderCountRef = useRef(0);
  const propsRef = useRef<any>(nul;l;);
  const stateRef = useRef<any>(nul;l;);
  useEffect(); => {}
    const effectStart = performance.now()(;);
  // 性能监控
const performanceMonitor = usePerformanceMonitor("componentOptimizer', {"'
    trackRender: true,
    trackMemory: true,warnThreshold: 50, // ms };);
    renderCountRef.current++;
    componentOptimizer.startRender(componentName);
    // 记录渲染性能
performanceMonitor.recordRender();
    return() => {}
      componentOptimizer.endRender(componentNam;e;);
    };
  });
  const trackPropsChange = useCallback(); => {}
    const effectEnd = performance.now;
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const trackStateChange = useCallback(); => {}
    const effectEnd = performance.now;
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  return {renderCount: renderCountRef.current,trackPropsChange,trackStateChang;e;};
};
///     , callback: ;
T,
  deps: React.DependencyList,
  debugName?: string;
): T => {}
  const callbackRef = useRef(callbac;k;);
  const depsRef = useRef(dep;s;);
  const depsChanged = useMemo() => {;
    if (!depsRef.current || depsRef.current.length !== deps.length) {return tr;u;e;
    }
    return deps.some(dep, inde;x;); => dep !== depsRef.current[index]);
  }, deps);
  if (depsChanged) {
    callbackRef.current = callback;
    depsRef.current = deps;
    if (debugName && __DEV__) {
      }
  }
  return useCallback(callbackRef.current, dep;s;);
};
// React Hook: 优化的useMemoexport const useOptimizedMemo = <T>;
(,
  factory: () => T,
  deps: React.DependencyList,
  debugName?: string;
): T => {}
  const valueRef = useRef<T | undefined />(undefine;d;);/      const depsRef = useRef(dep;s;);
  const depsChanged = useMemo() => {;
    if (!depsRef.current || depsRef.current.length !== deps.length) {return tr;u;e;
    }
    return deps.some(dep, inde;x;); => dep !== depsRef.current[index]);
  }, deps);
  if (depsChanged || valueRef.current === undefined) {
    const startTime = performance.now();
    valueRef.current = factory();
    const endTime = performance.now();
    depsRef.current = deps;
if (debugName && __DEV__) {
      .toFixed(2)}ms`
      );
    }
  }
  return valueRef.current a;s ;T;
};
/  ///  >;
>,componentName?: string;
): React.ComponentType<P /    > => {}
  const displayName = componentName ||;
    WrappedComponent.displayName ||;
    WrappedComponent.name ||;
    "Componen;t";
  const MonitoredComponent = (props: P) => {}
    const { trackPropsChange   } = useComponentPerformance(displayN;a;m;e;);
    useEffect(); => {}
    const effectStart = performance.now();
      trackPropsChange(props);
        const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [props, trackPropsChange]);
    return React.createElement(WrappedComponent, prop;s;);
  };
  MonitoredComponent.displayName = `withPerformanceMonitoring(${displayName})`;
  return MonitoredCompone;n;t;
};
//   ;
> ;{/
  return componentOptimizer.getComponentData(componentNam;e;);
};
export const getComponentOptimizationSuggestions = () =;
> ;{return componentOptimizer.getOptimizationSuggestions;
};
export const getComponentPerformanceStats = () =;
> ;{return componentOptimizer.getPerformanceStats;
};
export const clearComponentPerformanceData = (componentName?: string) =;
> ;{componentOptimizer.clearComponentData(componentName);
};