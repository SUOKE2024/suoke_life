import { Session } from 'neo4j-driver';
import Neo4jConnection from '../database/neo4j';
import logger from '../logger';

export interface IndexConfig {
  name: string;           // 索引名称
  nodeLabels: string[];   // 节点标签
  properties: string[];   // 索引属性
  analyzer?: string;      // 分词器
  eventuallyConsistent?: boolean; // 是否最终一致性
}

export interface IndexStats {
  name: string;
  status: string;
  popularity: number;
  selectivity: number;
  uniqueValues: number;
  size: number;
  type: string;
  valuesSize: number;
  indexProvider: string;
}

export class FullTextIndexManager {
  private static instance: FullTextIndexManager;
  private readonly DEFAULT_ANALYZER = 'cjk'; // 中日韩分词器

  private constructor() {}

  public static getInstance(): FullTextIndexManager {
    if (!FullTextIndexManager.instance) {
      FullTextIndexManager.instance = new FullTextIndexManager();
    }
    return FullTextIndexManager.instance;
  }

  /**
   * 创建全文搜索索引
   */
  public async createIndex(config: IndexConfig): Promise<void> {
    const session = this.getSession();
    try {
      const {
        name,
        nodeLabels,
        properties,
        analyzer = this.DEFAULT_ANALYZER,
        eventuallyConsistent = true
      } = config;

      const query = `
        CALL db.index.fulltext.createNodeIndex(
          $name,
          $nodeLabels,
          $properties,
          {
            analyzer: $analyzer,
            eventuallyConsistent: $eventuallyConsistent
          }
        )
      `;

      await session.run(query, {
        name,
        nodeLabels,
        properties,
        analyzer,
        eventuallyConsistent
      });

      logger.info(`全文搜索索引 ${name} 创建成功`);
    } catch (error) {
      logger.error('创建全文搜索索引失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 删除全文搜索索引
   */
  public async dropIndex(name: string): Promise<void> {
    const session = this.getSession();
    try {
      await session.run(
        'CALL db.index.fulltext.drop($name)',
        { name }
      );

      logger.info(`全文搜索索引 ${name} 删除成功`);
    } catch (error) {
      logger.error('删除全文搜索索引失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 获取索引统计信息
   */
  public async getIndexStats(name: string): Promise<IndexStats> {
    const session = this.getSession();
    try {
      const result = await session.run(
        'CALL db.indexDetails($name)',
        { name }
      );

      if (result.records.length === 0) {
        throw new Error(`索引 ${name} 不存在`);
      }

      const stats = result.records[0].get('indexDetails');
      return {
        name: stats.name,
        status: stats.state,
        popularity: stats.popularity || 0,
        selectivity: stats.selectivity || 0,
        uniqueValues: stats.uniqueValues || 0,
        size: stats.size || 0,
        type: stats.type,
        valuesSize: stats.valuesSize || 0,
        indexProvider: stats.indexProvider
      };
    } catch (error) {
      logger.error('获取索引统计信息失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 重建索引
   */
  public async rebuildIndex(name: string): Promise<void> {
    const session = this.getSession();
    try {
      await session.run(
        'CALL db.index.fulltext.awaitEventuallyConsistentIndexRefresh($name)',
        { name }
      );

      logger.info(`全文搜索索引 ${name} 重建成功`);
    } catch (error) {
      logger.error('重建索引失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 分析索引使用情况
   */
  public async analyzeIndexUsage(name: string): Promise<{
    usageCount: number;
    avgExecutionTime: number;
    hitRatio: number;
  }> {
    const session = this.getSession();
    try {
      const result = await session.run(`
        CALL db.stats.retrieve('INDEX STATISTICS')
        YIELD stats
        RETURN stats
      `);

      const stats = result.records[0].get('stats');
      const indexStats = stats.indexes[name] || {};

      return {
        usageCount: indexStats.uses || 0,
        avgExecutionTime: indexStats.avgExecutionTime || 0,
        hitRatio: indexStats.hitRatio || 0
      };
    } catch (error) {
      logger.error('分析索引使用情况失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 优化索引
   */
  public async optimizeIndex(name: string): Promise<void> {
    const session = this.getSession();
    try {
      // 1. 获取索引统计信息
      const stats = await this.getIndexStats(name);
      
      // 2. 分析索引使用情况
      const usage = await this.analyzeIndexUsage(name);

      // 3. 根据统计信息决定是否需要优化
      if (
        stats.selectivity < 0.1 || // 选择性太低
        usage.hitRatio < 0.5 ||    // 命中率太低
        stats.size > 1000000       // 索引太大
      ) {
        // 4. 执行优化
        await session.run(
          'CALL db.index.fulltext.optimize($name)',
          { name }
        );

        logger.info(`全文搜索索引 ${name} 优化成功`);
      } else {
        logger.info(`全文搜索索引 ${name} 无需优化`);
      }
    } catch (error) {
      logger.error('优化索引失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 监控索引健康状态
   */
  public async monitorIndexHealth(name: string): Promise<{
    isHealthy: boolean;
    issues: string[];
  }> {
    try {
      const stats = await this.getIndexStats(name);
      const usage = await this.analyzeIndexUsage(name);
      const issues: string[] = [];

      // 检查各项指标
      if (stats.status !== 'ONLINE') {
        issues.push(`索引状态异常: ${stats.status}`);
      }
      if (stats.selectivity < 0.1) {
        issues.push('索引选择性过低');
      }
      if (usage.hitRatio < 0.5) {
        issues.push('索引命中率过低');
      }
      if (usage.avgExecutionTime > 1000) {
        issues.push('索引查询性能较差');
      }
      if (stats.size > 1000000) {
        issues.push('索引体积过大');
      }

      return {
        isHealthy: issues.length === 0,
        issues
      };
    } catch (error) {
      logger.error('监控索引健康状态失败:', error);
      throw error;
    }
  }

  private getSession(): Session {
    return Neo4jConnection.getInstance().getSession();
  }
}