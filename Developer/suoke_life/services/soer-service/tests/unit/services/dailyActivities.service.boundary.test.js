/**
 * 日常活动服务边界条件测试
 */
const DailyActivitiesService = require('../../../src/services/dailyActivities.service');
const { ValidationError, NotFoundError, DatabaseError } = require('../../../src/utils/errors');

// 模拟依赖
jest.mock('../../../src/models/db.service', () => ({
  connect: jest.fn().mockResolvedValue(undefined),
  query: jest.fn(),
  find: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn()
}));

jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

describe('日常活动服务边界条件测试', () => {
  let service;
  const dbService = require('../../../src/models/db.service');
  
  beforeEach(() => {
    jest.clearAllMocks();
    service = new DailyActivitiesService();
  });
  
  describe('异常参数处理', () => {
    test('用户ID为空时应抛出ValidationError', async () => {
      await expect(service.getActivitySummary('', 'day'))
        .rejects.toThrow(ValidationError);
      
      await expect(service.getActivitySummary(null, 'day'))
        .rejects.toThrow(ValidationError);
      
      await expect(service.getActivitySummary(undefined, 'day'))
        .rejects.toThrow(ValidationError);
    });
    
    test('极长用户ID应被正确处理', async () => {
      // 创建一个非常长的ID
      const longId = 'a'.repeat(1000);
      
      // 模拟数据库返回
      dbService.find.mockResolvedValueOnce([]);
      dbService.query.mockResolvedValueOnce([]);
      
      // 应正常处理并不抛出错误
      await service.getActivitySummary(longId, 'day');
      
      // 验证调用时使用了长ID
      expect(dbService.find).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ user_id: longId }),
        expect.any(Object)
      );
    });
    
    test('超大数据量应被正确处理', async () => {
      // 模拟大量活动记录
      const largeActivitiesList = Array(1000).fill().map((_, i) => ({
        id: `act${i}`,
        user_id: 'user123',
        type: i % 2 === 0 ? 'walking' : 'yoga',
        type_label: i % 2 === 0 ? '步行' : '瑜伽',
        duration: 30,
        calories: 100,
        distance: 2,
        created_at: new Date(),
        updated_at: new Date()
      }));
      
      dbService.find.mockResolvedValueOnce([]);
      dbService.query.mockResolvedValueOnce(largeActivitiesList);
      
      // 应能处理大量数据
      const result = await service.getActivitySummary('user123', 'day');
      
      // 验证结果包含所有活动
      expect(result.totalActivities).toBe(1000);
    });
  });
  
  describe('数据库错误处理', () => {
    test('数据库查询错误应抛出DatabaseError', async () => {
      // 模拟数据库错误
      const dbError = new Error('数据库连接失败');
      dbService.find.mockRejectedValueOnce(dbError);
      
      // 验证错误被转换为DatabaseError
      await expect(service.getActivitySummary('user123', 'day'))
        .rejects.toThrow(DatabaseError);
    });
    
    test('数据库返回无效数据应优雅处理', async () => {
      // 模拟数据库返回无效JSON
      dbService.find.mockResolvedValueOnce([{
        user_id: 'user123',
        period: 'day',
        activity_breakdown: '{这不是有效的JSON}',
        total_activities: 10,
        total_duration: 300
      }]);
      
      // 应能处理无效数据
      const result = await service.getActivitySummary('user123', 'day');
      
      // 应返回默认的空数组
      expect(result.activityBreakdown).toEqual([]);
    });
    
    test('记录不存在时应抛出NotFoundError', async () => {
      // 模拟空结果
      dbService.query.mockResolvedValueOnce([]);
      
      // 验证抛出NotFoundError
      await expect(service.getActivityDetail('user123', 'non-existent-id'))
        .rejects.toThrow(NotFoundError);
    });
  });
  
  describe('记录活动边界条件', () => {
    test('极端值处理', async () => {
      // 测试极端值
      const extremeValues = {
        type: 'walking',
        description: '极端值测试',
        duration: 999999, // 非常长的时间
        distance: 99999.9, // 非常远的距离
        calories: 1000000 // 非常高的卡路里
      };
      
      // 模拟创建成功
      dbService.create.mockResolvedValueOnce({
        id: 'extreme-123',
        user_id: 'user123',
        ...extremeValues
      });
      
      // 应能处理极端值
      const result = await service.recordActivity('user123', extremeValues);
      
      // 验证结果包含所有极端值
      expect(result).toHaveProperty('duration', 999999);
      expect(result).toHaveProperty('distance', 99999.9);
      expect(result).toHaveProperty('calories', 1000000);
    });
    
    test('重复记录处理', async () => {
      // 连续记录两个相同的活动
      const sameActivity = {
        type: 'walking',
        description: '重复活动',
        duration: 30
      };
      
      // 第一次创建
      dbService.create.mockResolvedValueOnce({
        id: 'repeat-1',
        user_id: 'user123',
        ...sameActivity,
        created_at: new Date()
      });
      
      // 第二次创建
      dbService.create.mockResolvedValueOnce({
        id: 'repeat-2',
        user_id: 'user123',
        ...sameActivity,
        created_at: new Date()
      });
      
      // 连续记录两次
      await service.recordActivity('user123', sameActivity);
      await service.recordActivity('user123', sameActivity);
      
      // 验证两次都调用了create
      expect(dbService.create).toHaveBeenCalledTimes(2);
    });
    
    test('无效活动类型边界检查', async () => {
      // 各种边界情况的无效类型
      const invalidTypes = [
        { type: '', description: '空字符串类型', duration: 30 },
        { type: '   ', description: '空白字符类型', duration: 30 },
        { type: 123, description: '数字类型', duration: 30 },
        { type: 'a'.repeat(100), description: '超长类型', duration: 30 }
      ];
      
      // 所有这些应该都抛出ValidationError
      for (const invalidActivity of invalidTypes) {
        await expect(service.recordActivity('user123', invalidActivity))
          .rejects.toThrow(ValidationError);
      }
    });
  });
  
  describe('活动推荐边界条件', () => {
    test('异常用户活动模式处理', async () => {
      // 模拟用户有很多不同类型的活动
      dbService.query.mockResolvedValueOnce([
        { type: 'type1', count: 10 },
        { type: 'type2', count: 9 },
        { type: 'type3', count: 8 },
        { type: 'type4', count: 7 },
        { type: 'type5', count: 6 },
        { type: 'type6', count: 5 },
        { type: 'type7', count: 4 },
        { type: 'type8', count: 3 },
        { type: 'type9', count: 2 },
        { type: 'type10', count: 1 }
      ]);
      
      // 应能处理多种活动类型
      const result = await service.getActivityRecommendations('user123');
      
      // 验证结果
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
    });
    
    test('用户无活动记录处理', async () => {
      // 模拟用户没有任何活动记录
      dbService.query.mockResolvedValueOnce([]);
      
      // 应返回默认推荐
      const result = await service.getActivityRecommendations('user123');
      
      // 验证结果
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
    });
  });
}); 