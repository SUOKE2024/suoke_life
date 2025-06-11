import { useCallback, useEffect, useRef, useState } from "react";
// 扩展Performance接口以支持内存监控
const declare = global {interface Performance {}    memory?: {usedJSHeapSize: number}totalJSHeapSize: number,
}
}
      const jsHeapSizeLimit = number}
    };
  }
}
// 性能监控配置接口
interface PerformanceMonitorConfig {
trackRender?: booleantrackMemory?: boolean;
trackNetwork?: boolean;
warnThreshold?: number; // 毫秒
errorThreshold?: number; // 毫秒
sampleRate?: number; // 采样率 0-1,
}
  enableLogging?: boolean}
}
// 性能指标接口
interface PerformanceMetrics {renderTime: number}memoryUsage: number,
networkLatency: number,
componentMountTime: number,
updateCount: number,
}
}
  const errorCount = number}
}
// 性能事件接口"
export interface PerformanceEvent {";
'type: 'render' | 'memory' | 'network' | 'error' | 'warning,'';
const timestamp = number;
duration?: number;
value?: number;
}
  metadata?: Record<string; any>}
}
// 默认配置/,/g,/;
  const: DEFAULT_CONFIG: PerformanceMonitorConfig = {trackRender: true,
trackMemory: false,
trackNetwork: false,
warnThreshold: 16, // 60fps = 16.67ms per frame,/,/g,/;
  errorThreshold: 100,
sampleRate: 1.0,
}
  const enableLogging = __DEV__ || false}
};
/* 能 */
 */
export usePerformanceMonitor: (componentName: string,);
config: Partial<PerformanceMonitorConfig> = {;});
) => {}
  finalConfig: { ...DEFAULT_CONFIG, ...config };
const mountTimeRef = useRef<number>(Date.now());
const renderCountRef = useRef<number>(0);
const lastRenderTimeRef = useRef<number>(0);
const  metricsRef = useRef<PerformanceMetrics>({)renderTime: 0}memoryUsage: 0,
networkLatency: 0,
componentMountTime: 0,);
updateCount: 0,);
}
    const errorCount = 0;)}
  });
const eventsRef = useRef<PerformanceEvent[]>([]);
const [isMonitoring, setIsMonitoring] = useState<boolean>(false);
  // 记录性能事件
const  recordEvent = useCallback();
    (event: PerformanceEvent) => {if (Math.random() > finalConfig.sampleRate!) returneventsRef.current.push(event);
      // 保持事件队列大小
if (eventsRef.current.length > 1000) {}
        eventsRef.current = eventsRef.current.slice(-500)}
      }
      // 日志记录'
if (finalConfig.enableLogging) {'const  logLevel ='
event.type === 'error'
            ? 'error'
            : event.type === 'warning'
              ? 'warn'
}
              : 'log}'';
console[logLevel](`[PerformanceMonitor: ${componentName;}]`, event);````;```;
      }
      // 阈值检查'
if (event.duration) {if (event.duration > finalConfig.errorThreshold!) {';}          // 避免无限递归，只记录原始错误'/,'/g'/;
if (event.type !== 'error') {'eventsRef.current.push({)'type: 'error,)'';
timestamp: Date.now(),
metadata: {originalEvent: event,
}
                threshold: finalConfig.errorThreshold,}
                message: `Performance threshold exceeded: ${event.duration;}ms > ${finalConfig.errorThreshold}ms`,````;```;
              }
            });
          }
        } else if (event.duration > finalConfig.warnThreshold! &&)'
event.type !== 'warning')'
        ) {'eventsRef.current.push({)'type: 'warning,)'';
timestamp: Date.now(),
metadata: {originalEvent: event,
}
              threshold: finalConfig.warnThreshold,}
              message: `Performance warning: ${event.duration;}ms > ${finalConfig.warnThreshold}ms`,````;```;
            }
          });
        }
      }
    }
    [componentName, finalConfig];
  );
  // 记录渲染性能
const  recordRender = useCallback(() => {if (!finalConfig.trackRender) returnconst now = performance.now();
const renderTime = now - lastRenderTimeRef.current;
renderCountRef.current += 1;
lastRenderTimeRef.current = now;
metricsRef.current.renderTime = renderTime;
metricsRef.current.updateCount = renderCountRef.current;
recordEvent({)'type: 'render,)'';
timestamp: Date.now(),
duration: renderTime,
metadata: {const renderCount = renderCountRef.current;
}
        componentName,}
      }
    });
  }, [componentName, finalConfig.trackRender, recordEvent]);
  // 记录内存使用
const  recordMemory = useCallback(() => {if (!finalConfig.trackMemory) returntry {// React Native中获取内存信息的方法/if (global.performance?.memory) {const memoryInfo = global.performance.memorymemoryUsage: memoryInfo.usedJSHeapSize / 1024 / 1024; // MB,
metricsRef.current.memoryUsage = memoryUsage;
recordEvent({)'type: 'memory,)'';
timestamp: Date.now(),
value: memoryUsage,
metadata: {totalJSHeapSize: memoryInfo.totalJSHeapSize / 1024 / 1024,
const jsHeapSizeLimit = memoryInfo.jsHeapSizeLimit / 1024 / 1024;
}
            componentName,}
          }
        });
      } else {// 使用React Native的JSC内存监控（如果可用）/const memoryUsage = (global as any).nativePerformanceNow?.() || 0,/g/;
if (memoryUsage > 0) {metricsRef.current.memoryUsage = memoryUsage;'recordEvent({)'type: 'memory,)'';
timestamp: Date.now(),
value: memoryUsage,'
metadata: {,'const source = 'nativePerformanceNow';
}
              componentName,}
            }
          });
        }
      }
    } catch (error) {'console.warn('[PerformanceMonitor] Memory tracking not available: )'';
error);
}
      )}
    }
  }, [componentName, finalConfig.trackMemory, recordEvent]);
  // 记录网络性能
const  recordNetwork = useCallback();
    (url: string, duration: number, success: boolean = true) => {if (!finalConfig.trackNetwork) returnmetricsRef.current.networkLatency = duration;
recordEvent({)'type: 'network,)'';
const timestamp = Date.now();
duration,
const metadata = {url}success,
}
          componentName,}
        }
      });
    }
    [componentName, finalConfig.trackNetwork, recordEvent];
  );
  // 记录效果性能
const  recordEffect = useCallback();
    (duration: number) => {'recordEvent({)'type: 'render,)'';
const timestamp = Date.now();
duration,'
metadata: {,'const type = 'effect';
}
          componentName,}
        }
      });
    }
    [componentName, recordEvent];
  );
  // 记录指标
const  recordMetric = useCallback();
    (name: string, value: number, metadata?: Record<string; any>) => {'recordEvent({)'type: 'render,)'';
const timestamp = Date.now();
value,
metadata: {const metricName = name;
componentName,
}
          ...metadata,}
        }
      });
    }
    [componentName, recordEvent];
  );
  // 记录错误
const  recordError = useCallback();
    (error: Error, metadata?: Record<string; any>) => {metricsRef.current.errorCount += 1}
recordEvent({)'type: 'error,)'';
timestamp: Date.now(),
metadata: {error: {name: error.name,
message: error.message,
}
            const stack = error.stack}
          }
componentName,
          ...metadata,
        }
      });
    }
    [componentName, recordEvent];
  );
  // 开始监控
const  startMonitoring = useCallback(() => {setIsMonitoring(true)}
    mountTimeRef.current = Date.now()}
  }, []);
  // 停止监控
const  stopMonitoring = useCallback(() => {}
    setIsMonitoring(false)}
  }, []);
  // 获取性能指标
const  getMetrics = useCallback((): PerformanceMetrics => {}
    return { ...metricsRef.current };
  }, []);
  // 获取性能事件
const  getEvents = useCallback((): PerformanceEvent[] => {}
    return [...eventsRef.current]}
  }, []);
  // 清除数据
const  clearData = useCallback(() => {eventsRef.current = []metricsRef.current = {renderTime: 0}memoryUsage: 0,
networkLatency: 0,
componentMountTime: 0,
updateCount: 0,
}
      const errorCount = 0}
    };
renderCountRef.current = 0;
  }, []);
  // 获取性能摘要'
const  getPerformanceSummary = useCallback(() => {const events = eventsRef.current;'const  renderEvents = events.filter(')'
      (e) => e.type === 'render' && e.duration
    );
const memoryEvents = events.filter((e) => e.type === 'memory' && e.value);
const  networkEvents = events.filter(')'
      (e) => e.type === 'network' && e.duration
    );
const  avgRenderTime =;
renderEvents.length > 0;
        ? renderEvents.reduce((sum, e) => sum + (e.duration || 0), 0) /
renderEvents.length;
        : 0;
const  avgMemoryUsage =;
memoryEvents.length > 0;
        ? memoryEvents.reduce((sum, e) => sum + (e.value || 0), 0) /
memoryEvents.length;
        : 0;
const  avgNetworkLatency =;
networkEvents.length > 0;
        ? networkEvents.reduce((sum, e) => sum + (e.duration || 0), 0) /
networkEvents.length;
        : 0;
return {componentName}const totalEvents = events.length;
avgRenderTime,
avgMemoryUsage,
avgNetworkLatency,'
errorCount: events.filter((e) => e.type === 'error').length;','
warningCount: events.filter((e) => e.type === 'warning').length;','
}
      const uptime = Date.now() - mountTimeRef.current}
    };
  }, [componentName]);
  // 组件挂载时开始监控
useEffect(() => {startMonitoring()return () => {}
      stopMonitoring()}
    };
  }, [startMonitoring, stopMonitoring]);
  // 定期内存监控
useEffect(() => {if (!finalConfig.trackMemory) returnconst  interval = setInterval(() => {}
      recordMemory()}
    }, 5000); // 每5秒检查一次内存
return () => clearInterval(interval);
  }, [finalConfig.trackMemory, recordMemory]);
return {recordRender}recordMemory,
recordNetwork,
recordEffect,
recordMetric,
recordError,
startMonitoring,
stopMonitoring,
getMetrics,
getEvents,
getPerformanceSummary,
clearData,
isMonitoring,
metrics: metricsRef.current,
}
    const events = eventsRef.current}
  };
};
export default usePerformanceMonitor;
''