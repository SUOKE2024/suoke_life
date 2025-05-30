/**
 * 索克生活 - 缓存管理系统
 * 提供多层缓存、过期策略、缓存优化和性能监控
 */

import { performanceMonitor, PerformanceCategory } from '../monitoring/PerformanceMonitor';

export enum CacheType {
  MEMORY = 'MEMORY',
  LOCAL_STORAGE = 'LOCAL_STORAGE',
  SESSION_STORAGE = 'SESSION_STORAGE',
  INDEXED_DB = 'INDEXED_DB'
}

export enum CacheStrategy {
  LRU = 'LRU',           // 最近最少使用
  LFU = 'LFU',           // 最少使用频率
  FIFO = 'FIFO',         // 先进先出
  TTL = 'TTL'            // 基于时间过期
}

export interface CacheItem<T = any> {
  key: string;
  value: T;
  timestamp: number;
  ttl?: number;          // 生存时间（毫秒）
  accessCount: number;
  lastAccessed: number;
  size?: number;         // 数据大小（字节）
  metadata?: Record<string, any>;
}

export interface CacheConfig {
  type: CacheType;
  strategy: CacheStrategy;
  maxSize: number;       // 最大条目数
  maxMemory?: number;    // 最大内存使用（字节）
  defaultTTL?: number;   // 默认TTL（毫秒）
  cleanupInterval?: number; // 清理间隔（毫秒）
  compression?: boolean; // 是否压缩
}

export interface CacheStats {
  hits: number;
  misses: number;
  hitRate: number;
  totalItems: number;
  totalSize: number;
  memoryUsage: number;
  oldestItem?: number;
  newestItem?: number;
}

export interface CacheLayer {
  name: string;
  config: CacheConfig;
  cache: Map<string, CacheItem>;
  stats: CacheStats;
}

export class CacheManager {
  private static instance: CacheManager;
  private layers: Map<string, CacheLayer> = new Map();
  private cleanupIntervals: Map<string, NodeJS.Timeout> = new Map();
  private compressionEnabled: boolean = false;

  private constructor() {
    this.setupDefaultLayers();
    this.startGlobalCleanup();
  }

  public static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  /**
   * 创建缓存层
   */
  public createLayer(name: string, config: CacheConfig): void {
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

    // 启动定期清理
    if (config.cleanupInterval) {
      const interval = setInterval(() => {
        this.cleanupLayer(name);
      }, config.cleanupInterval);
      
      this.cleanupIntervals.set(name, interval);
    }

    console.log(`🗄️ Cache layer created: ${name} (${config.type}, ${config.strategy})`);
  }

  /**
   * 设置缓存项
   */
  public async set<T>(
    layerName: string,
    key: string,
    value: T,
    options: {
      ttl?: number;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<boolean> {
    return performanceMonitor.measureAsync(
      'cache_set',
      PerformanceCategory.MEMORY,
      async () => {
        const layer = this.layers.get(layerName);
        if (!layer) {
          console.warn(`Cache layer not found: ${layerName}`);
          return false;
        }

        const now = Date.now();
        const serializedValue = await this.serializeValue(value, layer.config.compression);
        const size = this.calculateSize(serializedValue);

        const item: CacheItem<T> = {
          key,
          value: serializedValue,
          timestamp: now,
          ttl: options.ttl || layer.config.defaultTTL,
          accessCount: 0,
          lastAccessed: now,
          size,
          metadata: options.metadata
        };

        // 检查是否需要清理空间
        if (this.needsEviction(layer, size)) {
          await this.evictItems(layer);
        }

        // 存储到不同类型的缓存
        const success = await this.storeItem(layer, key, item);
        
        if (success) {
          this.updateStats(layer, 'set', size);
        }

        return success;
      }
    );
  }

  /**
   * 获取缓存项
   */
  public async get<T>(layerName: string, key: string): Promise<T | null> {
    return performanceMonitor.measureAsync(
      'cache_get',
      PerformanceCategory.MEMORY,
      async () => {
        const layer = this.layers.get(layerName);
        if (!layer) {
          console.warn(`Cache layer not found: ${layerName}`);
          return null;
        }

        const item = await this.retrieveItem(layer, key);
        
        if (!item) {
          this.updateStats(layer, 'miss');
          return null;
        }

        // 检查是否过期
        if (this.isExpired(item)) {
          await this.delete(layerName, key);
          this.updateStats(layer, 'miss');
          return null;
        }

        // 更新访问信息
        item.accessCount++;
        item.lastAccessed = Date.now();
        await this.storeItem(layer, key, item);

        this.updateStats(layer, 'hit');
        
        return await this.deserializeValue(item.value, layer.config.compression);
      }
    );
  }

  /**
   * 删除缓存项
   */
  public async delete(layerName: string, key: string): Promise<boolean> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return false;
    }

    const item = await this.retrieveItem(layer, key);
    if (!item) {
      return false;
    }

    const success = await this.removeItem(layer, key);
    
    if (success) {
      this.updateStats(layer, 'delete', item.size);
    }

    return success;
  }

  /**
   * 检查缓存项是否存在
   */
  public async has(layerName: string, key: string): Promise<boolean> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return false;
    }

    const item = await this.retrieveItem(layer, key);
    return item !== null && !this.isExpired(item);
  }

  /**
   * 清空缓存层
   */
  public async clear(layerName: string): Promise<void> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return;
    }

    await this.clearLayer(layer);
    this.resetStats(layer);
    
    console.log(`🗑️ Cache layer cleared: ${layerName}`);
  }

  /**
   * 获取缓存统计信息
   */
  public getStats(layerName?: string): CacheStats | Map<string, CacheStats> {
    if (layerName) {
      const layer = this.layers.get(layerName);
      return layer ? layer.stats : {
        hits: 0,
        misses: 0,
        hitRate: 0,
        totalItems: 0,
        totalSize: 0,
        memoryUsage: 0
      };
    }

    const allStats = new Map<string, CacheStats>();
    for (const [name, layer] of this.layers.entries()) {
      allStats.set(name, layer.stats);
    }
    return allStats;
  }

  /**
   * 获取所有缓存键
   */
  public async getKeys(layerName: string): Promise<string[]> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return [];
    }

    return await this.getLayerKeys(layer);
  }

  /**
   * 批量设置
   */
  public async setMultiple<T>(
    layerName: string,
    items: Array<{ key: string; value: T; options?: any }>
  ): Promise<boolean[]> {
    const results: boolean[] = [];
    
    for (const item of items) {
      const result = await this.set(layerName, item.key, item.value, item.options);
      results.push(result);
    }

    return results;
  }

  /**
   * 批量获取
   */
  public async getMultiple<T>(layerName: string, keys: string[]): Promise<Map<string, T | null>> {
    const results = new Map<string, T | null>();
    
    for (const key of keys) {
      const value = await this.get<T>(layerName, key);
      results.set(key, value);
    }

    return results;
  }

  /**
   * 预热缓存
   */
  public async warmup<T>(
    layerName: string,
    dataLoader: () => Promise<Map<string, T>>,
    options: { ttl?: number } = {}
  ): Promise<void> {
    console.log(`🔥 Warming up cache layer: ${layerName}`);
    
    try {
      const data = await dataLoader();
      const items = Array.from(data.entries()).map(([key, value]) => ({
        key,
        value,
        options
      }));

      await this.setMultiple(layerName, items);
      console.log(`✅ Cache warmup completed: ${layerName} (${data.size} items)`);
    } catch (error) {
      console.error(`❌ Cache warmup failed: ${layerName}`, error);
    }
  }

  /**
   * 缓存穿透保护
   */
  public async getOrSet<T>(
    layerName: string,
    key: string,
    loader: () => Promise<T>,
    options: { ttl?: number; metadata?: Record<string, any> } = {}
  ): Promise<T> {
    // 先尝试从缓存获取
    let value = await this.get<T>(layerName, key);
    
    if (value !== null) {
      return value;
    }

    // 缓存未命中，加载数据
    try {
      value = await loader();
      
      // 存储到缓存
      await this.set(layerName, key, value, options);
      
      return value;
    } catch (error) {
      console.error(`Failed to load data for cache key: ${key}`, error);
      throw error;
    }
  }

  /**
   * 删除缓存层
   */
  public async removeLayer(layerName: string): Promise<boolean> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return false;
    }

    // 停止清理定时器
    const interval = this.cleanupIntervals.get(layerName);
    if (interval) {
      clearInterval(interval);
      this.cleanupIntervals.delete(layerName);
    }

    // 清空缓存
    await this.clearLayer(layer);
    
    // 移除层
    this.layers.delete(layerName);
    
    console.log(`🗑️ Cache layer removed: ${layerName}`);
    return true;
  }

  private async storeItem(layer: CacheLayer, key: string, item: CacheItem): Promise<boolean> {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          layer.cache.set(key, item);
          return true;

        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== 'undefined') {
            localStorage.setItem(`cache_${layer.name}_${key}`, JSON.stringify(item));
            return true;
          }
          break;

        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.setItem(`cache_${layer.name}_${key}`, JSON.stringify(item));
            return true;
          }
          break;

        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here
          console.warn('IndexedDB cache not implemented yet');
          break;
      }
    } catch (error) {
      console.error(`Failed to store cache item: ${key}`, error);
    }
    
    return false;
  }

  private async retrieveItem(layer: CacheLayer, key: string): Promise<CacheItem | null> {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          return layer.cache.get(key) || null;

        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== 'undefined') {
            const data = localStorage.getItem(`cache_${layer.name}_${key}`);
            return data ? JSON.parse(data) : null;
          }
          break;

        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== 'undefined') {
            const data = sessionStorage.getItem(`cache_${layer.name}_${key}`);
            return data ? JSON.parse(data) : null;
          }
          break;

        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here
          console.warn('IndexedDB cache not implemented yet');
          break;
      }
    } catch (error) {
      console.error(`Failed to retrieve cache item: ${key}`, error);
    }
    
    return null;
  }

  private async removeItem(layer: CacheLayer, key: string): Promise<boolean> {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          return layer.cache.delete(key);

        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== 'undefined') {
            localStorage.removeItem(`cache_${layer.name}_${key}`);
            return true;
          }
          break;

        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.removeItem(`cache_${layer.name}_${key}`);
            return true;
          }
          break;

        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here
          console.warn('IndexedDB cache not implemented yet');
          break;
      }
    } catch (error) {
      console.error(`Failed to remove cache item: ${key}`, error);
    }
    
    return false;
  }

  private async clearLayer(layer: CacheLayer): Promise<void> {
    switch (layer.config.type) {
      case CacheType.MEMORY:
        layer.cache.clear();
        break;

      case CacheType.LOCAL_STORAGE:
        if (typeof localStorage !== 'undefined') {
          const keys = Object.keys(localStorage).filter(key => 
            key.startsWith(`cache_${layer.name}_`)
          );
          keys.forEach(key => localStorage.removeItem(key));
        }
        break;

      case CacheType.SESSION_STORAGE:
        if (typeof sessionStorage !== 'undefined') {
          const keys = Object.keys(sessionStorage).filter(key => 
            key.startsWith(`cache_${layer.name}_`)
          );
          keys.forEach(key => sessionStorage.removeItem(key));
        }
        break;

      case CacheType.INDEXED_DB:
        // IndexedDB implementation would go here
        break;
    }
  }

  private async getLayerKeys(layer: CacheLayer): Promise<string[]> {
    switch (layer.config.type) {
      case CacheType.MEMORY:
        return Array.from(layer.cache.keys());

      case CacheType.LOCAL_STORAGE:
        if (typeof localStorage !== 'undefined') {
          return Object.keys(localStorage)
            .filter(key => key.startsWith(`cache_${layer.name}_`))
            .map(key => key.replace(`cache_${layer.name}_`, ''));
        }
        break;

      case CacheType.SESSION_STORAGE:
        if (typeof sessionStorage !== 'undefined') {
          return Object.keys(sessionStorage)
            .filter(key => key.startsWith(`cache_${layer.name}_`))
            .map(key => key.replace(`cache_${layer.name}_`, ''));
        }
        break;

      case CacheType.INDEXED_DB:
        // IndexedDB implementation would go here
        break;
    }
    
    return [];
  }

  private needsEviction(layer: CacheLayer, newItemSize: number): boolean {
    const currentSize = layer.stats.totalItems;
    const currentMemory = layer.stats.memoryUsage;

    // 检查条目数限制
    if (currentSize >= layer.config.maxSize) {
      return true;
    }

    // 检查内存限制
    if (layer.config.maxMemory && (currentMemory + newItemSize) > layer.config.maxMemory) {
      return true;
    }

    return false;
  }

  private async evictItems(layer: CacheLayer): Promise<void> {
    const keys = await this.getLayerKeys(layer);
    const items: Array<{ key: string; item: CacheItem }> = [];

    // 收集所有项目信息
    for (const key of keys) {
      const item = await this.retrieveItem(layer, key);
      if (item) {
        items.push({ key, item });
      }
    }

    // 根据策略排序
    let itemsToEvict: Array<{ key: string; item: CacheItem }> = [];

    switch (layer.config.strategy) {
      case CacheStrategy.LRU:
        items.sort((a, b) => a.item.lastAccessed - b.item.lastAccessed);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1)); // 清理10%
        break;

      case CacheStrategy.LFU:
        items.sort((a, b) => a.item.accessCount - b.item.accessCount);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1));
        break;

      case CacheStrategy.FIFO:
        items.sort((a, b) => a.item.timestamp - b.item.timestamp);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1));
        break;

      case CacheStrategy.TTL:
        const now = Date.now();
        itemsToEvict = items.filter(({ item }) => this.isExpired(item));
        break;
    }

    // 执行清理
    for (const { key } of itemsToEvict) {
      await this.removeItem(layer, key);
    }

    console.log(`🧹 Evicted ${itemsToEvict.length} items from cache layer: ${layer.name}`);
  }

  private isExpired(item: CacheItem): boolean {
    if (!item.ttl) {
      return false;
    }
    
    return Date.now() - item.timestamp > item.ttl;
  }

  private async cleanupLayer(layerName: string): Promise<void> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return;
    }

    const keys = await this.getLayerKeys(layer);
    let cleanedCount = 0;

    for (const key of keys) {
      const item = await this.retrieveItem(layer, key);
      if (item && this.isExpired(item)) {
        await this.removeItem(layer, key);
        cleanedCount++;
      }
    }

    if (cleanedCount > 0) {
      console.log(`🧹 Cleaned up ${cleanedCount} expired items from cache layer: ${layerName}`);
    }
  }

  private updateStats(layer: CacheLayer, operation: 'hit' | 'miss' | 'set' | 'delete', size?: number): void {
    const stats = layer.stats;

    switch (operation) {
      case 'hit':
        stats.hits++;
        break;
      case 'miss':
        stats.misses++;
        break;
      case 'set':
        stats.totalItems++;
        if (size) stats.totalSize += size;
        break;
      case 'delete':
        stats.totalItems = Math.max(0, stats.totalItems - 1);
        if (size) stats.totalSize = Math.max(0, stats.totalSize - size);
        break;
    }

    // 更新命中率
    const totalRequests = stats.hits + stats.misses;
    stats.hitRate = totalRequests > 0 ? stats.hits / totalRequests : 0;

    // 更新内存使用
    stats.memoryUsage = stats.totalSize;
  }

  private resetStats(layer: CacheLayer): void {
    layer.stats = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      totalItems: 0,
      totalSize: 0,
      memoryUsage: 0
    };
  }

  private calculateSize(value: any): number {
    try {
      return JSON.stringify(value).length * 2; // 粗略估算（UTF-16）
    } catch {
      return 0;
    }
  }

  private async serializeValue(value: any, compression?: boolean): Promise<any> {
    if (!compression) {
      return value;
    }

    // 这里可以实现压缩逻辑
    // 例如使用 LZ-string 或其他压缩算法
    return value;
  }

  private async deserializeValue(value: any, compression?: boolean): Promise<any> {
    if (!compression) {
      return value;
    }

    // 这里可以实现解压缩逻辑
    return value;
  }

  private setupDefaultLayers(): void {
    // 内存缓存层 - 用于频繁访问的数据
    this.createLayer('memory', {
      type: CacheType.MEMORY,
      strategy: CacheStrategy.LRU,
      maxSize: 1000,
      maxMemory: 50 * 1024 * 1024, // 50MB
      defaultTTL: 5 * 60 * 1000,   // 5分钟
      cleanupInterval: 60 * 1000    // 1分钟清理一次
    });

    // 本地存储缓存层 - 用于持久化数据
    this.createLayer('localStorage', {
      type: CacheType.LOCAL_STORAGE,
      strategy: CacheStrategy.TTL,
      maxSize: 500,
      defaultTTL: 24 * 60 * 60 * 1000, // 24小时
      cleanupInterval: 10 * 60 * 1000   // 10分钟清理一次
    });

    // 会话存储缓存层 - 用于会话期间的数据
    this.createLayer('sessionStorage', {
      type: CacheType.SESSION_STORAGE,
      strategy: CacheStrategy.FIFO,
      maxSize: 200,
      defaultTTL: 30 * 60 * 1000,  // 30分钟
      cleanupInterval: 5 * 60 * 1000 // 5分钟清理一次
    });
  }

  private startGlobalCleanup(): void {
    // 全局清理定时器，每小时执行一次
    setInterval(() => {
      console.log('🧹 Starting global cache cleanup...');
      
      for (const layerName of this.layers.keys()) {
        this.cleanupLayer(layerName);
      }
    }, 60 * 60 * 1000); // 1小时
  }
}

// 导出单例实例
export const cacheManager = CacheManager.getInstance();

// 便捷函数
export const setCache = <T>(layerName: string, key: string, value: T, options?: any) =>
  cacheManager.set(layerName, key, value, options);

export const getCache = <T>(layerName: string, key: string) =>
  cacheManager.get<T>(layerName, key);

export const deleteCache = (layerName: string, key: string) =>
  cacheManager.delete(layerName, key);

export const hasCache = (layerName: string, key: string) =>
  cacheManager.has(layerName, key);

export const clearCache = (layerName: string) =>
  cacheManager.clear(layerName);

export const getCacheStats = (layerName?: string) =>
  cacheManager.getStats(layerName); 