/**
 * 会话路由集成测试
 */
import request from 'supertest';
import express from 'express';
import sessionRoutes from '../../../src/routes/session-routes';
import { SessionController } from '../../../src/controllers/session-controller';

// 模拟SessionController
jest.mock('../../../src/controllers/session-controller');

// 模拟validation-middleware
jest.mock('../../../src/middlewares/validation-middleware', () => ({
  validateCreateSession: jest.fn((req, res, next) => next()),
  validateUpdateSession: jest.fn((req, res, next) => next())
}));

describe('会话路由集成测试', () => {
  let app: express.Application;
  let mockCreateSession: jest.Mock;
  let mockGetSession: jest.Mock;
  let mockUpdateSession: jest.Mock;
  let mockEndSession: jest.Mock;
  let mockGetSessionMessages: jest.Mock;

  beforeEach(() => {
    // 设置mock方法
    mockCreateSession = jest.fn().mockImplementation((req, res) => {
      res.status(201).json({
        success: true,
        data: {
          sessionId: 'session123',
          userId: req.body.userId,
          agentId: req.body.preferredAgentId || 'default-agent',
          createdAt: new Date().toISOString()
        }
      });
    });

    mockGetSession = jest.fn().mockImplementation((req, res) => {
      const { sessionId } = req.params;
      if (sessionId === 'session123') {
        res.status(200).json({
          success: true,
          data: {
            sessionId: 'session123',
            userId: 'user123',
            agentId: 'agent1',
            status: 'active',
            context: {},
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        });
      } else {
        res.status(404).json({
          success: false,
          message: '会话未找到'
        });
      }
    });

    mockUpdateSession = jest.fn().mockImplementation((req, res) => {
      const { sessionId } = req.params;
      if (sessionId === 'session123') {
        res.status(200).json({
          success: true,
          data: {
            sessionId: 'session123',
            userId: 'user123',
            agentId: 'agent1',
            status: req.body.status || 'active',
            context: req.body.context || {},
            updatedAt: new Date().toISOString()
          }
        });
      } else {
        res.status(404).json({
          success: false,
          message: '会话未找到'
        });
      }
    });

    mockEndSession = jest.fn().mockImplementation((req, res) => {
      const { sessionId } = req.params;
      if (sessionId === 'session123') {
        res.status(204).end();
      } else {
        res.status(404).json({
          success: false,
          message: '会话未找到'
        });
      }
    });

    mockGetSessionMessages = jest.fn().mockImplementation((req, res) => {
      const { sessionId } = req.params;
      if (sessionId === 'session123') {
        res.status(200).json({
          success: true,
          data: {
            messages: [
              {
                id: 'msg1',
                sessionId: 'session123',
                content: '你好',
                role: 'user',
                timestamp: new Date().toISOString()
              },
              {
                id: 'msg2',
                sessionId: 'session123',
                content: '你好，有什么我可以帮助你的？',
                role: 'assistant',
                timestamp: new Date().toISOString()
              }
            ],
            total: 2
          }
        });
      } else {
        res.status(404).json({
          success: false,
          message: '会话未找到'
        });
      }
    });

    // 设置控制器mock实例
    (SessionController as jest.Mock).mockImplementation(() => ({
      createSession: mockCreateSession,
      getSession: mockGetSession,
      updateSession: mockUpdateSession,
      endSession: mockEndSession,
      getSessionMessages: mockGetSessionMessages
    }));

    // 创建Express应用
    app = express();
    app.use(express.json());
    app.use('/api/sessions', sessionRoutes);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/sessions', () => {
    it('应创建新会话', async () => {
      const response = await request(app)
        .post('/api/sessions')
        .send({
          userId: 'user123',
          preferredAgentId: 'agent1'
        });
      
      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data.sessionId).toBeTruthy();
      expect(response.body.data.userId).toBe('user123');
      expect(mockCreateSession).toHaveBeenCalled();
    });
  });

  describe('GET /api/sessions/:sessionId', () => {
    it('应返回会话详情', async () => {
      const response = await request(app).get('/api/sessions/session123');
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.sessionId).toBe('session123');
      expect(mockGetSession).toHaveBeenCalled();
    });

    it('对于不存在的会话应返回404', async () => {
      const response = await request(app).get('/api/sessions/nonexistent');
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(mockGetSession).toHaveBeenCalled();
    });
  });

  describe('PUT /api/sessions/:sessionId', () => {
    it('应更新会话信息', async () => {
      const response = await request(app)
        .put('/api/sessions/session123')
        .send({
          status: 'paused',
          context: { key: 'value' }
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('paused');
      expect(mockUpdateSession).toHaveBeenCalled();
    });

    it('对于不存在的会话应返回404', async () => {
      const response = await request(app)
        .put('/api/sessions/nonexistent')
        .send({ status: 'paused' });
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(mockUpdateSession).toHaveBeenCalled();
    });
  });

  describe('DELETE /api/sessions/:sessionId', () => {
    it('应结束会话', async () => {
      const response = await request(app).delete('/api/sessions/session123');
      
      expect(response.status).toBe(204);
      expect(mockEndSession).toHaveBeenCalled();
    });

    it('对于不存在的会话应返回404', async () => {
      const response = await request(app).delete('/api/sessions/nonexistent');
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(mockEndSession).toHaveBeenCalled();
    });
  });

  describe('GET /api/sessions/:sessionId/messages', () => {
    it('应返回会话消息历史', async () => {
      const response = await request(app)
        .get('/api/sessions/session123/messages')
        .query({ limit: 10, offset: 0 });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data.messages)).toBe(true);
      expect(response.body.data.messages.length).toBe(2);
      expect(mockGetSessionMessages).toHaveBeenCalled();
    });

    it('对于不存在的会话应返回404', async () => {
      const response = await request(app)
        .get('/api/sessions/nonexistent/messages');
      
      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(mockGetSessionMessages).toHaveBeenCalled();
    });
  });
});