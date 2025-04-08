import { PerformanceMonitor } from './PerformanceMonitor';

export type {
  PerformanceMetrics,
  QueryProfile,
  PerformanceThresholds
} from './PerformanceMonitor';

// 导出主要类
export { PerformanceMonitor };

// 导出工厂函数
export const getPerformanceMonitor = () => PerformanceMonitor.getInstance();

// 导出实用函数
export const initializeMonitoring = (config?: {
  alertCallback?: (alert: any) => void;
  customThresholds?: Partial<PerformanceThresholds>;
}) => {
  const monitor = getPerformanceMonitor();
  
  if (config?.alertCallback) {
    monitor.onAlert(config.alertCallback);
  }
  
  return monitor;
};

// 导出监控装饰器
export function MonitorQuery(queryId: string) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const monitor = getPerformanceMonitor();
      
      try {
        // 提取查询信息
        const query = args[0];
        const parameters = args[1] || {};
        
        // 监控查询执行
        const metrics = await monitor.monitorQuery(queryId, query, parameters);
        
        // 执行原始方法
        const result = await originalMethod.apply(this, args);
        
        return result;
      } catch (error) {
        // 记录错误并重新抛出
        logger.error(`查询执行失败 [${queryId}]:`, error);
        throw error;
      }
    };

    return descriptor;
  };
}

// 导出监控中间件
export const monitoringMiddleware = (queryId: string) => {
  return async (
    request: any,
    reply: any,
    next: () => Promise<void>
  ) => {
    const startTime = process.hrtime();
    const startMemory = process.memoryUsage().heapUsed;

    try {
      await next();

      const [seconds, nanoseconds] = process.hrtime(startTime);
      const queryTime = seconds * 1000 + nanoseconds / 1e6;
      const memoryUsage = process.memoryUsage().heapUsed - startMemory;

      const monitor = getPerformanceMonitor();
      await monitor.monitorQuery(queryId, request.raw.url, {
        method: request.method,
        headers: request.headers,
        query: request.query,
        body: request.body
      });
    } catch (error) {
      logger.error(`API请求监控失败 [${queryId}]:`, error);
      throw error;
    }
  };
};

// 导出监控工具函数
export const monitoringUtils = {
  /**
   * 生成性能报告
   */
  generatePerformanceReport: async (queryId: string, timeRange?: {
    start: Date;
    end: Date;
  }) => {
    const monitor = getPerformanceMonitor();
    const report = monitor.getQueryReport(queryId);
    
    if (timeRange) {
      const trends = monitor.getPerformanceTrends(queryId, timeRange);
      return { ...report, trends };
    }
    
    return report;
  },

  /**
   * 批量监控多个查询
   */
  monitorQueries: async (queries: Array<{
    queryId: string;
    query: string;
    parameters?: Record<string, any>;
  }>) => {
    const monitor = getPerformanceMonitor();
    const results = new Map();

    for (const { queryId, query, parameters = {} } of queries) {
      try {
        const metrics = await monitor.monitorQuery(queryId, query, parameters);
        results.set(queryId, { success: true, metrics });
      } catch (error) {
        results.set(queryId, { success: false, error });
      }
    }

    return results;
  }
};

// 导出常用的监控配置
export const monitoringConfigs = {
  // 默认的API监控配置
  defaultApiMonitoring: {
    queryId: 'api_request',
    thresholds: {
      maxQueryTime: 2000,    // 2秒
      maxMemoryUsage: 5e7,   // 50MB
      maxResultCount: 5000   // 5000条结果
    }
  },
  
  // 默认的数据库查询监控配置
  defaultDbMonitoring: {
    queryId: 'db_query',
    thresholds: {
      maxQueryTime: 1000,    // 1秒
      maxMemoryUsage: 1e8,   // 100MB
      maxResultCount: 10000  // 10000条结果
    }
  },
  
  // 默认的缓存操作监控配置
  defaultCacheMonitoring: {
    queryId: 'cache_operation',
    thresholds: {
      maxQueryTime: 100,     // 100毫秒
      maxMemoryUsage: 1e7,   // 10MB
      maxResultCount: 1000   // 1000条结果
    }
  }
};