/**
 * Redis服务单元测试
 */
import { RedisService, setupRedisConnection, getRedisClient, closeRedisConnection } from '../../../src/services/redis-service';
import { RedisError } from '../../../src/errors/redis-error';

// 模拟ioredis
jest.mock('ioredis', () => {
  return jest.fn().mockImplementation(() => {
    return {
      quit: jest.fn().mockResolvedValue('OK'),
      on: jest.fn().mockImplementation((event, callback) => {
        if (event === 'connect') {
          process.nextTick(() => callback());
        }
        return this;
      })
    };
  });
});

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
      quit: jest.fn().mockResolvedValue('OK'),
      on: jest.fn(),
    };
    
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

  describe('全局Redis函数', () => {
    // 在测试前保存原始环境变量
    const originalEnv = { ...process.env };
    
    beforeEach(() => {
      // 提供默认的Redis环境变量值
      process.env.REDIS_HOST = 'localhost';
      process.env.REDIS_PORT = '6379';
      process.env.REDIS_PASSWORD = 'password123';
      
      // 重置模块，确保redisClient为null
      jest.resetModules();
    });
    
    afterEach(() => {
      // 恢复原始环境变量
      process.env = { ...originalEnv };
    });
    
    describe('setupRedisConnection', () => {
      it('应成功建立Redis连接', async () => {
        const Redis = require('ioredis');
        const mockOnMethod = jest.fn().mockImplementation((event, callback) => {
          if (event === 'connect') {
            callback();
          }
          return this;
        });

        Redis.mockImplementation(() => ({
          on: mockOnMethod,
          quit: jest.fn().mockResolvedValue('OK')
        }));

        await setupRedisConnection();
        
        // 验证Redis构造函数调用
        expect(Redis).toHaveBeenCalled();
        
        // 获取Redis客户端，不应抛出错误
        expect(() => getRedisClient()).not.toThrow();
      });
      
      it('应处理Redis连接错误', async () => {
        const Redis = require('ioredis');
        const mockOnMethod = jest.fn().mockImplementation((event, callback) => {
          if (event === 'error') {
            callback(new Error('Redis连接错误测试'));
          }
          return this;
        });

        Redis.mockImplementation(() => ({
          on: mockOnMethod,
          quit: jest.fn().mockResolvedValue('OK')
        }));
        
        await expect(setupRedisConnection()).rejects.toThrow();
      });
    });
    
    describe('getRedisClient', () => {
      it('未初始化时应抛出错误', () => {
        // 确保redisClient为null
        jest.resetModules();
        
        // 尝试获取客户端应该抛出错误
        expect(() => {
          const { getRedisClient } = require('../../../src/services/redis-service');
          getRedisClient();
        }).toThrow('Redis客户端未初始化');
      });
    });
    
    describe('closeRedisConnection', () => {
      it('应正确关闭Redis连接', async () => {
        const Redis = require('ioredis');
        const mockQuit = jest.fn().mockResolvedValue('OK');
        const mockOnMethod = jest.fn();

        Redis.mockImplementation(() => ({
          on: mockOnMethod,
          quit: mockQuit
        }));

        // 先初始化连接
        await setupRedisConnection();
        
        // 关闭连接
        await closeRedisConnection();
        
        // 验证quit方法被调用
        expect(mockQuit).toHaveBeenCalled();
      });
      
      it('应处理未初始化的情况', async () => {
        // 确保redisClient为null
        jest.resetModules();
        
        // 调用应该不会抛出错误
        const { closeRedisConnection } = require('../../../src/services/redis-service');
        await expect(closeRedisConnection()).resolves.not.toThrow();
      });
    });
  });
}); 