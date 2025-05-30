import {
import { diagnosisServiceClient } from '../services/DiagnosisServiceClient';


  ChatContext,
  ChatResponse,
  DiagnosisIntent,
  FourDiagnosisResults,
  IntegratedDiagnosis,
  DiagnosisAction,
  ImageData,
  AudioData,
  PalpationData,
  InquiryResult,
  LookResult,
  ListenResult,
  PalpationResult,
} from '../types';

/**
 * 小艾智能体聊天中的四诊调用集成器
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
      // 1. 分析用户消息，识别是否需要四诊服务
      const diagnosisIntent = await this.analyzeDiagnosisIntent(message, context);
      
      // 2. 根据意图调用相应的四诊服务
      const diagnosisResults: FourDiagnosisResults = {};
      
      if (diagnosisIntent.needsInquiry) {
        diagnosisResults.inquiry = await this.performInquiry(context.userId, message);
      }
      
      if (diagnosisIntent.needsLookDiagnosis && context.hasImages && context.images) {
        diagnosisResults.look = await this.performLookDiagnosis(context.images);
      }
      
      if (diagnosisIntent.needsListenDiagnosis && context.hasAudio && context.audio) {
        diagnosisResults.listen = await this.performListenDiagnosis(context.audio);
      }
      
      if (diagnosisIntent.needsPalpationDiagnosis && context.hasPalpationData && context.palpationData) {
        diagnosisResults.palpation = await this.performPalpationDiagnosis(context.palpationData);
      }

      // 3. 如果有多个诊断结果，进行四诊合参
      if (this.hasMultipleDiagnosisResults(diagnosisResults)) {
        diagnosisResults.integrated = await this.performFourDiagnosisIntegration(diagnosisResults);
      }

      // 4. 生成自然的聊天回复
      return this.generateChatResponseWithDiagnosis(message, diagnosisResults, context, diagnosisIntent);
      
    } catch (error) {
      console.error('处理聊天消息时发生错误:', error);
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
    // 症状关键词检测
    const symptomKeywords = [
      '咳嗽', '胸闷', '头痛', '发热', '乏力', '失眠', '腹痛', '恶心', '呕吐',
      '腹泻', '便秘', '心悸', '气短', '眩晕', '耳鸣', '视力模糊', '关节痛',
      '肌肉痛', '皮疹', '瘙痒', '出汗', '怕冷', '怕热', '口干', '口苦',
      '食欲不振', '消化不良', '月经不调', '痛经',
    ];

    // 检测症状关键词
    const extractedSymptoms = symptomKeywords.filter(keyword => 
      message.includes(keyword)
    );

    // 检测紧急程度
    const emergencyKeywords = ['急性', '剧烈', '严重', '突然', '无法忍受', '呼吸困难'];
    const urgencyLevel = emergencyKeywords.some(keyword => message.includes(keyword)) 
      ? 'high' : extractedSymptoms.length > 0 ? 'medium' : 'low';

    // 基于消息内容和上下文判断需要的诊断类型
    const needsInquiry = extractedSymptoms.length > 0 || 
                        message.includes('症状') || 
                        message.includes('不舒服') ||
                        message.includes('身体') ||
                        message.includes('健康');

    const needsLookDiagnosis = context.hasImages || 
                              message.includes('看看') || 
                              message.includes('舌头') ||
                              message.includes('面色') ||
                              message.includes('照片');

    const needsListenDiagnosis = context.hasAudio || 
                                message.includes('听听') || 
                                message.includes('声音') ||
                                message.includes('咳嗽声') ||
                                message.includes('录音');

    const needsPalpationDiagnosis = context.hasPalpationData || 
                                   message.includes('脉搏') || 
                                   message.includes('按压') ||
                                   message.includes('触诊');

    // 计算置信度
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
  private async performInquiry(userId: string, message: string): Promise<InquiryResult> {
    try {
      // 检查是否已有活跃的问诊会话
      let sessionId = this.activeSessions.get(`inquiry_${userId}`);
      
      if (!sessionId) {
        // 开始新的问诊会话
        const sessionResponse = await diagnosisServiceClient.inquiry.startSession(userId);
        sessionId = sessionResponse.session_id;
        this.activeSessions.set(`inquiry_${userId}`, sessionId);
      }

      // 进行问诊交互
      await diagnosisServiceClient.inquiry.interact(sessionId, message);
      
      // 获取当前的问诊结果（不结束会话，保持连续对话）
      // 这里可能需要调用一个获取当前状态的API，而不是结束会话
      // 暂时使用模拟数据
      return {
        sessionId,
        detectedSymptoms: [],
        tcmPatterns: [],
        healthProfile: {} as any,
        recommendations: [],
        confidence: 0.8,
      };
      
    } catch (error) {
      console.error('问诊执行失败:', error);
      throw error;
    }
  }

  /**
   * 执行望诊
   */
  private async performLookDiagnosis(images: ImageData[]): Promise<LookResult> {
    try {
      // 选择最适合的图片进行分析
      const primaryImage = this.selectPrimaryImage(images);
      return await diagnosisServiceClient.look.analyzeImage(primaryImage);
    } catch (error) {
      console.error('望诊执行失败:', error);
      throw error;
    }
  }

  /**
   * 执行闻诊
   */
  private async performListenDiagnosis(audioData: AudioData[]): Promise<ListenResult> {
    try {
      // 选择最适合的音频进行分析
      const primaryAudio = this.selectPrimaryAudio(audioData);
      return await diagnosisServiceClient.listen.analyzeAudio(primaryAudio);
    } catch (error) {
      console.error('闻诊执行失败:', error);
      throw error;
    }
  }

  /**
   * 执行切诊
   */
  private async performPalpationDiagnosis(palpationData: PalpationData[]): Promise<PalpationResult> {
    try {
      // 选择最适合的触诊数据进行分析
      const primaryData = this.selectPrimaryPalpationData(palpationData);
      return await diagnosisServiceClient.palpation.analyzePalpation(primaryData);
    } catch (error) {
      console.error('切诊执行失败:', error);
      throw error;
    }
  }

  /**
   * 执行四诊合参
   */
  private async performFourDiagnosisIntegration(
    diagnosisResults: FourDiagnosisResults
  ): Promise<IntegratedDiagnosis> {
    // 这里实现四诊合参的逻辑
    // 目前返回模拟数据，后续需要实现真正的中医四诊合参算法
    
    const evidences: string[] = [];
    
    if (diagnosisResults.inquiry) {
      evidences.push('问诊：' + diagnosisResults.inquiry.detectedSymptoms.map(s => s.name).join('、'));
    }
    
    if (diagnosisResults.look) {
      evidences.push('望诊：' + diagnosisResults.look.overallAssessment);
    }
    
    if (diagnosisResults.listen) {
      evidences.push('闻诊：' + diagnosisResults.listen.overallAssessment);
    }
    
    if (diagnosisResults.palpation) {
      evidences.push('切诊：' + diagnosisResults.palpation.overallAssessment);
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
    const actions: DiagnosisAction[] = [];
    const suggestions: string[] = [];

    // 根据紧急程度调整回复语气
    if (intent.urgencyLevel === 'high' || intent.urgencyLevel === 'emergency') {
      responseText = '我注意到你描述的症状比较严重，让我立即为你进行详细分析。';
    } else if (intent.extractedSymptoms.length > 0) {
      responseText = `我了解到你有${intent.extractedSymptoms.join('、')}等症状，让我帮你分析一下。`;
    } else {
      responseText = '我来帮你了解一下你的健康状况。';
    }

    // 根据诊断结果生成具体回复
    if (diagnosisResults.integrated) {
      responseText += `\n\n${diagnosisResults.integrated.overallAssessment}`;
      
      if (diagnosisResults.integrated.healthRecommendations.length > 0) {
        responseText += '\n\n我的建议：';
        diagnosisResults.integrated.healthRecommendations.forEach((rec, index) => {
          responseText += `\n${index + 1}. ${rec.title}：${rec.description}`;
        });
      }
    } else {
      // 单个诊断结果的处理
      if (diagnosisResults.inquiry) {
        responseText += '\n\n基于我们的对话，我了解了你的症状情况。';
      }
      
      if (diagnosisResults.look) {
        responseText += '\n\n从你提供的图片来看：' + diagnosisResults.look.overallAssessment;
      }
      
      if (diagnosisResults.listen) {
        responseText += '\n\n从你的声音分析：' + diagnosisResults.listen.overallAssessment;
      }
      
      if (diagnosisResults.palpation) {
        responseText += '\n\n触诊数据显示：' + diagnosisResults.palpation.overallAssessment;
      }
    }

    // 生成后续建议的操作
    if (intent.needsInquiry && !diagnosisResults.inquiry) {
      actions.push({
        type: 'inquiry',
        prompt: '我想了解一下你的具体症状，可以详细说说吗？',
        autoStart: true,
        priority: 1,
      });
    }

    if (intent.needsLookDiagnosis && !diagnosisResults.look) {
      actions.push({
        type: 'look',
        prompt: '如果方便的话，可以拍张舌头的照片让我看看吗？',
        optional: true,
        priority: 2,
      });
    }

    if (intent.needsListenDiagnosis && !diagnosisResults.listen) {
      actions.push({
        type: 'listen',
        prompt: '可以录一段咳嗽声或者说话声让我听听吗？',
        optional: true,
        priority: 3,
      });
    }

    // 生成建议
    suggestions.push('继续描述症状');
    suggestions.push('上传相关图片');
    suggestions.push('录制音频');
    suggestions.push('查看详细报告');

    return {
      text: responseText,
      actions,
      suggestions,
      diagnosisResults,
      timestamp: Date.now(),
    };
  }

  /**
   * 生成错误回复
   */
  private generateErrorResponse(message: string, error: any): ChatResponse {
    return {
      text: '抱歉，我在分析你的情况时遇到了一些技术问题。请稍后再试，或者换个方式描述你的症状。',
      suggestions: ['重新描述症状', '稍后再试', '联系技术支持'],
      timestamp: Date.now(),
    };
  }

  /**
   * 辅助方法
   */
  private calculateIntentConfidence(
    symptomCount: number,
    needsInquiry: boolean,
    needsLook: boolean,
    needsListen: boolean,
    needsPalpation: boolean
  ): number {
    let confidence = 0.5; // 基础置信度
    
    confidence += symptomCount * 0.1; // 每个症状增加0.1
    confidence += (needsInquiry ? 0.2 : 0);
    confidence += (needsLook ? 0.1 : 0);
    confidence += (needsListen ? 0.1 : 0);
    confidence += (needsPalpation ? 0.1 : 0);
    
    return Math.min(confidence, 1.0);
  }

  private hasMultipleDiagnosisResults(results: FourDiagnosisResults): boolean {
    const count = [results.inquiry, results.look, results.listen, results.palpation]
      .filter(result => result !== undefined).length;
    return count > 1;
  }

  private selectPrimaryImage(images: ImageData[]): ImageData {
    // 优先选择舌象图片，其次是面部图片
    const tongueImage = images.find(img => img.type === 'tongue');
    if (tongueImage) {return tongueImage;}
    
    const faceImage = images.find(img => img.type === 'face');
    if (faceImage) {return faceImage;}
    
    return images[0];
  }

  private selectPrimaryAudio(audioData: AudioData[]): AudioData {
    // 优先选择咳嗽声，其次是语音
    const coughAudio = audioData.find(audio => audio.type === 'cough');
    if (coughAudio) {return coughAudio;}
    
    const voiceAudio = audioData.find(audio => audio.type === 'voice');
    if (voiceAudio) {return voiceAudio;}
    
    return audioData[0];
  }

  private selectPrimaryPalpationData(palpationData: PalpationData[]): PalpationData {
    // 优先选择脉诊数据
    const pulseData = palpationData.find(data => data.type === 'pulse');
    if (pulseData) {return pulseData;}
    
    return palpationData[0];
  }

  /**
   * 清理会话
   */
  async cleanupSession(userId: string, sessionType?: string): Promise<void> {
    if (sessionType) {
      this.activeSessions.delete(`${sessionType}_${userId}`);
    } else {
      // 清理所有相关会话
      const keysToDelete = Array.from(this.activeSessions.keys())
        .filter(key => key.endsWith(`_${userId}`));
      keysToDelete.forEach(key => this.activeSessions.delete(key));
    }
  }

  /**
   * 获取活跃会话状态
   */
  getActiveSessionsStatus(userId: string): { [key: string]: any } {
    const userSessions: { [key: string]: any } = {};
    
    this.activeSessions.forEach((sessionId, key) => {
      if (key.endsWith(`_${userId}`)) {
        const sessionType = key.replace(`_${userId}`, '');
        userSessions[sessionType] = sessionId;
      }
    });
    
    return userSessions;
  }
} 