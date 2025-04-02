import { Request, Response } from 'express';
import { XiaoAiService } from '../services/XiaoAiService';
import { logger } from '../index';
import XiaoAiAgent from '../models/XiaoAiAgent';

// 创建XiaoAi服务实例
const xiaoAiService = new XiaoAiService();

/**
 * 智能体控制器 - 管理小艾智能体状态和操作
 */
export const agentController = {
  /**
   * 获取小艾智能体状态
   */
  async getAgentStatus(req: Request, res: Response): Promise<void> {
    try {
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        // 如果智能体不存在，尝试初始化
        const newAgent = await xiaoAiService.initializeAgent();
        
        res.status(200).json({
          agentId: newAgent.agentId,
          name: newAgent.name,
          status: newAgent.status,
          version: newAgent.version,
          state: newAgent.state,
        });
        return;
      }
      
      res.status(200).json({
        agentId: agent.agentId,
        name: agent.name,
        status: agent.status,
        version: agent.version,
        state: agent.state,
      });
    } catch (error) {
      logger.error('获取智能体状态失败:', error);
      res.status(500).json({ error: '获取智能体状态时发生错误' });
    }
  },
  
  /**
   * 更新小艾智能体状态
   */
  async updateAgentStatus(req: Request, res: Response): Promise<void> {
    try {
      const { status, state } = req.body;
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 更新状态
      if (status) {
        agent.status = status;
      }
      
      // 更新状态配置
      if (state) {
        Object.assign(agent.state, state);
      }
      
      await agent.save();
      
      res.status(200).json({
        success: true,
        message: '智能体状态已更新',
        agent: {
          agentId: agent.agentId,
          name: agent.name,
          status: agent.status,
          version: agent.version,
          state: agent.state,
        },
      });
    } catch (error) {
      logger.error('更新智能体状态失败:', error);
      res.status(500).json({ error: '更新智能体状态时发生错误' });
    }
  },
  
  /**
   * 获取小艾智能体能力列表
   */
  async getAgentCapabilities(req: Request, res: Response): Promise<void> {
    try {
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      res.status(200).json({
        success: true,
        capabilities: agent.capabilities,
      });
    } catch (error) {
      logger.error('获取智能体能力列表失败:', error);
      res.status(500).json({ error: '获取智能体能力列表时发生错误' });
    }
  },
  
  /**
   * 重置小艾智能体
   */
  async resetAgent(req: Request, res: Response): Promise<void> {
    try {
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 重置状态
      agent.state = {
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
      };
      
      // 清空对话历史，但保留系统消息
      agent.conversationHistory = agent.conversationHistory.filter(
        entry => entry.messageType === 'system'
      );
      
      await agent.save();
      
      res.status(200).json({
        success: true,
        message: '智能体已重置',
      });
    } catch (error) {
      logger.error('重置智能体失败:', error);
      res.status(500).json({ error: '重置智能体时发生错误' });
    }
  },
  
  /**
   * 获取小艾智能体与特定用户的对话历史
   */
  async getConversationWithUser(req: Request, res: Response): Promise<void> {
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
      
      // 过滤与特定用户的对话
      const userConversation = agent.conversationHistory
        .filter(entry => entry.userId === userId || entry.userId === 'xiaoai')
        .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
        .slice(Number(offset), Number(offset) + Number(limit));
      
      res.status(200).json({
        success: true,
        total: agent.conversationHistory.filter(entry => entry.userId === userId || entry.userId === 'xiaoai').length,
        offset: Number(offset),
        limit: Number(limit),
        conversations: userConversation,
      });
    } catch (error) {
      logger.error('获取用户对话历史失败:', error);
      res.status(500).json({ error: '获取用户对话历史时发生错误' });
    }
  },
  
  /**
   * 获取小艾智能体使用指标
   */
  async getAgentMetrics(req: Request, res: Response): Promise<void> {
    try {
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 计算总对话数
      const totalConversations = agent.conversationHistory.length;
      
      // 计算唯一用户数
      const uniqueUsers = new Set(
        agent.conversationHistory
          .filter(entry => entry.userId !== 'xiaoai')
          .map(entry => entry.userId)
      ).size;
      
      // 计算按消息类型分组的统计
      const messageTypeStats = {
        text: 0,
        voice: 0,
        image: 0,
        system: 0,
      };
      
      agent.conversationHistory.forEach(entry => {
        if (messageTypeStats.hasOwnProperty(entry.messageType)) {
          messageTypeStats[entry.messageType as keyof typeof messageTypeStats]++;
        }
      });
      
      // 计算最近24小时的活跃度
      const last24Hours = new Date();
      last24Hours.setHours(last24Hours.getHours() - 24);
      
      const recentActivity = agent.conversationHistory.filter(
        entry => entry.timestamp > last24Hours
      ).length;
      
      res.status(200).json({
        success: true,
        metrics: {
          totalConversations,
          uniqueUsers,
          messageTypeStats,
          recentActivity,
        },
      });
    } catch (error) {
      logger.error('获取智能体使用指标失败:', error);
      res.status(500).json({ error: '获取智能体使用指标时发生错误' });
    }
  },
};