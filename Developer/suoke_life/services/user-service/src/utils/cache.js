/**
 * 缓存工具
 * 提供内存缓存和Redis缓存功能
 */
const Redis = require('ioredis');
const NodeCache = require('node-cache');
const config = require('../config');
const logger = require('./logger');

// 内存缓存，用于单实例场景或Redis不可用时的回退
const memoryCache = new NodeCache({
  stdTTL: 300, // 默认缓存时间5分钟
  checkperiod: 60, // 每分钟检查过期项
  useClones: false // 不使用深拷贝以提高性能
});

// Redis客户端实例
let redisClient = null;

/**
 * 缓存服务
 */
const cacheService = {
  /**
   * 初始化缓存
   */
  async init() {
    try {
      if (config.redis.enabled) {
        redisClient = new Redis({
          host: config.redis.host,
          port: config.redis.port,
          password: config.redis.password,
          db: config.redis.db,
          retryStrategy: (times) => {
            const delay = Math.min(times * 50, 2000);
            return delay;
          }
        });
        
        redisClient.on('error', (err) => {
          logger.error('Redis连接错误', err);
        });
        
        redisClient.on('connect', () => {
          logger.info('Redis连接成功');
        });
        
        // 测试连接
        await redisClient.ping();
        logger.info('Redis连接测试成功');
      } else {
        logger.info('Redis未启用，使用内存缓存');
      }
    } catch (err) {
      logger.error('初始化缓存服务失败', err);
      logger.info('回退到内存缓存');
      redisClient = null;
    }
  },
  
  /**
   * 获取缓存项
   * @param {string} key - 缓存键
   * @returns {Promise<any>} 缓存内容，不存在返回null
   */
  async get(key) {
    try {
      // 首先尝试从Redis获取
      if (redisClient) {
        const value = await redisClient.get(key);
        if (value) {
          return JSON.parse(value);
        }
        return null;
      }
      
      // 回退到内存缓存
      return memoryCache.get(key) || null;
    } catch (err) {
      logger.error(`获取缓存[${key}]失败`, err);
      // 回退到内存缓存
      return memoryCache.get(key) || null;
    }
  },
  
  /**
   * 设置缓存项
   * @param {string} key - 缓存键
   * @param {any} value - 缓存值
   * @param {number} ttl - 缓存时间(秒)，0表示永不过期
   * @returns {Promise<boolean>} 操作结果
   */
  async set(key, value, ttl = 300) {
    try {
      // 存入Redis
      if (redisClient) {
        if (ttl > 0) {
          await redisClient.set(key, JSON.stringify(value), 'EX', ttl);
        } else {
          await redisClient.set(key, JSON.stringify(value));
        }
      }
      
      // 同时存入内存缓存(保持一致性)
      memoryCache.set(key, value, ttl);
      return true;
    } catch (err) {
      logger.error(`设置缓存[${key}]失败`, err);
      // 至少尝试存入内存缓存
      memoryCache.set(key, value, ttl);
      return false;
    }
  },
  
  /**
   * 删除缓存项
   * @param {string} key - 缓存键
   * @returns {Promise<boolean>} 操作结果
   */
  async del(key) {
    try {
      // 从Redis删除
      if (redisClient) {
        await redisClient.del(key);
      }
      
      // 从内存缓存删除
      memoryCache.del(key);
      return true;
    } catch (err) {
      logger.error(`删除缓存[${key}]失败`, err);
      // 至少尝试从内存缓存删除
      memoryCache.del(key);
      return false;
    }
  },
  
  /**
   * 清除所有缓存
   * @returns {Promise<boolean>} 操作结果
   */
  async clear() {
    try {
      // 清除Redis
      if (redisClient) {
        await redisClient.flushdb();
      }
      
      // 清除内存缓存
      memoryCache.flushAll();
      return true;
    } catch (err) {
      logger.error('清除缓存失败', err);
      // 至少尝试清除内存缓存
      memoryCache.flushAll();
      return false;
    }
  },
  
  /**
   * 关闭缓存连接
   * @returns {Promise<void>}
   */
  async close() {
    if (redisClient) {
      await redisClient.quit();
      redisClient = null;
    }
    memoryCache.flushAll();
  },
  
  /**
   * 获取缓存健康状态
   * @returns {Promise<Object>} 缓存状态
   */
  async getStatus() {
    const status = {
      memoryCache: {
        enabled: true,
        stats: memoryCache.getStats()
      },
      redisCache: {
        enabled: Boolean(redisClient),
        connected: false
      }
    };
    
    if (redisClient) {
      try {
        await redisClient.ping();
        status.redisCache.connected = true;
      } catch (err) {
        status.redisCache.connected = false;
        status.redisCache.error = err.message;
      }
    }
    
    return status;
  }
};

module.exports = cacheService;