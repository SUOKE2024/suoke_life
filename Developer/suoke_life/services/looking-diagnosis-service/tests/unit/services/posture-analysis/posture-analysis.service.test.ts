import { PostureAnalysisService } from '../../../../src/services/posture-analysis/posture-analysis.service';
import { PostureAnalysisRepository } from '../../../../src/repositories/posture-analysis.repository';
import { PostureDiagnosis, PostureFeatures, TCMImplication } from '../../../../src/models/diagnosis/posture.model';
import fs from 'fs';
import path from 'path';

// 模拟依赖
jest.mock('../../../../src/repositories/posture-analysis.repository');
jest.mock('sharp', () => ({
  __esModule: true,
  default: jest.fn().mockReturnThis(),
  resize: jest.fn().mockReturnThis(),
  toFile: jest.fn().mockResolvedValue(undefined)
}));

describe('PostureAnalysisService', () => {
  let service: PostureAnalysisService;
  let repository: jest.Mocked<PostureAnalysisRepository>;
  
  const mockPostureDiagnosis: Partial<PostureDiagnosis> = {
    diagnosisId: 'test-id-123',
    sessionId: 'test-session-123',
    userId: 'test-user-123',
    timestamp: new Date(),
    features: {
      overallPosture: '正常',
      shoulderAlignment: '对称',
      spineAlignment: '正常',
      hipAlignment: '对称',
      hasForwardHeadPosture: false,
      hasRoundedShoulders: false,
      hasSwaybBack: false,
      hasFlatBack: false,
      posturalDeviation: 0,
      comments: '测试评注'
    },
    tcmImplications: [
      {
        concept: '平和体质',
        confidence: 0.9,
        explanation: '体态正常，无明显偏颇'
      }
    ],
    recommendations: ['保持良好姿势', '定期进行体态评估'],
    metadata: {
      processingSteps: ['图像预处理', '体态特征提取', 'TCM辨证分析']
    }
  } as Partial<PostureDiagnosis>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // 设置环境变量
    process.env.IMAGE_STORAGE_PATH = '/tmp/test-images';
    
    // 模拟文件系统操作
    jest.spyOn(fs, 'existsSync').mockReturnValue(true);
    jest.spyOn(fs, 'mkdirSync').mockImplementation(() => undefined);
    
    // 初始化存储库模拟
    repository = new PostureAnalysisRepository() as jest.Mocked<PostureAnalysisRepository>;
    repository.savePostureDiagnosis.mockResolvedValue(mockPostureDiagnosis as any);
    repository.getPostureDiagnosisById.mockResolvedValue(mockPostureDiagnosis as any);
    repository.getPostureDiagnosisByUserId.mockResolvedValue([mockPostureDiagnosis] as any);
    repository.getPostureDiagnosisBySessionId.mockResolvedValue([mockPostureDiagnosis] as any);
    
    // 创建服务实例
    service = new PostureAnalysisService(repository);
    
    // 模拟私有方法
    (service as any).extractPostureFeatures = jest.fn().mockResolvedValue(mockPostureDiagnosis.features);
    (service as any).generateTCMImplications = jest.fn().mockReturnValue(mockPostureDiagnosis.tcmImplications);
    (service as any).generateRecommendations = jest.fn().mockReturnValue(mockPostureDiagnosis.recommendations);
  });
  
  afterEach(() => {
    jest.resetAllMocks();
    delete process.env.IMAGE_STORAGE_PATH;
  });

  describe('analyzePosture', () => {
    it('应该处理图像并生成体态分析结果', async () => {
      // 准备测试数据
      const imageBase64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
      const sessionId = 'test-session-123';
      const userId = 'test-user-123';
      const metadata = { testKey: 'testValue' };
      
      // 执行方法
      const result = await service.analyzePosture(imageBase64, sessionId, userId, metadata);
      
      // 验证结果
      expect(result).toEqual(mockPostureDiagnosis);
      expect(repository.savePostureDiagnosis).toHaveBeenCalledTimes(1);
      
      // 验证传入savePostureDiagnosis的参数
      const savedData = repository.savePostureDiagnosis.mock.calls[0][0];
      expect(savedData.sessionId).toBe(sessionId);
      expect(savedData.userId).toBe(userId);
      expect(savedData.metadata).toEqual(expect.objectContaining({
        testKey: 'testValue',
        processingSteps: expect.any(Array)
      }));
    });
    
    it('应该处理异常并抛出有用的错误信息', async () => {
      // 设置模拟失败
      repository.savePostureDiagnosis.mockRejectedValue(new Error('数据库错误'));
      
      // 执行并验证异常
      await expect(
        service.analyzePosture('testImage', 'testSession', 'testUser')
      ).rejects.toThrow('体态分析失败');
    });
  });
  
  describe('getPostureDiagnosisById', () => {
    it('应该检索指定ID的体态诊断记录', async () => {
      const diagnosisId = 'test-id-123';
      const result = await service.getPostureDiagnosisById(diagnosisId);
      
      expect(repository.getPostureDiagnosisById).toHaveBeenCalledWith(diagnosisId);
      expect(result).toEqual(mockPostureDiagnosis);
    });
    
    it('应该处理异常并抛出有用的错误信息', async () => {
      repository.getPostureDiagnosisById.mockRejectedValue(new Error('数据库错误'));
      
      await expect(
        service.getPostureDiagnosisById('test-id')
      ).rejects.toThrow('获取体态诊断记录失败');
    });
  });
  
  describe('getPostureDiagnosisByUserId', () => {
    it('应该检索用户的体态诊断历史记录', async () => {
      const userId = 'test-user-123';
      const limit = 10;
      const offset = 0;
      
      const result = await service.getPostureDiagnosisByUserId(userId, limit, offset);
      
      expect(repository.getPostureDiagnosisByUserId).toHaveBeenCalledWith(userId, limit, offset);
      expect(result).toEqual([mockPostureDiagnosis]);
    });
  });
  
  describe('getPostureDiagnosisBySessionId', () => {
    it('应该检索会话的体态诊断历史记录', async () => {
      const sessionId = 'test-session-123';
      const limit = 10;
      const offset = 0;
      
      const result = await service.getPostureDiagnosisBySessionId(sessionId, limit, offset);
      
      expect(repository.getPostureDiagnosisBySessionId).toHaveBeenCalledWith(sessionId, limit, offset);
      expect(result).toEqual([mockPostureDiagnosis]);
    });
  });
});