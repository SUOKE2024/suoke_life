/**
 * 知识服务单元测试
 */
import { jest } from '@jest/globals';
import axios from 'axios';
import { KnowledgeService, KnowledgeQueryParams, KnowledgeSearchResult, KnowledgeGraphQueryParams, KnowledgeGraphResult } from '../../../src/services/knowledge-service';

// 模拟Axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

// 模拟config-loader
jest.mock('../../../src/utils/config-loader', () => ({
  loadConfig: jest.fn().mockReturnValue({
    toolRegistry: {
      tools: [
        { name: 'knowledge_base', serviceUrl: 'http://knowledge-base-service:8080' },
        { name: 'knowledge_graph', serviceUrl: 'http://knowledge-graph-service:8080' },
        { name: 'rag_service', serviceUrl: 'http://rag-service:8080' }
      ],
      toolTimeoutSeconds: 30
    },
    knowledge: {
      apiBaseUrl: 'http://knowledge-service/api',
      graphApiUrl: 'http://knowledge-graph/api',
      ragApiUrl: 'http://rag-service/api',
      precisionMedicineApiUrl: 'http://precision-medicine/api',
      multimodalHealthApiUrl: 'http://multimodal-health/api',
      environmentalHealthApiUrl: 'http://environmental-health/api',
      mentalHealthApiUrl: 'http://mental-health/api'
    }
  })
}));

// 模拟logger
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
  __esModule: true,
  default: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  }
}));

describe('知识服务', () => {
  let knowledgeService: KnowledgeService;
  const mockedAxios = axios as jest.Mocked<typeof axios>;
  
  // 模拟知识搜索响应
  const mockSearchResults: KnowledgeSearchResult[] = [
    {
      id: 'knowledge1',
      title: '四诊合参',
      content: '中医诊断方法，包括望、闻、问、切四种方法',
      domain: 'tcm',
      type: 'theory',
      tags: ['诊断', '基础理论'],
      confidence: 0.95,
      source: 'tcm_classics',
      metadata: { author: '李东垣' }
    },
    {
      id: 'knowledge2',
      title: '望诊',
      content: '察看患者的精神状态、面色、形态、舌象等',
      domain: 'tcm',
      type: 'diagnostic',
      tags: ['诊断', '望诊'],
      confidence: 0.92,
      source: 'tcm_handbook'
    }
  ];
  
  // 模拟知识图谱响应
  const mockGraphResult: KnowledgeGraphResult = {
    nodes: [
      { id: 'node1', type: 'symptom', label: '头痛', properties: { severity: 'mild' } },
      { id: 'node2', type: 'treatment', label: '按摩太阳穴', properties: { efficacy: 'medium' } }
    ],
    relations: [
      { id: 'rel1', type: 'treats', source: 'node2', target: 'node1', properties: { confidence: 0.8 } }
    ],
    centralNode: { id: 'node1', type: 'symptom', label: '头痛', properties: { severity: 'mild' } },
    metadata: {
      queryTime: 120,
      totalNodesCount: 2,
      totalRelationsCount: 1
    }
  };
  
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 创建知识服务实例
    knowledgeService = new KnowledgeService();
  });
  
  describe('searchKnowledge', () => {
    it('应正确搜索知识并返回结果', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 准备搜索参数
      const searchParams: KnowledgeQueryParams = {
        query: '中医诊断方法',
        domainFilter: ['tcm'],
        typeFilter: ['theory', 'diagnostic'],
        semanticSearch: true
      };
      
      // 执行搜索
      const result = await knowledgeService.searchKnowledge(searchParams);
      
      // 验证axios调用
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/search/semantic',
        expect.objectContaining({
          params: expect.objectContaining({
            query: '中医诊断方法',
            domains: 'tcm',
            types: 'theory,diagnostic'
          })
        })
      );
      
      // 验证结果
      expect(result).toEqual(mockSearchResults);
      expect(result).toHaveLength(2);
      expect(result[0].id).toBe('knowledge1');
      expect(result[1].title).toBe('望诊');
    });
    
    it('当使用混合搜索时应调用正确的端点', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 准备搜索参数
      const searchParams: KnowledgeQueryParams = {
        query: '中医诊断方法',
        hybridSearch: true
      };
      
      // 执行搜索
      await knowledgeService.searchKnowledge(searchParams);
      
      // 验证axios调用的端点
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/search/hybrid',
        expect.any(Object)
      );
    });
    
    it('应使用默认端点进行普通搜索', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 准备搜索参数（无搜索类型指定）
      const searchParams: KnowledgeQueryParams = {
        query: '中医诊断方法'
      };
      
      // 执行搜索
      await knowledgeService.searchKnowledge(searchParams);
      
      // 验证axios调用的端点
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/search',
        expect.any(Object)
      );
    });
    
    it('当API调用失败时应抛出异常', async () => {
      // 模拟axios错误
      mockedAxios.get.mockRejectedValueOnce(new Error('API连接失败'));
      
      // 执行搜索并验证异常
      await expect(
        knowledgeService.searchKnowledge({ query: '中医诊断方法' })
      ).rejects.toThrow('知识库搜索失败: API连接失败');
    });
  });
  
  describe('queryKnowledgeGraph', () => {
    it('应正确查询知识图谱并返回结果', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: mockGraphResult
      });
      
      // 准备查询参数
      const queryParams: KnowledgeGraphQueryParams = {
        query: '头痛的治疗方法',
        nodeTypes: ['symptom', 'treatment'],
        relationTypes: ['treats'],
        maxDepth: 3
      };
      
      // 执行查询
      const result = await knowledgeService.queryKnowledgeGraph(queryParams);
      
      // 验证axios调用
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-graph-service:8080/api/graph/query',
        expect.objectContaining({
          params: expect.objectContaining({
            query: '头痛的治疗方法',
            nodeTypes: 'symptom,treatment',
            relationTypes: 'treats',
            maxDepth: 3
          })
        })
      );
      
      // 验证结果
      expect(result).toEqual(mockGraphResult);
      expect(result.nodes).toHaveLength(2);
      expect(result.relations).toHaveLength(1);
      expect(result.centralNode?.label).toBe('头痛');
    });
    
    it('当API调用失败时应抛出异常', async () => {
      // 模拟axios错误
      mockedAxios.get.mockRejectedValueOnce(new Error('图谱服务不可用'));
      
      // 执行查询并验证异常
      await expect(
        knowledgeService.queryKnowledgeGraph({ query: '头痛的治疗方法' })
      ).rejects.toThrow('知识图谱查询失败: 图谱服务不可用');
    });
  });
  
  describe('generateRAGResponse', () => {
    it('应正确调用RAG服务并返回生成的回答', async () => {
      // 模拟axios响应
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          response: '根据中医理论，头痛可以分为外感头痛和内伤头痛...',
          sources: [
            { title: '中医头痛辨证', content: '头痛辨证内容...', url: 'http://example.com/article1' },
            { title: '常见头痛类型', content: '头痛类型内容...', url: 'http://example.com/article2' }
          ],
          metadata: {
            responseTime: 1.2,
            confidence: 0.87,
            model: 'tcm-llm-v2'
          }
        }
      });
      
      // 执行RAG生成
      const result = await knowledgeService.generateRAGResponse('中医如何治疗头痛？', {
        userId: 'user123',
        sessionId: 'session456',
        domainFilters: ['tcm', 'health']
      });
      
      // 验证axios调用
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://rag-service:8080/api/generate',
        expect.objectContaining({
          query: '中医如何治疗头痛？',
          userId: 'user123',
          sessionId: 'session456',
          domainFilters: ['tcm', 'health'],
          useSpecialized: true
        }),
        expect.any(Object)
      );
      
      // 验证结果
      expect(result).toHaveProperty('response');
      expect(result).toHaveProperty('sources');
      expect(result).toHaveProperty('metadata');
      expect(result.response).toContain('根据中医理论');
      expect(result.sources).toHaveLength(2);
      expect(result.metadata).toHaveProperty('confidence', 0.87);
    });
    
    it('当API调用失败时应抛出异常', async () => {
      // 模拟axios错误
      mockedAxios.post.mockRejectedValueOnce(new Error('RAG服务超时'));
      
      // 执行RAG生成并验证异常
      await expect(
        knowledgeService.generateRAGResponse('中医如何治疗头痛？')
      ).rejects.toThrow('RAG响应生成失败: RAG服务超时');
    });
  });
  
  describe('queryPrecisionMedicine', () => {
    it('应正确查询精准医学知识并返回结果', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 执行查询
      const result = await knowledgeService.queryPrecisionMedicine({
        query: '基因突变与肺癌',
        genomeFeatures: ['EGFR', 'ALK'],
        healthRisks: ['smoking']
      });
      
      // 验证axios调用
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/precision-medicine/search',
        expect.objectContaining({
          params: expect.objectContaining({
            query: '基因突变与肺癌',
            genomeFeatures: 'EGFR,ALK',
            healthRisks: 'smoking'
          })
        })
      );
      
      // 验证结果
      expect(result).toEqual(mockSearchResults);
    });
  });
  
  describe('queryMultimodalHealth', () => {
    it('应正确查询多模态健康数据并返回结果', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 执行查询
      const result = await knowledgeService.queryMultimodalHealth({
        query: '心律异常的声音特征',
        dataTypes: ['audio', 'biosignal']
      });
      
      // 验证axios调用
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/multimodal-health/search',
        expect.objectContaining({
          params: expect.objectContaining({
            query: '心律异常的声音特征',
            dataTypes: 'audio,biosignal'
          })
        })
      );
      
      // 验证结果
      expect(result).toEqual(mockSearchResults);
    });
  });
  
  // 环境健康数据查询测试
  describe('queryEnvironmentalHealth', () => {
    it('应正确查询环境健康数据并返回结果', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 执行查询
      const result = await knowledgeService.queryEnvironmentalHealth({
        query: '空气质量对呼吸系统的影响',
        environmentalFactors: ['air_pollution', 'pollen']
      });
      
      // 验证axios调用
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/environmental-health/search',
        expect.any(Object)
      );
      
      // 验证结果
      expect(result).toEqual(mockSearchResults);
    });
  });
  
  // 心理健康数据查询测试
  describe('queryMentalHealth', () => {
    it('应正确查询心理健康数据并返回结果', async () => {
      // 模拟axios响应
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          results: mockSearchResults
        }
      });
      
      // 执行查询
      const result = await knowledgeService.queryMentalHealth({
        query: '冥想对焦虑症的效果',
        mentalHealthAspects: ['anxiety'],
        therapyTypes: ['meditation']
      });
      
      // 验证axios调用
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://knowledge-base-service:8080/api/mental-health/search',
        expect.any(Object)
      );
      
      // 验证结果
      expect(result).toEqual(mockSearchResults);
    });
  });
});