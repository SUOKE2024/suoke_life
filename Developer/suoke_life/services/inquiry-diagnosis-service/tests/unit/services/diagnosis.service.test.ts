import 'reflect-metadata';
import { Container } from 'typedi';
import { DiagnosisService } from '../../../src/services/diagnosis.service';
import { TCMAnalysisService } from '../../../src/services/tcm-analysis.service';
import { DiagnosisResultRepository } from '../../../src/db/repositories/diagnosis-result.repository';
import { InquirySessionRepository } from '../../../src/db/repositories/inquiry-session.repository';
import { 
  DiagnosisNotFoundException, 
  InsufficientDataException,
  InquiryNotFoundException
} from '../../../src/exceptions/business.exception';

// 模拟依赖
jest.mock('../../../src/services/tcm-analysis.service');
jest.mock('../../../src/db/repositories/diagnosis-result.repository');
jest.mock('../../../src/db/repositories/inquiry-session.repository');

describe('DiagnosisService', () => {
  let diagnosisService: DiagnosisService;
  let mockTCMAnalysisService: jest.Mocked<TCMAnalysisService>;
  let mockDiagnosisResultRepository: jest.Mocked<DiagnosisResultRepository>;
  let mockInquirySessionRepository: jest.Mocked<InquirySessionRepository>;

  beforeEach(() => {
    // 清除容器，确保测试隔离
    Container.reset();

    // 设置模拟实例
    mockTCMAnalysisService = {
      performPatternDifferentiation: jest.fn(),
      categorizeSymptoms: jest.fn(),
      analyzeConstitution: jest.fn(),
      generateRecommendations: jest.fn(),
    } as unknown as jest.Mocked<TCMAnalysisService>;

    mockDiagnosisResultRepository = {
      create: jest.fn(),
      findById: jest.fn(),
      findBySessionId: jest.fn(),
      findByUserId: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    } as unknown as jest.Mocked<DiagnosisResultRepository>;

    mockInquirySessionRepository = {
      findById: jest.fn(),
      update: jest.fn(),
    } as unknown as jest.Mocked<InquirySessionRepository>;

    // 注册模拟实例到容器
    Container.set(TCMAnalysisService, mockTCMAnalysisService);
    Container.set(DiagnosisResultRepository, mockDiagnosisResultRepository);
    Container.set(InquirySessionRepository, mockInquirySessionRepository);

    // 获取服务实例
    diagnosisService = Container.get(DiagnosisService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createDiagnosis', () => {
    it('应成功创建诊断并返回结果', async () => {
      // 准备测试数据
      const sessionId = 'session123';
      const userId = 'user123';
      
      const mockSession = {
        sessionId,
        userId,
        status: 'active',
        exchanges: [
          {
            question: { content: '我头痛发热', timestamp: new Date() },
            response: { 
              content: '您可能感冒了', 
              extractedSymptoms: ['头痛', '发热'],
              timestamp: new Date() 
            },
            exchangeId: 'exchange1'
          }
        ],
        patientInfo: { age: 30, gender: 'male' },
        preferences: {},
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      const mockTCMPatterns = [
        { 
          name: '风热感冒', 
          confidence: 0.85, 
          description: '风热感冒描述', 
          symptoms: ['头痛', '发热', '喉咙痛'] 
        }
      ];
      
      const mockCategorizedSymptoms = [
        { category: '头面', symptoms: ['头痛'] },
        { category: '其他', symptoms: ['发热'] }
      ];
      
      const mockConstitution = {
        primaryType: '阳虚质',
        secondaryTypes: ['气虚质'],
        description: '阳虚体质描述',
        constitutionScore: { '阳虚质': 0.8, '气虚质': 0.6 }
      };
      
      const mockRecommendations = [
        { 
          category: 'diet', 
          content: '多吃温热食物', 
          importance: 'high' as const
        }
      ];
      
      const mockDiagnosisResult = {
        diagnosisId: 'diagnosis123',
        sessionId,
        userId,
        timestamp: expect.any(Date),
        tcmPatterns: mockTCMPatterns,
        categorizedSymptoms: mockCategorizedSymptoms,
        constitutionAnalysis: mockConstitution,
        recommendations: mockRecommendations,
        summary: expect.any(String),
        followUpQuestions: expect.any(Array),
        warningIndicators: expect.any(Array),
        confidence: expect.any(Number),
        metadata: expect.any(Object)
      };
      
      // 设置模拟返回值
      mockInquirySessionRepository.findById.mockResolvedValue(mockSession);
      mockTCMAnalysisService.performPatternDifferentiation.mockResolvedValue(mockTCMPatterns);
      mockTCMAnalysisService.categorizeSymptoms.mockResolvedValue(mockCategorizedSymptoms);
      mockTCMAnalysisService.analyzeConstitution.mockResolvedValue(mockConstitution);
      mockTCMAnalysisService.generateRecommendations.mockResolvedValue(mockRecommendations);
      mockDiagnosisResultRepository.create.mockResolvedValue(mockDiagnosisResult);
      
      // 调用被测方法
      const result = await diagnosisService.createDiagnosis({
        sessionId,
        userId,
        includeRecommendations: true
      });
      
      // 验证结果
      expect(result).toEqual(mockDiagnosisResult);
      expect(mockInquirySessionRepository.findById).toHaveBeenCalledWith(sessionId);
      expect(mockTCMAnalysisService.performPatternDifferentiation).toHaveBeenCalledWith(
        ['头痛', '发热'],
        userId
      );
      expect(mockTCMAnalysisService.categorizeSymptoms).toHaveBeenCalledWith(['头痛', '发热']);
      expect(mockTCMAnalysisService.analyzeConstitution).toHaveBeenCalledWith(
        ['头痛', '发热'],
        mockSession.patientInfo,
        userId
      );
      expect(mockTCMAnalysisService.generateRecommendations).toHaveBeenCalled();
      expect(mockDiagnosisResultRepository.create).toHaveBeenCalled();
    });

    it('会话不存在时应抛出异常', async () => {
      // 设置模拟返回null表示会话不存在
      mockInquirySessionRepository.findById.mockResolvedValue(null);
      
      // 验证异常被抛出
      await expect(
        diagnosisService.createDiagnosis({
          sessionId: 'nonexistent-session',
          userId: 'user123'
        })
      ).rejects.toThrow(InquiryNotFoundException);
    });

    it('症状不足时应抛出异常', async () => {
      // 准备无症状的会话
      const mockSessionWithoutSymptoms = {
        sessionId: 'session123',
        userId: 'user123',
        status: 'active',
        exchanges: [
          {
            question: { content: '你好', timestamp: new Date() },
            response: { 
              content: '您好，有什么可以帮助您的？', 
              extractedSymptoms: [],
              timestamp: new Date() 
            },
            exchangeId: 'exchange1'
          }
        ],
        patientInfo: {},
        preferences: {},
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      // 设置模拟返回值
      mockInquirySessionRepository.findById.mockResolvedValue(mockSessionWithoutSymptoms);
      
      // 验证异常被抛出
      await expect(
        diagnosisService.createDiagnosis({
          sessionId: 'session123',
          userId: 'user123'
        })
      ).rejects.toThrow(InsufficientDataException);
    });
  });

  describe('getDiagnosis', () => {
    it('应成功获取诊断结果', async () => {
      // 准备测试数据
      const diagnosisId = 'diagnosis123';
      const mockDiagnosisResult = {
        diagnosisId,
        sessionId: 'session123',
        userId: 'user123',
        timestamp: new Date(),
        tcmPatterns: [],
        categorizedSymptoms: [],
        constitutionAnalysis: {
          primaryType: '阳虚质',
          secondaryTypes: [],
          description: '',
          constitutionScore: {}
        },
        recommendations: [],
        summary: '',
        followUpQuestions: [],
        warningIndicators: [],
        confidence: 0.8,
        metadata: {}
      };
      
      // 设置模拟返回值
      mockDiagnosisResultRepository.findById.mockResolvedValue(mockDiagnosisResult);
      
      // 调用被测方法
      const result = await diagnosisService.getDiagnosis(diagnosisId);
      
      // 验证结果
      expect(result).toEqual(mockDiagnosisResult);
      expect(mockDiagnosisResultRepository.findById).toHaveBeenCalledWith(diagnosisId);
    });

    it('诊断不存在时应抛出异常', async () => {
      // 设置模拟返回null表示诊断不存在
      mockDiagnosisResultRepository.findById.mockResolvedValue(null);
      
      // 验证异常被抛出
      await expect(
        diagnosisService.getDiagnosis('nonexistent-diagnosis')
      ).rejects.toThrow(DiagnosisNotFoundException);
    });
  });

  // 更多测试...
}); 