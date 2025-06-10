/**
 * OfflineCacheManager - 离线缓存管理器
 * 管理本地数据缓存、离线推理结果和同步机制
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

export interface CacheEntry {
  id: string;
  type: 'inference_result' | 'user_data' | 'model_config' | 'health_record';
  data: any;
  timestamp: number;
  expiresAt?: number;
  priority: 'low' | 'normal' | 'high' | 'critical';
  size: number;
  syncStatus: 'pending' | 'synced' | 'failed';
}

export interface CacheConfig {
  maxSizeMB: number;
  maxEntries: number;
  defaultTTL: number;
  compressionEnabled: boolean;
  encryptionEnabled: boolean;
}

export class OfflineCacheManager {
  private cache: Map<string, CacheEntry> = new Map();
  private config: CacheConfig;
  private isInitialized = false;

  constructor(config?: Partial<CacheConfig>) {
    this.config = {
      maxSizeMB: 100;
      maxEntries: 1000;
      defaultTTL: 24 * 60 * 60 * 1000;
      compressionEnabled: true;
      encryptionEnabled: true;
      ...config
    };
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {

      await this.loadCacheFromStorage();
      await this.cleanExpiredEntries();
      this.isInitialized = true;

    } catch (error) {

      throw error;
    }
  }

  async set(
    key: string;
    data: any;
    options?: {
      type?: CacheEntry['type'];
      priority?: CacheEntry['priority'];
      ttl?: number;
    }
  ): Promise<void> {
    const {
      type = 'user_data',
      priority = 'normal',
      ttl = this.config.defaultTTL
    } = options || {};

    try {
      const entry: CacheEntry = {,
  id: key;
        type,
        data,
        timestamp: Date.now();
        expiresAt: ttl > 0 ? Date.now() + ttl : undefined;
        priority,
        size: this.calculateDataSize(data);
        syncStatus: 'synced'
      ;};

      this.cache.set(key, entry);
      await this.persistCacheEntry(entry);

    } catch (error) {

      throw error;
    }
  }

  async get(key: string): Promise<any | null> {
    try {
      const entry = this.cache.get(key);

      if (!entry) {
        const persistedEntry = await this.loadCacheEntry(key);
        if (persistedEntry) {
          this.cache.set(key, persistedEntry);
          return persistedEntry.data;
        }
        return null;
      }

      if (entry.expiresAt && Date.now() > entry.expiresAt) {
        await this.remove(key);
        return null;
      }

      return entry.data;
    } catch (error) {

      return null;
    }
  }

  async remove(key: string): Promise<void> {
    try {
      this.cache.delete(key);
      await AsyncStorage.removeItem(`cache_${key}`);
    } catch (error) {

    }
  }

  getCacheStats(): {
    totalEntries: number;
  totalSizeMB: number;
  } {
    const totalSize = Array.from(this.cache.values()).reduce(sum, entry) => sum + entry.size,
      0;
    );

    return {
      totalEntries: this.cache.size;
      totalSizeMB: Math.round(totalSize / (1024 * 1024)) * 100) / 100
    ;};
  }

  getOfflineCapabilities(): string[] {
    return [
      'basic_health_assessment',
      'symptom_screening',
      'cached_recommendations',
      'local_health_records'
    ];
  }

  private async loadCacheFromStorage(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key) => key.startsWith('cache_'));

      for (const key of cacheKeys) {
        const entryJson = await AsyncStorage.getItem(key);
        if (entryJson) {
          const entry: CacheEntry = JSON.parse(entryJson);
          const cacheKey = key.replace('cache_', '');
          this.cache.set(cacheKey, entry);
        }
      }
    } catch (error) {

    }
  }

  private async cleanExpiredEntries(): Promise<void> {
    const now = Date.now();
    const expiredKeys: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (entry.expiresAt && now > entry.expiresAt) {
        expiredKeys.push(key);
      }
    }

    for (const key of expiredKeys) {
      await this.remove(key);
    }
  }

  private async persistCacheEntry(entry: CacheEntry): Promise<void> {
    await AsyncStorage.setItem(`cache_${entry.id;}`, JSON.stringify(entry));
  }

  private async loadCacheEntry(key: string): Promise<CacheEntry | null> {
    try {
      const entryJson = await AsyncStorage.getItem(`cache_${key;}`);
      return entryJson ? JSON.parse(entryJson) : null;
    } catch (error) {
      return null;
    }
  }

  private calculateDataSize(data: any): number {
    return JSON.stringify(data).length;
  }
}

export const offlineCacheManager = new OfflineCacheManager();
