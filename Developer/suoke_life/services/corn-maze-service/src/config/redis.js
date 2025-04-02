/**
 * Redis配置和共享连接模块
 * 提供集中式Redis管理，避免多个服务创建独立连接
 */
const Redis = require('redis');
const logger = require('../utils/logger');

// Redis配置
const REDIS_CONFIG = {
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  retry_strategy: function(options) {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      logger.error('Redis连接被拒绝');
      return new Error('Redis服务器连接被拒绝');
    }
    if (options.total_retry_time > 1000 * 60 * 30) {
      logger.error('Redis重试时间过长，放弃连接');
      return new Error('Redis重试超时');
    }
    return Math.min(options.attempt * 100, 3000);
  }
};

// 创建单例Redis客户端实例
let redisClient = null;
let redisSubscriber = null;

/**
 * 获取Redis客户端实例（单例模式）
 * @returns {Object} Redis客户端
 */
const getRedisClient = () => {
  if (!redisClient) {
    redisClient = Redis.createClient(REDIS_CONFIG);
    
    // 连接事件处理
    redisClient.on('connect', () => {
      logger.info('Redis主客户端连接成功');
    });
    
    redisClient.on('error', (err) => {
      logger.error('Redis主客户端错误:', err);
    });
    
    redisClient.on('reconnecting', () => {
      logger.info('Redis主客户端重新连接中...');
    });
    
    redisClient.on('end', () => {
      logger.info('Redis主客户端连接已关闭');
    });
  }
  
  return redisClient;
};

/**
 * 获取Redis订阅客户端实例（单例模式）
 * @returns {Object} Redis订阅客户端
 */
const getRedisSubscriber = () => {
  if (!redisSubscriber) {
    if (!redisClient) {
      getRedisClient();
    }
    
    redisSubscriber = redisClient.duplicate();
    
    // 连接事件处理
    redisSubscriber.on('connect', () => {
      logger.info('Redis订阅客户端连接成功');
    });
    
    redisSubscriber.on('error', (err) => {
      logger.error('Redis订阅客户端错误:', err);
    });
    
    redisSubscriber.on('reconnecting', () => {
      logger.info('Redis订阅客户端重新连接中...');
    });
    
    redisSubscriber.on('end', () => {
      logger.info('Redis订阅客户端连接已关闭');
    });
  }
  
  return redisSubscriber;
};

/**
 * 订阅Redis频道
 * @param {String|Array} channels - 频道名称或名称数组
 * @param {Function} messageHandler - 消息处理函数 (channel, message) => {}
 * @returns {Object} 订阅实例
 */
const subscribeToChannels = (channels, messageHandler) => {
  const subscriber = getRedisSubscriber();
  
  // 处理单个频道或频道数组
  const channelList = Array.isArray(channels) ? channels : [channels];
  
  // 订阅所有频道
  channelList.forEach(channel => {
    subscriber.subscribe(channel);
    logger.info(`已订阅Redis频道: ${channel}`);
  });
  
  // 设置消息处理器
  if (messageHandler) {
    subscriber.on('message', messageHandler);
  }
  
  return subscriber;
};

/**
 * 发布消息到Redis频道
 * @param {String} channel - 频道名称
 * @param {Object|String} message - 消息内容
 * @returns {Promise<Number>} 接收到消息的客户端数量
 */
const publishToChannel = async (channel, message) => {
  const client = getRedisClient();
  let messageString = message;
  
  // 如果消息是对象，转换为JSON
  if (typeof message === 'object') {
    messageString = JSON.stringify(message);
  }
  
  try {
    return await client.publish(channel, messageString);
  } catch (error) {
    logger.error(`发布消息到频道${channel}失败:`, error);
    throw error;
  }
};

/**
 * 创建健康检查中间件
 * @returns {Function} Express中间件
 */
const redisHealthCheck = () => {
  return async (req, res, next) => {
    const client = getRedisClient();
    
    try {
      if (client.connected) {
        return next();
      }
      
      logger.error('Redis健康检查失败: 连接丢失');
      return res.status(500).json({
        error: 'Redis连接不可用',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      logger.error('Redis健康检查失败:', error);
      return res.status(500).json({
        error: 'Redis连接检查失败',
        message: error.message,
        timestamp: new Date().toISOString()
      });
    }
  };
};

/**
 * 关闭所有Redis连接
 * @returns {Promise<void>}
 */
const closeAllConnections = async () => {
  try {
    if (redisSubscriber) {
      await redisSubscriber.quit();
      redisSubscriber = null;
      logger.info('Redis订阅客户端已关闭');
    }
    
    if (redisClient) {
      await redisClient.quit();
      redisClient = null;
      logger.info('Redis主客户端已关闭');
    }
  } catch (error) {
    logger.error('关闭Redis连接失败:', error);
    throw error;
  }
};

// 为Promisify支持导出客户端
const getAsyncRedisClient = async () => {
  return getRedisClient();
};

// 确保程序退出时关闭连接
process.on('SIGTERM', async () => {
  logger.info('收到SIGTERM信号，关闭Redis连接');
  await closeAllConnections();
});

process.on('SIGINT', async () => {
  logger.info('收到SIGINT信号，关闭Redis连接');
  await closeAllConnections();
});

module.exports = {
  getRedisClient,
  getRedisSubscriber,
  getAsyncRedisClient,
  subscribeToChannels,
  publishToChannel,
  redisHealthCheck,
  closeAllConnections
}; 