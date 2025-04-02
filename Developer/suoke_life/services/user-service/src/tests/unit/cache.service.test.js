/**
 * 缓存服务单元测试
 */
const { describe, it, beforeEach, afterEach, expect, jest } = require('@jest/globals');
const Redis = require('ioredis');
const NodeCache = require('node-cache');

// 模拟依赖
jest.mock('ioredis');
jest.mock('node-cache');
jest.mock('../../utils/logger');

// 重新导入缓存服务以获取模拟后的实例
let cacheService;

describe('缓存服务测试', () => {
  beforeEach(() => {
    jest.resetModules();
    
    // 模拟NodeCache
    NodeCache.mockImplementation(() => ({
      set: jest.fn().mockReturnValue(true),
      get: jest.fn(),
      del: jest.fn().mockReturnValue(1),
      flushAll: jest.fn(),
      getStats: jest.fn().mockReturnValue({ hits: 0, misses: 0 })
    }));
    
    // 模拟Redis
    Redis.mockImplementation(() => ({
      on: jest.fn(),
      ping: jest.fn().mockResolvedValue('PONG'),
      get: jest.fn(),
      set: jest.fn().mockResolvedValue('OK'),
      quit: jest.fn().mockResolvedValue('OK'),
      del: jest.fn().mockResolvedValue(1),
      flushdb: jest.fn().mockResolvedValue('OK')
    }));
    
    // 重新导入模块以应用模拟
    cacheService = require('../../utils/cache');
  });
  
  afterEach(() => {
    jest.clearAllMocks();
  });
  
  describe('init', () => {
    it('应该成功初始化Redis连接', async () => {
      // 修改配置以启用Redis
      const config = require('../../config');
      config.redis = { enabled: true, host: 'localhost', port: 6379 };
      
      await cacheService.init();
      
      // 验证Redis构造函数被调用
      expect(Redis).toHaveBeenCalled();
      expect(Redis.mock.instances[0].ping).toHaveBeenCalled();
    });
    
    it('应该在Redis禁用时使用内存缓存', async () => {
      // 修改配置以禁用Redis
      const config = require('../../config');
      config.redis = { enabled: false };
      
      await cacheService.init();
      
      // 验证Redis构造函数未被调用
      expect(Redis).not.toHaveBeenCalled();
    });
    
    it('应该在Redis连接失败时回退到内存缓存', async () => {
      // 修改配置以启用Redis
      const config = require('../../config');
      config.redis = { enabled: true, host: 'localhost', port: 6379 };
      
      // 模拟Redis连接失败
      Redis.mockImplementation(() => ({
        on: jest.fn(),
        ping: jest.fn().mockRejectedValue(new Error('连接失败')),
        quit: jest.fn().mockResolvedValue('OK')
      }));
      
      await cacheService.init();
      
      // 验证Redis构造函数被调用但服务回退到内存缓存
      expect(Redis).toHaveBeenCalled();
      expect(Redis.mock.instances[0].ping).toHaveBeenCalled();
    });
  });
  
  describe('get', () => {
    it('应该从Redis获取缓存项', async () => {
      // 准备
      const key = 'test-key';
      const expectedValue = { id: 1, name: 'test' };
      
      // 模拟Redis响应
      Redis.mockImplementation(() => ({
        on: jest.fn(),
        ping: jest.fn().mockResolvedValue('PONG'),
        get: jest.fn().mockResolvedValue(JSON.stringify(expectedValue))
      }));
      
      // 重新导入模块以应用新的模拟
      jest.resetModules();
      cacheService = require('../../utils/cache');
      
      // 设置配置并初始化
      const config = require('../../config');
      config.redis = { enabled: true, host: 'localhost', port: 6379 };
      await cacheService.init();
      
      // 执行
      const result = await cacheService.get(key);
      
      // 验证
      expect(Redis.mock.instances[0].get).toHaveBeenCalledWith(key);
      expect(result).toEqual(expectedValue);
    });
    
    it('应该在Redis禁用时从内存缓存获取', async () => {
      // 准备
      const key = 'test-key';
      const expectedValue = { id: 1, name: 'test' };
      
      // 模拟NodeCache响应
      NodeCache.mockImplementation(() => ({
        set: jest.fn(),
        get: jest.fn().mockReturnValue(expectedValue),
        getStats: jest.fn()
      }));
      
      // 重新导入模块以应用新的模拟
      jest.resetModules();
      cacheService = require('../../utils/cache');
      
      // 设置配置并初始化
      const config = require('../../config');
      config.redis = { enabled: false };
      await cacheService.init();
      
      // 执行
      const result = await cacheService.get(key);
      
      // 验证
      expect(NodeCache.mock.instances[0].get).toHaveBeenCalledWith(key);
      expect(result).toEqual(expectedValue);
    });
  });
  
  describe('set', () => {
    it('应该将缓存项存入Redis和内存缓存', async () => {
      // 准备
      const key = 'test-key';
      const value = { id: 1, name: 'test' };
      const ttl = 300;
      
      // 重新导入模块
      jest.resetModules();
      cacheService = require('../../utils/cache');
      
      // 设置配置并初始化
      const config = require('../../config');
      config.redis = { enabled: true, host: 'localhost', port: 6379 };
      await cacheService.init();
      
      // 执行
      await cacheService.set(key, value, ttl);
      
      // 验证
      expect(Redis.mock.instances[0].set).toHaveBeenCalledWith(
        key, 
        JSON.stringify(value), 
        'EX', 
        ttl
      );
      expect(NodeCache.mock.instances[0].set).toHaveBeenCalledWith(
        key,
        value,
        ttl
      );
    });
  });
  
  describe('del', () => {
    it('应该从Redis和内存缓存中删除项', async () => {
      // 准备
      const key = 'test-key';
      
      // 重新导入模块
      jest.resetModules();
      cacheService = require('../../utils/cache');
      
      // 设置配置并初始化
      const config = require('../../config');
      config.redis = { enabled: true, host: 'localhost', port: 6379 };
      await cacheService.init();
      
      // 执行
      await cacheService.del(key);
      
      // 验证
      expect(Redis.mock.instances[0].del).toHaveBeenCalledWith(key);
      expect(NodeCache.mock.instances[0].del).toHaveBeenCalledWith(key);
    });
  });
  
  describe('clear', () => {
    it('应该清除Redis和内存缓存', async () => {
      // 重新导入模块
      jest.resetModules();
      cacheService = require('../../utils/cache');
      
      // 设置配置并初始化
      const config = require('../../config');
      config.redis = { enabled: true, host: 'localhost', port: 6379 };
      await cacheService.init();
      
      // 执行
      await cacheService.clear();
      
      // 验证
      expect(Redis.mock.instances[0].flushdb).toHaveBeenCalled();
      expect(NodeCache.mock.instances[0].flushAll).toHaveBeenCalled();
    });
  });
});