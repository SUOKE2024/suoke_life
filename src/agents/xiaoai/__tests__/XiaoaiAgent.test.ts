import { xiaoaiAgent } from '../XiaoaiAgent';
import { ChatContext, UserProfile } from '../types';

// Mock 四诊服务客户端
jest.mock('../services/DiagnosisServiceClient', () => ({
  diagnosisServiceClient: {
    inquiry: {
      startSession: jest.fn().mockResolvedValue({ session_id: 'test_session' }),
      interact: jest.fn().mockResolvedValue({ response: 'test_response' }),
      endSession: jest.fn().mockResolvedValue({
        sessionId: 'test_session',
        detectedSymptoms: [],
        tcmPatterns: [],
        healthProfile: {},
        recommendations: [],
        confidence: 0.8
      })
    },
    look: {
      analyzeImage: jest.fn().mockResolvedValue({
        analysisId: 'test_analysis',
        overallAssessment: '测试分析结果',
        confidence: 0.8
      })
    },
    listen: {
      analyzeAudio: jest.fn().mockResolvedValue({
        analysisId: 'test_analysis',
        voiceFeatures: {},
        emotionalState: {},
        overallAssessment: '测试分析结果',
        confidence: 0.8
      })
    },
    palpation: {
      analyzePalpation: jest.fn().mockResolvedValue({
        analysisId: 'test_analysis',
        overallAssessment: '测试分析结果',
        confidence: 0.8
      })
    },
    healthCheck: jest.fn().mockResolvedValue({
      inquiry: true,
      look: true,
      listen: true,
      palpation: true
    })
  }
}));

describe('XiaoaiAgent', () => {
  const mockContext: ChatContext = {
    userId: 'test_user',
    sessionId: 'test_session',
    conversationHistory: [],
    timestamp: Date.now()
  };

  const mockUserProfile: UserProfile = {
    id: 'test_user',
    basicInfo: {
      age: 30,
      gender: 'male',
      height: 175,
      weight: 70
    },
    medicalHistory: [],
    preferences: {
      language: 'zh-CN',
      communicationStyle: 'caring',
      diagnosisPreferences: {
        autoStartDiagnosis: false,
        preferredDiagnosisTypes: [],
        privacyLevel: 'medium'
      }
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('chat', () => {
    it('应该能够处理基本的聊天消息', async () => {
      const response = await xiaoaiAgent.chat('你好', mockContext);
      
      expect(response).toBeDefined();
      expect(response.text).toContain('亲爱的朋友');
      expect(response.timestamp).toBeDefined();
    });

    it('应该能够识别症状相关的消息', async () => {
      const response = await xiaoaiAgent.chat('我最近头痛', mockContext);
      
      expect(response).toBeDefined();
      expect(response.text).toContain('头痛');
      expect(response.suggestions).toBeDefined();
    });

    it('应该能够处理多模态输入', async () => {
      const contextWithImage: ChatContext = {
        ...mockContext,
        hasImages: true,
        images: [{
          id: 'test_image',
          type: 'tongue',
          uri: 'test://image.jpg',
          metadata: {
            width: 100,
            height: 100,
            timestamp: Date.now()
          }
        }]
      };

      const response = await xiaoaiAgent.chat('帮我看看舌头', contextWithImage);
      
      expect(response).toBeDefined();
      expect(response.text).toContain('图片');
    });
  });

  describe('generateSuggestions', () => {
    it('应该能够基于用户年龄生成建议', async () => {
      const suggestions = await xiaoaiAgent.generateSuggestions(mockUserProfile);
      
      expect(suggestions).toBeDefined();
      expect(Array.isArray(suggestions)).toBe(true);
    });

    it('应该为40岁以上用户生成体检建议', async () => {
      const olderProfile = {
        ...mockUserProfile,
        basicInfo: { ...mockUserProfile.basicInfo, age: 45 }
      };

      const suggestions = await xiaoaiAgent.generateSuggestions(olderProfile);
      
      const checkupSuggestion = suggestions.find(s => s.title.includes('体检'));
      expect(checkupSuggestion).toBeDefined();
      expect(checkupSuggestion?.priority).toBe('high');
    });

    it('应该为女性用户生成铁质补充建议', async () => {
      const femaleProfile = {
        ...mockUserProfile,
        basicInfo: { ...mockUserProfile.basicInfo, gender: 'female' as const }
      };

      const suggestions = await xiaoaiAgent.generateSuggestions(femaleProfile);
      
      const ironSuggestion = suggestions.find(s => s.title.includes('铁质'));
      expect(ironSuggestion).toBeDefined();
    });
  });

  describe('四诊功能', () => {
    it('应该能够启动问诊会话', async () => {
      const result = await xiaoaiAgent.startInquirySession('test_user');
      
      expect(result).toBeDefined();
      expect(result.session_id).toBe('test_session');
    });

    it('应该能够分析图像', async () => {
      const imageData = {
        id: 'test_image',
        type: 'tongue' as const,
        uri: 'test://image.jpg'
      };

      const result = await xiaoaiAgent.analyzeImage(imageData, 'tongue');
      
      expect(result).toBeDefined();
      expect(result.analysisId).toBe('test_analysis');
    });

    it('应该能够分析音频', async () => {
      const audioData = {
        id: 'test_audio',
        type: 'voice' as const,
        uri: 'test://audio.mp3'
      };

      const result = await xiaoaiAgent.analyzeAudio(audioData, 'voice');
      
      expect(result).toBeDefined();
      expect(result.analysisId).toBe('test_analysis');
    });

    it('应该能够处理触诊数据', async () => {
      const palpationData = {
        id: 'test_palpation',
        type: 'pulse' as const,
        sensorData: { rate: 72, rhythm: 'regular' }
      };

      const result = await xiaoaiAgent.processPalpationData(palpationData);
      
      expect(result).toBeDefined();
      expect(result.analysisId).toBe('test_analysis');
    });
  });

  describe('无障碍功能', () => {
    it('应该能够获取无障碍状态', async () => {
      const status = await xiaoaiAgent.getAccessibilityStatus();
      
      expect(status).toBeDefined();
      expect(status.visual).toBeDefined();
      expect(status.hearing).toBeDefined();
      expect(status.motor).toBeDefined();
      expect(status.cognitive).toBeDefined();
    });

    it('应该能够适配视觉障碍界面', async () => {
      const adaptations = await xiaoaiAgent.adaptInterfaceForDisability({
        type: 'visual'
      });
      
      expect(adaptations).toBeDefined();
      expect(adaptations.fontSize).toBe('large');
      expect(adaptations.highContrast).toBe(true);
      expect(adaptations.screenReader).toBe(true);
    });
  });

  describe('健康状态监控', () => {
    it('应该能够获取健康状态', async () => {
      const status = await xiaoaiAgent.getHealthStatus();
      
      expect(status).toBeDefined();
      expect(status.agent).toBeDefined();
      expect(status.services).toBeDefined();
      expect(status.timestamp).toBeDefined();
    });
  });

  describe('个性化设置', () => {
    it('应该能够设置个性化特征', () => {
      const traits = {
        style: 'formal',
        tone: 'professional'
      };

      expect(() => {
        xiaoaiAgent.setPersonality(traits);
      }).not.toThrow();
    });
  });

  describe('错误处理', () => {
    it('应该能够正常处理症状消息', async () => {
      const response = await xiaoaiAgent.chat('我头痛', mockContext);
      
      expect(response).toBeDefined();
      expect(response.text).toContain('头痛');
      expect(response.suggestions).toBeDefined();
      expect(Array.isArray(response.suggestions)).toBe(true);
    });
  });

  describe('资源清理', () => {
    it('应该能够清理用户资源', async () => {
      await expect(xiaoaiAgent.cleanup('test_user')).resolves.not.toThrow();
    });
  });
}); 