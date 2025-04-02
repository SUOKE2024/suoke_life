/**
 * 速率限制中间件
 */
const redisClient = require('../utils/redis');
const logger = require('../utils/logger');
const config = require('../config');

// 默认配置
const DEFAULT_WINDOW_MS = 60 * 1000; // 1分钟
const DEFAULT_MAX_REQUESTS = 60; // 每分钟60次请求
const DEFAULT_BLOCK_DURATION = 10 * 60; // 10分钟封禁

/**
 * 创建速率限制中间件
 * @param {Object} options - 配置选项
 * @param {number} [options.windowMs] - 时间窗口（毫秒）
 * @param {number} [options.maxRequests] - 时间窗口内最大请求数
 * @param {number} [options.blockDuration] - 封禁时长（秒）
 * @param {Function} [options.keyGenerator] - 自定义键生成函数
 * @param {Function} [options.handler] - 自定义超限处理函数
 * @param {Array<string>} [options.skipPaths] - 不受限制的路径
 * @returns {Function} Express中间件
 */
const createRateLimiter = (options = {}) => {
  const windowMs = options.windowMs || DEFAULT_WINDOW_MS;
  const maxRequests = options.maxRequests || DEFAULT_MAX_REQUESTS;
  const blockDuration = options.blockDuration || DEFAULT_BLOCK_DURATION;
  const skipPaths = options.skipPaths || [];
  
  // 默认键生成函数（基于IP）
  const defaultKeyGenerator = (req) => {
    return `rate-limit:${req.ip}`;
  };
  
  // 默认超限处理函数
  const defaultHandler = (req, res) => {
    return res.status(429).json({
      success: false,
      message: '请求过于频繁，请稍后再试',
      code: 'rate_limit_exceeded'
    });
  };
  
  const keyGenerator = options.keyGenerator || defaultKeyGenerator;
  const handler = options.handler || defaultHandler;
  
  // 返回中间件函数
  return async (req, res, next) => {
    try {
      // 检查是否跳过该路径
      const path = req.originalUrl || req.url;
      if (skipPaths.some(p => path.startsWith(p))) {
        return next();
      }
      
      const key = keyGenerator(req);
      
      // 检查是否被封禁
      const bannedKey = `${key}:banned`;
      const isBanned = await redisClient.get(bannedKey);
      
      if (isBanned) {
        const ttl = await redisClient.ttl(bannedKey);
        
        logger.warn('请求被限流（已封禁）', {
          key,
          path,
          ttl,
          ip: req.ip
        });
        
        return handler(req, res);
      }
      
      // 获取当前计数
      const current = await redisClient.incr(key);
      
      // 如果是第一次请求，设置过期时间
      if (current === 1) {
        await redisClient.expire(key, Math.floor(windowMs / 1000));
      }
      
      // 检查是否超过限制
      if (current > maxRequests) {
        // 封禁
        await redisClient.set(bannedKey, 1);
        await redisClient.expire(bannedKey, blockDuration);
        
        logger.warn('请求被限流（新封禁）', {
          key,
          path,
          current,
          limit: maxRequests,
          ip: req.ip
        });
        
        return handler(req, res);
      }
      
      // 设置RateLimit相关头
      res.setHeader('X-RateLimit-Limit', maxRequests);
      res.setHeader('X-RateLimit-Remaining', Math.max(0, maxRequests - current));
      res.setHeader('X-RateLimit-Reset', Math.ceil(Date.now() / 1000) + await redisClient.ttl(key));
      
      next();
    } catch (error) {
      logger.error('速率限制错误', {
        error: error.message,
        ip: req.ip,
        path: req.originalUrl
      });
      
      // 出错时放行请求，避免因限流功能故障而阻止正常请求
      next();
    }
  };
};

/**
 * 默认速率限制中间件
 * 通用API限流：每IP每分钟60次请求
 */
const rateLimiter = createRateLimiter({
  skipPaths: ['/health', '/metrics']
});

/**
 * 严格速率限制中间件
 * 敏感API限流：每IP每分钟10次请求
 */
const strictRateLimiter = createRateLimiter({
  maxRequests: 10,
  blockDuration: 30 * 60 // 30分钟封禁
});

/**
 * 宽松速率限制中间件
 * 公共API限流：每IP每分钟120次请求
 */
const looseRateLimiter = createRateLimiter({
  maxRequests: 120
});

/**
 * 登录尝试限制中间件
 * 登录限流：每IP每5分钟10次尝试
 */
const loginRateLimiter = createRateLimiter({
  windowMs: 5 * 60 * 1000, // 5分钟
  maxRequests: 10,
  blockDuration: 30 * 60, // 30分钟封禁
  keyGenerator: (req) => `login-attempts:${req.ip}`
});

module.exports = {
  rateLimiter,
  strictRateLimiter,
  looseRateLimiter,
  loginRateLimiter,
  createRateLimiter
}; 