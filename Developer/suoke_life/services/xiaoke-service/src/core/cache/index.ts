import Redis from 'ioredis';
import { logger } from '../../utils/logger';

let redisClient: Redis | null = null;

/**
 * 设置Redis客户端
 */
export const setupRedisClient = async (): Promise<Redis> => {
  try {
    if (redisClient) {
      return redisClient;
    }

    // 获取Redis连接配置
    const host = process.env.REDIS_HOST || 'localhost';
    const port = parseInt(process.env.REDIS_PORT || '6379', 10);
    const password = process.env.REDIS_PASSWORD || undefined;

    // 创建Redis客户端
    redisClient = new Redis({
      host,
      port,
      password,
      lazyConnect: true,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        logger.info(`Redis重连延迟: ${delay}ms`);
        return delay;
      }
    });

    // 连接Redis
    await redisClient.connect();

    // 设置事件监听器
    redisClient.on('connect', () => {
      logger.info('Redis连接已建立');
    });

    redisClient.on('ready', () => {
      logger.info('Redis服务器已就绪');
    });

    redisClient.on('error', (err) => {
      logger.error('Redis错误:', err);
    });

    redisClient.on('close', () => {
      logger.warn('Redis连接已关闭');
    });

    redisClient.on('reconnecting', () => {
      logger.info('正在重新连接到Redis...');
    });

    return redisClient;
  } catch (error) {
    logger.error('Redis连接失败:', error);
    throw error;
  }
};

/**
 * 获取Redis客户端实例
 */
export const getRedisClient = (): Redis => {
  if (!redisClient) {
    throw new Error('Redis客户端未初始化');
  }
  return redisClient;
};

/**
 * 关闭Redis连接
 */
export const closeRedisConnection = async (): Promise<void> => {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
    logger.info('Redis连接已关闭');
  }
};

/**
 * 缓存帮助函数
 */

/**
 * 设置缓存
 */
export const setCache = async (key: string, value: any, ttl?: number): Promise<void> => {
  try {
    const client = getRedisClient();
    const serializedValue = JSON.stringify(value);
    
    if (ttl) {
      await client.set(key, serializedValue, 'EX', ttl);
    } else {
      await client.set(key, serializedValue);
    }
  } catch (error) {
    logger.error(`设置缓存[${key}]失败:`, error);
    throw error;
  }
};

/**
 * 获取缓存
 */
export const getCache = async <T>(key: string): Promise<T | null> => {
  try {
    const client = getRedisClient();
    const value = await client.get(key);
    
    if (!value) {
      return null;
    }
    
    return JSON.parse(value) as T;
  } catch (error) {
    logger.error(`获取缓存[${key}]失败:`, error);
    return null;
  }
};

/**
 * 删除缓存
 */
export const deleteCache = async (key: string): Promise<void> => {
  try {
    const client = getRedisClient();
    await client.del(key);
  } catch (error) {
    logger.error(`删除缓存[${key}]失败:`, error);
    throw error;
  }
};

/**
 * 使用模式匹配删除多个缓存
 */
export const deleteCacheByPattern = async (pattern: string): Promise<void> => {
  try {
    const client = getRedisClient();
    const keys = await client.keys(pattern);
    
    if (keys.length > 0) {
      await client.del(...keys);
      logger.info(`已删除${keys.length}个匹配模式[${pattern}]的缓存`);
    }
  } catch (error) {
    logger.error(`删除缓存模式[${pattern}]失败:`, error);
    throw error;
  }
};

export default {
  setup: setupRedisClient,
  getClient: getRedisClient,
  close: closeRedisConnection,
  set: setCache,
  get: getCache,
  delete: deleteCache,
  deleteByPattern: deleteCacheByPattern
}; 