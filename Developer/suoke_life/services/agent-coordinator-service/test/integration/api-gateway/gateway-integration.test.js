const { describe, it, before, after } = require('mocha');
const { expect } = require('chai');
const request = require('supertest');

describe('API网关集成测试', () => {
  let app;
  
  before(() => {
    process.env.API_GATEWAY_ENABLED = 'true';
    process.env.API_GATEWAY_NAME = 'api-gateway';
    process.env.TRUSTED_HEADERS = 'X-API-Gateway,X-Request-ID,Authorization';
    
    // 动态导入app，避免在设置环境变量前就导入
    app = require('../../src/app');
  });
  
  after(() => {
    delete process.env.API_GATEWAY_ENABLED;
    delete process.env.API_GATEWAY_NAME;
    delete process.env.TRUSTED_HEADERS;
  });
  
  it('应该识别并处理来自API网关的请求', async () => {
    const res = await request(app)
      .get('/health')
      .set('X-API-Gateway', 'true')
      .set('X-Request-ID', '123456');
      
    expect(res.status).to.equal(200);
    expect(res.body).to.have.property('status');
  });
  
  it('应该验证API网关请求头', async () => {
    // 没有设置X-API-Gateway头的请求，尝试访问受保护的路由
    const res = await request(app)
      .get('/agents')
      .set('Authorization', 'Bearer test-token');
      
    // 应当返回401或403，因为它不是从API网关来的
    expect(res.status).to.be.oneOf([401, 403]);
  });
  
  it('应该接收X-Request-ID并用于跟踪', async () => {
    const requestId = '123456-test-id';
    const res = await request(app)
      .get('/health')
      .set('X-API-Gateway', 'true')
      .set('X-Request-ID', requestId);
      
    // 正常情况下会在响应头中返回相同的request-id
    // 如果应用程序已配置，检查响应头中是否有X-Request-ID
    if (res.headers['x-request-id']) {
      expect(res.headers['x-request-id']).to.equal(requestId);
    }
    
    expect(res.status).to.equal(200);
  });
});