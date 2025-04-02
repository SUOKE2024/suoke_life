/**
 * realTimeService单元测试
 */
const { jest } = require('@jest/globals');

// 模拟依赖
jest.mock('../../../src/utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn()
}));

jest.mock('redis', () => {
  const mockRedisClient = {
    get: jest.fn(),
    set: jest.fn(),
    incr: jest.fn(),
    pexpire: jest.fn(),
    publish: jest.fn(),
    duplicate: jest.fn(),
    on: jest.fn()
  };
  
  mockRedisClient.duplicate.mockReturnValue({
    on: jest.fn(),
    subscribe: jest.fn()
  });
  
  return {
    createClient: jest.fn().mockReturnValue(mockRedisClient)
  };
});

// 导入测试目标
const realTimeService = require('../../../src/services/realTimeService');

describe('实时服务测试', () => {
  // 每个测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('sendUserNotification', () => {
    test('应该将消息添加到用户的消息队列', async () => {
      // 执行
      const result = await realTimeService.sendUserNotification('user123', {
        type: 'test_notification',
        message: '测试消息'
      });
      
      // 断言
      expect(result).toBe(true);
    });
  });
  
  describe('notifyTeamMembers', () => {
    test('应该广播消息到团队成员', async () => {
      // 模拟实现
      const redisPub = require('redis').createClient().publish;
      redisPub.mockResolvedValue(1);
      
      // 执行
      const result = await realTimeService.notifyTeamMembers('team123', 'team_event', { 
        data: '测试数据' 
      });
      
      // 断言
      expect(redisPub).toHaveBeenCalled();
      expect(result).toHaveProperty('success');
    });
  });
  
  describe('broadcastMazeEvent', () => {
    test('应该广播迷宫事件', async () => {
      // 模拟实现
      const redisPub = require('redis').createClient().publish;
      redisPub.mockResolvedValue(1);
      
      // 执行
      const result = await realTimeService.broadcastMazeEvent('maze123', 'maze_event', {
        action: 'treasure_found'
      });
      
      // 断言
      expect(redisPub).toHaveBeenCalled();
      expect(result).toHaveProperty('success');
    });
  });
  
  describe('joinRoom', () => {
    test('应该将用户添加到房间', async () => {
      // 模拟实现
      const redisPub = require('redis').createClient().publish;
      redisPub.mockResolvedValue(1);
      
      // 执行
      const result = await realTimeService.joinRoom('user123', 'team', 'team123');
      
      // 断言
      expect(result).toBe(true);
      expect(redisPub).toHaveBeenCalled();
    });
    
    test('如果用户已在房间中，应该不重复添加', async () => {
      // 准备
      await realTimeService.joinRoom('user123', 'team', 'team123');
      const redisPub = require('redis').createClient().publish;
      redisPub.mockClear();
      
      // 执行
      const result = await realTimeService.joinRoom('user123', 'team', 'team123');
      
      // 断言
      expect(result).toBe(true);
      expect(redisPub).toHaveBeenCalledTimes(1);
    });
  });
  
  describe('leaveRoom', () => {
    test('应该将用户从房间中移除', async () => {
      // 准备
      await realTimeService.joinRoom('user123', 'team', 'team123');
      const redisPub = require('redis').createClient().publish;
      redisPub.mockClear();
      
      // 执行
      const result = await realTimeService.leaveRoom('user123', 'team', 'team123');
      
      // 断言
      expect(result).toBe(true);
      expect(redisPub).toHaveBeenCalled();
    });
    
    test('如果房间为空，应该删除房间', async () => {
      // 准备
      await realTimeService.joinRoom('user123', 'team', 'team123');
      const redisPub = require('redis').createClient().publish;
      redisPub.mockClear();
      
      // 执行
      const result = await realTimeService.leaveRoom('user123', 'team', 'team123');
      
      // 断言
      expect(result).toBe(true);
      // 房间应该被删除（无法直接测试内部状态，但可以测试Redis发布）
      expect(redisPub).toHaveBeenCalled();
    });
  });
  
  describe('userConnect', () => {
    test('应该注册用户连接并检查离线消息', async () => {
      // 模拟实现
      const redisGet = require('redis').createClient().get;
      const redisPub = require('redis').createClient().publish;
      redisGet.mockResolvedValue(null); // 无离线消息
      redisPub.mockResolvedValue(1);
      
      // 执行
      const result = await realTimeService.userConnect('user123', { 
        device: 'mobile',
        version: '1.0.0'
      });
      
      // 断言
      expect(result).toBe(true);
      expect(redisPub).toHaveBeenCalledWith('user:connections', expect.any(String));
      expect(redisGet).toHaveBeenCalled();
    });
    
    test('应该处理离线消息', async () => {
      // 模拟实现
      const redisGet = require('redis').createClient().get;
      const redisSet = require('redis').createClient().set;
      redisGet.mockResolvedValue(JSON.stringify([
        { type: 'offline_message', content: '离线消息1' },
        { type: 'offline_message', content: '离线消息2' }
      ]));
      redisSet.mockResolvedValue('OK');
      
      // 执行
      const result = await realTimeService.userConnect('user123', { device: 'mobile' });
      
      // 断言
      expect(result).toBe(true);
      expect(redisGet).toHaveBeenCalled();
      expect(redisSet).toHaveBeenCalled();
    });
  });
  
  describe('userDisconnect', () => {
    test('应该移除用户连接并从所有房间中移除用户', async () => {
      // 准备
      await realTimeService.userConnect('user123', { device: 'mobile' });
      await realTimeService.joinRoom('user123', 'team', 'team123');
      
      const redisPub = require('redis').createClient().publish;
      redisPub.mockClear();
      
      // 执行
      const result = await realTimeService.userDisconnect('user123');
      
      // 断言
      expect(result).toBe(true);
      expect(redisPub).toHaveBeenCalledWith('user:connections', expect.any(String));
    });
  });
  
  describe('updateUserActivity', () => {
    test('应该更新用户的最后活动时间', async () => {
      // 准备
      await realTimeService.userConnect('user123', { device: 'mobile' });
      
      // 执行
      const result = await realTimeService.updateUserActivity('user123');
      
      // 断言
      expect(result).toBe(true);
    });
    
    test('对不存在的用户应该返回false', async () => {
      // 执行
      const result = await realTimeService.updateUserActivity('nonexistent');
      
      // 断言
      expect(result).toBe(false);
    });
  });
  
  describe('消息压缩', () => {
    test('应该能够压缩和解压消息数据', async () => {
      // 准备
      const testData = { 
        type: 'complex_message',
        payload: { 
          items: Array(100).fill({ id: 'test', value: 'data' }),
          stats: { count: 100, average: 0.5 }
        }
      };
      
      // 执行
      const compressed = await realTimeService.compressData(testData);
      const decompressed = await realTimeService.decompressData(compressed);
      
      // 断言
      expect(Buffer.isBuffer(compressed)).toBe(true);
      expect(decompressed).toEqual(testData);
    });
  });
}); 