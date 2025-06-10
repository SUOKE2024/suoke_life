import { diagnosisServiceClient } from '../services/DiagnosisServiceClient';

// 本地类型定义，与服务客户端返回类型匹配
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
  sampleRate?: number;
  type?: string;
}

interface PalpationData {
  type: string;
  sensorData: Record<string, any>;
  timestamp?: number;
}

interface InquiryResult {
  sessionId: string;
  response: string;
  extractedSymptoms: string[];
  confidence: number;
  nextQuestions: string[];
  isComplete: boolean;
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

// 基本类型定义
interface ChatContext {
  userId: string;
  hasImages?: boolean;
  images?: ImageData[];
  hasAudio?: boolean;
  audio?: AudioData[];
  hasPalpationData?: boolean;
  palpationData?: PalpationData[];
}

interface ChatResponse {
  text: string;
  actions: any[];
  suggestions: string[];
  diagnosisResults: any;
  confidence: number;
  timestamp: Date;
  error?: string;
}

interface DiagnosisIntent {
  needsInquiry: boolean;
  needsLookDiagnosis: boolean;
  needsListenDiagnosis: boolean;
  needsPalpationDiagnosis: boolean;
  confidence: number;
  extractedSymptoms: string[];
  urgencyLevel: 'low' | 'medium' | 'high' | 'emergency';
}

interface FourDiagnosisResults {
  inquiry?: InquiryResult;
  look?: LookResult;
  listen?: ListenResult;
  palpation?: PalpationResult;
  integrated?: any;
}

/**
 * 负责在聊天过程中智能识别并调用相应的四诊服务
 */
export class XiaoaiChatDiagnosisIntegrator {
  private activeSessions: Map<string, any> = new Map();

  /**
   * 处理聊天消息，智能调用四诊服务
   */
  async processChatMessage(
    message: string,
    context: ChatContext
  ): Promise<ChatResponse> {
    try {
      const diagnosisIntent = await this.analyzeDiagnosisIntent(
        message,
        context
      );
      const diagnosisResults: FourDiagnosisResults = {};

      if (diagnosisIntent.needsInquiry) {
        diagnosisResults.inquiry = await this.performInquiry(
          context.userId,
          message
        );
      }

      if (
        diagnosisIntent.needsLookDiagnosis &&
        context.hasImages &&
        context.images
      ) {
        diagnosisResults.look = await this.performLookDiagnosis(context.images);
      }

      if (
        diagnosisIntent.needsListenDiagnosis &&
        context.hasAudio &&
        context.audio
      ) {
        diagnosisResults.listen = await this.performListenDiagnosis(
          context.audio
        );
      }

      if (
        diagnosisIntent.needsPalpationDiagnosis &&
        context.hasPalpationData &&
        context.palpationData
      ) {
        diagnosisResults.palpation = await this.performPalpationDiagnosis(
          context.palpationData
        );
      }

      if (this.hasMultipleDiagnosisResults(diagnosisResults)) {
        diagnosisResults.integrated =
          await this.performFourDiagnosisIntegration(diagnosisResults);
      }

      return this.generateChatResponseWithDiagnosis(
        message,
        diagnosisResults,
        context,
        diagnosisIntent
      );
    } catch (error) {
      return this.generateErrorResponse(message, error);
    }
  }

  /**
   * 分析用户消息的四诊意图
   */
  private async analyzeDiagnosisIntent(
    message: string,
    context: ChatContext
  ): Promise<DiagnosisIntent> {
    const symptomKeywords = [
      '咳嗽',
      '胸闷',
      '头痛',
      '发热',
      '乏力',
      '失眠',
      '腹痛',
      '恶心',
      '呕吐',
      '腹泻',
      '便秘',
      '心悸',
      '气短',
      '眩晕',
      '耳鸣',
      '视力模糊',
      '关节痛',
      '肌肉痛',
      '皮疹',
      '瘙痒',
      '出汗',
      '怕冷',
      '怕热',
      '口干',
      '口苦',
      '食欲不振',
      '消化不良',
      '月经不调',
      '痛经',
    ];

    const extractedSymptoms = symptomKeywords.filter((keyword) =>
      message.includes(keyword)
    );

    const emergencyKeywords = [
      '急性',
      '剧烈',
      '严重',
      '突然',
      '无法忍受',
      '呼吸困难',
    ];
    const urgencyLevel = emergencyKeywords.some((keyword) =>
      message.includes(keyword)
    )
      ? 'high'
      : extractedSymptoms.length > 0
        ? 'medium'
        : 'low';

    const needsInquiry =
      extractedSymptoms.length > 0 ||
      message.includes('症状') ||
      message.includes('不舒服') ||
      message.includes('身体') ||
      message.includes('健康');

    const needsLookDiagnosis =
      context.hasImages ||
      message.includes('看看') ||
      message.includes('舌头') ||
      message.includes('面色') ||
      message.includes('照片');

    const needsListenDiagnosis =
      context.hasAudio ||
      message.includes('听听') ||
      message.includes('声音') ||
      message.includes('咳嗽声') ||
      message.includes('录音');

    const needsPalpationDiagnosis =
      context.hasPalpationData ||
      message.includes('脉搏') ||
      message.includes('按压') ||
      message.includes('触诊');

    const confidence = this.calculateIntentConfidence(
      extractedSymptoms.length,
      needsInquiry,
      needsLookDiagnosis,
      needsListenDiagnosis,
      needsPalpationDiagnosis
    );

    return {
      needsInquiry,
      needsLookDiagnosis,
      needsListenDiagnosis,
      needsPalpationDiagnosis,
      confidence,
      extractedSymptoms,
      urgencyLevel: urgencyLevel as 'low' | 'medium' | 'high' | 'emergency',
    };
  }

  /**
   * 执行问诊
   */
  private async performInquiry(
    userId: string,
    message: string
  ): Promise<InquiryResult> {
    try {
      let sessionId = this.activeSessions.get(`inquiry_${userId}`);
      if (!sessionId) {
        sessionId = await diagnosisServiceClient.inquiry.startSession(userId);
        this.activeSessions.set(`inquiry_${userId}`, sessionId);
      }

      await diagnosisServiceClient.inquiry.askQuestion(sessionId, message);

      // 这里可能需要调用一个获取当前状态的API，而不是结束会话
      // 暂时使用模拟数据
      return {
        sessionId,
        response: '已收到您的症状描述',
        extractedSymptoms: [],
        confidence: 0.8,
        nextQuestions: [],
        isComplete: false,
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 执行望诊
   */
  private async performLookDiagnosis(images: ImageData[]): Promise<LookResult> {
    try {
      const primaryImage = this.selectPrimaryImage(images);
      return await diagnosisServiceClient.look.analyzeFace(primaryImage);
    } catch (error) {
      throw error;
    }
  }

  /**
   * 执行闻诊
   */
  private async performListenDiagnosis(
    audioData: AudioData[]
  ): Promise<ListenResult> {
    try {
      const primaryAudio = this.selectPrimaryAudio(audioData);
      return await diagnosisServiceClient.listen.analyzeVoice(primaryAudio);
    } catch (error) {
      throw error;
    }
  }

  /**
   * 执行切诊
   */
  private async performPalpationDiagnosis(
    palpationData: PalpationData[]
  ): Promise<PalpationResult> {
    try {
      const primaryData = this.selectPrimaryPalpationData(palpationData);
      // 确保数据包含timestamp字段
      const dataWithTimestamp = {
        ...primaryData,
        timestamp: primaryData.timestamp || Date.now(),
      };
      return await diagnosisServiceClient.palpation.analyzePalpation(
        dataWithTimestamp
      );
    } catch (error) {
      throw error;
    }
  }

  /**
   * 执行四诊合参
   */
  private async performFourDiagnosisIntegration(
    diagnosisResults: FourDiagnosisResults
  ): Promise<any> {
    // 目前返回模拟数据，后续需要实现真正的中医四诊合参算法
    const evidences: string[] = [];

    if (diagnosisResults.inquiry) {
      evidences.push(
        '问诊：' +
          diagnosisResults.inquiry.extractedSymptoms.map((s) => s).join('、')
      );
    }

    if (diagnosisResults.look) {
      evidences.push('望诊：' + diagnosisResults.look.analysis);
    }

    if (diagnosisResults.listen) {
      evidences.push('闻诊：' + diagnosisResults.listen.analysis);
    }

    if (diagnosisResults.palpation) {
      evidences.push('切诊：' + diagnosisResults.palpation.analysis);
    }

    return {
      overallAssessment: `综合四诊分析：${evidences.join('；')}`,
      tcmDiagnosis: {
        syndrome: '待进一步分析',
        pathogenesis: '基于四诊合参的病机分析',
        treatment: '个性化治疗方案',
        prognosis: '良好',
      },
      healthRecommendations: [
        {
          category: 'lifestyle',
          title: '生活方式调整',
          description: '基于四诊结果的生活建议',
          priority: 'medium',
          timeframe: '1-2周',
        },
      ],
      riskFactors: [],
      followUpActions: [
        {
          action: '定期复查',
          timeframe: '1周后',
          priority: 'medium',
          description: '观察症状变化',
        },
      ],
      confidence: 0.85,
    };
  }

  /**
   * 生成包含诊断结果的聊天回复
   */
  private generateChatResponseWithDiagnosis(
    originalMessage: string,
    diagnosisResults: FourDiagnosisResults,
    context: ChatContext,
    intent: DiagnosisIntent
  ): ChatResponse {
    let responseText = '';
    const actions: any[] = [];
    const suggestions: string[] = [];

    if (intent.urgencyLevel === 'high' || intent.urgencyLevel === 'emergency') {
      responseText = '我注意到你描述的症状比较严重，让我立即为你进行详细分析。';
    } else if (intent.extractedSymptoms.length > 0) {
      responseText = `我了解到你有${intent.extractedSymptoms.join('、')}等症状，让我帮你分析一下。`;
    } else {
      responseText = '我来帮你了解一下你的健康状况。';
    }

    if (diagnosisResults.integrated) {
      responseText += `\n\n${diagnosisResults.integrated.overallAssessment}`;

      if (diagnosisResults.integrated.healthRecommendations.length > 0) {
        responseText += '\n\n我的建议：';
        diagnosisResults.integrated.healthRecommendations.forEach(
          (rec, index) => {
            responseText += `\n${index + 1}. ${rec.title}：${rec.description}`;
          }
        );
      }
    } else {
      if (diagnosisResults.inquiry) {
        responseText += '\n\n基于我们的对话，我了解了你的症状情况。';
      }

      if (diagnosisResults.look) {
        responseText += `\n\n望诊分析：${diagnosisResults.look.analysis}`;
      }

      if (diagnosisResults.listen) {
        responseText += `\n\n闻诊分析：${diagnosisResults.listen.analysis}`;
      }

      if (diagnosisResults.palpation) {
        responseText += `\n\n切诊分析：${diagnosisResults.palpation.analysis}`;
      }
    }

    if (intent.needsInquiry && !diagnosisResults.inquiry) {
      actions.push({
        type: 'inquiry',
        prompt: '我想了解一下你的具体症状，可以详细说说吗？',
        autoStart: true,
      });
    }

    return {
      text: responseText,
      actions,
      suggestions,
      diagnosisResults,
      confidence: intent.confidence,
      timestamp: new Date(),
    };
  }

  /**
   * 生成错误回复
   */
  private generateErrorResponse(
    originalMessage: string,
    error: any
  ): ChatResponse {
    return {
      text: '抱歉，在分析你的消息时遇到了一些问题。请稍后再试，或者换个方式描述你的情况。',
      actions: [],
      suggestions: ['重新描述症状', '稍后再试'],
      diagnosisResults: {},
      confidence: 0,
      timestamp: new Date(),
      error: error.message,
    };
  }

  /**
   * 检查是否有多个诊断结果
   */
  private hasMultipleDiagnosisResults(results: FourDiagnosisResults): boolean {
    const resultCount = Object.keys(results).length;
    return resultCount >= 2;
  }

  /**
   * 计算意图置信度
   */
  private calculateIntentConfidence(
    symptomCount: number,
    needsInquiry: boolean,
    needsLook: boolean,
    needsListen: boolean,
    needsPalpation: boolean
  ): number {
    let confidence = 0.5; // 基础置信度

    // 症状数量影响
    confidence += Math.min(symptomCount * 0.1, 0.3);

    // 诊断需求影响
    const diagnosisNeeds = [
      needsInquiry,
      needsLook,
      needsListen,
      needsPalpation,
    ];
    const activeNeeds = diagnosisNeeds.filter(Boolean).length;
    confidence += activeNeeds * 0.05;

    return Math.min(confidence, 1.0);
  }

  /**
   * 选择主要图片
   */
  private selectPrimaryImage(images: ImageData[]): ImageData {
    // 简单选择第一张图片，后续可以实现更智能的选择逻辑
    return images[0];
  }

  /**
   * 选择主要音频
   */
  private selectPrimaryAudio(audioData: AudioData[]): AudioData {
    // 简单选择第一个音频，后续可以实现更智能的选择逻辑
    return audioData[0];
  }

  /**
   * 选择主要触诊数据
   */
  private selectPrimaryPalpationData(
    palpationData: PalpationData[]
  ): PalpationData {
    // 简单选择第一个数据，后续可以实现更智能的选择逻辑
    return palpationData[0];
  }
}
