import { Session } from 'neo4j-driver';
import Neo4jConnection from '../database/neo4j';
import { FullTextIndexManager } from './FullTextIndexManager';
import logger from '../logger';

export interface IndexUpdateConfig {
  batchSize: number;     // 批量更新大小
  retryAttempts: number; // 重试次数
  retryDelay: number;    // 重试延迟（毫秒）
}

export interface UpdateStats {
  totalUpdated: number;
  failedUpdates: number;
  executionTime: number;
  lastUpdateTime: Date;
}

export class IndexUpdateManager {
  private static instance: IndexUpdateManager;
  private indexManager: FullTextIndexManager;
  private updateQueue: Set<string>;
  private isProcessing: boolean;
  
  private readonly DEFAULT_CONFIG: IndexUpdateConfig = {
    batchSize: 1000,
    retryAttempts: 3,
    retryDelay: 1000
  };

  private constructor() {
    this.indexManager = FullTextIndexManager.getInstance();
    this.updateQueue = new Set();
    this.isProcessing = false;
  }

  public static getInstance(): IndexUpdateManager {
    if (!IndexUpdateManager.instance) {
      IndexUpdateManager.instance = new IndexUpdateManager();
    }
    return IndexUpdateManager.instance;
  }

  /**
   * 添加节点到更新队列
   */
  public async queueForUpdate(nodeIds: string[]): Promise<void> {
    nodeIds.forEach(id => this.updateQueue.add(id));
    
    if (!this.isProcessing) {
      await this.processUpdateQueue();
    }
  }

  /**
   * 处理更新队列
   */
  private async processUpdateQueue(config: Partial<IndexUpdateConfig> = {}): Promise<void> {
    if (this.isProcessing || this.updateQueue.size === 0) {
      return;
    }

    this.isProcessing = true;
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    const session = this.getSession();

    try {
      const stats: UpdateStats = {
        totalUpdated: 0,
        failedUpdates: 0,
        executionTime: 0,
        lastUpdateTime: new Date()
      };

      const startTime = Date.now();
      const batches = this.createBatches(Array.from(this.updateQueue), finalConfig.batchSize);

      for (const batch of batches) {
        try {
          await this.updateBatch(session, batch, finalConfig);
          stats.totalUpdated += batch.length;
          
          // 从队列中移除成功更新的节点
          batch.forEach(id => this.updateQueue.delete(id));
        } catch (error) {
          stats.failedUpdates += batch.length;
          logger.error('批量更新索引失败:', error);
          
          // 重试失败的批次
          await this.retryBatch(session, batch, finalConfig);
        }
      }

      stats.executionTime = Date.now() - startTime;
      logger.info('索引更新完成:', stats);
    } catch (error) {
      logger.error('处理更新队列失败:', error);
      throw error;
    } finally {
      this.isProcessing = false;
      await session.close();

      // 如果队列中还有未处理的节点，继续处理
      if (this.updateQueue.size > 0) {
        await this.processUpdateQueue(config);
      }
    }
  }

  /**
   * 更新单个批次
   */
  private async updateBatch(
    session: Session,
    nodeIds: string[],
    config: IndexUpdateConfig
  ): Promise<void> {
    const query = `
      MATCH (n)
      WHERE n.id IN $nodeIds
      CALL db.index.fulltext.updateNodes('nodeContent', [n])
      RETURN count(n) as updated
    `;

    await session.run(query, { nodeIds });
  }

  /**
   * 重试失败的批次
   */
  private async retryBatch(
    session: Session,
    nodeIds: string[],
    config: IndexUpdateConfig
  ): Promise<void> {
    for (let attempt = 1; attempt <= config.retryAttempts; attempt++) {
      try {
        await this.updateBatch(session, nodeIds, config);
        // 更新成功，从队列中移除
        nodeIds.forEach(id => this.updateQueue.delete(id));
        return;
      } catch (error) {
        logger.warn(`重试更新索引失败 (尝试 ${attempt}/${config.retryAttempts}):`, error);
        
        if (attempt < config.retryAttempts) {
          await this.delay(config.retryDelay);
        }
      }
    }

    // 所有重试都失败，记录错误
    logger.error(`节点索引更新失败，已达到最大重试次数: ${nodeIds.join(', ')}`);
  }

  /**
   * 强制更新所有节点的索引
   */
  public async forceUpdateAll(): Promise<UpdateStats> {
    const session = this.getSession();
    const stats: UpdateStats = {
      totalUpdated: 0,
      failedUpdates: 0,
      executionTime: 0,
      lastUpdateTime: new Date()
    };

    try {
      const startTime = Date.now();

      // 获取所有节点ID
      const result = await session.run(
        'MATCH (n:KnowledgeNode) RETURN n.id as id'
      );

      const nodeIds = result.records.map(record => record.get('id'));
      await this.queueForUpdate(nodeIds);

      stats.executionTime = Date.now() - startTime;
      return stats;
    } catch (error) {
      logger.error('强制更新所有索引失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * 验证索引更新
   */
  public async validateUpdates(nodeIds: string[]): Promise<{
    valid: boolean;
    missingNodes: string[];
  }> {
    const session = this.getSession();
    try {
      const result = await session.run(
        `
        MATCH (n:KnowledgeNode)
        WHERE n.id IN $nodeIds
        WITH n
        CALL db.index.fulltext.queryNodes('nodeContent', n.content) YIELD node
        WHERE node.id = n.id
        RETURN collect(n.id) as foundIds
        `,
        { nodeIds }
      );

      const foundIds = result.records[0].get('foundIds');
      const missingNodes = nodeIds.filter(id => !foundIds.includes(id));

      return {
        valid: missingNodes.length === 0,
        missingNodes
      };
    } catch (error) {
      logger.error('验证索引更新失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  private createBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getSession(): Session {
    return Neo4jConnection.getInstance().getSession();
  }
}