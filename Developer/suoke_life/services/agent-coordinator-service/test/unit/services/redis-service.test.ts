/**
 * Redis服务单元测试
 */
import { jest } from '@jest/globals';
import Redis from 'ioredis';
import { RedisService, setupRedisConnection, getRedisClient, closeRedisConnection } from '../../../src/services/redis-service';

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
  const RedisMock = Redis as jest.MockedClass<typeof Redis>;
  
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 模拟Redis客户端
    mockRedisClient = {
      quit: jest.fn().mockImplementation(() => Promise.resolve()),
      on: jest.fn().mockImplementation((event, callback) => mockRedisClient),
      set: jest.fn().mockImplementation(() => Promise.resolve('OK')),
      get: jest.fn().mockImplementation(() => Promise.resolve('value')),
      exists: jest.fn().mockImplementation(() => Promise.resolve(1)),
      del: jest.fn().mockImplementation(() => Promise.resolve(1))
    };
    
    // 模拟Redis构造函数
    RedisMock.mockImplementation(() => mockRedisClient);
    
    // 创建Redis服务实例
    redisService = new RedisService(mockRedisClient);
    
    // 为全局函数测试准备
    (global as any).redisClient = null;
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
  
  describe('setupRedisConnection', () => {
    beforeEach(() => {
      // 保存原始环境变量
      process.env.REDIS_HOST = 'test-host';
      process.env.REDIS_PORT = '6380';
      process.env.REDIS_PASSWORD = 'test-password';
    });
    
    it('应成功设置Redis连接', async () => {
      await setupRedisConnection();
      
      expect(RedisMock).toHaveBeenCalledWith(expect.objectContaining({
        host: 'test-host',
        port: 6380,
        password: 'test-password'
      }));
      
      expect(mockRedisClient.on).toHaveBeenCalledWith('connect', expect.any(Function));
      expect(mockRedisClient.on).toHaveBeenCalledWith('error', expect.any(Function));
    });
    
    it('应使用默认值当环境变量未设置时', async () => {
      // 清除环境变量
      delete process.env.REDIS_HOST;
      delete process.env.REDIS_PORT;
      delete process.env.REDIS_PASSWORD;
      
      await setupRedisConnection();
      
      expect(RedisMock).toHaveBeenCalledWith(expect.objectContaining({
        host: 'localhost',
        port: 6379,
        password: undefined
      }));
    });
    
    it('应处理Redis连接错误', async () => {
      // 模拟连接错误
      mockRedisClient.on.mockImplementation((event, callback) => {
        if (event === 'error') {
          callback(new Error('连接错误'));
        }
        return mockRedisClient;
      });
      
      await expect(setupRedisConnection()).rejects.toThrow('Redis连接失败');
    });
  });
  
  describe('getRedisClient', () => {
    it('应返回Redis客户端实例', () => {
      // 先设置连接
      (global as any).redisClient = mockRedisClient;
      
      const client = getRedisClient();
      expect(client).toBe(mockRedisClient);
      
      // 清理
      (global as any).redisClient = null;
    });
    
    it('当客户端未初始化时应抛出错误', () => {
      // 确保redisClient为null
      (global as any).redisClient = null;
      
      expect(() => getRedisClient()).toThrow('Redis客户端未初始化');
    });
  });
  
  describe('closeRedisConnection', () => {
    it('应正确关闭Redis连接', async () => {
      // 先设置连接
      (global as any).redisClient = mockRedisClient;
      
      await closeRedisConnection();
      
      expect(mockRedisClient.quit).toHaveBeenCalled();
      expect((global as any).redisClient).toBeNull();
    });
    
    it('当客户端为null时不应抛出错误', async () => {
      // 确保redisClient为null
      (global as any).redisClient = null;
      
      // 不应抛出错误
      await expect(closeRedisConnection()).resolves.not.toThrow();
    });
  });
}); 