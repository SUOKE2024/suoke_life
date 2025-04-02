/**
 * 索儿服务断路器工具
 * 实现服务熔断和降级功能，防止故障级联传播
 */
const Opossum = require('opossum');
const logger = require('./logger');
const { incrementCounter, setGauge } = require('../metrics');

// 存储断路器实例
const circuitBreakers = new Map();

// 默认断路器选项
const defaultOptions = {
  timeout: 5000, // 5秒超时
  errorThresholdPercentage: 50, // 50%的错误率将触发断路器
  resetTimeout: 10000, // 10秒后重置为半开状态
  rollingCountTimeout: 60000, // 统计窗口为60秒
  rollingCountBuckets: 10, // 将窗口划分为10个桶
  name: 'default' // 默认名称
};

/**
 * 创建断路器
 * @param {Function} action 需要保护的函数
 * @param {String} name 断路器名称
 * @param {Object} options 断路器选项
 * @returns {Opossum} 断路器实例
 */
function createCircuitBreaker(action, name, options = {}) {
  const breaker = new Opossum(action, {
    ...defaultOptions,
    ...options,
    name
  });
  
  // 添加事件监听器
  breaker.on('open', () => {
    logger.warn(`断路器 ${name} 已开启 - 停止执行受保护的函数`);
    incrementCounter('errorTotal', { module: 'circuit-breaker', code: 'open' });
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  breaker.on('halfOpen', () => {
    logger.info(`断路器 ${name} 处于半开状态 - 正在测试受保护的函数`);
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  breaker.on('close', () => {
    logger.info(`断路器 ${name} 已关闭 - 正常执行受保护的函数`);
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  breaker.on('fallback', (result) => {
    logger.info(`断路器 ${name} 使用了降级方案`);
    incrementCounter('businessOperationsTotal', { operation: `fallback_${name}`, status: 'success' });
  });
  
  breaker.on('success', () => {
    incrementCounter('businessOperationsTotal', { operation: name, status: 'success' });
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  breaker.on('failure', (error) => {
    logger.error(`断路器 ${name} 操作失败`, { error: error.message });
    incrementCounter('errorTotal', { module: 'circuit-breaker', code: 'failure' });
    incrementCounter('businessOperationsTotal', { operation: name, status: 'failure' });
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  breaker.on('timeout', () => {
    logger.warn(`断路器 ${name} 操作超时`);
    incrementCounter('errorTotal', { module: 'circuit-breaker', code: 'timeout' });
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  breaker.on('reject', () => {
    logger.warn(`断路器 ${name} 拒绝操作`);
    incrementCounter('errorTotal', { module: 'circuit-breaker', code: 'reject' });
    updateCircuitBreakerMetrics(name, breaker);
  });
  
  // 存储断路器实例
  circuitBreakers.set(name, breaker);
  return breaker;
}

/**
 * 获取断路器实例
 * @param {String} name 断路器名称
 * @returns {Opossum|null} 断路器实例或null
 */
function getCircuitBreaker(name) {
  return circuitBreakers.get(name) || null;
}

/**
 * 获取所有断路器状态
 * @returns {Object} 断路器状态映射
 */
function getCircuitBreakerStatus() {
  const statuses = {};
  let overallStatus = 'ok';
  
  for (const [name, breaker] of circuitBreakers.entries()) {
    const stats = breaker.stats;
    const status = breaker.status;
    
    statuses[name] = {
      status: status === 'closed' ? 'ok' : (status === 'open' ? 'error' : 'warning'),
      state: status,
      stats: {
        successes: stats.successes,
        failures: stats.failures,
        rejects: stats.rejects,
        timeouts: stats.timeouts,
        errorRate: stats.failures / (stats.successes + stats.failures) * 100 || 0
      }
    };
    
    // 更新整体状态
    if (status === 'open' && overallStatus === 'ok') {
      overallStatus = 'degraded';
    }
  }
  
  return {
    status: overallStatus,
    timestamp: new Date().toISOString(),
    circuits: statuses
  };
}

/**
 * 更新断路器指标
 * @param {String} name 断路器名称
 * @param {Opossum} breaker 断路器实例
 */
function updateCircuitBreakerMetrics(name, breaker) {
  const stats = breaker.stats;
  const status = breaker.status;
  
  // 设置断路器状态指标
  setGauge('resourceUsage', status === 'closed' ? 0 : (status === 'open' ? 1 : 0.5), {
    resource: `circuitBreaker_${name}`
  });
  
  // 设置错误率指标
  const errorRate = stats.failures / (stats.successes + stats.failures) * 100 || 0;
  setGauge('cacheHitRatio', errorRate, { cache: `circuitBreaker_${name}_errorRate` });
}

module.exports = {
  createCircuitBreaker,
  getCircuitBreaker,
  getCircuitBreakerStatus
};