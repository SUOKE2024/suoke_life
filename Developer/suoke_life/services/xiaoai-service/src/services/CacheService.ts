/**
 * 缓存服务
 * 基于Redis的数据缓存和会话管理服务
 */
import { createClient, RedisClientType, RedisClientOptions } from 'redis';
import { logger } from '../index';

export interface ICacheService {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  set(key: string, value: any, expireSeconds?: number): Promise<void>;
  get<T>(key: string): Promise<T | null>;
  del(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
  expire(key: string, seconds: number): Promise<void>;
  ttl(key: string): Promise<number>;
  incr(key: string): Promise<number>;
  hset(key: string, field: string, value: any): Promise<void>;
  hget<T>(key: string, field: string): Promise<T | null>;
  hgetall<T>(key: string): Promise<Record<string, T> | null>;
  hdel(key: string, field: string): Promise<void>;
  flush(): Promise<void>;
}

export class CacheService implements ICacheService {
  private client: RedisClientType;
  private isConnected: boolean = false;
  
  constructor(options?: RedisClientOptions) {
    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
    
    this.client = createClient({
      url: redisUrl,
      ...options
    });
    
    this.client.on('error', (err) => {
      logger.error('Redis错误:', err);
    });
    
    this.client.on('connect', () => {
      this.isConnected = true;
      logger.info('Redis已连接');
    });
    
    this.client.on('disconnect', () => {
      this.isConnected = false;
      logger.warn('Redis连接已断开');
    });
  }
  
  async connect(): Promise<void> {
    if (!this.isConnected) {
      try {
        await this.client.connect();
      } catch (error) {
        logger.error('Redis连接失败:', error);
        throw error;
      }
    }
  }
  
  async disconnect(): Promise<void> {
    if (this.isConnected) {
      await this.client.disconnect();
      this.isConnected = false;
    }
  }
  
  async set(key: string, value: any, expireSeconds?: number): Promise<void> {
    try {
      const serializedValue = JSON.stringify(value);
      
      if (expireSeconds) {
        await this.client.setEx(key, expireSeconds, serializedValue);
      } else {
        await this.client.set(key, serializedValue);
      }
    } catch (error) {
      logger.error(`Redis SET错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async get<T>(key: string): Promise<T | null> {
    try {
      const value = await this.client.get(key);
      
      if (!value) {
        return null;
      }
      
      return JSON.parse(value) as T;
    } catch (error) {
      logger.error(`Redis GET错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async del(key: string): Promise<void> {
    try {
      await this.client.del(key);
    } catch (error) {
      logger.error(`Redis DEL错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async exists(key: string): Promise<boolean> {
    try {
      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      logger.error(`Redis EXISTS错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async expire(key: string, seconds: number): Promise<void> {
    try {
      await this.client.expire(key, seconds);
    } catch (error) {
      logger.error(`Redis EXPIRE错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async ttl(key: string): Promise<number> {
    try {
      return await this.client.ttl(key);
    } catch (error) {
      logger.error(`Redis TTL错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async incr(key: string): Promise<number> {
    try {
      return await this.client.incr(key);
    } catch (error) {
      logger.error(`Redis INCR错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async hset(key: string, field: string, value: any): Promise<void> {
    try {
      const serializedValue = JSON.stringify(value);
      await this.client.hSet(key, field, serializedValue);
    } catch (error) {
      logger.error(`Redis HSET错误 (key: ${key}, field: ${field}):`, error);
      throw error;
    }
  }
  
  async hget<T>(key: string, field: string): Promise<T | null> {
    try {
      const value = await this.client.hGet(key, field);
      
      if (!value) {
        return null;
      }
      
      return JSON.parse(value) as T;
    } catch (error) {
      logger.error(`Redis HGET错误 (key: ${key}, field: ${field}):`, error);
      throw error;
    }
  }
  
  async hgetall<T>(key: string): Promise<Record<string, T> | null> {
    try {
      const result = await this.client.hGetAll(key);
      
      if (!result || Object.keys(result).length === 0) {
        return null;
      }
      
      // 对所有值进行反序列化
      const deserialized: Record<string, T> = {};
      
      for (const [field, value] of Object.entries(result)) {
        deserialized[field] = JSON.parse(value) as T;
      }
      
      return deserialized;
    } catch (error) {
      logger.error(`Redis HGETALL错误 (key: ${key}):`, error);
      throw error;
    }
  }
  
  async hdel(key: string, field: string): Promise<void> {
    try {
      await this.client.hDel(key, field);
    } catch (error) {
      logger.error(`Redis HDEL错误 (key: ${key}, field: ${field}):`, error);
      throw error;
    }
  }
  
  async flush(): Promise<void> {
    try {
      await this.client.flushAll();
    } catch (error) {
      logger.error('Redis FLUSHALL错误:', error);
      throw error;
    }
  }
} 