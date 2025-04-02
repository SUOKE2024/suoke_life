const request = require('supertest');
const app = require('../src/app');

// 模拟依赖
jest.mock('../src/utils/circuit-breaker', () => ({
  getCircuitBreakerStatus: jest.fn().mockResolvedValue({
    status: 'ok',
    timestamp: new Date().toISOString(),
    circuits: {}
  })
}));

jest.mock('../src/metrics', () => ({
  incrementCounter: jest.fn(),
  httpRequestTimer: (req, res, next) => next()
}));

// 健康检查测试
describe('健康检查接口', () => {
  it('应该返回基本健康状态', async () => {
    const response = await request(app).get('/health');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'ok');
    expect(response.body).toHaveProperty('timestamp');
    expect(response.body).toHaveProperty('service', 'soer-service');
  });
  
  it('应该返回详细就绪状态', async () => {
    const response = await request(app).get('/health/ready');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status');
    expect(response.body).toHaveProperty('timestamp');
    expect(response.body).toHaveProperty('checks');
    expect(response.body.checks).toHaveProperty('database');
    expect(response.body.checks).toHaveProperty('redis');
    expect(response.body.checks).toHaveProperty('dependencies');
    expect(response.body.checks).toHaveProperty('circuitBreaker');
  });
});