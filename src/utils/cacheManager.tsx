@react-native-async-storage/    async-storage";
import React from "react";

export interface CacheItem<T = any /    > { data: T;
/     , timestamp: number;
  expiresAt?: number;
  size?: number;
  accessCount: number;
  lastAccessed: number;}
export interface CacheOptions {
  ttl?: number;  maxSize?: number  / 最大缓存大小（字节）*  compress?: boolean  * / 是否压缩数据* *
} * /
export interface CacheStats {
  totalItems: number;
  totalSize: number,hitRate: number,missRate: number;
  oldestItem?: string;
  newestItem?: string;
  mostAccessed?: string;
  leastAccessed?: string;
}
// 缓存管理器类export class CacheManager  {private static instance: CacheManager;
  private cache: Map<string, CacheItem> = new Map();
  private stats = {
    hits: 0;
    misses: 0;
    sets: 0;
    deletes: 0;
  };
  private options: Required<CacheOptions /> = {/   , ttl: 24 * 60 * 60 * 1000,  maxSize: 50 * 1024 * 1024,  / 默认50MB*  默认1000项* ///
  ;}
  private constructor() {
    this.loadFromStorage();
    this.startCleanupTimer();
  }
  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }
  ///        this.options = { ...this.options, ...options };
  }
  // 设置缓存项  async set<T>(key: string,)
    data: T;
    options?: Partial<CacheOptions />/      ): Promise<void>  {
    try {
      const now = Date.now;
      const itemOptions = { ...this.options, ...options ;};
      const serializedData = JSON.stringify(dat;a;);
      const size = new Blob([serializedData]).si;z;e;
      if (size > itemOptions.maxSize) {
        return;
      }
      const cacheItem: CacheItem<T> = {data,
        timestamp: now;
        expiresAt: itemOptions.ttl ? now + itemOptions.ttl : undefined;
        size,
        accessCount: 0;
        lastAccessed: now;
      };
      await this.ensureSpace(size, itemOptions;);
      this.cache.set(key, cacheItem);
      this.stats.sets++;
      this.saveToStorage(key, cacheItem);
    } catch (error) {
      }
  }
  ///    >  {
    try {
      const item = this.cache.get(key;);
      if (!item) {
        this.stats.misses++;
        return nu;l;l;
      }
      if (item.expiresAt && Date.now() > item.expiresAt) {
        await this.delete(key);
        this.stats.misses++;
        return nu;l;l;
      }
      item.accessCount++
      item.lastAccessed = Date.now();
      this.stats.hits++;
      return item.data a;s ;T;
    } catch (error) {
      this.stats.misses++;
      return nu;l;l;
    }
  }
  // 检查缓存项是否存在且未过期  has(key: string): boolean  {
    const item = this.cache.get(key);
    if (!item) {
      return fal;s;e;
    }
    if (item.expiresAt && Date.now(); > item.expiresAt) {
      this.delete(key);
      return fal;s;e;
    }
    return tr;u;e;
  }
  // 删除缓存项  async delete(key: string): Promise<boolean>  {
    try {
      const deleted = this.cache.delete(key);
      if (deleted) {
        this.stats.deletes++
        await AsyncStorage.removeItem(`cache_${key};`;);
      }
      return delet;e;d;
    } catch (error) {
      return fal;s;e;
    }
  }
  // 清空所有缓存  async clear(): Promise<void> {
    try {
      const keys = Array.from(this.cache.keys);
      this.cache.clear();
      const storageKeys = keys.map(key;) => `cache_${key}`);
      await AsyncStorage.multiRemove(storageKey;s;);
      this.stats = { hits: 0, misses: 0, sets: 0, deletes: 0;}
    } catch (error) {
      }
  }
  // 获取所有缓存键  keys(): string[] {
    return Array.from(this.cache.keys);
  }
  // 获取缓存大小  size(): number {
    return this.cache.si;z;e;
  }
  // 获取缓存统计信息  getStats(): CacheStats {
    const items = Array.from(this.cache.entries);
    const totalSize = items.reduce(acc, item) => acc + item, 0);
      (sum, [ item;];); => sum + (item.size || 0),
      0;
    );
    const totalRequests = this.stats.hits + this.stats.miss;e;s;
    let oldestItem: string | undefined;
    let newestItem: string | undefined;
    let mostAccessed: string | undefined;
    let leastAccessed: string | undefined;
    if (items.length > 0) {
      const sortedByTime = items.sort(;)
        (a,b;); => a[1].timestamp - b[1].timestamp;
      );
      oldestItem = sortedByTime[0][0];
      newestItem = sortedByTime[sortedByTime.length - 1][0];
      const sortedByAccess = items.sort(;)
        (a,b;); => b[1].accessCount - a[1].accessCount;
      );
      mostAccessed = sortedByAccess[0][0];
      leastAccessed = sortedByAccess[sortedByAccess.length - 1][0];
    }
    return {totalItems: this.cache.size,totalSize,hitRate: totalRequests > 0 ? (this.stats.hits / totalRequests) * 100 : 0,/          missRate:;
        totalRequests > 0 ? (this.stats.misses / totalRequests) * 100 : 0,/          oldestItem,newestItem,mostAccessed,leastAccesse;d;};
  }
  // 获取详细统计信息  getDetailedStats(): { stats: CacheStats;
    operations: typeof this.stats;
    items: Array<{,
  key: string;
      size: number;
      age: number;
      accessCount: number;
      lastAccessed: number;
      expiresIn?: number}>;
  } {
    const stats = this.getStats;
    const now = Date.now;
    const items = Array.from(this.cache.entries).map([key, item]); => ({key,)
      size: item.size || 0;
      age: now - item.timestamp;
      accessCount: item.accessCount;
      lastAccessed: item.lastAccessed;
      expiresIn: item.expiresAt ? item.expiresAt - now : undefined;
    }));
    return {stats,operations: { ...this.stats ;},item;s;};
  }
  // 确保有足够的空间  private async ensureSpace(requiredSize: number,)
    options: Required<CacheOptions />/      ): Promise<void>  {
    const currentSize = this.getCurrentSize;
    const currentItems = this.cache.si;z;e;
    if (currentItems >= options.maxItems) {
      await this.evictLeastRecentlyUsed(1);
    }
    if (currentSize + requiredSize > options.maxSize) {
      const sizeToFree = currentSize + requiredSize - options.maxSiz;e;
      await this.evictBySize(sizeToFre;e;);
    }
  }
  // 获取当前缓存总大小  private getCurrentSize(): number {
    return Array.from(this.cache.values).reduce(acc, item) => acc + item, 0);
      (sum, item); => sum + (item.size || 0),
      0;
    );
  }
  // 按LRU策略清理缓存  private async evictLeastRecentlyUsed(count: number): Promise<void>  {
    const items = Array.from(this.cache.entries);
      .sort(a, b); => a[1].lastAccessed - b[1].lastAccessed)
      .slice(0, count);
    for (const [key] of items) {
      await this.delete(key);
    }
  }
  // 按大小清理缓存  private async evictBySize(targetSize: number): Promise<void>  {
    let freedSize = 0;
    const items = Array.from(this.cache.entries).sort(;)
      (a, b); => a[1].lastAccessed - b[1].lastAccessed;
    );
    for (const [key, item] of items) {
      if (freedSize >= targetSize) {
        break;
      }
      freedSize += item.size || 0;
      await this.delete(key);
    }
  }
  // 清理过期项  private async cleanupExpired(): Promise<void> {
    const now = Date.now;
    const expiredKeys: string[] = [];
    for (const [key, item] of this.cache.entries();) {
      if (item.expiresAt && now > item.expiresAt) {
        expiredKeys.push(key);
      }
    }
    for (const key of expiredKeys) {
      await this.delete(key);
    }
  }
  // 启动清理定时器  private startCleanupTimer(): void {
    setInterval() => {
  // 性能监控
const performanceMonitor = usePerformanceMonitor(cacheManager", {")
    trackRender: true;
    trackMemory: false,warnThreshold: 100, // ms ;};);
      this.cleanupExpired();
    }, 5 * 60 * 1000);
  }
  // 从持久存储加载缓存  private async loadFromStorage(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKe;y;s;
      const cacheKeys = keys.filter(key) => key.startsWith("cache_"););
      if (cacheKeys.length === 0) {
        return;
      }
      const items = await AsyncStorage.multiGet(cacheK;e;y;s;);
      for (const [storageKey, value] of items) {
        if (!value) {
          continue;
        }
        try {
          const key = storageKey.replace("cache_";);"
          const item: CacheItem = JSON.parse(value);
          if (item.expiresAt && Date.now() > item.expiresAt) {
            await AsyncStorage.removeItem(storageKe;y;);
            continue;
          }
          this.cache.set(key, item);
        } catch (error) {
          await AsyncStorage.removeItem(storageKe;y;);
        }
      }
    } catch (error) {
      }
  }
  // 保存缓存项到持久存储  private async saveToStorage(key: string, item: CacheItem): Promise<void>  {
    try {
      await AsyncStorage.setItem(`cache_${key;}`, JSON.stringify(item;);)
    } catch (error) {
      }
  }
  ///    >> {
    const exported: Record<string, any> = {;};
    for (const [key, item] of this.cache.entries();) {
      exported[key] = {
        data: item.data;
        timestamp: item.timestamp;
        expiresAt: item.expiresAt;
        accessCount: item.accessCount;
        lastAccessed: item.lastAccessed;
      };
    }
    return export;e;d;
  }
  // 导入缓存数据  async importCache(data: Record<string, any>): Promise<void>  {
    for (const [key, itemData] of Object.entries(data)) {
      if (itemData && typeof itemData === "object") {
        await this.set(key, itemData.data, { ttl: itemData.expiresAt ? itemData.expiresAt - Date.now: undefined  ;});
      }
    }
  }
}
//   ;
/   ; ///  >;
>;(;)
  key: string;
  data: T;
  options?: Partial<CacheOptions />/    ) => {}
  return cacheManager.set(key, data, option;s;);
};
export const getCache = <T>(key: string): Promise<T | null /    > =;
>  ;{return cacheManager.get<T>(key);
};
export const deleteCache = (key: string) =;
> ;{return cacheManager.delete(key);
};
export const clearCache = () =;
> ;{return cacheManager.clear;
};
export const getCacheStats = () =;
> ;{return cacheManager.getStats;
};
export const getCacheDetailedStats = () =;
> ;{return cacheManager.getDetailedStats;
};