import AsyncStorage from '@react-native-async-storage/async-storage';
import { FiveDiagnosisInput, FiveDiagnosisResult } from './fiveDiagnosisService';

// 缓存键前缀
const CACHE_PREFIX = 'diagnosis_cache_';
const SESSION_PREFIX = 'diagnosis_session_';
const RESULT_PREFIX = 'diagnosis_result_';

// 缓存配置
interface CacheConfig {
  maxAge: number; // 最大缓存时间（毫秒）
  maxSize: number; // 最大缓存条目数
  compressionEnabled: boolean; // 是否启用压缩
}

// 缓存条目
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
  size: number;
  accessCount: number;
  lastAccessed: number;
}

// 诊断会话缓存
interface DiagnosisSessionCache {
  sessionId: string;
  userId: string;
  startTime: number;
  lastUpdateTime: number;
  currentStep: string;
  collectedData: Partial<FiveDiagnosisInput>;
  isCompleted: boolean;
}

// 诊断结果缓存
interface DiagnosisResultCache {
  resultId: string;
  sessionId: string;
  userId: string;
  result: FiveDiagnosisResult;
  createdAt: number;
  isSynced: boolean;
}

export class DiagnosisCacheManager {
  private config: CacheConfig;
  private memoryCache: Map<string, CacheEntry<any>>;
  private cacheStats: {
    hits: number;
    misses: number;
    evictions: number;
    totalSize: number;
  };

  constructor(config?: Partial<CacheConfig>) {
    this.config = {
      maxAge: 24 * 60 * 60 * 1000, // 24小时
      maxSize: 100, // 最多100个条目
      compressionEnabled: true,
      ...config
    };

    this.memoryCache = new Map();
    this.cacheStats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalSize: 0
    };

    // 定期清理过期缓存
    this.startCleanupTimer();
  }

  // 保存诊断会话
  async saveSession(session: DiagnosisSessionCache): Promise<void> {
    try {
      const key = `${SESSION_PREFIX}${session.sessionId}`;
      const cacheEntry: CacheEntry<DiagnosisSessionCache> = {
        data: session,
        timestamp: Date.now(),
        expiresAt: Date.now() + this.config.maxAge,
        size: this.calculateSize(session),
        accessCount: 1,
        lastAccessed: Date.now()
      };

      // 保存到内存缓存
      this.memoryCache.set(key, cacheEntry);

      // 保存到持久化存储
      await AsyncStorage.setItem(key, JSON.stringify(cacheEntry));

      // 更新统计信息
      this.updateCacheStats();

      console.log(`诊断会话已缓存: ${session.sessionId}`);
    } catch (error) {
      console.error('保存诊断会话失败:', error);
      throw error;
    }
  }

  // 获取诊断会话
  async getSession(sessionId: string): Promise<DiagnosisSessionCache | null> {
    try {
      const key = `${SESSION_PREFIX}${sessionId}`;

      // 先从内存缓存获取
      let cacheEntry = this.memoryCache.get(key);

      if (!cacheEntry) {
        // 从持久化存储获取
        const stored = await AsyncStorage.getItem(key);
        if (stored) {
          cacheEntry = JSON.parse(stored);
          // 重新加载到内存缓存
          if (cacheEntry && !this.isExpired(cacheEntry)) {
            this.memoryCache.set(key, cacheEntry);
          }
        }
      }

      if (!cacheEntry || this.isExpired(cacheEntry)) {
        this.cacheStats.misses++;
        return null;
      }

      // 更新访问统计
      cacheEntry.accessCount++;
      cacheEntry.lastAccessed = Date.now();
      this.cacheStats.hits++;

      return cacheEntry.data;
    } catch (error) {
      console.error('获取诊断会话失败:', error);
      this.cacheStats.misses++;
      return null;
    }
  }

  // 保存诊断结果
  async saveResult(result: DiagnosisResultCache): Promise<void> {
    try {
      const key = `${RESULT_PREFIX}${result.resultId}`;
      const cacheEntry: CacheEntry<DiagnosisResultCache> = {
        data: result,
        timestamp: Date.now(),
        expiresAt: Date.now() + this.config.maxAge * 7, // 结果保存7天
        size: this.calculateSize(result),
        accessCount: 1,
        lastAccessed: Date.now()
      };

      // 保存到内存缓存
      this.memoryCache.set(key, cacheEntry);

      // 保存到持久化存储
      await AsyncStorage.setItem(key, JSON.stringify(cacheEntry));

      // 更新统计信息
      this.updateCacheStats();

      console.log(`诊断结果已缓存: ${result.resultId}`);
    } catch (error) {
      console.error('保存诊断结果失败:', error);
      throw error;
    }
  }

  // 获取诊断结果
  async getResult(resultId: string): Promise<DiagnosisResultCache | null> {
    try {
      const key = `${RESULT_PREFIX}${resultId}`;

      // 先从内存缓存获取
      let cacheEntry = this.memoryCache.get(key);

      if (!cacheEntry) {
        // 从持久化存储获取
        const stored = await AsyncStorage.getItem(key);
        if (stored) {
          cacheEntry = JSON.parse(stored);
          // 重新加载到内存缓存
          if (cacheEntry && !this.isExpired(cacheEntry)) {
            this.memoryCache.set(key, cacheEntry);
          }
        }
      }

      if (!cacheEntry || this.isExpired(cacheEntry)) {
        this.cacheStats.misses++;
        return null;
      }

      // 更新访问统计
      cacheEntry.accessCount++;
      cacheEntry.lastAccessed = Date.now();
      this.cacheStats.hits++;

      return cacheEntry.data;
    } catch (error) {
      console.error('获取诊断结果失败:', error);
      this.cacheStats.misses++;
      return null;
    }
  }

  // 获取用户的所有诊断结果
  async getUserResults(userId: string): Promise<DiagnosisResultCache[]> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const resultKeys = keys.filter(key => key.startsWith(RESULT_PREFIX));
      
      const results: DiagnosisResultCache[] = [];
      
      for (const key of resultKeys) {
        const stored = await AsyncStorage.getItem(key);
        if (stored) {
          const cacheEntry: CacheEntry<DiagnosisResultCache> = JSON.parse(stored);
          if (!this.isExpired(cacheEntry) && cacheEntry.data.userId === userId) {
            results.push(cacheEntry.data);
          }
        }
      }

      // 按创建时间倒序排列
      return results.sort((a, b) => b.createdAt - a.createdAt);
    } catch (error) {
      console.error('获取用户诊断结果失败:', error);
      return [];
    }
  }

  // 删除会话
  async deleteSession(sessionId: string): Promise<void> {
    try {
      const key = `${SESSION_PREFIX}${sessionId}`;
      
      // 从内存缓存删除
      this.memoryCache.delete(key);
      
      // 从持久化存储删除
      await AsyncStorage.removeItem(key);
      
      console.log(`诊断会话已删除: ${sessionId}`);
    } catch (error) {
      console.error('删除诊断会话失败:', error);
    }
  }

  // 删除结果
  async deleteResult(resultId: string): Promise<void> {
    try {
      const key = `${RESULT_PREFIX}${resultId}`;
      
      // 从内存缓存删除
      this.memoryCache.delete(key);
      
      // 从持久化存储删除
      await AsyncStorage.removeItem(key);
      
      console.log(`诊断结果已删除: ${resultId}`);
    } catch (error) {
      console.error('删除诊断结果失败:', error);
    }
  }

  // 清理过期缓存
  async cleanupExpiredCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => 
        key.startsWith(SESSION_PREFIX) || 
        key.startsWith(RESULT_PREFIX)
      );

      let cleanedCount = 0;

      for (const key of cacheKeys) {
        const stored = await AsyncStorage.getItem(key);
        if (stored) {
          const cacheEntry: CacheEntry<any> = JSON.parse(stored);
          if (this.isExpired(cacheEntry)) {
            await AsyncStorage.removeItem(key);
            this.memoryCache.delete(key);
            cleanedCount++;
          }
        }
      }

      console.log(`清理了 ${cleanedCount} 个过期缓存条目`);
    } catch (error) {
      console.error('清理过期缓存失败:', error);
    }
  }

  // 清空所有缓存
  async clearAllCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => 
        key.startsWith(SESSION_PREFIX) || 
        key.startsWith(RESULT_PREFIX)
      );

      await AsyncStorage.multiRemove(cacheKeys);
      this.memoryCache.clear();

      // 重置统计信息
      this.cacheStats = {
        hits: 0,
        misses: 0,
        evictions: 0,
        totalSize: 0
      };

      console.log('所有诊断缓存已清空');
    } catch (error) {
      console.error('清空缓存失败:', error);
    }
  }

  // 获取缓存统计信息
  getCacheStats() {
    const hitRate = this.cacheStats.hits + this.cacheStats.misses > 0 
      ? this.cacheStats.hits / (this.cacheStats.hits + this.cacheStats.misses) 
      : 0;

    return {
      ...this.cacheStats,
      hitRate: Math.round(hitRate * 100),
      memoryEntries: this.memoryCache.size
    };
  }

  // 获取缓存大小信息
  async getCacheSizeInfo() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => 
        key.startsWith(SESSION_PREFIX) || 
        key.startsWith(RESULT_PREFIX)
      );

      let totalSize = 0;
      let sessionCount = 0;
      let resultCount = 0;

      for (const key of cacheKeys) {
        const stored = await AsyncStorage.getItem(key);
        if (stored) {
          totalSize += stored.length;
          if (key.startsWith(SESSION_PREFIX)) {
            sessionCount++;
          } else if (key.startsWith(RESULT_PREFIX)) {
            resultCount++;
          }
        }
      }

      return {
        totalSize,
        sessionCount,
        resultCount,
        memorySize: this.cacheStats.totalSize
      };
    } catch (error) {
      console.error('获取缓存大小信息失败:', error);
      return {
        totalSize: 0,
        sessionCount: 0,
        resultCount: 0,
        memorySize: 0
      };
    }
  }

  // 私有方法：检查是否过期
  private isExpired(cacheEntry: CacheEntry<any>): boolean {
    return Date.now() > cacheEntry.expiresAt;
  }

  // 私有方法：计算数据大小
  private calculateSize(data: any): number {
    try {
      return JSON.stringify(data).length;
    } catch {
      return 0;
    }
  }

  // 私有方法：更新缓存统计
  private updateCacheStats(): void {
    this.cacheStats.totalSize = Array.from(this.memoryCache.values())
      .reduce((total, entry) => total + entry.size, 0);

    // 如果超过最大大小，执行LRU清理
    if (this.memoryCache.size > this.config.maxSize) {
      this.evictLRU();
    }
  }

  // 私有方法：LRU清理
  private evictLRU(): void {
    const entries = Array.from(this.memoryCache.entries());
    
    // 按最后访问时间排序
    entries.sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);
    
    // 删除最久未访问的条目
    const toEvict = entries.slice(0, entries.length - this.config.maxSize + 1);
    
    for (const [key] of toEvict) {
      this.memoryCache.delete(key);
      this.cacheStats.evictions++;
    }
  }

  // 私有方法：启动清理定时器
  private startCleanupTimer(): void {
    // 每小时清理一次过期缓存
    setInterval(() => {
      this.cleanupExpiredCache();
    }, 60 * 60 * 1000);
  }
}

// 单例实例
export const diagnosisCacheManager = new DiagnosisCacheManager(); 