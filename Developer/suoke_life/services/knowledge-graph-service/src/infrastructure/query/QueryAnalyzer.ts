import { Session } from 'neo4j-driver';
import logger from '../logger';

export interface QueryPlan {
  operatorType: string;
  identifiers: string[];
  arguments: Record<string, any>;
  children: QueryPlan[];
  dbHits: number;
  rows: number;
  estimatedRows: number;
  pageCacheMisses: number;
  pageCacheHits: number;
  pageCacheHitRatio: number;
  time: number;
}

export interface QueryStats {
  queryText: string;
  executionTime: number;
  resultCount: number;
  dbHits: number;
  pageCacheHitRatio: number;
  indexes: string[];
}

export class QueryAnalyzer {
  private static instance: QueryAnalyzer;

  private constructor() {}

  public static getInstance(): QueryAnalyzer {
    if (!QueryAnalyzer.instance) {
      QueryAnalyzer.instance = new QueryAnalyzer();
    }
    return QueryAnalyzer.instance;
  }

  /**
   * 分析查询计划
   */
  public async analyzeQuery(session: Session, query: string, params: Record<string, any> = {}): Promise<QueryPlan> {
    try {
      const result = await session.run(`EXPLAIN ${query}`, params);
      const plan = result.summary.plan;
      
      return this.parseQueryPlan(plan);
    } catch (error) {
      logger.error('查询计划分析失败:', error);
      throw error;
    }
  }

  /**
   * 收集查询统计信息
   */
  public async collectQueryStats(session: Session, query: string, params: Record<string, any> = {}): Promise<QueryStats> {
    try {
      const startTime = Date.now();
      const result = await session.run(`PROFILE ${query}`, params);
      const executionTime = Date.now() - startTime;

      const summary = result.summary;
      const profile = summary.profile;

      return {
        queryText: query,
        executionTime,
        resultCount: result.records.length,
        dbHits: this.calculateTotalDbHits(profile),
        pageCacheHitRatio: this.calculateCacheHitRatio(profile),
        indexes: this.extractUsedIndexes(summary)
      };
    } catch (error) {
      logger.error('查询统计收集失败:', error);
      throw error;
    }
  }

  /**
   * 优化查询
   */
  public optimizeQuery(query: string, stats: QueryStats): string {
    let optimizedQuery = query;

    // 检查是否需要添加索引提示
    if (stats.dbHits > 1000 && stats.indexes.length > 0) {
      optimizedQuery = this.addIndexHints(optimizedQuery, stats.indexes);
    }

    // 检查是否需要添加查询限制
    if (!optimizedQuery.toLowerCase().includes('limit') && stats.resultCount > 100) {
      optimizedQuery = this.addLimit(optimizedQuery);
    }

    return optimizedQuery;
  }

  private parseQueryPlan(plan: any): QueryPlan {
    return {
      operatorType: plan.operatorType,
      identifiers: plan.identifiers,
      arguments: plan.arguments,
      children: plan.children.map((child: any) => this.parseQueryPlan(child)),
      dbHits: plan.dbHits.toNumber(),
      rows: plan.rows.toNumber(),
      estimatedRows: plan.estimatedRows.toNumber(),
      pageCacheMisses: plan.pageCacheMisses?.toNumber() || 0,
      pageCacheHits: plan.pageCacheHits?.toNumber() || 0,
      pageCacheHitRatio: this.calculateHitRatio(
        plan.pageCacheHits?.toNumber() || 0,
        plan.pageCacheMisses?.toNumber() || 0
      ),
      time: plan.time || 0
    };
  }

  private calculateTotalDbHits(profile: any): number {
    let total = profile.dbHits?.toNumber() || 0;
    for (const child of profile.children || []) {
      total += this.calculateTotalDbHits(child);
    }
    return total;
  }

  private calculateCacheHitRatio(profile: any): number {
    const hits = profile.pageCacheHits?.toNumber() || 0;
    const misses = profile.pageCacheMisses?.toNumber() || 0;
    return this.calculateHitRatio(hits, misses);
  }

  private calculateHitRatio(hits: number, misses: number): number {
    const total = hits + misses;
    return total > 0 ? hits / total : 0;
  }

  private extractUsedIndexes(summary: any): string[] {
    const indexes = new Set<string>();
    const notifications = summary.notifications || [];

    for (const notification of notifications) {
      if (notification.code === 'Neo.ClientNotification.Statement.IndexHint') {
        const match = notification.description.match(/Index hint: (\w+)/);
        if (match) {
          indexes.add(match[1]);
        }
      }
    }

    return Array.from(indexes);
  }

  private addIndexHints(query: string, indexes: string[]): string {
    const hintParts = indexes.map(index => `USING INDEX ${index}`);
    const hint = hintParts.join(' ');
    return `${hint} ${query}`;
  }

  private addLimit(query: string): string {
    return `${query} LIMIT 100`;
  }
}