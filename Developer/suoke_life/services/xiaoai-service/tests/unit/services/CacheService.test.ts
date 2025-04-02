/**
 * CacheService单元测试
 */
import { CacheService } from '../../../src/services/CacheService';
import { createMockRedisClient, clearRedisMocks } from '../helpers/mockRedis';

// 模拟redis模块
jest.mock('redis', () => {
  const mockClient = createMockRedisClient();
  return {
    createClient: jest.fn().mockReturnValue(mockClient)
  };
});

// 模拟日志记录器
jest.mock('../../../src/index', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
  }
}));

// 导入模拟的模块
import { createClient } from 'redis';
import { logger } from '../../../src/index';

describe('CacheService', () => {
  let cacheService: CacheService;
  let mockRedisClient: ReturnType<typeof createMockRedisClient>;
  
  beforeEach(() => {
    clearRedisMocks();
    process.env.REDIS_URL = 'redis://localhost:6379';
    
    // 获取模拟的Redis客户端实例
    mockRedisClient = (createClient as jest.Mock)();
    
    // 创建缓存服务实例
    cacheService = new CacheService();
  });
  
  describe('constructor', () => {
    it('应该根据环境变量创建Redis客户端', () => {
      expect(createClient).toHaveBeenCalledWith({
        url: 'redis://localhost:6379'
      });
    });
    
    it('应该设置事件监听器', () => {
      expect(mockRedisClient.on).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockRedisClient.on).toHaveBeenCalledWith('connect', expect.any(Function));
      expect(mockRedisClient.on).toHaveBeenCalledWith('disconnect', expect.any(Function));
    });
  });
  
  describe('connect', () => {
    it('如果未连接应该连接Redis', async () => {
      await cacheService.connect();
      expect(mockRedisClient.connect).toHaveBeenCalled();
    });
    
    it('如果已连接不应该再次连接', async () => {
      // 触发connect事件
      mockRedisClient.on.mock.calls.find(call => call[0] === 'connect')[1]();
      
      await cacheService.connect();
      expect(mockRedisClient.connect).not.toHaveBeenCalled();
    });
    
    it('连接失败时应该抛出错误', async () => {
      const error = new Error('连接失败');
      mockRedisClient.connect.mockRejectedValueOnce(error);
      
      await expect(cacheService.connect()).rejects.toThrow('连接失败');
      expect(logger.error).toHaveBeenCalledWith('Redis连接失败:', error);
    });
  });
  
  describe('disconnect', () => {
    it('如果已连接应该断开Redis连接', async () => {
      // 触发connect事件，设置连接状态
      mockRedisClient.on.mock.calls.find(call => call[0] === 'connect')[1]();
      
      await cacheService.disconnect();
      expect(mockRedisClient.disconnect).toHaveBeenCalled();
    });
    
    it('如果未连接不应该尝试断开连接', async () => {
      await cacheService.disconnect();
      expect(mockRedisClient.disconnect).not.toHaveBeenCalled();
    });
  });
  
  describe('set', () => {
    it('应该设置字符串键值', async () => {
      const key = 'test-key';
      const value = { name: 'test', value: 123 };
      
      await cacheService.set(key, value);
      
      expect(mockRedisClient.set).toHaveBeenCalledWith(key, JSON.stringify(value));
    });
    
    it('使用过期时间时应该调用setEx', async () => {
      const key = 'test-key';
      const value = { name: 'test', value: 123 };
      const ttl = 60;
      
      await cacheService.set(key, value, ttl);
      
      expect(mockRedisClient.setEx).toHaveBeenCalledWith(key, ttl, JSON.stringify(value));
    });
    
    it('出错时应该记录错误并重新抛出', async () => {
      const error = new Error('设置失败');
      mockRedisClient.set.mockRejectedValueOnce(error);
      
      await expect(cacheService.set('key', 'value')).rejects.toThrow('设置失败');
      expect(logger.error).toHaveBeenCalledWith(expect.stringContaining('Redis SET错误'), error);
    });
  });
  
  describe('get', () => {
    it('应该获取并解析值', async () => {
      const key = 'test-key';
      const value = { name: 'test', value: 123 };
      mockRedisClient.get.mockResolvedValueOnce(JSON.stringify(value));
      
      const result = await cacheService.get(key);
      
      expect(mockRedisClient.get).toHaveBeenCalledWith(key);
      expect(result).toEqual(value);
    });
    
    it('键不存在时应该返回null', async () => {
      mockRedisClient.get.mockResolvedValueOnce(null);
      
      const result = await cacheService.get('non-existent');
      
      expect(result).toBeNull();
    });
  });
  
  describe('hset/hget', () => {
    it('应该设置哈希字段', async () => {
      const key = 'hash-key';
      const field = 'field1';
      const value = { name: 'test', value: 123 };
      
      await cacheService.hset(key, field, value);
      
      expect(mockRedisClient.hSet).toHaveBeenCalledWith(key, field, JSON.stringify(value));
    });
    
    it('应该获取并解析哈希字段', async () => {
      const key = 'hash-key';
      const field = 'field1';
      const value = { name: 'test', value: 123 };
      mockRedisClient.hGet.mockResolvedValueOnce(JSON.stringify(value));
      
      const result = await cacheService.hget(key, field);
      
      expect(mockRedisClient.hGet).toHaveBeenCalledWith(key, field);
      expect(result).toEqual(value);
    });
  });
  
  describe('flush', () => {
    it('应该清空所有数据', async () => {
      await cacheService.flush();
      expect(mockRedisClient.flushAll).toHaveBeenCalled();
    });
  });
}); 