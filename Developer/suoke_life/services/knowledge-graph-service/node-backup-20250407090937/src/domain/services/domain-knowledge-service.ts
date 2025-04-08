import { Logger } from '../../infrastructure/logger';
import { Neo4jKnowledgeGraphRepository } from '../../infrastructure/repositories/Neo4jKnowledgeGraphRepository';

/**
 * 领域特定知识服务 - 负责管理和查询特定领域的知识
 */
export class DomainKnowledgeService {
  private readonly logger;

  constructor(
    private readonly graphRepository: Neo4jKnowledgeGraphRepository,
  ) {
    this.logger = new Logger('DomainKnowledgeService');
  }

  /**
   * 在特定领域内搜索知识
   * @param domain 领域名称
   * @param query 查询文本
   * @param options 查询选项
   * @returns 搜索结果
   */
  async searchInDomain(domain: string, query: string, options: DomainSearchOptions = {}): Promise<DomainSearchResult> {
    try {
      this.logger.info(`在领域 ${domain} 中搜索: ${query}`);
      
      // 在领域内搜索节点
      const nodes = await this.graphRepository.searchNodesInDomain(domain, query, {
        limit: options.limit || 10,
        nodeTypes: options.nodeTypes || [],
        threshold: options.threshold || 0.7
      });
      
      // 如果需要包含关系，则获取节点之间的关系
      let relationships = [];
      if (options.includeRelationships && nodes.length > 0) {
        const nodeIds = nodes.map(node => node.id);
        relationships = await this.graphRepository.getRelationshipsBetweenNodes(nodeIds, {
          types: options.relationshipTypes || []
        });
      }
      
      return {
        query,
        domain,
        nodes,
        relationships,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      this.logger.error(`领域搜索失败: ${error.message}`);
      throw new Error(`在领域 ${domain} 中搜索失败: ${error.message}`);
    }
  }

  /**
   * 获取所有可用领域
   * @returns 领域列表
   */
  async getAllDomains(): Promise<Domain[]> {
    try {
      const domains = await this.graphRepository.getDomains();
      return domains.map(domain => ({
        name: domain.name,
        description: domain.description || '',
        nodeCount: domain.nodeCount || 0
      }));
    } catch (error) {
      this.logger.error(`获取领域列表失败: ${error.message}`);
      throw new Error(`获取领域列表失败: ${error.message}`);
    }
  }

  /**
   * 获取领域统计信息
   * @param domain 领域名称
   * @returns 领域统计信息
   */
  async getDomainStatistics(domain: string): Promise<DomainStatistics> {
    try {
      const stats = await this.graphRepository.getDomainStatistics(domain);
      return {
        domain,
        nodeCount: stats.nodeCount || 0,
        relationshipCount: stats.relationshipCount || 0,
        nodeTypeDistribution: stats.nodeTypeDistribution || {},
        relationshipTypeDistribution: stats.relationshipTypeDistribution || {},
        updatedAt: stats.updatedAt || new Date().toISOString()
      };
    } catch (error) {
      this.logger.error(`获取领域统计失败: ${error.message}`);
      throw new Error(`获取领域 ${domain} 统计信息失败: ${error.message}`);
    }
  }

  /**
   * 获取领域核心概念
   * @param domain 领域名称
   * @param limit 限制结果数量
   * @returns 核心概念列表
   */
  async getCoreConcepts(domain: string, limit = 10): Promise<any[]> {
    try {
      return await this.graphRepository.getCoreConcepts(domain, limit);
    } catch (error) {
      this.logger.error(`获取领域核心概念失败: ${error.message}`);
      throw new Error(`获取领域 ${domain} 核心概念失败: ${error.message}`);
    }
  }
}

/**
 * 领域搜索选项接口
 */
export interface DomainSearchOptions {
  limit?: number;
  threshold?: number;
  nodeTypes?: string[];
  relationshipTypes?: string[];
  includeRelationships?: boolean;
}

/**
 * 领域搜索结果接口
 */
export interface DomainSearchResult {
  query: string;
  domain: string;
  nodes: any[];
  relationships: any[];
  timestamp: string;
}

/**
 * 领域接口
 */
export interface Domain {
  name: string;
  description: string;
  nodeCount: number;
}

/**
 * 领域统计信息接口
 */
export interface DomainStatistics {
  domain: string;
  nodeCount: number;
  relationshipCount: number;
  nodeTypeDistribution: Record<string, number>;
  relationshipTypeDistribution: Record<string, number>;
  updatedAt: string;
} 