/**
 * 速率限制中间件
 */
const { rateLimit } = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = require('../config/redis');
const { logger } = require('@suoke/shared').utils;

/**
 * 创建通用速率限制中间件
 * 
 * @param {Object} options - 速率限制选项
 * @returns {Function} Express中间件
 */
const createRateLimiter = (options = {}) => {
  const {
    windowMs = 15 * 60 * 1000, // 默认15分钟
    max = 100, // 默认最多100个请求
    message = '请求过于频繁，请稍后再试',
    keyGenerator,
    skip,
    handler,
    prefix = 'rl:common:'
  } = options;
  
  return rateLimit({
    windowMs,
    max,
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req, res) => {
      // 跳过健康检查和API文档路径
      if (req.path.startsWith('/health') || 
          req.path.startsWith('/api-docs') || 
          req.path.startsWith('/metrics')) {
        return true;
      }
      
      // 使用自定义跳过函数(如果提供)
      return skip ? skip(req, res) : false;
    },
    keyGenerator: keyGenerator || ((req) => {
      // 默认使用IP + 用户ID(如果有)作为键
      const userId = req.user?.id || '';
      return `${req.ip}:${userId}`;
    }),
    handler: handler || ((req, res) => {
      logger.warn(`速率限制触发: IP=${req.ip}, 路径=${req.path}`);
      return res.status(429).json({
        success: false,
        message,
        retryAfter: Math.ceil(windowMs / 1000)
      });
    }),
    store: new RedisStore({
      // @ts-ignore
      sendCommand: (...args) => redis.call(...args),
      prefix
    })
  });
};

/**
 * API通用速率限制 - 适用于所有API
 */
const globalLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 300, // 每IP 15分钟内300个请求
  message: '请求过于频繁，请稍后再试',
  prefix: 'rl:global:'
});

/**
 * 登录请求速率限制 - 防止暴力破解
 */
const loginLimiter = createRateLimiter({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 10, // 每IP 1小时内10次登录尝试
  message: '登录尝试次数过多，请1小时后再试',
  prefix: 'rl:login:',
  keyGenerator: (req) => {
    // 使用用户名+IP作为键，防止针对特定用户的暴力破解
    const username = req.body.username || '';
    return `${username}:${req.ip}`;
  }
});

/**
 * 注册请求速率限制 - 防止批量注册
 */
const registerLimiter = createRateLimiter({
  windowMs: 24 * 60 * 60 * 1000, // 24小时
  max: 5, // 每IP 24小时内5次注册
  message: '注册次数超出限制，请24小时后再试',
  prefix: 'rl:register:'
});

/**
 * 密码重置速率限制 - 防止滥用
 */
const passwordResetLimiter = createRateLimiter({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 3, // 每IP 1小时内3次密码重置请求
  message: '密码重置请求次数过多，请1小时后再试',
  prefix: 'rl:pwd-reset:'
});

/**
 * 短信验证码速率限制 - 防止滥用
 */
const smsLimiter = createRateLimiter({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 5, // 每IP 1小时内5条短信
  message: '短信发送次数过多，请1小时后再试',
  prefix: 'rl:sms:',
  keyGenerator: (req) => {
    // 使用手机号+IP作为键
    const phone = req.body.phone || '';
    return `${phone}:${req.ip}`;
  }
});

/**
 * OAuth请求速率限制 - 防止滥用
 */
const oauthLimiter = createRateLimiter({
  windowMs: 10 * 60 * 1000, // 10分钟
  max: 10, // 每IP 10分钟内10次OAuth请求
  message: 'OAuth请求次数过多，请稍后再试',
  prefix: 'rl:oauth:'
});

module.exports = {
  globalLimiter,
  loginLimiter,
  registerLimiter,
  passwordResetLimiter,
  smsLimiter,
  oauthLimiter,
  createRateLimiter
};