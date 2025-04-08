import { CacheFactory, CacheType } from './CacheFactory';
import { ICache, CacheOptions, CacheStats } from './ICache';
import logger from '../logger';

export class CacheManager {
  private static instance: CacheManager;
  private cache: ICache;

  private constructor() {
    this.cache = CacheFactory.getInstance().getCache(CacheType.REDIS);
  }

  public static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  /**
   * 设置缓存
   */
  public async set(key: string, value: any, options?: CacheOptions): Promise<void> {
    try {
      await this.cache.set(key, value, options);
      logger.debug(`缓存设置成功: ${key}`);
    } catch (error) {
      logger.error(`缓存设置失败: ${key}`, error);
      throw error;
    }
  }

  /**
   * 获取缓存
   */
  public async get<T>(key: string, prefix?: string): Promise<T | null> {
    try {
      const result = await this.cache.get<T>(key, prefix);
      logger.debug(`缓存获取${result ? '成功' : '未命中'}: ${key}`);
      return result;
    } catch (error) {
      logger.error(`缓存获取失败: ${key}`, error);
      throw error;
    }
  }

  /**
   * 删除缓存
   */
  public async delete(key: string, prefix?: string): Promise<void> {
    try {
      await this.cache.delete(key, prefix);
      logger.debug(`缓存删除成功: ${key}`);
    } catch (error) {
      logger.error(`缓存删除失败: ${key}`, error);
      throw error;
    }
  }

  /**
   * 批量设置缓存
   */
  public async mset(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    try {
      await this.cache.mset(items, options);
      logger.debug(`批量缓存设置成功: ${items.length}条`);
    } catch (error) {
      logger.error('批量缓存设置失败', error);
      throw error;
    }
  }

  /**
   * 批量获取缓存
   */
  public async mget<T>(keys: string[], prefix?: string): Promise<Array<T | null>> {
    try {
      const results = await this.cache.mget<T>(keys, prefix);
      const hitCount = results.filter(r => r !== null).length;
      logger.debug(`批量缓存获取完成: ${hitCount}/${keys.length}命中`);
      return results;
    } catch (error) {
      logger.error('批量缓存获取失败', error);
      throw error;
    }
  }

  /**
   * 缓存预热
   */
  public async warmup(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    try {
      await this.cache.warmup(items, options);
      logger.info(`缓存预热完成: ${items.length}条数据`);
    } catch (error) {
      logger.error('缓存预热失败', error);
      throw error;
    }
  }

  /**
   * 清除指定前缀的缓存
   */
  public async clearByPrefix(prefix: string): Promise<void> {
    try {
      await this.cache.clearByPrefix(prefix);
      logger.info(`前缀${prefix}的缓存已清除`);
    } catch (error) {
      logger.error(`清除前缀${prefix}的缓存失败`, error);
      throw error;
    }
  }

  /**
   * 获取缓存统计信息
   */
  public async getStats(): Promise<CacheStats> {
    try {
      const stats = await this.cache.getStats();
      logger.debug('缓存统计信息获取成功', stats);
      return stats;
    } catch (error) {
      logger.error('获取缓存统计信息失败', error);
      throw error;
    }
  }

  /**
   * 健康检查
   */
  public async healthCheck(): Promise<boolean> {
    try {
      const testKey = 'health_check';
      const testValue = { timestamp: Date.now() };
      
      await this.set(testKey, testValue, { ttl: 5 });
      const result = await this.get(testKey);
      
      return result !== null;
    } catch (error) {
      logger.error('缓存健康检查失败', error);
      return false;
    }
  }
}