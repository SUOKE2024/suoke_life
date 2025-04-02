/**
 * 知识控制器单元测试
 */
import { Request, Response } from 'express';
import { KnowledgeController } from '../../../src/controllers/knowledge-controller';
import { KnowledgeService } from '../../../src/services/knowledge-service';
import { domainClassifier } from '../../../src/utils/domain-classifier';
import logger from '../../../src/utils/logger';

// 模拟依赖
jest.mock('../../../src/services/knowledge-service');
jest.mock('../../../src/utils/domain-classifier');
jest.mock('../../../src/utils/logger');

// 模拟logger
jest.mock('../../../src/utils/logger', () => ({
  __esModule: true,
  default: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

describe('知识控制器', () => {
  let knowledgeController: KnowledgeController;
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockJson: jest.Mock;
  let mockStatus: jest.Mock;
  let mockKnowledgeService: jest.Mocked<KnowledgeService>;

  // 模拟响应数据
  const mockSearchResults = [
    {
      id: 'result1',
      title: '测试结果1',
      content: '这是测试内容1',
      domain: '中医',
      type: '理论',
      tags: ['测试', '样例'],
      confidence: 0.95,
      source: '测试来源',
      metadata: { date: '2023-01-01' }
    }
  ];

  const mockGraphResults = {
    nodes: [{ id: 'node1', type: 'concept', label: '测试节点', properties: {} }],
    relations: [{ id: 'rel1', type: 'related', source: 'node1', target: 'node2', properties: {} }],
    centralNode: { id: 'node1', type: 'concept', label: '测试节点', properties: {} }
  };

  const mockRagResponse = {
    response: '这是RAG生成的回答',
    sources: [{ title: '来源1', content: '来源内容', url: 'http://example.com' }],
    metadata: { processingTime: 245 }
  };

  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();

    // 模拟请求和响应对象
    mockJson = jest.fn();
    mockStatus = jest.fn().mockReturnValue({ json: mockJson });
    mockRequest = {
      body: {},
      query: {}
    };
    mockResponse = {
      json: mockJson,
      status: mockStatus
    };

    // 模拟域名分类器
    (domainClassifier.classifyQuery as jest.Mock).mockReturnValue([
      { domain: '中医', confidence: 0.8 },
      { domain: '养生', confidence: 0.6 }
    ]);

    // 模拟知识服务的所有方法
    mockKnowledgeService = {
      searchKnowledge: jest.fn().mockResolvedValue(mockSearchResults),
      queryKnowledgeGraph: jest.fn().mockResolvedValue(mockGraphResults),
      generateRAGResponse: jest.fn().mockResolvedValue(mockRagResponse),
      queryPrecisionMedicine: jest.fn().mockResolvedValue(mockSearchResults),
      queryMultimodalHealth: jest.fn().mockResolvedValue(mockSearchResults),
      queryEnvironmentalHealth: jest.fn().mockResolvedValue(mockSearchResults),
      queryMentalHealth: jest.fn().mockResolvedValue(mockSearchResults)
    } as unknown as jest.Mocked<KnowledgeService>;

    // 替换KnowledgeService的构造函数，返回我们的模拟对象
    (KnowledgeService as jest.Mock).mockImplementation(() => mockKnowledgeService);

    // 初始化控制器
    knowledgeController = new KnowledgeController();
  });

  describe('searchKnowledge', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.query = {
        query: '测试查询',
        domains: '中医,养生',
        types: '理论,方剂',
        page: '1',
        limit: '10'
      };
    });

    it('应正确搜索知识并返回结果', async () => {
      await knowledgeController.searchKnowledge(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.searchKnowledge).toHaveBeenCalledWith({
        query: '测试查询',
        domainFilter: ['中医', '养生'],
        typeFilter: ['理论', '方剂'],
        page: 1,
        limit: 10,
        userId: undefined,
        semanticSearch: false,
        hybridSearch: false,
        minConfidence: 0.6
      });

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith({
        results: mockSearchResults,
        meta: {
          page: 1,
          limit: 10,
          domainClassifications: [
            { domain: '中医', confidence: 0.8 },
            { domain: '养生', confidence: 0.6 }
          ]
        }
      });
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.query = {};
      await knowledgeController.searchKnowledge(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: '搜索查询不能为空' });
    });

    it('应支持语义搜索模式', async () => {
      mockRequest.query = {
        query: '测试查询',
        semanticSearch: 'true'
      };
      
      await knowledgeController.searchKnowledge(mockRequest as Request, mockResponse as Response);
      
      expect(mockKnowledgeService.searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({
          semanticSearch: true,
          hybridSearch: false
        })
      );
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('测试错误');
      mockKnowledgeService.searchKnowledge.mockRejectedValue(error);
      
      await knowledgeController.searchKnowledge(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('知识搜索失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: '知识搜索失败',
        message: '测试错误'
      });
    });
  });

  describe('queryKnowledgeGraph', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.query = {
        query: '测试图谱查询',
        nodeTypes: '概念,症状',
        relationTypes: '关联,导致',
        maxDepth: '3',
        limit: '50'
      };
    });

    it('应正确查询知识图谱并返回结果', async () => {
      await knowledgeController.queryKnowledgeGraph(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.queryKnowledgeGraph).toHaveBeenCalledWith({
        query: '测试图谱查询',
        nodeTypes: ['概念', '症状'],
        relationTypes: ['关联', '导致'],
        maxDepth: 3,
        limit: 50,
        userId: undefined
      });

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith(mockGraphResults);
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.query = {};
      await knowledgeController.queryKnowledgeGraph(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: '图谱查询不能为空' });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('图谱查询错误');
      mockKnowledgeService.queryKnowledgeGraph.mockRejectedValue(error);
      
      await knowledgeController.queryKnowledgeGraph(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('知识图谱查询失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: '知识图谱查询失败',
        message: '图谱查询错误'
      });
    });
  });

  describe('generateRAGResponse', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.body = {
        query: '测试RAG查询',
        domainFilters: ['中医', '养生'],
        typeFilters: ['方剂'],
        useSpecialized: true,
        userId: 'user123',
        sessionId: 'session456'
      };
    });

    it('应正确生成RAG响应并返回结果', async () => {
      await knowledgeController.generateRAGResponse(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.generateRAGResponse).toHaveBeenCalledWith(
        '测试RAG查询',
        {
          userId: 'user123',
          sessionId: 'session456',
          domainFilters: ['中医', '养生'],
          typeFilters: ['方剂'],
          useSpecialized: true
        }
      );

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith(mockRagResponse);
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.body = {};
      await knowledgeController.generateRAGResponse(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: 'RAG查询不能为空' });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('RAG生成错误');
      mockKnowledgeService.generateRAGResponse.mockRejectedValue(error);
      
      await knowledgeController.generateRAGResponse(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('RAG响应生成失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: 'RAG响应生成失败',
        message: 'RAG生成错误'
      });
    });
  });

  describe('queryPrecisionMedicine', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.query = {
        query: '测试精准医学查询',
        genomeFeatures: 'feature1,feature2',
        healthRisks: 'risk1,risk2',
        diseaseTypes: 'disease1,disease2',
        page: '1',
        limit: '10'
      };
    });

    it('应正确查询精准医学知识并返回结果', async () => {
      await knowledgeController.queryPrecisionMedicine(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.queryPrecisionMedicine).toHaveBeenCalledWith({
        query: '测试精准医学查询',
        genomeFeatures: ['feature1', 'feature2'],
        healthRisks: ['risk1', 'risk2'],
        diseaseTypes: ['disease1', 'disease2'],
        page: 1,
        limit: 10
      });

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith({
        results: mockSearchResults,
        meta: {
          page: 1,
          limit: 10
        }
      });
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.query = {};
      await knowledgeController.queryPrecisionMedicine(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: '查询不能为空' });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('精准医学查询错误');
      mockKnowledgeService.queryPrecisionMedicine.mockRejectedValue(error);
      
      await knowledgeController.queryPrecisionMedicine(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('精准医学知识查询失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: '精准医学知识查询失败',
        message: '精准医学查询错误'
      });
    });
  });

  describe('queryMultimodalHealth', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.query = {
        query: '测试多模态健康查询',
        dataTypes: 'image,audio,text',
        sources: 'source1,source2',
        page: '1',
        limit: '10'
      };
    });

    it('应正确查询多模态健康数据并返回结果', async () => {
      await knowledgeController.queryMultimodalHealth(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.queryMultimodalHealth).toHaveBeenCalledWith({
        query: '测试多模态健康查询',
        dataTypes: ['image', 'audio', 'text'],
        sources: ['source1', 'source2'],
        page: 1,
        limit: 10
      });

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith({
        results: mockSearchResults,
        meta: {
          page: 1,
          limit: 10
        }
      });
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.query = {};
      await knowledgeController.queryMultimodalHealth(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: '查询不能为空' });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('多模态健康数据查询错误');
      mockKnowledgeService.queryMultimodalHealth.mockRejectedValue(error);
      
      await knowledgeController.queryMultimodalHealth(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('多模态健康数据查询失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: '多模态健康数据查询失败',
        message: '多模态健康数据查询错误'
      });
    });
  });

  describe('queryEnvironmentalHealth', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.query = {
        query: '测试环境健康查询',
        factors: 'air,water',
        locations: 'location1,location2',
        startTime: '2023-01-01',
        endTime: '2023-12-31',
        page: '1',
        limit: '10'
      };
    });

    it('应正确查询环境健康数据并返回结果', async () => {
      await knowledgeController.queryEnvironmentalHealth(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.queryEnvironmentalHealth).toHaveBeenCalledWith({
        query: '测试环境健康查询',
        environmentalFactors: ['air', 'water'],
        locations: ['location1', 'location2'],
        timeRange: {
          start: '2023-01-01',
          end: '2023-12-31'
        },
        page: 1,
        limit: 10
      });

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith({
        results: mockSearchResults,
        meta: {
          page: 1,
          limit: 10
        }
      });
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.query = {};
      await knowledgeController.queryEnvironmentalHealth(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: '查询不能为空' });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('环境健康数据查询错误');
      mockKnowledgeService.queryEnvironmentalHealth.mockRejectedValue(error);
      
      await knowledgeController.queryEnvironmentalHealth(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('环境健康数据查询失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: '环境健康数据查询失败',
        message: '环境健康数据查询错误'
      });
    });
  });

  describe('queryMentalHealth', () => {
    beforeEach(() => {
      // 准备模拟请求
      mockRequest.query = {
        query: '测试心理健康查询',
        aspects: 'emotion,cognitive',
        therapies: 'cbt,mindfulness',
        conditions: 'anxiety,depression',
        page: '1',
        limit: '10'
      };
    });

    it('应正确查询心理健康数据并返回结果', async () => {
      await knowledgeController.queryMentalHealth(mockRequest as Request, mockResponse as Response);

      // 验证服务调用
      expect(mockKnowledgeService.queryMentalHealth).toHaveBeenCalledWith({
        query: '测试心理健康查询',
        mentalHealthAspects: ['emotion', 'cognitive'],
        therapyTypes: ['cbt', 'mindfulness'],
        conditions: ['anxiety', 'depression'],
        page: 1,
        limit: 10
      });

      // 验证响应
      expect(mockJson).toHaveBeenCalledWith({
        results: mockSearchResults,
        meta: {
          page: 1,
          limit: 10
        }
      });
    });

    it('查询为空时应返回400错误', async () => {
      mockRequest.query = {};
      await knowledgeController.queryMentalHealth(mockRequest as Request, mockResponse as Response);
      
      expect(mockStatus).toHaveBeenCalledWith(400);
      expect(mockJson).toHaveBeenCalledWith({ error: '查询不能为空' });
    });

    it('服务抛出异常时应返回500错误', async () => {
      const error = new Error('心理健康数据查询错误');
      mockKnowledgeService.queryMentalHealth.mockRejectedValue(error);
      
      await knowledgeController.queryMentalHealth(mockRequest as Request, mockResponse as Response);
      
      expect(logger.error).toHaveBeenCalledWith('心理健康数据查询失败', { error });
      expect(mockStatus).toHaveBeenCalledWith(500);
      expect(mockJson).toHaveBeenCalledWith({
        error: '心理健康数据查询失败',
        message: '心理健康数据查询错误'
      });
    });
  });
});