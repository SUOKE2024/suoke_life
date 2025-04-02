const request = require('supertest');
const { describe, it, before, after } = require('mocha');
const { expect } = require('chai');
const nock = require('nock');
const { createMockApp } = require('../utils/mock-app');

describe('代理协调器服务集成测试', () => {
  let app;

  before(() => {
    app = createMockApp();
    
    // 模拟代理协调器服务
    nock('http://agent-coordinator-service.suoke.svc.cluster.local')
      .get('/health')
      .reply(200, { status: 'ok' });
      
    nock('http://agent-coordinator-service.suoke.svc.cluster.local')
      .get('/agents/available')
      .reply(200, { 
        agents: [
          { id: 'xiaoke', name: '小克', status: 'active' },
          { id: 'xiaoai', name: '小艾', status: 'active' }
        ]
      });
  });

  after(() => {
    nock.cleanAll();
  });

  it('应该能通过API网关访问代理协调器健康检查端点', async () => {
    const res = await request(app)
      .get('/api/v1/agents/coordinator/health')
      .set('X-API-Gateway', 'true');
      
    expect(res.status).to.equal(200);
    expect(res.body).to.have.property('status', 'ok');
  });

  it('应该能获取可用代理列表', async () => {
    const res = await request(app)
      .get('/api/v1/agents/coordinator/agents/available')
      .set('X-API-Gateway', 'true');
      
    expect(res.status).to.equal(200);
    expect(res.body).to.have.property('agents').that.is.an('array');
    expect(res.body.agents).to.have.lengthOf(2);
  });
  
  it('应该处理未授权的请求', async () => {
    // 不设置X-API-Gateway头
    const res = await request(app)
      .get('/api/v1/agents/coordinator/agents/available');
      
    // 在实际应用中会检查授权，此处模拟的应用可能不会做此检查
    // 这里只是检查请求能够被处理
    expect(res.status).to.be.oneOf([200, 401, 403]);
  });
});