/**
 * Redis服务
 */
import Redis from 'ioredis';
import logger from '../utils/logger';

// Redis客户端实例
let redisClient: Redis | null = null;

/**
 * Redis服务类 - 提供Redis操作接口
 */
export class RedisService {
  private client: Redis | null = null;
  
  /**
   * 初始化Redis服务
   */
  constructor(client?: Redis) {
    // 允许注入Redis客户端，方便测试
    this.client = client || redisClient;
  }
  
  /**
   * 获取Redis客户端实例
   */
  getClient(): Redis {
    if (!this.client) {
      throw new Error('Redis客户端未初始化');
    }
    return this.client;
  }
  
  /**
   * 关闭Redis连接
   */
  async close(): Promise<void> {
    if (this.client) {
      await this.client.quit();
      this.client = null;
    }
  }
}

/**
 * 建立Redis连接
 * @returns 连接成功的Promise
 */
export async function setupRedisConnection(): Promise<void> {
  try {
    // 从环境变量获取Redis配置
    const host = process.env.REDIS_HOST || 'localhost';
    const port = parseInt(process.env.REDIS_PORT || '6379', 10);
    const password = process.env.REDIS_PASSWORD;
    
    // 创建Redis客户端
    redisClient = new Redis({
      host,
      port,
      password,
      retryStrategy: (times) => {
        // 处理重试策略
        if (times > 20) {
          // 超过最大重试次数
          return null; // 停止重试
        }
        
        // 指数退避策略
        return Math.min(times * 500, 5000);
      },
      maxRetriesPerRequest: 3
    });
    
    // 注册事件处理
    redisClient.on('connect', () => {
      logger.info(`Redis连接成功: ${host}:${port}`);
    });
    
    redisClient.on('error', (err) => {
      logger.error(`Redis连接错误: ${err.message}`);
      throw new Error(`Redis连接失败: ${err.message}`);
    });
    
    // 等待连接成功
    return Promise.resolve();
  } catch (error: any) {
    logger.error(`Redis连接设置失败: ${error.message}`);
    throw error;
  }
}

/**
 * 获取Redis客户端实例
 * @returns Redis客户端
 */
export function getRedisClient(): Redis {
  if (!redisClient) {
    throw new Error('Redis客户端未初始化');
  }
  return redisClient;
}

/**
 * 关闭Redis连接
 */
export async function closeRedisConnection(): Promise<void> {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
    logger.info('Redis连接已关闭');
  }
}