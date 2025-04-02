import { Injectable } from '@nestjs/common';
import { Logger } from '../../infrastructure/logger';
import { Neo4jKnowledgeGraphRepository } from '../../infrastructure/repositories/Neo4jKnowledgeGraphRepository';
import axios from 'axios';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class KnowledgeIntegrationService {
  private readonly logger = new Logger(KnowledgeIntegrationService.name);
  private readonly ragServiceUrl: string;
  private readonly knowledgeBaseServiceUrl: string;

  constructor(
    private readonly graphRepository: Neo4jKnowledgeGraphRepository,
    private readonly configService: ConfigService,
  ) {
    this.ragServiceUrl = this.configService.get<string>('RAG_SERVICE_URL', 'http://rag-service:3000');
    this.knowledgeBaseServiceUrl = this.configService.get<string>('KNOWLEDGE_BASE_SERVICE_URL', 'http://knowledge-base-service:3000');
  }

  /**
   * 整合多源知识：从RAG、知识库和知识图谱获取结果并整合
   * @param query 查询文本
   * @param options 查询选项
   * @returns 整合后的知识结果
   */
  async integrateKnowledge(query: string, options: KnowledgeIntegrationOptions = {}): Promise<IntegratedKnowledgeResult> {
    this.logger.info(`整合知识查询: ${query}`);
    
    try {
      // 并行获取各个来源的知识
      const [ragResult, kbResult, graphResult] = await Promise.all([
        this.getRAGResults(query, options),
        this.getKnowledgeBaseResults(query, options),
        this.getGraphResults(query, options),
      ]);

      // 融合知识结果
      const integratedResult = this.mergeResults(query, ragResult, kbResult, graphResult, options);
      
      // 记录整合的知识作为新节点（可选，取决于配置）
      if (options.saveIntegratedResult) {
        await this.saveIntegratedResult(query, integratedResult);
      }

      return integratedResult;
    } catch (error) {
      this.logger.error(`知识整合失败: ${error.message}`, error.stack);
      throw new Error(`知识整合失败: ${error.message}`);
    }
  }

  /**
   * 从RAG服务获取结果
   */
  private async getRAGResults(query: string, options: KnowledgeIntegrationOptions): Promise<RAGResult> {
    try {
      const response = await axios.post(`${this.ragServiceUrl}/api/query`, {
        query,
        maxResults: options.maxResults || 5,
        threshold: options.threshold || 0.7,
        domains: options.domains || [],
      });
      return response.data;
    } catch (error) {
      this.logger.warn(`RAG服务查询失败: ${error.message}`);
      return { passages: [], answer: '', metadata: { source: 'rag', status: 'error' } };
    }
  }

  /**
   * 从知识库服务获取结果
   */
  private async getKnowledgeBaseResults(query: string, options: KnowledgeIntegrationOptions): Promise<KnowledgeBaseResult> {
    try {
      const response = await axios.post(`${this.knowledgeBaseServiceUrl}/api/query`, {
        query,
        limit: options.maxResults || 5,
        domains: options.domains || [],
      });
      return response.data;
    } catch (error) {
      this.logger.warn(`知识库服务查询失败: ${error.message}`);
      return { entries: [], metadata: { source: 'knowledge_base', status: 'error' } };
    }
  }

  /**
   * 从知识图谱获取结果
   */
  private async getGraphResults(query: string, options: KnowledgeIntegrationOptions): Promise<GraphResult> {
    try {
      // 使用本地知识图谱仓库
      const nodes = await this.graphRepository.searchNodes(query, {
        limit: options.maxResults || 10,
        nodeTypes: options.nodeTypes || [],
        relationshipTypes: options.relationshipTypes || [],
      });
      
      const relationships = options.includeRelationships 
        ? await this.graphRepository.getRelationshipsForNodes(
            nodes.map(node => node.id),
            { types: options.relationshipTypes || [] }
          )
        : [];

      return {
        nodes,
        relationships,
        metadata: { source: 'knowledge_graph', status: 'success' }
      };
    } catch (error) {
      this.logger.warn(`知识图谱查询失败: ${error.message}`);
      return { 
        nodes: [], 
        relationships: [],
        metadata: { source: 'knowledge_graph', status: 'error' }
      };
    }
  }

  /**
   * 融合多源知识结果
   */
  private mergeResults(
    query: string,
    ragResult: RAGResult,
    kbResult: KnowledgeBaseResult,
    graphResult: GraphResult,
    options: KnowledgeIntegrationOptions
  ): IntegratedKnowledgeResult {
    // 融合逻辑实现
    const sources = {
      rag: ragResult.metadata.status === 'success',
      knowledgeBase: kbResult.metadata.status === 'success',
      knowledgeGraph: graphResult.metadata.status === 'success'
    };

    // 计算置信度和融合知识
    let confidence = 0;
    let sourcesUsed = 0;
    
    if (sources.rag) {
      confidence += 0.3;
      sourcesUsed++;
    }
    
    if (sources.knowledgeBase) {
      confidence += 0.3;
      sourcesUsed++;
    }
    
    if (sources.knowledgeGraph) {
      confidence += 0.4;
      sourcesUsed++;
    }
    
    // 归一化置信度
    confidence = sourcesUsed > 0 ? confidence / sourcesUsed : 0;

    // 组装结果
    return {
      query,
      answer: ragResult.answer || this.generateIntegratedAnswer(query, ragResult, kbResult, graphResult),
      confidence,
      sources,
      evidence: {
        rag: ragResult.passages || [],
        knowledgeBase: kbResult.entries || [],
        knowledgeGraph: {
          nodes: graphResult.nodes || [],
          relationships: graphResult.relationships || [],
        }
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * 生成整合的回答（当RAG没有直接回答时）
   */
  private generateIntegratedAnswer(
    query: string,
    ragResult: RAGResult,
    kbResult: KnowledgeBaseResult,
    graphResult: GraphResult
  ): string {
    // 简单整合逻辑：优先使用RAG结果，然后是知识库，最后是知识图谱
    if (ragResult.passages && ragResult.passages.length > 0) {
      return `根据检索结果：${ragResult.passages[0].text}`;
    }
    
    if (kbResult.entries && kbResult.entries.length > 0) {
      return `根据知识库：${kbResult.entries[0].content}`;
    }
    
    if (graphResult.nodes && graphResult.nodes.length > 0) {
      return `根据知识图谱中的"${graphResult.nodes[0].name}"节点信息：${graphResult.nodes[0].description || '无详细描述'}`;
    }
    
    return `未找到与"${query}"相关的知识。`;
  }

  /**
   * 保存整合的结果作为新的知识节点
   */
  private async saveIntegratedResult(query: string, result: IntegratedKnowledgeResult): Promise<void> {
    try {
      const nodeProperties = {
        query,
        answer: result.answer,
        confidence: result.confidence,
        sources: JSON.stringify(result.sources),
        timestamp: result.timestamp,
        type: 'integrated_knowledge'
      };
      
      await this.graphRepository.createNode('IntegratedKnowledge', nodeProperties);
    } catch (error) {
      this.logger.warn(`保存整合知识失败: ${error.message}`);
    }
  }
}

/**
 * 知识整合选项接口
 */
export interface KnowledgeIntegrationOptions {
  maxResults?: number;
  threshold?: number;
  domains?: string[];
  nodeTypes?: string[];
  relationshipTypes?: string[];
  includeRelationships?: boolean;
  saveIntegratedResult?: boolean;
}

/**
 * RAG服务结果接口
 */
export interface RAGResult {
  passages: Array<{
    text: string;
    score: number;
    source?: string;
  }>;
  answer: string;
  metadata: {
    source: string;
    status: string;
  };
}

/**
 * 知识库服务结果接口
 */
export interface KnowledgeBaseResult {
  entries: Array<{
    id: string;
    title: string;
    content: string;
    domain?: string;
    confidence?: number;
  }>;
  metadata: {
    source: string;
    status: string;
  };
}

/**
 * 知识图谱结果接口
 */
export interface GraphResult {
  nodes: Array<any>;
  relationships: Array<any>;
  metadata: {
    source: string;
    status: string;
  };
}

/**
 * 整合知识结果接口
 */
export interface IntegratedKnowledgeResult {
  query: string;
  answer: string;
  confidence: number;
  sources: {
    rag: boolean;
    knowledgeBase: boolean;
    knowledgeGraph: boolean;
  };
  evidence: {
    rag: Array<any>;
    knowledgeBase: Array<any>;
    knowledgeGraph: {
      nodes: Array<any>;
      relationships: Array<any>;
    };
  };
  timestamp: string;
} 