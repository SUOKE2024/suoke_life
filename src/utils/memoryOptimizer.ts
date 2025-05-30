import { performanceMonitor } from "./performanceMonitor";

/**
 * 内存优化工具
 * 提供内存监控、垃圾回收建议、内存泄漏检测等功能
 */

export interface MemorySnapshot {
  timestamp: number;
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
  components: Map<string, number>;
  listeners: Map<string, number>;
}

export interface MemoryLeak {
  type: "component" | "listener" | "timer" | "memory";
  name: string;
  count: number;
  growth: number;
  severity: "low" | "medium" | "high" | "critical";
  suggestion: string;
}

export interface MemoryOptimizationSuggestion {
  type: "cleanup" | "optimization" | "warning";
  priority: "low" | "medium" | "high" | "critical";
  message: string;
  action?: () => void;
}

/**
 * 内存优化器类
 */
export class MemoryOptimizer {
  private static instance: MemoryOptimizer;
  private snapshots: MemorySnapshot[] = [];
  private componentRegistry: Map<string, number> = new Map();
  private listenerRegistry: Map<string, number> = new Map();
  private timerRegistry: Set<any> = new Set();
  private intervalRegistry: Set<any> = new Set();
  private maxSnapshots = 100;
  private monitoringInterval: any = null;

  private constructor() {
    this.startMonitoring();
  }

  static getInstance(): MemoryOptimizer {
    if (!MemoryOptimizer.instance) {
      MemoryOptimizer.instance = new MemoryOptimizer();
    }
    return MemoryOptimizer.instance;
  }

  /**
   * 开始内存监控
   */
  startMonitoring(interval: number = 30000): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }

    this.monitoringInterval = setInterval(() => {
      this.takeSnapshot();
      this.detectLeaks();
    }, interval);
  }

  /**
   * 停止内存监控
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  /**
   * 拍摄内存快照
   */
  takeSnapshot(): MemorySnapshot {
    const snapshot: MemorySnapshot = {
      timestamp: Date.now(),
      usedJSHeapSize: 0,
      totalJSHeapSize: 0,
      jsHeapSizeLimit: 0,
      components: new Map(this.componentRegistry),
      listeners: new Map(this.listenerRegistry),
    };

    // 在支持的环境中获取内存信息
    if (typeof performance !== "undefined" && performance.memory) {
      snapshot.usedJSHeapSize = performance.memory.usedJSHeapSize;
      snapshot.totalJSHeapSize = performance.memory.totalJSHeapSize;
      snapshot.jsHeapSizeLimit = performance.memory.jsHeapSizeLimit;
    }

    this.snapshots.push(snapshot);

    // 限制快照数量
    if (this.snapshots.length > this.maxSnapshots) {
      this.snapshots = this.snapshots.slice(-this.maxSnapshots);
    }

    // 记录性能指标
    performanceMonitor.recordMemoryUsage();

    return snapshot;
  }

  /**
   * 注册组件
   */
  registerComponent(name: string): void {
    const count = this.componentRegistry.get(name) || 0;
    this.componentRegistry.set(name, count + 1);
  }

  /**
   * 注销组件
   */
  unregisterComponent(name: string): void {
    const count = this.componentRegistry.get(name) || 0;
    if (count > 1) {
      this.componentRegistry.set(name, count - 1);
    } else {
      this.componentRegistry.delete(name);
    }
  }

  /**
   * 注册事件监听器
   */
  registerListener(name: string): void {
    const count = this.listenerRegistry.get(name) || 0;
    this.listenerRegistry.set(name, count + 1);
  }

  /**
   * 注销事件监听器
   */
  unregisterListener(name: string): void {
    const count = this.listenerRegistry.get(name) || 0;
    if (count > 1) {
      this.listenerRegistry.set(name, count - 1);
    } else {
      this.listenerRegistry.delete(name);
    }
  }

  /**
   * 注册定时器
   */
  registerTimer(timer: any): void {
    this.timerRegistry.add(timer);
  }

  /**
   * 注销定时器
   */
  unregisterTimer(timer: any): void {
    this.timerRegistry.delete(timer);
  }

  /**
   * 注册间隔器
   */
  registerInterval(interval: any): void {
    this.intervalRegistry.add(interval);
  }

  /**
   * 注销间隔器
   */
  unregisterInterval(interval: any): void {
    this.intervalRegistry.delete(interval);
  }

  /**
   * 检测内存泄漏
   */
  detectLeaks(): MemoryLeak[] {
    const leaks: MemoryLeak[] = [];

    // 检测组件泄漏
    this.componentRegistry.forEach((count, name) => {
      if (count > 10) {
        // 阈值可配置
        leaks.push({
          type: "component",
          name,
          count,
          growth: this.calculateGrowthRate(name, "component"),
          severity: count > 50 ? "critical" : count > 25 ? "high" : "medium",
          suggestion: `组件 ${name} 实例过多 (${count})，检查是否存在内存泄漏`,
        });
      }
    });

    // 检测监听器泄漏
    this.listenerRegistry.forEach((count, name) => {
      if (count > 20) {
        // 阈值可配置
        leaks.push({
          type: "listener",
          name,
          count,
          growth: this.calculateGrowthRate(name, "listener"),
          severity: count > 100 ? "critical" : count > 50 ? "high" : "medium",
          suggestion: `事件监听器 ${name} 过多 (${count})，检查是否正确清理`,
        });
      }
    });

    // 检测定时器泄漏
    if (this.timerRegistry.size > 50) {
      leaks.push({
        type: "timer",
        name: "timers",
        count: this.timerRegistry.size,
        growth: 0,
        severity: this.timerRegistry.size > 200 ? "critical" : "high",
        suggestion: `活跃定时器过多 (${this.timerRegistry.size})，检查是否正确清理`,
      });
    }

    // 检测内存增长
    const memoryGrowth = this.calculateMemoryGrowth();
    if (memoryGrowth > 0.5) {
      // 50%增长阈值
      leaks.push({
        type: "memory",
        name: "heap",
        count: 0,
        growth: memoryGrowth,
        severity:
          memoryGrowth > 2 ? "critical" : memoryGrowth > 1 ? "high" : "medium",
        suggestion: `内存使用量持续增长 (${(memoryGrowth * 100).toFixed(
          1
        )}%)，可能存在内存泄漏`,
      });
    }

    return leaks;
  }

  /**
   * 计算增长率
   */
  private calculateGrowthRate(
    name: string,
    type: "component" | "listener"
  ): number {
    if (this.snapshots.length < 2) {
      return 0;
    }

    const recent = this.snapshots.slice(-5); // 最近5个快照
    const registry = type === "component" ? "components" : "listeners";

    const values = recent.map((snapshot) => snapshot[registry].get(name) || 0);
    if (values.length < 2) {
      return 0;
    }

    const first = values[0];
    const last = values[values.length - 1];

    return first > 0 ? (last - first) / first : 0;
  }

  /**
   * 计算内存增长
   */
  private calculateMemoryGrowth(): number {
    if (this.snapshots.length < 10) {
      return 0;
    }

    const recent = this.snapshots.slice(-10);
    const first = recent[0].usedJSHeapSize;
    const last = recent[recent.length - 1].usedJSHeapSize;

    return first > 0 ? (last - first) / first : 0;
  }

  /**
   * 获取优化建议
   */
  getOptimizationSuggestions(): MemoryOptimizationSuggestion[] {
    const suggestions: MemoryOptimizationSuggestion[] = [];
    const leaks = this.detectLeaks();

    // 基于泄漏检测的建议
    leaks.forEach((leak) => {
      suggestions.push({
        type: "warning",
        priority: leak.severity as any,
        message: leak.suggestion,
      });
    });

    // 内存使用率建议
    const latestSnapshot = this.snapshots[this.snapshots.length - 1];
    if (latestSnapshot && latestSnapshot.jsHeapSizeLimit > 0) {
      const usageRate =
        latestSnapshot.usedJSHeapSize / latestSnapshot.jsHeapSizeLimit;

      if (usageRate > 0.8) {
        suggestions.push({
          type: "warning",
          priority: "high",
          message: `内存使用率过高 (${(usageRate * 100).toFixed(
            1
          )}%)，建议清理缓存或优化代码`,
          action: () => this.suggestCleanup(),
        });
      } else if (usageRate > 0.6) {
        suggestions.push({
          type: "optimization",
          priority: "medium",
          message: `内存使用率较高 (${(usageRate * 100).toFixed(
            1
          )}%)，建议监控内存使用情况`,
        });
      }
    }

    // 定时器清理建议
    if (this.timerRegistry.size > 20) {
      suggestions.push({
        type: "cleanup",
        priority: "medium",
        message: `检测到 ${this.timerRegistry.size} 个活跃定时器，建议检查是否需要清理`,
        action: () => this.cleanupTimers(),
      });
    }

    return suggestions;
  }

  /**
   * 建议清理操作
   */
  private suggestCleanup(): void {
    // 这里可以实现自动清理逻辑
    console.log("建议执行内存清理操作");
  }

  /**
   * 清理定时器
   */
  private cleanupTimers(): void {
    // 清理已完成的定时器
    this.timerRegistry.forEach((timer) => {
      // 在实际实现中，这里需要更复杂的逻辑来判断定时器是否仍然需要
      // 这里只是示例
    });
  }

  /**
   * 强制垃圾回收（如果支持）
   */
  forceGarbageCollection(): boolean {
    // 在React Native环境中，垃圾回收由系统自动管理
    // 这个方法主要用于开发和调试目的，实际上在RN中无法手动触发GC
    console.log("垃圾回收请求已记录，系统将自动管理内存");
    return false;
  }

  /**
   * 获取内存统计
   */
  getMemoryStats(): {
    current: MemorySnapshot | null;
    trend: "increasing" | "decreasing" | "stable";
    leaks: MemoryLeak[];
    suggestions: MemoryOptimizationSuggestion[];
    components: number;
    listeners: number;
    timers: number;
    intervals: number;
  } {
    const current = this.snapshots[this.snapshots.length - 1] || null;
    const trend = this.calculateMemoryTrend();
    const leaks = this.detectLeaks();
    const suggestions = this.getOptimizationSuggestions();

    return {
      current,
      trend,
      leaks,
      suggestions,
      components: this.componentRegistry.size,
      listeners: this.listenerRegistry.size,
      timers: this.timerRegistry.size,
      intervals: this.intervalRegistry.size,
    };
  }

  /**
   * 计算内存趋势
   */
  private calculateMemoryTrend(): "increasing" | "decreasing" | "stable" {
    if (this.snapshots.length < 5) {
      return "stable";
    }

    const recent = this.snapshots.slice(-5);
    const values = recent.map((s) => s.usedJSHeapSize);

    let increasing = 0;
    let decreasing = 0;

    for (let i = 1; i < values.length; i++) {
      if (values[i] > values[i - 1]) {
        increasing++;
      } else if (values[i] < values[i - 1]) {
        decreasing++;
      }
    }

    if (increasing > decreasing + 1) {
      return "increasing";
    }
    if (decreasing > increasing + 1) {
      return "decreasing";
    }
    return "stable";
  }

  /**
   * 导出内存数据
   */
  exportMemoryData(): {
    snapshots: MemorySnapshot[];
    stats: {
      current: MemorySnapshot | null;
      trend: "increasing" | "decreasing" | "stable";
      leaks: MemoryLeak[];
      suggestions: MemoryOptimizationSuggestion[];
      components: number;
      listeners: number;
      timers: number;
      intervals: number;
    };
    timestamp: number;
  } {
    return {
      snapshots: [...this.snapshots],
      stats: this.getMemoryStats(),
      timestamp: Date.now(),
    };
  }

  /**
   * 清理所有数据
   */
  cleanup(): void {
    this.stopMonitoring();
    this.snapshots = [];
    this.componentRegistry.clear();
    this.listenerRegistry.clear();
    this.timerRegistry.clear();
    this.intervalRegistry.clear();
  }
}

// 导出单例实例
export const memoryOptimizer = MemoryOptimizer.getInstance();

// 便捷函数
export const registerComponent = (name: string) => {
  memoryOptimizer.registerComponent(name);
};

export const unregisterComponent = (name: string) => {
  memoryOptimizer.unregisterComponent(name);
};

export const registerListener = (name: string) => {
  memoryOptimizer.registerListener(name);
};

export const unregisterListener = (name: string) => {
  memoryOptimizer.unregisterListener(name);
};

export const getMemoryStats = () => {
  return memoryOptimizer.getMemoryStats();
};

export const takeMemorySnapshot = () => {
  return memoryOptimizer.takeSnapshot();
};

export const detectMemoryLeaks = () => {
  return memoryOptimizer.detectLeaks();
};
