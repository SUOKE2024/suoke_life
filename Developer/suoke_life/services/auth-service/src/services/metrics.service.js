/**
 * 指标服务
 */
const logger = require('../utils/logger');

/**
 * 指标服务
 */
class MetricsService {
  constructor() {
    this.metrics = {
      counters: new Map(),
      gauges: new Map(),
      histograms: new Map(),
      timers: new Map()
    };
  }

  /**
   * 增加计数器值
   * @param {string} name - 指标名称
   * @param {Object} [labels] - 标签
   * @param {number} [value=1] - 增加值
   */
  increment(name, labels = {}, value = 1) {
    try {
      const key = this._formatKey(name, labels);
      const counter = this.metrics.counters.get(key) || 0;
      this.metrics.counters.set(key, counter + value);
      logger.debug(`指标增加: ${key} => ${counter + value}`);
    } catch (error) {
      logger.error(`指标增加失败: ${name}`, error);
    }
  }

  /**
   * 设置指标值
   * @param {string} name - 指标名称
   * @param {number} value - 指标值
   * @param {Object} [labels] - 标签
   */
  gauge(name, value, labels = {}) {
    try {
      const key = this._formatKey(name, labels);
      this.metrics.gauges.set(key, value);
      logger.debug(`指标设置: ${key} => ${value}`);
    } catch (error) {
      logger.error(`指标设置失败: ${name}`, error);
    }
  }

  /**
   * 记录时间指标
   * @param {string} name - 指标名称
   * @param {number} value - 时间值（毫秒）
   * @param {Object} [labels] - 标签
   */
  timing(name, value, labels = {}) {
    try {
      const key = this._formatKey(name, labels);
      const times = this.metrics.timers.get(key) || [];
      times.push(value);
      this.metrics.timers.set(key, times);
      logger.debug(`时间指标: ${key} => ${value}ms`);
    } catch (error) {
      logger.error(`时间指标记录失败: ${name}`, error);
    }
  }

  /**
   * 观察直方图数据
   * @param {string} name - 指标名称
   * @param {number} value - 观察值
   * @param {Object} [labels] - 标签
   */
  observe(name, value, labels = {}) {
    try {
      const key = this._formatKey(name, labels);
      const values = this.metrics.histograms.get(key) || [];
      values.push(value);
      this.metrics.histograms.set(key, values);
      logger.debug(`直方图观察: ${key} => ${value}`);
    } catch (error) {
      logger.error(`直方图观察失败: ${name}`, error);
    }
  }

  /**
   * 启动计时器
   * @param {string} name - 指标名称
   * @param {Object} [labels] - 标签
   * @returns {Function} 结束计时器的函数
   */
  startTimer(name, labels = {}) {
    const startTime = Date.now();
    return () => {
      const duration = Date.now() - startTime;
      this.timing(name, duration, labels);
      return duration;
    };
  }

  /**
   * 获取所有指标
   * @returns {Object} 所有指标
   */
  getMetrics() {
    return {
      counters: Object.fromEntries(this.metrics.counters),
      gauges: Object.fromEntries(this.metrics.gauges),
      histograms: Object.fromEntries(this.metrics.histograms),
      timers: Object.fromEntries(this.metrics.timers)
    };
  }

  /**
   * 格式化指标键
   * @private
   * @param {string} name - 指标名称
   * @param {Object} labels - 标签
   * @returns {string} 格式化的键
   */
  _formatKey(name, labels) {
    if (!Object.keys(labels).length) {
      return name;
    }
    
    const labelsStr = Object.entries(labels)
      .map(([k, v]) => `${k}="${v}"`)
      .join(',');
    
    return `${name}{${labelsStr}}`;
  }

  /**
   * 重置所有指标
   */
  reset() {
    this.metrics.counters.clear();
    this.metrics.gauges.clear();
    this.metrics.histograms.clear();
    this.metrics.timers.clear();
    logger.debug('指标已重置');
  }
}

// 单例
const metricsService = new MetricsService();

module.exports = metricsService;