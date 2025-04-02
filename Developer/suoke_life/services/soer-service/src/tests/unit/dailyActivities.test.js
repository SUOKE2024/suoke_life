/**
 * 日常活动功能单元测试
 */
const DailyActivitiesService = require('../../services/dailyActivities.service');
const DailyActivitiesController = require('../../controllers/dailyActivities.controller');

// 模拟数据库服务
const mockDbService = {
  query: jest.fn(),
  getById: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn()
};

// 模拟请求和响应对象
const mockRequest = (params = {}, query = {}, body = {}) => ({
  params,
  query,
  body
});

const mockResponse = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

const mockNext = jest.fn();

describe('日常活动服务', () => {
  let dailyActivitiesService;
  
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 创建服务实例
    dailyActivitiesService = new DailyActivitiesService(mockDbService);
  });
  
  describe('getActivitySummary', () => {
    it('应返回用户活动摘要数据', async () => {
      // 安排
      const userId = 'user123';
      const period = 'day';
      
      // 执行
      const result = await dailyActivitiesService.getActivitySummary(userId, period);
      
      // 断言
      expect(result).toBeDefined();
      expect(result.userId).toBe(userId);
      expect(result.period).toBe(period);
      expect(result.periodLabel).toBe('今日');
      expect(result.summary).toBeDefined();
      expect(result.activityBreakdown).toBeInstanceOf(Array);
    });
    
    it('应为不同时间周期返回适当的数据', async () => {
      // 安排
      const userId = 'user123';
      
      // 执行 - 周
      const weekResult = await dailyActivitiesService.getActivitySummary(userId, 'week');
      
      // 断言 - 周
      expect(weekResult.periodLabel).toBe('本周');
      expect(weekResult.summary.totalActivities).toBe(12);
      
      // 执行 - 月
      const monthResult = await dailyActivitiesService.getActivitySummary(userId, 'month');
      
      // 断言 - 月
      expect(monthResult.periodLabel).toBe('本月');
      expect(monthResult.summary.totalActivities).toBe(45);
    });
  });
  
  describe('getActivityDetail', () => {
    it('应返回活动详情数据', async () => {
      // 安排
      const userId = 'user123';
      const activityId = 'activity1';
      
      // 执行
      const result = await dailyActivitiesService.getActivityDetail(userId, activityId);
      
      // 断言
      expect(result).toBeDefined();
      expect(result.id).toBe(activityId);
      expect(result.userId).toBe(userId);
      expect(result.type).toBeDefined();
      expect(result.duration).toBeDefined();
    });
    
    it('活动不存在时应抛出错误', async () => {
      // 安排
      const userId = 'user123';
      const activityId = 'notfound123';
      
      // 执行和断言
      await expect(dailyActivitiesService.getActivityDetail(userId, activityId))
        .rejects.toHaveProperty('status', 404);
    });
  });
  
  describe('recordActivity', () => {
    it('应创建并返回新活动', async () => {
      // 安排
      const userId = 'user123';
      const activityData = {
        type: 'walking',
        duration: 30,
        description: '测试活动'
      };
      
      // 执行
      const result = await dailyActivitiesService.recordActivity(userId, activityData);
      
      // 断言
      expect(result).toBeDefined();
      expect(result.id).toBeDefined();
      expect(result.userId).toBe(userId);
      expect(result.type).toBe(activityData.type);
      expect(result.duration).toBe(activityData.duration);
      expect(result.description).toBe(activityData.description);
      expect(result.createdAt).toBeDefined();
    });
    
    it('缺少必要字段时应抛出错误', async () => {
      // 安排
      const userId = 'user123';
      
      // 缺少类型
      const invalidActivity1 = {
        duration: 30,
        description: '测试活动'
      };
      
      // 缺少持续时间
      const invalidActivity2 = {
        type: 'walking',
        description: '测试活动'
      };
      
      // 执行和断言 - 缺少类型
      await expect(dailyActivitiesService.recordActivity(userId, invalidActivity1))
        .rejects.toHaveProperty('status', 400);
      
      // 执行和断言 - 缺少持续时间
      await expect(dailyActivitiesService.recordActivity(userId, invalidActivity2))
        .rejects.toHaveProperty('status', 400);
    });
    
    it('应验证活动类型的有效性', async () => {
      // 安排
      const userId = 'user123';
      const invalidActivity = {
        type: 'invalid_type', // 无效类型
        duration: 30,
        description: '测试活动'
      };
      
      // 执行和断言
      await expect(dailyActivitiesService.recordActivity(userId, invalidActivity))
        .rejects.toHaveProperty('status', 400);
    });
  });
  
  describe('getActivityRecommendations', () => {
    it('应返回活动建议列表', async () => {
      // 安排
      const userId = 'user123';
      
      // 执行
      const result = await dailyActivitiesService.getActivityRecommendations(userId);
      
      // 断言
      expect(result).toBeInstanceOf(Array);
      expect(result.length).toBeGreaterThan(0);
      
      // 检查第一个建议的结构
      const firstRecommendation = result[0];
      expect(firstRecommendation.id).toBeDefined();
      expect(firstRecommendation.type).toBeDefined();
      expect(firstRecommendation.typeLabel).toBeDefined();
      expect(firstRecommendation.title).toBeDefined();
      expect(firstRecommendation.description).toBeDefined();
      expect(firstRecommendation.benefitsForUser).toBeDefined();
    });
  });
});

describe('日常活动控制器', () => {
  let dailyActivitiesController;
  let dailyActivitiesService;
  
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 创建模拟服务
    dailyActivitiesService = {
      getActivitySummary: jest.fn(),
      getActivityDetail: jest.fn(),
      recordActivity: jest.fn(),
      getActivityRecommendations: jest.fn()
    };
    
    // 创建控制器实例
    dailyActivitiesController = new DailyActivitiesController(dailyActivitiesService);
  });
  
  describe('getActivitySummary', () => {
    it('应调用服务并返回活动摘要', async () => {
      // 安排
      const userId = 'user123';
      const period = 'day';
      const mockSummary = { id: 'summary1', userId, period };
      
      const req = mockRequest({ userId }, { period });
      const res = mockResponse();
      
      dailyActivitiesService.getActivitySummary.mockResolvedValue(mockSummary);
      
      // 执行
      await dailyActivitiesController.getActivitySummary(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.getActivitySummary).toHaveBeenCalledWith(userId, period);
      expect(res.json).toHaveBeenCalledWith(mockSummary);
      expect(mockNext).not.toHaveBeenCalled();
    });
    
    it('无效period参数时应返回400错误', async () => {
      // 安排
      const userId = 'user123';
      const invalidPeriod = 'invalid';
      
      const req = mockRequest({ userId }, { period: invalidPeriod });
      const res = mockResponse();
      
      // 执行
      await dailyActivitiesController.getActivitySummary(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.getActivitySummary).not.toHaveBeenCalled();
      expect(mockNext).toHaveBeenCalled();
      expect(mockNext.mock.calls[0][0]).toHaveProperty('status', 400);
    });
    
    it('服务抛出错误时应正确处理', async () => {
      // 安排
      const userId = 'user123';
      const period = 'day';
      const mockError = new Error('服务错误');
      
      const req = mockRequest({ userId }, { period });
      const res = mockResponse();
      
      dailyActivitiesService.getActivitySummary.mockRejectedValue(mockError);
      
      // 执行
      await dailyActivitiesController.getActivitySummary(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.getActivitySummary).toHaveBeenCalledWith(userId, period);
      expect(res.json).not.toHaveBeenCalled();
      expect(mockNext).toHaveBeenCalled();
    });
  });
  
  describe('getActivityDetail', () => {
    it('应调用服务并返回活动详情', async () => {
      // 安排
      const userId = 'user123';
      const activityId = 'activity1';
      const mockDetail = { id: activityId, userId, type: 'walking' };
      
      const req = mockRequest({ userId, activityId });
      const res = mockResponse();
      
      dailyActivitiesService.getActivityDetail.mockResolvedValue(mockDetail);
      
      // 执行
      await dailyActivitiesController.getActivityDetail(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.getActivityDetail).toHaveBeenCalledWith(userId, activityId);
      expect(res.json).toHaveBeenCalledWith(mockDetail);
      expect(mockNext).not.toHaveBeenCalled();
    });
  });
  
  describe('recordActivity', () => {
    it('应调用服务并返回201状态码', async () => {
      // 安排
      const userId = 'user123';
      const activityData = { type: 'walking', duration: 30, description: '测试活动' };
      const mockActivity = { id: 'new1', userId, ...activityData };
      
      const req = mockRequest({ userId }, {}, activityData);
      const res = mockResponse();
      
      dailyActivitiesService.recordActivity.mockResolvedValue(mockActivity);
      
      // 执行
      await dailyActivitiesController.recordActivity(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.recordActivity).toHaveBeenCalledWith(userId, activityData);
      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith(mockActivity);
      expect(mockNext).not.toHaveBeenCalled();
    });
    
    it('无效请求体时应返回400错误', async () => {
      // 安排
      const userId = 'user123';
      
      // 无效请求体
      const req = mockRequest({ userId }, {}, null);
      const res = mockResponse();
      
      // 执行
      await dailyActivitiesController.recordActivity(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.recordActivity).not.toHaveBeenCalled();
      expect(mockNext).toHaveBeenCalled();
      expect(mockNext.mock.calls[0][0]).toHaveProperty('status', 400);
    });
  });
  
  describe('getActivityRecommendations', () => {
    it('应调用服务并返回活动推荐', async () => {
      // 安排
      const userId = 'user123';
      const mockRecommendations = [
        { id: 'rec1', type: 'walking', title: '建议1' },
        { id: 'rec2', type: 'yoga', title: '建议2' }
      ];
      
      const req = mockRequest({ userId });
      const res = mockResponse();
      
      dailyActivitiesService.getActivityRecommendations.mockResolvedValue(mockRecommendations);
      
      // 执行
      await dailyActivitiesController.getActivityRecommendations(req, res, mockNext);
      
      // 断言
      expect(dailyActivitiesService.getActivityRecommendations).toHaveBeenCalledWith(userId);
      expect(res.json).toHaveBeenCalledWith(mockRecommendations);
      expect(mockNext).not.toHaveBeenCalled();
    });
  });
}); 