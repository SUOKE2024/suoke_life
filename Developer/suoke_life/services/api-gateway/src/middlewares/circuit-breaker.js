/**
 * 断路器中间件
 * 
 * 基于断路器模式，用于增强API网关的弹性，防止级联故障
 */
const logger = require('../utils/logger');

// 断路器状态
const STATE = {
  CLOSED: 'CLOSED',    // 闭合状态，可以正常通过请求
  OPEN: 'OPEN',        // 开路状态，拒绝所有请求
  HALF_OPEN: 'HALF_OPEN' // 半开状态，允许有限数量请求通过进行测试
};

/**
 * 断路器类
 */
class CircuitBreaker {
  /**
   * 创建断路器实例
   * @param {string} name 断路器名称
   * @param {Object} options 配置选项
   */
  constructor(name, options = {}) {
    this.name = name;
    this.state = STATE.CLOSED;
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 30000; // 30s
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.successThreshold = options.successThreshold || 2;
    this.successCount = 0;
    this.timeout = options.timeout || 10000; // 10s
    
    logger.info(`创建断路器: ${name}, 故障阈值: ${this.failureThreshold}, 重置超时: ${this.resetTimeout}ms`);
  }
  
  /**
   * 记录请求成功
   */
  recordSuccess() {
    if (this.state === STATE.HALF_OPEN) {
      this.successCount++;
      
      if (this.successCount >= this.successThreshold) {
        this.reset();
        logger.info(`断路器 ${this.name} 恢复正常状态`);
      }
    }
  }
  
  /**
   * 记录请求失败
   */
  recordFailure() {
    this.lastFailureTime = Date.now();
    
    if (this.state === STATE.CLOSED) {
      this.failureCount++;
      
      if (this.failureCount >= this.failureThreshold) {
        this.trip();
        logger.warn(`断路器 ${this.name} 触发开路状态`);
      }
    } else if (this.state === STATE.HALF_OPEN) {
      this.trip();
      logger.warn(`断路器 ${this.name} 在半开状态下失败，恢复到开路状态`);
    }
  }
  
  /**
   * 触发断路器开路
   */
  trip() {
    this.state = STATE.OPEN;
    setTimeout(() => this.halfOpen(), this.resetTimeout);
  }
  
  /**
   * 将断路器设为半开状态
   */
  halfOpen() {
    this.state = STATE.HALF_OPEN;
    this.successCount = 0;
    logger.info(`断路器 ${this.name} 进入半开状态，开始尝试请求`);
  }
  
  /**
   * 重置断路器状态
   */
  reset() {
    this.state = STATE.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
  }
  
  /**
   * 检查断路器是否允许请求通过
   */
  isAllowed() {
    if (this.state === STATE.CLOSED) {
      return true;
    }
    
    if (this.state === STATE.HALF_OPEN) {
      return true;
    }
    
    return false;
  }
  
  /**
   * 获取断路器状态
   */
  getState() {
    return {
      name: this.name,
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime,
      isAllowed: this.isAllowed()
    };
  }
}

// 存储所有断路器实例
const circuitBreakers = new Map();

/**
 * 获取或创建断路器
 * @param {string} name 断路器名称
 * @param {Object} options 配置选项
 * @returns {CircuitBreaker} 断路器实例
 */
function getCircuitBreaker(name, options = {}) {
  if (!circuitBreakers.has(name)) {
    circuitBreakers.set(name, new CircuitBreaker(name, options));
  }
  
  return circuitBreakers.get(name);
}

/**
 * 断路器中间件工厂函数
 * @param {string} serviceName 服务名称
 * @param {Object} options 断路器配置选项
 * @returns {Function} Express中间件
 */
function circuitBreakerMiddleware(serviceName, options = {}) {
  const circuitBreaker = getCircuitBreaker(serviceName, options);
  
  return (req, res, next) => {
    if (!circuitBreaker.isAllowed()) {
      logger.warn(`断路器 ${serviceName} 阻止请求: ${req.method} ${req.path}`);
      return res.status(503).json({
        error: '服务暂时不可用',
        message: `服务 ${serviceName} 当前不可用，请稍后再试`,
        retryAfter: Math.ceil(options.resetTimeout / 1000) || 30
      });
    }
    
    // 请求超时控制
    const timeoutId = setTimeout(() => {
      logger.warn(`请求超时: ${req.method} ${req.path}`);
      circuitBreaker.recordFailure();
      res.status(504).json({
        error: '请求超时',
        message: `服务 ${serviceName} 请求超时`
      });
    }, circuitBreaker.timeout);
    
    // 拦截响应完成事件
    const originalEnd = res.end;
    res.end = function() {
      clearTimeout(timeoutId);
      
      // 记录请求结果
      if (res.statusCode >= 500) {
        circuitBreaker.recordFailure();
      } else {
        circuitBreaker.recordSuccess();
      }
      
      return originalEnd.apply(this, arguments);
    };
    
    next();
  };
}

/**
 * 获取所有断路器状态
 * @returns {Object} 所有断路器的状态
 */
function getAllCircuitBreakersStatus() {
  const result = {};
  
  for (const [name, breaker] of circuitBreakers.entries()) {
    result[name] = breaker.getState();
  }
  
  return result;
}

module.exports = {
  circuitBreakerMiddleware,
  getCircuitBreaker,
  getAllCircuitBreakersStatus,
  STATE
};