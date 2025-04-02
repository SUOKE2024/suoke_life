/**
 * Redis连接工具
 */

import { createClient, RedisClientType } from 'redis';
import logger from './logger';

let redisClient: RedisClientType;

/**
 * 连接到Redis服务器
 */
export const connectToRedis = async (): Promise<void> => {
  const REDIS_HOST = process.env.REDIS_HOST || 'localhost';
  const REDIS_PORT = parseInt(process.env.REDIS_PORT || '6379');
  const REDIS_PASSWORD = process.env.REDIS_PASSWORD;
  const REDIS_DB = parseInt(process.env.REDIS_DB || '0');
  
  const url = REDIS_PASSWORD
    ? `redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}`
    : `redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}`;
  
  try {
    redisClient = createClient({
      url
    });
    
    redisClient.on('error', (err) => {
      logger.error('Redis连接错误', { error: err });
    });
    
    redisClient.on('reconnecting', () => {
      logger.warn('正在重新连接Redis...');
    });
    
    redisClient.on('connect', () => {
      logger.info('Redis连接成功');
    });
    
    await redisClient.connect();
    
  } catch (error) {
    logger.error('Redis连接失败', { error });
    throw error;
  }
};

/**
 * 获取Redis客户端实例
 */
export const getRedisClient = (): RedisClientType => {
  if (!redisClient) {
    throw new Error('Redis客户端尚未初始化');
  }
  return redisClient;
};

/**
 * 关闭Redis连接
 */
export const closeRedisConnection = async (): Promise<void> => {
  if (redisClient) {
    try {
      await redisClient.quit();
      logger.info('Redis连接已关闭');
    } catch (error) {
      logger.error('关闭Redis连接失败', { error });
      throw error;
    }
  }
};