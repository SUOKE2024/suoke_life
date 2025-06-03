import React from "react";
import { usePerformanceMonitor } from "../../hooks/usePerformanceMonitor";
import { errorHandler, ErrorType } from "../error/ErrorHandler";
import { performanceMonitor, PerformanceCategory } from "../monitoring/PerformanceMonitor";

/**
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
  LRU = "LRU", // 最近最少使用
  LFU = "LFU", // 最少使用频率
  FIFO = "FIFO", // 先进先出
  TTL = "TTL" // 基于过期时间
}

export interface CacheItem<T = any> {
  key: string;
  value: T;
  timestamp: number;
  ttl?: number; // 生存时间（毫秒）
  accessCount: number;
  lastAccessed: number;
  size?: number; // 数据大小（字节）
  metadata?: Record<string, any>;
}

export interface CacheConfig {
  type: CacheType;
  strategy: CacheStrategy;
  maxSize: number;
  maxMemory?: number; // 最大内存使用（字节）
  defaultTTL?: number; // 默认TTL（毫秒）
  cleanupInterval?: number; // 清理间隔（毫秒）
  compression?: boolean; // 是否压缩
  maxMemorySize: number; // 最大内存缓存大小(MB)
  persistentStorage: boolean; // 是否启用持久化存储
  encryptionEnabled: boolean; // 是否启用加密
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
  totalHits: number;
  totalMisses: number;
  evictionCount: number;
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
        memoryUsage: 0,
        totalHits: 0,
        totalMisses: 0,
        evictionCount: 0
      }
    };
    this.layers.set(name, layer);

    if (config.cleanupInterval) {
      const interval = setInterval(() => {
        this.cleanupLayer(name);
      }, config.cleanupInterval);
      this.cleanupIntervals.set(name, interval);
    }
  }

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
      "cache_set",
      PerformanceCategory.MEMORY,
      async () => {
        const layer = this.layers.get(layerName);
        if (!layer) {
          return false;
        }
        const now = Date.now();
        const serializedValue = await this.serializeValue(
          value,
          layer.config.compression && this.compressionEnabled
        );
        const size = this.calculateSize(serializedValue);
        const item: CacheItem<T> = {
          key,
          value: serializedValue,
          timestamp: now,
          ttl: options.ttl || layer.config.defaultTTL,
          accessCount: 0,
          lastAccessed: now,
          size,
          metadata: options.metadata,
          compressed: layer.config.compression && this.compressionEnabled,
          encrypted: layer.config.encryptionEnabled
        };

        if (this.needsEviction(layer, size)) {
          await this.evictItems(layer, size);
        }

        if (await this.storeItem(layer, key, item)) {
          this.updateStats(layer, "set", size);
          return true;
        }
        return false;
      }
    );
  }

  public async get<T>(layerName: string, key: string): Promise<T | null> {
    return performanceMonitor.measureAsync(
      "cache_get",
      PerformanceCategory.MEMORY,
      async () => {
        const layer = this.layers.get(layerName);
        if (!layer) {
          return null;
        }
        const item = await this.retrieveItem(layer, key);
        if (!item) {
          this.updateStats(layer, "miss");
          return null;
        }
        if (this.isExpired(item)) {
          await this.delete(layerName, key);
          this.updateStats(layer, "miss");
          return null;
        }
        item.accessCount++;
        item.lastAccessed = Date.now();
        await this.storeItem(layer, key, item);
        this.updateStats(layer, "hit");

        let value = item.value;

        if (item.encrypted) {
          value = await this.decryptData(value);
        }
        
        if (item.compressed) {
          value = await this.decompressData(value);
        }

        return value as T;
      }
    );
  }

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
      this.updateStats(layer, "delete", item.size);
    }
    return success;
  }

  public async has(layerName: string, key: string): Promise<boolean> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return false;
    }
    const item = await this.retrieveItem(layer, key);
    return item !== null && !this.isExpired(item);
  }

  public async clear(layerName: string): Promise<void> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return;
    }
    await this.clearLayer(layer);
    this.resetStats(layer);
  }

  public getStats(layerName?: string): CacheStats | Map<string, CacheStats> {
    if (layerName) {
      const layer = this.layers.get(layerName);
      return layer ? layer.stats : {
        hits: 0,
        misses: 0,
        hitRate: 0,
        totalItems: 0,
        totalSize: 0,
        memoryUsage: 0,
        totalHits: 0,
        totalMisses: 0,
        evictionCount: 0
      };
    }
    const allStats = new Map<string, CacheStats>();
    for (const [name, layer] of this.layers.entries()) {
      allStats.set(name, layer.stats);
    }
    return allStats;
  }

  public async getKeys(layerName: string): Promise<string[]> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return [];
    }
    return await this.getLayerKeys(layer);
  }

  public async setMultiple<T>(layerName: string,
    items: Array<{ key: string, value: T, options?: unknown }>
  ): Promise<boolean[]> {
    const results: boolean[] = [];
    for (const item of items) {
      const result = await this.set(layerName, item.key, item.value, item.options);
      results.push(result);
    }
    return results;
  }

  public async getMultiple<T>(layerName: string,
    keys: string[]): Promise<Map<string, T | null>> {
    const results = new Map<string, T | null>();
    for (const key of keys) {
      const value = await this.get<T>(layerName, key);
      results.set(key, value);
    }
    return results;
  }

  public async warmup<T>(
    layerName: string,
    dataLoader: () => Promise<Map<string, T>>,
    options: { ttl?: number } = {}
  ): Promise<void> {
    try {
      const data = await dataLoader();
      const items = Array.from(data.entries()).map(([key, value]) => ({
        key,
        value,
        options
      }));
      await this.setMultiple(layerName, items);
    } catch (error) {
      // Handle error
    }
  }

  public async getOrSet<T>(
    layerName: string,
    key: string,
    loader: () => Promise<T>,
    options: { ttl?: number, metadata?: Record<string, any> } = {}
  ): Promise<T> {
    const value = await this.get<T>(layerName, key);
    if (value !== null) {
      return value;
    }
    try {
      const newValue = await loader();
      await this.set(layerName, key, newValue, options);
      return newValue;
    } catch (error) {
      throw error;
    }
  }

  public async removeLayer(layerName: string): Promise<boolean> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return false;
    }
    if (this.cleanupIntervals.get(layerName)) {
      clearInterval(this.cleanupIntervals.get(layerName));
      this.cleanupIntervals.delete(layerName);
    }
    await this.clearLayer(layer);
    return true;
  }

  private async storeItem(layer: CacheLayer,
    key: string,
    item: CacheItem<any>): Promise<boolean> {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          layer.cache.set(key, item);
          return true;
        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== "undefined") {
            localStorage.setItem(
              `cache_${layer.name}_${key}`,
              JSON.stringify(item)
            );
            return true;
          }
          break;
        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== "undefined") {
            sessionStorage.setItem(
              `cache_${layer.name}_${key}`,
              JSON.stringify(item)
            );
            return true;
          }
          break;
        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here
          break;
      }
    } catch (error) {
      // Handle error
    }
    return false;
  }

  private async retrieveItem(layer: CacheLayer,
    key: string): Promise<CacheItem<any> | null> {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          return layer.cache.get(key) || null;
        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== "undefined") {
            const data = localStorage.getItem(`cache_${layer.name}_${key}`);
            return data ? JSON.parse(data) : null;
          }
          break;
        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== "undefined") {
            const data = sessionStorage.getItem(`cache_${layer.name}_${key}`);
            return data ? JSON.parse(data) : null;
          }
          break;
        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here
          break;
      }
    } catch (error) {
      // Handle error
    }
    return null;
  }

  private async removeItem(layer: CacheLayer, key: string): Promise<boolean> {
    try {
      switch (layer.config.type) {
        case CacheType.MEMORY:
          return layer.cache.delete(key);
        case CacheType.LOCAL_STORAGE:
          if (typeof localStorage !== "undefined") {
            localStorage.removeItem(`cache_${layer.name}_${key}`);
            return true;
          }
          break;
        case CacheType.SESSION_STORAGE:
          if (typeof sessionStorage !== "undefined") {
            sessionStorage.removeItem(`cache_${layer.name}_${key}`);
            return true;
          }
          break;
        case CacheType.INDEXED_DB:
          // IndexedDB implementation would go here
          break;
      }
    } catch (error) {
      // Handle error
    }
    return false;
  }

  private async clearLayer(layer: CacheLayer): Promise<void> {
    switch (layer.config.type) {
      case CacheType.MEMORY:
        layer.cache.clear();
        break;
      case CacheType.LOCAL_STORAGE:
        if (typeof localStorage !== "undefined") {
          const keys = Object.keys(localStorage).filter((key) =>
            key.startsWith(`cache_${layer.name}_`);
          );
          keys.forEach((key) => localStorage.removeItem(key));
        }
        break;
      case CacheType.SESSION_STORAGE:
        if (typeof sessionStorage !== "undefined") {
          const keys = Object.keys(sessionStorage).filter((key) =>
            key.startsWith(`cache_${layer.name}_`);
          );
          keys.forEach((key) => sessionStorage.removeItem(key));
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
        return Array.from(layer.cache.keys);
      case CacheType.LOCAL_STORAGE:
        if (typeof localStorage !== "undefined") {
          return Object.keys(localStorage)
            .filter((key) => key.startsWith(`cache_${layer.name}_`))
            .map((key) => key.replace(`cache_${layer.name}_`, ""));
        }
        break;
      case CacheType.SESSION_STORAGE:
        if (typeof sessionStorage !== "undefined") {
          return Object.keys(sessionStorage)
            .filter((key) => key.startsWith(`cache_${layer.name}_`))
            .map((key) => key.replace(`cache_${layer.name}_`, ""));
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
    if (currentSize >= layer.config.maxSize) {
      return true;
    }
    if (
      layer.config.maxMemory &&
      currentMemory + newItemSize > layer.config.maxMemory
    ) {
      return true;
    }
    return false;
  }

  private async evictItems(layer: CacheLayer, requiredSpace: number): Promise<void> {
    const requiredMB = requiredSpace / (1024 * 1024);
    let freedMB = 0;

    const keys = await this.getLayerKeys(layer);
    const items: Array<{ key: string, item: CacheItem<any> }> = [];
    for (const key of keys) {
      const item = await this.retrieveItem(layer, key);
      if (item) {
        items.push({ key, item });
      }
    }

    let itemsToEvict: Array<{ key: string, item: CacheItem<any> }> = [];
    switch (layer.config.strategy) {
      case CacheStrategy.LRU:
        items.sort((a, b) => a.item.lastAccessed - b.item.lastAccessed);
        itemsToEvict = items.slice(0, Math.ceil(items.length * 0.1));
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

    for (const { key } of itemsToEvict) {
      await this.removeItem(layer, key);
      freedMB += items.find(({ item }) => item.key === key)?.item.size / (1024 * 1024) || 0;
      layer.stats.evictionCount++;
      if (freedMB >= requiredMB) break;
    }
  }

  private isExpired(item: CacheItem<any>): boolean {
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
      // Handle cleanup logic
    }
  }

  private updateStats(layer: CacheLayer,
    operation: "hit" | "miss" | "set" | "delete",
    size?: number): void {
    const stats = layer.stats;
    switch (operation) {
      case "hit":
        stats.hits++;
        stats.totalHits++;
        break;
      case "miss":
        stats.misses++;
        stats.totalMisses++;
        break;
      case "set":
        stats.totalItems++;
        if (size) stats.totalSize += size;
        break;
      case "delete":
        stats.totalItems = Math.max(0, stats.totalItems - 1);
        if (size) stats.totalSize = Math.max(0, stats.totalSize - size);
        break;
    }
    stats.hitRate = (stats.hits + stats.misses) > 0 ? stats.hits / (stats.hits + stats.misses) : 0;
    stats.memoryUsage = stats.totalSize / (1024 * 1024);
  }

  private resetStats(layer: CacheLayer): void {
    layer.stats = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      totalItems: 0,
      totalSize: 0,
      memoryUsage: 0,
      totalHits: 0,
      totalMisses: 0,
      evictionCount: 0
    };
  }

  private calculateSize(value: unknown): number {
    try {
      return JSON.stringify(value).length * 2; // 粗略估算字节数
    } catch {
      return 0;
    }
  }

  private async serializeValue(value: unknown,
    compression?: boolean): Promise<any> {
    if (!compression) {
      return value;
    }
    // 这里可以实现压缩逻辑
    return value;
  }

  private async deserializeValue(value: unknown,
    compression?: boolean): Promise<any> {
    if (!compression) {
      return value;
    }
    // 这里可以实现解压缩逻辑
    return value;
  }

  private setupDefaultLayers(): void {
    // 内存缓存层 - 用于频繁访问的数据
    this.createLayer("memory", {
      type: CacheType.MEMORY,
      strategy: CacheStrategy.LRU,
      maxSize: 1000,
      maxMemory: 50 * 1024 * 1024, // 50MB
      defaultTTL: 5 * 60 * 1000,  // 5分钟
      cleanupInterval: 60 * 1000,  // 1分钟清理一次
    });

    // 本地存储缓存层 - 用于持久化数据
    this.createLayer("localStorage", {
      type: CacheType.LOCAL_STORAGE,
      strategy: CacheStrategy.TTL,
      maxSize: 500,
      defaultTTL: 24 * 60 * 60 * 1000, // 24小时
      cleanupInterval: 10 * 60 * 1000,  // 10分钟清理一次
    });

    // 会话存储缓存层 - 用于会话期间的数据
    this.createLayer("sessionStorage", {
      type: CacheType.SESSION_STORAGE,
      strategy: CacheStrategy.FIFO,
      maxSize: 200,
      defaultTTL: 30 * 60 * 1000, // 30分钟
      cleanupInterval: 5 * 60 * 1000,  // 5分钟清理一次
    });
  }

  private startGlobalCleanup(): void {
    setInterval(() => {
      for (const layerName of this.layers.keys()) {
        this.cleanupLayer(layerName);
      }
    }, 60 * 60 * 1000); // 1小时
  }

  private async compressData(data: any): Promise<any> {
    // 这里应该实现真正的压缩逻辑
    return data;
  }

  private async decompressData(data: any): Promise<any> {
    // 这里应该实现真正的解压缩逻辑
    return data;
  }

  private async encryptData(data: any): Promise<any> {
    // 这里应该实现真正的加密逻辑
    return data;
  }

  private async decryptData(data: any): Promise<any> {
    // 这里应该实现真正的解密逻辑
    return data;
  }

  private async persistItem(item: CacheItem<any>): Promise<void> {
    // 这里应该实现持久化存储逻辑
  }

  private async loadFromPersistent(key: string): Promise<CacheItem<any> | null> {
    // 这里应该实现从持久化存储加载的逻辑
    return null;
  }

  private async deleteFromPersistent(key: string): Promise<void> {
    // 这里应该实现从持久化存储删除的逻辑
  }

  private async clearPersistent(): Promise<void> {
    // 这里应该实现清空持久化存储的逻辑
  }

  public destroy(): void {
    if (this.cleanupIntervals.size > 0) {
      for (const interval of this.cleanupIntervals.values()) {
        clearInterval(interval);
      }
      this.cleanupIntervals.clear();
    }
    this.layers.clear();
  }
}

export default CacheManager;