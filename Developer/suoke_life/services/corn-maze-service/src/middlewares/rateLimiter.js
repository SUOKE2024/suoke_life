/**
 * 请求速率限制中间件
 * 提供API请求速率控制，防止滥用和DDoS攻击
 */
const Redis = require('redis');
const { createError } = require('./errorHandler');
const logger = require('../utils/logger');

// Redis客户端配置 - 如果realTimeService已初始化Redis，可考虑共享连接
const redisClient = Redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  retry_strategy: function(options) {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      logger.error('速率限制Redis连接被拒绝');
      return new Error('Redis服务器连接被拒绝');
    }
    if (options.total_retry_time > 1000 * 60 * 30) {
      logger.error('Redis重试时间过长，放弃连接');
      return new Error('Redis重试超时');
    }
    return Math.min(options.attempt * 100, 3000);
  }
});

// 健壮性处理：使用内存回退机制，防止Redis不可用
const memoryFallbackStore = new Map();
let redisAvailable = false;

redisClient.on('connect', () => {
  logger.info('速率限制Redis客户端连接成功');
  redisAvailable = true;
});

redisClient.on('error', (err) => {
  logger.error('速率限制Redis客户端错误:', err);
  redisAvailable = false;
});

/**
 * 创建基于IP的速率限制中间件
 * @param {Object} options - 配置选项
 * @param {number} options.windowMs - 时间窗口（毫秒）
 * @param {number} options.max - 最大请求数
 * @param {string} options.keyPrefix - 键前缀
 * @param {Function} options.keyGenerator - 自定义键生成函数，默认使用IP
 * @param {string} options.message - 达到限制时的消息
 * @param {number} options.statusCode - 达到限制时的状态码
 * @param {boolean} options.skipFailedRequests - 是否跳过失败的请求
 * @param {boolean} options.skipSuccessfulRequests - 是否跳过成功的请求
 * @returns {Function} Express中间件
 */
const rateLimit = (options = {}) => {
  const {
    windowMs = 60 * 1000, // 默认1分钟
    max = 100, // 默认每分钟100次
    keyPrefix = 'rl:',
    keyGenerator = (req) => req.ip || req.connection.remoteAddress,
    message = '请求过于频繁，请稍后再试',
    statusCode = 429,
    skipFailedRequests = false,
    skipSuccessfulRequests = false
  } = options;

  // 根据Redis可用性选择存储方式
  const getCount = async (key) => {
    try {
      if (redisAvailable) {
        const value = await redisClient.get(key);
        return value ? parseInt(value, 10) : 0;
      } else {
        return memoryFallbackStore.get(key) || 0;
      }
    } catch (error) {
      logger.error('获取速率限制计数失败:', error);
      return 0;
    }
  };

  const incrementCount = async (key) => {
    try {
      if (redisAvailable) {
        await redisClient.incr(key);
        await redisClient.pexpire(key, windowMs);
      } else {
        const current = memoryFallbackStore.get(key) || 0;
        memoryFallbackStore.set(key, current + 1);
        
        // 设置内存过期逻辑
        setTimeout(() => {
          const value = memoryFallbackStore.get(key);
          if (value === current + 1) {
            memoryFallbackStore.delete(key);
          }
        }, windowMs);
      }
    } catch (error) {
      logger.error('递增速率限制计数失败:', error);
    }
  };

  // 返回中间件函数
  return async (req, res, next) => {
    try {
      const key = `${keyPrefix}${keyGenerator(req)}`;
      const current = await getCount(key);

      if (max && current >= max) {
        // 超出限制，返回错误
        logger.warn(`请求速率限制超出: IP=${req.ip}, 路径=${req.path}`);
        const err = createError(message, statusCode);
        err.rateLimit = {
          current,
          limit: max,
          remaining: 0,
          resetTime: new Date(Date.now() + windowMs)
        };
        return next(err);
      }

      // 添加速率限制信息到响应头
      res.set('X-RateLimit-Limit', max);
      res.set('X-RateLimit-Remaining', Math.max(0, max - current - 1));
      res.set('X-RateLimit-Reset', Math.ceil(Date.now() / 1000) + Math.ceil(windowMs / 1000));

      // 在请求完成时递增计数
      const afterResponse = () => {
        res.removeListener('finish', afterResponse);
        res.removeListener('close', afterResponse);
        res.removeListener('error', afterResponse);

        // 根据配置决定是否记录请求
        if (
          (skipFailedRequests && res.statusCode >= 400) ||
          (skipSuccessfulRequests && res.statusCode < 400)
        ) {
          return;
        }

        incrementCount(key);
      };

      res.on('finish', afterResponse);
      res.on('close', afterResponse);
      res.on('error', afterResponse);

      return next();
    } catch (error) {
      logger.error('速率限制中间件错误:', error);
      return next();
    }
  };
};

/**
 * 常用预定义速率限制器
 */

// 通用API速率限制
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 300, // 每15分钟300次
  keyPrefix: 'rl:api:',
  message: 'API请求过于频繁，请15分钟后再试'
});

// 登录速率限制，防止暴力破解
const loginLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 5, // 每IP每小时5次
  keyPrefix: 'rl:login:',
  message: '登录尝试过多，请1小时后再试'
});

// 上传限制，防止过多上传
const uploadLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 50, // 每IP每小时50次
  keyPrefix: 'rl:upload:',
  message: '上传操作过于频繁，请稍后再试'
});

// AR互动限制，防止过度请求
const arInteractionLimiter = rateLimit({
  windowMs: 10 * 60 * 1000, // 10分钟
  max: 100, // 每IP每10分钟100次
  keyPrefix: 'rl:ar:',
  message: 'AR互动请求过于频繁，请稍后再试'
});

// NPC互动限制，防止对话滥用
const npcInteractionLimiter = rateLimit({
  windowMs: 5 * 60 * 1000, // 5分钟
  max: 30, // 每IP每5分钟30次
  keyPrefix: 'rl:npc:',
  message: 'NPC互动过于频繁，请稍后再试'
});

module.exports = {
  rateLimit,
  apiLimiter,
  loginLimiter,
  uploadLimiter,
  arInteractionLimiter,
  npcInteractionLimiter
}; 