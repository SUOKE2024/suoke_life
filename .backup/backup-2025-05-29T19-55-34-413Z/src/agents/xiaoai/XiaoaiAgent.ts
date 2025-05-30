import {
import { XiaoaiChatDiagnosisIntegrator } from './core/XiaoaiChatDiagnosisIntegrator';
import { diagnosisServiceClient } from './services/DiagnosisServiceClient';
import { accessibilityServiceClient } from './services/AccessibilityServiceClient';


  XiaoaiAgent,
  ChatContext,
  ChatResponse,
  UserProfile,
  HealthRecommendation,
  ImageData,
  LookResult,
  AudioData,
  ListenResult,
  PalpationData,
  PalpationResult,
  FourDiagnosisResults,
  IntegratedDiagnosis,
  AccessibilityNeeds,
} from './types';

/**
 * 小艾智能体主类
 * 健康助手 & 首页聊天频道版主，具备完整的四诊能力和无障碍服务
 */
export class XiaoaiAgentImpl implements XiaoaiAgent {
  private diagnosisIntegrator: XiaoaiChatDiagnosisIntegrator;
  private personality: any = {
    style: 'caring', // 关怀型
    tone: 'warm',    // 温暖的语调
    expertise: 'health', // 健康专业
    patience: 'high',     // 高耐心
  };

  constructor() {
    this.diagnosisIntegrator = new XiaoaiChatDiagnosisIntegrator();
  }

  /**
   * 核心聊天功能 - 智能调用四诊服务
   */
  async chat(message: string, context: ChatContext): Promise<ChatResponse> {
    try {
      // 使用诊断集成器处理消息
      const response = await this.diagnosisIntegrator.processChatMessage(message, context);
      
      // 应用个性化风格
      response.text = this.applyPersonalityToResponse(response.text, context);
      
      return response;
    } catch (error) {
      console.error('小艾聊天处理失败:', error);
      return this.generateFallbackResponse(message, context);
    }
  }

  /**
   * 分析健康数据
   */
  async analyzeHealthData(data: any): Promise<any> {
    try {
      // 这里可以集成更复杂的健康数据分析逻辑
      const analysis = {
        summary: '健康数据分析完成',
        insights: [] as string[],
        recommendations: [] as string[],
        riskFactors: [] as string[],
        trends: [] as string[],
      };

      // 基于数据类型进行不同的分析
      if (data.vitalSigns) {
        analysis.insights.push('生命体征数据已分析');
      }

      if (data.symptoms) {
        analysis.insights.push(`检测到${data.symptoms.length}个症状`);
      }

      if (data.lifestyle) {
        analysis.insights.push('生活方式数据已评估');
      }

      return analysis;
    } catch (error) {
      console.error('健康数据分析失败:', error);
      throw error;
    }
  }

  /**
   * 生成个性化健康建议
   */
  async generateSuggestions(profile: UserProfile): Promise<HealthRecommendation[]> {
    const recommendations: HealthRecommendation[] = [];

    try {
      // 基于用户基本信息生成建议
      const { age, gender } = profile.basicInfo;
      
      // 年龄相关建议
      if (age >= 40) {
        recommendations.push({
          category: 'lifestyle',
          title: '定期体检',
          description: '建议每年进行一次全面体检，重点关注心血管和代谢指标',
          priority: 'high',
          timeframe: '每年一次',
        });
      }

      if (age >= 60) {
        recommendations.push({
          category: 'exercise',
          title: '适度运动',
          description: '建议进行低强度有氧运动，如散步、太极等',
          priority: 'medium',
          timeframe: '每周3-5次',
        });
      }

      // 性别相关建议
      if (gender === 'female') {
        recommendations.push({
          category: 'diet',
          title: '补充铁质',
          description: '注意补充铁质丰富的食物，预防贫血',
          priority: 'medium',
          timeframe: '日常饮食',
        });
      }

      // 基于病史生成建议
      if (profile.medicalHistory.length > 0) {
        recommendations.push({
          category: 'lifestyle',
          title: '疾病管理',
          description: '根据既往病史，建议定期随访和监测',
          priority: 'high',
          timeframe: '按医嘱执行',
        });
      }

      // 基于用户偏好调整建议
      if (profile.preferences.diagnosisPreferences.privacyLevel === 'high') {
        recommendations.forEach(rec => {
          rec.description = '建议咨询专业医生获取个性化指导';
        });
      }

      return recommendations;
    } catch (error) {
      console.error('生成健康建议失败:', error);
      return [];
    }
  }

  /**
   * 设置个性化特征
   */
  setPersonality(traits: any): void {
    this.personality = { ...this.personality, ...traits };
  }

  /**
   * 四诊功能集成
   */
  async startInquirySession(userId: string): Promise<any> {
    try {
      return await diagnosisServiceClient.inquiry.startSession(userId);
    } catch (error) {
      console.error('启动问诊会话失败:', error);
      throw error;
    }
  }

  async analyzeImage(imageData: ImageData, type: 'face' | 'tongue' | 'body'): Promise<LookResult> {
    try {
      // 确保图片类型正确
      const processedImageData = { ...imageData, type };
      return await diagnosisServiceClient.look.analyzeImage(processedImageData);
    } catch (error) {
      console.error('图像分析失败:', error);
      throw error;
    }
  }

  async analyzeAudio(audioData: AudioData, type: 'voice' | 'sound'): Promise<ListenResult> {
    try {
      // 确保音频类型正确，将'sound'映射为'other'
      const audioType: 'voice' | 'cough' | 'breathing' | 'other' = type === 'sound' ? 'other' : type as 'voice';
      const processedAudioData = { ...audioData, type: audioType };
      return await diagnosisServiceClient.listen.analyzeAudio(processedAudioData);
    } catch (error) {
      console.error('音频分析失败:', error);
      throw error;
    }
  }

  async processPalpationData(data: PalpationData): Promise<PalpationResult> {
    try {
      return await diagnosisServiceClient.palpation.analyzePalpation(data);
    } catch (error) {
      console.error('触诊数据处理失败:', error);
      throw error;
    }
  }

  async performFourDiagnosisIntegration(data: FourDiagnosisResults): Promise<IntegratedDiagnosis> {
    try {
      // 调用诊断集成器的四诊合参功能
      return await this.diagnosisIntegrator.performFourDiagnosisIntegration(data);
    } catch (error) {
      console.error('四诊合参失败:', error);
      throw error;
    }
  }

  /**
   * 无障碍功能
   */
  async enableAccessibilityFeature(feature: any): Promise<void> {
    try {
      console.log('启用无障碍功能:', feature);
      
      // 根据功能类型调用相应的无障碍服务
      if (feature.type === 'voice_assistance') {
        // 启用语音辅助功能
        await accessibilityServiceClient.manageAccessibilitySettings(
          feature.userId,
          { voice_assistance: true, ...feature.preferences },
          'update'
        );
      } else if (feature.type === 'screen_reader') {
        // 启用屏幕阅读功能
        await accessibilityServiceClient.manageAccessibilitySettings(
          feature.userId,
          { screen_reader: true, ...feature.preferences },
          'update'
        );
      } else if (feature.type === 'sign_language') {
        // 启用手语识别功能
        await accessibilityServiceClient.manageAccessibilitySettings(
          feature.userId,
          { sign_language: true, ...feature.preferences },
          'update'
        );
      }
      
    } catch (error) {
      console.error('启用无障碍功能失败:', error);
      throw error;
    }
  }

  async getAccessibilityStatus(): Promise<any> {
    try {
      // 检查无障碍服务健康状态
      const serviceHealthy = await accessibilityServiceClient.healthCheck();
      
      if (!serviceHealthy) {
        return {
          serviceAvailable: false,
          error: '无障碍服务不可用',
        };
      }

      // 获取当前无障碍功能状态
      return {
        serviceAvailable: true,
        visual: {
          screenReader: false,
          highContrast: false,
          magnification: false,
        },
        hearing: {
          captions: false,
          signLanguage: false,
          audioDescription: false,
        },
        motor: {
          voiceControl: false,
          eyeTracking: false,
          switchControl: false,
        },
        cognitive: {
          simplifiedInterface: false,
          reminders: false,
          navigationAssist: false,
        },
      };
    } catch (error) {
      console.error('获取无障碍状态失败:', error);
      throw error;
    }
  }

  async adaptInterfaceForDisability(disability: any): Promise<any> {
    try {
      // 使用无障碍服务客户端进行界面适配
      const accessibilityNeeds = {
        visual: disability.type === 'visual',
        hearing: disability.type === 'hearing',
        motor: disability.type === 'motor',
        cognitive: disability.type === 'cognitive',
        preferences: {
          fontSize: disability.fontSize || 'large',
          highContrast: disability.highContrast || true,
          voiceOutput: disability.voiceOutput || true,
          simplifiedInterface: disability.simplifiedInterface || true,
        },
      };

      const adaptations = await accessibilityServiceClient.adaptInterfaceForAccessibility(accessibilityNeeds);
      
      // 根据障碍类型返回相应的适配方案
      switch (disability.type) {
        case 'visual':
          return adaptations.visual;
        case 'hearing':
          return adaptations.hearing;
        case 'motor':
          return adaptations.motor;
        case 'cognitive':
          return adaptations.cognitive;
        default:
          return adaptations;
      }
    } catch (error) {
      console.error('界面适配失败:', error);
      throw error;
    }
  }

  /**
   * 私有辅助方法
   */
  private applyPersonalityToResponse(text: string, context: ChatContext): string {
    // 根据个性化设置调整回复风格
    let personalizedText = text;

    if (this.personality.style === 'caring') {
      // 添加关怀性的表达
      if (!text.includes('亲爱的') && !text.includes('您好')) {
        personalizedText = '亲爱的朋友，' + personalizedText;
      }
    }

    if (this.personality.tone === 'warm') {
      // 使用温暖的语调
      personalizedText = personalizedText.replace(/。/g, '呢。');
      personalizedText = personalizedText.replace(/！/g, '哦！');
    }

    // 根据用户偏好调整
    if (context.userProfile?.preferences.communicationStyle === 'formal') {
      personalizedText = personalizedText.replace(/亲爱的朋友/g, '您');
      personalizedText = personalizedText.replace(/呢。/g, '。');
    }

    return personalizedText;
  }

  private generateFallbackResponse(message: string, context: ChatContext): ChatResponse {
    return {
      text: '抱歉，我现在遇到了一些技术问题。不过别担心，我还是很愿意帮助你的！你可以尝试重新描述一下你的问题，或者稍后再试。',
      suggestions: [
        '重新描述问题',
        '查看健康建议',
        '联系技术支持',
        '稍后再试',
      ],
      timestamp: Date.now(),
    };
  }

  /**
   * 健康检查和状态监控
   */
  async getHealthStatus(): Promise<any> {
    try {
      const serviceHealth = await diagnosisServiceClient.healthCheck();
      
      return {
        agent: {
          status: 'healthy',
          personality: this.personality,
          activeSessions: this.diagnosisIntegrator.getActiveSessionsStatus('current_user'),
        },
        services: serviceHealth,
        timestamp: Date.now(),
      };
    } catch (error) {
      console.error('获取健康状态失败:', error);
             return {
         agent: {
           status: 'error',
           error: (error as Error).message,
         },
         timestamp: Date.now(),
       };
    }
  }

  /**
   * 清理资源
   */
  async cleanup(userId: string): Promise<void> {
    try {
      await this.diagnosisIntegrator.cleanupSession(userId);
    } catch (error) {
      console.error('清理资源失败:', error);
    }
  }
}

// 创建单例实例
export const xiaoaiAgent = new XiaoaiAgentImpl(); 