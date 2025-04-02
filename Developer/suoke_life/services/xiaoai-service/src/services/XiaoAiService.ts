import { v4 as uuidv4 } from 'uuid';
import { Logger } from '../utils/logger';
import { VoiceGuidanceService } from './VoiceGuidanceService';
import { DialectService } from './DialectService';
import { User } from '../models/User';
import { XiaoAiAgent } from '../models/XiaoAiAgent';
import { Conversation } from '../models/Conversation';
import { DialectType, DialectDetection } from '../types';
import axios from 'axios';
import { LLMService } from './LLMService';
import { DiagnosticCoordinationService } from './DiagnosticCoordinationService';

const logger = new Logger('XiaoAiService');

// 创建服务实例
const llmService = new LLMService();
const voiceGuidanceService = new VoiceGuidanceService();
const dialectService = new DialectService();
const diagnosticCoordinationService = new DiagnosticCoordinationService();

export class XiaoAiService {
  private readonly ttsServiceUrl: string;
  private readonly openaiApiKey: string;

  constructor() {
    this.ttsServiceUrl = process.env.TTS_SERVICE_URL || 'http://tts-service:3060';
    this.openaiApiKey = process.env.OPENAI_API_KEY || '';
  }

  /**
   * 初始化小艾智能体
   */
  public async initializeAgent(): Promise<any> {
    try {
      // 查找小艾智能体
      let agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      // 如果不存在，创建新的小艾智能体
      if (!agent) {
        agent = new XiaoAiAgent({
          agentId: uuidv4(),
          name: '小艾',
          status: 'active',
          version: '1.0.0',
          role: '首页聊天频道版主',
          description: '负责统筹协调望诊、闻诊、问诊、切诊服务，提供无障碍功能，语音引导服务',
          state: {
            mode: 'normal',
            userPreferences: {
              voiceEnabled: false,
              voiceSpeed: 1.0,
              preferredLanguage: 'zh-CN',
              notificationEnabled: true,
            },
            activeDiagnosticServices: [],
            accessibilitySettings: {
              visualAssistance: false,
              audioAssistance: false,
              textSize: 'normal',
              highContrast: false,
            },
          },
          capabilities: [
            {
              name: '四诊协调',
              description: '统筹协调望诊、闻诊、问诊、切诊服务',
              enabled: true,
            },
            {
              name: '无障碍功能',
              description: '为特殊需求用户提供无障碍功能',
              enabled: true,
            },
            {
              name: '语音引导',
              description: '为视障用户提供语音引导，包括导盲服务',
              enabled: true,
            },
            {
              name: '方言支持',
              description: '支持多种方言的识别和交互',
              enabled: true,
            },
            {
              name: '健康咨询',
              description: '提供基础的健康咨询和指导',
              enabled: true,
            },
          ],
          conversationHistory: [
            {
              timestamp: new Date(),
              userId: 'system',
              messageType: 'system',
              content: '小艾智能体已初始化，准备为用户提供服务。',
            },
          ],
        });
        
        await agent.save();
        logger.info('小艾智能体已成功初始化');
      }
      
      return agent;
    } catch (error) {
      logger.error('初始化小艾智能体失败:', error);
      throw new Error('初始化小艾智能体失败');
    }
  }

  /**
   * 处理用户消息
   * @param userId 用户ID
   * @param message 消息内容
   * @param messageType 消息类型
   * @param context 上下文信息
   */
  public async processUserMessage(
    userId: string,
    message: string,
    messageType: 'text' | 'voice' | 'image' = 'text',
    context?: any
  ): Promise<any> {
    try {
      // 查找用户
      let user = await User.findOne({ userId });
      
      // 如果用户不存在，创建新用户
      if (!user) {
        user = new User({
          userId,
          createdAt: new Date(),
          settings: {
            accessibilityNeeds: {
              visuallyImpaired: false,
              hearingImpaired: false,
              needsVoiceGuidance: false,
              preferredVoiceSpeed: 1.0,
            },
            notifications: {
              enabled: true,
              types: ['important', 'health'],
            },
          },
        });
        
        await user.save();
        logger.info(`创建新用户: ${userId}`);
      }
      
      // 查找小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        throw new Error('小艾智能体不存在');
      }
      
      // 记录用户消息到会话历史
      agent.conversationHistory.push({
        timestamp: new Date(),
        userId,
        messageType,
        content: message,
        metadata: context || {},
      });
      
      await agent.save();
      
      // 根据智能体状态确定处理流程
      let response;
      let actions = [];
      
      switch (agent.state.mode) {
        case 'diagnosis-coordination':
          // 在诊断协调模式下，使用诊断协调服务处理消息
          const diagnosticResponse = await diagnosticCoordinationService.processDiagnosticMessage(
            user,
            message,
            agent.state.activeDiagnosticServices
          );
          
          response = diagnosticResponse.response;
          actions = diagnosticResponse.actions;
          break;
        
        default:
          // 正常模式下，使用 LLM 处理消息
          response = await this.generateResponse(user, message, messageType, context);
      }
      
      // 记录小艾回复到会话历史
      agent.conversationHistory.push({
        timestamp: new Date(),
        userId: 'xiaoai',
        messageType: 'text',
        content: response,
      });
      
      await agent.save();
      
      // 如果用户需要语音引导，生成语音响应
      let voiceResponse = null;
      if (user.settings.accessibilityNeeds.needsVoiceGuidance) {
        const audioUrl = await voiceGuidanceService.generateVoiceGuidance(
          response,
          user.settings.accessibilityNeeds.preferredVoiceSpeed,
          'zh-CN'
        );
        
        voiceResponse = audioUrl;
      }
      
      return {
        userId,
        response,
        voiceResponse,
        messageType: 'text',
        timestamp: new Date().toISOString(),
        actions,
      };
    } catch (error) {
      logger.error('处理用户消息失败:', error);
      throw new Error('处理用户消息失败');
    }
  }
  
  /**
   * 生成响应
   * @param user 用户
   * @param message 消息内容
   * @param messageType 消息类型
   * @param context 上下文信息
   */
  private async generateResponse(
    user: any,
    message: string,
    messageType: string,
    context?: any
  ): Promise<string> {
    try {
      // 构建上下文
      const llmContext = {
        userId: user.userId,
        messageType,
        userProfile: {
          accessibilityNeeds: user.settings.accessibilityNeeds,
        },
        additionalContext: context || {},
      };
      
      // 根据消息类型特殊处理
      if (messageType === 'image' && context?.imageAnalysis) {
        return await llmService.generateImageResponse(message, context.imageAnalysis, llmContext);
      }
      
      // 标准文本响应
      return await llmService.generateTextResponse(message, llmContext);
    } catch (error) {
      logger.error('生成响应失败:', error);
      return '抱歉，我现在无法正确处理您的请求。请稍后再试或者换一种方式表达。';
    }
  }

  /**
   * 语音转文字
   * @param audioBuffer 音频数据
   * @returns 转录结果
   */
  public async speechToText(audioBuffer: Buffer): Promise<{ text: string; confidence: number }> {
    try {
      // 将音频发送到语音识别服务
      const response = await axios.post(
        'http://speech-service:3080/transcribe',
        { audio: audioBuffer.toString('base64') },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.status !== 200 || !response.data.text) {
        throw new Error('语音识别服务返回无效结果');
      }
      
      return {
        text: response.data.text,
        confidence: response.data.confidence || 0.8,
      };
    } catch (error) {
      logger.error('语音转文字失败:', error);
      throw new Error('语音转文字处理失败');
    }
  }

  /**
   * 图像分析
   * @param imageBuffer 图像数据
   * @returns 分析结果
   */
  public async analyzeImage(imageBuffer: Buffer): Promise<{
    description: string;
    tags: string[];
    objects: any[];
    healthRelevant: boolean;
    healthContext?: any;
  }> {
    try {
      // 将图像发送到图像分析服务
      const response = await axios.post(
        'http://vision-service:3090/analyze',
        { image: imageBuffer.toString('base64') },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.openaiApiKey}`,
          },
        }
      );
      
      if (response.status !== 200) {
        throw new Error('图像分析服务返回无效结果');
      }
      
      // 检查是否与健康相关
      const healthAnalysisResult = await this.analyzeHealthContext(response.data);
      
      return {
        description: response.data.description || '未能生成图像描述',
        tags: response.data.tags || [],
        objects: response.data.objects || [],
        healthRelevant: healthAnalysisResult.isHealthRelevant,
        healthContext: healthAnalysisResult.isHealthRelevant ? healthAnalysisResult.context : undefined,
      };
    } catch (error) {
      logger.error('图像分析失败:', error);
      return {
        description: '抱歉，我无法分析这张图片',
        tags: [],
        objects: [],
        healthRelevant: false,
      };
    }
  }

  /**
   * 分析健康上下文
   * @param imageAnalysisData 图像分析数据
   */
  private async analyzeHealthContext(imageAnalysisData: any): Promise<{
    isHealthRelevant: boolean;
    context?: any;
  }> {
    // 健康相关标签
    const healthRelatedTags = [
      '医疗', '健康', '药物', '疾病', '症状', '皮肤', '伤口', '舌头',
      '医院', '诊所', '药片', '中草药', '食物', '运动', '健身', '营养',
    ];
    
    // 检查标签是否包含健康相关内容
    const matchingTags = imageAnalysisData.tags.filter((tag: string) =>
      healthRelatedTags.some(healthTag => tag.includes(healthTag))
    );
    
    if (matchingTags.length === 0) {
      return { isHealthRelevant: false };
    }
    
    // 根据健康相关内容进行更详细的分析
    try {
      const healthAnalysisResponse = await llmService.analyzeHealthContext(
        imageAnalysisData.description,
        matchingTags
      );
      
      return {
        isHealthRelevant: true,
        context: healthAnalysisResponse,
      };
    } catch (error) {
      logger.error('健康上下文分析失败:', error);
      return {
        isHealthRelevant: matchingTags.length > 0,
        context: { relatedTags: matchingTags },
      };
    }
  }
}