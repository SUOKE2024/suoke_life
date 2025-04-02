/**
 * 知识路由集成测试
 */
import request from 'supertest';
import express from 'express';
import knowledgeRoutes from '../../../src/routes/knowledge-routes';
import { KnowledgeController } from '../../../src/controllers/knowledge-controller';

// 增加全局测试超时设置为30秒
jest.setTimeout(30000);

// 模拟KnowledgeController
jest.mock('../../../src/controllers/knowledge-controller');

// 模拟认证中间件
jest.mock('../../../src/middlewares/auth', () => ({
  authenticate: jest.fn((req, res, next) => next())
}));

describe('知识路由集成测试', () => {
  let app: express.Application;
  let mockSearchKnowledge: jest.Mock;
  let mockQueryKnowledgeGraph: jest.Mock;
  let mockGenerateRAGResponse: jest.Mock;
  let mockQueryPrecisionMedicine: jest.Mock;
  let mockQueryMultimodalHealth: jest.Mock;
  let mockQueryEnvironmentalHealth: jest.Mock;
  let mockQueryMentalHealth: jest.Mock;

  beforeEach(() => {
    // 设置mock方法
    mockSearchKnowledge = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          results: [
            { id: 'k1', title: '中医养生基础', content: '内容1' },
            { id: 'k2', title: '食疗养生', content: '内容2' }
          ],
          total: 2
        }
      });
    });

    mockQueryKnowledgeGraph = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          nodes: [
            { id: 'n1', type: 'concept', name: '中医' },
            { id: 'n2', type: 'concept', name: '养生' }
          ],
          relationships: [
            { source: 'n1', target: 'n2', type: '包含' }
          ]
        }
      });
    });

    mockGenerateRAGResponse = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          response: '基于知识库生成的回答...',
          sources: [
            { id: 'k1', title: '中医养生基础', relevance: 0.92 }
          ]
        }
      });
    });

    mockQueryPrecisionMedicine = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          results: [
            { id: 'pm1', title: '个性化治疗方案', content: '内容...' }
          ]
        }
      });
    });

    mockQueryMultimodalHealth = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          results: [
            { id: 'mh1', type: 'image', title: '舌诊图像分析', content: '图像URL...' }
          ]
        }
      });
    });

    mockQueryEnvironmentalHealth = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          results: [
            { id: 'eh1', title: '环境与健康的关系', content: '内容...' }
          ]
        }
      });
    });

    mockQueryMentalHealth = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: {
          results: [
            { id: 'mth1', title: '心理健康评估', content: '内容...' }
          ]
        }
      });
    });

    // 设置控制器mock实例
    (KnowledgeController as jest.Mock).mockImplementation(() => ({
      searchKnowledge: mockSearchKnowledge,
      queryKnowledgeGraph: mockQueryKnowledgeGraph,
      generateRAGResponse: mockGenerateRAGResponse,
      queryPrecisionMedicine: mockQueryPrecisionMedicine,
      queryMultimodalHealth: mockQueryMultimodalHealth,
      queryEnvironmentalHealth: mockQueryEnvironmentalHealth,
      queryMentalHealth: mockQueryMentalHealth
    }));

    // 创建Express应用
    app = express();
    app.use(express.json());
    app.use('/api/knowledge', knowledgeRoutes);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /api/knowledge/search', () => {
    it('应返回搜索结果', async () => {
      const response = await request(app)
        .get('/api/knowledge/search')
        .query({ q: '养生' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.results)).toBe(true);
      expect(response.body.data.results.length).toBe(2);
      expect(mockSearchKnowledge).toHaveBeenCalled();
    }, 15000); // 增加单独测试的超时时间到15秒
  });

  describe('GET /api/knowledge/graph/query', () => {
    it('应返回知识图谱查询结果', async () => {
      const response = await request(app)
        .get('/api/knowledge/graph/query')
        .query({ concept: '中医' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.nodes)).toBe(true);
      expect(Array.isArray(response.body.data.relationships)).toBe(true);
      expect(mockQueryKnowledgeGraph).toHaveBeenCalled();
    }, 15000);
  });

  describe('POST /api/knowledge/rag/generate', () => {
    it('应生成基于检索增强的回答', async () => {
      const response = await request(app)
        .post('/api/knowledge/rag/generate')
        .send({
          query: '中医养生的基本原则是什么？',
          maxSources: 5
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.response).toBeTruthy();
      expect(Array.isArray(response.body.data.sources)).toBe(true);
      expect(mockGenerateRAGResponse).toHaveBeenCalled();
    }, 15000);
  });

  describe('GET /api/knowledge/precision-medicine/search', () => {
    it('应返回精准医学知识查询结果', async () => {
      const response = await request(app)
        .get('/api/knowledge/precision-medicine/search')
        .query({ condition: '糖尿病' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.results)).toBe(true);
      expect(mockQueryPrecisionMedicine).toHaveBeenCalled();
    }, 15000);
  });

  describe('GET /api/knowledge/multimodal-health/search', () => {
    it('应返回多模态健康数据查询结果', async () => {
      const response = await request(app)
        .get('/api/knowledge/multimodal-health/search')
        .query({ modalityType: 'image', query: '舌苔' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.results)).toBe(true);
      expect(mockQueryMultimodalHealth).toHaveBeenCalled();
    }, 15000);
  });

  describe('GET /api/knowledge/environmental-health/search', () => {
    it('应返回环境健康数据查询结果', async () => {
      const response = await request(app)
        .get('/api/knowledge/environmental-health/search')
        .query({ factor: '空气质量' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.results)).toBe(true);
      expect(mockQueryEnvironmentalHealth).toHaveBeenCalled();
    }, 15000);
  });

  describe('GET /api/knowledge/mental-health/search', () => {
    it('应返回心理健康数据查询结果', async () => {
      const response = await request(app)
        .get('/api/knowledge/mental-health/search')
        .query({ topic: '压力管理' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.results)).toBe(true);
      expect(mockQueryMentalHealth).toHaveBeenCalled();
    }, 15000);
  });
});