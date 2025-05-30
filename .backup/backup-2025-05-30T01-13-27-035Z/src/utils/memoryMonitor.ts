import { useEffect, useRef } from "react";


/**
 * 内存监控工具
 * 索克生活APP - 性能优化
 */


interface MemoryInfo {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

class MemoryMonitor {
  private static instance: MemoryMonitor;
  private listeners: ((info: MemoryInfo) => void)[] = [];
  private intervalId: NodeJS.Timeout | null = null;

  static getInstance(): MemoryMonitor {
    if (!MemoryMonitor.instance) {
      MemoryMonitor.instance = new MemoryMonitor();
    }
    return MemoryMonitor.instance;
  }

  startMonitoring(interval: number = 5000) {
    if (this.intervalId) {
      return;
    }

    this.intervalId = setInterval(() => {
      const memoryInfo = this.getMemoryInfo();
      if (memoryInfo) {
        this.notifyListeners(memoryInfo);
        this.checkMemoryThreshold(memoryInfo);
      }
    }, interval);
  }

  stopMonitoring() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  addListener(callback: (info: MemoryInfo) => void) {
    this.listeners.push(callback);
  }

  removeListener(callback: (info: MemoryInfo) => void) {
    this.listeners = this.listeners.filter((listener) => listener !== callback);
  }

  private getMemoryInfo(): MemoryInfo | null {
    if ("memory" in performance) {
      const memory = (performance as any).memory;
      return {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit,
      };
    }
    return null;
  }

  private notifyListeners(info: MemoryInfo) {
    this.listeners.forEach((listener) => listener(info));
  }

  private checkMemoryThreshold(info: MemoryInfo) {
    const usagePercentage = (info.usedJSHeapSize / info.jsHeapSizeLimit) * 100;

    if (usagePercentage > 80) {
      console.warn("内存使用率过高:", usagePercentage.toFixed(2) + "%");
      // 触发垃圾回收建议
      this.suggestGarbageCollection();
    }
  }

  private suggestGarbageCollection() {
    if ("gc" in global) {
      (global as any).gc();
    }
  }
}

// React Hook for memory monitoring
export const useMemoryMonitor = (enabled: boolean = true) => {
  const memoryInfoRef = useRef<MemoryInfo | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const monitor = MemoryMonitor.getInstance();

    const handleMemoryUpdate = (info: MemoryInfo) => {
      memoryInfoRef.current = info;
    };

    monitor.addListener(handleMemoryUpdate);
    monitor.startMonitoring();

    return () => {
      monitor.removeListener(handleMemoryUpdate);
      monitor.stopMonitoring();
    };
  }, [enabled]);

  return memoryInfoRef.current;
};

export default MemoryMonitor;
