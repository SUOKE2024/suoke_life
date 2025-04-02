/**
 * 速率限制中间件
 * 防止API滥用和DoS攻击
 */
const rateLimit = require('express-rate-limit');
const { StatusCodes } = require('http-status-codes');
const { createLogger } = require('../utils/logger');
const config = require('../config');
const { metrics } = require('../utils');

const logger = createLogger('rate-limit');

// 获取速率限制配置
const rateLimitConfig = config.security.rateLimiting || {};

// 创建速率限制器
const rateLimiter = rateLimit({
  windowMs: rateLimitConfig.windowMs || 15 * 60 * 1000, // 默认15分钟
  max: rateLimitConfig.maxRequests || 100, // 默认每个IP最多100个请求
  standardHeaders: true, // 返回标准的RateLimit头
  legacyHeaders: false, // 禁用X-RateLimit-*头
  
  // 自定义处理程序
  handler: (req, res, next, options) => {
    // 记录速率限制事件
    logger.warn('速率限制超出', {
      ip: req.ip,
      path: req.path,
      method: req.method,
      requestId: req.requestId,
      userId: req.user ? req.user.id : undefined,
      limit: options.max,
      window: options.windowMs
    });
    
    // 记录指标
    metrics.trackRateLimitMetrics(req.path, req.method);
    
    // 返回本地化的错误消息
    res.status(StatusCodes.TOO_MANY_REQUESTS).json({
      success: false,
      message: req.t('common.rate_limit', { namespace: 'errors' }),
      retryAfter: Math.ceil(options.windowMs / 1000),
      requestId: req.requestId
    });
  },
  
  // 跳过速率限制的请求
  skip: (req, res) => {
    // 健康检查和指标端点不受限制
    if (req.path === '/health' || req.path === '/health/readiness' || req.path === '/metrics') {
      return true;
    }
    
    // 可以根据用户角色跳过限制
    if (req.user && req.user.role === 'admin') {
      return true;
    }
    
    return false;
  },
  
  // 自定义密钥生成器
  keyGenerator: (req, res) => {
    // 如果用户已认证，使用用户ID作为键
    if (req.user && req.user.id) {
      return `user:${req.user.id}`;
    }
    
    // 否则使用IP地址
    return req.ip;
  }
});

/**
 * 创建特定路由的速率限制器
 * @param {Object} options - 速率限制选项
 * @returns {Function} - 速率限制中间件
 */
const createRouteLimiter = (options) => {
  const routeOptions = {
    windowMs: options.windowMs || rateLimitConfig.windowMs || 15 * 60 * 1000,
    max: options.max || rateLimitConfig.maxRequests || 100,
    standardHeaders: true,
    legacyHeaders: false,
    
    // 自定义处理程序
    handler: (req, res, next, opts) => {
      // 记录速率限制事件
      logger.warn('路由速率限制超出', {
        ip: req.ip,
        path: req.path,
        method: req.method,
        requestId: req.requestId,
        userId: req.user ? req.user.id : undefined,
        limit: opts.max,
        window: opts.windowMs,
        routeName: options.routeName || req.path
      });
      
      // 记录指标
      metrics.trackRateLimitMetrics(req.path, req.method, options.routeName);
      
      // 返回本地化的错误消息
      res.status(StatusCodes.TOO_MANY_REQUESTS).json({
        success: false,
        message: req.t('common.rate_limit', { namespace: 'errors' }),
        retryAfter: Math.ceil(opts.windowMs / 1000),
        requestId: req.requestId
      });
    },
    
    // 自定义密钥生成器
    keyGenerator: options.keyGenerator || ((req, res) => {
      // 如果用户已认证，使用用户ID作为键
      if (req.user && req.user.id) {
        return `${options.routeName || req.path}:user:${req.user.id}`;
      }
      
      // 否则使用IP地址
      return `${options.routeName || req.path}:ip:${req.ip}`;
    }),
    
    // 跳过速率限制的请求
    skip: options.skip || ((req, res) => {
      // 可以根据用户角色跳过限制
      if (req.user && (req.user.role === 'admin' || req.user.role === 'system')) {
        return true;
      }
      
      return false;
    })
  };
  
  return rateLimit(routeOptions);
};

// 创建登录路由的速率限制器
const loginLimiter = createRouteLimiter({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 5, // 每个IP最多5次尝试
  routeName: 'login',
  // 不跳过任何请求
  skip: () => false
});

// 创建注册路由的速率限制器
const registerLimiter = createRouteLimiter({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 3, // 每个IP最多3次尝试
  routeName: 'register',
  // 不跳过任何请求
  skip: () => false
});

// 创建密码重置路由的速率限制器
const passwordResetLimiter = createRouteLimiter({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 3, // 每个IP最多3次尝试
  routeName: 'password-reset',
  // 不跳过任何请求
  skip: () => false
});

// 创建验证码发送路由的速率限制器
const verificationCodeLimiter = createRouteLimiter({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 5, // 每个IP最多5次尝试
  routeName: 'verification-code',
  // 不跳过任何请求
  skip: () => false
});

module.exports = {
  rateLimiter,
  createRouteLimiter,
  loginLimiter,
  registerLimiter,
  passwordResetLimiter,
  verificationCodeLimiter
}; 