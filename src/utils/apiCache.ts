/**
 * API缓存管理器
 * 提供智能缓存机制，提升API响应速度并减少网络请求
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

export interface CacheConfig {
  ttl: number; // 生存时间（毫秒）
  maxSize: number; // 最大缓存条目数
  compress: boolean; // 是否压缩数据
}

export interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  hash: string;
  compressed: boolean;
}

export interface CacheStats {
  totalEntries: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  oldestEntry: string;
  newestEntry: string;
}

class ApiCache {
  private cache: Map<string, CacheEntry> = new Map();
  private hitCount = 0;
  private missCount = 0;
  private readonly STORAGE_KEY = '@suoke_life_api_cache';
  
  private defaultConfig: CacheConfig = {
    ttl: 5 * 60 * 1000, // 5分钟
    maxSize: 100, // 最多100个条目
    compress: true,
  };

  // 不同API类型的缓存配置
  private cacheConfigs: { [key: string]: Partial<CacheConfig> } = {
    // 健康记录 - 长期缓存
    'health-records': { ttl: 60 * 60 * 1000 }, // 1小时
    'health-profile': { ttl: 30 * 60 * 1000 }, // 30分钟
    
    // 知识文章 - 中期缓存
    'knowledge-articles': { ttl: 15 * 60 * 1000 }, // 15分钟
    'learning-paths': { ttl: 15 * 60 * 1000 },
    
    // 实时数据 - 短期缓存
    'sensor-data': { ttl: 2 * 60 * 1000 }, // 2分钟
    'chat-responses': { ttl: 1 * 60 * 1000 }, // 1分钟
    
    // 静态数据 - 长期缓存
    'food-database': { ttl: 24 * 60 * 60 * 1000 }, // 24小时
    'recipes': { ttl: 12 * 60 * 60 * 1000 }, // 12小时
  };

  constructor() {
    this.loadFromStorage();
  }

  /**
   * 从本地存储加载缓存
   */
  private async loadFromStorage(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        this.cache = new Map(data.entries);
        this.hitCount = data.hitCount || 0;
        this.missCount = data.missCount || 0;
        
        // 清理过期条目
        this.cleanup();
      }
    } catch (error) {
      console.warn('加载API缓存失败:', error);
    }
  }

  /**
   * 保存缓存到本地存储
   */
  private async saveToStorage(): Promise<void> {
    try {
      const data = {
        entries: Array.from(this.cache.entries()),
        hitCount: this.hitCount,
        missCount: this.missCount,
        timestamp: Date.now(),
      };
      await AsyncStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.warn('保存API缓存失败:', error);
    }
  }

  /**
   * 生成缓存键
   */
  private generateKey(url: string, params?: any): string {
    const paramStr = params ? JSON.stringify(params) : '';
    return `${url}:${this.hashString(paramStr)}`;
  }

  /**
   * 简单哈希函数
   */
  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为32位整数
    }
    return hash.toString(36);
  }

  /**
   * 获取缓存配置
   */
  private getConfig(cacheType?: string): CacheConfig {
    const typeConfig = cacheType ? this.cacheConfigs[cacheType] : {};
    return { ...this.defaultConfig, ...typeConfig };
  }

  /**
   * 压缩数据
   */
  private compressData(data: any): string {
    // 简单的JSON字符串化（实际项目中可以使用更高效的压缩算法）
    return JSON.stringify(data);
  }

  /**
   * 解压数据
   */
  private decompressData(compressed: string): any {
    return JSON.parse(compressed);
  }

  /**
   * 设置缓存
   */
  async set<T>(
    url: string, 
    data: T, 
    params?: any, 
    cacheType?: string
  ): Promise<void> {
    const key = this.generateKey(url, params);
    const config = this.getConfig(cacheType);
    
    let processedData: any = data;
    let compressed = false;
    
    if (config.compress) {
      try {
        processedData = this.compressData(data);
        compressed = true;
      } catch (error) {
        console.warn('数据压缩失败，使用原始数据:', error);
        processedData = data;
      }
    }

    const entry: CacheEntry<T> = {
      data: processedData,
      timestamp: Date.now(),
      ttl: config.ttl,
      hash: this.hashString(JSON.stringify(data)),
      compressed,
    };

    this.cache.set(key, entry);

    // 检查缓存大小限制
    if (this.cache.size > config.maxSize) {
      this.evictOldest();
    }

    await this.saveToStorage();
  }

  /**
   * 获取缓存
   */
  async get<T>(url: string, params?: any): Promise<T | null> {
    const key = this.generateKey(url, params);
    const entry = this.cache.get(key);

    if (!entry) {
      this.missCount++;
      return null;
    }

    // 检查是否过期
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      this.missCount++;
      await this.saveToStorage();
      return null;
    }

    this.hitCount++;
    
    let data = entry.data;
    if (entry.compressed) {
      try {
        data = this.decompressData(entry.data);
      } catch (error) {
        console.warn('数据解压失败:', error);
        this.cache.delete(key);
        return null;
      }
    }

    return data as T;
  }

  /**
   * 删除缓存条目
   */
  async delete(url: string, params?: any): Promise<void> {
    const key = this.generateKey(url, params);
    this.cache.delete(key);
    await this.saveToStorage();
  }

  /**
   * 清空所有缓存
   */
  async clear(): Promise<void> {
    this.cache.clear();
    this.hitCount = 0;
    this.missCount = 0;
    await this.saveToStorage();
  }

  /**
   * 清理过期条目
   */
  async cleanup(): Promise<number> {
    const now = Date.now();
    let removedCount = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
        removedCount++;
      }
    }

    if (removedCount > 0) {
      await this.saveToStorage();
    }

    return removedCount;
  }

  /**
   * 驱逐最旧的条目
   */
  private evictOldest(): void {
    let oldestKey = '';
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTime) {
        oldestTime = entry.timestamp;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  /**
   * 获取缓存统计信息
   */
  getStats(): CacheStats {
    const entries = Array.from(this.cache.values());
    const totalRequests = this.hitCount + this.missCount;
    
    let oldestEntry = '';
    let newestEntry = '';
    let oldestTime = Date.now();
    let newestTime = 0;
    let totalSize = 0;

    for (const [key, entry] of this.cache.entries()) {
      const dataSize = JSON.stringify(entry.data).length;
      totalSize += dataSize;

      if (entry.timestamp < oldestTime) {
        oldestTime = entry.timestamp;
        oldestEntry = key;
      }

      if (entry.timestamp > newestTime) {
        newestTime = entry.timestamp;
        newestEntry = key;
      }
    }

    return {
      totalEntries: this.cache.size,
      totalSize,
      hitRate: totalRequests > 0 ? Math.round((this.hitCount / totalRequests) * 100) : 0,
      missRate: totalRequests > 0 ? Math.round((this.missCount / totalRequests) * 100) : 0,
      oldestEntry,
      newestEntry,
    };
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(url: string, params?: any): boolean {
    const key = this.generateKey(url, params);
    const entry = this.cache.get(key);
    
    if (!entry) return false;
    
    return Date.now() - entry.timestamp <= entry.ttl;
  }

  /**
   * 预加载缓存（用于关键API）
   */
  async preload(requests: Array<{ url: string; params?: any; cacheType?: string }>): Promise<void> {
    console.log('🚀 开始预加载API缓存...');
    
    const promises = requests.map(async ({ url, params, cacheType }) => {
      try {
        // 这里需要根据实际API调用方法来实现
        // 示例：const response = await apiCall(url, params);
        // await this.set(url, response, params, cacheType);
        console.log(`预加载缓存: ${url}`);
      } catch (error) {
        console.warn(`预加载失败 ${url}:`, error);
      }
    });

    await Promise.allSettled(promises);
    console.log('✅ API缓存预加载完成');
  }

  /**
   * 设置缓存策略
   */
  setCacheConfig(cacheType: string, config: Partial<CacheConfig>): void {
    this.cacheConfigs[cacheType] = {
      ...this.cacheConfigs[cacheType],
      ...config,
    };
  }
}

// 导出单例实例
export const apiCache = new ApiCache();

/**
 * 带缓存的API请求装饰器
 */
export function withCache<T extends any[], R>(
  cacheType?: string,
  keyGenerator?: (...args: T) => string
) {
  return function(
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
  ) {
    const method = descriptor.value;

    descriptor.value = async function(...args: T): Promise<R> {
      const cacheKey = keyGenerator ? keyGenerator(...args) : `${propertyName}:${JSON.stringify(args)}`;
      
      // 尝试从缓存获取
      const cached = await apiCache.get<R>(cacheKey);
      if (cached !== null) {
        console.log(`🎯 缓存命中: ${cacheKey}`);
        return cached;
      }

      // 执行原方法
      const result = await method.apply(this, args);
      
      // 保存到缓存
      await apiCache.set(cacheKey, result, undefined, cacheType);
      console.log(`💾 缓存保存: ${cacheKey}`);
      
      return result;
    };
  };
}

/**
 * API缓存工具函数
 */
export const cacheUtils = {
  /**
   * 获取缓存键
   */
  getCacheKey: (service: string, method: string, params?: any) => {
    return `${service}:${method}:${JSON.stringify(params || {})}`;
  },

  /**
   * 批量删除缓存
   */
  deleteBatch: async (pattern: string) => {
    // 实现批量删除逻辑
    console.log(`批量删除缓存模式: ${pattern}`);
  },

  /**
   * 缓存预热
   */
  warmup: async () => {
    await apiCache.preload([
      { url: 'knowledge/articles', cacheType: 'knowledge-articles' },
      { url: 'food/database', cacheType: 'food-database' },
      { url: 'recipes/popular', cacheType: 'recipes' },
    ]);
  },
};