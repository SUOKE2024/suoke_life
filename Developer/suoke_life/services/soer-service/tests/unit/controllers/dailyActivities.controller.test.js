/**
 * 日常活动控制器单元测试
 */
const DailyActivitiesController = require('../../../src/controllers/dailyActivities.controller');
const { ValidationError, NotFoundError } = require('../../../src/utils/errors');

// 模拟服务
jest.mock('../../../src/services/dailyActivities.service', () => {
  return jest.fn().mockImplementation(() => ({
    getActivitySummary: jest.fn(),
    getActivityDetail: jest.fn(),
    recordActivity: jest.fn(),
    getActivityRecommendations: jest.fn()
  }));
});

jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

describe('日常活动控制器', () => {
  let controller;
  let mockService;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // 创建控制器实例
    controller = new DailyActivitiesController();
    
    // 获取模拟的服务实例
    mockService = controller.service;
  });
  
  describe('getActivitySummary', () => {
    test('应正确处理有效请求', async () => {
      // 设置请求和响应对象
      const req = {
        params: { userId: 'user123' },
        query: { period: 'week' }
      };
      
      // 模拟服务响应
      const mockSummary = {
        userId: 'user123',
        period: 'week',
        totalActivities: 10,
        totalDuration: 300
      };
      mockService.getActivitySummary.mockResolvedValueOnce(mockSummary);
      
      // 调用控制器方法
      const result = await controller.getActivitySummary(req);
      
      // 验证结果
      expect(result).toEqual(mockSummary);
      expect(mockService.getActivitySummary).toHaveBeenCalledWith('user123', 'week');
    });
    
    test('应处理默认时间段', async () => {
      // 没有指定时间段的请求
      const req = {
        params: { userId: 'user123' },
        query: {}
      };
      
      // 模拟服务响应
      mockService.getActivitySummary.mockResolvedValueOnce({});
      
      // 调用控制器方法
      await controller.getActivitySummary(req);
      
      // 验证默认时间段
      expect(mockService.getActivitySummary).toHaveBeenCalledWith('user123', 'day');
    });
    
    test('无效时间段应抛出验证错误', async () => {
      // 无效时间段请求
      const req = {
        params: { userId: 'user123' },
        query: { period: 'invalid' }
      };
      
      // 调用控制器方法并验证错误
      await expect(controller.getActivitySummary(req))
        .rejects.toThrow(ValidationError);
    });
    
    test('应传递服务错误', async () => {
      const req = {
        params: { userId: 'user123' },
        query: { period: 'day' }
      };
      
      // 模拟服务错误
      const mockError = new Error('服务错误');
      mockService.getActivitySummary.mockRejectedValueOnce(mockError);
      
      // 调用控制器方法并验证错误传递
      await expect(controller.getActivitySummary(req))
        .rejects.toThrow('服务错误');
    });
  });
  
  describe('getActivityDetail', () => {
    test('应正确处理有效请求', async () => {
      // 设置请求对象
      const req = {
        params: { userId: 'user123', activityId: 'act123' }
      };
      
      // 模拟服务响应
      const mockActivity = {
        id: 'act123',
        userId: 'user123',
        type: 'walking',
        description: '散步'
      };
      mockService.getActivityDetail.mockResolvedValueOnce(mockActivity);
      
      // 调用控制器方法
      const result = await controller.getActivityDetail(req);
      
      // 验证结果
      expect(result).toEqual(mockActivity);
      expect(mockService.getActivityDetail).toHaveBeenCalledWith('user123', 'act123');
    });
    
    test('缺少活动ID应抛出验证错误', async () => {
      // 缺少活动ID的请求
      const req = {
        params: { userId: 'user123' }
      };
      
      // 调用控制器方法并验证错误
      await expect(controller.getActivityDetail(req))
        .rejects.toThrow(ValidationError);
    });
    
    test('应传递NotFoundError', async () => {
      const req = {
        params: { userId: 'user123', activityId: 'nonexistent' }
      };
      
      // 模拟服务错误
      const mockError = new NotFoundError('活动不存在');
      mockService.getActivityDetail.mockRejectedValueOnce(mockError);
      
      // 调用控制器方法并验证错误传递
      await expect(controller.getActivityDetail(req))
        .rejects.toThrow(NotFoundError);
      expect(mockService.getActivityDetail).toHaveBeenCalledWith('user123', 'nonexistent');
    });
  });
  
  describe('recordActivity', () => {
    test('应正确处理有效请求', async () => {
      // 设置请求对象
      const req = {
        params: { userId: 'user123' },
        body: {
          type: 'walking',
          description: '早晨散步',
          duration: 30,
          distance: 2.5
        }
      };
      
      // 模拟服务响应
      const mockActivity = {
        id: 'new-act-123',
        userId: 'user123',
        type: 'walking',
        description: '早晨散步',
        duration: 30,
        distance: 2.5
      };
      mockService.recordActivity.mockResolvedValueOnce(mockActivity);
      
      // 调用控制器方法
      const result = await controller.recordActivity(req);
      
      // 验证结果
      expect(result).toEqual(mockActivity);
      expect(mockService.recordActivity).toHaveBeenCalledWith('user123', req.body);
    });
    
    test('空请求体应抛出验证错误', async () => {
      // 空请求体
      const req = {
        params: { userId: 'user123' },
        body: {}
      };
      
      // 调用控制器方法并验证错误
      await expect(controller.recordActivity(req))
        .rejects.toThrow(ValidationError);
    });
    
    test('缺少必要字段应抛出验证错误', async () => {
      // 缺少持续时间
      const req = {
        params: { userId: 'user123' },
        body: {
          type: 'walking',
          description: '散步'
          // 缺少duration
        }
      };
      
      // 调用控制器方法并验证错误
      await expect(controller.recordActivity(req))
        .rejects.toThrow(ValidationError);
    });
    
    test('应传递服务验证错误', async () => {
      const req = {
        params: { userId: 'user123' },
        body: {
          type: 'invalid',
          description: '无效活动',
          duration: 30
        }
      };
      
      // 模拟服务验证错误
      const mockError = new ValidationError('无效的活动类型');
      mockService.recordActivity.mockRejectedValueOnce(mockError);
      
      // 调用控制器方法并验证错误传递
      await expect(controller.recordActivity(req))
        .rejects.toThrow(ValidationError);
    });
  });
  
  describe('getActivityRecommendations', () => {
    test('应正确处理有效请求', async () => {
      // 设置请求对象
      const req = {
        params: { userId: 'user123' }
      };
      
      // 模拟服务响应
      const mockRecommendations = [
        {
          id: 'rec1',
          type: 'walking',
          title: '晨间散步'
        },
        {
          id: 'rec2',
          type: 'yoga',
          title: '休闲瑜伽'
        }
      ];
      mockService.getActivityRecommendations.mockResolvedValueOnce(mockRecommendations);
      
      // 调用控制器方法
      const result = await controller.getActivityRecommendations(req);
      
      // 验证结果
      expect(result).toEqual(mockRecommendations);
      expect(mockService.getActivityRecommendations).toHaveBeenCalledWith('user123');
    });
    
    test('应传递服务错误', async () => {
      const req = {
        params: { userId: 'user123' }
      };
      
      // 模拟服务错误
      const mockError = new Error('推荐服务暂时不可用');
      mockService.getActivityRecommendations.mockRejectedValueOnce(mockError);
      
      // 调用控制器方法并验证错误传递
      await expect(controller.getActivityRecommendations(req))
        .rejects.toThrow('推荐服务暂时不可用');
    });
  });
}); 