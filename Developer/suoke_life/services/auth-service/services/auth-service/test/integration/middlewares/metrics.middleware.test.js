/**
 * 指标中间件集成测试
 */
const request = require('supertest');
const { expect } = require('chai');
const express = require('express');
const sinon = require('sinon');
const metricsMiddleware = require('../../../src/middlewares/metrics.middleware');
const metricsService = require('../../../src/services/metrics.service');

describe('指标中间件', () => {
  let app;
  let getMetricsStub;

  beforeEach(() => {
    // 创建测试用Express应用
    app = express();
    
    // 应用指标中间件
    app.use(metricsMiddleware);
    
    // 添加测试路由
    app.get('/test', (req, res) => {
      res.status(200).json({ success: true });
    });
    
    app.get('/error', (req, res) => {
      res.status(500).json({ error: 'Test error' });
    });
    
    // 重置指标服务
    metricsService.reset();
  });

  afterEach(() => {
    // 恢复所有stubs
    sinon.restore();
  });

  it('应该记录成功请求的指标', async () => {
    // 执行
    await request(app)
      .get('/test')
      .expect(200);

    // 验证
    const metrics = metricsService.getMetrics();
    
    // 检查请求总数
    expect(metrics.counters).to.have.property('http_requests_total{method="GET",path="/test"}', 1);
    
    // 检查响应计数
    expect(metrics.counters).to.have.property('http_responses_total{method="GET",path="/test",status=200}', 1);
    
    // 检查是否有请求持续时间
    expect(metrics.timers).to.have.property('http_request_duration{method="GET",path="/test"}');
    expect(metrics.timers['http_request_duration{method="GET",path="/test"}'].length).to.equal(1);
  });

  it('应该记录错误请求的指标', async () => {
    // 执行
    await request(app)
      .get('/error')
      .expect(500);

    // 验证
    const metrics = metricsService.getMetrics();
    
    // 检查请求总数
    expect(metrics.counters).to.have.property('http_requests_total{method="GET",path="/error"}', 1);
    
    // 检查响应计数
    expect(metrics.counters).to.have.property('http_responses_total{method="GET",path="/error",status=500}', 1);
    
    // 检查错误计数
    expect(metrics.counters).to.have.property('http_errors_total{method="GET",path="/error",status=500}', 1);
    
    // 检查是否有请求持续时间
    expect(metrics.timers).to.have.property('http_request_duration{method="GET",path="/error"}');
    expect(metrics.timers['http_request_duration{method="GET",path="/error"}'].length).to.equal(1);
  });

  it('应该跟踪活跃连接数', async () => {
    // 执行第一个请求
    await request(app)
      .get('/test')
      .expect(200);

    // 验证活跃连接数更新后归零
    const metrics = metricsService.getMetrics();
    expect(metrics.gauges).to.have.property('http_active_connections', 0);
  });
});
