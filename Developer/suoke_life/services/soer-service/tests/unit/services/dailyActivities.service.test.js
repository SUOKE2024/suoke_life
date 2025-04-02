/**
 * 日常活动服务单元测试
 */
const DailyActivitiesService = require('../../../src/services/dailyActivities.service');
const { ValidationError, NotFoundError } = require('../../../src/utils/errors');

// 模拟依赖
jest.mock('../../../src/models/db.service', () => ({
  connect: jest.fn().mockResolvedValue(undefined),
  query: jest.fn(),
  find: jest.fn(),
  create: jest.fn()
}));

jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

describe('日常活动服务', () => {
  let service;
  const dbService = require('../../../src/models/db.service');
  
  beforeEach(() => {
    jest.clearAllMocks();
    service = new DailyActivitiesService();
  });
  
  describe('getActivitySummary', () => {
    test('应处理有效的时间段参数', async () => {
      // 为每种时间段分别测试
      const periods = ['day', 'week', 'month'];
      
      for (const period of periods) {
        // 模拟数据库响应，返回指标
        dbService.find.mockResolvedValueOnce([{
          user_id: 'user123',
          period: period,
          date: new Date(),
          total_activities: 5,
          total_duration: 150,
          total_distance: 10.5,
          total_calories: 800,
          activity_breakdown: JSON.stringify([
            { type: 'walking', typeLabel: '步行', count: 3, duration: 90 },
            { type: 'yoga', typeLabel: '瑜伽', count: 2, duration: 60 }
          ])
        }]);
        
        // 调用方法
        const result = await service.getActivitySummary('user123', period);
        
        // 验证结果
        expect(result).toHaveProperty('userId', 'user123');
        expect(result).toHaveProperty('period', period);
        expect(result).toHaveProperty('totalActivities', 5);
        expect(result).toHaveProperty('totalDuration', 150);
        expect(result).toHaveProperty('totalDistance', 10.5);
        expect(result).toHaveProperty('totalCalories', 800);
        expect(result).toHaveProperty('activityBreakdown');
        expect(result.activityBreakdown).toHaveLength(2);
        expect(result.activityBreakdown[0]).toHaveProperty('type', 'walking');
        expect(result.activityBreakdown[1]).toHaveProperty('type', 'yoga');
      }
    });
    
    test('无指标记录时应从活动数据计算摘要', async () => {
      // 模拟没有找到指标记录
      dbService.find.mockResolvedValueOnce([]);
      
      // 模拟找到了活动记录
      const mockActivities = [
        {
          id: 'act1',
          user_id: 'user123',
          type: 'walking',
          type_label: '步行',
          description: '早晨散步',
          duration: 30,
          distance: 2.5,
          calories: 120,
          start_time: new Date(),
          heart_rate: JSON.stringify({ average: 80 })
        },
        {
          id: 'act2',
          user_id: 'user123',
          type: 'yoga',
          type_label: '瑜伽',
          description: '晚间瑜伽',
          duration: 45,
          calories: 180,
          start_time: new Date()
        }
      ];
      
      dbService.query.mockResolvedValueOnce(mockActivities);
      
      // 模拟创建新的指标记录
      dbService.create.mockResolvedValueOnce({});
      
      // 调用方法
      const result = await service.getActivitySummary('user123', 'day');
      
      // 验证结果
      expect(result).toHaveProperty('userId', 'user123');
      expect(result).toHaveProperty('totalActivities', 2);
      expect(result).toHaveProperty('totalDuration', 75);
      expect(result).toHaveProperty('totalCalories', 300);
      expect(result).toHaveProperty('activityBreakdown');
      expect(result.activityBreakdown).toHaveLength(2);
      
      // 验证异步保存指标调用
      expect(dbService.create).toHaveBeenCalled();
    });
    
    test('无活动数据时应返回空摘要', async () => {
      // 模拟没有找到指标记录
      dbService.find.mockResolvedValueOnce([]);
      
      // 模拟没有找到活动记录
      dbService.query.mockResolvedValueOnce([]);
      
      // 调用方法
      const result = await service.getActivitySummary('user123', 'day');
      
      // 验证结果
      expect(result).toHaveProperty('userId', 'user123');
      expect(result).toHaveProperty('totalActivities', 0);
      expect(result).toHaveProperty('totalDuration', 0);
      expect(result).toHaveProperty('totalDistance', 0);
      expect(result).toHaveProperty('totalCalories', 0);
      expect(result).toHaveProperty('activityBreakdown', []);
    });
    
    test('无效时间段应抛出验证错误', async () => {
      await expect(service.getActivitySummary('user123', 'invalid'))
        .rejects.toThrow(ValidationError);
    });
  });
  
  describe('getActivityDetail', () => {
    test('应返回存在的活动详情', async () => {
      // 模拟找到活动记录
      const mockActivity = {
        id: 'act123',
        user_id: 'user123',
        type: 'running',
        type_label: '跑步',
        description: '5公里跑',
        duration: 25,
        distance: 5,
        calories: 300,
        heart_rate: JSON.stringify({ average: 150, max: 170, min: 120 }),
        created_at: new Date(),
        updated_at: new Date()
      };
      
      dbService.query.mockResolvedValueOnce([mockActivity]);
      
      // 调用方法
      const result = await service.getActivityDetail('user123', 'act123');
      
      // 验证结果
      expect(result).toHaveProperty('id', 'act123');
      expect(result).toHaveProperty('userId', 'user123');
      expect(result).toHaveProperty('type', 'running');
      expect(result).toHaveProperty('typeLabel', '跑步');
      expect(result).toHaveProperty('heartRate');
      expect(result.heartRate).toEqual({ average: 150, max: 170, min: 120 });
    });
    
    test('活动不存在时应抛出NotFoundError', async () => {
      // 模拟未找到活动记录
      dbService.query.mockResolvedValueOnce([]);
      
      // 调用方法并验证错误
      await expect(service.getActivityDetail('user123', 'nonexistent'))
        .rejects.toThrow(NotFoundError);
    });
  });
  
  describe('recordActivity', () => {
    test('应成功记录有效活动', async () => {
      // 模拟活动数据
      const activityData = {
        type: 'walking',
        description: '下午散步',
        duration: 40,
        distance: 3,
        calories: 160
      };
      
      // 模拟创建成功
      const createdActivity = {
        id: 'new-act-123',
        user_id: 'user123',
        type: 'walking',
        description: '下午散步',
        duration: 40,
        distance: 3,
        calories: 160,
        created_at: new Date(),
        updated_at: new Date()
      };
      
      dbService.create.mockResolvedValueOnce(createdActivity);
      
      // 调用方法
      const result = await service.recordActivity('user123', activityData);
      
      // 验证结果
      expect(result).toHaveProperty('id', 'new-act-123');
      expect(result).toHaveProperty('userId', 'user123');
      expect(result).toHaveProperty('type', 'walking');
      expect(result).toHaveProperty('duration', 40);
    });
    
    test('缺少必要字段应抛出ValidationError', async () => {
      // 测试缺少各种必要字段的情况
      const invalidCases = [
        { description: '无类型', duration: 30 },
        { type: 'walking', duration: 30 },
        { type: 'walking', description: '无时长' }
      ];
      
      for (const invalidData of invalidCases) {
        await expect(service.recordActivity('user123', invalidData))
          .rejects.toThrow(ValidationError);
      }
    });
    
    test('无效活动类型应抛出ValidationError', async () => {
      // 使用不支持的活动类型
      const invalidActivity = {
        type: 'invalid_type',
        description: '无效类型活动',
        duration: 30
      };
      
      await expect(service.recordActivity('user123', invalidActivity))
        .rejects.toThrow(ValidationError);
    });
  });
  
  describe('getActivityRecommendations', () => {
    test('应返回活动建议列表', async () => {
      // 模拟用户最近活动类型
      dbService.query.mockResolvedValueOnce([
        { type: 'walking', count: 5 },
        { type: 'yoga', count: 3 }
      ]);
      
      // 调用方法
      const result = await service.getActivityRecommendations('user123');
      
      // 验证结果
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      
      // 验证建议格式
      for (const recommendation of result) {
        expect(recommendation).toHaveProperty('id');
        expect(recommendation).toHaveProperty('type');
        expect(recommendation).toHaveProperty('title');
        expect(recommendation).toHaveProperty('description');
        expect(recommendation).toHaveProperty('durationMinutes');
        expect(recommendation).toHaveProperty('benefits');
        expect(Array.isArray(recommendation.benefits)).toBe(true);
      }
      
      // 确认用户偏好活动类型的自定义建议
      expect(result.some(r => r.type === 'walking')).toBe(true);
    });
    
    test('无历史活动时应返回标准建议', async () => {
      // 模拟没有历史活动
      dbService.query.mockResolvedValueOnce([]);
      
      // 调用方法
      const result = await service.getActivityRecommendations('user123');
      
      // 验证结果
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      
      // 应该只包含标准建议
      const standardTypes = ['walking', 'yoga', 'meditation'];
      for (const recommendation of result) {
        expect(standardTypes).toContain(recommendation.type);
      }
    });
  });
}); 