import { Session } from 'neo4j-driver';
import Neo4jConnection from '../database/neo4j';
import logger from '../logger';

export interface PerformanceMetrics {
  queryTime: number;
  resultCount: number;
  memoryUsage: number;
  timestamp: Date;
}

export interface QueryProfile {
  queryId: string;
  query: string;
  parameters: Record<string, any>;
  metrics: PerformanceMetrics;
  executionPlan?: any;
}

export interface PerformanceThresholds {
  maxQueryTime: number;      // 毫秒
  maxMemoryUsage: number;    // 字节
  maxResultCount: number;    // 结果数量
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, PerformanceMetrics[]>;
  private queryProfiles: Map<string, QueryProfile>;
  private alertCallbacks: ((alert: any) => void)[];
  
  private readonly DEFAULT_THRESHOLDS: PerformanceThresholds = {
    maxQueryTime: 1000,      // 1秒
    maxMemoryUsage: 1e8,     // 100MB
    maxResultCount: 10000    // 1万条结果
  };

  private constructor() {
    this.metrics = new Map();
    this.queryProfiles = new Map();
    this.alertCallbacks = [];
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  /**
   * 监控查询执行
   */
  public async monitorQuery(
    queryId: string,
    query: string,
    parameters: Record<string, any>
  ): Promise<PerformanceMetrics> {
    const startTime = process.hrtime();
    const startMemory = process.memoryUsage().heapUsed;
    
    const session = this.getSession();
    let resultCount = 0;
    let executionPlan;

    try {
      // 获取查询执行计划
      const planResult = await session.run(`EXPLAIN ${query}`, parameters);
      executionPlan = planResult.summary.plan;

      // 执行实际查询
      const result = await session.run(query, parameters);
      resultCount = result.records.length;

      // 计算性能指标
      const [seconds, nanoseconds] = process.hrtime(startTime);
      const queryTime = seconds * 1000 + nanoseconds / 1e6;
      const memoryUsage = process.memoryUsage().heapUsed - startMemory;

      const metrics: PerformanceMetrics = {
        queryTime,
        resultCount,
        memoryUsage,
        timestamp: new Date()
      };

      // 存储查询配置
      const profile: QueryProfile = {
        queryId,
        query,
        parameters,
        metrics,
        executionPlan
      };

      this.queryProfiles.set(queryId, profile);
      this.storeMetrics(queryId, metrics);

      // 检查性能阈值
      await this.checkThresholds(metrics, profile);

      return metrics;
    } catch (error) {
      logger.error('查询监控失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 存储性能指标
   */
  private storeMetrics(queryId: string, metrics: PerformanceMetrics): void {
    if (!this.metrics.has(queryId)) {
      this.metrics.set(queryId, []);
    }
    
    const queryMetrics = this.metrics.get(queryId)!;
    queryMetrics.push(metrics);

    // 只保留最近1000条记录
    if (queryMetrics.length > 1000) {
      queryMetrics.shift();
    }
  }

  /**
   * 检查性能阈值
   */
  private async checkThresholds(
    metrics: PerformanceMetrics,
    profile: QueryProfile,
    thresholds: Partial<PerformanceThresholds> = {}
  ): Promise<void> {
    const finalThresholds = { ...this.DEFAULT_THRESHOLDS, ...thresholds };

    const alerts = [];

    if (metrics.queryTime > finalThresholds.maxQueryTime) {
      alerts.push({
        type: 'SLOW_QUERY',
        message: `查询执行时间过长: ${metrics.queryTime}ms`,
        queryId: profile.queryId,
        threshold: finalThresholds.maxQueryTime
      });
    }

    if (metrics.memoryUsage > finalThresholds.maxMemoryUsage) {
      alerts.push({
        type: 'HIGH_MEMORY_USAGE',
        message: `内存使用过高: ${metrics.memoryUsage} bytes`,
        queryId: profile.queryId,
        threshold: finalThresholds.maxMemoryUsage
      });
    }

    if (metrics.resultCount > finalThresholds.maxResultCount) {
      alerts.push({
        type: 'LARGE_RESULT_SET',
        message: `结果集过大: ${metrics.resultCount} 条记录`,
        queryId: profile.queryId,
        threshold: finalThresholds.maxResultCount
      });
    }

    // 触发告警回调
    for (const alert of alerts) {
      this.alertCallbacks.forEach(callback => callback(alert));
      logger.warn('性能告警:', alert);
    }
  }

  /**
   * 注册告警回调
   */
  public onAlert(callback: (alert: any) => void): void {
    this.alertCallbacks.push(callback);
  }

  /**
   * 获取查询性能报告
   */
  public getQueryReport(queryId: string): {
    profile: QueryProfile | undefined;
    statistics: {
      averageQueryTime: number;
      averageMemoryUsage: number;
      averageResultCount: number;
      totalExecutions: number;
    };
  } {
    const profile = this.queryProfiles.get(queryId);
    const metrics = this.metrics.get(queryId) || [];

    if (metrics.length === 0) {
      return {
        profile,
        statistics: {
          averageQueryTime: 0,
          averageMemoryUsage: 0,
          averageResultCount: 0,
          totalExecutions: 0
        }
      };
    }

    const statistics = {
      averageQueryTime: this.calculateAverage(metrics, 'queryTime'),
      averageMemoryUsage: this.calculateAverage(metrics, 'memoryUsage'),
      averageResultCount: this.calculateAverage(metrics, 'resultCount'),
      totalExecutions: metrics.length
    };

    return { profile, statistics };
  }

  /**
   * 获取性能趋势分析
   */
  public getPerformanceTrends(queryId: string, timeRange: {
    start: Date;
    end: Date;
  }): {
    timeSeriesData: {
      timestamp: Date;
      queryTime: number;
      memoryUsage: number;
      resultCount: number;
    }[];
    trends: {
      queryTimeSlope: number;
      memoryUsageSlope: number;
      resultCountSlope: number;
    };
  } {
    const metrics = this.metrics.get(queryId) || [];
    const filteredMetrics = metrics.filter(m => 
      m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
    );

    const timeSeriesData = filteredMetrics.map(m => ({
      timestamp: m.timestamp,
      queryTime: m.queryTime,
      memoryUsage: m.memoryUsage,
      resultCount: m.resultCount
    }));

    // 计算趋势斜率
    const trends = {
      queryTimeSlope: this.calculateTrendSlope(timeSeriesData, 'queryTime'),
      memoryUsageSlope: this.calculateTrendSlope(timeSeriesData, 'memoryUsage'),
      resultCountSlope: this.calculateTrendSlope(timeSeriesData, 'resultCount')
    };

    return { timeSeriesData, trends };
  }

  private calculateAverage(metrics: PerformanceMetrics[], key: keyof PerformanceMetrics): number {
    if (metrics.length === 0) return 0;
    const sum = metrics.reduce((acc, curr) => acc + (curr[key] as number), 0);
    return sum / metrics.length;
  }

  private calculateTrendSlope(data: any[], key: string): number {
    if (data.length < 2) return 0;

    const n = data.length;
    let sumX = 0;
    let sumY = 0;
    let sumXY = 0;
    let sumXX = 0;

    data.forEach((point, i) => {
      const x = i;
      const y = point[key];
      sumX += x;
      sumY += y;
      sumXY += x * y;
      sumXX += x * x;
    });

    return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  }

  private getSession(): Session {
    return Neo4jConnection.getInstance().getSession();
  }
}