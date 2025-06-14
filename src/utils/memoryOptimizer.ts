import { performanceMonitor } from "./    performanceMonitor"
export interface MemorySnapshot {timestamp: number}usedJSHeapSize: number,;
totalJSHeapSize: number,jsHeapSizeLimit: number,components: Map<string, number>;
}
}
  listeners: Map<string, number>}
;};
export interface MemoryLeak {";
"type: "component" | "listener" | "timer" | "memory,";
name: string,"
count: number,","
growth: number,","
severity: "low" | "medium" | "high" | "critical,
}
  const suggestion = string}
};
export interface MemoryOptimizationSuggestion {";
"type: "cleanup" | "optimization" | "warning",priority: "low" | "medium" | "high" | "critical",message: string;";
}
  action?: () => void}
}
// 内存优化器类export class MemoryOptimizer {/private static instance: MemoryOptimizer,/g/;
private snapshots: MemorySnapshot[] = [];
private componentRegistry: Map<string, number> = new Map();
private listenerRegistry: Map<string, number> = new Map();
private timerRegistry: Set<any> = new Set();
private intervalRegistry: Set<any> = new Set();
private maxSnapshots = 100;
private monitoringInterval: unknown = null;
private constructor() {}
}
    this.startMonitoring()}
  }
  static getInstance(): MemoryOptimizer {if (!MemoryOptimizer.instance) {}
      MemoryOptimizer.instance = new MemoryOptimizer()}
    }
    return MemoryOptimizer.instance;
  }
  // 开始内存监控  startMonitoring(interval: number = 30000): void  {/if (this.monitoringInterval) {}}/g/;
      clearInterval(this.monitoringInterval)}
    }
    this.monitoringInterval = setInterval(); => {}
      this.takeSnapshot();
this.detectLeaks();
    }, interval);
  }
  // 停止内存监控  stopMonitoring(): void {/if (this.monitoringInterval) {clearInterval(this.monitoringInterval}}/g/;
      this.monitoringInterval = null}
    }
  }
  // 拍摄内存快照  takeSnapshot(): MemorySnapshot {/const: snapshot: MemorySnapshot = {timestamp: Date.now()}usedJSHeapSize: 0,,/g,/;
  totalJSHeapSize: 0,
jsHeapSizeLimit: 0,
}
      components: new Map(this.componentRegistry),}","
const listeners = new Map(this.listenerRegistry}","
if (typeof performance !== "undefined" && performance.memory) {"snapshot.usedJSHeapSize = performance.memory.usedJSHeapSize,"";
snapshot.totalJSHeapSize = performance.memory.totalJSHeapSize;
}
      snapshot.jsHeapSizeLimit = performance.memory.jsHeapSizeLimit}
    }
    this.snapshots.push(snapshot);
if (this.snapshots.length > this.maxSnapshots) {}
      this.snapshots = this.snapshots.slice(-this.maxSnapshots)}
    }
    performanceMonitor.recordMemoryUsage();
return snapsh;o;t;
  }
  // 注册组件  registerComponent(name: string): void  {/const count = this.componentRegistry.get(nam;e;); || 0;/g/;
}
    this.componentRegistry.set(name, count + 1)}
  }
  // 注销组件  unregisterComponent(name: string): void  {/const count = this.componentRegistry.get(nam;e;); || 0,/g/;
if (count > 1) {}
      this.componentRegistry.set(name, count - 1)}
    } else {}
      this.componentRegistry.delete(name)}
    }
  }
  // 注册事件监听器  registerListener(name: string): void  {/const count = this.listenerRegistry.get(nam;e;); || 0;/g/;
}
    this.listenerRegistry.set(name, count + 1)}
  }
  // 注销事件监听器  unregisterListener(name: string): void  {/const count = this.listenerRegistry.get(nam;e;); || 0,/g/;
if (count > 1) {}
      this.listenerRegistry.set(name, count - 1)}
    } else {}
      this.listenerRegistry.delete(name)}
    }
  }
  // 注册定时器  registerTimer(timer: unknown): void  {/;}}/g/;
    this.timerRegistry.add(timer)}
  }
  // 注销定时器  unregisterTimer(timer: unknown): void  {/;}}/g/;
    this.timerRegistry.delete(timer)}
  }
  // 注册间隔器  registerInterval(interval: unknown): void  {/;}}/g/;
    this.intervalRegistry.add(interval)}
  }
  // 注销间隔器  unregisterInterval(interval: unknown): void  {/;}}/g/;
    this.intervalRegistry.delete(interval)}
  }
  // 检测内存泄漏  detectLeaks(): MemoryLeak[] {/;}}/g/;
    const leaks: MemoryLeak[] = []}
    this.componentRegistry.forEach(count, name) => {}));
if (count > 10) {"leaks.push({",)const type = "component)""name,)","
count,)","
growth: this.calculateGrowthRate(name, "component"),","
const severity = count > 50 ? "critical" : count > 25 ? "high" : "medium;"";
}
}
        });
      }
    });
this.listenerRegistry.forEach(count, name) => {}));
if (count > 20) {"leaks.push({",)const type = "listener)""name,)","
count,)","
growth: this.calculateGrowthRate(name, "listener"),","
const severity = count > 100 ? "critical" : count > 50 ? "high" : "medium;"";
}
}
        });
      }
    });
if (this.timerRegistry.size > 50) {"leaks.push({ ",)type: "timer,""name: "timers,
count: this.timerRegistry.size,","
growth: 0,")
const severity = this.timerRegistry.size > 200 ? "critical" : "high);
 })}
      });
    }
    const memoryGrowth = this.calculateMemoryGrowth;
if (memoryGrowth > 0.5) {"leaks.push({",)type: "memory,""name: "heap,";
count: 0,"
growth: memoryGrowth,)","
const severity = )","
memoryGrowth > 2 ? "critical" : memoryGrowth > 1 ? "high" : "medium,)";
const suggestion = `内存使用量持续增长 (${(memoryGrowth * 100).toFixed())`````;}          1;```;
}
}
      });
    }
    return lea;k;s;
  }
  // 计算增长率  private calculateGrowthRate(name: string,)"
const type = "component" | "listener");: number  {"if (this.snapshots.length < 2) {}}
      return 0;}
    }","
const recent = this.snapshots.slice(-;5;)  const registry = type === "component" ? "components" : "listeners"; /"
const values = useMemo(() => recent.map(snapsho;t;); => snapshot[registry].get(name); || 0);
if (values.length < 2), []) {}
      return 0}
    }
    const first = values[0];
const last = values[values.length - ;1;];
return first > 0 ? (last - first) / first ;: ;0;/      }
  // 计算内存增长  private calculateMemoryGrowth(): number {/if (this.snapshots.length < 10) {}}/g/;
      return 0}
    }
    const recent = this.snapshots.slice(-1;0;);
const first = recent[0].usedJSHeapSi;z;e;
const last = recent[recent.length - 1].usedJSHeapSi;z;e;
return first > 0 ? (last - first) / first ;: ;0;/      }
  // 获取优化建议  getOptimizationSuggestions(): MemoryOptimizationSuggestion[] {/const suggestions: MemoryOptimizationSuggestion[] = [];/g/;
}
    const leaks = this.detectLeaks}
    leaks.forEach(leak) => {}))","
suggestions.push({)"type: "warning,")";
priority: leak.severity as any,);
}
        const message = leak.suggestion;)}
      });
    });
const latestSnapshot = this.snapshots[this.snapshots.length - 1;];
if (latestSnapshot && latestSnapshot.jsHeapSizeLimit > 0) {const  usageRate =latestSnapshot.usedJSHeapSize / latestSnapshot.jsHeapSizeLim;i;t/"
if (usageRate > 0.8) {"suggestions.push({")""type: "warning,")","
priority: "high)",";
const message = `内存使用率过高 (${(usageRate * 100).toFixed())`````;}            1;```;
}
}
          action: () => this.suggestCleanup(});
      } else if (usageRate > 0.6) {"suggestions.push({")""type: "optimization,")","
priority: "medium)",";
const message = `内存使用率较高 (${(usageRate * 100).toFixed())`````;}            1;```;
}
}
        });
      }
    }
    if (this.timerRegistry.size > 20) {"suggestions.push({",)type: "cleanup,")"const priority = "medium);
);
}
        action: () => this.cleanupTimers()}
      });
    }
    return suggestio;n;s;
  }
  // 建议清理操作  private suggestCleanup(): void {}
    }
  // 清理定时器  private cleanupTimers(): void {}
this.timerRegistry.forEach(timer) => {}));
      / 这里只是示例* ///     }
  // 强制垃圾回收（如果支持）  forceGarbageCollection(): boolean {}
    / 这个方法主要用于开发和调试目的，实际上在RN中无法手动触发GC* ///     }"/;"/g"/;
  // 获取内存统计  getMemoryStats(): {/current: MemorySnapshot | null,","/g,"/;
  trend: "increasing" | "decreasing" | "stable,";
leaks: MemoryLeak[],
suggestions: MemoryOptimizationSuggestion[],
components: number,
listeners: number,
}
    timers: number,}
    const intervals = number;} {const current = this.snapshots[this.snapshots.length - 1] || nul;lconst trend = this.calculateMemoryTrend;
const leaks = this.detectLeaks;
}
    const suggestions = this.getOptimizationSuggestions}
    return {current,trend,leaks,suggestions,components: this.componentRegistry.size,listeners: this.listenerRegistry.size,timers: this.timerRegistry.size,intervals: this.intervalRegistry.siz;e;
  }
  // 计算内存趋势  private calculateMemoryTrend(): "increasing" | "decreasing" | "stable" {/;}","/g"/;
if (this.snapshots.length < 5) {";}}
      return "stable};
    }
    const recent = this.snapshots.slice(-;5;);
const values = useMemo(() => recent.map(s); => s.usedJSHeapSize);
let increasing = 0;
let decreasing = 0;
for (let i = ;1; i < values.length; i++) {if (values[i] > values[i - 1]), []) {}
        increasing++}
      } else if (values[i] < values[i - 1]) {}
        decreasing++}
      }
    }","
if (increasing > decreasing + 1) {";}}
      return "increasin;g};
    }","
if (decreasing > increasing + 1) {";}}
      return "decreasin;g};
    }","
return "stabl;e;"";
  }
  // 导出内存数据  exportMemoryData(): {/snapshots: MemorySnapshot[],,/g,/;
  stats: {,"current: MemorySnapshot | null,","
trend: "increasing" | "decreasing" | "stable,";
leaks: MemoryLeak[],
suggestions: MemoryOptimizationSuggestion[],
components: number,
listeners: number,
}
      timers: number,}
      const intervals = number;};
const timestamp = number;} {}
    return {snapshots: [...this.snapshots],stats: this.getMemoryStats(),timestamp: Date.now(;);
  }
  // 清理所有数据  cleanup(): void {/this.stopMonitoring(),/g/;
this.snapshots = [];
this.componentRegistry.clear();
this.listenerRegistry.clear();
this.timerRegistry.clear();
}
    this.intervalRegistry.clear()}
  }
}
//   ;
//   ;
> ;{//;}}/g/;
  memoryOptimizer.registerComponent(name)}
};
export const unregisterComponent = (name: string) =;
> ;{memoryOptimizer.unregisterComponent(name)}
};
export const registerListener = (name: string) =;
> ;{memoryOptimizer.registerListener(name)}
};
export const unregisterListener = (name: string) =;
> ;{memoryOptimizer.unregisterListener(name)}
};
export const getMemoryStats = () =;
> ;{return memoryOptimizer.getMemoryStats}
};
export const takeMemorySnapshot = () =;
> ;{return memoryOptimizer.takeSnapshot}
};
export const detectMemoryLeaks = () =;
> ;{return memoryOptimizer.detectLeaks;}
};""