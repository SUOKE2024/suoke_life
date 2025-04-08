import { Session } from 'neo4j-driver';
import { IKnowledgeGraphRepository } from '../../domain/repositories/IKnowledgeGraphRepository';
import { KnowledgeNode, Relation } from '../../domain/entities/KnowledgeGraph';
import Neo4jConnection from '../database/neo4j';
import { TCMDataValidator } from '../validators/TCMDataValidator';
import { FullTextIndexManager } from '../search/FullTextIndexManager';
import { IndexUpdateManager } from '../search/IndexUpdateManager';
import { IndexOptimizationManager } from '../search/IndexOptimizationManager';
import { getPerformanceMonitor, MonitorQuery } from '../monitoring';
import { QueryAnalyzer } from '../query/QueryAnalyzer';
import { PaginationManager } from '../query/PaginationManager';
import { RateLimiter } from '../query/RateLimiter';
import { TimeoutManager } from '../query/TimeoutManager';
import { Cacheable, CacheEvict } from '../cache/decorators';
import logger from '../logger';

export class Neo4jKnowledgeGraphRepository implements IKnowledgeGraphRepository {
  private static instance: Neo4jKnowledgeGraphRepository;
  private connection: Neo4jConnection;
  private validator: TCMDataValidator;
  private indexManager: FullTextIndexManager;
  private indexUpdateManager: IndexUpdateManager;
  private indexOptimizationManager: IndexOptimizationManager;
  private queryAnalyzer: QueryAnalyzer;
  private paginationManager: PaginationManager;
  private rateLimiter: RateLimiter;
  private timeoutManager: TimeoutManager;
  private performanceMonitor: any;

  private constructor() {
    this.connection = Neo4jConnection.getInstance();
    this.validator = new TCMDataValidator();
    this.indexManager = FullTextIndexManager.getInstance();
    this.indexUpdateManager = IndexUpdateManager.getInstance();
    this.indexOptimizationManager = IndexOptimizationManager.getInstance();
    this.queryAnalyzer = QueryAnalyzer.getInstance();
    this.paginationManager = PaginationManager.getInstance();
    this.rateLimiter = RateLimiter.getInstance();
    this.timeoutManager = TimeoutManager.getInstance();
    this.performanceMonitor = getPerformanceMonitor();
  }

  public static getInstance(): Neo4jKnowledgeGraphRepository {
    if (!Neo4jKnowledgeGraphRepository.instance) {
      Neo4jKnowledgeGraphRepository.instance = new Neo4jKnowledgeGraphRepository();
    }
    return Neo4jKnowledgeGraphRepository.instance;
  }

  @MonitorQuery('create_node')
  @CacheEvict('nodes')
  async createNode(node: KnowledgeNode): Promise<string> {
    await this.rateLimiter.checkLimit('create_node');
    await this.validator.validateNode(node);

    const session = this.getSession();
    const queryId = 'create_node';

    try {
      const query = `
        CREATE (n:KnowledgeNode {
          id: $id,
          type: $type,
          content: $content,
          metadata: $metadata,
          created_at: datetime(),
          updated_at: datetime()
        })
        RETURN n.id as id
      `;

      const result = await this.timeoutManager.executeWithTimeout(
        async () => {
          const executionPlan = await this.queryAnalyzer.analyzeQuery(query);
          logger.info('创建节点查询执行计划:', executionPlan);

          return session.run(query, {
            id: node.id,
            type: node.type,
            content: node.content,
            metadata: node.metadata
          });
        },
        queryId
      );

      const nodeId = result.records[0].get('id');

      // 更新索引
      await this.indexUpdateManager.queueForUpdate([nodeId]);

      return nodeId;
    } catch (error) {
      logger.error('创建节点失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  @MonitorQuery('update_node')
  @CacheEvict('nodes')
  async updateNode(node: KnowledgeNode): Promise<void> {
    await this.rateLimiter.checkLimit('update_node');
    await this.validator.validateNode(node);

    const session = this.getSession();
    const queryId = 'update_node';

    try {
      const query = `
        MATCH (n:KnowledgeNode {id: $id})
        SET n.type = $type,
            n.content = $content,
            n.metadata = $metadata,
            n.updated_at = datetime()
        RETURN n.id as id
      `;

      await this.timeoutManager.executeWithTimeout(
        async () => {
          const executionPlan = await this.queryAnalyzer.analyzeQuery(query);
          logger.info('更新节点查询执行计划:', executionPlan);

          return session.run(query, {
            id: node.id,
            type: node.type,
            content: node.content,
            metadata: node.metadata
          });
        },
        queryId
      );

      // 更新索引
      await this.indexUpdateManager.queueForUpdate([node.id]);
    } catch (error) {
      logger.error('更新节点失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  @MonitorQuery('delete_node')
  @CacheEvict('nodes')
  async deleteNode(nodeId: string): Promise<void> {
    await this.rateLimiter.checkLimit('delete_node');
    
    const session = this.getSession();
    const queryId = 'delete_node';

    try {
      const query = `
        MATCH (n:KnowledgeNode {id: $id})
        DETACH DELETE n
      `;

      await this.timeoutManager.executeWithTimeout(
        async () => {
          const executionPlan = await this.queryAnalyzer.analyzeQuery(query);
          logger.info('删除节点查询执行计划:', executionPlan);

          return session.run(query, { id: nodeId });
        },
        queryId
      );

      // 从索引中移除
      await this.indexManager.removeFromIndex(nodeId);
    } catch (error) {
      logger.error('删除节点失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  @MonitorQuery('get_node')
  @Cacheable('nodes')
  async getNodeById(nodeId: string): Promise<KnowledgeNode | null> {
    await this.rateLimiter.checkLimit('get_node');
    
    const session = this.getSession();
    const queryId = 'get_node';

    try {
      const query = `
        MATCH (n:KnowledgeNode {id: $id})
        RETURN n
      `;

      const result = await this.timeoutManager.executeWithTimeout(
        async () => {
          const executionPlan = await this.queryAnalyzer.analyzeQuery(query);
          logger.info('获取节点查询执行计划:', executionPlan);

          return session.run(query, { id: nodeId });
        },
        queryId
      );

      if (result.records.length === 0) {
        return null;
      }

      const nodeData = result.records[0].get('n').properties;
      return this.mapToKnowledgeNode(nodeData);
    } catch (error) {
      logger.error('获取节点失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  @MonitorQuery('search_nodes')
  @Cacheable('search_results')
  async searchNodes(query: string, options: any = {}): Promise<KnowledgeNode[]> {
    await this.rateLimiter.checkLimit('search_nodes');
    
    const session = this.getSession();
    const queryId = 'search_nodes';

    try {
      // 使用分页管理器处理分页
      const { skip, limit, cursor } = await this.paginationManager.getPaginationParams(options);

      const searchQuery = `
        CALL db.index.fulltext.queryNodes("nodeContent", $query)
        YIELD node, score
        RETURN node, score
        ORDER BY score DESC
        SKIP $skip
        LIMIT $limit
      `;

      const result = await this.timeoutManager.executeWithTimeout(
        async () => {
          const executionPlan = await this.queryAnalyzer.analyzeQuery(searchQuery);
          logger.info('搜索节点查询执行计划:', executionPlan);

          return session.run(searchQuery, {
            query,
            skip,
            limit
          });
        },
        queryId
      );

      const nodes = result.records.map(record => {
        const nodeData = record.get('node').properties;
        return this.mapToKnowledgeNode(nodeData);
      });

      // 更新分页游标
      await this.paginationManager.updateCursor(cursor, nodes);

      return nodes;
    } catch (error) {
      logger.error('搜索节点失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  @MonitorQuery('create_relation')
  @CacheEvict(['relations', 'nodes'])
  async createRelation(relation: Relation): Promise<string> {
    await this.rateLimiter.checkLimit('create_relation');
    await this.validator.validateRelation(relation);

    const session = this.getSession();
    const queryId = 'create_relation';

    try {
      const query = `
        MATCH (from:KnowledgeNode {id: $fromId})
        MATCH (to:KnowledgeNode {id: $toId})
        CREATE (from)-[r:RELATES {
          id: $id,
          type: $type,
          metadata: $metadata,
          created_at: datetime(),
          updated_at: datetime()
        }]->(to)
        RETURN r.id as id
      `;

      const result = await this.timeoutManager.executeWithTimeout(
        async () => {
          const executionPlan = await this.queryAnalyzer.analyzeQuery(query);
          logger.info('创建关系查询执行计划:', executionPlan);

          return session.run(query, {
            id: relation.id,
            fromId: relation.fromId,
            toId: relation.toId,
            type: relation.type,
            metadata: relation.metadata
          });
        },
        queryId
      );

      return result.records[0].get('id');
    } catch (error) {
      logger.error('创建关系失败:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  private mapToKnowledgeNode(data: any): KnowledgeNode {
    return {
      id: data.id,
      type: data.type,
      content: data.content,
      metadata: data.metadata,
      createdAt: new Date(data.created_at),
      updatedAt: new Date(data.updated_at)
    };
  }

  private getSession(): Session {
    return this.connection.getSession();
  }
}