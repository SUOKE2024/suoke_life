/* 议 *//;/g/;
*//;,/g/;
export interface PerformanceMetric {name: string}value: number,;
unit: string,;
timestamp: number,;
const category = 'network' | 'rendering' | 'memory' | 'cpu' | 'user_interaction';';,'';
threshold?: number;';'';
}
}
  const status = 'good' | 'warning' | 'critical';'}'';'';
}
export interface PerformanceReport {timestamp: number}metrics: PerformanceMetric[],;
summary: {score: number,;
issues: string[],;
}
}
  const recommendations = string[];}
};
}
export class PerformanceMonitor {;,}private static instance: PerformanceMonitor;
private metrics: PerformanceMetric[] = [];
private observers: PerformanceObserver[] = [];
private isMonitoring = false;
private constructor() {}}
}
    this.setupPerformanceObservers();}
  }
  const public = static getInstance(): PerformanceMonitor {if (!PerformanceMonitor.instance) {}}
      PerformanceMonitor.instance = new PerformanceMonitor();}
    }
    return PerformanceMonitor.instance;
  }
  /* 控 *//;/g/;
  *//;,/g/;
const public = startMonitoring(): void {if (this.isMonitoring) return;,}this.isMonitoring = true;
this.collectInitialMetrics();
this.startPeriodicCollection();
}
}
  }
  /* 控 *//;/g/;
  *//;,/g/;
const public = stopMonitoring(): void {this.isMonitoring = false;,}this.observers.forEach(observer => observer.disconnect());
this.observers = [];
}
}
  }
  /* 标 *//;/g/;
  *//;,/g/;
const public = recordMetric();
name: string,;
value: number,';,'';
unit: string,';,'';
const category = PerformanceMetric['category'];';,'';
threshold?: number;
  ): void {const  metric: PerformanceMetric = {}      name,;
value,;
unit,;
const timestamp = Date.now();
category,;
}
      threshold,}
      status: this.getMetricStatus(value, threshold);};
this.metrics.push(metric);
this.trimMetrics();
  }
  /* 间 *//;/g/;
  *//;,/g/;
const public = async measureFunction<T>();
name: string,;
fn: () => Promise<T> | T;
  ): Promise<T> {const startTime = performance.now();,}try {const result = await fn();,}const duration = performance.now() - startTime;
}
      this.recordMetric()}
        `function_${name}`,``'`;,```;
duration,';'';
        "ms",cpu','';'';
        100, // 100ms threshold;/;/g/;
      );
return result;
    } catch (error) {const duration = performance.now() - startTime;}}
      this.recordMetric()}
        `function_${name}_error`,``'`;,```;
duration,';'';
        "ms",cpu','';'';
      );
const throw = error;
    }
  }
  /* 能 *//;/g/;
  *//;,/g,/;
  public: measureApiRequest(url: string, duration: number, status: number): void {}}
    this.recordMetric()}
      `api_request_${this.getUrlPath(url);}`,``'`;,```;
duration,';'';
      "ms",network','';'';
      2000, // 2s threshold;/;/g/;
    );
this.recordMetric();
      `api_status_${status}`,``'`;```;
      1,';'';
      "count",network','';'';
    );
  }
  /* 告 *//;/g/;
  *//;,/g/;
const public = getPerformanceReport(): PerformanceReport {const  recentMetrics = this.metrics.filter();,}metric => Date.now() - metric.timestamp < 60000, // 最近1分钟/;/g/;
    );
const score = this.calculatePerformanceScore(recentMetrics);
const issues = this.identifyIssues(recentMetrics);
const recommendations = this.generateRecommendations(issues);
return {timestamp: Date.now()}metrics: recentMetrics,;
const summary = {score,;}}
        issues,}
        recommendations;}};
  }
  /* 标 *//;/g/;
  *//;,/g/;
const public = getVitalMetrics(): {fcp: number; // First Contentful Paint,/;,}lcp: number; // Largest Contentful Paint,/;,/g,/;
  fid: number; // First Input Delay,/;,/g,/;
  cls: number; // Cumulative Layout Shift,/;/g/;
}
  const ttfb = number; // Time to First Byte; }/;/g/;
  } {const  getLatestMetric = useCallback((name: string) => {}      const metric = this.metrics;
        .filter(m => m.name === name);
        .sort(a, b) => b.timestamp - a.timestamp)[0];
}
      return metric?.value || 0;}
    };';,'';
return {';,}fcp: getLatestMetric('first_contentful_paint');','';
lcp: getLatestMetric('largest_contentful_paint');','';
fid: getLatestMetric('first_input_delay');','';'';
}
      cls: getLatestMetric('cumulative_layout_shift');','}';,'';
const ttfb = getLatestMetric('time_to_first_byte');};';'';
  }
  /* 况 *//;/g/;
  *//;,/g/;
const public = getMemoryUsage(): {used: number}total: number,;
}
  const percentage = number;}';'';
  } {';,}if ('memory' in performance) {';,}const memory = (performance as any).memory;,'';
return {used: memory.usedJSHeapSize,;}}
        total: memory.totalJSHeapSize,}
        const percentage = (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100;};/;/g/;
    }
    return { used: 0, total: 0, percentage: 0 ;};
  }
  /* 器 *//;/g/;
  */'/;,'/g'/;
private setupPerformanceObservers(): void {';,}if (typeof PerformanceObserver === 'undefined') return;';'';
    // 观察导航时间/;,/g/;
try {const  navObserver = new PerformanceObserver(list) => {';,}list.getEntries().forEach(entry) => {';,}if (entry.entryType === 'navigation') {';,}const navEntry = entry as PerformanceNavigationTiming;'';
}
            this.recordNavigationMetrics(navEntry);}
          }
        });';'';
      });';,'';
navObserver.observe({ entryTypes: ['navigation'] ;});';,'';
this.observers.push(navObserver);';'';
    } catch (e) {';}}'';
      console.warn('Navigation observer not supported');'}'';'';
    }
    // 观察资源加载时间/;,/g/;
try {const  resourceObserver = new PerformanceObserver(list) => {';,}list.getEntries().forEach(entry) => {';,}if (entry.entryType === 'resource') {';}}'';
            this.recordResourceMetric(entry as PerformanceResourceTiming);}
          }
        });';'';
      });';,'';
resourceObserver.observe({ entryTypes: ['resource'] ;});';,'';
this.observers.push(resourceObserver);';'';
    } catch (e) {';}}'';
      console.warn('Resource observer not supported');'}'';'';
    }
    // 观察用户交互/;,/g/;
try {const  interactionObserver = new PerformanceObserver(list) => {';,}list.getEntries().forEach(entry) => {';,}if (entry.entryType === 'event') {';}}'';
            this.recordInteractionMetric(entry as PerformanceEventTiming);}
          }
        });';'';
      });';,'';
interactionObserver.observe({ entryTypes: ['event'] ;});';,'';
this.observers.push(interactionObserver);';'';
    } catch (e) {';}}'';
      console.warn('Event observer not supported');'}'';'';
    }
  }
  /* 标 *//;/g/;
  *//;,/g/;
private collectInitialMetrics(): void {// 收集内存使用情况/;,}const memoryUsage = this.getMemoryUsage();,/g/;
if (memoryUsage.total > 0) {';,}this.recordMetric()';'';
        'memory_usage',';,'';
memoryUsage.percentage,';'';
        "%",memory','';'';
        80, // 80% threshold;/;/g/;
}
      );}
    }';'';
    // 收集连接信息'/;,'/g'/;
if ('connection' in navigator) {';,}const connection = (navigator as any).connection;';,'';
this.recordMetric()';'';
        'network_downlink',';,'';
connection.downlink,';'';
        "Mbps",network','';'';
}
      );}
    }
  }
  /* 集 *//;/g/;
  *//;,/g/;
private startPeriodicCollection(): void {setInterval() => {}      if (!this.isMonitoring) return;
}
      this.collectInitialMetrics();}
    }, 30000); // 每30秒收集一次/;/g/;
  }
  /* 标 *//;/g/;
  */'/;,'/g'/;
private recordNavigationMetrics(entry: PerformanceNavigationTiming): void {';,}this.recordMetric('dns_lookup', entry.domainLookupEnd - entry.domainLookupStart, "ms",network');'';
this.recordMetric('tcp_connect', entry.connectEnd - entry.connectStart, "ms",network');'';
this.recordMetric('request_response', entry.responseEnd - entry.requestStart, "ms",network');'';
this.recordMetric('dom_loading', entry.domContentLoadedEventEnd - entry.domLoading, "ms",rendering');'';'';
}
    this.recordMetric('page_load', entry.loadEventEnd - entry.loadEventStart, "ms",rendering');'}'';'';
  }
  /* 标 *//;/g/;
  *//;,/g/;
private recordResourceMetric(entry: PerformanceResourceTiming): void {const duration = entry.responseEnd - entry.startTime;,}const resourceType = this.getResourceType(entry.name);
}
    this.recordMetric()}
      `resource_${resourceType}`,``'`;,```;
duration,';'';
      "ms",network','';'';
      1000, // 1s threshold;/;/g/;
    );
  }
  /* 标 *//;/g/;
  *//;,/g/;
private recordInteractionMetric(entry: PerformanceEventTiming): void {}}
    this.recordMetric()}
      `interaction_${entry.name;}`,``'`;,```;
entry.duration,';'';
      "ms",user_interaction','';'';
      100, // 100ms threshold;/;/g/;
    );
  }
  /* ' *//;'/g'/;
  */'/;,'/g'/;
private getMetricStatus(value: number, threshold?: number): PerformanceMetric['status'] {';,}if (!threshold) return 'good';';,'';
if (value > threshold * 2) return 'critical';';,'';
if (value > threshold) return 'warning';';'';
}
    return 'good';'}'';'';
  }
  /* 数 *//;/g/;
  *//;,/g/;
private calculatePerformanceScore(metrics: PerformanceMetric[]): number {if (metrics.length === 0) return 100;,}const  weights = {good: 1,;}}
      warning: 0.7,}
      const critical = 0.3;};
totalWeight: metrics.reduce(sum, metric) => sum + weights[metric.status], 0);
const maxWeight = metrics.length;
return Math.round(totalWeight / maxWeight) * 100);/;/g/;
  }
  /* 题 *//;/g/;
  *//;,/g/;
private identifyIssues(metrics: PerformanceMetric[]): string[] {';,}const issues: string[] = [];';,'';
const criticalMetrics = metrics.filter(m => m.status === 'critical');';,'';
const warningMetrics = metrics.filter(m => m.status === 'warning');';,'';
if (criticalMetrics.length > 0) {}}
}
    }
    if (warningMetrics.length > 0) {}}
}
    }';'';
    // 检查特定问题'/;,'/g'/;
const memoryMetric = metrics.find(m => m.name === 'memory_usage');';,'';
if (memoryMetric && memoryMetric.value > 90) {}}
}';'';
    }';,'';
const apiMetrics = metrics.filter(m => m.name.startsWith('api_request_'));';,'';
const slowApis = apiMetrics.filter(m => m.value > 3000);
if (slowApis.length > 0) {}}
}
    }
    return issues;
  }
  /* 议 *//;/g/;
  *//;,/g/;
private generateRecommendations(issues: string[]): string[] {const recommendations: string[] = [];}}
}';'';
    }';,'';
if (issues.some(issue => issue.includes('API'))) {';}}'';
}
    }

    }
    if (recommendations.length === 0) {}}
}
    }
    return recommendations;
  }
  /* 径 *//;/g/;
  *//;,/g/;
private getUrlPath(url: string): string {';,}try {';}}'';
      return new URL(url).pathname.replace(/\//g, '_').slice(1) || 'root';'}''/;'/g'/;
    } catch {';}}'';
      return 'unknown';'}'';'';
    }
  }
  /* 型 *//;/g/;
  */'/;,'/g'/;
private getResourceType(url: string): string {';,}const extension = url.split('.').pop()?.toLowerCase();';,'';
if (["js",ts'].includes(extension || ')) return 'script';';,'';
if (['css'].includes(extension || ')) return 'style';'';
if (["png",jpg', "jpeg",gif', 'svg'].includes(extension || ')) return 'image';'';
if (["woff",woff2', 'ttf'].includes(extension || ')) return 'font';';'';
}
    return 'other';'}'';'';
  }
  /* 标 *//;/g/;
  *//;,/g/;
private trimMetrics(): void {const maxAge = 5 * 60 * 1000; // 5分钟/;,}const cutoff = Date.now() - maxAge;/g/;
}
    this.metrics = this.metrics.filter(metric => metric.timestamp > cutoff);}
  }
}
// 导出单例实例'/;,'/g'/;
export const performanceMonitor = PerformanceMonitor.getInstance();