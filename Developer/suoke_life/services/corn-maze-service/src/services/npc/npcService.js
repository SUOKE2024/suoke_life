/**
 * 老克NPC服务
 * 提供与老克NPC的交互功能，包括对话、任务和知识管理
 */
const axios = require('axios');
const mongoose = require('mongoose');
const logger = require('../../utils/logger');

// 导入模型
const NPCInteraction = require('../../models/npcInteraction.model');
const Quest = require('../../models/quest.model');

/**
 * 老克NPC服务类
 */
class NPCService {
  /**
   * 构造函数
   */
  constructor() {
    this.laokeServiceUrl = process.env.LAOKE_SERVICE_URL || 'http://localhost:3005';
    this.knowledgeServiceUrl = process.env.KNOWLEDGE_GRAPH_SERVICE_URL || 'http://localhost:3006';
  }

  /**
   * 与NPC进行对话交互
   * @param {string} userId - 用户ID
   * @param {string} npcId - NPC ID，默认为"老克"
   * @param {string} message - 用户消息
   * @param {Object} context - 交互上下文
   * @returns {Promise<Object>} - 返回NPC回复及相关动作
   */
  async interact(userId, npcId = 'laoke', message, context = {}) {
    try {
      logger.info(`用户[${userId}]与NPC[${npcId}]交互: ${message}`);

      // 构建交互上下文
      const enrichedContext = await this.enrichContext(userId, context);
      
      // 调用老克服务进行对话处理
      const response = await axios.post(`${this.laokeServiceUrl}/api/dialogue`, {
        userId,
        npcId,
        message,
        context: enrichedContext
      });

      // 记录交互
      await this.recordInteraction(userId, npcId, message, response.data);

      // 处理可能触发的任务
      if (response.data.quest) {
        await this.processQuest(userId, response.data.quest);
      }

      return response.data;
    } catch (error) {
      logger.error('NPC交互失败', error);
      throw new Error(`与NPC[${npcId}]交互失败: ${error.message}`);
    }
  }

  /**
   * 丰富交互上下文
   * @param {string} userId - 用户ID
   * @param {Object} baseContext - 基础上下文
   * @returns {Promise<Object>} - 返回增强的上下文
   */
  async enrichContext(userId, baseContext) {
    // 获取用户历史交互
    const recentInteractions = await NPCInteraction.find({ userId })
      .sort({ createdAt: -1 })
      .limit(10)
      .lean();
    
    // 获取用户当前任务
    const activeQuests = await Quest.find({ 
      userId, 
      status: { $in: ['active', 'in_progress'] } 
    }).lean();
    
    // 从知识图谱获取相关知识
    let relevantKnowledge = [];
    try {
      const knowledgeResponse = await axios.post(
        `${this.knowledgeServiceUrl}/api/knowledge/relevant`,
        { 
          userId,
          context: baseContext.location || {},
          topics: ['corn', 'agriculture', 'maze']
        }
      );
      relevantKnowledge = knowledgeResponse.data.knowledge || [];
    } catch (err) {
      logger.warn('获取相关知识失败', err);
      // 失败时继续，不阻断主流程
    }

    // 返回增强的上下文
    return {
      ...baseContext,
      recentInteractions: recentInteractions.map(i => ({
        message: i.userMessage,
        response: i.npcResponse,
        timestamp: i.createdAt
      })),
      activeQuests: activeQuests.map(q => ({
        id: q._id,
        title: q.title,
        progress: q.progress,
        deadline: q.deadline
      })),
      relevantKnowledge
    };
  }

  /**
   * 记录NPC交互
   * @param {string} userId - 用户ID
   * @param {string} npcId - NPC ID
   * @param {string} userMessage - 用户消息
   * @param {Object} npcResponse - NPC回复
   * @returns {Promise<Object>} - 返回交互记录
   */
  async recordInteraction(userId, npcId, userMessage, npcResponse) {
    try {
      const interaction = new NPCInteraction({
        userId,
        npcId,
        userMessage,
        npcResponse: npcResponse.message,
        sentiment: npcResponse.sentiment || 'neutral',
        actions: npcResponse.actions || [],
        location: npcResponse.context?.location || {}
      });
      
      await interaction.save();
      return interaction;
    } catch (error) {
      logger.error('记录NPC交互失败', error);
      // 记录失败不应影响主流程
      return null;
    }
  }

  /**
   * 处理任务逻辑
   * @param {string} userId - 用户ID
   * @param {Object} questData - 任务数据
   * @returns {Promise<Object>} - 返回处理后的任务
   */
  async processQuest(userId, questData) {
    try {
      // 检查是否是新任务
      if (questData.action === 'new') {
        // 创建新任务
        const quest = new Quest({
          userId,
          title: questData.title,
          description: questData.description,
          type: questData.type || 'standard',
          rewards: questData.rewards || [],
          steps: questData.steps || [],
          deadline: questData.deadline,
          difficulty: questData.difficulty || 'normal',
          status: 'active',
          progress: 0
        });
        
        await quest.save();
        logger.info(`为用户[${userId}]创建新任务: ${quest.title}`);
        
        return quest;
      } 
      // 更新任务进度
      else if (questData.action === 'update' && questData.questId) {
        const quest = await Quest.findById(questData.questId);
        
        if (!quest) {
          logger.warn(`任务未找到: ${questData.questId}`);
          return null;
        }
        
        // 更新进度
        if (questData.progress !== undefined) {
          quest.progress = questData.progress;
        }
        
        // 更新状态
        if (questData.status) {
          quest.status = questData.status;
        }
        
        // 添加新步骤
        if (questData.newStep) {
          quest.steps.push(questData.newStep);
        }
        
        await quest.save();
        logger.info(`更新用户[${userId}]的任务进度: ${quest.title} (${quest.progress}%)`);
        
        return quest;
      }
      
      return null;
    } catch (error) {
      logger.error('处理任务失败', error);
      return null;
    }
  }

  /**
   * 获取NPC相关知识
   * @param {string} npcId - NPC ID
   * @param {string} topic - 知识主题
   * @returns {Promise<Array>} - 返回知识列表
   */
  async getNPCKnowledge(npcId = 'laoke', topic) {
    try {
      const response = await axios.get(
        `${this.knowledgeServiceUrl}/api/knowledge/npc/${npcId}`,
        { params: { topic } }
      );
      
      return response.data.knowledge || [];
    } catch (error) {
      logger.error('获取NPC知识失败', error);
      return [];
    }
  }
}

module.exports = new NPCService(); 