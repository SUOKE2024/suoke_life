import { XiaoaiChatDiagnosisIntegrator } from './core/XiaoaiChatDiagnosisIntegrator';
import { accessibilityServiceClient } from './services/AccessibilityServiceClient';
import { diagnosisServiceClient } from './services/DiagnosisServiceClient';

// 基础类型定义
interface ChatContext {
  userId: string;
  sessionId?: string;
  hasImages?: boolean;
  hasAudio?: boolean;
  hasPalpationData?: boolean;
  accessibilityNeeds?: AccessibilityNeeds;
}

interface ChatResponse {
  text: string;
  suggestions?: string[];
  requiresFollowUp?: boolean;
  diagnosisIntent?: boolean;
  confidence?: number;
}

interface UserProfile {
  id: string;
  basicInfo: {
    age: number;
    gender: string;
    name: string;
  };
  medicalHistory: string[];
  preferences: {
    diagnosisPreferences: {
      privacyLevel: string;
    };
  };
}

interface HealthRecommendation {
  category: string;
  title: string;
  description: string;
  priority: string;
  timeframe: string;
}

interface ImageData {
  data: ArrayBuffer;
  format: string;
  width: number;
  height: number;
  type?: string;
}

interface AudioData {
  data: ArrayBuffer;
  format: string;
  duration: number;
  type?: string;
}

interface PalpationData {
  type: string;
  sensorData: Record<string, any>;
  timestamp: number;
}

interface LookResult {
  analysis: string;
  features: Array<{
    type: string;
    description: string;
    confidence: number;
  }>;
  confidence: number;
  recommendations: string[];
}

interface ListenResult {
  analysis: string;
  features: Array<{
    type: string;
    description: string;
    confidence: number;
  }>;
  confidence: number;
  recommendations: string[];
}

interface PalpationResult {
  analysis: string;
  measurements: Record<string, any>;
  confidence: number;
  recommendations: string[];
}

interface FourDiagnosisResults {
  inquiry?: any;
  look?: LookResult;
  listen?: ListenResult;
  palpation?: PalpationResult;
}

interface IntegratedDiagnosis {
  summary: string;
  confidence: number;
  recommendations: string[];
  syndrome?: string;
  treatment?: string;
}

interface AccessibilityNeeds {
  visualImpairment: boolean;
  hearingImpairment: boolean;
  motorImpairment: boolean;
  cognitiveSupport: boolean;
}

interface XiaoaiAgent {
  processMessage(message: string, context: ChatContext): Promise<ChatResponse>;
  analyzeHealthData(data: any): Promise<any>;
  generateHealthRecommendations(
    profile: UserProfile
  ): Promise<HealthRecommendation[]>;
  setPersonality(traits: any): void;
  startInquirySession(userId: string): Promise<any>;
  analyzeImage(
    imageData: ImageData,
    type: 'face' | 'tongue' | 'body'
  ): Promise<LookResult>;
  analyzeAudio(
    audioData: AudioData,
    type: 'voice' | 'sound'
  ): Promise<ListenResult>;
  processPalpationData(data: PalpationData): Promise<PalpationResult>;
  performFourDiagnosisIntegration(
    data: FourDiagnosisResults
  ): Promise<IntegratedDiagnosis>;
  enableAccessibilityFeature(feature: any): Promise<void>;
  getAccessibilityStatus(): Promise<any>;
  adaptInterfaceForDisability(disability: any): Promise<any>;
}

/**
 * 小艾智能体实现
 * 健康助手 & 首页聊天频道版主，具备完整的四诊能力和无障碍服务
 */
export class XiaoaiAgentImpl implements XiaoaiAgent {
  private diagnosisIntegrator: XiaoaiChatDiagnosisIntegrator;
  private personality: any = {
    style: 'caring',
    tone: 'warm', // 温暖的语调
    expertise: 'health', // 健康专业
    patience: 'high', // 高耐心
  };

  constructor() {
    this.diagnosisIntegrator = new XiaoaiChatDiagnosisIntegrator();
  }

  // 处理聊天消息
  async processMessage(
    message: string,
    context: ChatContext
  ): Promise<ChatResponse> {
    try {
      const response = await this.diagnosisIntegrator.processChatMessage(
        message,
        context
      );
      response.text = this.applyPersonalityToResponse(response.text, context);
      return response;
    } catch (error) {
      return this.generateFallbackResponse(message, context);
    }
  }

  // 分析健康数据
  async analyzeHealthData(data: any): Promise<any> {
    try {
      const analysis = {
        summary: '健康数据分析完成',
        insights: [] as string[],
        recommendations: [] as string[],
        riskFactors: [] as string[],
        trends: [] as string[],
      };

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
      throw error;
    }
  }

  // 生成健康建议
  async generateHealthRecommendations(
    profile: UserProfile
  ): Promise<HealthRecommendation[]> {
    const recommendations: HealthRecommendation[] = [];

    try {
      const { age, gender } = profile.basicInfo;

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

      if (gender === 'female') {
        recommendations.push({
          category: 'diet',
          title: '补充铁质',
          description: '注意补充铁质丰富的食物，预防贫血',
          priority: 'medium',
          timeframe: '日常饮食',
        });
      }

      if (profile.medicalHistory.length > 0) {
        recommendations.push({
          category: 'lifestyle',
          title: '疾病管理',
          description: '根据既往病史，建议定期随访和监测',
          priority: 'high',
          timeframe: '按医嘱执行',
        });
      }

      if (profile.preferences.diagnosisPreferences.privacyLevel === 'high') {
        recommendations.forEach((rec) => {
          rec.description = '建议咨询专业医生获取个性化指导';
        });
      }

      return recommendations;
    } catch (error) {
      return [];
    }
  }

  // 设置个性化特征
  setPersonality(traits: any): void {
    this.personality = { ...this.personality, ...traits };
  }

  // 四诊功能集成
  async startInquirySession(userId: string): Promise<any> {
    try {
      return await diagnosisServiceClient.inquiry.startSession(userId);
    } catch (error) {
      throw error;
    }
  }

  async analyzeImage(
    imageData: ImageData,
    type: 'face' | 'tongue' | 'body'
  ): Promise<LookResult> {
    try {
      const processedImageData = { ...imageData, type };

      if (type === 'face') {
        return await diagnosisServiceClient.look.analyzeFace(
          processedImageData
        );
      } else if (type === 'tongue') {
        return await diagnosisServiceClient.look.analyzeTongue(
          processedImageData
        );
      } else {
        // 默认使用面部分析
        return await diagnosisServiceClient.look.analyzeFace(
          processedImageData
        );
      }
    } catch (error) {
      throw error;
    }
  }

  async analyzeAudio(
    audioData: AudioData,
    type: 'voice' | 'sound'
  ): Promise<ListenResult> {
    try {
      const audioType: 'voice' | 'breathing' =
        type === 'sound' ? 'breathing' : 'voice';
      const processedAudioData = { ...audioData, type: audioType };

      if (audioType === 'voice') {
        return await diagnosisServiceClient.listen.analyzeVoice(
          processedAudioData
        );
      } else {
        return await diagnosisServiceClient.listen.analyzeBreathing(
          processedAudioData
        );
      }
    } catch (error) {
      throw error;
    }
  }

  async processPalpationData(data: PalpationData): Promise<PalpationResult> {
    try {
      return await diagnosisServiceClient.palpation.analyzePalpation(data);
    } catch (error) {
      throw error;
    }
  }

  async performFourDiagnosisIntegration(
    data: FourDiagnosisResults
  ): Promise<IntegratedDiagnosis> {
    try {
      // 综合四诊结果
      const summary = this.generateDiagnosisSummary(data);
      const confidence = this.calculateDiagnosisConfidence(data);
      const recommendations = this.generateDiagnosisRecommendations(data);

      return {
        summary,
        confidence,
        recommendations,
        syndrome: this.identifySyndrome(data),
        treatment: this.suggestTreatment(data),
      };
    } catch (error) {
      throw error;
    }
  }

  // 无障碍功能
  async enableAccessibilityFeature(feature: any): Promise<void> {
    try {
      if (feature.type === 'voice_assistance') {
        await accessibilityServiceClient.updateAccessibilitySettings(
          feature.userId,
          { voice_assistance: true, ...feature.preferences }
        );
      } else if (feature.type === 'screen_reader') {
        await accessibilityServiceClient.updateAccessibilitySettings(
          feature.userId,
          { screen_reader: true, ...feature.preferences }
        );
      } else if (feature.type === 'sign_language') {
        await accessibilityServiceClient.updateAccessibilitySettings(
          feature.userId,
          { sign_language: true, ...feature.preferences }
        );
      }
    } catch (error) {
      throw error;
    }
  }

  async getAccessibilityStatus(): Promise<any> {
    try {
      // 检查无障碍服务状态
      const defaultStatus = {
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

      return defaultStatus;
    } catch (error) {
      throw error;
    }
  }

  async adaptInterfaceForDisability(disability: any): Promise<any> {
    try {
      const adaptations: any = {};

      if (disability.type === 'visual') {
        adaptations.visual = {
          fontSize: 'large',
          highContrast: true,
          screenReader: true,
        };
      } else if (disability.type === 'hearing') {
        adaptations.hearing = {
          captions: true,
          visualIndicators: true,
          signLanguage: true,
        };
      } else if (disability.type === 'motor') {
        adaptations.motor = {
          largeButtons: true,
          voiceControl: true,
          gestureAlternatives: true,
        };
      } else if (disability.type === 'cognitive') {
        adaptations.cognitive = {
          simplifiedInterface: true,
          stepByStep: true,
          reminders: true,
        };
      }

      return adaptations;
    } catch (error) {
      throw error;
    }
  }

  // 私有辅助方法
  private applyPersonalityToResponse(
    text: string,
    context: ChatContext
  ): string {
    // 根据个性化设置调整回复语调
    if (this.personality.tone === 'warm') {
      return `${text} 😊`;
    }
    return text;
  }

  private generateFallbackResponse(
    message: string,
    context: ChatContext
  ): ChatResponse {
    return {
      text: '抱歉，我暂时无法理解您的问题。请您重新描述一下，我会尽力帮助您。',
      suggestions: ['请描述您的症状', '我想了解健康建议', '帮我分析健康数据'],
      requiresFollowUp: true,
      confidence: 0.1,
    };
  }

  private generateDiagnosisSummary(data: FourDiagnosisResults): string {
    const parts: string[] = [];

    if (data.inquiry) {
      parts.push('问诊分析完成');
    }
    if (data.look) {
      parts.push('望诊分析完成');
    }
    if (data.listen) {
      parts.push('闻诊分析完成');
    }
    if (data.palpation) {
      parts.push('切诊分析完成');
    }

    return parts.length > 0 ? parts.join('，') : '诊断分析完成';
  }

  private calculateDiagnosisConfidence(data: FourDiagnosisResults): number {
    const confidences: number[] = [];

    if (data.look?.confidence) confidences.push(data.look.confidence);
    if (data.listen?.confidence) confidences.push(data.listen.confidence);
    if (data.palpation?.confidence) confidences.push(data.palpation.confidence);

    return confidences.length > 0
      ? confidences.reduce((sum, conf) => sum + conf, 0) / confidences.length
      : 0.5;
  }

  private generateDiagnosisRecommendations(
    data: FourDiagnosisResults
  ): string[] {
    const recommendations: string[] = [];

    if (data.look?.recommendations) {
      recommendations.push(...data.look.recommendations);
    }
    if (data.listen?.recommendations) {
      recommendations.push(...data.listen.recommendations);
    }
    if (data.palpation?.recommendations) {
      recommendations.push(...data.palpation.recommendations);
    }

    return Array.from(new Set(recommendations));
  }

  private identifySyndrome(data: FourDiagnosisResults): string {
    // 基于四诊结果识别证候
    return '需要进一步分析确定证候';
  }

  private suggestTreatment(data: FourDiagnosisResults): string {
    // 基于诊断结果建议治疗方案
    return '建议咨询专业中医师制定个性化治疗方案';
  }
}

// 创建小艾智能体实例
export const xiaoaiAgent = new XiaoaiAgentImpl();

export default XiaoaiAgentImpl;
