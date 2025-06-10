import { performanceMonitor } from "./performanceMonitor";""/;,"/g"/;
import { configService } from "./configService";""/;"/g"/;
// 事件类型定义/;,/g/;
export interface AnalyticsEvent {";,}id: string,';,'';
type: 'api_call' | 'error' | 'performance' | 'user_action' | 'system';','';
timestamp: number,;
data: Record<string, any>;
userId?: string;
const sessionId = string;
service?: string;
}
}
  endpoint?: string;}
}
// 性能指标/;,/g/;
export interface PerformanceMetrics {responseTime: number}throughput: number,;
errorRate: number,;
cacheHitRate: number,;
memoryUsage: number,;
}
}
  const cpuUsage = number;}
}
// 用户行为数据/;,/g/;
export interface UserBehavior {userId: string}sessionId: string,;
actions: string[],;
duration: number,;
screens: string[],;
}
}
  const errors = number;}
}
// 服务使用统计/;,/g/;
export interface ServiceUsage {service: string}calls: number,;
errors: number,;
avgResponseTime: number,;
}
}
  const lastUsed = number;}
}
// 分析配置/;,/g/;
interface AnalyticsConfig {enabled: boolean}batchSize: number,;
flushInterval: number,;
maxEvents: number,;
enableUserTracking: boolean,;
enablePerformanceTracking: boolean,;
}
}
  const enableErrorTracking = boolean;}
}
class AnalyticsService {private events: AnalyticsEvent[] = [];,}private sessionId: string;
private userId?: string;
private config: AnalyticsConfig;
private flushTimer?: NodeJS.Timeout;
private performanceObserver?: PerformanceObserver;
constructor() {this.sessionId = this.generateSessionId();,}this.config = {enabled: true}batchSize: 50,;
flushInterval: 30000, // 30秒/;,/g,/;
  maxEvents: 1000,;
enableUserTracking: true,;
enablePerformanceTracking: true,;
}
}
      const enableErrorTracking = true;}
    };
this.initializePerformanceTracking();
this.startFlushTimer();
  }
  // 生成会话ID;/;,/g/;
private generateSessionId(): string {}
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  // 生成事件ID;/;,/g/;
private generateEventId(): string {}
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  // 初始化性能跟踪'/;,'/g'/;
private initializePerformanceTracking() {';,}if (!this.config.enablePerformanceTracking || typeof PerformanceObserver === 'undefined') {';}}'';
      return;}
    }
    try {this.performanceObserver = new PerformanceObserver(list) => {}        const entries = list.getEntries();';,'';
entries.forEach(entry) => {';,}this.trackEvent('performance', {';,)name: entry.name}duration: entry.duration,);,'';
startTime: entry.startTime,);
}
            const entryType = entry.entryType;)}
          });
        });';'';
      });';,'';
this.performanceObserver.observe({ entryTypes: ["measure",navigation', 'resource'] ;});'';'';
    } catch (error) {';}}'';
      console.warn('Performance tracking not supported:', error);'}'';'';
    }
  }
  // 启动定时刷新/;,/g/;
private startFlushTimer() {this.flushTimer = setInterval() => {}}
      this.flush();}
    }, this.config.flushInterval);
  }
  // 设置用户ID;/;,/g/;
setUserId(userId: string) {';,}this.userId = userId;';,'';
this.trackEvent('user_action', {')'';,}const action = 'login';')'';'';
}
      userId;)}
    });
  }
  // 清除用户ID;/;,/g/;
clearUserId() {';,}if (this.userId) {';,}this.trackEvent('user_action', {')'';,}action: "logout";",")"";"";
}
      const userId = this.userId;)}
      });
    }
    this.userId = undefined;
  }";"";
  // 跟踪事件"/;,"/g"/;
trackEvent(type: AnalyticsEvent['type'], data: Record<string, any>, service?: string; endpoint?: string) {';,}if (!this.config.enabled) return;,'';
const: event: AnalyticsEvent = {const id = this.generateEventId();
type,;
const timestamp = Date.now();
data,;
userId: this.userId,;
const sessionId = this.sessionId;
service,;
}
      endpoint;}
    };
this.events.push(event);
    // 如果事件过多，移除旧事件/;,/g/;
if (this.events.length > this.config.maxEvents) {}}
      this.events = this.events.slice(-this.config.maxEvents);}
    }
    // 如果达到批次大小，立即刷新/;,/g/;
if (this.events.length >= this.config.batchSize) {}}
      this.flush();}
    }
  }
  // 跟踪API调用'/;,'/g'/;
trackApiCall(service: string, endpoint: string, method: string, responseTime: number, status: number) {';,}this.trackEvent('api_call', {';,)method}responseTime,);,'';
status,);
}
      success: status >= 200 && status < 300;)}
    }, service, endpoint);
  }
  // 跟踪错误/;,/g/;
trackError(error: Error, context?: Record<string; any>) {';,}if (!this.config.enableErrorTracking) return;';,'';
this.trackEvent('error', {';,)message: error.message}stack: error.stack,);,'';
const name = error.name;);
}
      context;)}
    });
  }
  // 跟踪用户行为/;,/g/;
trackUserAction(action: string, data?: Record<string; any>) {';,}if (!this.config.enableUserTracking) return;';,'';
this.trackEvent('user_action', {')'';,}action,);'';
}
      ...data;)}
    });
  }
  // 跟踪页面访问'/;,'/g'/;
trackPageView(screen: string, data?: Record<string; any>) {';,}this.trackEvent('user_action', {';,)const action = 'page_view';')'';,}screen,);'';
}
      ...data;)}
    });
  }
  // 获取性能指标'/;,'/g'/;
getPerformanceMetrics(): PerformanceMetrics {';,}const apiEvents = this.events.filter(e => e.type === 'api_call');';,'';
const errorEvents = this.events.filter(e => e.type === 'error');';,'';
const responseTimes = useMemo(() => apiEvents.map(e => e.data.responseTime).filter(Boolean);
const avgResponseTime = responseTimes.length > 0;
      ? responseTimes.reduce(a, b) => a + b, 0) / responseTimes.length;/;/g/;
      : 0;
const errorRate = apiEvents.length > 0;
      ? (errorEvents.length / apiEvents.length) * 100;/;/g/;
      : 0;
return {responseTime: avgResponseTime}const throughput = apiEvents.length;
errorRate,;
cacheHitRate: this.calculateCacheHitRate(),;
memoryUsage: this.getMemoryUsage(), []),;
}
      const cpuUsage = 0 // 浏览器环境无法获取CPU使用率}/;/g/;
    ;};
  }
  // 计算缓存命中率/;,/g/;
private calculateCacheHitRate(): number {';,}const  cacheEvents = this.events.filter(e =>)';,'';
e.type === 'api_call' && e.data.fromCache !== undefined;';'';
    );
if (cacheEvents.length === 0) return 0;
const hits = cacheEvents.filter(e => e.data.fromCache).length;
}
    return (hits / cacheEvents.length) * 100;}/;/g/;
  }
  // 获取内存使用情况'/;,'/g'/;
private getMemoryUsage(): number {';,}if (typeof performance !== 'undefined' && (performance as any).memory) {';,}const memory = (performance as any).memory;'';
}
      return memory.usedJSHeapSize / memory.totalJSHeapSize * 100;}/;/g/;
    }
    return 0;
  }
  // 获取用户行为数据/;,/g/;
getUserBehavior(): UserBehavior[] {userSessions: new Map<string, UserBehavior>();';,}this.events;';'';
      .filter(e => e.type === 'user_action' && e.userId)';'';
}
      .forEach(event => {)}
        const key = `${event.userId}_${event.sessionId}`;`)```;,```;
if (!userSessions.has(key)) {userSessions.set(key, {)            userId: event.userId!}sessionId: event.sessionId,;
actions: [],;
duration: 0,);
screens: [],);
}
            const errors = 0;)}
          });
        }
        const behavior = userSessions.get(key)!;
behavior.actions.push(event.data.action);
if (event.data.screen && !behavior.screens.includes(event.data.screen)) {}}
          behavior.screens.push(event.data.screen);}
        }
      });
    // 计算会话持续时间/;,/g/;
userSessions.forEach(behavior, key) => {const  sessionEvents = this.events.filter(e =>);,}e.userId === behavior.userId && e.sessionId === behavior.sessionId;
      );
if (sessionEvents.length > 1) {const timestamps = useMemo(() => sessionEvents.map(e => e.timestamp);}}
        behavior.duration = Math.max(...timestamps) - Math.min(...timestamps), []);}
      }
      // 计算错误数量'/;,'/g'/;
behavior.errors = this.events.filter(e =>)';,'';
e.type === 'error' && e.userId === behavior.userId && e.sessionId === behavior.sessionId;';'';
      ).length;
    });
return Array.from(userSessions.values());
  }
  // 获取服务使用统计/;,/g/;
getServiceUsage(): ServiceUsage[] {serviceStats: new Map<string, ServiceUsage>();';,}this.events;';'';
      .filter(e => e.type === 'api_call' && e.service)';'';
      .forEach(event => {);,}const service = event.service!;);
if (!serviceStats.has(service)) {serviceStats.set(service, {)            service}calls: 0,;
errors: 0,);
avgResponseTime: 0,);
}
            const lastUsed = 0;)}
          });
        }
        const stats = serviceStats.get(service)!;
stats.calls++;
stats.lastUsed = Math.max(stats.lastUsed, event.timestamp);
if (!event.data.success) {}}
          stats.errors++;}
        }
        if (event.data.responseTime) {}}
          stats.avgResponseTime = (stats.avgResponseTime * (stats.calls - 1) + event.data.responseTime) / stats.calls;}/;/g/;
        }
      });
return Array.from(serviceStats.values());
  }
  // 获取事件统计/;,/g/;
getEventStats(): Record<string, number> {}
    const stats: Record<string, number> = {;};
this.events.forEach(event => {));}}
      stats[event.type] = (stats[event.type] || 0) + 1;}
    });
return stats;
  }
  // 刷新事件到服务器/;,/g/;
const async = flush(): Promise<void> {if (this.events.length === 0) return;,}const eventsToSend = [...this.events];
this.events = [];
try {// 这里应该发送到分析服务器'/;}      // 目前只是记录到控制台'/;,'/g'/;
if (process.env.NODE_ENV === 'development') {';}}'';
        console.log('Analytics events:', eventsToSend);'}'';'';
      }
      // 实际实现中应该调用API;/;/g/;
      // await this.sendToAnalyticsServer(eventsToSend);'/;'/g'/;
    } catch (error) {';,}console.error('Failed to send analytics events:', error);';'';
      // 失败时重新添加事件/;/g/;
}
      this.events.unshift(...eventsToSend);}
    }
  }
  // 发送到分析服务器（示例实现）/;,/g/;
private async sendToAnalyticsServer(events: AnalyticsEvent[]): Promise<void> {';}    // 实际实现中应该调用真实的分析API;'/;,'/g,'/;
  const: response = await fetch('/api/analytics/events', {'/;,)method: "POST";","";,}const headers = {")"";}}"/g"/;
        'Content-Type': 'application/json')}''/;'/g'/;
      ;},);
const body = JSON.stringify({ events ;});
    });
if (!response.ok) {}
      const throw = new Error(`Analytics API error: ${response.status;}`);````;```;
    }
  }
  // 更新配置/;,/g/;
updateConfig(newConfig: Partial<AnalyticsConfig>) {}
    this.config = { ...this.config, ...newConfig ;};
  }
  // 获取配置/;,/g/;
getConfig(): AnalyticsConfig {}
    return { ...this.config };
  }
  // 清理资源/;,/g/;
destroy() {if (this.flushTimer) {}}
      clearInterval(this.flushTimer);}
    }
    if (this.performanceObserver) {}}
      this.performanceObserver.disconnect();}
    }
    this.flush();
  }
}
// 导出单例实例'/;,'/g'/;
export const analyticsService = new AnalyticsService();