/**
 * 指标服务单元测试
 */
const { expect } = require('chai');
const sinon = require('sinon');
const proxyquire = require('proxyquire');

describe('MetricsService', () => {
  let metricsService;
  let loggerStub;

  beforeEach(() => {
    // 创建logger的stub
    loggerStub = {
      debug: sinon.stub(),
      error: sinon.stub()
    };

    // 使用proxyquire加载指标服务，替换logger依赖
    metricsService = proxyquire('../../../src/services/metrics.service', {
      '../utils/logger': loggerStub
    });

    // 每个测试前重置指标
    metricsService.reset();
  });

  afterEach(() => {
    // 恢复所有stubs
    sinon.restore();
  });

  describe('increment', () => {
    it('应该增加计数器值', () => {
      // 执行
      metricsService.increment('test_counter');
      metricsService.increment('test_counter');

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.counters).to.have.property('test_counter', 2);
      expect(loggerStub.debug.calledTwice).to.be.true;
    });

    it('应该使用自定义值增加计数器', () => {
      // 执行
      metricsService.increment('test_counter', {}, 5);

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.counters).to.have.property('test_counter', 5);
    });

    it('应该处理带标签的计数器', () => {
      // 执行
      metricsService.increment('test_counter', { service: 'auth' });

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.counters).to.have.property('test_counter{service="auth"}', 1);
    });

    it('应该处理错误并记录日志', () => {
      // 设置
      const error = new Error('测试错误');
      const formatKeyStub = sinon.stub(metricsService, '_formatKey').throws(error);

      // 执行
      metricsService.increment('test_counter');

      // 验证
      expect(loggerStub.error.calledOnce).to.be.true;
      expect(loggerStub.error.firstCall.args[0]).to.equal('指标增加失败: test_counter');
      expect(loggerStub.error.firstCall.args[1]).to.equal(error);

      // 清理
      formatKeyStub.restore();
    });
  });

  describe('gauge', () => {
    it('应该设置指标值', () => {
      // 执行
      metricsService.gauge('test_gauge', 100);

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.gauges).to.have.property('test_gauge', 100);
    });

    it('应该更新指标值', () => {
      // 执行
      metricsService.gauge('test_gauge', 100);
      metricsService.gauge('test_gauge', 200);

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.gauges).to.have.property('test_gauge', 200);
    });
  });

  describe('timing', () => {
    it('应该记录时间指标', () => {
      // 执行
      metricsService.timing('test_timing', 100);
      metricsService.timing('test_timing', 200);

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.timers).to.have.property('test_timing');
      expect(metrics.timers['test_timing']).to.deep.equal([100, 200]);
    });
  });

  describe('observe', () => {
    it('应该观察直方图数据', () => {
      // 执行
      metricsService.observe('test_histogram', 10);
      metricsService.observe('test_histogram', 20);
      metricsService.observe('test_histogram', 30);

      // 验证
      const metrics = metricsService.getMetrics();
      expect(metrics.histograms).to.have.property('test_histogram');
      expect(metrics.histograms['test_histogram']).to.deep.equal([10, 20, 30]);
    });
  });

  describe('startTimer', () => {
    it('应该返回计时器函数并记录时间', () => {
      // 设置
      const clock = sinon.useFakeTimers();
      
      // 执行
      const endTimer = metricsService.startTimer('test_timer');
      clock.tick(100);
      const duration = endTimer();

      // 验证
      expect(duration).to.equal(100);
      const metrics = metricsService.getMetrics();
      expect(metrics.timers).to.have.property('test_timer');
      expect(metrics.timers['test_timer']).to.deep.equal([100]);

      // 清理
      clock.restore();
    });
  });

  describe('getMetrics', () => {
    it('应该返回所有指标', () => {
      // 设置
      metricsService.increment('test_counter');
      metricsService.gauge('test_gauge', 100);
      metricsService.timing('test_timer', 200);
      metricsService.observe('test_histogram', 300);

      // 执行
      const metrics = metricsService.getMetrics();

      // 验证
      expect(metrics).to.have.property('counters');
      expect(metrics).to.have.property('gauges');
      expect(metrics).to.have.property('timers');
      expect(metrics).to.have.property('histograms');
      expect(metrics.counters).to.have.property('test_counter', 1);
      expect(metrics.gauges).to.have.property('test_gauge', 100);
      expect(metrics.timers).to.have.property('test_timer');
      expect(metrics.timers['test_timer']).to.deep.equal([200]);
      expect(metrics.histograms).to.have.property('test_histogram');
      expect(metrics.histograms['test_histogram']).to.deep.equal([300]);
    });
  });

  describe('_formatKey', () => {
    it('应该格式化无标签的键', () => {
      // 执行
      const key = metricsService._formatKey('test_key', {});

      // 验证
      expect(key).to.equal('test_key');
    });

    it('应该格式化带单个标签的键', () => {
      // 执行
      const key = metricsService._formatKey('test_key', { label: 'value' });

      // 验证
      expect(key).to.equal('test_key{label="value"}');
    });

    it('应该格式化带多个标签的键', () => {
      // 执行
      const key = metricsService._formatKey('test_key', { label1: 'value1', label2: 'value2' });

      // 验证
      expect(key).to.equal('test_key{label1="value1",label2="value2"}');
    });
  });

  describe('reset', () => {
    it('应该重置所有指标', () => {
      // 设置
      metricsService.increment('test_counter');
      metricsService.gauge('test_gauge', 100);
      metricsService.timing('test_timer', 200);
      metricsService.observe('test_histogram', 300);

      // 执行
      metricsService.reset();

      // 验证
      const metrics = metricsService.getMetrics();
      expect(Object.keys(metrics.counters)).to.have.length(0);
      expect(Object.keys(metrics.gauges)).to.have.length(0);
      expect(Object.keys(metrics.timers)).to.have.length(0);
      expect(Object.keys(metrics.histograms)).to.have.length(0);
    });
  });
});
