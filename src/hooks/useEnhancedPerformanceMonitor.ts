import React, { useEffect, useRef, useState, useCallback } from "react";";
import { InteractionManager, Dimensions } from "react-native";"";"";
// 性能指标接口/;,/g/;
interface PerformanceMetrics {renderTime: number}memoryUsage: number,;
networkLatency: number,;
frameDrops: number,;
interactionDelay: number,;
bundleSize: number,;
cacheHitRate: number,;
errorCount: number,;
warningCount: number,;
}
}
  const timestamp = number;}
}
// 性能阈值配置/;,/g/;
interface PerformanceThresholds {renderTime: number}memoryUsage: number,;
networkLatency: number,;
frameDrops: number,;
}
}
  const interactionDelay = number;}
}
// 性能优化建议"/;,"/g"/;
interface OptimizationSuggestion {';,}type: 'render' | 'memory' | 'network' | 'interaction' | 'bundle';','';
severity: 'low' | 'medium' | 'high' | 'critical';','';
message: string,;
action: string,;
}
}
  const impact = string;}
}
// 性能监控配置/;,/g/;
interface PerformanceMonitorConfig {enabled: boolean}sampleRate: number,;
thresholds: PerformanceThresholds,;
reportInterval: number,;
maxSamples: number,;
}
}
  const enableDetailedLogging = boolean;}
}
// 默认配置/;,/g,/;
  const: DEFAULT_CONFIG: PerformanceMonitorConfig = {enabled: true,;
sampleRate: 0.1, // 10% 采样率/;,/g,/;
  thresholds: {renderTime: 16, // 16ms (60fps)/;,/g,/;
  memoryUsage: 100 * 1024 * 1024, // 100MB;/;,/g,/;
  networkLatency: 1000, // 1s;/;,/g,/;
  frameDrops: 5,;
}
    interactionDelay: 100, // 100ms;}/;/g/;
  }
reportInterval: 30000, // 30秒/;,/g,/;
  maxSamples: 100,;
const enableDetailedLogging = false;};
// 性能数据收集器/;,/g/;
class PerformanceCollector {private static instance: PerformanceCollector;,}private metrics: PerformanceMetrics[] = [];
private config: PerformanceMonitorConfig;
private frameDropCounter = 0;
private lastFrameTime = 0;
private networkRequests: Map<string, number> = new Map();
private errorCount = 0;
private warningCount = 0;
constructor(config: PerformanceMonitorConfig = DEFAULT_CONFIG) {this.config = config;}}
}
    this.setupGlobalErrorHandling();}
  }
  static getInstance(config?: PerformanceMonitorConfig): PerformanceCollector {if (!PerformanceCollector.instance) {}}
      PerformanceCollector.instance = new PerformanceCollector(config);}
    }
    return PerformanceCollector.instance;
  }
  private setupGlobalErrorHandling(): void {// 监听全局错误/;,}const originalError = console.error;,/g/;
console.error = (...args) => {this.errorCount++;}}
      originalError.apply(console, args);}
    };
const originalWarn = console.warn;
console.warn = (...args) => {this.warningCount++;}}
      originalWarn.apply(console, args);}
    };
  }
  // 记录渲染时间/;,/g/;
recordRenderTime(componentName: string, renderTime: number): void {if (!this.shouldSample()) return;,}const  metric: PerformanceMetrics = {renderTime}memoryUsage: this.getMemoryUsage(),;
networkLatency: this.getAverageNetworkLatency(),;
frameDrops: this.frameDropCounter,;
interactionDelay: 0,;
bundleSize: 0,;
cacheHitRate: 0,;
errorCount: this.errorCount,;
}
      warningCount: this.warningCount,}
      const timestamp = Date.now();};
this.addMetric(metric);
if (this.config.enableDetailedLogging) {}
      console.log(`[Performance] ${componentName} render time: ${renderTime;}ms`);````;```;
    }
  }
  // 记录网络请求/;,/g/;
recordNetworkRequest(url: string, startTime: number, endTime: number): void {const latency = endTime - startTime;,}this.networkRequests.set(url, latency);
}
    if (latency > this.config.thresholds.networkLatency) {}
      console.warn(`[Performance] Slow network request: ${url;} (${latency}ms)`);````;```;
    }
  }
  // 记录交互延迟/;,/g/;
recordInteractionDelay(interactionType: string, delay: number): void {if (!this.shouldSample()) return;}}
    if (delay > this.config.thresholds.interactionDelay) {}
      console.warn(`[Performance] Slow interaction: ${interactionType;} (${delay}ms)`);````;```;
    }
  }
  // 记录帧丢失/;,/g/;
recordFrameDrop(): void {}}
    this.frameDropCounter++;}
  }
  // 获取内存使用情况/;,/g/;
private getMemoryUsage(): number {// React Native 中获取内存使用情况的方法有限/;}    // 这里返回一个估算值/;/g/;
}
    return (performance as any)?.memory?.usedJSHeapSize || 0;}
  }
  // 获取平均网络延迟/;,/g/;
private getAverageNetworkLatency(): number {if (this.networkRequests.size === 0) return 0;,}const latencies = Array.from(this.networkRequests.values());
}
    return latencies.reduce(sum, latency) => sum + latency, 0) / latencies.length;}/;/g/;
  }
  // 判断是否应该采样/;,/g/;
private shouldSample(): boolean {}}
    return this.config.enabled && Math.random() < this.config.sampleRate;}
  }
  // 添加性能指标/;,/g/;
private addMetric(metric: PerformanceMetrics): void {this.metrics.push(metric);}        // 限制样本数量/;,/g/;
if (this.metrics.length > this.config.maxSamples) {}}
      this.metrics.shift();}
    }
  }
  // 获取性能报告/;,/g/;
getPerformanceReport(): {metrics: PerformanceMetrics[]}averages: Partial<PerformanceMetrics>,;
}
  const suggestions = OptimizationSuggestion[];}
  } {const averages = this.calculateAverages();,}const suggestions = this.generateOptimizationSuggestions(averages);
return {const metrics = this.metrics;}}
      averages,}
      suggestions};
  }
  // 计算平均值/;,/g/;
private calculateAverages(): Partial<PerformanceMetrics> {}
    if (this.metrics.length === 0) return {};
const: sums = this.metrics.reduce(acc, metric) => ({)renderTime: acc.renderTime + metric.renderTime}memoryUsage: acc.memoryUsage + metric.memoryUsage,;
networkLatency: acc.networkLatency + metric.networkLatency,;
frameDrops: acc.frameDrops + metric.frameDrops,);
interactionDelay: acc.interactionDelay + metric.interactionDelay,);
}
        errorCount: acc.errorCount + metric.errorCount;),}
        warningCount: acc.warningCount + metric.warningCount;}),;
      {renderTime: 0}memoryUsage: 0,;
networkLatency: 0,;
frameDrops: 0,;
interactionDelay: 0,;
}
        errorCount: 0,}
        const warningCount = 0;}
    );
const count = this.metrics.length;
return {renderTime: sums.renderTime / count,/;,}memoryUsage: sums.memoryUsage / count,/;,/g,/;
  networkLatency: sums.networkLatency / count,/;,/g,/;
  frameDrops: sums.frameDrops / count,/;,/g,/;
  interactionDelay: sums.interactionDelay / count,/;/g/;
}
      errorCount: sums.errorCount / count,}/;,/g/;
const warningCount = sums.warningCount / count;};/;/g/;
  }
  // 生成优化建议/;,/g/;
private generateOptimizationSuggestions(averages: Partial<PerformanceMetrics>): OptimizationSuggestion[] {const suggestions: OptimizationSuggestion[] = [];}    // 渲染性能建议/;,/g/;
if (averages.renderTime && averages.renderTime > this.config.thresholds.renderTime) {';,}suggestions.push({';,)type: "render";","";,}const severity = averages.renderTime > this.config.thresholds.renderTime * 2 ? 'high' : 'medium';';'';

}
)}
    });
    // 内存使用建议)/;,/g/;
if (averages.memoryUsage && averages.memoryUsage > this.config.thresholds.memoryUsage) {';,}suggestions.push({')'';,}type: "memory";",")";"";
}
      severity: averages.memoryUsage > this.config.thresholds.memoryUsage * 2 ? 'critical' : 'high';')',}'';
message: `平均内存使用 ${(averages.memoryUsage / 1024 / 1024).toFixed(2);}MB 超过阈值`,```/`;`/g`/`;

    }
    // 网络延迟建议/;,/g/;
if (averages.networkLatency && averages.networkLatency > this.config.thresholds.networkLatency) {';,}suggestions.push({';,)type: "network";","";,}const severity = 'medium';';'';

}
)}
    });
    // 交互延迟建议)/;,/g/;
if (averages.interactionDelay && averages.interactionDelay > this.config.thresholds.interactionDelay) {';,}suggestions.push({';,)type: "interaction";","";,}const severity = 'medium';';'';

}
}
    }
    return suggestions;);
  });
  // 清理数据)/;,/g/;
clear(): void {this.metrics = [];,}this.frameDropCounter = 0;
this.networkRequests.clear();
this.errorCount = 0;
}
    this.warningCount = 0;}
  }
}
// 增强的性能监控Hook;/;,/g/;
export const useEnhancedPerformanceMonitor = ();
componentName: string,;
config: Partial<PerformanceMonitorConfig> = {;}
) => {const [performanceData, setPerformanceData] = useState<{}    metrics: PerformanceMetrics[],;
averages: Partial<PerformanceMetrics>,;
}
  const suggestions = OptimizationSuggestion[];}
  }>({ metrics: [], averages: {;}, suggestions: [] ;});
const renderStartTime = useRef<number>(0);
const collector = useRef<PerformanceCollector>();
const reportTimer = useRef<NodeJS.Timeout>();
  // 初始化收集器/;,/g/;
useEffect() => {}
    mergedConfig: { ...DEFAULT_CONFIG, ...config };
collector.current = PerformanceCollector.getInstance(mergedConfig);
  }, [config]);
  // 记录渲染开始时间/;,/g/;
const  startRenderMeasurement = useCallback() => {}}
    renderStartTime.current = Date.now();}
  }, []);
  // 记录渲染结束时间/;,/g/;
const  endRenderMeasurement = useCallback() => {if (renderStartTime.current > 0 && collector.current) {}      const renderTime = Date.now() - renderStartTime.current;
collector.current.recordRenderTime(componentName, renderTime);
}
      renderStartTime.current = 0;}
    }
  }, [componentName]);
  // 记录网络请求/;,/g,/;
  const: recordNetworkRequest = useCallback(url: string, startTime: number, endTime: number) => {}}
    collector.current?.recordNetworkRequest(url, startTime, endTime);}
  }, []);
  // 记录交互延迟/;,/g,/;
  const: recordInteraction = useCallback(interactionType: string, startTime: number) => {const delay = Date.now() - startTime;}}
    collector.current?.recordInteractionDelay(interactionType, delay);}
  }, []);
  // 获取性能报告/;,/g/;
const  getPerformanceReport = useCallback() => {}
    return collector.current?.getPerformanceReport() || { metrics: [], averages: {;}, suggestions: [] ;};
  }, []);
  // 定期更新性能数据/;,/g/;
useEffect() => {}
    mergedConfig: { ...DEFAULT_CONFIG, ...config };
if (mergedConfig.enabled) {reportTimer.current = setInterval() => {}        const report = getPerformanceReport();
}
        setPerformanceData(report);}
      }, mergedConfig.reportInterval);
    }
    return () => {if (reportTimer.current) {}}
        clearInterval(reportTimer.current);}
      }
    };
  }, [config, getPerformanceReport]);
  // 组件挂载时开始测量/;,/g/;
useEffect() => {startRenderMeasurement();}        // 使用 InteractionManager 确保在交互完成后测量/;,/g/;
const  handle = InteractionManager.runAfterInteractions() => {}}
      endRenderMeasurement();}
    });
return () => {}}
      handle.cancel();}
    };
  }, [startRenderMeasurement, endRenderMeasurement]);
return {performanceData}startRenderMeasurement,;
endRenderMeasurement,;
recordNetworkRequest,;
recordInteraction,;
}
    getPerformanceReport,}
    clearData: () => collector.current?.clear();};
};
// 性能监控装饰器/;,/g/;
export const withPerformanceMonitoring = <P extends object>();
const WrappedComponent = React.ComponentType<P>;
componentName?: string;
) => {';,}const  MonitoredComponent = (props: P) => {';}}'';
    const name = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Unknown';'}'';
const { startRenderMeasurement, endRenderMeasurement } = useEnhancedPerformanceMonitor(name);
useEffect() => {startRenderMeasurement();,}return () => {}}
        endRenderMeasurement();}
      };
    }, [startRenderMeasurement, endRenderMeasurement]);
return React.createElement(WrappedComponent, props);';'';
  };';,'';
MonitoredComponent.displayName = `withPerformanceMonitoring(${componentName || 'Component'})`;````;,```;
return MonitoredComponent;
};';,'';
export type { PerformanceMetrics, OptimizationSuggestion, PerformanceMonitorConfig };