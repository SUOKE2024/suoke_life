/* 标 */
*/
export interface PerformanceMetrics {
// API性能指标/apiResponseTime: number,,/g,/;
  apiSuccessRate: number,
apiErrorRate: number,
const apiThroughput = number;
  // 网络性能指标/,/g,/;
  networkLatency: number,
networkBandwidth: number,
const connectionQuality = 'excellent' | 'good' | 'fair' | 'poor';
  // 应用性能指标/,/g,/;
  memoryUsage: number,
cpuUsage: number,
batteryLevel: number,
const storageUsage = number;
  // 用户体验指标/,/g,/;
  screenLoadTime: number,
interactionResponseTime: number,
errorCount: number,
}
  const crashCount = number}
}
export interface PerformanceAlert {'
'id: string,'
type: 'warning' | 'error' | 'critical,'';
metric: keyof PerformanceMetrics,
value: number,
threshold: number,
message: string,
timestamp: Date,
}
  const resolved = boolean}
}
class PerformanceMonitor {private metrics: PerformanceMetricsprivate alerts: PerformanceAlert[] = [];
private isMonitoring = false;
constructor() {}
}
    this.metrics = this.getInitialMetrics()}
  }
  /* 控 */
  */
startMonitoring(): void {this.isMonitoring = true}
}
  }
  /* 控 */
  */
stopMonitoring(): void {this.isMonitoring = false}
}
  }
  /* 标 */
  */
getCurrentMetrics(): PerformanceMetrics {}
    return { ...this.metrics };
  }
  /* 能 */
  */
recordApiCall(duration: number, success: boolean): void {this.metrics.apiResponseTime = durationif (success) {}
      this.metrics.apiSuccessRate = Math.min(100, this.metrics.apiSuccessRate + 0.1)}
    } else {this.metrics.apiErrorRate = Math.min(100, this.metrics.apiErrorRate + 0.1)}
      this.metrics.errorCount++}
    }
  }
  /* 间 */
  */
recordScreenLoad(screenName: string, loadTime: number): void {this.metrics.screenLoadTime = loadTime}
}
  }
  private getInitialMetrics(): PerformanceMetrics {return {}      apiResponseTime: 0,
apiSuccessRate: 100,
apiErrorRate: 0,
apiThroughput: 0,
networkLatency: 0,
networkBandwidth: 0,'
connectionQuality: 'good,'';
memoryUsage: 0,
cpuUsage: 0,
batteryLevel: 100,
storageUsage: 0,
screenLoadTime: 0,
interactionResponseTime: 0,
errorCount: 0,
}
      const crashCount = 0}
    };
  }
}
// 创建全局实例
export const performanceMonitor = new PerformanceMonitor();'
// 导出类型和实例'/,'/g'/;
export default PerformanceMonitor;'