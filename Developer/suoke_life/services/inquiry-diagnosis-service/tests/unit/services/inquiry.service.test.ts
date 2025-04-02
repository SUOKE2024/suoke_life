import 'reflect-metadata';
import { Container } from 'typedi';
import { InquiryService } from '../../../src/services/inquiry.service';
import { LLMService } from '../../../src/integrations/llm.service';
import { NLPService } from '../../../src/integrations/nlp.service';
import { InquirySessionRepository } from '../../../src/db/repositories/inquiry-session.repository';
import { 
  InquiryNotFoundException, 
  InquirySessionCompletedException 
} from '../../../src/exceptions/business.exception';

// 模拟依赖
jest.mock('../../../src/integrations/llm.service');
jest.mock('../../../src/integrations/nlp.service');
jest.mock('../../../src/db/repositories/inquiry-session.repository');

describe('InquiryService', () => {
  let inquiryService: InquiryService;
  let mockLLMService: jest.Mocked<LLMService>;
  let mockNLPService: jest.Mocked<NLPService>;
  let mockInquirySessionRepository: jest.Mocked<InquirySessionRepository>;

  beforeEach(() => {
    // 清除容器，确保测试隔离
    Container.reset();

    // 设置模拟实例
    mockLLMService = {
      generateResponse: jest.fn(),
    } as unknown as jest.Mocked<LLMService>;

    mockNLPService = {
      extractSymptoms: jest.fn(),
      generateFollowUpQuestions: jest.fn(),
    } as unknown as jest.Mocked<NLPService>;

    mockInquirySessionRepository = {
      create: jest.fn(),
      findById: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      findByUserId: jest.fn(),
    } as unknown as jest.Mocked<InquirySessionRepository>;

    // 注册模拟实例到容器
    Container.set(LLMService, mockLLMService);
    Container.set(NLPService, mockNLPService);
    Container.set(InquirySessionRepository, mockInquirySessionRepository);

    // 获取服务实例
    inquiryService = Container.get(InquiryService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createSession', () => {
    it('应成功创建问诊会话', async () => {
      // 准备测试数据
      const userId = 'user123';
      const patientInfo = { age: 30, gender: 'male' };
      const preferences = { language: 'zh-CN' };
      
      const mockSession = {
        sessionId: 'session123',
        userId,
        status: 'active',
        patientInfo,
        preferences,
        exchanges: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      // 设置模拟返回值
      mockInquirySessionRepository.create.mockResolvedValue(mockSession);
      
      // 调用被测方法
      const result = await inquiryService.createSession(userId, patientInfo, preferences);
      
      // 验证结果
      expect(result).toEqual(mockSession);
      expect(mockInquirySessionRepository.create).toHaveBeenCalledWith({
        userId,
        patientInfo,
        preferences,
      });
    });

    it('创建会话时出现错误应抛出异常', async () => {
      // 设置模拟抛出错误
      mockInquirySessionRepository.create.mockRejectedValue(new Error('数据库错误'));
      
      // 验证异常被抛出
      await expect(
        inquiryService.createSession('user123', {}, {})
      ).rejects.toThrow('数据库错误');
    });
  });

  describe('processInquiry', () => {
    it('应成功处理问诊请求并返回响应', async () => {
      // 准备测试数据
      const sessionId = 'session123';
      const userId = 'user123';
      const questionContent = '我最近头痛得厉害，而且有点发热';
      
      const mockSession = {
        sessionId,
        userId,
        status: 'active',
        exchanges: [],
        patientInfo: {},
        preferences: {},
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      const mockExtractedSymptoms = ['头痛', '发热'];
      const mockResponse = '根据您的描述，您可能有感冒症状。请问您的头痛是持续性的还是间歇性的？';
      const mockFollowUpQuestions = ['头痛是持续性的还是间歇性的？', '有没有其他不适？'];
      
      // 设置模拟返回值
      mockInquirySessionRepository.findById.mockResolvedValue(mockSession);
      mockNLPService.extractSymptoms.mockResolvedValue(mockExtractedSymptoms);
      mockLLMService.generateResponse.mockResolvedValue(mockResponse);
      mockNLPService.generateFollowUpQuestions.mockResolvedValue(mockFollowUpQuestions);
      mockInquirySessionRepository.update.mockResolvedValue({
        ...mockSession,
        exchanges: [{
          question: { content: questionContent, timestamp: expect.any(Date) },
          response: { 
            content: mockResponse, 
            extractedSymptoms: mockExtractedSymptoms,
            suggestedFollowUp: mockFollowUpQuestions,
            timestamp: expect.any(Date) 
          },
          exchangeId: expect.any(String)
        }]
      });
      
      // 调用被测方法
      const result = await inquiryService.processInquiry(userId, sessionId, questionContent);
      
      // 验证结果
      expect(result).toHaveProperty('response.content', mockResponse);
      expect(result).toHaveProperty('response.extractedSymptoms', mockExtractedSymptoms);
      expect(result).toHaveProperty('response.suggestedFollowUp', mockFollowUpQuestions);
      expect(mockInquirySessionRepository.findById).toHaveBeenCalledWith(sessionId);
      expect(mockNLPService.extractSymptoms).toHaveBeenCalledWith(questionContent);
      expect(mockLLMService.generateResponse).toHaveBeenCalled();
      expect(mockInquirySessionRepository.update).toHaveBeenCalled();
    });

    it('会话不存在时应抛出异常', async () => {
      // 设置模拟返回null表示会话不存在
      mockInquirySessionRepository.findById.mockResolvedValue(null);
      
      // 验证异常被抛出
      await expect(
        inquiryService.processInquiry('user123', 'nonexistent-session', '我头痛')
      ).rejects.toThrow(InquiryNotFoundException);
    });

    it('会话已完成时应抛出异常', async () => {
      // 准备已完成的会话
      const mockCompletedSession = {
        sessionId: 'completed-session',
        userId: 'user123',
        status: 'completed',
        exchanges: [],
        patientInfo: {},
        preferences: {},
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      // 设置模拟返回值
      mockInquirySessionRepository.findById.mockResolvedValue(mockCompletedSession);
      
      // 验证异常被抛出
      await expect(
        inquiryService.processInquiry('user123', 'completed-session', '我头痛')
      ).rejects.toThrow(InquirySessionCompletedException);
    });
  });

  // 更多测试...
}); 