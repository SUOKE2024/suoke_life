/* ; */
*/
export interface MonitoringConfig {enabled: boolean}metrics: {performance: boolean,;
accuracy: boolean,
usage: boolean,
}
}
  const errors = boolean}
};
reporting: {interval: number,
destination: string,
}
  const format = 'json' | 'csv' | 'prometheus}
  };
}
export interface PerformanceMetrics {;
responseTime: {average: number,
p50: number,
p95: number,
}
  const p99 = number}
};
throughput: {requestsPerSecond: number,
}
  const requestsPerMinute = number}
  };
accuracy: {overallAccuracy: number,
diagnosisAccuracy: {looking: number,
listening: number,
inquiry: number,
palpation: number,
}
  const calculation = number}
    };
  };
resourceUsage: {cpuUsage: number,
memoryUsage: number,
}
  const diskUsage = number}
  };
errorRate: {total: number,
}
  byType: Record<string, number>}
  };
}
export interface MetricEvent {timestamp: number}type: string,;
const value = number;
}
}
  metadata?: Record<string; any>}
}
// 性能监控器类
export class PerformanceMonitor {private config: MonitoringConfig;
private metrics: PerformanceMetrics;
private events: MetricEvent[] = [];
private startTime: number = Date.now();
constructor(config: MonitoringConfig) {this.config = config}
}
    this.metrics = this.initializeMetrics()}
  }
  // 初始化指标
private initializeMetrics(): PerformanceMetrics {return {}      responseTime: {average: 0,
p50: 0,
p95: 0,
}
        const p99 = 0}
      }
throughput: {requestsPerSecond: 0,
}
        const requestsPerMinute = 0}
      }
accuracy: {overallAccuracy: 0,
diagnosisAccuracy: {,}
  looking: 0,listening: 0,inquiry: 0,palpation: 0,calculation: 0}
        };
      },resourceUsage: {cpuUsage: 0,memoryUsage: 0,diskUsage: 0}
      },errorRate: {total: 0,byType: {;
      };
    };
  }
  // 记录响应时间/,/g,/;
  public: recordResponseTime(duration: number, operation: string): void {if (!this.config.enabled || !this.config.metrics.performance) {}
      return}
    }
    this.events.push({))'timestamp: Date.now(),'
type: 'response_time,'
}
      value: duration,}
      const metadata = { operation }
    });
this.updateResponseTimeMetrics();
  }
  // 记录准确率/,/g,/;
  public: recordAccuracy(accuracy: number, diagnosisType: string): void {if (!this.config.enabled || !this.config.metrics.accuracy) {}
      return}
    }
    this.events.push({))'timestamp: Date.now(),'
type: 'accuracy,'
}
      value: accuracy,}
      const metadata = { diagnosisType }
    });
this.updateAccuracyMetrics();
  }
  // 记录错误/,/g,/;
  public: recordError(errorType: string, details?: unknown): void {if (!this.config.enabled || !this.config.metrics.errors) {}
      return}
    }
    this.events.push({))'timestamp: Date.now(),'
type: 'error,'
}
      value: 1,}
      metadata: { errorType, details }
    });
this.updateErrorMetrics();
  }
  // 记录资源使用/,/g,/;
  public: recordResourceUsage(cpu: number, memory: number, disk: number): void {if (!this.config.enabled || !this.config.metrics.usage) {}
      return}
    }
    this.metrics.resourceUsage = {cpuUsage: cpu}memoryUsage: memory,
}
      const diskUsage = disk}
    };
  }
  // 获取当前指标
const public = getMetrics(): PerformanceMetrics {}
    return { ...this.metrics };
  }
  // 获取指标报告'
const public = generateReport(): object {'const uptime = Date.now() - this.startTime;
}
    return {timestamp: Date.now(),uptime,metrics: this.metrics,eventCount: this.events.length,summary: {totalRequests: this.events.filter(e => e.type === 'response_time').length,totalErrors: this.events.filter(e => e.type === 'error').length,averageResponseTime: this.metrics.responseTime.average,overallAccuracy: this.metrics.accuracy.overallAccuracy;'}
      };
    };
  }
  // 清理旧事件
const public = cleanup(maxAge: number = 3600000): void {// 默认1小时/const cutoff = Date.now() - maxAge;/g/;
}
    this.events = this.events.filter(event => event.timestamp > cutoff)}
  }
  // 重置指标
const public = reset(): void {this.metrics = this.initializeMetrics()this.events = [];
}
    this.startTime = Date.now()}
  }
  // 私有方法'
private updateResponseTimeMetrics(): void {'const responseTimes = this.events;
      .filter(e => e.type === 'response_time');
      .map(e => e.value);
      .sort(a, b) => a - b);
if (responseTimes.length === 0) {}
      return}
    }
    this.metrics.responseTime.average =;
responseTimes.reduce(sum, time) => sum + time, 0) / responseTimes.length;
this.metrics.responseTime.p50 = this.percentile(responseTimes, 0.5);
this.metrics.responseTime.p95 = this.percentile(responseTimes, 0.95);
this.metrics.responseTime.p99 = this.percentile(responseTimes, 0.99);
    // 计算吞吐量'/,'/g'/;
const recentEvents = this.events.filter(;)'
e => e.type === 'response_time' && e.timestamp > Date.now() - 60000 // 最近1分钟;'/;'/g'/;
    );
this.metrics.throughput.requestsPerMinute = recentEvents.length;
this.metrics.throughput.requestsPerSecond = recentEvents.length / 60;
  }
private updateAccuracyMetrics(): void {'const accuracyEvents = this.events.filter(e => e.type === 'accuracy');
if (accuracyEvents.length === 0) {}
      return}
    }
    // 计算总体准确率
this.metrics.accuracy.overallAccuracy =;
accuracyEvents.reduce(sum, event) => sum + event.value, 0) / accuracyEvents.length;'/;'/g'/;
    // 计算各诊法准确率'/,'/g,'/;
  diagnosisTypes: ["looking",listening', "inquiry",palpation', 'calculation'];
for (const type of diagnosisTypes) {const typeEvents = accuracyEvents.filter(e => e.metadata?.diagnosisType === type);
if (typeEvents.length > 0) {this.metrics.accuracy.diagnosisAccuracy[,]const type: keyof typeof this.metrics.accuracy.diagnosisAccuracy}
];
        ] = typeEvents.reduce(sum, event) => sum + event.value, 0) / typeEvents.length;}
      }
    }
  }
private updateErrorMetrics(): void {'const errorEvents = this.events.filter(e => e.type === 'error');
this.metrics.errorRate.total = errorEvents.length;
}
    // 按错误类型统计}
const errorByType: Record<string, number> = {;};
for (const event of errorEvents) {'const errorType = event.metadata?.errorType || 'unknown';
}
      errorByType[errorType] = (errorByType[errorType] || 0) + 1}
    }
    this.metrics.errorRate.byType = errorByType;
  }
  private percentile(values: number[], p: number): number {if (values.length === 0) {}
      return 0}
    }
    const index = Math.ceil(values.length * p) - 1;
return values[Math.max(0, index)];
  }
}
export default PerformanceMonitor;