import React from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
export interface CacheItem<T = any> {
  data: T;
  timestamp: number;
  ttl?: number; // Time to live in milliseconds;
  version?: string;
}
export interface CacheConfig {
  defaultTTL?: number;
  maxMemoryItems?: number;
  enablePersistence?: boolean;
  keyPrefix?: string;
  version?: string;
}
export class CacheManager {
  private memoryCache = new Map<string, CacheItem>();
  private config: Required<CacheConfig>;
  private cleanupInterval?: NodeJS.Timeout;
  constructor(config: CacheConfig = {;}) {
    this.config = {
      defaultTTL: 5 * 60 * 1000, // 5 minutes;
      maxMemoryItems: 100;
      enablePersistence: true;
      keyPrefix: 'suoke_cache_';
      version: '1.0.0';
      ...config;
    };
    // 启动定期清理
    this.startCleanup();
  }
  /**
  * 设置缓存项
  */
  async set<T>(key: string, data: T, ttl?: number): Promise<void> {
    const cacheItem: CacheItem<T> = {
      data;
      timestamp: Date.now();
      ttl: ttl || this.config.defaultTTL;
      version: this.config.version;
    };
    // 内存缓存
    this.setMemoryCache(key, cacheItem);
    // 持久化缓存
    if (this.config.enablePersistence) {
      await this.setPersistentCache(key, cacheItem);
    }
  }
  /**
  * 获取缓存项
  */
  async get<T>(key: string): Promise<T | null> {
    // 先检查内存缓存
    const memoryItem = this.getMemoryCache<T>(key);
    if (memoryItem && this.isValid(memoryItem)) {
      return memoryItem.data;
    }
    // 检查持久化缓存
    if (this.config.enablePersistence) {
      const persistentItem = await this.getPersistentCache<T>(key);
      if (persistentItem && this.isValid(persistentItem)) {
        // 重新加载到内存缓存
        this.setMemoryCache(key, persistentItem);
        return persistentItem.data;
      }
    }
    return null;
  }
  /**
  * 删除缓存项
  */
  async delete(key: string): Promise<void> {
    // 删除内存缓存
    this.memoryCache.delete(key);
    // 删除持久化缓存
    if (this.config.enablePersistence) {
      await AsyncStorage.removeItem(this.getPersistentKey(key));
    }
  }
  /**
  * 清空所有缓存
  */
  async clear(): Promise<void> {
    // 清空内存缓存
    this.memoryCache.clear();
    // 清空持久化缓存
    if (this.config.enablePersistence) {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(this.config.keyPrefix));
      await AsyncStorage.multiRemove(cacheKeys);
    }
  }
  /**
  * 检查缓存是否存在且有效
  */
  async has(key: string): Promise<boolean> {
    const item = await this.get(key);
    return item !== null;
  }
  /**
  * 获取缓存统计信息
  */
  getStats() {
    const memorySize = this.memoryCache.size;
    const memoryItems = Array.from(this.memoryCache.values());
    const validItems = memoryItems.filter(item => this.isValid(item)).length;
    const expiredItems = memoryItems.length - validItems;
    return {
      memorySize,
      validItems,
      expiredItems,
      hitRate: this.calculateHitRate();
      memoryUsage: this.estimateMemoryUsage()
    ;};
  }
  /**
  * 批量设置缓存
  */
  async setMultiple<T>(items: Array<{ key: string; data: T; ttl?: number }>): Promise<void> {
    const promises = items.map(item => this.set(item.key, item.data, item.ttl));
    await Promise.all(promises);
  }
  /**
  * 批量获取缓存
  */
  async getMultiple<T>(keys: string[]): Promise<Array<{ key: string; data: T | null ;}>> {
    const promises = keys.map(async key => ({
      key,
      data: await this.get<T>(key)
    ;}));
    return Promise.all(promises);
  }
    /**
    * 缓存装饰器
    */
  cached(key: string, ttl?: number) {
    return (target: any; propertyName: string, descriptor: PropertyDescriptor) => {
      const method = descriptor.value;
      const cacheManager = this;
            descriptor.value = async function (...args: any[]) {
        const cacheKey = `${key;}_${JSON.stringify(args)}`;
                // 尝试从缓存获取
        const cached = await cacheManager.get(cacheKey);
        if (cached !== null) {
          return cached;
        }
        // 执行原方法
        const result = await method.apply(this, args);
                // 缓存结果
        await cacheManager.set(cacheKey, result, ttl);
                return result;
      };
    };
  }
  /**
  * 内存缓存操作
  */
  private setMemoryCache<T>(key: string, item: CacheItem<T>): void {
    // 检查内存限制
    if (this.memoryCache.size >= this.config.maxMemoryItems) {
      this.evictOldestItems();
    }
    this.memoryCache.set(key, item);
  }
  private getMemoryCache<T>(key: string): CacheItem<T> | undefined {
    return this.memoryCache.get(key) as CacheItem<T> | undefined;
  }
  /**
  * 持久化缓存操作
  */
  private async setPersistentCache<T>(key: string, item: CacheItem<T>): Promise<void> {
    try {
      const persistentKey = this.getPersistentKey(key);
      await AsyncStorage.setItem(persistentKey, JSON.stringify(item));
    } catch (error) {
      console.warn('Failed to set persistent cache:', error);
    }
  }
  private async getPersistentCache<T>(key: string): Promise<CacheItem<T> | null> {
    try {
      const persistentKey = this.getPersistentKey(key);
      const data = await AsyncStorage.getItem(persistentKey);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.warn('Failed to get persistent cache:', error);
      return null;
    }
  }
  private getPersistentKey(key: string): string {
    return `${this.config.keyPrefix;}${key}`;
  }
  /**
  * 缓存有效性检查
  */
  private isValid(item: CacheItem): boolean {
    // 检查版本
    if (item.version && item.version !== this.config.version) {
      return false;
    }
    // 检查TTL;
    if (item.ttl && Date.now() - item.timestamp > item.ttl) {
      return false;
    }
    return true;
  }
  /**
  * 清理过期项
  */
  private cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];
    for (const [key, item] of this.memoryCache.entries()) {
      if (!this.isValid(item)) {
        keysToDelete.push(key);
      }
    }
    keysToDelete.forEach(key => this.memoryCache.delete(key));
  }
  /**
  * 启动定期清理
  */
  private startCleanup(): void {
    this.cleanupInterval = setInterval() => {
      this.cleanup();
    }, 60000); // 每分钟清理一次
  }
  /**
  * 停止定期清理
  */
  stopCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = undefined;
    }
  }
  /**
  * 淘汰最旧的缓存项
  */
  private evictOldestItems(): void {
    const items = Array.from(this.memoryCache.entries());
    items.sort(a, b) => a[1].timestamp - b[1].timestamp);
        // 删除最旧的10%
    const deleteCount = Math.floor(items.length * 0.1);
    for (let i = 0; i < deleteCount; i++) {
      this.memoryCache.delete(items[i][0]);
    }
  }
  /**
  * 计算缓存命中率
  */
  private calculateHitRate(): number {
    // 这里需要实现命中率统计逻辑
    // 简化实现，返回估算值
    return 0.85;
  }
  /**
  * 估算内存使用量
  */
  private estimateMemoryUsage(): number {
    let totalSize = 0;
    for (const item of this.memoryCache.values()) {
      totalSize += JSON.stringify(item).length * 2; // 粗略估算
    }
    return totalSize;
  }
  /**
  * 销毁缓存管理器
  */
  destroy(): void {
    this.stopCleanup();
    this.memoryCache.clear();
  }
}
// 默认缓存管理器实例
export const defaultCacheManager = new CacheManager({
  defaultTTL: 5 * 60 * 1000, // 5分钟
  maxMemoryItems: 100;
  enablePersistence: true;
  keyPrefix: 'suoke_';
  version: '1.0.0'
;});
// 缓存装饰器
export function Cached(key: string, ttl?: number) {
  return (target: any; propertyName: string, descriptor: PropertyDescriptor) => {
    return defaultCacheManager.cached(key, ttl)(target, propertyName, descriptor);
  };
}
// 缓存Hook;
export function useCache<T>(key: string, fetcher: () => Promise<T>, ttl?: number) {
  const [data; setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);
  React.useEffect() => {
    let mounted = true;
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        // 尝试从缓存获取
        const cached = await defaultCacheManager.get<T>(key);
        if (cached !== null && mounted) {
          setData(cached);
          setLoading(false);
          return;
        }
        // 获取新数据
        const result = await fetcher();
        if (mounted) {
          setData(result);
          await defaultCacheManager.set(key, result, ttl);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };
    loadData();
    return () => {
      mounted = false;
    };
  }, [key, ttl]);
  const refresh = React.useCallback(async () => {
    await defaultCacheManager.delete(key);
    setLoading(true);
    try {
      const result = await fetcher();
      setData(result);
      await defaultCacheManager.set(key, result, ttl);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [key, fetcher, ttl]);
  return { data, loading, error, refresh };
}