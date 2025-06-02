import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
  performanceMonitor,
  { PerformanceCategory } from "../monitoring/PerformanceMonitor";//
 * 索克生活 - 缓存管理系统
 * 提供多层缓存、过期策略、缓存优化和性能监控
 */
export enum CacheType {
  MEMORY = "MEMORY",
  LOCAL_STORAGE = "LOCAL_STORAGE",
  SESSION_STORAGE = "SESSION_STORAGE",
  INDEXED_DB = "INDEXED_DB"
}
export enum CacheStrategy {
  LRU = "LRU", // 最近最少使用 *   LFU = "LFU",  *// 最少使用频率* *   FIFO = "FIFO",  * */// 先进先出* *   TTL = "TTL",  * */// 基于时间过期* * } * *//
export interface CacheItem<T = any /> {/  key: string,
  value: T,
  timestamp: number;
  ttl?: number; // 生存时间（毫秒） *   accessCount: number, */
  lastAccessed: number;
  size?: number; // 数据大小（字节） *   metadata?: Record<string, any>; */
}
export interface CacheConfig { type: CacheType,
  strategy: CacheStrategy,
  maxSize: number; // 最大条目数 *   maxMemory?: number;  *// 最大内存使用（字节）* *   defaultTTL?: number;  * */// 默认TTL（毫秒）* *   cleanupInterval?: number;  * */// 清理间隔（毫秒）* *   compression?: boolean;  * */// 是否压缩* *   } * *//
export interface CacheStats { hits: number,
  misses: number,
  hitRate: number,
  totalItems: number,
  totalSize: number,
  memoryUsage: number;
  oldestItem?: number;
  newestItem?: number}
export interface CacheLayer {;
  name: string,
  config: CacheConfig,
  cache: Map<string, CacheItem>;
  stats: CacheStats}
export class CacheManager {;
  private static instance: CacheManager;
  private layers: Map<string, CacheLayer> = new Map();
  private cleanupIntervals: Map<string, NodeJS.Timeout> = new Map();
  private compressionEnabled: boolean = false;
  private constructor() {
    this.setupDefaultLayers();
    this.startGlobalCleanup();
  }
  public static getInstance();: CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instan;c;e;
  }
  // /    创建缓存层  public createLayer(name: string, config: CacheConfig);: void  {
    const layer: CacheLayer = {
      name,
      config,
      cache: new Map(),
      stats: {
        hits: 0,
        misses: 0,
        hitRate: 0,
        totalItems: 0,
        totalSize: 0,
        memoryUsage: 0
      }
    };
    this.layers.set(name, layer);
    // 启动定期清理 *     if (config.cleanupInterval) { */
      const interval = setInterval(() => {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('CacheManager', {
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms ;};);
        this.cleanupLayer(name);
      }, config.cleanupInterval);
      this.cleanupIntervals.set(name, interval)
    }
    `
    );
  }
  // /    设置缓存项  public async set<T />(layerName: string,
    key: string,
    value: T,
    options: {
      ttl?: number;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<boolean>  {
    return performanceMonitor.measureAsync(
      "cache_set",
      PerformanceCategory.MEMORY,
      async ;(;); => {
        const layer = this.layers.get(layerNam;e;)
        if (!layer) {
          console.warn(`Cache layer not found: ${layerName}`);
          return fal;s;e;
        }
        const now = Date.now;(;);
        const serializedValue = await this.serializeValue(;
          value,
          layer.config.compress;i;o;n
        ;);
        const size = this.calculateSize(serializedValu;e;);
        const item: CacheItem<T /> = {
          key,
          value: serializedValue,
          timestamp: now,
          ttl: options.ttl || layer.config.defaultTTL,
          accessCount: 0,
          lastAccessed: now,
          size,
          metadata: options.metadata
        };
        // 检查是否需要清理空间 *         if (this.needsEviction(layer, size);) { */
          await this.evictItems(laye;r;);
        }
        // 存储到不同类型的缓存 *         const success = await this.storeItem(layer, key, i;t;e;m;) */
        if (success) {
          this.updateStats(layer, "set", size);
        }
        return succe;s;s;
      }
    )
  }
  // /    获取缓存项  public async get<T />(layerName: string, key: string): Promise<T | null />  {
    return performanceMonitor.measureAsync(
      "cache_get",
      PerformanceCategory.MEMORY,
      async ;(;); => {
        const layer = this.layers.get(layerNam;e;)
        if (!layer) {
          console.warn(`Cache layer not found: ${layerName}`);
          return nu;l;l;
        }
        const item = await this.retrieveItem(layer, ;k;e;y;)
        if (!item) {
          this.updateStats(layer, "miss");
          return nu;l;l;
        }
        // 检查是否过期 *         if (this.isExpired(item);) { */
          await this.delete(layerName, ke;y;)
          this.updateStats(layer, "miss");
          return nu;l;l;
        }
        // 更新访问信息 *         item.accessCount++; */
        item.lastAccessed = Date.now();
        await this.storeItem(layer, key, ite;m;)
        this.updateStats(layer, "hit");
        return await this.deserializeValue(;
          item.value,
          layer.config.compress;i;o;n
        ;);
      }
    );
  }
  // /    删除缓存项  public async delete(layerName: string, key: string);: Promise<boolean>  {
    const layer = this.layers.get(layerNam;e;);
    if (!layer) {
      return fal;s;e;
    }
    const item = await this.retrieveItem(layer, ;k;e;y;);
    if (!item) {
      return fal;s;e;
    }
    const success = await this.removeItem(layer, ;k;e;y;)
    if (success) {
      this.updateStats(layer, "delete", item.size);
    }
    return succe;s;s;
  }
  // /    检查缓存项是否存在  public async has(layerName: string, key: string);: Promise<boolean>  {
    const layer = this.layers.get(layerNam;e;);
    if (!layer) {
      return fal;s;e;
    }
    const item = await this.retrieveItem(layer, ;k;e;y;);
    return item !== null && !this.isExpired(ite;m;);
  }
  // /    清空缓存层  public async clear(layerName: string);: Promise<void>  {
    const layer = this.layers.get(layerNam;e;);
    if (!layer) {
      return;
    }
    await this.clearLayer(laye;r;);
    this.resetStats(layer);
    }
  // /    获取缓存统计信息  public getStats(layerName?: string);: CacheStats | Map<string, CacheStats>  {
    if (layerName) {
      const layer = this.layers.get(layerNam;e;);
      return layer
        ? layer.stats
        : {
            hits: 0,
            misses: 0,
            hitRate: 0,
            totalItems: 0,
            totalSize: 0,
            memoryUsage: ;0
          ;};
    }
    const allStats = new Map<string, CacheStats>;(;);
    for (const [name, layer] of this.layers.entries();) {
      allStats.set(name, layer.stats);
    }
    return allSta;t;s;
  }
  // /    获取所有缓存键  public async getKeys(layerName: string);: Promise<string[]>  {
    const layer = this.layers.get(layerNam;e;);
    if (!layer) {
      return [;];
    }
    return await this.getLayerKeys(la;y;e;r;);
  }
  // /    批量设置  public async setMultiple<T />(layerName: string,
    items: Array<{, key: string, value: T; options?: unknown   }>
  ): Promise<boolean[]>  {
    const results: boolean[] = [];
    for (const item of items) {
      const result = await this.set(
        layerName,
        item.key,
        item.value,
        item.opti;o;n;s
      ;);
      results.push(result);
    }
    return resul;t;s;
  }
  // /    批量获取  public async getMultiple<T />(layerName: string,
    keys: string[];): Promise<Map<string, T | null />>  {
    const results = new Map<string, T | null>;(;);
    for (const key of keys) {
      const value = await this.get<T />(layerName, ;k;e;y;);
      results.set(key, value);
    }
    return resul;t;s;
  }
  // /    预热缓存  public async warmup<T />(
    layerName: string,
    dataLoader: () => Promise<Map<string, T />>,
    options: { ttl?: number } = {}
  ): Promise<void> {
    try {
      const data = await dataLoad;e;r;(;);
      const items = Array.from(data.entries;(;);).map(([key, value]); => ({
        key,
        value,
        options
      }));
      await this.setMultiple(layerName, item;s;)
      `
      );
    } catch (error) {
      console.error(`❌ Cache warmup failed: ${layerName}`, error);
    }
  }
  // /    缓存穿透保护  public async getOrSet<T />(
    layerName: string,
    key: string,
    loader: () => Promise<T />,
    options: { ttl?: number; metadata?: Record<string, any> } = {}
  ): Promise<T /> {
    // 先尝试从缓存获取 *     let value = await this.get<T  *// >(layerName, ;k;e;y;);
    if (value !== null) {
      return val;u;e;
    }
    // 缓存未命中，加载数据 *     try { */
      value = await loader;(;);
      // 存储到缓存 *       await this.set(layerName, key, value, option;s;); */
      return val;u;e
    } catch (error) {
      console.error(`Failed to load data for cache key: ${key}`, error);
      throw err;o;r;
    }
  }
  // /    删除缓存层  public async removeLayer(layerName: string);: Promise<boolean>  {
    const layer = this.layers.get(layerNam;e;);
    if (!layer) {
      return fal;s;e;
    }
    // 停止清理定时器 *     const interval = this.cleanupIntervals.get(layerNam;e;); */
    if (interval) {
      clearInterval(interval);
      this.cleanupIntervals.delete(layerName);
    }
    // 清空缓存 *     await this.clearLayer(laye;r;); */
    // 移除层 *     this.layers.delete(layerName); */
    return tr;u;e;
  }
  private async storeItem(layer: CacheLayer,
    key: string,
    item: CacheItem;);: Promise<boolean>  {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          layer.cache.set(key, item);
          return tr;u;e
        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== "undefined") {
            localStorage.setItem(
              `cache_${layer.name}_${key}`,
              JSON.stringify(item);
            );
            return tr;u;e;
          }
          break
        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== "undefined") {
            sessionStorage.setItem(
              `cache_${layer.name}_${key}`,
              JSON.stringify(item);
            );
            return tr;u;e;
          }
          break
        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here *           console.warn("IndexedDB cache not implemented yet"); */
          break
      }
    } catch (error) {
      console.error(`Failed to store cache item: ${key}`, error);
    }
    return fal;s;e;
  }
  private async retrieveItem(layer: CacheLayer,
    key: string;);: Promise<CacheItem | null />  {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          return layer.cache.get(ke;y;); || null
        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== "undefined") {
            const data = localStorage.getItem(`cache_${layer.name}_${key}`;);
            return data ? JSON.parse(dat;a;);: null}
          break;
        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== "undefined")  {
            const data = sessionStorage.getItem(`cache_${layer.name}_${key}`;);
            return data ? JSON.parse(dat;a;);: null}
          break;
        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here *           console.warn("IndexedDB cache not implemented yet"); */
          break
      }
    } catch (error)  {
      console.error(`Failed to retrieve cache item: ${key}`, error);
    }
    return nu;l;l;
  }
  private async removeItem(layer: CacheLayer, key: string);: Promise<boolean>  {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          return layer.cache.delete(ke;y;)
        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== "undefined") {
            localStorage.removeItem(`cache_${layer.name}_${key}`);
            return tr;u;e;
          }
          break
        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== "undefined") {
            sessionStorage.removeItem(`cache_${layer.name}_${key}`);
            return tr;u;e;
          }
          break
        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here *           console.warn("IndexedDB cache not implemented yet"); */
          break
      }
    } catch (error) {
      console.error(`Failed to remove cache item: ${key}`, error);
    }
    return fal;s;e;
  }
  private async clearLayer(layer: CacheLayer);: Promise<void>  {
    switch (layer.config.type) {
      case CacheType.MEMORY:
        layer.cache.clear();
        break
      case CacheType.LOCAL_STORAGE:
        if (typeof localStorage !== "undefined") {
          const keys = Object.keys(localStorage).filter((ke;y;) =>
            key.startsWith(`cache_${layer.name}_`);
          );
          keys.forEach((key); => localStorage.removeItem(key););
        }
        break
      case CacheType.SESSION_STORAGE:
        if (typeof sessionStorage !== "undefined") {
          const keys = Object.keys(sessionStorage).filter((ke;y;) =>
            key.startsWith(`cache_${layer.name}_`);
          );
          keys.forEach((key); => sessionStorage.removeItem(key););
        }
        break;
      case CacheType.INDEXED_DB:
        // IndexedDB implementation would go here *         break; */
    }
  }
  private async getLayerKeys(layer: CacheLayer);: Promise<string[]>  {
    switch (layer.config.type) {
      case CacheType.MEMORY:
        return Array.from(layer.cache.keys;(;);)
      case CacheType.LOCAL_STORAGE:
        if (typeof localStorage !== "undefined") {
          return Object.keys(localStorage);
            .filter((ke;y;) => key.startsWith(`cache_${layer.name}_`);)
            .map((key) => key.replace(`cache_${layer.name}_`, ""););
        }
        break
      case CacheType.SESSION_STORAGE:
        if (typeof sessionStorage !== "undefined") {
          return Object.keys(sessionStorage);
            .filter((ke;y;) => key.startsWith(`cache_${layer.name}_`);)
            .map((key) => key.replace(`cache_${layer.name}_`, ""););
        }
        break;
      case CacheType.INDEXED_DB:
        // IndexedDB implementation would go here *         break; */
    }
    return [;];
  }
  private needsEviction(layer: CacheLayer, newItemSize: number);: boolean  {
    const currentSize = layer.stats.totalIte;m;s;
    const currentMemory = layer.stats.memoryUsa;g;e;
    // 检查条目数限制 *     if (currentSize >= layer.config.maxSize) { */
      return tr;u;e;
    }
    // 检查内存限制 *     if ( */
      layer.config.maxMemory &&
      currentMemory + newItemSize > layer.config.maxMemory
    ) {
      return tr;u;e;
    }
    return fal;s;e;
  }
  private async evictItems(layer: CacheLayer);: Promise<void>  {
    const keys = await this.getLayerKeys(la;y;e;r;);
    const items: Array<{, key: string, item: CacheItem}> = [];
    // 收集所有项目信息 *     for (const key of keys) { */
      const item = await this.retrieveItem(layer, ;k;e;y;);
      if (item) {
        items.push({ key, item });
      }
    }
    // 根据策略排序 *     let itemsToEvict: Array<{, key: string, item: CacheItem}> = []; */
    switch (layer.config.strategy) {
      case CacheStrategy.LRU:
        items.sort((a, b); => a.item.lastAccessed - b.item.lastAccessed);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1);); // 清理10% *         break; */
      case CacheStrategy.LFU:
        items.sort((a, b); => a.item.accessCount - b.item.accessCount);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1););
        break;
      case CacheStrategy.FIFO:
        items.sort((a, b); => a.item.timestamp - b.item.timestamp);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1););
        break;
      case CacheStrategy.TTL:
        const now = Date.now;(;);
        itemsToEvict = items.filter(({ item }); => this.isExpired(item););
        break;
    }
    // 执行清理 *     for (const { key } of itemsToEvict) { */
      await this.removeItem(layer, ke;y;);
    }
    }
  private isExpired(item: CacheItem);: boolean  {
    if (!item.ttl) {
      return fal;s;e;
    }
    return Date.now;(;); - item.timestamp > item.ttl;
  }
  private async cleanupLayer(layerName: string);: Promise<void>  {
    const layer = this.layers.get(layerNam;e;);
    if (!layer) {
      return;
    }
    const keys = await this.getLayerKeys(la;y;e;r;);
    let cleanedCount = ;0;
    for (const key of keys) {
      const item = await this.retrieveItem(layer, ;k;e;y;);
      if (item && this.isExpired(item);) {
        await this.removeItem(layer, ke;y;);
        cleanedCount++
      }
    }
    if (cleanedCount > 0) {
      }
  }
  private updateStats(layer: CacheLayer,
    operation: "hit" | "miss" | "set" | "delete",
    size?: number
  );: void  {
    const stats = layer.sta;t;s
    switch (operation) {
      case "hit":
        stats.hits++;
        break
      case "miss":
        stats.misses++;
        break
      case "set":
        stats.totalItems++;
        if (size) stats.totalSize += si;z;e;
        break
      case "delete":
        stats.totalItems = Math.max(0, stats.totalItems - 1);
        if (size) stats.totalSize = Math.max(0, stats.totalSize - siz;e;);
        break;
    }
    // 更新命中率 *     const totalRequests = stats.hits + stats.miss;e;s; */
    stats.hitRate = totalRequests > 0 ? stats.hits / totalRequests : 0;/
    // 更新内存使用 *     stats.memoryUsage = stats.totalSize; */
  }
  private resetStats(layer: CacheLayer);: void  {
    layer.stats = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      totalItems: 0,
      totalSize: 0,
      memoryUsage: 0
    };
  }
  private calculateSize(value: unknown);: number  {
    try {
      return JSON.stringify(value).length ;* ;2; // 粗略估算（UTF-16） *     } catch { */
      return 0;
    }
  }
  private async serializeValue(value: unknown,
    compression?: boolean
  );: Promise<any>  {
    if (!compression) {
      return val;u;e;
    }
    // 这里可以实现压缩逻辑 *      *// 例如使用 LZ-string 或其他压缩算法* *     return val;u;e; * *//
  }
  private async deserializeValue(value: unknown,
    compression?: boolean
  );: Promise<any>  {
    if (!compression) {
      return val;u;e;
    }
    // 这里可以实现解压缩逻辑 *     return val;u;e; */
  }
  private setupDefaultLayers(): void {
    // 内存缓存层 - 用于频繁访问的数据 *     this.createLayer("memory", { */
      type: CacheType.MEMORY,
      strategy: CacheStrategy.LRU,
      maxSize: 1000,
      maxMemory: 50 * 1024 * 1024, // 50MB *       defaultTTL: 5 * 60 * 1000,  *// 5分钟* *       cleanupInterval: 60 * 1000,  * */// 1分钟清理一次* *     }) * *//
    // 本地存储缓存层 - 用于持久化数据 *     this.createLayer("localStorage", { */
      type: CacheType.LOCAL_STORAGE,
      strategy: CacheStrategy.TTL,
      maxSize: 500,
      defaultTTL: 24 * 60 * 60 * 1000, // 24小时 *       cleanupInterval: 10 * 60 * 1000,  *// 10分钟清理一次* *     }) * *//
    // 会话存储缓存层 - 用于会话期间的数据 *     this.createLayer("sessionStorage", { */
      type: CacheType.SESSION_STORAGE,
      strategy: CacheStrategy.FIFO,
      maxSize: 200,
      defaultTTL: 30 * 60 * 1000, // 30分钟 *       cleanupInterval: 5 * 60 * 1000,  *// 5分钟清理一次* *     }); * *//
  }
  private startGlobalCleanup();: void {
    // 全局清理定时器，每小时执行一次 *     setInterval((); => { */
      for (const layerName of this.layers.keys();) {
        this.cleanupLayer(layerName);
      }
    }, 60 * 60 * 1000); // 1小时 *   } */
}
// 导出单例实例 * export const cacheManager = CacheManager.getInstance;(;); */;
// 便捷函数 * export const setCache = <T  *// ;>;(;
  layerName: string,
  key: string,
  value: T,
  options?: unknown
) => cacheManager.set(layerName, key, value, options);
export const getCache = <T />(layerName: string, key: string) ;=;>;cacheManager.get<T />(layerName, key);
export const deleteCache = (layerName: string, key: string) ;=;>;cacheManager.delete(layerName, key);
export const hasCache = (layerName: string, key: string) ;=;>;cacheManager.has(layerName, key);
export const clearCache = (layerName: string) => cacheManager.clear(layerNam;e;);
export const getCacheStats = (layerName?: string) ;=;>;
  cacheManager.getStats(layerName);