/**
 * 指标监控工具
 */
import { Request, Response, NextFunction } from 'express';
import NodeCache from 'node-cache';
import logger from './logger';

class MetricsCollector {
  private cache: NodeCache;
  private apiCalls: Record<string, number> = {};
  private responseLatency: Record<string, number[]> = {};
  private agentCalls: Record<string, number> = {};
  private knowledgeServiceCalls: Record<string, number> = {};
  private errorCounts: Record<string, number> = {};
  
  constructor() {
    this.cache = new NodeCache({ stdTTL: 3600 }); // 1小时过期
    
    // 每小时保存一次指标到磁盘（此处仅记录日志，实际实现可以存储到数据库）
    setInterval(() => {
      this.saveMetrics();
    }, 60 * 60 * 1000);
  }
  
  /**
   * 记录API调用
   */
  recordApiCall(path: string): void {
    if (!this.apiCalls[path]) {
      this.apiCalls[path] = 0;
    }
    this.apiCalls[path]++;
  }
  
  /**
   * 记录响应延迟
   */
  recordLatency(path: string, latencyMs: number): void {
    if (!this.responseLatency[path]) {
      this.responseLatency[path] = [];
    }
    this.responseLatency[path].push(latencyMs);
  }
  
  /**
   * 记录代理调用
   */
  recordAgentCall(agentId: string): void {
    if (!this.agentCalls[agentId]) {
      this.agentCalls[agentId] = 0;
    }
    this.agentCalls[agentId]++;
  }
  
  /**
   * 记录知识服务调用
   */
  recordKnowledgeServiceCall(service: string): void {
    if (!this.knowledgeServiceCalls[service]) {
      this.knowledgeServiceCalls[service] = 0;
    }
    this.knowledgeServiceCalls[service]++;
  }
  
  /**
   * 记录错误
   */
  recordError(errorCode: string): void {
    if (!this.errorCounts[errorCode]) {
      this.errorCounts[errorCode] = 0;
    }
    this.errorCounts[errorCode]++;
  }
  
  /**
   * 获取当前指标
   */
  getMetrics(): Record<string, any> {
    const latencyAverages: Record<string, number> = {};
    
    // 计算每个路径的平均延迟
    Object.keys(this.responseLatency).forEach((path) => {
      const latencies = this.responseLatency[path];
      if (latencies.length > 0) {
        const sum = latencies.reduce((a, b) => a + b, 0);
        latencyAverages[path] = Math.round(sum / latencies.length);
      }
    });
    
    return {
      apiCalls: this.apiCalls,
      latencyAverages,
      agentCalls: this.agentCalls,
      knowledgeServiceCalls: this.knowledgeServiceCalls,
      errorCounts: this.errorCounts,
      timestamp: new Date().toISOString(),
    };
  }
  
  /**
   * 保存指标
   */
  private saveMetrics(): void {
    const metrics = this.getMetrics();
    logger.info('服务指标数据', { metrics });
    
    // 重置计数器
    this.apiCalls = {};
    this.responseLatency = {};
    this.errorCounts = {};
    
    // 保存历史记录，实际实现中可以存储到数据库
    const timestamp = new Date().toISOString().replace(/:/g, '-');
    this.cache.set(`metrics_${timestamp}`, metrics);
  }
}

// 创建单例实例
export const metricsCollector = new MetricsCollector();

/**
 * 指标中间件 - 用于记录API调用和响应时间
 */
export function metricsMiddleware(req: Request, res: Response, next: NextFunction): void {
  const startTime = Date.now();
  const path = req.baseUrl + req.path;
  
  // 记录API调用
  metricsCollector.recordApiCall(path);
  
  // 添加响应结束监听器，记录响应时间
  res.on('finish', () => {
    const latencyMs = Date.now() - startTime;
    metricsCollector.recordLatency(path, latencyMs);
    
    // 如果是错误响应，记录错误
    if (res.statusCode >= 400) {
      metricsCollector.recordError(`HTTP_${res.statusCode}`);
    }
  });
  
  next();
} 