import Redis from 'ioredis';
import config from '../../config';
import logger from '../logger';

export interface CacheOptions {
  ttl?: number;        // 缓存过期时间（秒）
  prefix?: string;     // 缓存键前缀
}

export class RedisCache {
  private static instance: RedisCache;
  private client: Redis;
  private readonly defaultTTL: number = 3600; // 默认1小时
  private readonly defaultPrefix: string = 'kg:';

  private constructor() {
    this.client = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      password: config.redis.password,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      }
    });

    this.client.on('error', (error) => {
      logger.error('Redis连接错误:', error);
    });

    this.client.on('connect', () => {
      logger.info('Redis连接成功');
    });
  }

  public static getInstance(): RedisCache {
    if (!RedisCache.instance) {
      RedisCache.instance = new RedisCache();
    }
    return RedisCache.instance;
  }

  private generateKey(key: string, prefix?: string): string {
    const finalPrefix = prefix || this.defaultPrefix;
    return `${finalPrefix}${key}`;
  }

  /**
   * 设置缓存
   */
  public async set(key: string, value: any, options?: CacheOptions): Promise<void> {
    try {
      const finalKey = this.generateKey(key, options?.prefix);
      const ttl = options?.ttl || this.defaultTTL;
      const serializedValue = JSON.stringify(value);

      await this.client.setex(finalKey, ttl, serializedValue);
    } catch (error) {
      logger.error('设置缓存失败:', error);
      throw error;
    }
  }

  /**
   * 获取缓存
   */
  public async get<T>(key: string, prefix?: string): Promise<T | null> {
    try {
      const finalKey = this.generateKey(key, prefix);
      const value = await this.client.get(finalKey);

      if (!value) {
        return null;
      }

      return JSON.parse(value) as T;
    } catch (error) {
      logger.error('获取缓存失败:', error);
      throw error;
    }
  }

  /**
   * 删除缓存
   */
  public async delete(key: string, prefix?: string): Promise<void> {
    try {
      const finalKey = this.generateKey(key, prefix);
      await this.client.del(finalKey);
    } catch (error) {
      logger.error('删除缓存失败:', error);
      throw error;
    }
  }

  /**
   * 批量设置缓存
   */
  public async mset(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    try {
      const pipeline = this.client.pipeline();
      const ttl = options?.ttl || this.defaultTTL;

      for (const item of items) {
        const finalKey = this.generateKey(item.key, options?.prefix);
        const serializedValue = JSON.stringify(item.value);
        pipeline.setex(finalKey, ttl, serializedValue);
      }

      await pipeline.exec();
    } catch (error) {
      logger.error('批量设置缓存失败:', error);
      throw error;
    }
  }

  /**
   * 批量获取缓存
   */
  public async mget<T>(keys: string[], prefix?: string): Promise<Array<T | null>> {
    try {
      const finalKeys = keys.map(key => this.generateKey(key, prefix));
      const values = await this.client.mget(finalKeys);

      return values.map(value => {
        if (!value) {
          return null;
        }
        return JSON.parse(value) as T;
      });
    } catch (error) {
      logger.error('批量获取缓存失败:', error);
      throw error;
    }
  }

  /**
   * 缓存预热
   */
  public async warmup(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    try {
      await this.mset(items, options);
      logger.info(`缓存预热完成，共${items.length}条数据`);
    } catch (error) {
      logger.error('缓存预热失败:', error);
      throw error;
    }
  }

  /**
   * 清除指定前缀的所有缓存
   */
  public async clearByPrefix(prefix: string): Promise<void> {
    try {
      const pattern = this.generateKey('*', prefix);
      const keys = await this.client.keys(pattern);
      
      if (keys.length > 0) {
        await this.client.del(...keys);
      }
      
      logger.info(`清除前缀${prefix}的缓存完成，共${keys.length}条`);
    } catch (error) {
      logger.error('清除缓存失败:', error);
      throw error;
    }
  }

  /**
   * 获取缓存统计信息
   */
  public async getStats(): Promise<{
    totalKeys: number;
    memoryUsage: number;
    hitRate: number;
  }> {
    try {
      const info = await this.client.info();
      const memory = await this.client.info('memory');
      
      // 解析Redis INFO命令返回的信息
      const keyspace = info.split('\n').find(line => line.startsWith('keyspace_hits'));
      const hits = parseInt(keyspace?.split(':')[1] || '0');
      const misses = parseInt(info.split('\n').find(line => line.startsWith('keyspace_misses'))?.split(':')[1] || '0');
      const hitRate = hits / (hits + misses) || 0;

      return {
        totalKeys: parseInt(info.split('\n').find(line => line.startsWith('db0'))?.split('=')[1] || '0'),
        memoryUsage: parseInt(memory.split('\n').find(line => line.startsWith('used_memory'))?.split(':')[1] || '0'),
        hitRate
      };
    } catch (error) {
      logger.error('获取缓存统计信息失败:', error);
      throw error;
    }
  }
}