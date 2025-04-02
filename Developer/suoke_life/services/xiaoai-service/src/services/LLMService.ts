import OpenAI from 'openai';
import { IConversationEntry } from '../models/XiaoAiAgent';
import { IUser } from '../models/User';
import { logger } from '../index';
import axios from 'axios';

/**
 * 用户意图接口
 */
interface UserIntent {
  isDiagnosticRequest: boolean;
  requestedDiagnostics?: string[];
  isAccessibilityRequest: boolean;
  requestedAccessibilityFeatures?: string[];
  primaryIntent: string;
  confidence: number;
}

/**
 * LLM服务 - 处理自然语言理解与生成
 */
export class LLMService {
  private client: OpenAI;
  private readonly apiKey: string;
  private readonly modelName: string;
  
  constructor() {
    this.apiKey = process.env.OPENAI_API_KEY || '';
    this.modelName = process.env.OPENAI_MODEL || 'gpt-3.5-turbo';

    this.client = new OpenAI({
      apiKey: this.apiKey,
    });
    
    logger.info('LLM服务已初始化');
  }
  
  /**
   * 检测用户意图
   */
  public async detectUserIntent(userMessage: string): Promise<UserIntent> {
    try {
      const response = await this.client.chat.completions.create({
        model: this.modelName,
        messages: [
          {
            role: 'system',
            content: `你是一个意图分析助手，负责分析用户消息并检测其意图。
            特别关注:
            1. 是否请求中医四诊服务(望诊、闻诊、问诊、切诊)
            2. 是否请求无障碍功能(如语音引导、大字体、高对比度等)
            3. 主要意图是什么
            
            以JSON格式返回，包含以下字段:
            {
              "isDiagnosticRequest": boolean,
              "requestedDiagnostics": string[] | null, // ["looking", "inquiry", "smell", "touch"]中的一个或多个
              "isAccessibilityRequest": boolean,
              "requestedAccessibilityFeatures": string[] | null,
              "primaryIntent": string, // 主要意图简短描述
              "confidence": number // 0-1之间的置信度
            }`,
          },
          {
            role: 'user',
            content: userMessage,
          },
        ],
        temperature: 0.1,
        response_format: { type: 'json_object' },
      });
      
      // 解析并返回意图分析结果
      const content = response.choices[0].message.content || '{}';
      const intent = JSON.parse(content) as UserIntent;
      
      logger.info('检测到用户意图:', intent);
      return intent;
    } catch (error) {
      logger.error('检测用户意图失败:', error);
      
      // 返回默认意图
      return {
        isDiagnosticRequest: false,
        isAccessibilityRequest: false,
        primaryIntent: 'general_inquiry',
        confidence: 0.5,
      };
    }
  }
  
  /**
   * 生成回复
   */
  public async generateResponse(
    userMessage: string,
    conversationHistory: IConversationEntry[],
    user: IUser
  ): Promise<string> {
    try {
      // 准备对话历史上下文
      const recentHistory = conversationHistory.slice(-10); // 最近10条消息
      
      const messages: any[] = [
        {
          role: 'system',
          content: this.getSystemPrompt(user),
        },
      ];
      
      // 添加对话历史
      recentHistory.forEach((entry) => {
        const role = entry.userId === 'xiaoai' ? 'assistant' : 'user';
        messages.push({
          role,
          content: entry.content,
        });
      });
      
      // 添加用户最新消息（如果不在历史记录中）
      if (recentHistory.length === 0 || recentHistory[recentHistory.length - 1].userId !== 'user') {
        messages.push({
          role: 'user',
          content: userMessage,
        });
      }
      
      // 调用OpenAI生成回复
      const response = await this.client.chat.completions.create({
        model: this.modelName,
        messages,
        temperature: 0.7,
        max_tokens: 1000,
      });
      
      const generatedResponse = response.choices[0].message.content || '抱歉，我遇到了一些问题，无法回应您的请求。';
      return generatedResponse;
    } catch (error) {
      logger.error('生成回复失败:', error);
      return '抱歉，我暂时无法处理您的请求。请稍后再试。';
    }
  }
  
  /**
   * 获取系统提示词
   */
  private getSystemPrompt(user: IUser): string {
    // 基础系统提示
    let systemPrompt = `你是小艾，索克生活APP首页(聊天频道)版主，负责统筹协调望诊、闻诊、问诊、切诊服务，并为用户提供无障碍功能服务。
    你的主要职责包括：
    1. 健康咨询与引导用户使用四诊服务
    2. 提供温暖、专业、友善的对话体验
    3. 基于中医理念提供健康生活方式建议
    
    回复风格：亲切、专业、简洁明了。使用简单易懂的语言描述复杂的健康概念。`;
    
    // 根据用户无障碍需求调整提示词
    if (user.accessibilityNeeds.visuallyImpaired) {
      systemPrompt += `
      重要：用户有视觉障碍，需要语音引导。
      - 使用详细、清晰的描述
      - 避免依赖视觉信息来解释概念
      - 提供线性、有序的指导步骤
      - 不要使用"点击这里"、"看这里"等视觉指向语言
      - 所有步骤都应详细且明确`;
    }
    
    if (user.accessibilityNeeds.hearingImpaired) {
      systemPrompt += `
      重要：用户有听力障碍。
      - 避免依赖音频信息
      - 提供视觉替代方案
      - 使用简洁、明确的文字`;
    }
    
    if (user.accessibilityNeeds.cognitiveImpaired) {
      systemPrompt += `
      重要：用户可能有认知障碍。
      - 使用简单、直接的语言
      - 避免过长的句子和段落
      - 一次只介绍一个概念
      - 重复重要信息
      - 避免使用复杂术语和专业词汇`;
    }
    
    // 添加用户偏好信息
    systemPrompt += `
    用户语言偏好: ${user.preferences.language}
    通知偏好: ${user.preferences.notificationsEnabled ? '启用' : '禁用'}
    语音助手: ${user.preferences.voiceAssistantEnabled ? '启用' : '禁用'}
    主题偏好: ${user.preferences.theme}`;
    
    return systemPrompt;
  }

  /**
   * 生成文本响应
   * @param prompt 提示内容
   * @param context 上下文信息
   */
  public async generateTextResponse(prompt: string, context?: any): Promise<string> {
    try {
      // 构建系统消息
      const systemMessage = this.buildSystemMessage(context);

      // 发送请求到OpenAI
      const response = await this.client.chat.completions.create({
        model: this.modelName,
        messages: [
          { role: 'system', content: systemMessage },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 800,
      });

      return response.choices[0].message.content || '对不起，我无法回答这个问题。';
    } catch (error) {
      logger.error('生成文本响应失败:', error);
      return '抱歉，我无法处理您的请求。请稍后再试。';
    }
  }

  /**
   * 生成图像响应
   * @param prompt 提示内容
   * @param imageAnalysis 图像分析结果
   * @param context 上下文信息
   */
  public async generateImageResponse(prompt: string, imageAnalysis: any, context?: any): Promise<string> {
    try {
      // 构建系统消息
      const systemMessage = this.buildSystemMessage(context, true);

      // 构建图像上下文
      const imageContext = this.buildImageContext(imageAnalysis);

      // 发送请求到OpenAI
      const response = await this.client.chat.completions.create({
        model: this.modelName,
        messages: [
          { role: 'system', content: systemMessage },
          { role: 'user', content: imageContext },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 800,
      });

      return response.choices[0].message.content || '对不起，我无法分析这张图片。';
    } catch (error) {
      logger.error('生成图像响应失败:', error);
      return '抱歉，我无法分析您的图片。请稍后再试或提供更清晰的图片。';
    }
  }

  /**
   * 分析健康上下文
   * @param description 图像描述
   * @param tags 相关标签
   */
  public async analyzeHealthContext(description: string, tags: string[]): Promise<any> {
    try {
      const prompt = `
分析以下图像描述和标签，判断是否与健康相关，并提取相关健康信息：

描述: ${description}

标签: ${tags.join(', ')}

请提供以下分析:
1. 这是否与健康或医疗相关?
2. 如果是，请识别可能的健康主题(如饮食、运动、症状、药物等)
3. 提取任何可能的健康关注点
4. 考虑到中医视角的相关性
`;

      const response = await this.client.chat.completions.create({
        model: this.modelName,
        messages: [
          { 
            role: 'system', 
            content: '你是一个专注于健康和医疗图像分析的AI助手，尤其擅长从中医角度分析健康相关内容。' 
          },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 500,
      });

      const analysisText = response.choices[0].message.content || '';

      // 结构化分析结果
      return this.structureHealthAnalysis(analysisText, tags);
    } catch (error) {
      logger.error('健康上下文分析失败:', error);
      return {
        isHealthRelevant: tags.length > 0,
        healthTopics: tags,
        tcmRelevance: 'unknown',
      };
    }
  }

  /**
   * 结构化健康分析结果
   * @param analysisText 分析文本
   * @param tags 原始标签
   */
  private structureHealthAnalysis(analysisText: string, tags: string[]): any {
    // 简单结构化，实际项目中可能需要更复杂的解析
    const isHealthRelevant = 
      analysisText.includes('是与健康相关') || 
      analysisText.includes('与健康相关') ||
      analysisText.includes('健康主题');
    
    const healthTopics = [];
    if (analysisText.includes('饮食')) healthTopics.push('diet');
    if (analysisText.includes('运动')) healthTopics.push('exercise');
    if (analysisText.includes('症状')) healthTopics.push('symptoms');
    if (analysisText.includes('药物')) healthTopics.push('medication');
    if (analysisText.includes('中草药')) healthTopics.push('herbs');
    if (analysisText.includes('保健')) healthTopics.push('wellness');

    const tcmRelevant = 
      analysisText.includes('中医') || 
      analysisText.includes('草药') || 
      analysisText.includes('针灸') ||
      analysisText.includes('经络') ||
      analysisText.includes('气血') ||
      analysisText.includes('阴阳');

    return {
      isHealthRelevant,
      healthTopics: healthTopics.length > 0 ? healthTopics : tags,
      rawAnalysis: analysisText,
      tcmRelevance: tcmRelevant ? 'relevant' : 'not_relevant',
    };
  }

  /**
   * 构建系统消息
   * @param context 上下文信息
   * @param isImageContext 是否是图像上下文
   */
  private buildSystemMessage(context?: any, isImageContext = false): string {
    // 构建基础系统消息
    let systemMessage = `你是小艾，索克生活APP的智能健康助手。你负责提供健康咨询和服务协调。
用户与你交流时，请保持友好、专业和有帮助性。`;

    // 添加用户特定信息
    if (context?.userProfile?.accessibilityNeeds) {
      const { accessibilityNeeds } = context.userProfile;
      
      if (accessibilityNeeds.visuallyImpaired) {
        systemMessage += `\n请注意，用户是视障人士，请提供清晰、详细的文字描述，避免依赖视觉信息。`;
      }
      
      if (accessibilityNeeds.hearingImpaired) {
        systemMessage += `\n请注意，用户是听障人士，避免依赖语音指令，使用文字交流。`;
      }
    }

    // 添加图像相关指南
    if (isImageContext) {
      systemMessage += `\n
你正在分析用户上传的图片。请根据提供的图像描述和分析结果回答用户问题。
如果图像与健康相关，请提供相关的健康建议或解释，尤其关注中医养生的视角。
如果不确定图像内容，请诚实告知并要求用户提供更多信息。`;
    }

    return systemMessage;
  }

  /**
   * 构建图像上下文
   * @param imageAnalysis 图像分析结果
   */
  private buildImageContext(imageAnalysis: any): string {
    let imageContext = `我上传了一张图片，系统分析结果如下：\n`;
    
    // 添加图像描述
    imageContext += `描述：${imageAnalysis.description || '无可用描述'}\n\n`;
    
    // 添加标签
    if (imageAnalysis.tags && imageAnalysis.tags.length > 0) {
      imageContext += `标签：${imageAnalysis.tags.join(', ')}\n\n`;
    }
    
    // 添加检测到的对象
    if (imageAnalysis.objects && imageAnalysis.objects.length > 0) {
      imageContext += `检测到的对象：${imageAnalysis.objects.map((obj: any) => obj.name).join(', ')}\n\n`;
    }
    
    // 添加健康相关信息
    if (imageAnalysis.healthRelevant && imageAnalysis.healthContext) {
      imageContext += `健康相关信息：
主题：${imageAnalysis.healthContext.healthTopics.join(', ')}
中医相关性：${imageAnalysis.healthContext.tcmRelevance === 'relevant' ? '相关' : '不相关'}
\n`;
    }
    
    return imageContext;
  }
}