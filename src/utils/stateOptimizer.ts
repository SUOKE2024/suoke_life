// 状态优化器工具 - 提供状态更新优化、状态变化追踪、状态性能监控等功能
// 应用状态管理优化工具   提供状态更新优化、状态变化追踪、状态性能监控等功能
export interface StateChangeEvent {
  stateName: string;,
  oldValue: unknown;
  newValue: unknown;,
  timestamp: number;
  duration: number;,
  source: string;
}
export interface StatePerformanceData {
  stateName: string;,
  updateCount: number;
  averageUpdateTime: number;,
  lastUpdateTime: number;
  totalChanges: number;,
  unnecessaryUpdates: number;
  timestamp: number;
}
export interface StateOptimizationSuggestion {
  type: 'batching' | 'memoization' | 'normalization' | 'splitting';,
  severity: 'low' | 'medium' | 'high';
  message: string;,
  stateName: string;
  impact: number;
}
// 批量更新项接口
interface BatchUpdateItem {
  update: unknown;,
  resolve: () => void;
}
// 状态优化器类
export class StateOptimizer {private static instance: StateOptimizer;
  private stateData = new Map<string, StatePerformanceData>();
  private stateHistory = new Map<string, StateChangeEvent[]>();
  private activeUpdates = new Map<string, number>();
  private batchedUpdates = new Map<string, BatchUpdateItem[]>();
  private batchTimer: NodeJS.Timeout | null = null;
  private readonly batchDelay = 16; // 16ms批量延迟
private readonly maxHistorySize = 100;
  private constructor() {}
  static getInstance(): StateOptimizer {
    if (!StateOptimizer.instance) {
      StateOptimizer.instance = new StateOptimizer();
    }
    return StateOptimizer.instance;
  }
  // 开始状态更新跟踪
startStateUpdate(stateName: string): void {
    this.activeUpdates.set(stateName, Date.now());
  }
  // 结束状态更新跟踪
endStateUpdate()
    stateName: string,
    oldValue: unknown,
    newValue: unknown,
    source: string = 'unknown',
  ): void {
    const startTime = this.activeUpdates.get(stateName);
    if (!startTime) return;
    const duration = Date.now() - startTime;
    this.activeUpdates.delete(stateName);
    // 检查是否为不必要的更新
const isUnnecessary = this.isUnnecessaryUpdate(oldValue, newValue);
    // 记录状态变化历史
this.recordStateChange(stateName, oldValue, newValue, duration, source);
    // 更新性能数据
this.updatePerformanceData(stateName, duration, isUnnecessary);
  }
  // 检查是否为不必要的更新
private isUnnecessaryUpdate(oldValue: unknown, newValue: unknown): boolean {
    try {
      return JSON.stringify(oldValue) === JSON.stringify(newValue);
    } catch {
      return oldValue === newValue;
    }
  }
  // 记录状态变化
private recordStateChange()
    stateName: string,
    oldValue: unknown,
    newValue: unknown,
    duration: number,
    source: string,
  ): void {
    const event: StateChangeEvent = { stateName,
      oldValue,
      newValue,
      timestamp: Date.now(),
      duration,
      source };
    const history = this.stateHistory.get(stateName) || [];
    history.push(event);
    // 限制历史记录大小
if (history.length > this.maxHistorySize) {
      history.shift();
    }
    this.stateHistory.set(stateName, history);
  }
  // 更新性能数据
private updatePerformanceData()
    stateName: string,
    duration: number,
    isUnnecessary: boolean,
  ): void {
    const existing = this.stateData.get(stateName);
    if (existing) {
      const newUpdateCount = existing.updateCount + 1;
      const newAverageTime = (existing.averageUpdateTime * existing.updateCount + duration) / newUpdateCount;
      this.stateData.set(stateName, {
        ...existing,
        updateCount: newUpdateCount,
        averageUpdateTime: newAverageTime,
        lastUpdateTime: duration,
        totalChanges: existing.totalChanges + 1,
        unnecessaryUpdates: existing.unnecessaryUpdates + (isUnnecessary ? 1 : 0),
        timestamp: Date.now() });
    } else {
      this.stateData.set(stateName, {
        stateName,
        updateCount: 1,
        averageUpdateTime: duration,
        lastUpdateTime: duration,
        totalChanges: 1,
        unnecessaryUpdates: isUnnecessary ? 1 : 0,
        timestamp: Date.now() });
    }
  }
  // 批量状态更新
batchStateUpdate(stateName: string, update: unknown): Promise<void> {
    return new Promise(resolve) => {
      const updates = this.batchedUpdates.get(stateName) || [];
      updates.push({ update, resolve });
      this.batchedUpdates.set(stateName, updates);
      if (!this.batchTimer) {
        this.batchTimer = setTimeout() => {
          this.processBatchedUpdates();
        }, this.batchDelay);
      }
    });
  }
  // 处理批量更新
private processBatchedUpdates(): void {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
    this.batchedUpdates.forEach((updates, stateName) => {
      if (updates.length > 0) {
        const mergedUpdate = updates.reduce(acc, { update }) => {
          return { ...acc, ...(update as object) };
        }, {} as Record<string, unknown>);
        this.startStateUpdate(`${stateName}_batch`);
        this.endStateUpdate(`${stateName}_batch`, {}, mergedUpdate, 'batch');
        updates.forEach(({ resolve }) => resolve());)
      }
    });
    this.batchedUpdates.clear();
  }
  // 获取状态性能数据
getStatePerformanceData(stateName?: string): StatePerformanceData[] {
    if (stateName) {
      const data = this.stateData.get(stateName);
      return data ? [data] : [];
    }
    return Array.from(this.stateData.values());
  }
  // 获取状态变化历史
getStateHistory(stateName: string, limit: number = 50): StateChangeEvent[] {
    const history = this.stateHistory.get(stateName) || [];
    return history.slice(-limit);
  }
  // 获取优化建议
getOptimizationSuggestions(): StateOptimizationSuggestion[] {
    const suggestions: StateOptimizationSuggestion[] = [];
    this.stateData.forEach((data, stateName) => {
      const unnecessaryRate = data.unnecessaryUpdates / data.updateCount;
      if (unnecessaryRate > 0.3) {
        suggestions.push({
      type: "memoization",
      severity: unnecessaryRate > 0.7 ? 'high' : 'medium',
          message: `状态 ${stateName} 有 ${(unnecessaryRate * 100).toFixed(1)}% 的不必要更新，建议使用记忆化优化`,
          stateName,
          impact: unnecessaryRate});
      }
      if (data.updateCount > 100 && data.averageUpdateTime > 5) {
        suggestions.push({
      type: "batching",
      severity: 'medium',
          message: `状态 ${stateName} 更新频繁，建议使用批量更新优化`,
          stateName,
          impact: data.updateCount / 100});
      }
      if (data.averageUpdateTime > 16) {
        suggestions.push({
      type: "normalization",
      severity: 'high',
          message: `状态 ${stateName} 更新耗时过长，建议优化数据结构或拆分状态`,
          stateName,
          impact: data.averageUpdateTime / 16});
      }
    });
    return suggestions.sort(a, b) => b.impact - a.impact);
  }
  // 获取状态统计
getStateStats(): {
    totalStates: number,
  totalUpdates: number;,
  averageUpdateTime: number,
  unnecessaryUpdateRate: number;,
  slowestStates: StatePerformanceData[],
  mostUpdatedStates: StatePerformanceData[];,
  suggestions: StateOptimizationSuggestion[];
  } {
    const states = Array.from(this.stateData.values());
    const totalStates = states.length;
    const totalUpdates = states.reduce(sum, state) => sum + state.updateCount, 0);
    const totalUnnecessaryUpdates = states.reduce(sum, state) => sum + state.unnecessaryUpdates, 0);
    const averageUpdateTime = states.length > 0 ? states.reduce(sum, state) => sum + state.averageUpdateTime, 0) / states.length : 0;
    const unnecessaryUpdateRate = totalUpdates > 0 ? totalUnnecessaryUpdates / totalUpdates : 0;
    const slowestStates = [...states].sort(a, b) => b.averageUpdateTime - a.averageUpdateTime).slice(0, 5);
    const mostUpdatedStates = [...states].sort(a, b) => b.updateCount - a.updateCount).slice(0, 5);
    const suggestions = this.getOptimizationSuggestions();
    return { totalStates, totalUpdates, averageUpdateTime, unnecessaryUpdateRate, slowestStates, mostUpdatedStates, suggestions };
  }
  // 清除状态数据
clearStateData(stateName?: string): void {
    if (stateName) {
      this.stateData.delete(stateName);
      this.stateHistory.delete(stateName);
    } else {
      this.stateData.clear();
      this.stateHistory.clear();
    }
  }
  // 导出状态数据
exportStateData(): {
    performanceData: StatePerformanceData[],
  history: Record<string, StateChangeEvent[]>;
        stats: {,
  totalStates: number;
      totalUpdates: number,
  averageUpdateTime: number;,
  unnecessaryUpdateRate: number,
  slowestStates: StatePerformanceData[];,
  mostUpdatedStates: StatePerformanceData[],
  suggestions: StateOptimizationSuggestion[];
    };
    timestamp: number;
  } {
    const history: Record<string, StateChangeEvent[]> = {};
    this.stateHistory.forEach((events, stateName) => {
      history[stateName] = [...events];
    });
    return { performanceData: Array.from(this.stateData.values()), history, stats: this.getStateStats(), timestamp: Date.now() };
  }
}
// 导出单例实例
export const stateOptimizer = StateOptimizer.getInstance();
// 便捷函数
export const trackStateUpdate = (stateName: string, oldValue: unknown, newValue: unknown, source?: string) => {
  stateOptimizer.startStateUpdate(stateName);
  // 模拟异步更新
setTimeout() => {
    stateOptimizer.endStateUpdate(stateName, oldValue, newValue, source);
  }, 0);
};
export const batchStateUpdate = (stateName: string, update: unknown) => {
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