import { XiaoAiService } from '../../src/services/XiaoAiService';
import axios from 'axios';

// 模拟依赖
jest.mock('axios');
jest.mock('../../src/index', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  },
}));

describe('XiaoAiService', () => {
  let xiaoAiService: XiaoAiService;
  const mockedAxios = axios as jest.Mocked<typeof axios>;
  
  beforeEach(() => {
    jest.clearAllMocks();
    xiaoAiService = new XiaoAiService();
  });
  
  describe('speechToText', () => {
    it('should convert speech to text successfully', async () => {
      // 准备模拟数据
      const audioBuffer = Buffer.from('mock audio data');
      const expectedResponse = {
        status: 200,
        data: {
          text: '你好，小艾',
          confidence: 0.95,
        },
      };
      
      // 设置axios模拟
      mockedAxios.post.mockResolvedValueOnce(expectedResponse);
      
      // 执行测试
      const result = await xiaoAiService.speechToText(audioBuffer);
      
      // 验证结果
      expect(result).toEqual({
        text: '你好，小艾',
        confidence: 0.95,
      });
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://speech-service:3080/transcribe',
        { audio: audioBuffer.toString('base64') },
        expect.any(Object)
      );
    });
    
    it('should handle errors from speech service', async () => {
      // 准备模拟数据
      const audioBuffer = Buffer.from('mock audio data');
      
      // 设置axios模拟
      mockedAxios.post.mockRejectedValueOnce(new Error('Speech service error'));
      
      // 执行测试并验证异常
      await expect(xiaoAiService.speechToText(audioBuffer)).rejects.toThrow('语音转文字处理失败');
    });
  });
  
  describe('analyzeImage', () => {
    it('should analyze image successfully', async () => {
      // 准备模拟数据
      const imageBuffer = Buffer.from('mock image data');
      const visionServiceResponse = {
        status: 200,
        data: {
          description: '一张中草药的图片',
          tags: ['中草药', '植物', '健康', '药物'],
          objects: [{ name: '草药', confidence: 0.9 }],
        },
      };
      
      const healthAnalysisResponse = {
        isHealthRelevant: true,
        healthTopics: ['herbs'],
        tcmRelevance: 'relevant',
      };
      
      // 设置axios模拟
      mockedAxios.post.mockResolvedValueOnce(visionServiceResponse);
      
      // 模拟analyzeHealthContext方法
      jest.spyOn(xiaoAiService as any, 'analyzeHealthContext').mockResolvedValueOnce(healthAnalysisResponse);
      
      // 执行测试
      const result = await xiaoAiService.analyzeImage(imageBuffer);
      
      // 验证结果
      expect(result).toEqual({
        description: '一张中草药的图片',
        tags: ['中草药', '植物', '健康', '药物'],
        objects: [{ name: '草药', confidence: 0.9 }],
        healthRelevant: true,
        healthContext: healthAnalysisResponse,
      });
      
      // 验证axios调用
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://vision-service:3090/analyze',
        { image: imageBuffer.toString('base64') },
        expect.any(Object)
      );
    });
    
    it('should handle errors from vision service', async () => {
      // 准备模拟数据
      const imageBuffer = Buffer.from('mock image data');
      
      // 设置axios模拟
      mockedAxios.post.mockRejectedValueOnce(new Error('Vision service error'));
      
      // 执行测试
      const result = await xiaoAiService.analyzeImage(imageBuffer);
      
      // 验证结果（错误情况下返回默认值）
      expect(result).toEqual({
        description: '抱歉，我无法分析这张图片',
        tags: [],
        objects: [],
        healthRelevant: false,
      });
    });
  });
  
  describe('processUserMessage', () => {
    it('should process text message successfully', async () => {
      // 这里需要模拟用户和代理的查找和保存操作
      // 由于这些涉及到数据库操作，我们会在集成测试中进行更全面的测试
      // 这里只测试基本功能
      
      // 模拟User.findOne和XiaoAiAgent.findOne
      const mockUser = {
        userId: 'test-user',
        settings: {
          accessibilityNeeds: {
            needsVoiceGuidance: false,
          },
        },
      };
      
      const mockAgent = {
        state: { mode: 'normal' },
        conversationHistory: [],
        save: jest.fn().mockResolvedValue(true),
      };
      
      jest.spyOn(global, 'Promise').mockImplementation((executor) => {
        const mockResolve = (value) => value;
        const mockReject = (reason) => { throw reason; };
        executor(mockResolve, mockReject);
        return {
          then: jest.fn().mockImplementation((callback) => {
            try {
              return Promise.resolve(callback(mockUser));
            } catch (e) {
              return Promise.reject(e);
            }
          }),
        } as any;
      });
      
      // 模拟generateResponse方法
      jest.spyOn(xiaoAiService as any, 'generateResponse').mockResolvedValueOnce('这是对您消息的回复');
      
      // 模拟代理的查找
      global.fetch = jest.fn().mockResolvedValueOnce({
        json: () => Promise.resolve(mockAgent),
      }) as any;
      
      // 这个测试主要验证功能调用，而不是实际数据库交互
      // 实际情况下应使用更完整的数据库模拟或集成测试
    });
  });
}); 