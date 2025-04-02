import request from 'supertest';
import express from 'express';
import { jest } from '@jest/globals';
import { CoordinationService } from '../../../src/services/coordination-service';
import { CoordinationController } from '../../../src/controllers/coordination-controller';
import { Router } from 'express';

// 模拟协调服务
jest.mock('../../../src/services/coordination-service');

// 模拟logger避免测试输出过多日志
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

// 手动创建路由（与routes/coordination-routes.ts相同的逻辑）
function setupCoordinationRoutes(app: express.Application, controller: CoordinationController): void {
  const router = Router();
  
  router.post('/sessions', controller.createCoordinationSession);
  router.post('/analyze', controller.analyzeQuery);
  router.get('/sessions/:sessionId', controller.getCoordinationSession);
  router.get('/capabilities', controller.getSystemCapabilities);
  router.post('/handoff', controller.handoffToAgent);
  
  app.use('/api/coordination', router);
}

describe('Coordination Routes集成测试', () => {
  let app: express.Application;
  let mockCoordinationService: jest.Mocked<CoordinationService>;
  
  beforeEach(() => {
    // 清除所有模拟
    jest.clearAllMocks();
    
    // 创建Express应用
    app = express();
    app.use(express.json());
    
    // 创建模拟服务
    mockCoordinationService = {
      createSession: jest.fn(),
      analyzeQuery: jest.fn(),
      getSession: jest.fn(),
      getSystemCapabilities: jest.fn(),
      handoffToAgent: jest.fn(),
    } as unknown as jest.Mocked<CoordinationService>;
    
    // 创建控制器和路由
    const coordinationController = new CoordinationController(mockCoordinationService);
    setupCoordinationRoutes(app, coordinationController);
  });
  
  describe('POST /api/coordination/sessions', () => {
    it('应创建新的协调会话', async () => {
      // 模拟创建会话结果
      const newSession = {
        sessionId: 'session-123',
        userId: 'user-456',
        createdAt: new Date().toISOString(),
        status: 'active',
        context: { preferredLanguage: 'zh-CN' }
      };
      
      mockCoordinationService.createSession.mockResolvedValue(newSession);
      
      // 发送请求
      const response = await request(app)
        .post('/api/coordination/sessions')
        .send({
          userId: 'user-456',
          context: { preferredLanguage: 'zh-CN' }
        })
        .expect('Content-Type', /json/)
        .expect(201);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        data: newSession
      });
      
      // 验证服务调用
      expect(mockCoordinationService.createSession).toHaveBeenCalledWith(
        'user-456',
        { preferredLanguage: 'zh-CN' }
      );
    });
    
    it('当创建会话失败时应返回错误', async () => {
      // 模拟创建会话失败
      mockCoordinationService.createSession.mockRejectedValue(new Error('创建会话失败'));
      
      // 发送请求
      const response = await request(app)
        .post('/api/coordination/sessions')
        .send({
          userId: 'user-456',
          context: { preferredLanguage: 'zh-CN' }
        })
        .expect('Content-Type', /json/)
        .expect(500);
      
      // 验证响应
      expect(response.body).toEqual({
        success: false,
        error: expect.stringContaining('创建会话失败')
      });
    });
  });
  
  describe('POST /api/coordination/analyze', () => {
    it('应分析查询并返回结果', async () => {
      // 模拟分析结果
      const analysisResult = {
        queryId: 'query-789',
        domains: ['health', 'nutrition'],
        intent: 'information_seeking',
        entities: ['维生素', '健康'],
        suggestedAgents: [
          { id: 'health-agent', confidence: 0.85 },
          { id: 'nutrition-agent', confidence: 0.75 }
        ],
        sentiment: 'neutral',
        complexity: 'medium'
      };
      
      mockCoordinationService.analyzeQuery.mockResolvedValue(analysisResult);
      
      // 发送请求
      const response = await request(app)
        .post('/api/coordination/analyze')
        .send({
          query: '维生素对健康有什么好处？',
          sessionId: 'session-123',
          context: { userId: 'user-456' }
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        data: analysisResult
      });
      
      // 验证服务调用
      expect(mockCoordinationService.analyzeQuery).toHaveBeenCalledWith(
        '维生素对健康有什么好处？',
        { userId: 'user-456', sessionId: 'session-123' }
      );
    });
    
    it('当查询分析失败时应返回错误', async () => {
      // 模拟查询分析失败
      mockCoordinationService.analyzeQuery.mockRejectedValue(new Error('查询分析失败'));
      
      // 发送请求
      const response = await request(app)
        .post('/api/coordination/analyze')
        .send({
          query: '维生素对健康有什么好处？',
          sessionId: 'session-123'
        })
        .expect('Content-Type', /json/)
        .expect(500);
      
      // 验证响应
      expect(response.body).toEqual({
        success: false,
        error: expect.stringContaining('查询分析失败')
      });
    });
  });
  
  describe('GET /api/coordination/sessions/:sessionId', () => {
    it('应返回指定的协调会话', async () => {
      // 模拟会话数据
      const sessionData = {
        sessionId: 'session-123',
        userId: 'user-456',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: 'active',
        context: {
          preferredLanguage: 'zh-CN',
          interactionCount: 5
        },
        history: [
          {
            timestamp: new Date().toISOString(),
            query: '你好',
            response: '您好，有什么可以帮助您的？'
          }
        ]
      };
      
      mockCoordinationService.getSession.mockResolvedValue(sessionData);
      
      // 发送请求
      const response = await request(app)
        .get('/api/coordination/sessions/session-123')
        .expect('Content-Type', /json/)
        .expect(200);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        data: sessionData
      });
      
      // 验证服务调用
      expect(mockCoordinationService.getSession).toHaveBeenCalledWith('session-123');
    });
    
    it('当会话不存在时应返回404错误', async () => {
      // 模拟会话不存在
      mockCoordinationService.getSession.mockRejectedValue(new Error('会话不存在'));
      
      // 发送请求
      const response = await request(app)
        .get('/api/coordination/sessions/nonexistent')
        .expect('Content-Type', /json/)
        .expect(404);
      
      // 验证响应
      expect(response.body).toEqual({
        success: false,
        error: expect.stringContaining('会话不存在')
      });
    });
  });
  
  describe('GET /api/coordination/capabilities', () => {
    it('应返回系统能力信息', async () => {
      // 模拟系统能力信息
      const capabilities = {
        agents: [
          {
            id: 'health-agent',
            name: '健康代理',
            capabilities: ['health_queries', 'symptom_analysis']
          },
          {
            id: 'nutrition-agent',
            name: '营养代理',
            capabilities: ['nutrition_advice', 'diet_planning']
          }
        ],
        supportedDomains: ['health', 'nutrition', 'exercise', 'mental_health'],
        maxContextLength: 10000,
        supportedLanguages: ['zh-CN', 'en-US'],
        version: '1.0.0'
      };
      
      mockCoordinationService.getSystemCapabilities.mockResolvedValue(capabilities);
      
      // 发送请求
      const response = await request(app)
        .get('/api/coordination/capabilities')
        .expect('Content-Type', /json/)
        .expect(200);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        data: capabilities
      });
      
      // 验证服务调用
      expect(mockCoordinationService.getSystemCapabilities).toHaveBeenCalled();
    });
  });
  
  describe('POST /api/coordination/handoff', () => {
    it('应成功将会话交接给指定代理', async () => {
      // 模拟交接结果
      const handoffResult = {
        sessionId: 'session-123',
        targetAgentId: 'health-agent',
        status: 'success',
        timestamp: new Date().toISOString(),
        context: { handoffReason: '健康相关查询' }
      };
      
      mockCoordinationService.handoffToAgent.mockResolvedValue(handoffResult);
      
      // 发送请求
      const response = await request(app)
        .post('/api/coordination/handoff')
        .send({
          sessionId: 'session-123',
          targetAgentId: 'health-agent',
          context: { handoffReason: '健康相关查询' }
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        data: handoffResult
      });
      
      // 验证服务调用
      expect(mockCoordinationService.handoffToAgent).toHaveBeenCalledWith(
        'session-123',
        'health-agent',
        { handoffReason: '健康相关查询' }
      );
    });
    
    it('当交接失败时应返回错误', async () => {
      // 模拟交接失败
      mockCoordinationService.handoffToAgent.mockRejectedValue(new Error('交接失败'));
      
      // 发送请求
      const response = await request(app)
        .post('/api/coordination/handoff')
        .send({
          sessionId: 'session-123',
          targetAgentId: 'health-agent'
        })
        .expect('Content-Type', /json/)
        .expect(500);
      
      // 验证响应
      expect(response.body).toEqual({
        success: false,
        error: expect.stringContaining('交接失败')
      });
    });
  });
}); 