/**
 * 知识服务集成
 * 提供与知识库服务和知识图谱服务的集成接口
 */
import axios from 'axios';
import { loadConfig } from '../utils/config-loader';
import logger from '../utils/logger';

export interface KnowledgeQueryParams {
  query: string;
  domainFilter?: string[];
  typeFilter?: string[];
  page?: number;
  limit?: number;
  userId?: string;
  semanticSearch?: boolean;
  hybridSearch?: boolean;
  minConfidence?: number;
}

export interface KnowledgeSearchResult {
  id: string;
  title: string;
  content: string;
  domain: string;
  type: string;
  tags: string[];
  confidence: number;
  source: string;
  metadata?: Record<string, any>;
}

export interface KnowledgeGraphQueryParams {
  query: string;
  nodeTypes?: string[];
  relationTypes?: string[];
  maxDepth?: number;
  limit?: number;
  userId?: string;
}

export interface KnowledgeNode {
  id: string;
  type: string;
  label: string;
  properties: Record<string, any>;
  confidence?: number;
}

export interface KnowledgeRelation {
  id: string;
  type: string;
  source: string;
  target: string;
  properties: Record<string, any>;
}

export interface KnowledgeGraphResult {
  nodes: KnowledgeNode[];
  relations: KnowledgeRelation[];
  centralNode?: KnowledgeNode;
  metadata?: {
    queryTime: number;
    totalNodesCount: number;
    totalRelationsCount: number;
  };
}

export class KnowledgeService {
  private config = loadConfig();
  private knowledgeBaseUrl: string;
  private knowledgeGraphUrl: string;
  private ragServiceUrl: string;

  constructor() {
    const knowledgeBaseTool = this.config.toolRegistry.tools.find(
      (tool) => tool.name === 'knowledge_base'
    ) || { serviceUrl: 'http://knowledge-base-service:8080' };

    const knowledgeGraphTool = this.config.toolRegistry.tools.find(
      (tool) => tool.name === 'knowledge_graph'
    ) || { serviceUrl: 'http://knowledge-graph-service:8080' };

    const ragTool = this.config.toolRegistry.tools.find(
      (tool) => tool.name === 'rag_service'
    ) || { serviceUrl: 'http://rag-service:8080' };

    this.knowledgeBaseUrl = knowledgeBaseTool.serviceUrl;
    this.knowledgeGraphUrl = knowledgeGraphTool.serviceUrl;
    this.ragServiceUrl = ragTool.serviceUrl;
  }

  /**
   * 搜索知识库
   */
  async searchKnowledge(params: KnowledgeQueryParams): Promise<KnowledgeSearchResult[]> {
    try {
      const endpoint = params.semanticSearch
        ? '/api/search/semantic'
        : params.hybridSearch
          ? '/api/search/hybrid'
          : '/api/search';

      const response = await axios.get(`${this.knowledgeBaseUrl}${endpoint}`, {
        params: {
          query: params.query,
          domains: params.domainFilter?.join(','),
          types: params.typeFilter?.join(','),
          page: params.page || 1,
          limit: params.limit || 10,
          userId: params.userId,
          minConfidence: params.minConfidence || 0.6,
        },
        timeout: this.config.toolRegistry.toolTimeoutSeconds * 1000,
      });

      return response.data.results;
    } catch (error) {
      logger.error('知识库搜索失败', { error, params });
      throw new Error(`知识库搜索失败: ${error.message}`);
    }
  }

  /**
   * 查询知识图谱
   */
  async queryKnowledgeGraph(params: KnowledgeGraphQueryParams): Promise<KnowledgeGraphResult> {
    try {
      const response = await axios.get(`${this.knowledgeGraphUrl}/api/graph/query`, {
        params: {
          query: params.query,
          nodeTypes: params.nodeTypes?.join(','),
          relationTypes: params.relationTypes?.join(','),
          maxDepth: params.maxDepth || 2,
          limit: params.limit || 50,
          userId: params.userId,
        },
        timeout: this.config.toolRegistry.toolTimeoutSeconds * 1000,
      });

      return response.data;
    } catch (error) {
      logger.error('知识图谱查询失败', { error, params });
      throw new Error(`知识图谱查询失败: ${error.message}`);
    }
  }

  /**
   * 使用RAG服务生成回答
   */
  async generateRAGResponse(
    query: string,
    context: Record<string, any> = {}
  ): Promise<{
    response: string;
    sources: Array<{ title: string; content: string; url?: string }>;
    metadata: Record<string, any>;
  }> {
    try {
      const response = await axios.post(
        `${this.ragServiceUrl}/api/generate`,
        {
          query,
          userId: context.userId,
          sessionId: context.sessionId,
          domainFilters: context.domainFilters,
          typeFilters: context.typeFilters,
          useSpecialized: context.useSpecialized || true,
        },
        {
          timeout: (this.config.toolRegistry.toolTimeoutSeconds + 30) * 1000, // RAG需要更长的超时时间
        }
      );

      return response.data;
    } catch (error) {
      logger.error('RAG响应生成失败', { error, query });
      throw new Error(`RAG响应生成失败: ${error.message}`);
    }
  }

  /**
   * 查询精准医学领域知识
   */
  async queryPrecisionMedicine(params: {
    query: string;
    genomeFeatures?: string[];
    healthRisks?: string[];
    diseaseTypes?: string[];
    page?: number;
    limit?: number;
  }): Promise<KnowledgeSearchResult[]> {
    try {
      const response = await axios.get(
        `${this.knowledgeBaseUrl}/api/precision-medicine/search`,
        {
          params: {
            query: params.query,
            genomeFeatures: params.genomeFeatures?.join(','),
            healthRisks: params.healthRisks?.join(','),
            diseaseTypes: params.diseaseTypes?.join(','),
            page: params.page || 1,
            limit: params.limit || 10,
          },
          timeout: this.config.toolRegistry.toolTimeoutSeconds * 1000,
        }
      );

      return response.data.results;
    } catch (error) {
      logger.error('精准医学知识查询失败', { error, params });
      throw new Error(`精准医学知识查询失败: ${error.message}`);
    }
  }

  /**
   * 查询多模态健康数据
   */
  async queryMultimodalHealth(params: {
    query: string;
    dataTypes?: ('image' | 'audio' | 'text' | 'biosignal')[];
    sources?: string[];
    page?: number;
    limit?: number;
  }): Promise<KnowledgeSearchResult[]> {
    try {
      const response = await axios.get(
        `${this.knowledgeBaseUrl}/api/multimodal-health/search`,
        {
          params: {
            query: params.query,
            dataTypes: params.dataTypes?.join(','),
            sources: params.sources?.join(','),
            page: params.page || 1,
            limit: params.limit || 10,
          },
          timeout: this.config.toolRegistry.toolTimeoutSeconds * 1000,
        }
      );

      return response.data.results;
    } catch (error) {
      logger.error('多模态健康数据查询失败', { error, params });
      throw new Error(`多模态健康数据查询失败: ${error.message}`);
    }
  }

  /**
   * 查询环境健康数据
   */
  async queryEnvironmentalHealth(params: {
    query: string;
    environmentalFactors?: string[];
    locations?: string[];
    timeRange?: { start: string; end: string };
    page?: number;
    limit?: number;
  }): Promise<KnowledgeSearchResult[]> {
    try {
      const response = await axios.get(
        `${this.knowledgeBaseUrl}/api/environmental-health/search`,
        {
          params: {
            query: params.query,
            factors: params.environmentalFactors?.join(','),
            locations: params.locations?.join(','),
            startTime: params.timeRange?.start,
            endTime: params.timeRange?.end,
            page: params.page || 1,
            limit: params.limit || 10,
          },
          timeout: this.config.toolRegistry.toolTimeoutSeconds * 1000,
        }
      );

      return response.data.results;
    } catch (error) {
      logger.error('环境健康数据查询失败', { error, params });
      throw new Error(`环境健康数据查询失败: ${error.message}`);
    }
  }

  /**
   * 查询心理健康数据
   */
  async queryMentalHealth(params: {
    query: string;
    mentalHealthAspects?: string[];
    therapyTypes?: string[];
    conditions?: string[];
    page?: number;
    limit?: number;
  }): Promise<KnowledgeSearchResult[]> {
    try {
      const response = await axios.get(
        `${this.knowledgeBaseUrl}/api/mental-health/search`,
        {
          params: {
            query: params.query,
            aspects: params.mentalHealthAspects?.join(','),
            therapies: params.therapyTypes?.join(','),
            conditions: params.conditions?.join(','),
            page: params.page || 1,
            limit: params.limit || 10,
          },
          timeout: this.config.toolRegistry.toolTimeoutSeconds * 1000,
        }
      );

      return response.data.results;
    } catch (error) {
      logger.error('心理健康数据查询失败', { error, params });
      throw new Error(`心理健康数据查询失败: ${error.message}`);
    }
  }
}