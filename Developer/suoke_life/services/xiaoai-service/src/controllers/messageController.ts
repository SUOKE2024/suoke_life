import { Request, Response } from 'express';
import { XiaoAiService } from '../services/XiaoAiService';
import { logger } from '../index';
import XiaoAiAgent from '../models/XiaoAiAgent';
import { DialectService } from '../services/DialectService';

// 创建服务实例
const xiaoAiService = new XiaoAiService();
const dialectService = new DialectService();

/**
 * 消息控制器 - 处理各类用户消息
 */
export const messageController = {
  /**
   * 处理用户文本消息
   */
  async processTextMessage(req: Request, res: Response): Promise<void> {
    try {
      const { userId, message } = req.body;
      
      if (!userId || !message) {
        res.status(400).json({ error: '用户ID和消息内容不能为空' });
        return;
      }
      
      logger.info(`收到用户${userId}的文本消息: ${message.substring(0, 50)}${message.length > 50 ? '...' : ''}`);
      
      // 处理用户消息
      const response = await xiaoAiService.processUserMessage(userId, message, 'text');
      
      res.status(200).json(response);
    } catch (error) {
      logger.error('处理文本消息失败:', error);
      res.status(500).json({ error: '处理消息时发生错误' });
    }
  },
  
  /**
   * 处理用户语音消息
   */
  async processVoiceMessage(req: Request, res: Response): Promise<void> {
    try {
      const { userId, audioBase64, transcription, dialectCode } = req.body;
      
      if (!userId || (!audioBase64 && !transcription)) {
        res.status(400).json({ error: '用户ID和音频数据或转录文本不能为空' });
        return;
      }
      
      logger.info(`收到用户${userId}的语音消息`);
      
      // 如果提供了转录文本，直接使用
      if (transcription) {
        const response = await xiaoAiService.processUserMessage(userId, transcription, 'voice');
        res.status(200).json(response);
        return;
      }
      
      // 执行语音转文本处理
      try {
        // 将Base64音频转换为Buffer
        const audioBuffer = Buffer.from(audioBase64, 'base64');
        
        // 检测方言（如果提供了方言代码则使用，否则自动检测）
        let detectedDialect = dialectCode;
        if (!detectedDialect) {
          const dialectResult = await dialectService.detectAudioDialect(audioBuffer);
          detectedDialect = dialectResult.dialectCode;
          logger.info(`检测到方言: ${detectedDialect}`);
        }
        
        // 转换为文本（如果是方言，先转换为普通话）
        let textContent;
        if (detectedDialect && detectedDialect !== 'MANDARIN') {
          // 将方言音频转换为普通话文本
          const translationResult = await dialectService.translateDialectAudio(detectedDialect, audioBuffer);
          textContent = translationResult.translation;
          logger.info(`方言音频已转换为普通话文本: ${textContent}`);
        } else {
          // 直接转换为文本
          const sttResult = await xiaoAiService.speechToText(audioBuffer);
          textContent = sttResult.text;
          logger.info(`语音已转换为文本: ${textContent}`);
        }
        
        // 处理文本内容
        const response = await xiaoAiService.processUserMessage(userId, textContent, 'voice', {
          originalAudio: audioBase64,
          detectedDialect,
        });
        
        res.status(200).json(response);
      } catch (sttError) {
        logger.error('语音转文本失败:', sttError);
        res.status(422).json({ error: '语音转文本失败，请尝试清晰地说话或使用文本输入' });
      }
    } catch (error) {
      logger.error('处理语音消息失败:', error);
      res.status(500).json({ error: '处理语音消息时发生错误' });
    }
  },
  
  /**
   * 处理用户图像消息
   */
  async processImageMessage(req: Request, res: Response): Promise<void> {
    try {
      const { userId, imageBase64, caption } = req.body;
      
      if (!userId || !imageBase64) {
        res.status(400).json({ error: '用户ID和图像数据不能为空' });
        return;
      }
      
      logger.info(`收到用户${userId}的图像消息`);
      
      // 分析图像内容
      const imageBuffer = Buffer.from(imageBase64, 'base64');
      const imageAnalysisResult = await xiaoAiService.analyzeImage(imageBuffer);
      
      // 生成图像描述
      const imageDescription = caption || imageAnalysisResult.description;
      
      // 处理带有上下文的消息
      const contextMessage = `[用户发送了一张图片${imageDescription ? ': ' + imageDescription : ''}]`;
      const analysisContext = {
        imageAnalysis: imageAnalysisResult,
        originalImage: imageBase64,
      };
      
      const response = await xiaoAiService.processUserMessage(userId, contextMessage, 'image', analysisContext);
      res.status(200).json(response);
    } catch (error) {
      logger.error('处理图像消息失败:', error);
      res.status(500).json({ error: '处理图像消息时发生错误' });
    }
  },
  
  /**
   * 获取用户消息历史
   */
  async getUserMessageHistory(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      const { limit = 50, offset = 0 } = req.query;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 过滤指定用户的对话
      const userConversation = agent.conversationHistory
        .filter(entry => entry.userId === userId || entry.userId === 'xiaoai')
        .slice(Number(offset), Number(offset) + Number(limit));
      
      res.status(200).json({
        total: agent.conversationHistory.filter(entry => entry.userId === userId || entry.userId === 'xiaoai').length,
        offset: Number(offset),
        limit: Number(limit),
        conversations: userConversation,
      });
    } catch (error) {
      logger.error('获取用户消息历史失败:', error);
      res.status(500).json({ error: '获取消息历史时发生错误' });
    }
  },
  
  /**
   * 清除用户消息历史
   */
  async clearUserMessageHistory(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 过滤掉指定用户的对话
      agent.conversationHistory = agent.conversationHistory.filter(
        entry => entry.userId !== userId && entry.userId !== 'xiaoai'
      );
      
      await agent.save();
      
      res.status(200).json({ success: true, message: '用户消息历史已清除' });
    } catch (error) {
      logger.error('清除用户消息历史失败:', error);
      res.status(500).json({ error: '清除消息历史时发生错误' });
    }
  },
};