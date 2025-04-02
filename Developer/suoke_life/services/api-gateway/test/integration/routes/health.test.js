/**
 * 健康检查路由集成测试
 */
const request = require('supertest');
const { expect } = require('chai');
const express = require('express');
const routes = require('../../../src/routes');

describe('健康检查端点', () => {
  let app;
  
  beforeEach(() => {
    app = express();
    app.use(routes);
  });

  describe('GET /health', () => {
    it('应返回状态码200和健康状态信息', async () => {
      const response = await request(app)
        .get('/health')
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body).to.have.property('status', 'ok');
      expect(response.body).to.have.property('service');
      expect(response.body).to.have.property('timestamp');
    });
  });

  describe('GET /health/ready', () => {
    it('应返回状态码200和就绪状态信息', async () => {
      // 模拟app.get('serviceLBMap')返回值
      app.get = () => new Map();
      
      const response = await request(app)
        .get('/health/ready')
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body).to.have.property('status', 'ready');
      expect(response.body).to.have.property('uptime');
      expect(response.body).to.have.property('services');
    });
  });
  
  describe('GET /', () => {
    it('应返回API根路径信息', async () => {
      const response = await request(app)
        .get('/')
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body).to.have.property('service');
      expect(response.body).to.have.property('version');
      expect(response.body).to.have.property('endpoints');
      expect(response.body.endpoints).to.have.property('health');
      expect(response.body.endpoints).to.have.property('ready');
    });
  });
});