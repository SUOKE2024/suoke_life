/**
 * 缓存服务
 */
const redis = require('../config/redis');
const { logger } = require('@suoke/shared').utils;

// 默认缓存时间（秒）
const DEFAULT_TTL = 3600; // 1小时

/**
 * 缓存服务
 */
class CacheService {
  /**
   * 设置缓存
   * 
   * @param {string} key - 缓存键
   * @param {any} value - 要缓存的值
   * @param {number} [ttl=DEFAULT_TTL] - 生存时间（秒）
   * @param {boolean} [useCompression=false] - 是否使用压缩
   * @returns {Promise<boolean>} 是否成功
   */
  async set(key, value, ttl = DEFAULT_TTL, useCompression = false) {
    try {
      const serializedValue = JSON.stringify(value);
      
      // 仅当数据大于1KB且启用压缩时使用压缩
      if (useCompression && Buffer.byteLength(serializedValue) > 1024) {
        // 使用ZLIB压缩
        const zlib = require('zlib');
        const compressedBuffer = zlib.deflateSync(Buffer.from(serializedValue));
        
        // 存储压缩数据，添加前缀标识
        await redis.set(`${key}:compressed`, compressedBuffer, 'EX', ttl);
        return true;
      }
      
      // 存储普通JSON数据
      await redis.set(key, serializedValue, 'EX', ttl);
      return true;
    } catch (error) {
      logger.error(`缓存设置失败: ${error.message}`, { key });
      return false;
    }
  }
  
  /**
   * 获取缓存
   * 
   * @param {string} key - 缓存键
   * @returns {Promise<any>} 缓存的值，如果不存在则返回null
   */
  async get(key) {
    try {
      // 首先尝试获取压缩数据
      const compressedData = await redis.get(`${key}:compressed`);
      
      if (compressedData) {
        // 解压缩数据
        const zlib = require('zlib');
        const decompressedBuffer = zlib.inflateSync(Buffer.from(compressedData));
        return JSON.parse(decompressedBuffer.toString());
      }
      
      // 获取普通数据
      const data = await redis.get(key);
      
      if (!data) {
        return null;
      }
      
      return JSON.parse(data);
    } catch (error) {
      logger.error(`缓存获取失败: ${error.message}`, { key });
      return null;
    }
  }
  
  /**
   * 删除缓存
   * 
   * @param {string} key - 缓存键
   * @returns {Promise<boolean>} 是否成功
   */
  async del(key) {
    try {
      await redis.del(key);
      await redis.del(`${key}:compressed`);
      return true;
    } catch (error) {
      logger.error(`缓存删除失败: ${error.message}`, { key });
      return false;
    }
  }
  
  /**
   * 设置带哈希的缓存
   * 
   * @param {string} hashName - 哈希名称
   * @param {string} field - 字段名
   * @param {any} value - 要缓存的值
   * @param {number} [ttl=DEFAULT_TTL] - 生存时间（秒）
   * @returns {Promise<boolean>} 是否成功
   */
  async hset(hashName, field, value, ttl = DEFAULT_TTL) {
    try {
      await redis.hset(hashName, field, JSON.stringify(value));
      
      // 设置哈希过期时间
      if (ttl > 0) {
        await redis.expire(hashName, ttl);
      }
      
      return true;
    } catch (error) {
      logger.error(`哈希缓存设置失败: ${error.message}`, { hashName, field });
      return false;
    }
  }
  
  /**
   * 获取哈希缓存
   * 
   * @param {string} hashName - 哈希名称
   * @param {string} field - 字段名
   * @returns {Promise<any>} 缓存的值，如果不存在则返回null
   */
  async hget(hashName, field) {
    try {
      const data = await redis.hget(hashName, field);
      
      if (!data) {
        return null;
      }
      
      return JSON.parse(data);
    } catch (error) {
      logger.error(`哈希缓存获取失败: ${error.message}`, { hashName, field });
      return null;
    }
  }
  
  /**
   * 删除哈希缓存字段
   * 
   * @param {string} hashName - 哈希名称
   * @param {string} field - 字段名
   * @returns {Promise<boolean>} 是否成功
   */
  async hdel(hashName, field) {
    try {
      await redis.hdel(hashName, field);
      return true;
    } catch (error) {
      logger.error(`哈希缓存字段删除失败: ${error.message}`, { hashName, field });
      return false;
    }
  }
  
  /**
   * 清除键前缀下的所有缓存
   * 
   * @param {string} prefix - 缓存键前缀
   * @returns {Promise<boolean>} 是否成功
   */
  async clearByPrefix(prefix) {
    try {
      // 查找匹配前缀的所有键
      const keys = await redis.keys(`${prefix}*`);
      
      if (keys.length > 0) {
        // 批量删除
        await redis.del(keys);
        logger.info(`已清除前缀[${prefix}]下的${keys.length}个缓存项`);
      }
      
      return true;
    } catch (error) {
      logger.error(`前缀缓存清除失败: ${error.message}`, { prefix });
      return false;
    }
  }
  
  /**
   * 执行缓存清理（定期执行）
   */
  async runCacheMaintenance() {
    // 这里可以实现缓存统计、过期缓存预处理等机制
    logger.info('执行缓存维护操作');
    
    try {
      // 缓存使用统计
      const info = await redis.info('memory');
      logger.info(`Redis内存使用情况: ${info}`);
      
      return true;
    } catch (error) {
      logger.error(`缓存维护失败: ${error.message}`);
      return false;
    }
  }
}

// 创建单例
const cacheService = new CacheService();

module.exports = cacheService;