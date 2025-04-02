import { Request, Response } from 'express';
import { AccessibilityService } from '../services/AccessibilityService';
import { VoiceGuidanceService } from '../services/VoiceGuidanceService';
import { XiaoAiService } from '../services/XiaoAiService';
import { logger } from '../index';
import User from '../models/User';
import XiaoAiAgent from '../models/XiaoAiAgent';

// 创建服务实例
const accessibilityService = new AccessibilityService();
const voiceGuidanceService = new VoiceGuidanceService();
const xiaoAiService = new XiaoAiService();

/**
 * 无障碍控制器 - 处理无障碍功能相关请求
 */
export const accessibilityController = {
  /**
   * 获取用户的无障碍需求配置
   */
  async getUserAccessibilityProfile(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 查找用户
      const user = await User.findOne({ userId });
      
      if (!user) {
        res.status(404).json({ error: '用户不存在' });
        return;
      }
      
      // 返回用户的无障碍需求信息
      res.status(200).json({
        userId: user.userId,
        accessibilityNeeds: user.accessibilityNeeds,
        voicePreferences: {
          voiceAssistantEnabled: user.preferences.voiceAssistantEnabled,
          voiceAssistantVolume: user.preferences.voiceAssistantVolume,
        },
      });
    } catch (error) {
      logger.error('获取用户无障碍需求配置失败:', error);
      res.status(500).json({ error: '获取无障碍需求配置时发生错误' });
    }
  },
  
  /**
   * 更新用户的无障碍需求配置
   */
  async updateUserAccessibilityProfile(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      const { accessibilityNeeds, voicePreferences } = req.body;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 更新用户的无障碍需求
      const updatedUser = await xiaoAiService.updateUserAccessibilityNeeds(
        userId,
        accessibilityNeeds
      );
      
      // 如果提供了语音偏好设置，也更新它们
      if (voicePreferences) {
        updatedUser.preferences.voiceAssistantEnabled = 
          voicePreferences.voiceAssistantEnabled !== undefined 
            ? voicePreferences.voiceAssistantEnabled 
            : updatedUser.preferences.voiceAssistantEnabled;
        
        updatedUser.preferences.voiceAssistantVolume = 
          voicePreferences.voiceAssistantVolume !== undefined 
            ? voicePreferences.voiceAssistantVolume 
            : updatedUser.preferences.voiceAssistantVolume;
        
        await updatedUser.save();
      }
      
      res.status(200).json({
        success: true,
        message: '用户无障碍需求配置已更新',
        user: {
          userId: updatedUser.userId,
          accessibilityNeeds: updatedUser.accessibilityNeeds,
          voicePreferences: {
            voiceAssistantEnabled: updatedUser.preferences.voiceAssistantEnabled,
            voiceAssistantVolume: updatedUser.preferences.voiceAssistantVolume,
          },
        },
      });
    } catch (error) {
      logger.error('更新用户无障碍需求配置失败:', error);
      res.status(500).json({ error: '更新无障碍需求配置时发生错误' });
    }
  },
  
  /**
   * 生成语音引导内容
   */
  async generateVoiceGuidance(req: Request, res: Response): Promise<void> {
    try {
      const { text, speed, language } = req.body;
      
      if (!text) {
        res.status(400).json({ error: '文本内容不能为空' });
        return;
      }
      
      // 生成语音引导
      const audioUrl = await voiceGuidanceService.generateVoiceGuidance(
        text,
        speed || 1.0,
        language || 'zh-CN'
      );
      
      res.status(200).json({
        success: true,
        audioUrl,
      });
    } catch (error) {
      logger.error('生成语音引导失败:', error);
      res.status(500).json({ error: '生成语音引导时发生错误' });
    }
  },
  
  /**
   * 为视障用户生成特殊引导
   */
  async generateBlindGuidance(req: Request, res: Response): Promise<void> {
    try {
      const { screenContext, action, speed } = req.body;
      
      if (!screenContext) {
        res.status(400).json({ error: '屏幕上下文不能为空' });
        return;
      }
      
      // 生成导盲引导
      const audioUrl = await voiceGuidanceService.generateBlindGuidance(
        screenContext,
        action,
        speed || 1.0
      );
      
      res.status(200).json({
        success: true,
        audioUrl,
      });
    } catch (error) {
      logger.error('生成导盲引导失败:', error);
      res.status(500).json({ error: '生成导盲引导时发生错误' });
    }
  },
  
  /**
   * 自动检测用户可能的无障碍需求
   */
  async detectUserAccessibilityNeeds(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 获取小艾智能体以访问对话历史
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 获取与该用户的对话历史
      const userInteractions = agent.conversationHistory.filter(
        entry => entry.userId === userId
      );
      
      // 检测可能的无障碍需求
      const potentialNeeds = await accessibilityService.detectPotentialAccessibilityNeeds(
        userId,
        userInteractions
      );
      
      // 仅在检测到需求时返回结果
      if (Object.keys(potentialNeeds).length > 0) {
        res.status(200).json({
          success: true,
          potentialNeeds,
          message: '检测到可能的无障碍需求',
        });
      } else {
        res.status(200).json({
          success: true,
          potentialNeeds: {},
          message: '未检测到明显的无障碍需求',
        });
      }
    } catch (error) {
      logger.error('检测用户无障碍需求失败:', error);
      res.status(500).json({ error: '检测无障碍需求时发生错误' });
    }
  },
  
  /**
   * 获取针对用户的无障碍使用提示
   */
  async getAccessibilityTips(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 查找用户
      const user = await User.findOne({ userId });
      
      if (!user) {
        res.status(404).json({ error: '用户不存在' });
        return;
      }
      
      // 生成无障碍使用提示
      const tips = accessibilityService.generateAccessibilityTips(user);
      
      res.status(200).json({
        success: true,
        tips,
      });
    } catch (error) {
      logger.error('获取无障碍使用提示失败:', error);
      res.status(500).json({ error: '获取无障碍使用提示时发生错误' });
    }
  },
};