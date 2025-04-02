/**
 * Redis连接工具
 */
const Redis = require('ioredis');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port,
  password: config.redis.password,
  keyPrefix: 'user:',
  retryStrategy: (times) => {
    const delay = Math.min(100 + times * 200, 10000);
    return delay;
  },
  maxRetriesPerRequest: 3,
  connectTimeout: 10000,
  enableReadyCheck: true,
  lazyConnect: true
});

// 初始化函数 - 检查Redis连接
const initialize = async () => {
  try {
    await redis.connect();
    await redis.ping();
    logger.info('Redis连接成功');
    return true;
  } catch (error) {
    logger.error('Redis连接失败', { error: error.message });
    return false;
  }
};

// 关闭Redis连接
const shutdown = async () => {
  try {
    await redis.quit();
    logger.info('Redis连接已关闭');
    return true;
  } catch (error) {
    logger.error('关闭Redis连接失败', { error: error.message });
    return false;
  }
};

// 通用缓存函数
const getCache = async (key, fetchFunction, ttl = 3600) => {
  try {
    // 尝试从缓存获取
    const cachedData = await redis.get(key);
    
    // 如果缓存存在，返回解析后的数据
    if (cachedData) {
      return JSON.parse(cachedData);
    }
    
    // 如果缓存不存在，调用获取函数
    const data = await fetchFunction();
    
    // 将数据存入缓存
    await redis.set(key, JSON.stringify(data), 'EX', ttl);
    
    return data;
  } catch (error) {
    logger.error('缓存操作失败', { error: error.message, key });
    // 缓存失败时，直接调用获取函数
    return fetchFunction();
  }
};

// 删除缓存
const deleteCache = async (key) => {
  try {
    await redis.del(key);
    return true;
  } catch (error) {
    logger.error('删除缓存失败', { error: error.message, key });
    return false;
  }
};

// 按模式删除缓存
const deleteCacheByPattern = async (pattern) => {
  try {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(keys);
    }
    return true;
  } catch (error) {
    logger.error('按模式删除缓存失败', { error: error.message, pattern });
    return false;
  }
};

/**
 * 检查Redis连接状态
 * @returns {boolean} 连接是否有效
 */
const isConnected = () => {
  try {
    return !!redis && redis.status === 'ready';
  } catch (error) {
    logger.error('检查Redis连接状态时出错:', error);
    return false;
  }
};

module.exports = {
  redis,
  initialize,
  shutdown,
  getCache,
  deleteCache,
  deleteCacheByPattern,
  isConnected
}; 