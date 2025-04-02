/**
 * 日常活动模块集成测试
 */
const fastify = require('fastify');
const DailyActivitiesService = require('../../src/services/dailyActivities.service');
const dbService = require('../../src/models/db.service');
const { 
  ACTIVITIES_TABLE, 
  ACTIVITY_METRICS_TABLE,
  createTables 
} = require('../../src/models/dailyActivities.model');
const routes = require('../../src/routes/dailyActivities.routes');

// 模拟配置
jest.mock('../../src/config', () => ({
  database: {
    host: process.env.TEST_DB_HOST || 'localhost',
    port: process.env.TEST_DB_PORT || 3306,
    user: process.env.TEST_DB_USER || 'test',
    password: process.env.TEST_DB_PASSWORD || 'test',
    name: process.env.TEST_DB_NAME || 'test_db',
    connectionLimit: 2
  }
}));

describe('日常活动集成测试', () => {
  let app;
  let service;
  const testUserId = 'test-user-' + Date.now();
  let testActivityId;
  
  // 在所有测试前设置
  beforeAll(async () => {
    // 连接数据库
    await dbService.connect();
    
    // 创建测试表
    await createTables(dbService);
    
    // 创建服务实例
    service = new DailyActivitiesService();
    
    // 创建测试应用
    app = fastify();
    await app.register(routes);
  });
  
  // 在所有测试后清理
  afterAll(async () => {
    // 清理测试数据
    try {
      await dbService.query(`DELETE FROM ${ACTIVITIES_TABLE} WHERE user_id = ?`, [testUserId]);
      await dbService.query(`DELETE FROM ${ACTIVITY_METRICS_TABLE} WHERE user_id = ?`, [testUserId]);
    } catch (error) {
      console.error('清理测试数据失败:', error);
    }
    
    // 断开数据库连接
    await dbService.disconnect();
    
    // 关闭测试应用
    await app.close();
  });
  
  // 测试数据库服务集成
  describe('数据库集成', () => {
    test('应成功连接数据库', async () => {
      // 验证连接是否成功
      expect(dbService.initialized).toBe(true);
      expect(dbService.pool).not.toBeNull();
    });
    
    test('应成功执行简单查询', async () => {
      // 执行简单查询
      const result = await dbService.query('SELECT 1 as value');
      expect(result).toHaveLength(1);
      expect(result[0]).toHaveProperty('value', 1);
    });
  });
  
  // 测试活动记录和查询
  describe('活动记录集成', () => {
    test('应成功记录新活动', async () => {
      // 创建测试活动数据
      const activityData = {
        type: 'walking',
        description: '集成测试活动',
        duration: 45,
        distance: 3.2,
        calories: 180,
        startTime: new Date().toISOString(),
        mood: '精神',
        tags: ['测试', '集成测试']
      };
      
      // 记录活动
      const activity = await service.recordActivity(testUserId, activityData);
      
      // 保存ID用于后续测试
      testActivityId = activity.id;
      
      // 验证结果
      expect(activity).toHaveProperty('id');
      expect(activity).toHaveProperty('userId', testUserId);
      expect(activity).toHaveProperty('type', 'walking');
      expect(activity).toHaveProperty('description', '集成测试活动');
      expect(activity).toHaveProperty('duration', 45);
    });
    
    test('应成功获取活动详情', async () => {
      // 确保有活动ID
      expect(testActivityId).toBeDefined();
      
      // 获取活动详情
      const activity = await service.getActivityDetail(testUserId, testActivityId);
      
      // 验证结果
      expect(activity).toHaveProperty('id', testActivityId);
      expect(activity).toHaveProperty('userId', testUserId);
      expect(activity).toHaveProperty('description', '集成测试活动');
      expect(activity).toHaveProperty('tags');
      expect(Array.isArray(activity.tags)).toBe(true);
      expect(activity.tags).toContain('测试');
    });
    
    test('应成功获取活动摘要', async () => {
      // 获取活动摘要
      const summary = await service.getActivitySummary(testUserId, 'day');
      
      // 验证结果
      expect(summary).toHaveProperty('userId', testUserId);
      expect(summary).toHaveProperty('totalActivities');
      expect(summary.totalActivities).toBeGreaterThan(0);
      expect(summary).toHaveProperty('totalDuration');
      expect(summary.totalDuration).toBeGreaterThan(0);
      expect(summary).toHaveProperty('activityBreakdown');
      expect(Array.isArray(summary.activityBreakdown)).toBe(true);
    });
    
    test('应成功获取推荐活动', async () => {
      // 获取推荐
      const recommendations = await service.getActivityRecommendations(testUserId);
      
      // 验证结果
      expect(Array.isArray(recommendations)).toBe(true);
      expect(recommendations.length).toBeGreaterThan(0);
      
      // 验证推荐格式
      for (const recommendation of recommendations) {
        expect(recommendation).toHaveProperty('id');
        expect(recommendation).toHaveProperty('type');
        expect(recommendation).toHaveProperty('title');
        expect(recommendation).toHaveProperty('description');
      }
    });
  });
  
  // API路由集成测试
  describe('API路由集成', () => {
    test('GET /api/users/:userId/activities/summary 应返回摘要', async () => {
      const response = await app.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/summary`,
        query: { period: 'day' }
      });
      
      // 验证状态码和响应格式
      expect(response.statusCode).toBe(200);
      const result = JSON.parse(response.payload);
      
      expect(result).toHaveProperty('userId', testUserId);
      expect(result).toHaveProperty('totalActivities');
    });
    
    test('GET /api/users/:userId/activities/:activityId 应返回详情', async () => {
      // 确保有活动ID
      expect(testActivityId).toBeDefined();
      
      const response = await app.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/${testActivityId}`
      });
      
      // 验证状态码和响应格式
      expect(response.statusCode).toBe(200);
      const result = JSON.parse(response.payload);
      
      expect(result).toHaveProperty('id', testActivityId);
      expect(result).toHaveProperty('userId', testUserId);
    });
    
    test('GET /api/users/:userId/activities/:activityId 不存在时应返回404', async () => {
      const response = await app.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/nonexistent-id`
      });
      
      // 验证状态码和错误响应
      expect(response.statusCode).toBe(404);
      const error = JSON.parse(response.payload);
      
      expect(error).toHaveProperty('error');
      expect(error.error).toHaveProperty('name', 'NotFoundError');
    });
    
    test('POST /api/users/:userId/activities 应创建新活动', async () => {
      const activityData = {
        type: 'yoga',
        description: 'API测试瑜伽',
        duration: 60,
        calories: 200
      };
      
      const response = await app.inject({
        method: 'POST',
        url: `/api/users/${testUserId}/activities`,
        payload: activityData
      });
      
      // 验证状态码和响应格式
      expect(response.statusCode).toBe(201);
      const result = JSON.parse(response.payload);
      
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('userId', testUserId);
      expect(result).toHaveProperty('type', 'yoga');
    });
    
    test('POST /api/users/:userId/activities 缺少必要字段应返回400', async () => {
      // 缺少必要字段duration
      const invalidData = {
        type: 'walking',
        description: '无效活动'
      };
      
      const response = await app.inject({
        method: 'POST',
        url: `/api/users/${testUserId}/activities`,
        payload: invalidData
      });
      
      // 验证状态码和错误响应
      expect(response.statusCode).toBe(400);
      const error = JSON.parse(response.payload);
      
      expect(error).toHaveProperty('error');
      expect(error.error).toHaveProperty('name', 'ValidationError');
    });
    
    test('GET /api/users/:userId/activities/recommendations 应返回推荐', async () => {
      const response = await app.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/recommendations`
      });
      
      // 验证状态码和响应格式
      expect(response.statusCode).toBe(200);
      const result = JSON.parse(response.payload);
      
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      
      // 验证推荐格式
      for (const recommendation of result) {
        expect(recommendation).toHaveProperty('id');
        expect(recommendation).toHaveProperty('type');
        expect(recommendation).toHaveProperty('title');
      }
    });
  });
}); 