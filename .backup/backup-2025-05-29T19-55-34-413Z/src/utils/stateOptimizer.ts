import { performanceMonitor } from "./performanceMonitor";

/**
 * 应用状态管理优化工具
 * 提供状态更新优化、状态变化追踪、状态性能监控等功能
 */

export interface StateChangeEvent {
  stateName: string;
  oldValue: any;
  newValue: any;
  timestamp: number;
  duration: number;
  source: string;
}

export interface StatePerformanceData {
  stateName: string;
  updateCount: number;
  averageUpdateTime: number;
  lastUpdateTime: number;
  totalChanges: number;
  unnecessaryUpdates: number;
  timestamp: number;
}

export interface StateOptimizationSuggestion {
  type: "batching" | "memoization" | "normalization" | "splitting";
  severity: "low" | "medium" | "high";
  message: string;
  stateName: string;
  impact: number;
}

/**
 * 状态优化器类
 */
export class StateOptimizer {
  private static instance: StateOptimizer;
  private stateData: Map<string, StatePerformanceData> = new Map();
  private stateHistory: Map<string, StateChangeEvent[]> = new Map();
  private updateTimers: Map<string, number> = new Map();
  private batchedUpdates: Map<string, any[]> = new Map();
  private batchTimer: any = null;
  private readonly batchDelay = 16; // 16ms批量延迟（一帧时间）

  private constructor() {}

  static getInstance(): StateOptimizer {
    if (!StateOptimizer.instance) {
      StateOptimizer.instance = new StateOptimizer();
    }
    return StateOptimizer.instance;
  }

  /**
   * 开始状态更新计时
   */
  startStateUpdate(stateName: string): void {
    const startTime = performance.now();
    this.updateTimers.set(stateName, startTime);
  }

  /**
   * 结束状态更新计时
   */
  endStateUpdate(
    stateName: string,
    oldValue: any,
    newValue: any,
    source: string = "unknown"
  ): void {
    const endTime = performance.now();
    const startTime = this.updateTimers.get(stateName);

    if (!startTime) {
      return;
    }

    const duration = endTime - startTime;
    this.updateTimers.delete(stateName);

    // 检查是否为不必要的更新
    const isUnnecessary = this.isUnnecessaryUpdate(oldValue, newValue);

    // 记录状态变化事件
    const changeEvent: StateChangeEvent = {
      stateName,
      oldValue,
      newValue,
      timestamp: Date.now(),
      duration,
      source,
    };

    this.recordStateChange(changeEvent, isUnnecessary);

    // 记录到性能监控器
    performanceMonitor.recordUserInteraction(
      "state_update",
      stateName,
      undefined,
      { duration, source }
    );
  }

  /**
   * 检查是否为不必要的更新
   */
  private isUnnecessaryUpdate(oldValue: any, newValue: any): boolean {
    // 深度比较检查值是否真的发生了变化
    try {
      return JSON.stringify(oldValue) === JSON.stringify(newValue);
    } catch (error) {
      // 如果无法序列化，使用浅比较
      return oldValue === newValue;
    }
  }

  /**
   * 记录状态变化
   */
  private recordStateChange(
    changeEvent: StateChangeEvent,
    isUnnecessary: boolean
  ): void {
    const { stateName, duration } = changeEvent;

    // 更新状态历史
    const history = this.stateHistory.get(stateName) || [];
    history.push(changeEvent);

    // 限制历史记录数量
    if (history.length > 100) {
      history.splice(0, history.length - 100);
    }
    this.stateHistory.set(stateName, history);

    // 更新性能数据
    const existing = this.stateData.get(stateName);

    if (existing) {
      const newUpdateCount = existing.updateCount + 1;
      const newAverageUpdateTime =
        (existing.averageUpdateTime * existing.updateCount + duration) /
        newUpdateCount;

      this.stateData.set(stateName, {
        ...existing,
        updateCount: newUpdateCount,
        averageUpdateTime: newAverageUpdateTime,
        lastUpdateTime: duration,
        totalChanges: existing.totalChanges + 1,
        unnecessaryUpdates:
          existing.unnecessaryUpdates + (isUnnecessary ? 1 : 0),
        timestamp: Date.now(),
      });
    } else {
      this.stateData.set(stateName, {
        stateName,
        updateCount: 1,
        averageUpdateTime: duration,
        lastUpdateTime: duration,
        totalChanges: 1,
        unnecessaryUpdates: isUnnecessary ? 1 : 0,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * 批量状态更新
   */
  batchStateUpdate(stateName: string, update: any): Promise<void> {
    return new Promise((resolve) => {
      const updates = this.batchedUpdates.get(stateName) || [];
      updates.push({ update, resolve });
      this.batchedUpdates.set(stateName, updates);

      if (!this.batchTimer) {
        this.batchTimer = setTimeout(() => {
          this.processBatchedUpdates();
        }, this.batchDelay);
      }
    });
  }

  /**
   * 处理批量更新
   */
  private processBatchedUpdates(): void {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    this.batchedUpdates.forEach((updates, stateName) => {
      if (updates.length > 0) {
        // 合并所有更新
        const mergedUpdate = updates.reduce((acc, { update }) => {
          return { ...acc, ...update };
        }, {});

        // 执行合并后的更新
        this.startStateUpdate(`${stateName}_batch`);

        // 这里应该调用实际的状态更新逻辑
        // 由于这是一个通用工具，具体的更新逻辑需要在使用时提供

        this.endStateUpdate(`${stateName}_batch`, {}, mergedUpdate, "batch");

        // 解析所有Promise
        updates.forEach(({ resolve }) => resolve());
      }
    });

    this.batchedUpdates.clear();
  }

  /**
   * 获取状态性能数据
   */
  getStatePerformanceData(stateName?: string): StatePerformanceData[] {
    if (stateName) {
      const data = this.stateData.get(stateName);
      return data ? [data] : [];
    }
    return Array.from(this.stateData.values());
  }

  /**
   * 获取状态变化历史
   */
  getStateHistory(stateName: string, limit: number = 50): StateChangeEvent[] {
    const history = this.stateHistory.get(stateName) || [];
    return history.slice(-limit);
  }

  /**
   * 获取优化建议
   */
  getOptimizationSuggestions(): StateOptimizationSuggestion[] {
    const suggestions: StateOptimizationSuggestion[] = [];

    this.stateData.forEach((data, stateName) => {
      // 检查不必要的更新
      const unnecessaryRate = data.unnecessaryUpdates / data.updateCount;
      if (unnecessaryRate > 0.3) {
        suggestions.push({
          type: "memoization",
          severity: unnecessaryRate > 0.7 ? "high" : "medium",
          message: `状态 ${stateName} 有 ${(unnecessaryRate * 100).toFixed(
            1
          )}% 的不必要更新，建议使用记忆化优化`,
          stateName,
          impact: unnecessaryRate,
        });
      }

      // 检查更新频率
      if (data.updateCount > 100 && data.averageUpdateTime > 5) {
        suggestions.push({
          type: "batching",
          severity: "medium",
          message: `状态 ${stateName} 更新频繁，建议使用批量更新优化`,
          stateName,
          impact: data.updateCount / 100,
        });
      }

      // 检查更新耗时
      if (data.averageUpdateTime > 16) {
        suggestions.push({
          type: "normalization",
          severity: "high",
          message: `状态 ${stateName} 更新耗时过长，建议优化数据结构或拆分状态`,
          stateName,
          impact: data.averageUpdateTime / 16,
        });
      }

      // 检查状态复杂度
      const history = this.stateHistory.get(stateName) || [];
      if (history.length > 0) {
        const recentChanges = history.slice(-10);
        const hasComplexChanges = recentChanges.some((change) => {
          try {
            const changeSize = JSON.stringify(change.newValue).length;
            return changeSize > 10000; // 10KB阈值
          } catch {
            return false;
          }
        });

        if (hasComplexChanges) {
          suggestions.push({
            type: "splitting",
            severity: "medium",
            message: `状态 ${stateName} 数据结构复杂，建议拆分为多个小状态`,
            stateName,
            impact: 2,
          });
        }
      }
    });

    return suggestions.sort((a, b) => b.impact - a.impact);
  }

  /**
   * 获取状态统计
   */
  getStateStats(): {
    totalStates: number;
    totalUpdates: number;
    averageUpdateTime: number;
    unnecessaryUpdateRate: number;
    slowestStates: StatePerformanceData[];
    mostUpdatedStates: StatePerformanceData[];
    suggestions: StateOptimizationSuggestion[];
  } {
    const states = Array.from(this.stateData.values());
    const totalStates = states.length;
    const totalUpdates = states.reduce(
      (sum, state) => sum + state.updateCount,
      0
    );
    const totalUnnecessaryUpdates = states.reduce(
      (sum, state) => sum + state.unnecessaryUpdates,
      0
    );

    const averageUpdateTime =
      states.length > 0
        ? states.reduce((sum, state) => sum + state.averageUpdateTime, 0) /
          states.length
        : 0;

    const unnecessaryUpdateRate =
      totalUpdates > 0 ? totalUnnecessaryUpdates / totalUpdates : 0;

    const slowestStates = [...states]
      .sort((a, b) => b.averageUpdateTime - a.averageUpdateTime)
      .slice(0, 5);

    const mostUpdatedStates = [...states]
      .sort((a, b) => b.updateCount - a.updateCount)
      .slice(0, 5);

    const suggestions = this.getOptimizationSuggestions();

    return {
      totalStates,
      totalUpdates,
      averageUpdateTime,
      unnecessaryUpdateRate,
      slowestStates,
      mostUpdatedStates,
      suggestions,
    };
  }

  /**
   * 清除状态数据
   */
  clearStateData(stateName?: string): void {
    if (stateName) {
      this.stateData.delete(stateName);
      this.stateHistory.delete(stateName);
    } else {
      this.stateData.clear();
      this.stateHistory.clear();
    }
  }

  /**
   * 导出状态数据
   */
  exportStateData(): {
    performanceData: StatePerformanceData[];
    history: Record<string, StateChangeEvent[]>;
    stats: ReturnType<typeof this.getStateStats>;
    timestamp: number;
  } {
    const history: Record<string, StateChangeEvent[]> = {};
    this.stateHistory.forEach((events, stateName) => {
      history[stateName] = [...events];
    });

    return {
      performanceData: Array.from(this.stateData.values()),
      history,
      stats: this.getStateStats(),
      timestamp: Date.now(),
    };
  }
}

// 导出单例实例
export const stateOptimizer = StateOptimizer.getInstance();

// 便捷函数
export const trackStateUpdate = (
  stateName: string,
  oldValue: any,
  newValue: any,
  source?: string
) => {
  stateOptimizer.startStateUpdate(stateName);
  // 模拟异步更新
  setTimeout(() => {
    stateOptimizer.endStateUpdate(stateName, oldValue, newValue, source);
  }, 0);
};

export const batchStateUpdate = (stateName: string, update: any) => {
  return stateOptimizer.batchStateUpdate(stateName, update);
};

export const getStatePerformanceData = (stateName?: string) => {
  return stateOptimizer.getStatePerformanceData(stateName);
};

export const getStateOptimizationSuggestions = () => {
  return stateOptimizer.getOptimizationSuggestions();
};

export const getStateStats = () => {
  return stateOptimizer.getStateStats();
};

export const clearStatePerformanceData = (stateName?: string) => {
  stateOptimizer.clearStateData(stateName);
};
