/**
 * 缓存服务模块
 * 提供内存缓存和Redis缓存功能
 */
const NodeCache = require('node-cache');
const Redis = require('ioredis');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;

// 缓存配置
const CACHE_CONFIG = config.cache || {};
const CACHE_TTL = CACHE_CONFIG.ttl || 3600; // 默认缓存1小时
const ENABLE_REDIS = CACHE_CONFIG.enableRedis !== false && config.redis && config.redis.host;

// 内存缓存实例
const memoryCache = new NodeCache({
  stdTTL: CACHE_TTL,
  checkperiod: 120, // 每2分钟检查过期项
  useClones: false, // 不使用克隆以提高性能
  maxKeys: 5000 // 最多缓存5000个键
});

// Redis客户端实例
let redisClient = null;

// 如果启用Redis，初始化客户端
if (ENABLE_REDIS) {
  try {
    redisClient = new Redis({
      host: config.redis.host,
      port: config.redis.port || 6379,
      password: config.redis.password,
      db: config.redis.db || 0,
      keyPrefix: config.redis.keyPrefix || 'suoke:cache:',
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      }
    });
    
    redisClient.on('error', (err) => {
      logger.error('Redis连接错误', { error: err.message });
    });
    
    redisClient.on('ready', () => {
      logger.info('Redis已连接并准备就绪');
    });
  } catch (err) {
    logger.error('Redis初始化失败，将只使用内存缓存', { error: err.message });
  }
}

/**
 * 设置缓存项
 * @param {string} key - 缓存键
 * @param {*} value - 缓存值
 * @param {number} ttl - 生存时间（秒），不提供则使用默认值
 * @returns {boolean} - 是否设置成功
 */
const set = (key, value, ttl = CACHE_TTL) => {
  try {
    // 设置内存缓存
    memoryCache.set(key, value, ttl);
    
    // 如果启用Redis，也设置Redis缓存
    if (redisClient && redisClient.status === 'ready') {
      const valueStr = typeof value === 'string' ? value : JSON.stringify(value);
      redisClient.set(key, valueStr, 'EX', ttl).catch(err => {
        logger.warn(`Redis缓存设置失败: ${key}`, { error: err.message });
      });
    }
    
    return true;
  } catch (err) {
    logger.error(`缓存设置失败: ${key}`, { error: err.message });
    return false;
  }
};

/**
 * 获取缓存项
 * @param {string} key - 缓存键
 * @returns {*} - 缓存值，未找到则返回undefined
 */
const get = async (key) => {
  try {
    // 尝试从内存缓存获取
    let value = memoryCache.get(key);
    
    // 如果内存中没有但Redis可用，尝试从Redis获取
    if (value === undefined && redisClient && redisClient.status === 'ready') {
      try {
        const valueStr = await redisClient.get(key);
        
        if (valueStr) {
          try {
            // 尝试解析JSON
            value = JSON.parse(valueStr);
          } catch {
            // 如果解析失败，使用字符串值
            value = valueStr;
          }
          
          // 更新内存缓存
          const ttl = await redisClient.ttl(key);
          if (ttl > 0) {
            memoryCache.set(key, value, ttl);
          }
        }
      } catch (redisErr) {
        logger.warn(`从Redis读取缓存失败: ${key}`, { error: redisErr.message });
      }
    }
    
    return value;
  } catch (err) {
    logger.error(`读取缓存失败: ${key}`, { error: err.message });
    return undefined;
  }
};

/**
 * 同步获取缓存项（仅内存缓存）
 * @param {string} key - 缓存键
 * @returns {*} - 缓存值，未找到则返回undefined
 */
get.sync = (key) => {
  try {
    return memoryCache.get(key);
  } catch (err) {
    logger.error(`同步读取缓存失败: ${key}`, { error: err.message });
    return undefined;
  }
};

/**
 * 删除缓存项
 * @param {string} key - 缓存键
 * @returns {boolean} - 是否删除成功
 */
const del = (key) => {
  try {
    // 删除内存缓存
    memoryCache.del(key);
    
    // 如果Redis可用，也删除Redis缓存
    if (redisClient && redisClient.status === 'ready') {
      redisClient.del(key).catch(err => {
        logger.warn(`从Redis删除缓存失败: ${key}`, { error: err.message });
      });
    }
    
    return true;
  } catch (err) {
    logger.error(`删除缓存失败: ${key}`, { error: err.message });
    return false;
  }
};

/**
 * 清除所有缓存
 * @returns {boolean} - 是否清除成功
 */
const clear = () => {
  try {
    // 清除内存缓存
    memoryCache.flushAll();
    
    // 如果Redis可用，清除所有与前缀匹配的键
    if (redisClient && redisClient.status === 'ready') {
      const keyPrefix = config.redis.keyPrefix || 'suoke:cache:';
      redisClient.eval(
        `local keys = redis.call('keys', ARGV[1]) 
         for i=1,#keys,5000 do 
           redis.call('del', unpack(keys, i, math.min(i+4999, #keys))) 
         end 
         return #keys`,
        0,
        `${keyPrefix}*`
      ).catch(err => {
        logger.warn('清除Redis缓存失败', { error: err.message });
      });
    }
    
    logger.info('所有缓存已清除');
    return true;
  } catch (err) {
    logger.error('清除所有缓存失败', { error: err.message });
    return false;
  }
};

/**
 * 根据模式批量删除缓存
 * @param {string} pattern - 匹配模式
 * @returns {number} - 删除的键数量
 */
const delByPattern = async (pattern) => {
  try {
    // 匹配内存缓存中的键
    const memKeys = memoryCache.keys().filter(key => {
      const regexPattern = new RegExp(pattern.replace(/\*/g, '.*'));
      return regexPattern.test(key);
    });
    
    // 删除匹配的内存缓存
    memoryCache.del(memKeys);
    
    // 如果Redis可用，也删除匹配的Redis缓存
    let redisDeletedCount = 0;
    if (redisClient && redisClient.status === 'ready') {
      try {
        const keyPrefix = config.redis.keyPrefix || 'suoke:cache:';
        redisDeletedCount = await redisClient.eval(
          `local keys = redis.call('keys', ARGV[1]) 
           local deleted = 0
           for i=1,#keys,5000 do 
             deleted = deleted + redis.call('del', unpack(keys, i, math.min(i+4999, #keys))) 
           end 
           return deleted`,
          0,
          `${keyPrefix}${pattern}`
        );
      } catch (redisErr) {
        logger.warn(`根据模式删除Redis缓存失败: ${pattern}`, { error: redisErr.message });
      }
    }
    
    const totalDeleted = memKeys.length + redisDeletedCount;
    logger.info(`已删除 ${totalDeleted} 个匹配模式 ${pattern} 的缓存项`);
    return totalDeleted;
  } catch (err) {
    logger.error(`根据模式删除缓存失败: ${pattern}`, { error: err.message });
    return 0;
  }
};

/**
 * 获取缓存统计信息
 * @returns {Object} - 缓存统计信息
 */
const getStats = async () => {
  try {
    // 获取内存缓存统计
    const memStats = memoryCache.getStats();
    
    // 如果Redis可用，获取Redis统计
    let redisInfo = {};
    if (redisClient && redisClient.status === 'ready') {
      try {
        const info = await redisClient.info();
        const lines = info.split('\r\n');
        
        for (const line of lines) {
          if (line && !line.startsWith('#')) {
            const parts = line.split(':');
            if (parts.length === 2) {
              redisInfo[parts[0]] = parts[1];
            }
          }
        }
      } catch (redisErr) {
        logger.warn('获取Redis信息失败', { error: redisErr.message });
      }
    }
    
    return {
      memory: {
        keys: memoryCache.keys().length,
        hits: memStats.hits,
        misses: memStats.misses,
        hitRate: memStats.hits / (memStats.hits + memStats.misses || 1),
        ksize: memStats.ksize,
        vsize: memStats.vsize
      },
      redis: {
        connected: !!(redisClient && redisClient.status === 'ready'),
        usedMemory: redisInfo.used_memory_human,
        clients: redisInfo.connected_clients,
        uptime: redisInfo.uptime_in_seconds
      }
    };
  } catch (err) {
    logger.error('获取缓存统计失败', { error: err.message });
    return {
      error: err.message,
      memory: { keys: 0 },
      redis: { connected: false }
    };
  }
};

/**
 * 关闭缓存服务
 * 在应用关闭时调用
 */
const close = async () => {
  if (redisClient) {
    try {
      await redisClient.quit();
      logger.info('Redis连接已关闭');
    } catch (err) {
      logger.error('关闭Redis连接失败', { error: err.message });
    }
  }
};

// 导出缓存服务
const cacheService = {
  set,
  get,
  del,
  clear,
  delByPattern,
  getStats,
  close
};

module.exports = { cacheService }; 