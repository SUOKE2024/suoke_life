import mongoose from 'mongoose';
import { Container } from 'typedi';
import { PostureAnalysisService } from '../../../src/services/posture-analysis/posture-analysis.service';
import { PostureAnalysisRepository } from '../../../src/repositories/posture-analysis.repository';
import PostureDiagnosisModel from '../../../src/models/diagnosis/posture.model';
import fs from 'fs';
import path from 'path';

/**
 * 体态分析服务集成测试
 * 注意：这些测试需要连接到MongoDB测试数据库
 */
describe('PostureAnalysisService集成测试', () => {
  let service: PostureAnalysisService;
  let repository: PostureAnalysisRepository;
  
  beforeAll(async () => {
    // 连接到测试数据库
    const mongoUri = process.env.MONGODB_URI_TEST || 'mongodb://localhost:27017/looking_diagnosis_test';
    await mongoose.connect(mongoUri);
    
    // 设置存储目录
    process.env.IMAGE_STORAGE_PATH = path.join(__dirname, '../../../temp/test-images');
    if (!fs.existsSync(process.env.IMAGE_STORAGE_PATH)) {
      fs.mkdirSync(process.env.IMAGE_STORAGE_PATH, { recursive: true });
    }
    
    // 创建实例
    repository = new PostureAnalysisRepository();
    service = new PostureAnalysisService(repository);
    
    // 注册到Container（用于依赖注入）
    Container.set(PostureAnalysisRepository, repository);
    Container.set(PostureAnalysisService, service);
  });
  
  afterAll(async () => {
    // 清空测试数据
    await PostureDiagnosisModel.deleteMany({});
    
    // 关闭数据库连接
    await mongoose.connection.close();
    
    // 清理环境变量
    delete process.env.IMAGE_STORAGE_PATH;
  });
  
  beforeEach(async () => {
    // 每个测试前清空数据
    await PostureDiagnosisModel.deleteMany({});
  });
  
  // 测试图像数据（1x1像素PNG的base64编码）
  const testImageBase64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
  
  it('应该创建体态分析记录并保存到数据库', async () => {
    // 设置测试参数
    const sessionId = `test-session-${Date.now()}`;
    const userId = `test-user-${Date.now()}`;
    const metadata = {
      captureTime: new Date(),
      testId: 'integration-test-1'
    };
    
    // 调用服务
    const result = await service.analyzePosture(testImageBase64, sessionId, userId, metadata);
    
    // 验证结果
    expect(result).toBeDefined();
    expect(result.diagnosisId).toBeDefined();
    expect(result.sessionId).toBe(sessionId);
    expect(result.userId).toBe(userId);
    expect(result.features).toBeDefined();
    expect(result.tcmImplications).toBeDefined();
    expect(result.recommendations).toBeDefined();
    expect(result.metadata).toHaveProperty('testId', 'integration-test-1');
    
    // 验证数据库保存
    const savedRecord = await PostureDiagnosisModel.findOne({ diagnosisId: result.diagnosisId });
    expect(savedRecord).not.toBeNull();
    expect(savedRecord?.sessionId).toBe(sessionId);
    expect(savedRecord?.features).toBeDefined();
  });
  
  it('应该按ID检索体态分析记录', async () => {
    // 先创建一条记录
    const initialResult = await service.analyzePosture(
      testImageBase64,
      'test-session-retrieve',
      'test-user-retrieve'
    );
    
    // 然后根据ID检索
    const retrievedResult = await service.getPostureDiagnosisById(initialResult.diagnosisId);
    
    // 验证结果
    expect(retrievedResult).not.toBeNull();
    expect(retrievedResult?.diagnosisId).toBe(initialResult.diagnosisId);
    expect(retrievedResult?.features).toEqual(initialResult.features);
  });
  
  it('应该检索用户的所有体态分析记录', async () => {
    // 创建多条记录
    const userId = `test-user-multiple-${Date.now()}`;
    
    await Promise.all([
      service.analyzePosture(testImageBase64, 'session-1', userId),
      service.analyzePosture(testImageBase64, 'session-2', userId),
      service.analyzePosture(testImageBase64, 'session-3', userId)
    ]);
    
    // 检索用户记录
    const userRecords = await service.getPostureDiagnosisByUserId(userId);
    
    // 验证结果
    expect(userRecords).toHaveLength(3);
    expect(userRecords[0].userId).toBe(userId);
    expect(userRecords[1].userId).toBe(userId);
    expect(userRecords[2].userId).toBe(userId);
  });
  
  it('应该检索会话的所有体态分析记录', async () => {
    // 创建多条记录
    const sessionId = `test-session-multiple-${Date.now()}`;
    
    await Promise.all([
      service.analyzePosture(testImageBase64, sessionId, 'user-1'),
      service.analyzePosture(testImageBase64, sessionId, 'user-2')
    ]);
    
    // 检索会话记录
    const sessionRecords = await service.getPostureDiagnosisBySessionId(sessionId);
    
    // 验证结果
    expect(sessionRecords).toHaveLength(2);
    expect(sessionRecords[0].sessionId).toBe(sessionId);
    expect(sessionRecords[1].sessionId).toBe(sessionId);
  });
  
  it('应该生成有效的TCM含义和健康建议', async () => {
    const result = await service.analyzePosture(
      testImageBase64,
      'test-session-tcm',
      'test-user-tcm'
    );
    
    // 验证TCM含义
    expect(Array.isArray(result.tcmImplications)).toBe(true);
    expect(result.tcmImplications.length).toBeGreaterThan(0);
    expect(result.tcmImplications[0]).toHaveProperty('concept');
    expect(result.tcmImplications[0]).toHaveProperty('confidence');
    expect(result.tcmImplications[0]).toHaveProperty('explanation');
    
    // 验证健康建议
    expect(Array.isArray(result.recommendations)).toBe(true);
    expect(result.recommendations.length).toBeGreaterThan(0);
  });
});