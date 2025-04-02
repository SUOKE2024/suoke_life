/**
 * 响应缓存工具
 * 
 * 提供基于内存的响应缓存功能，支持TTL和容量限制
 */
const logger = require('./logger');

/**
 * 响应缓存类
 */
class ResponseCache {
  /**
   * 创建响应缓存实例
   * @param {Object} options 配置选项
   * @param {number} options.maxSize 最大缓存项数 (默认: 1000)
   * @param {number} options.defaultTTL 默认缓存TTL，单位秒 (默认: 60)
   * @param {number} options.cleanupInterval 清理间隔，单位秒 (默认: 300)
   */
  constructor(options = {}) {
    this.maxSize = options.maxSize || 1000;
    this.defaultTTL = (options.defaultTTL || 60) * 1000; // 转换为毫秒
    this.cleanupInterval = (options.cleanupInterval || 300) * 1000; // 转换为毫秒
    
    // 缓存存储
    this.cacheMap = new Map();
    
    // 统计信息
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      expired: 0,
      evicted: 0
    };
    
    // 启动定期清理
    this.cleanupTimer = setInterval(() => this.cleanup(), this.cleanupInterval);
    
    logger.info(`响应缓存已初始化, 最大容量: ${this.maxSize}项, TTL: ${this.defaultTTL/1000}秒, 清理间隔: ${this.cleanupInterval/1000}秒`);
  }
  
  /**
   * 生成缓存键
   * @param {string|Object} key 缓存键或对象
   * @returns {string} 缓存键
   */
  generateKey(key) {
    if (typeof key === 'string') {
      return key;
    }
    
    // 处理对象键
    if (typeof key === 'object') {
      try {
        return JSON.stringify(key);
      } catch (err) {
        logger.error(`缓存键序列化失败: ${err.message}`);
        return String(key);
      }
    }
    
    return String(key);
  }
  
  /**
   * 设置缓存
   * @param {string|Object} key 缓存键
   * @param {*} value 缓存值
   * @param {number} ttl 缓存TTL (可选)
   */
  set(key, value, ttl) {
    const cacheKey = this.generateKey(key);
    const expiresAt = Date.now() + (ttl ? ttl * 1000 : this.defaultTTL);
    
    // 创建缓存项
    const cacheItem = {
      data: value,
      expiresAt
    };
    
    // 检查容量限制
    if (!this.cacheMap.has(cacheKey) && this.cacheMap.size >= this.maxSize) {
      this.evictOldest();
    }
    
    // 存储缓存项
    this.cacheMap.set(cacheKey, cacheItem);
    this.stats.sets++;
    
    return true;
  }
  
  /**
   * 获取缓存
   * @param {string|Object} key 缓存键
   * @returns {*} 缓存值或undefined
   */
  get(key) {
    const cacheKey = this.generateKey(key);
    const cacheItem = this.cacheMap.get(cacheKey);
    
    // 缓存未命中
    if (!cacheItem) {
      this.stats.misses++;
      return undefined;
    }
    
    // 检查缓存是否过期
    if (cacheItem.expiresAt < Date.now()) {
      this.cacheMap.delete(cacheKey);
      this.stats.expired++;
      this.stats.misses++;
      return undefined;
    }
    
    // 缓存命中
    this.stats.hits++;
    return cacheItem.data;
  }
  
  /**
   * 删除缓存
   * @param {string|Object} key 缓存键
   * @returns {boolean} 是否成功删除
   */
  delete(key) {
    const cacheKey = this.generateKey(key);
    return this.cacheMap.delete(cacheKey);
  }
  
  /**
   * 清空缓存
   */
  clear() {
    this.cacheMap.clear();
    this.resetStats();
    logger.info('响应缓存已清空');
  }
  
  /**
   * 清理过期项
   */
  cleanup() {
    const now = Date.now();
    let expiredCount = 0;
    
    for (const [key, item] of this.cacheMap.entries()) {
      if (item.expiresAt < now) {
        this.cacheMap.delete(key);
        expiredCount++;
      }
    }
    
    if (expiredCount > 0) {
      this.stats.expired += expiredCount;
      logger.debug(`缓存清理: 移除了 ${expiredCount} 个过期项`);
    }
  }
  
  /**
   * 驱逐最旧的缓存项
   */
  evictOldest() {
    // 找到过期时间最早的项
    let oldestKey = null;
    let oldestExpiry = Infinity;
    
    for (const [key, item] of this.cacheMap.entries()) {
      if (item.expiresAt < oldestExpiry) {
        oldestKey = key;
        oldestExpiry = item.expiresAt;
      }
    }
    
    if (oldestKey) {
      this.cacheMap.delete(oldestKey);
      this.stats.evicted++;
      logger.debug(`缓存容量控制: 驱逐了最旧的项 ${oldestKey}`);
    }
  }
  
  /**
   * 获取缓存统计
   * @returns {Object} 缓存统计信息
   */
  getStats() {
    return {
      ...this.stats,
      size: this.cacheMap.size,
      maxSize: this.maxSize,
      hitRate: this.stats.hits / (this.stats.hits + this.stats.misses || 1)
    };
  }
  
  /**
   * 重置统计信息
   */
  resetStats() {
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      expired: 0,
      evicted: 0
    };
  }
  
  /**
   * 销毁缓存实例
   */
  destroy() {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
    this.cacheMap.clear();
    logger.info('响应缓存已销毁');
  }
}

// 导出单例实例
module.exports = new ResponseCache();

// 也导出类以支持创建多个实例
module.exports.ResponseCache = ResponseCache;