/**
 * Redis配置模块
 */
const Redis = require('ioredis');
const { logger } = require('@suoke/shared').utils;
const config = require('./index');

// Redis客户端实例
let redisClient = null;

/**
 * 创建Redis连接
 * @returns {Promise<Redis>} Redis客户端实例
 */
const connectRedis = async () => {
  if (redisClient) {
    return redisClient;
  }
  
  try {
    // 从环境变量获取Redis配置
    const redisOptions = {
      host: process.env.REDIS_HOST || config.redis.host,
      port: parseInt(process.env.REDIS_PORT || config.redis.port, 10),
      maxRetriesPerRequest: 5,
      retryStrategy: (times) => {
        const delay = Math.min(times * 100, 3000);
        logger.info(`Redis连接重试 (${times}), 延迟 ${delay}ms`);
        return delay;
      },
      reconnectOnError: (err) => {
        logger.error(`Redis连接错误: ${err.message}`);
        return true; // 自动重连
      },
      enableOfflineQueue: true,
      connectTimeout: 10000,
      // 设置连接池
      maxClientCount: parseInt(process.env.REDIS_MAX_CLIENTS || 100, 10)
    };
    
    // 添加密码认证（如果提供）
    if (process.env.REDIS_PASSWORD) {
      redisOptions.password = process.env.REDIS_PASSWORD;
    }
    
    // 初始化Redis客户端
    redisClient = new Redis(redisOptions);
    
    // 设置事件监听器
    redisClient.on('connect', () => {
      logger.info('Redis客户端已连接');
    });
    
    redisClient.on('error', (err) => {
      logger.error(`Redis错误: ${err.message}`);
    });
    
    redisClient.on('reconnecting', (delay) => {
      logger.info(`Redis正在重新连接，延迟 ${delay}ms`);
    });
    
    // 执行一个PING命令以确认连接
    await redisClient.ping();
    logger.info('Redis连接检查: PING成功');
    
    return redisClient;
  } catch (error) {
    logger.error(`Redis连接失败: ${error.message}`);
    throw error;
  }
};

/**
 * 获取Redis客户端实例
 * @returns {Redis} Redis客户端
 */
const getRedisClient = () => {
  if (!redisClient) {
    logger.warn('尝试在连接建立前获取Redis客户端');
    // 初始化连接但不等待
    connectRedis().catch(err => {
      logger.error(`延迟Redis连接失败: ${err.message}`);
    });
  }
  return redisClient;
};

/**
 * 关闭Redis连接
 * @returns {Promise<void>}
 */
const closeRedis = async () => {
  if (redisClient) {
    try {
      await redisClient.quit();
      logger.info('Redis连接已关闭');
      redisClient = null;
    } catch (error) {
      logger.error(`关闭Redis连接失败: ${error.message}`);
      throw error;
    }
  }
};

/**
 * 健康检查函数
 * @returns {Promise<boolean>}
 */
const healthCheck = async () => {
  try {
    if (!redisClient) {
      return false;
    }
    const result = await redisClient.ping();
    return result === 'PONG';
  } catch (error) {
    logger.error(`Redis健康检查失败: ${error.message}`);
    return false;
  }
};

// 导出接口
module.exports = getRedisClient();

// 导出其他实用函数
module.exports.connectRedis = connectRedis;
module.exports.getRedisClient = getRedisClient;
module.exports.closeRedis = closeRedis;
module.exports.healthCheck = healthCheck; 