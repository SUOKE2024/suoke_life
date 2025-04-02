import request from 'supertest';
import mongoose from 'mongoose';
import { app } from '../../../src/app';
import PostureDiagnosisModel from '../../../src/models/diagnosis/posture.model';
import fs from 'fs';
import path from 'path';

/**
 * 体态分析API集成测试
 * 注意：这些测试需要完整启动的应用
 */
describe('体态分析API集成测试', () => {
  // 保存生成的诊断ID用于后续测试
  let createdDiagnosisId: string;
  
  beforeAll(async () => {
    // 连接到测试数据库
    const mongoUri = process.env.MONGODB_URI_TEST || 'mongodb://localhost:27017/looking_diagnosis_test';
    await mongoose.connect(mongoUri);
    
    // 设置图片存储路径
    process.env.IMAGE_STORAGE_PATH = path.join(__dirname, '../../../temp/test-api-images');
    if (!fs.existsSync(process.env.IMAGE_STORAGE_PATH)) {
      fs.mkdirSync(process.env.IMAGE_STORAGE_PATH, { recursive: true });
    }
  });
  
  afterAll(async () => {
    // 清空测试数据
    await PostureDiagnosisModel.deleteMany({});
    
    // 关闭数据库连接
    await mongoose.connection.close();
  });
  
  beforeEach(async () => {
    // 每个测试前清空数据
    await PostureDiagnosisModel.deleteMany({});
  });
  
  // 测试图像数据
  const testImageBase64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
  
  describe('健康检查接口', () => {
    it('GET /api/looking-diagnosis/health 应返回服务状态', async () => {
      const response = await request(app)
        .get('/api/looking-diagnosis/health')
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.status).toBe('success');
      expect(response.body.message).toContain('服务运行正常');
    });
  });
  
  describe('体态分析接口', () => {
    it('POST /api/looking-diagnosis/posture 应处理体态分析请求', async () => {
      const response = await request(app)
        .post('/api/looking-diagnosis/posture')
        .send({
          imageBase64: testImageBase64,
          sessionId: 'api-test-session',
          userId: 'api-test-user',
          metadata: {
            captureTime: new Date().toISOString(),
            testType: 'api-integration'
          }
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('diagnosisId');
      expect(response.body.data).toHaveProperty('features');
      expect(response.body.data).toHaveProperty('tcmImplications');
      expect(response.body.data).toHaveProperty('recommendations');
      
      // 保存诊断ID用于后续测试
      createdDiagnosisId = response.body.data.diagnosisId;
    });
    
    it('应该验证必需参数', async () => {
      // 缺少必需参数imageBase64
      const response = await request(app)
        .post('/api/looking-diagnosis/posture')
        .send({
          sessionId: 'api-test-session',
          userId: 'api-test-user'
        })
        .expect('Content-Type', /json/)
        .expect(400);
      
      expect(response.body.success).toBe(false);
      expect(response.body.errors).toBeDefined();
    });
  });
  
  describe('体态分析检索接口', () => {
    // 先创建一条记录
    beforeEach(async () => {
      if (!createdDiagnosisId) {
        const response = await request(app)
          .post('/api/looking-diagnosis/posture')
          .send({
            imageBase64: testImageBase64,
            sessionId: 'api-test-session-retrieve',
            userId: 'api-test-user-retrieve'
          });
        
        createdDiagnosisId = response.body.data.diagnosisId;
      }
    });
    
    it('GET /api/looking-diagnosis/posture/:diagnosisId 应返回诊断记录', async () => {
      const response = await request(app)
        .get(`/api/looking-diagnosis/posture/${createdDiagnosisId}`)
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.diagnosisId).toBe(createdDiagnosisId);
    });
    
    it('对不存在的ID应返回404', async () => {
      const response = await request(app)
        .get('/api/looking-diagnosis/posture/non-existent-id')
        .expect('Content-Type', /json/)
        .expect(404);
      
      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('未找到');
    });
    
    it('GET /api/looking-diagnosis/posture/history 应返回用户历史', async () => {
      // 为同一用户创建多条记录
      const userId = 'api-test-user-history';
      
      await Promise.all([
        request(app)
          .post('/api/looking-diagnosis/posture')
          .send({
            imageBase64: testImageBase64,
            sessionId: 'session-1',
            userId
          }),
        request(app)
          .post('/api/looking-diagnosis/posture')
          .send({
            imageBase64: testImageBase64,
            sessionId: 'session-2',
            userId
          })
      ]);
      
      // 查询用户历史
      const response = await request(app)
        .get('/api/looking-diagnosis/posture/history')
        .query({ userId })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.data.length).toBe(2);
      expect(response.body.data[0].userId).toBe(userId);
      expect(response.body.data[1].userId).toBe(userId);
    });
    
    it('应支持按会话ID查询历史', async () => {
      const sessionId = 'api-test-session-history';
      
      // 创建两条记录
      await Promise.all([
        request(app)
          .post('/api/looking-diagnosis/posture')
          .send({
            imageBase64: testImageBase64,
            sessionId,
            userId: 'user-1'
          }),
        request(app)
          .post('/api/looking-diagnosis/posture')
          .send({
            imageBase64: testImageBase64,
            sessionId,
            userId: 'user-2'
          })
      ]);
      
      // 查询会话历史
      const response = await request(app)
        .get('/api/looking-diagnosis/posture/history')
        .query({ sessionId })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.data.length).toBe(2);
      expect(response.body.data[0].sessionId).toBe(sessionId);
      expect(response.body.data[1].sessionId).toBe(sessionId);
    });
    
    it('历史记录接口应支持分页', async () => {
      const userId = 'api-test-user-pagination';
      
      // 创建5条记录
      for (let i = 0; i < 5; i++) {
        await request(app)
          .post('/api/looking-diagnosis/posture')
          .send({
            imageBase64: testImageBase64,
            sessionId: `session-${i}`,
            userId
          });
      }
      
      // 查询第一页
      const response1 = await request(app)
        .get('/api/looking-diagnosis/posture/history')
        .query({ userId, limit: 2, offset: 0 })
        .expect(200);
      
      expect(response1.body.data.length).toBe(2);
      
      // 查询第二页
      const response2 = await request(app)
        .get('/api/looking-diagnosis/posture/history')
        .query({ userId, limit: 2, offset: 2 })
        .expect(200);
      
      expect(response2.body.data.length).toBe(2);
      
      // 确认两页内容不同
      const firstPageIds = response1.body.data.map(item => item.diagnosisId);
      const secondPageIds = response2.body.data.map(item => item.diagnosisId);
      
      expect(firstPageIds).not.toEqual(expect.arrayContaining(secondPageIds));
    });
  });
});