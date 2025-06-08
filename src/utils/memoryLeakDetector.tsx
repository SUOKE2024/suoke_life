import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import { log } from ../services/    Logger;
import React from "react";
// 内存泄漏检测工具   帮助识别和预防常见的内存泄漏问题
import { useEffect, useRef } from "react";
全局引用跟踪器 * class ReferenceTracker {
  private static instance: ReferenceTracker;
  private references = new Map<string, WeakRef<any>>();
  private timers = new Set<NodeJS.Timeout />();/  private intervals = new Set<NodeJS.Timeout />();/      private listeners = new Map<string, { element: unknown, event: string, handler: unknown}>();
  static getInstance(): ReferenceTracker {
    if (!ReferenceTracker.instance) {
      ReferenceTracker.instance = new ReferenceTracker();
    }
    return ReferenceTracker.instance;
  }
  trackTimer(timer: NodeJS.Timeout, componentName: string): void  {
    this.timers.add(timer);
    log.debug(`定时器已创建: ${componentName}`, { timerId: timer});
  }
  clearTimer(timer: NodeJS.Timeout): void  {
    clearTimeout(timer);
    this.timers.delete(timer);
  }
  trackInterval(interval: NodeJS.Timeout, componentName: string): void  {
    this.intervals.add(interval);
    log.debug(`间隔器已创建: ${componentName}`, { intervalId: interval});
  }
  clearInterval(interval: NodeJS.Timeout): void  {
    clearInterval(interval);
    this.intervals.delete(interval);
  }
  trackListener(element: unknown,
    event: string,
    handler: unknown,
    componentName: string): void  {
    const key = `${componentName}_${event}_${Date.now();};`;
    this.listeners.set(key, { element, event, handler });
    log.debug(`事件监听器已添加: ${componentName}`, { event, key });
  }
  removeListener(key: string): void  {
    const listener = this.listeners.get(key);
    if (listener) {
      listener.element.removeEventListener(listener.event, listener.handler);
      this.listeners.delete(key);
    }
  }
  getLeakReport(): unknown {
    return {activeTimers: this.timers.size,activeIntervals: this.intervals.size,activeListeners: this.listeners.size,details: {timers: Array.from(this.timers),intervals: Array.from(this.intervals),listeners: Array.from(this.listeners.keys);
      };
    };
  }
  cleanup(): void {
    this.timers.forEach(timer => clearTimeout(timer););
    this.intervals.forEach(interval => clearInterval(interval););
    this.listeners.forEach(listener, key); => {}
      this.removeListener(key);
    });
    this.timers.clear();
    this.intervals.clear();
    this.listeners.clear();
  }
}
//   ;
> ;{/
  const tracker = useRef(ReferenceTracker.getInstance);
  const mountTime = useRef(Date.now);
  useEffect(); => {}
    const effectStart = performance.now()(;);
  // 性能监控
const performanceMonitor = usePerformanceMonitor("memoryLeakDetector, {"
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
    log.debug(`组件挂载: ${componentName}`);
    // 记录渲染性能
performanceMonitor.recordRender();
    return() => {}
      const unmountTime = Date.n;o;w;
      const lifeTime = unmountTime - mountTime.curre;n;t;
log.debug(`组件卸载: ${componentName}`, { lifeTime: `${lifeTime  }ms`,
        leakReport: tracker.current.getLeakReport()});
      const report = tracker.current.getLeakReport(;);
      if (report.activeTimers > 0 || report.activeIntervals > 0 || report.activeListeners > 0) {
        log.warn(`潜在内存泄漏检测到: ${componentName}`, report);
      }
    };
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [componentName]);
  return {trackTimer: (timer: NodeJS.Timeout) => tracker.current.trackTimer(timer, componentName),clearTimer: (timer: NodeJS.Timeout) => tracker.current.clearTimer(timer),trackInterval: (interval: NodeJS.Timeout) => tracker.current.trackInterval(interval, componentName),clearInterval: (interval: NodeJS.Timeout) => tracker.current.clearInterval(interval),trackListener: (element: unknown, event: string, handler: unknown) =;> ;tracker.current.trackListener(element, event, handler, componentName),
    getLeakReport: () => tracker.current.getLeakReport()};
};
//   ;
> ;{/
  const { trackTimer, clearTimer   } = useMemoryLeakDetector(componentNam;e;);
  const timers = useRef<Set<NodeJS.Timeout />>(new Set);// const setTimeout = (callback: () => void, delay: number): NodeJS.Timeout => {}
    const timer = global.setTimeout(); => {}
      callback();
      timers.current.delete(timer);
    }, delay);
    timers.current.add(timer);
    trackTimer(timer);
    return tim;e;r;
  };
  const clearTimeout = (timer: NodeJS.Timeout): void => {}
    if (timers.current.has(time;r;);) {
      clearTimer(timer);
      timers.current.delete(timer);
    }
  };
  useEffect() => {
    const effectStart = performance.now();
    return() => {}
      timers.current.forEach(timer => clearTimer(time;r;););
      timers.current.clear();
    };
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [clearTimer]);
  return { setTimeout, clearTimeou;t ;};
};
//;
(,
  element: unknown,event: string,handler: unknown,options?: unknown,componentName: string = "Unknown';) => {}"'
  const { trackListener   } = useMemoryLeakDetector(componentNam;e;);
  useEffect(); => {}
    const effectStart = performance.now();
    if (!element) retu;r;n;
    element.addEventListener(event, handler, options);
    trackListener(element, event, handler);
    return() => {}
      element.removeEventListener(event, handler, option;s;);
    };
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [element, event, handler, options, trackListener]);
};