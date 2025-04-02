import request from 'supertest';
import express from 'express';
import { CoordinationService } from '../../src/services/coordination-service';
import { AgentService } from '../../src/services/agent-service';
import { KnowledgeService } from '../../src/services/knowledge-service';
import { CoordinationController } from '../../src/controllers/coordination-controller';
import { AgentController } from '../../src/controllers/agent-controller';
import { KnowledgeController } from '../../src/controllers/knowledge-controller';
import { Router } from 'express';

// 模拟服务
jest.mock('../../src/services/coordination-service');
jest.mock('../../src/services/agent-service');
jest.mock('../../src/services/knowledge-service');

// 模拟logger避免测试输出过多日志
jest.mock('../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

// 设置路由
function setupRoutes(app: express.Application): void {
  // 协调服务路由
  const coordinationRouter = Router();
  const coordinationController = new CoordinationController(new CoordinationService());
  coordinationRouter.post('/sessions', coordinationController.createCoordinationSession);
  coordinationRouter.post('/analyze', coordinationController.analyzeQuery);
  coordinationRouter.get('/capabilities', coordinationController.getSystemCapabilities);
  app.use('/api/coordination', coordinationRouter);
  
  // 代理服务路由
  const agentRouter = Router();
  const agentController = new AgentController(new AgentService());
  agentRouter.get('/', agentController.getAgents);
  agentRouter.get('/:agentId', agentController.getAgentById);
  agentRouter.post('/:agentId/query', agentController.queryAgent);
  app.use('/api/agents', agentRouter);
  
  // 知识服务路由
  const knowledgeRouter = Router();
  const knowledgeController = new KnowledgeController(new KnowledgeService());
  knowledgeRouter.get('/search', knowledgeController.searchKnowledge);
  knowledgeRouter.get('/graph', knowledgeController.queryKnowledgeGraph);
  knowledgeRouter.post('/rag', knowledgeController.generateRAGResponse);
  app.use('/api/knowledge', knowledgeRouter);
}

/**
 * 测量API响应时间的辅助函数
 * @param request 请求对象
 * @returns 返回响应和耗时（毫秒）
 */
async function measureResponseTime(req: request.Test): Promise<{response: request.Response, duration: number}> {
  const startTime = process.hrtime();
  const response = await req;
  const hrtime = process.hrtime(startTime);
  const duration = hrtime[0] * 1000 + hrtime[1] / 1000000; // 转换为毫秒
  
  return { response, duration };
}

// 性能测试套件
describe('API性能测试', () => {
  let app: express.Application;
  
  beforeAll(() => {
    // 设置Express应用
    app = express();
    app.use(express.json());
    setupRoutes(app);
    
    // 配置模拟服务的响应
    const mockCoordinationService = new CoordinationService() as jest.Mocked<CoordinationService>;
    mockCoordinationService.analyzeQuery = jest.fn().mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            domains: ['health', 'nutrition'],
            intent: 'information_seeking',
            entities: ['维生素', '健康'],
            sentiment: 'neutral',
            complexityLevel: 'medium',
            suggestedAgents: ['health_agent', 'nutrition_agent'],
            confidence: 0.85
          });
        }, 10); // 模拟10ms延迟
      });
    });
    
    const mockKnowledgeService = new KnowledgeService() as jest.Mocked<KnowledgeService>;
    mockKnowledgeService.searchKnowledge = jest.fn().mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve([
            {
              id: 'knowledge1',
              title: '健康知识1',
              content: '测试内容1',
              domain: 'health',
              type: 'article',
              tags: ['健康', '养生'],
              confidence: 0.85,
              source: 'test-source'
            }
          ]);
        }, 20); // 模拟20ms延迟
      });
    });
  });
  
  describe('响应时间测试', () => {
    // 响应时间阈值（毫秒）
    const RESPONSE_TIME_THRESHOLD = 100;
    
    test('协调服务API响应时间应在阈值内', async () => {
      // 测试分析查询端点
      const { response, duration } = await measureResponseTime(
        request(app)
          .post('/api/coordination/analyze')
          .send({
            query: '维生素对健康有什么好处？',
            context: { userId: 'user123' }
          })
      );
      
      // 验证响应状态
      expect(response.status).toBe(200);
      
      // 验证响应时间
      expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);
      console.log(`分析查询响应时间: ${duration.toFixed(2)}ms`);
    });
    
    test('知识搜索API响应时间应在阈值内', async () => {
      // 测试知识搜索端点
      const { response, duration } = await measureResponseTime(
        request(app)
          .get('/api/knowledge/search')
          .query({ query: '健康知识' })
      );
      
      // 验证响应状态
      expect(response.status).toBe(200);
      
      // 验证响应时间
      expect(duration).toBeLessThan(RESPONSE_TIME_THRESHOLD);
      console.log(`知识搜索响应时间: ${duration.toFixed(2)}ms`);
    });
  });
  
  describe('负载测试', () => {
    test('协调服务应能处理连续多个请求', async () => {
      const REQUEST_COUNT = 10;
      const requests = Array(REQUEST_COUNT).fill(0).map(() => 
        measureResponseTime(
          request(app)
            .post('/api/coordination/analyze')
            .send({
              query: '维生素对健康有什么好处？',
              context: { userId: 'user123' }
            })
        )
      );
      
      // 并发执行所有请求
      const results = await Promise.all(requests);
      
      // 计算平均响应时间
      const totalDuration = results.reduce((sum, { duration }) => sum + duration, 0);
      const averageDuration = totalDuration / REQUEST_COUNT;
      
      // 所有请求均应成功
      results.forEach(({ response }) => {
        expect(response.status).toBe(200);
      });
      
      // 记录性能指标
      console.log(`负载测试结果 (${REQUEST_COUNT}个请求):`);
      console.log(`  平均响应时间: ${averageDuration.toFixed(2)}ms`);
      console.log(`  最长响应时间: ${Math.max(...results.map(r => r.duration)).toFixed(2)}ms`);
      console.log(`  最短响应时间: ${Math.min(...results.map(r => r.duration)).toFixed(2)}ms`);
    });
  });
  
  describe('内存使用测试', () => {
    test('应能监控API请求的内存使用', async () => {
      // 记录初始内存使用
      const initialMemory = process.memoryUsage();
      
      // 执行大量请求
      const REQUEST_COUNT = 50;
      const requests = Array(REQUEST_COUNT).fill(0).map(() => 
        request(app)
          .get('/api/knowledge/search')
          .query({ query: '健康知识' })
      );
      
      // 并发执行所有请求
      await Promise.all(requests);
      
      // 记录结束时内存使用
      const finalMemory = process.memoryUsage();
      
      // 计算内存使用变化
      const heapUsedDiff = finalMemory.heapUsed - initialMemory.heapUsed;
      const heapTotalDiff = finalMemory.heapTotal - initialMemory.heapTotal;
      
      // 记录内存使用指标
      console.log('内存使用变化:');
      console.log(`  堆内存使用: ${(heapUsedDiff / 1024 / 1024).toFixed(2)}MB`);
      console.log(`  堆内存总量: ${(heapTotalDiff / 1024 / 1024).toFixed(2)}MB`);
      
      // 此测试仅记录内存使用，不做断言
      // 在实际场景中，可以根据应用特性设置合理的内存使用阈值
      expect(true).toBe(true);
    });
  });
}); 