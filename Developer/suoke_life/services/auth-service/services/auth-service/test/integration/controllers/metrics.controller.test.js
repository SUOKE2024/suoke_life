/**
 * 指标控制器集成测试
 */
const request = require('supertest');
const { expect } = require('chai');
const sinon = require('sinon');
const express = require('express');
const metricsController = require('../../../src/controllers/metrics.controller');
const metricsService = require('../../../src/services/metrics.service');

describe('指标控制器', () => {
  let app;

  beforeEach(() => {
    // 创建测试用Express应用
    app = express();
    app.use(express.json());
    app.use('/api/metrics', metricsController);

    // 重置指标服务
    metricsService.reset();

    // 添加一些测试指标
    metricsService.increment('test_counter', {}, 5);
    metricsService.gauge('test_gauge', 100);
    metricsService.timing('test_timer', 200);
    metricsService.observe('test_histogram', 300);
  });

  afterEach(() => {
    // 恢复所有stubs
    sinon.restore();
  });

  describe('GET /api/metrics', () => {
    it('应该返回所有指标', async () => {
      // 执行
      const response = await request(app)
        .get('/api/metrics')
        .expect('Content-Type', /json/)
        .expect(200);

      // 验证
      expect(response.body).to.have.property('counters');
      expect(response.body).to.have.property('gauges');
      expect(response.body).to.have.property('timers');
      expect(response.body).to.have.property('histograms');
      expect(response.body.counters).to.have.property('test_counter', 5);
      expect(response.body.gauges).to.have.property('test_gauge', 100);
      expect(response.body.timers).to.have.property('test_timer');
      expect(response.body.timers['test_timer']).to.deep.equal([200]);
      expect(response.body.histograms).to.have.property('test_histogram');
      expect(response.body.histograms['test_histogram']).to.deep.equal([300]);
    });
  });

  describe('DELETE /api/metrics', () => {
    it('应该重置所有指标', async () => {
      // 执行
      const response = await request(app)
        .delete('/api/metrics')
        .expect(204);

      // 验证
      expect(response.body).to.be.empty;
      
      // 获取指标并验证已清空
      const metrics = metricsService.getMetrics();
      expect(Object.keys(metrics.counters)).to.have.length(0);
      expect(Object.keys(metrics.gauges)).to.have.length(0);
      expect(Object.keys(metrics.timers)).to.have.length(0);
      expect(Object.keys(metrics.histograms)).to.have.length(0);
    });
  });
});
