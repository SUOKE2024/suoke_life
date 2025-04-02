/**
 * 指标中间件集成测试
 */
const { expect } = require('chai');
const express = require('express');
const request = require('supertest');
const sinon = require('sinon');

const { metricsMiddleware } = require('../../../src/middlewares/metrics.middleware');
const metricsService = require('../../../src/services/metrics.service');

describe('指标中间件集成测试', () => {
  let app;
  let sandbox;
  
  beforeEach(() => {
    // 创建测试应用
    app = express();
    app.use(metricsMiddleware);
    
    // 测试路由
    app.get('/test', (req, res) => {
      res.status(200).json({ success: true });
    });
    
    app.post('/test-post', express.json(), (req, res) => {
      res.status(201).json({ success: true, data: req.body });
    });
    
    app.get('/error', (req, res) => {
      res.status(500).json({ success: false, error: 'Server Error' });
    });
    
    // 排除路径
    app.get('/metrics', (req, res) => {
      res.status(200).json(metricsService.getMetrics());
    });
    
    app.get('/health', (req, res) => {
      res.status(200).json({ status: 'UP' });
    });
    
    // 创建沙箱
    sandbox = sinon.createSandbox();
  });
  
  afterEach(() => {
    // 重置指标
    metricsService.reset();
    
    // 恢复沙箱
    sandbox.restore();
  });
  
  it('应该统计成功的GET请求', async () => {
    // 发送请求
    await request(app)
      .get('/test')
      .set('User-Agent', 'test-agent')
      .expect(200);
    
    // 获取指标
    const metrics = metricsService.getMetrics();
    
    // 断言
    expect(metrics.counters).to.have.property('http_requests_total{method="GET",status=200,path="/test"}');
    expect(metrics.timers).to.have.property('http_request_duration_ms{method="GET",status=200,path="/test"}');
  });
  
  it('应该统计成功的POST请求', async () => {
    // 发送请求
    await request(app)
      .post('/test-post')
      .set('User-Agent', 'test-agent')
      .send({ test: 'data' })
      .expect(201);
    
    // 获取指标
    const metrics = metricsService.getMetrics();
    
    // 断言
    expect(metrics.counters).to.have.property('http_requests_total{method="POST",status=201,path="/test-post"}');
    expect(metrics.timers).to.have.property('http_request_duration_ms{method="POST",status=201,path="/test-post"}');
  });
  
  it('应该统计错误请求', async () => {
    // 发送请求
    await request(app)
      .get('/error')
      .set('User-Agent', 'test-agent')
      .expect(500);
    
    // 获取指标
    const metrics = metricsService.getMetrics();
    
    // 断言
    expect(metrics.counters).to.have.property('http_requests_total{method="GET",status=500,path="/error"}');
    expect(metrics.counters).to.have.property('http_errors_total{method="GET",status=500,path="/error"}');
    expect(metrics.timers).to.have.property('http_request_duration_ms{method="GET",status=500,path="/error"}');
  });
  
  it('应该正确统计浏览器类型', async () => {
    // 发送请求
    await request(app)
      .get('/test')
      .set('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
      .expect(200);
    
    // 获取指标
    const metrics = metricsService.getMetrics();
    
    // 断言
    expect(metrics.counters).to.have.property('client_requests{browser="chrome",browser_version="91",device_type="desktop"}');
  });
  
  it('应该正确统计移动设备', async () => {
    // 发送请求
    await request(app)
      .get('/test')
      .set('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1')
      .expect(200);
    
    // 获取指标
    const metrics = metricsService.getMetrics();
    
    // 断言
    expect(metrics.counters).to.have.property('client_requests{browser="safari",browser_version="604",device_type="mobile"}');
  });
  
  it('应该跳过排除的路径', async () => {
    // 记录初始指标
    const initialMetrics = metricsService.getMetrics();
    
    // 发送请求到排除路径
    await request(app)
      .get('/metrics')
      .set('User-Agent', 'test-agent')
      .expect(200);
    
    await request(app)
      .get('/health')
      .set('User-Agent', 'test-agent')
      .expect(200);
    
    // 获取更新后的指标
    const updatedMetrics = metricsService.getMetrics();
    
    // 断言指标没有变化
    expect(Object.keys(updatedMetrics.counters)).to.deep.equal(Object.keys(initialMetrics.counters));
  });
  
  it('应该正确维护活跃连接数', async () => {
    // 验证活跃连接数初始为0或未定义
    const initialMetrics = metricsService.getMetrics();
    const initialConnections = initialMetrics.gauges['http_active_connections'] || 0;
    
    // 模拟同时发送两个请求
    const requestPromises = [
      request(app).get('/test').set('User-Agent', 'test-agent-1'),
      request(app).get('/test').set('User-Agent', 'test-agent-2')
    ];
    
    // 等待所有请求完成
    await Promise.all(requestPromises);
    
    // 获取更新后的指标
    const updatedMetrics = metricsService.getMetrics();
    
    // 断言活跃连接数已恢复
    expect(updatedMetrics.gauges['http_active_connections']).to.equal(initialConnections);
  });
  
  it('应该处理没有User-Agent的请求', async () => {
    // 发送没有User-Agent的请求
    await request(app)
      .get('/test')
      .expect(200);
    
    // 获取指标
    const metrics = metricsService.getMetrics();
    
    // 断言
    expect(metrics.counters).to.have.property('client_requests{browser="unknown",browser_version="unknown",device_type="desktop"}');
  });
  
  it('指标收集不应影响请求处理', async () => {
    // 模拟指标服务抛出错误
    sandbox.stub(metricsService, 'increment').throws(new Error('模拟错误'));
    
    // 发送请求
    const response = await request(app)
      .get('/test')
      .set('User-Agent', 'test-agent')
      .expect(200);
    
    // 断言响应仍然正常
    expect(response.body).to.deep.equal({ success: true });
  });
}); 