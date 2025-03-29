/**
 * Redis服务单元测试
 */
import { jest } from '@jest/globals';
import Redis from 'ioredis';
import { RedisService } from '../../../src/services/redis-service';

// 模拟ioredis
jest.mock('ioredis');

// 模拟logger
jest.mock('../../../src/utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
}));

describe('Redis服务', () => {
  let redisService: RedisService;
  let mockRedisClient: any;
  
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 模拟Redis客户端
    mockRedisClient = {
      quit: jest.fn().mockImplementation(() => Promise.resolve()),
      on: jest.fn(),
    };
    
    // 模拟Redis构造函数
    (Redis as any).mockImplementation(() => mockRedisClient);
    
    // 创建Redis服务实例
    redisService = new RedisService(mockRedisClient);
  });
  
  describe('RedisService类', () => {
    it('应正确初始化', () => {
      expect(redisService).toBeDefined();
    });
    
    it('getClient应返回Redis客户端', () => {
      const client = redisService.getClient();
      expect(client).toBe(mockRedisClient);
    });
    
    it('当客户端未初始化时getClient应抛出错误', () => {
      // 创建一个client为null的实例
      const nullRedisService = new RedisService(null);
      
      expect(() => {
        nullRedisService.getClient();
      }).toThrow('Redis客户端未初始化');
    });
    
    it('close应正确关闭连接', async () => {
      await redisService.close();
      
      expect(mockRedisClient.quit).toHaveBeenCalled();
    });
    
    it('close应处理client为null的情况', async () => {
      // 创建一个client为null的实例
      const nullRedisService = new RedisService(null);
      
      // 不应抛出错误
      await expect(nullRedisService.close()).resolves.not.toThrow();
    });
  });
}); 