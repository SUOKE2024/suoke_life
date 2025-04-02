/**
 * 代理协调器服务路由集成测试
 */
const request = require('supertest');
const nock = require('nock');
const { expect } = require('chai');
const app = require('../../../src/index');

describe('代理协调器服务路由', () => {
  beforeEach(() => {
    // 清除所有模拟的HTTP请求
    nock.cleanAll();
  });

  afterEach(() => {
    // 确保所有模拟的HTTP请求都被调用
    expect(nock.isDone()).to.be.true;
  });

  describe('GET /api/v1/agents/coordinator/health', () => {
    it('应该转发健康检查请求到代理协调器服务', async () => {
      // 模拟代理协调器服务的响应
      nock(process.env.AGENT_COORDINATOR_SERVICE_URL)
        .get('/health')
        .reply(200, {
          status: 'UP',
          timestamp: new Date().toISOString(),
          service: 'agent-coordinator-service',
          version: '1.2.0'
        });

      // 发送请求到API网关
      const response = await request(app)
        .get('/api/v1/agents/coordinator/health')
        .expect(200);

      // 验证响应
      expect(response.body).to.have.property('status', 'UP');
      expect(response.body).to.have.property('service', 'agent-coordinator-service');
    });
  });

  describe('GET /api/v1/agents/coordinator/agents', () => {
    it('应该转发获取代理列表请求到代理协调器服务', async () => {
      // 模拟代理协调器服务的响应
      nock(process.env.AGENT_COORDINATOR_SERVICE_URL)
        .get('/api/agents')
        .reply(200, {
          success: true,
          data: [
            {
              id: 'xiaoke',
              name: '小克',
              capabilities: ['服务订阅', '农产品预制', '供应链管理', '农事活动体验'],
              isDefault: true,
              description: '小克是索克生活APP的商务服务智能体，专注于农产品订制、供应链管理和商务服务'
            },
            {
              id: 'xiaoai',
              name: '小艾',
              capabilities: ['四诊合一', '问诊服务', '健康记录管理', '健康建议', '望诊诊断'],
              description: '小艾是索克生活APP的健康管理智能助理，专注于四诊合一及健康问诊服务'
            }
          ]
        });

      // 发送请求到API网关
      const response = await request(app)
        .get('/api/v1/agents/coordinator/agents')
        .expect(200);

      // 验证响应
      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.be.an('array').that.has.lengthOf(2);
      expect(response.body.data[0]).to.have.property('id', 'xiaoke');
      expect(response.body.data[1]).to.have.property('id', 'xiaoai');
    });
  });

  describe('POST /api/v1/agents/coordinator/sessions', () => {
    it('应该转发创建会话请求到代理协调器服务', async () => {
      const requestPayload = {
        userId: 'user123',
        initialContext: {
          userProfile: {
            name: '张三',
            age: 35,
            preferences: ['中医', '健康管理']
          },
          timezone: 'Asia/Shanghai'
        }
      };

      // 模拟代理协调器服务的响应
      nock(process.env.AGENT_COORDINATOR_SERVICE_URL)
        .post('/api/sessions', requestPayload)
        .reply(201, {
          success: true,
          data: {
            sessionId: 'sess_12345abcde',
            createdAt: new Date().toISOString(),
            agentId: 'xiaoai',
            status: 'active'
          }
        });

      // 发送请求到API网关
      const response = await request(app)
        .post('/api/v1/agents/coordinator/sessions')
        .send(requestPayload)
        .expect(201);

      // 验证响应
      expect(response.body).to.have.property('success', true);
      expect(response.body.data).to.have.property('sessionId', 'sess_12345abcde');
      expect(response.body.data).to.have.property('agentId', 'xiaoai');
      expect(response.body.data).to.have.property('status', 'active');
    });
  });

  describe('监控端点', () => {
    it('GET /metrics/services/agent-coordinator 应返回服务监控信息', async () => {
      const response = await request(app)
        .get('/metrics/services/agent-coordinator')
        .expect(200);

      // 验证响应包含预期的字段
      expect(response.body).to.have.property('service', 'agent-coordinator-service');
      expect(response.body).to.have.property('timestamp');
      expect(response.body).to.have.property('availability');
      expect(response.body).to.have.property('metrics');
    });
  });
}); 