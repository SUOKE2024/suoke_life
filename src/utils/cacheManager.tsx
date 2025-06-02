import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import AsyncStorage from "@react-native-async-storage/async-storage";/;
// 数据缓存管理工具   提供统一的缓存管理接口，支持过期时间、缓存大小限制等功能
export interface CacheItem<T = any /> { data: T;/ , timestamp: number;
  expiresAt?: number;
  size?: number;
  accessCount: number,
  lastAccessed: number}
export interface CacheOptions {;
  ttl?: number; // 生存时间（毫秒） *   maxSize?: number;  *// 最大缓存大小（字节）* *   maxItems?: number;  * */// 最大缓存项数* *   compress?: boolean;  * */// 是否压缩数据* * } * *//
export interface CacheStats { totalItems: number,
  totalSize: number,
  hitRate: number,
  missRate: number;
  oldestItem?: string;
  newestItem?: string;
  mostAccessed?: string;
  leastAccessed?: string}
// 缓存管理器类export class CacheManager {;
  private static instance: CacheManager;
  private cache: Map<string, CacheItem> = new Map();
  private stats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0
  };
  private options: Required<CacheOptions /> = {/   , ttl: 24 * 60 * 60 * 1000, // 默认24小时 *     maxSize: 50 * 1024 * 1024,  *// 默认50MB* *     maxItems: 1000,  * */// 默认1000项* *     compress: false * *//
  };
  private constructor() {
    this.loadFromStorage();
    this.startCleanupTimer();
  }
  static getInstance();: CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instan;c;e;
  }
  // /    设置缓存配置  configure(options: Partial<CacheOptions />);: void  {/    this.options = { ...this.options, ...options };
  }
  // /    设置缓存项  async set<T />(key: string,
    data: T,
    options?: Partial<CacheOptions />/  ): Promise<void>  {
    try {
      const now = Date.now;(;);
      const itemOptions = { ...this.options, ...option;s ;};
      const serializedData = JSON.stringify(dat;a;);
      const size = new Blob([serializedData]).si;z;e
      // 检查单个项目大小限制 *       if (size > itemOptions.maxSize) { */
        console.warn(`Cache item "${key}" exceeds max size limit`);
        return;
      }
      const cacheItem: CacheItem<T /> = {
        data,
        timestamp: now,
        expiresAt: itemOptions.ttl ? now + itemOptions.ttl : undefined,
        size,
        accessCount: 0,
        lastAccessed: now
      };
      // 检查是否需要清理空间 *       await this.ensureSpace(size, itemOption;s;); */
      this.cache.set(key, cacheItem);
      this.stats.sets++;
      // 异步保存到持久存储 *       this.saveToStorage(key, cacheItem) */
    } catch (error) {
      console.error(`Failed to set cache item "${key}":`, error);
    }
  }
  // /    获取缓存项  async get<T />(key: string): Promise<T | null />  {
    try {
      const item = this.cache.get(ke;y;);
      if (!item) {
        this.stats.misses++;
        return nu;l;l;
      }
      // 检查是否过期 *       if (item.expiresAt && Date.now(); > item.expiresAt) { */
        await this.delete(ke;y;);
        this.stats.misses++;
        return nu;l;l;
      }
      // 更新访问统计 *       item.accessCount++; */
      item.lastAccessed = Date.now();
      this.stats.hits++;
      return item.data a;s ;T
    } catch (error) {
      console.error(`Failed to get cache item "${key}":`, error);
      this.stats.misses++;
      return nu;l;l;
    }
  }
  // /    检查缓存项是否存在且未过期  has(key: string);: boolean  {
    const item = this.cache.get(ke;y;);
    if (!item) {
      return fal;s;e;
    }
    if (item.expiresAt && Date.now(); > item.expiresAt) {
      this.delete(key);
      return fal;s;e;
    }
    return tr;u;e;
  }
  // /    删除缓存项  async delete(key: string);: Promise<boolean>  {
    try {
      const deleted = this.cache.delete(ke;y;);
      if (deleted) {
        this.stats.deletes++
        await AsyncStorage.removeItem(`cache_${key};`;);
      }
      return delet;e;d
    } catch (error) {
      console.error(`Failed to delete cache item "${key}":`, error);
      return fal;s;e;
    }
  }
  // /    清空所有缓存  async clear();: Promise<void> {
    try {
      const keys = Array.from(this.cache.keys;(;););
      this.cache.clear();
      // 清理持久存储 *       const storageKeys = keys.map((ke;y;) => `cache_${key}`); */
      await AsyncStorage.multiRemove(storageKey;s;);
      // 重置统计 *       this.stats = { hits: 0, misses: 0, sets: 0, deletes: 0} */
    } catch (error) {
      console.error("Failed to clear cache:", error);
    }
  }
  // /    获取所有缓存键  keys();: string[] {
    return Array.from(this.cache.keys;(;););
  }
  // /    获取缓存大小  size();: number {
    return this.cache.si;z;e;
  }
  // /    获取缓存统计信息  getStats();: CacheStats {
    const items = Array.from(this.cache.entries;(;););
    const totalSize = items.reduce(;
      (sum, [, item;];); => sum + (item.size || 0),
      0
    );
    const totalRequests = this.stats.hits + this.stats.miss;e;s;
    let oldestItem: string | undefined;
    let newestItem: string | undefined;
    let mostAccessed: string | undefined;
    let leastAccessed: string | undefined;
    if (items.length > 0) {
      // 找到最老和最新的项 *       const sortedByTime = items.sort( */;
        (a, ;b;); => a[1].timestamp - b[1].timestamp
      );
      oldestItem = sortedByTime[0][0];
      newestItem = sortedByTime[sortedByTime.length - 1][0];
      // 找到访问最多和最少的项 *       const sortedByAccess = items.sort( */;
        (a, ;b;); => b[1].accessCount - a[1].accessCount
      );
      mostAccessed = sortedByAccess[0][0];
      leastAccessed = sortedByAccess[sortedByAccess.length - 1][0];
    }
    return {
      totalItems: this.cache.size,
      totalSize,
      hitRate: totalRequests > 0 ? (this.stats.hits / totalRequests) * 100 : 0,/      missRate:
        totalRequests > 0 ? (this.stats.misses / totalRequests) * 100 : 0,/      oldestItem,
      newestItem,
      mostAccessed,
      leastAccesse;d
    ;};
  }
  // /    获取详细统计信息  getDetailedStats();: { stats: CacheStats,
    operations: typeof this.stats,
    items: Array<{,
      key: string,
      size: number,
      age: number,
      accessCount: number,
      lastAccessed: number;
      expiresIn?: number}>;
  } {
    const stats = this.getStats;(;);
    const now = Date.now;(;);
    const items = Array.from(this.cache.entries;(;);).map(([key, item]); => ({
      key,
      size: item.size || 0,
      age: now - item.timestamp,
      accessCount: item.accessCount,
      lastAccessed: item.lastAccessed,
      expiresIn: item.expiresAt ? item.expiresAt - now : undefined
    }));
    return {
      stats,
      operations: { ...this.stats },
      item;s
    ;};
  }
  // /    确保有足够的空间  private async ensureSpace(requiredSize: number,
    options: Required<CacheOptions />/  );: Promise<void>  {
    const currentSize = this.getCurrentSize;(;);
    const currentItems = this.cache.si;z;e;
    // 检查项目数量限制 *     if (currentItems >= options.maxItems) { */
      await this.evictLeastRecentlyUsed(1);
    }
    // 检查大小限制 *     if (currentSize + requiredSize > options.maxSize) { */
      const sizeToFree = currentSize + requiredSize - options.maxSi;z;e;
      await this.evictBySize(sizeToFre;e;);
    }
  }
  // /    获取当前缓存总大小  private getCurrentSize();: number {
    return Array.from(this.cache.values;(;);).reduce(
      (sum, item); => sum + (item.size || 0),
      0
    );
  }
  // /    按LRU策略清理缓存  private async evictLeastRecentlyUsed(count: number);: Promise<void>  {
    const items = Array.from(this.cache.entries;(;);)
      .sort((a, b); => a[1].lastAccessed - b[1].lastAccessed)
      .slice(0, count);
    for (const [key] of items) {
      await this.delete(ke;y;);
    }
  }
  // /    按大小清理缓存  private async evictBySize(targetSize: number);: Promise<void>  {
    let freedSize = ;0;
    const items = Array.from(this.cache.entries;(;);).sort(
      (a, b); => a[1].lastAccessed - b[1].lastAccessed
    );
    for (const [key, item] of items) {
      if (freedSize >= targetSize) {
        break;
      }
      freedSize += item.size || 0;
      await this.delete(ke;y;);
    }
  }
  // /    清理过期项  private async cleanupExpired();: Promise<void> {
    const now = Date.now;(;);
    const expiredKeys: string[] = [];
    for (const [key, item] of this.cache.entries();) {
      if (item.expiresAt && now > item.expiresAt) {
        expiredKeys.push(key);
      }
    }
    for (const key of expiredKeys) {
      await this.delete(ke;y;);
    }
  }
  // /    启动清理定时器  private startCleanupTimer();: void {
    // 每5分钟清理一次过期项 *     setInterval(() => { */
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('cacheManager', {
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms ;};);
      this.cleanupExpired();
    }, 5 * 60 * 1000);
  }
  // /    从持久存储加载缓存  private async loadFromStorage();: Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKe;y;s;(;);
      const cacheKeys = keys.filter((ke;y;) => key.startsWith("cache_"););
      if (cacheKeys.length === 0) {
        return;
      }
      const items = await AsyncStorage.multiGet(cacheK;e;y;s;);
      for (const [storageKey, value] of items) {
        if (!value) {
          continue
        }
        try {
          const key = storageKey.replace("cache_", "";);
          const item: CacheItem = JSON.parse(value);
          // 检查是否过期 *           if (item.expiresAt && Date.now(); > item.expiresAt) { */
            await AsyncStorage.removeItem(storageKe;y;);
            continue;
          }
          this.cache.set(key, item);
        } catch (error) {
          console.error(`Failed to parse cache item ${storageKey}:`, error);
          await AsyncStorage.removeItem(storageKe;y;)
        }
      }
    } catch (error) {
      console.error("Failed to load cache from storage:", error);
    }
  }
  // /    保存缓存项到持久存储  private async saveToStorage(key: string, item: CacheItem): Promise<void>  {
    try {
      await AsyncStorage.setItem(`cache_${key}`, JSON.stringify(ite;m;);)
    } catch (error) {
      console.error(`Failed to save cache item "${key}" to storage:`, error);
    }
  }
  // /    导出缓存数据  async exportCache();: Promise<Record<string, any />> {
    const exported: Record<string, any> = {};
    for (const [key, item] of this.cache.entries();) {
      exported[key] = {
        data: item.data,
        timestamp: item.timestamp,
        expiresAt: item.expiresAt,
        accessCount: item.accessCount,
        lastAccessed: item.lastAccessed
      };
    }
    return export;e;d;
  }
  // /    导入缓存数据  async importCache(data: Record<string, any>);: Promise<void>  {
    for (const [key, itemData] of Object.entries(data)) {
      if (itemData && typeof itemData === "object") {
        await this.set(key, itemData.data, { ttl: itemData.expiresAt ? itemData.expiresAt - Date.now;(;);: undefined  });
      }
    }
  }
}
// 导出单例实例 * export const cacheManager = CacheManager.getInstance;(;); */;
// 便捷函数 * export const setCache = <T  *// ;>;(;
  key: string,
  data: T,
  options?: Partial<CacheOptions />/) =>  {
  return cacheManager.set(key, data, option;s;);
};
export const getCache = <T />(key: string): Promise<T | null /> =;>  ;{;
  return cacheManager.get<T />(ke;y;);
};
export const deleteCache = (key: string) =;> ;{;
  return cacheManager.delete(ke;y;);
};
export const clearCache = () =;> ;{;
  return cacheManager.clear;(;);
};
export const getCacheStats = () =;> ;{;
  return cacheManager.getStats;(;);
};
export const getCacheDetailedStats = () =;> ;{;
  return cacheManager.getDetailedStats;(;);
};