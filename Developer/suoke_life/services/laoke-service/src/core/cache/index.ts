import Redis from 'ioredis';
import { promisify } from 'util';
import logger from '../utils/logger';

let redisClient: Redis.Redis;

/**
 * 连接Redis缓存
 */
export const connectRedis = async () => {
  try {
    // 创建Redis连接
    redisClient = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD || undefined,
      db: parseInt(process.env.REDIS_DB || '0'),
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      }
    });
    
    // 监听连接事件
    redisClient.on('connect', () => {
      logger.info('Redis缓存连接成功');
    });
    
    // 监听错误事件
    redisClient.on('error', (err) => {
      logger.error('Redis缓存错误:', err);
    });
    
    // 监听重连事件
    redisClient.on('reconnecting', () => {
      logger.warn('正在重新连接Redis缓存...');
    });
    
    // 等待连接就绪
    await redisClient.ping();
    
    return redisClient;
  } catch (error) {
    logger.error('连接Redis缓存失败:', error);
    throw error;
  }
};

/**
 * 关闭Redis连接
 */
export const disconnectRedis = async () => {
  if (redisClient) {
    await redisClient.quit();
    logger.info('Redis缓存连接已关闭');
  }
};

/**
 * 获取Redis客户端
 */
export const getRedisClient = () => {
  if (!redisClient) {
    throw new Error('Redis客户端未初始化');
  }
  return redisClient;
};

/**
 * 获取数据
 */
export const get = async (key: string) => {
  try {
    const result = await redisClient.get(key);
    return result ? JSON.parse(result) : null;
  } catch (error) {
    logger.error(`获取Redis缓存错误 [键: ${key}]:`, error);
    return null;
  }
};

/**
 * 设置数据
 */
export const set = async (key: string, value: any, ttlSeconds?: number) => {
  try {
    const serializedValue = JSON.stringify(value);
    
    if (ttlSeconds) {
      await redisClient.set(key, serializedValue, 'EX', ttlSeconds);
    } else {
      await redisClient.set(key, serializedValue);
    }
    
    return true;
  } catch (error) {
    logger.error(`设置Redis缓存错误 [键: ${key}]:`, error);
    return false;
  }
};

/**
 * 删除数据
 */
export const del = async (key: string) => {
  try {
    await redisClient.del(key);
    return true;
  } catch (error) {
    logger.error(`删除Redis缓存错误 [键: ${key}]:`, error);
    return false;
  }
};

/**
 * 设置缓存，如果不存在
 */
export const setNX = async (key: string, value: any, ttlSeconds: number) => {
  try {
    const serializedValue = JSON.stringify(value);
    const result = await redisClient.set(key, serializedValue, 'NX', 'EX', ttlSeconds);
    return result === 'OK';
  } catch (error) {
    logger.error(`设置NX Redis缓存错误 [键: ${key}]:`, error);
    return false;
  }
};

/**
 * 获取锁
 */
export const acquireLock = async (key: string, ttlSeconds: number) => {
  const lockValue = Date.now().toString();
  const acquired = await setNX(`lock:${key}`, lockValue, ttlSeconds);
  
  if (acquired) {
    return lockValue;
  }
  
  return null;
};

/**
 * 释放锁
 */
export const releaseLock = async (key: string, value: string) => {
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;
  
  try {
    const result = await redisClient.eval(script, 1, `lock:${key}`, value);
    return result === 1;
  } catch (error) {
    logger.error(`释放Redis锁错误 [键: ${key}]:`, error);
    return false;
  }
}; 