/**
 * 日常活动模块端到端测试
 * 测试完整用户流程
 */
const fastify = require('fastify');
const dbService = require('../../src/models/db.service');
const { 
  ACTIVITIES_TABLE, 
  ACTIVITY_METRICS_TABLE,
  ACTIVITY_GOALS_TABLE,
  createTables 
} = require('../../src/models/dailyActivities.model');
const app = require('../../src/app');

// 模拟配置
jest.mock('../../src/config', () => ({
  database: {
    host: process.env.TEST_DB_HOST || 'localhost',
    port: process.env.TEST_DB_PORT || 3306,
    user: process.env.TEST_DB_USER || 'test',
    password: process.env.TEST_DB_PASSWORD || 'test',
    name: process.env.TEST_DB_NAME || 'test_db',
    connectionLimit: 2
  },
  server: {
    port: 0 // 使用随机端口
  }
}));

describe('日常活动模块端到端测试', () => {
  let server;
  const testUserId = 'e2e-user-' + Date.now();
  let activityId1;
  let activityId2;
  
  // 在所有测试前设置
  beforeAll(async () => {
    try {
      // 连接数据库
      await dbService.connect();
      
      // 创建测试表
      await createTables(dbService);
      
      // 启动服务器
      server = await app();
      
      // 清理测试数据（如果有的话）
      await cleanupTestData();
    } catch (error) {
      console.error('E2E测试初始化失败:', error);
      throw error;
    }
  });
  
  // 在所有测试后清理
  afterAll(async () => {
    try {
      // 清理测试数据
      await cleanupTestData();
      
      // 断开数据库连接
      await dbService.disconnect();
      
      // 关闭服务器
      await server.close();
    } catch (error) {
      console.error('E2E测试清理失败:', error);
    }
  });
  
  // 清理测试数据的辅助函数
  async function cleanupTestData() {
    try {
      await dbService.query(`DELETE FROM ${ACTIVITIES_TABLE} WHERE user_id = ?`, [testUserId]);
      await dbService.query(`DELETE FROM ${ACTIVITY_METRICS_TABLE} WHERE user_id = ?`, [testUserId]);
      await dbService.query(`DELETE FROM ${ACTIVITY_GOALS_TABLE} WHERE user_id = ?`, [testUserId]);
    } catch (error) {
      console.error('清理测试数据失败:', error);
    }
  }
  
  // 测试完整用户流程
  describe('用户活动管理流程', () => {
    test('1. 用户记录第一个活动', async () => {
      // 创建第一个活动
      const morningActivity = {
        type: 'walking',
        description: '早晨散步',
        duration: 30,
        distance: 2.5,
        calories: 120,
        mood: '精神',
        tags: ['晨练', '户外'],
        startTime: new Date().toISOString()
      };
      
      const response = await server.inject({
        method: 'POST',
        url: `/api/users/${testUserId}/activities`,
        payload: morningActivity
      });
      
      // 验证创建成功
      expect(response.statusCode).toBe(201);
      const result = JSON.parse(response.payload);
      
      // 保存活动ID
      activityId1 = result.id;
      
      // 验证返回数据
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('userId', testUserId);
      expect(result).toHaveProperty('type', 'walking');
      expect(result).toHaveProperty('duration', 30);
      expect(result).toHaveProperty('tags');
      expect(result.tags).toContain('晨练');
    });
    
    test('2. 用户查看第一个活动详情', async () => {
      const response = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/${activityId1}`
      });
      
      // 验证请求成功
      expect(response.statusCode).toBe(200);
      const result = JSON.parse(response.payload);
      
      // 验证详情数据
      expect(result).toHaveProperty('id', activityId1);
      expect(result).toHaveProperty('type', 'walking');
      expect(result).toHaveProperty('description', '早晨散步');
    });
    
    test('3. 用户记录第二个活动', async () => {
      // 创建第二个活动
      const eveningActivity = {
        type: 'yoga',
        description: '晚间瑜伽',
        duration: 45,
        calories: 180,
        mood: '放松',
        tags: ['放松', '室内'],
        startTime: new Date().toISOString()
      };
      
      const response = await server.inject({
        method: 'POST',
        url: `/api/users/${testUserId}/activities`,
        payload: eveningActivity
      });
      
      // 验证创建成功
      expect(response.statusCode).toBe(201);
      const result = JSON.parse(response.payload);
      
      // 保存活动ID
      activityId2 = result.id;
      
      // 验证返回数据
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('userId', testUserId);
      expect(result).toHaveProperty('type', 'yoga');
      expect(result).toHaveProperty('duration', 45);
    });
    
    test('4. 用户查看当日活动摘要', async () => {
      // 等待1秒，确保摘要数据已更新
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const response = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/summary`,
        query: { period: 'day' }
      });
      
      // 验证请求成功
      expect(response.statusCode).toBe(200);
      const result = JSON.parse(response.payload);
      
      // 验证摘要数据
      expect(result).toHaveProperty('userId', testUserId);
      expect(result).toHaveProperty('totalActivities', 2);
      expect(result).toHaveProperty('totalDuration', 75); // 30 + 45
      expect(result).toHaveProperty('totalCalories', 300); // 120 + 180
      
      // 验证活动明细
      expect(result).toHaveProperty('activityBreakdown');
      expect(result.activityBreakdown.length).toBe(2);
      
      // 检查是否包含我们创建的两种活动
      const types = result.activityBreakdown.map(a => a.type);
      expect(types).toContain('walking');
      expect(types).toContain('yoga');
    });
    
    test('5. 用户获取活动建议', async () => {
      const response = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/recommendations`
      });
      
      // 验证请求成功
      expect(response.statusCode).toBe(200);
      const result = JSON.parse(response.payload);
      
      // 验证推荐数据
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      
      // 推荐中应该有对应我们已记录活动类型的建议
      const recommendedTypes = result.map(r => r.type);
      expect(recommendedTypes).toContain('walking');
      expect(recommendedTypes).toContain('yoga');
    });
    
    test('6. 验证活动删除场景', async () => {
      // 这个测试假设API提供了删除功能
      // 如果未实现，可以注释掉或跳过此测试
      
      // 1. 先尝试删除第一个活动
      const deleteResponse = await server.inject({
        method: 'DELETE',
        url: `/api/users/${testUserId}/activities/${activityId1}`
      });
      
      // 删除应该成功
      expect(deleteResponse.statusCode).toBe(200);
      
      // 2. 然后尝试获取已删除的活动
      const getResponse = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/${activityId1}`
      });
      
      // 应返回"未找到"错误
      expect(getResponse.statusCode).toBe(404);
      
      // 3. 再次检查活动摘要
      const summaryResponse = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/summary`,
        query: { period: 'day' }
      });
      
      // 验证摘要已更新
      const summary = JSON.parse(summaryResponse.payload);
      expect(summary.totalActivities).toBe(1); // 只剩一个活动
    }).skip(); // 如果删除API未实现，使用.skip()跳过此测试
  });
  
  // 测试错误场景
  describe('错误处理场景', () => {
    test('无效活动ID应返回404', async () => {
      const response = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/invalid-id-12345`
      });
      
      expect(response.statusCode).toBe(404);
    });
    
    test('无效活动数据应返回400', async () => {
      // 缺少必需字段的活动
      const invalidActivity = {
        type: 'walking',
        // 没有description和duration
      };
      
      const response = await server.inject({
        method: 'POST',
        url: `/api/users/${testUserId}/activities`,
        payload: invalidActivity
      });
      
      expect(response.statusCode).toBe(400);
      const error = JSON.parse(response.payload);
      expect(error.error).toHaveProperty('name', 'ValidationError');
    });
    
    test('无效的时间段参数应返回400', async () => {
      const response = await server.inject({
        method: 'GET',
        url: `/api/users/${testUserId}/activities/summary`,
        query: { period: 'invalid_period' }
      });
      
      expect(response.statusCode).toBe(400);
      const error = JSON.parse(response.payload);
      expect(error.error).toHaveProperty('name', 'ValidationError');
    });
  });
}); 