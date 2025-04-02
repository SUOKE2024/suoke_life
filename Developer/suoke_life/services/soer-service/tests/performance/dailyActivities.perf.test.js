/**
 * 日常活动模块性能测试
 */
const DailyActivitiesService = require('../../src/services/dailyActivities.service');
const dbService = require('../../src/models/db.service');
const { 
  ACTIVITIES_TABLE, 
  ACTIVITY_METRICS_TABLE,
  createTables 
} = require('../../src/models/dailyActivities.model');

// 配置测试常量
const TEST_USER_ID = 'perf-test-user';
const BATCH_SIZE = 100; // 批量插入数量
const TEST_ITERATIONS = 5; // 测试重复次数

// 模拟配置
jest.mock('../../src/config', () => ({
  database: {
    host: process.env.TEST_DB_HOST || 'localhost',
    port: process.env.TEST_DB_PORT || 3306,
    user: process.env.TEST_DB_USER || 'test',
    password: process.env.TEST_DB_PASSWORD || 'test',
    name: process.env.TEST_DB_NAME || 'test_db',
    connectionLimit: 5
  }
}));

// 跳过性能测试，除非明确设置环境变量
const runPerfTests = process.env.RUN_PERF_TESTS === 'true';
(runPerfTests ? describe : describe.skip)('日常活动性能测试', () => {
  let service;
  
  // 设置测试
  beforeAll(async () => {
    // 连接数据库
    await dbService.connect();
    
    // 创建测试表
    await createTables(dbService);
    
    // 创建服务实例
    service = new DailyActivitiesService();
    
    // 清理测试数据
    await cleanupTestData();
    
    // 创建测试数据
    await createTestData();
  }, 60000); // 增加超时时间
  
  // 清理
  afterAll(async () => {
    // 清理测试数据
    await cleanupTestData();
    
    // 断开数据库连接
    await dbService.disconnect();
  });
  
  // 清理测试数据
  async function cleanupTestData() {
    try {
      await dbService.query(`DELETE FROM ${ACTIVITIES_TABLE} WHERE user_id = ?`, [TEST_USER_ID]);
      await dbService.query(`DELETE FROM ${ACTIVITY_METRICS_TABLE} WHERE user_id = ?`, [TEST_USER_ID]);
    } catch (error) {
      console.error('清理测试数据失败:', error);
    }
  }
  
  // 创建测试数据
  async function createTestData() {
    console.log(`创建${BATCH_SIZE}条测试活动记录...`);
    
    // 创建多个活动记录
    const activityTypes = ['walking', 'running', 'cycling', 'swimming', 'yoga', 'meditation'];
    const randomActivities = [];
    
    // 生成随机时间
    function randomDate(start, end) {
      return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
    }
    
    // 设置日期范围（过去30天）
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    // 生成活动数据
    for (let i = 0; i < BATCH_SIZE; i++) {
      const type = activityTypes[Math.floor(Math.random() * activityTypes.length)];
      const duration = Math.floor(Math.random() * 120) + 15; // 15-135分钟
      const distance = type === 'meditation' || type === 'yoga' ? 0 : Math.random() * 10;
      const calories = Math.floor(Math.random() * 500) + 50;
      
      // 创建随机的开始时间
      const activityDate = randomDate(startDate, endDate);
      
      randomActivities.push({
        type,
        description: `性能测试活动 #${i+1}`,
        duration,
        distance,
        calories,
        startTime: activityDate.toISOString(),
        tags: [`test-${i % 5}`, 'performance']
      });
    }
    
    // 批量记录活动
    for (const activity of randomActivities) {
      await service.recordActivity(TEST_USER_ID, activity);
    }
    
    console.log(`已创建${BATCH_SIZE}条测试活动记录`);
  }
  
  // 性能测试: 获取日常摘要
  describe('getActivitySummary性能', () => {
    test('应快速获取日活动摘要', async () => {
      console.log('\n测试日活动摘要性能...');
      const times = [];
      
      for (let i = 0; i < TEST_ITERATIONS; i++) {
        const startTime = process.hrtime();
        
        await service.getActivitySummary(TEST_USER_ID, 'day');
        
        const endTime = process.hrtime(startTime);
        const timeInMs = (endTime[0] * 1000) + (endTime[1] / 1000000);
        times.push(timeInMs);
        
        console.log(`迭代 ${i+1}: ${timeInMs.toFixed(2)}ms`);
      }
      
      // 计算性能统计
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`日活动摘要性能结果:
        平均: ${average.toFixed(2)}ms
        最小: ${min.toFixed(2)}ms
        最大: ${max.toFixed(2)}ms
      `);
      
      // 期望平均响应时间小于500ms
      expect(average).toBeLessThan(500);
    }, 30000);
    
    test('应快速获取周活动摘要', async () => {
      console.log('\n测试周活动摘要性能...');
      const times = [];
      
      for (let i = 0; i < TEST_ITERATIONS; i++) {
        const startTime = process.hrtime();
        
        await service.getActivitySummary(TEST_USER_ID, 'week');
        
        const endTime = process.hrtime(startTime);
        const timeInMs = (endTime[0] * 1000) + (endTime[1] / 1000000);
        times.push(timeInMs);
        
        console.log(`迭代 ${i+1}: ${timeInMs.toFixed(2)}ms`);
      }
      
      // 计算性能统计
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`周活动摘要性能结果:
        平均: ${average.toFixed(2)}ms
        最小: ${min.toFixed(2)}ms
        最大: ${max.toFixed(2)}ms
      `);
      
      // 期望平均响应时间小于1000ms
      expect(average).toBeLessThan(1000);
    }, 30000);
    
    test('应快速获取月活动摘要', async () => {
      console.log('\n测试月活动摘要性能...');
      const times = [];
      
      for (let i = 0; i < TEST_ITERATIONS; i++) {
        const startTime = process.hrtime();
        
        await service.getActivitySummary(TEST_USER_ID, 'month');
        
        const endTime = process.hrtime(startTime);
        const timeInMs = (endTime[0] * 1000) + (endTime[1] / 1000000);
        times.push(timeInMs);
        
        console.log(`迭代 ${i+1}: ${timeInMs.toFixed(2)}ms`);
      }
      
      // 计算性能统计
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`月活动摘要性能结果:
        平均: ${average.toFixed(2)}ms
        最小: ${min.toFixed(2)}ms
        最大: ${max.toFixed(2)}ms
      `);
      
      // 期望平均响应时间小于1500ms
      expect(average).toBeLessThan(1500);
    }, 30000);
  });
  
  // 性能测试: 记录活动
  describe('recordActivity性能', () => {
    test('应快速记录新活动', async () => {
      console.log('\n测试记录活动性能...');
      const times = [];
      
      for (let i = 0; i < TEST_ITERATIONS; i++) {
        const activity = {
          type: 'walking',
          description: `性能测试 - 快速记录 #${i}`,
          duration: 30,
          distance: 2.5,
          calories: 120,
          startTime: new Date().toISOString()
        };
        
        const startTime = process.hrtime();
        
        await service.recordActivity(TEST_USER_ID, activity);
        
        const endTime = process.hrtime(startTime);
        const timeInMs = (endTime[0] * 1000) + (endTime[1] / 1000000);
        times.push(timeInMs);
        
        console.log(`迭代 ${i+1}: ${timeInMs.toFixed(2)}ms`);
      }
      
      // 计算性能统计
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`记录活动性能结果:
        平均: ${average.toFixed(2)}ms
        最小: ${min.toFixed(2)}ms
        最大: ${max.toFixed(2)}ms
      `);
      
      // 期望平均响应时间小于200ms
      expect(average).toBeLessThan(200);
    }, 30000);
  });
  
  // 性能测试: 获取活动详情
  describe('getActivityDetail性能', () => {
    test('应快速获取活动详情', async () => {
      console.log('\n测试获取活动详情性能...');
      
      // 先获取一个活动ID用于测试
      const activities = await dbService.query(
        `SELECT id FROM ${ACTIVITIES_TABLE} WHERE user_id = ? LIMIT 1`,
        [TEST_USER_ID]
      );
      
      if (activities.length === 0) {
        console.log('无法执行活动详情性能测试：没有可用的活动ID');
        return;
      }
      
      const testActivityId = activities[0].id;
      const times = [];
      
      for (let i = 0; i < TEST_ITERATIONS; i++) {
        const startTime = process.hrtime();
        
        await service.getActivityDetail(TEST_USER_ID, testActivityId);
        
        const endTime = process.hrtime(startTime);
        const timeInMs = (endTime[0] * 1000) + (endTime[1] / 1000000);
        times.push(timeInMs);
        
        console.log(`迭代 ${i+1}: ${timeInMs.toFixed(2)}ms`);
      }
      
      // 计算性能统计
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`获取活动详情性能结果:
        平均: ${average.toFixed(2)}ms
        最小: ${min.toFixed(2)}ms
        最大: ${max.toFixed(2)}ms
      `);
      
      // 期望平均响应时间小于100ms
      expect(average).toBeLessThan(100);
    }, 30000);
  });
  
  // 性能测试: 获取活动推荐
  describe('getActivityRecommendations性能', () => {
    test('应快速生成活动推荐', async () => {
      console.log('\n测试活动推荐性能...');
      const times = [];
      
      for (let i = 0; i < TEST_ITERATIONS; i++) {
        const startTime = process.hrtime();
        
        await service.getActivityRecommendations(TEST_USER_ID);
        
        const endTime = process.hrtime(startTime);
        const timeInMs = (endTime[0] * 1000) + (endTime[1] / 1000000);
        times.push(timeInMs);
        
        console.log(`迭代 ${i+1}: ${timeInMs.toFixed(2)}ms`);
      }
      
      // 计算性能统计
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      console.log(`活动推荐性能结果:
        平均: ${average.toFixed(2)}ms
        最小: ${min.toFixed(2)}ms
        最大: ${max.toFixed(2)}ms
      `);
      
      // 期望平均响应时间小于300ms
      expect(average).toBeLessThan(300);
    }, 30000);
  });
}); 