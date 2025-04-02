/**
 * 代理路由集成测试
 */
import request from 'supertest';
import express from 'express';
import agentRoutes from '../../../src/routes/agent-routes';
import { AgentController } from '../../../src/controllers/agent-controller';

// 模拟AgentController
jest.mock('../../../src/controllers/agent-controller');

// 模拟validation-middleware
jest.mock('../../../src/middlewares/validation-middleware', () => ({
  validateAgentRequest: jest.fn((req, res, next) => next())
}));

describe('代理路由集成测试', () => {
  let app: express.Application;
  let mockGetAgents: jest.Mock;
  let mockGetAgentById: jest.Mock;
  let mockCheckAgentCapability: jest.Mock;
  let mockQueryAgent: jest.Mock;
  let mockCheckAgentHealth: jest.Mock;

  beforeEach(() => {
    // 设置mock方法
    mockGetAgents = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: [{ id: 'agent1', name: 'Test Agent' }]
      });
    });

    mockGetAgentById = jest.fn().mockImplementation((req, res) => {
      const { agentId } = req.params;
      if (agentId === 'agent1') {
        res.status(200).json({
          success: true,
          data: { id: 'agent1', name: 'Test Agent' }
        });
      } else {
        res.status(404).json({
          success: false,
          message: '代理未找到'
        });
      }
    });

    mockCheckAgentCapability = jest.fn().mockImplementation((req, res) => {
      const { capability } = req.query;
      res.status(200).json({
        success: true,
        data: { hasCapability: capability === 'chat' }
      });
    });

    mockQueryAgent = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: { response: '这是代理回复' }
      });
    });

    mockCheckAgentHealth = jest.fn().mockImplementation((req, res) => {
      res.status(200).json({
        success: true,
        data: { status: 'healthy' }
      });
    });

    // 设置控制器mock实例
    (AgentController as jest.Mock).mockImplementation(() => ({
      getAgents: mockGetAgents,
      getAgentById: mockGetAgentById,
      checkAgentCapability: mockCheckAgentCapability,
      queryAgent: mockQueryAgent,
      checkAgentHealth: mockCheckAgentHealth
    }));

    // 创建Express应用
    app = express();
    app.use(express.json());
    app.use('/api/agents', agentRoutes);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /api/agents', () => {
    it('应返回代理列表', async () => {
      const response = await request(app).get('/api/agents');
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(mockGetAgents).toHaveBeenCalled();
    });
  });

  describe('GET /api/agents/:agentId', () => {
    it('应返回指定代理详情', async () => {
      const response = await request(app).get('/api/agents/agent1');
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe('agent1');
      expect(mockGetAgentById).toHaveBeenCalled();
    });

    it('对于不存在的代理应返回404', async () => {
      const response = await request(app).get('/api/agents/non-existent');
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(mockGetAgentById).toHaveBeenCalled();
    });
  });

  describe('GET /api/agents/:agentId/capabilities', () => {
    it('应检查代理能力', async () => {
      const response = await request(app)
        .get('/api/agents/agent1/capabilities')
        .query({ capability: 'chat' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.hasCapability).toBe(true);
      expect(mockCheckAgentCapability).toHaveBeenCalled();
    });

    it('对于不支持的能力应返回false', async () => {
      const response = await request(app)
        .get('/api/agents/agent1/capabilities')
        .query({ capability: 'unsupported' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.hasCapability).toBe(false);
      expect(mockCheckAgentCapability).toHaveBeenCalled();
    });
  });

  describe('POST /api/agents/:agentId/query', () => {
    it('应发送查询到代理并返回响应', async () => {
      const response = await request(app)
        .post('/api/agents/agent1/query')
        .send({
          sessionId: 'session123',
          query: '你好',
          context: { key: 'value' }
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.response).toBeTruthy();
      expect(mockQueryAgent).toHaveBeenCalled();
    });
  });

  describe('GET /api/agents/:agentId/health', () => {
    it('应检查代理健康状态', async () => {
      const response = await request(app)
        .get('/api/agents/agent1/health');
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('healthy');
      expect(mockCheckAgentHealth).toHaveBeenCalled();
    });
  });
});