/**
 * 知识传播服务
 * 负责知识内容的推送、传播和分享
 */
import { 
  KnowledgeContent, 
  ContentType, 
  KnowledgeDomain, 
  ContentStatus 
} from './types';
import { logger } from '../utils/logger';
import knowledgeManagement from './knowledge-management';

/**
 * 推送渠道枚举
 */
enum DistributionChannel {
  // 应用内推送
  APP = 'app',
  // 电子邮件
  EMAIL = 'email',
  // 短信
  SMS = 'sms',
  // 社交媒体
  SOCIAL = 'social',
  // 定制频道
  CUSTOM = 'custom'
}

/**
 * 推送目标接口
 */
interface DistributionTarget {
  // 目标ID
  id: string;
  // 目标类型
  type: 'user' | 'user_group' | 'topic' | 'channel';
  // 目标名称
  name: string;
  // 推送首选渠道
  preferredChannels: DistributionChannel[];
  // 元数据
  metadata: Record<string, any>;
}

/**
 * 推送任务接口
 */
interface DistributionTask {
  // 任务ID
  id: string;
  // 内容ID
  contentId: string;
  // 推送目标ID列表
  targetIds: string[];
  // 推送渠道
  channels: DistributionChannel[];
  // 计划推送时间
  scheduledTime: Date;
  // 是否已执行
  executed: boolean;
  // 执行时间
  executedTime?: Date;
  // 推送结果
  results?: DistributionResult[];
  // 创建者ID
  creatorId: string;
  // 创建时间
  createdAt: Date;
}

/**
 * 推送结果接口
 */
interface DistributionResult {
  // 目标ID
  targetId: string;
  // 渠道
  channel: DistributionChannel;
  // 是否成功
  success: boolean;
  // 错误信息
  error?: string;
  // 发送时间
  sentTime: Date;
  // 是否已查看
  viewed: boolean;
  // 查看时间
  viewedTime?: Date;
  // 交互数据
  interactionData?: Record<string, any>;
}

class KnowledgeDistribution {
  // 模拟数据存储
  private targetsStore: Map<string, DistributionTarget> = new Map();
  private tasksStore: Map<string, DistributionTask> = new Map();
  
  // 定时任务检查间隔(毫秒)
  private readonly TASK_CHECK_INTERVAL = 60000; // 1分钟
  
  // 定时器ID
  private taskCheckTimerId: NodeJS.Timeout | null = null;
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('知识传播服务初始化');
    this.startTaskChecker();
  }
  
  /**
   * 启动任务检查器
   */
  private startTaskChecker(): void {
    this.taskCheckTimerId = setInterval(() => {
      this.checkScheduledTasks();
    }, this.TASK_CHECK_INTERVAL);
    
    logger.info('启动定时任务检查器');
  }
  
  /**
   * 停止任务检查器
   */
  public stopTaskChecker(): void {
    if (this.taskCheckTimerId) {
      clearInterval(this.taskCheckTimerId);
      this.taskCheckTimerId = null;
      
      logger.info('停止定时任务检查器');
    }
  }
  
  /**
   * 检查计划任务
   */
  private async checkScheduledTasks(): Promise<void> {
    const now = new Date();
    const pendingTasks = Array.from(this.tasksStore.values())
      .filter(task => 
        !task.executed && 
        task.scheduledTime <= now
      );
    
    if (pendingTasks.length === 0) {
      return;
    }
    
    logger.info(`发现待执行的推送任务: ${pendingTasks.length}个`);
    
    for (const task of pendingTasks) {
      this.executeTask(task.id).catch(err => {
        logger.error(`执行推送任务失败: ${task.id}`, err);
      });
    }
  }
  
  /**
   * 创建推送目标
   * @param target 推送目标
   * @returns 目标ID
   */
  public async createTarget(
    target: Omit<DistributionTarget, 'id'>
  ): Promise<string> {
    const id = `target-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const newTarget = {
      ...target,
      id
    };
    
    this.targetsStore.set(id, newTarget);
    
    logger.info(`创建推送目标: ${id}`, {
      name: target.name,
      type: target.type
    });
    
    return id;
  }
  
  /**
   * 更新推送目标
   * @param id 目标ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateTarget(
    id: string,
    updates: Partial<Omit<DistributionTarget, 'id'>>
  ): Promise<boolean> {
    if (!this.targetsStore.has(id)) {
      logger.warn(`更新失败，推送目标不存在: ${id}`);
      return false;
    }
    
    const target = this.targetsStore.get(id)!;
    
    const updatedTarget = {
      ...target,
      ...updates
    };
    
    this.targetsStore.set(id, updatedTarget);
    
    logger.info(`更新推送目标: ${id}`);
    
    return true;
  }
  
  /**
   * 获取推送目标
   * @param id 目标ID
   * @returns 推送目标或null
   */
  public async getTarget(id: string): Promise<DistributionTarget | null> {
    if (!this.targetsStore.has(id)) {
      logger.warn(`获取失败，推送目标不存在: ${id}`);
      return null;
    }
    
    logger.info(`获取推送目标: ${id}`);
    
    return this.targetsStore.get(id)!;
  }
  
  /**
   * 删除推送目标
   * @param id 目标ID
   * @returns 是否删除成功
   */
  public async deleteTarget(id: string): Promise<boolean> {
    if (!this.targetsStore.has(id)) {
      logger.warn(`删除失败，推送目标不存在: ${id}`);
      return false;
    }
    
    this.targetsStore.delete(id);
    
    logger.info(`删除推送目标: ${id}`);
    
    return true;
  }
  
  /**
   * 创建推送任务
   * @param contentId 内容ID
   * @param targetIds 目标ID列表
   * @param channels 推送渠道
   * @param scheduledTime 计划推送时间
   * @param creatorId 创建者ID
   * @returns 任务ID
   */
  public async createTask(
    contentId: string,
    targetIds: string[],
    channels: DistributionChannel[],
    scheduledTime: Date,
    creatorId: string
  ): Promise<string> {
    // 验证内容是否存在
    const content = await knowledgeManagement.getContent(contentId);
    if (!content) {
      throw new Error(`内容不存在: ${contentId}`);
    }
    
    // 验证目标是否都存在
    for (const targetId of targetIds) {
      if (!this.targetsStore.has(targetId)) {
        throw new Error(`推送目标不存在: ${targetId}`);
      }
    }
    
    const id = `task-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    const newTask: DistributionTask = {
      id,
      contentId,
      targetIds,
      channels,
      scheduledTime,
      executed: false,
      creatorId,
      createdAt: now
    };
    
    this.tasksStore.set(id, newTask);
    
    logger.info(`创建推送任务: ${id}`, {
      contentId,
      targetCount: targetIds.length,
      scheduledTime
    });
    
    return id;
  }
  
  /**
   * 取消推送任务
   * @param id 任务ID
   * @returns 是否取消成功
   */
  public async cancelTask(id: string): Promise<boolean> {
    if (!this.tasksStore.has(id)) {
      logger.warn(`取消失败，推送任务不存在: ${id}`);
      return false;
    }
    
    const task = this.tasksStore.get(id)!;
    
    if (task.executed) {
      logger.warn(`取消失败，推送任务已执行: ${id}`);
      return false;
    }
    
    this.tasksStore.delete(id);
    
    logger.info(`取消推送任务: ${id}`);
    
    return true;
  }
  
  /**
   * 执行推送任务
   * @param id 任务ID
   * @returns 执行结果
   */
  public async executeTask(id: string): Promise<DistributionResult[]> {
    if (!this.tasksStore.has(id)) {
      throw new Error(`推送任务不存在: ${id}`);
    }
    
    const task = this.tasksStore.get(id)!;
    
    if (task.executed) {
      logger.warn(`推送任务已执行: ${id}`);
      return task.results || [];
    }
    
    logger.info(`执行推送任务: ${id}`);
    
    const content = await knowledgeManagement.getContent(task.contentId);
    if (!content) {
      throw new Error(`内容不存在: ${task.contentId}`);
    }
    
    const results: DistributionResult[] = [];
    const now = new Date();
    
    // 为每个目标在每个渠道执行推送
    for (const targetId of task.targetIds) {
      const target = await this.getTarget(targetId);
      if (!target) {
        continue;
      }
      
      // 确定要使用的渠道(交集)
      const effectiveChannels = task.channels.filter(channel => 
        target.preferredChannels.includes(channel)
      );
      
      // 如果没有有效渠道，使用第一个任务渠道
      if (effectiveChannels.length === 0 && task.channels.length > 0) {
        effectiveChannels.push(task.channels[0]);
      }
      
      // 在每个有效渠道执行推送
      for (const channel of effectiveChannels) {
        try {
          await this.distributeContentViaChannel(content, target, channel);
          
          // 记录成功结果
          results.push({
            targetId,
            channel,
            success: true,
            sentTime: now,
            viewed: false
          });
        } catch (error) {
          // 记录失败结果
          results.push({
            targetId,
            channel,
            success: false,
            error: String(error),
            sentTime: now,
            viewed: false
          });
        }
      }
    }
    
    // 更新任务状态
    const updatedTask: DistributionTask = {
      ...task,
      executed: true,
      executedTime: now,
      results
    };
    
    this.tasksStore.set(id, updatedTask);
    
    logger.info(`推送任务执行完成: ${id}`, {
      successCount: results.filter(r => r.success).length,
      failureCount: results.filter(r => !r.success).length
    });
    
    return results;
  }
  
  /**
   * 通过特定渠道分发内容
   * @param content 知识内容
   * @param target 推送目标
   * @param channel 推送渠道
   */
  private async distributeContentViaChannel(
    content: KnowledgeContent,
    target: DistributionTarget,
    channel: DistributionChannel
  ): Promise<void> {
    logger.info(`通过渠道分发内容`, {
      contentId: content.id,
      targetId: target.id,
      channel
    });
    
    // 这里应该实现实际的推送逻辑
    // 目前只是模拟操作
    
    switch (channel) {
      case DistributionChannel.APP:
        await this.sendAppNotification(content, target);
        break;
      case DistributionChannel.EMAIL:
        await this.sendEmailNotification(content, target);
        break;
      case DistributionChannel.SMS:
        await this.sendSmsNotification(content, target);
        break;
      case DistributionChannel.SOCIAL:
        await this.shareToSocialMedia(content, target);
        break;
      case DistributionChannel.CUSTOM:
        await this.distributeViaCustomChannel(content, target);
        break;
      default:
        throw new Error(`不支持的推送渠道: ${channel}`);
    }
  }
  
  /**
   * 发送应用内通知
   */
  private async sendAppNotification(content: KnowledgeContent, target: DistributionTarget): Promise<void> {
    // 模拟实现
    logger.info(`发送应用内通知`, {
      contentTitle: content.title,
      targetName: target.name
    });
  }
  
  /**
   * 发送电子邮件通知
   */
  private async sendEmailNotification(content: KnowledgeContent, target: DistributionTarget): Promise<void> {
    // 模拟实现
    logger.info(`发送电子邮件通知`, {
      contentTitle: content.title,
      targetName: target.name
    });
  }
  
  /**
   * 发送短信通知
   */
  private async sendSmsNotification(content: KnowledgeContent, target: DistributionTarget): Promise<void> {
    // 模拟实现
    logger.info(`发送短信通知`, {
      contentTitle: content.title,
      targetName: target.name
    });
  }
  
  /**
   * 分享到社交媒体
   */
  private async shareToSocialMedia(content: KnowledgeContent, target: DistributionTarget): Promise<void> {
    // 模拟实现
    logger.info(`分享到社交媒体`, {
      contentTitle: content.title,
      targetName: target.name
    });
  }
  
  /**
   * 通过自定义渠道分发
   */
  private async distributeViaCustomChannel(content: KnowledgeContent, target: DistributionTarget): Promise<void> {
    // 模拟实现
    logger.info(`通过自定义渠道分发`, {
      contentTitle: content.title,
      targetName: target.name,
      channel: target.metadata.customChannelName
    });
  }
  
  /**
   * 记录内容已被查看
   * @param taskId 任务ID
   * @param targetId 目标ID
   * @param channel 渠道
   * @returns 是否记录成功
   */
  public async markContentViewed(
    taskId: string,
    targetId: string,
    channel: DistributionChannel
  ): Promise<boolean> {
    if (!this.tasksStore.has(taskId)) {
      logger.warn(`记录失败，推送任务不存在: ${taskId}`);
      return false;
    }
    
    const task = this.tasksStore.get(taskId)!;
    
    if (!task.executed || !task.results) {
      logger.warn(`记录失败，推送任务未执行: ${taskId}`);
      return false;
    }
    
    // 查找匹配的结果
    const resultIndex = task.results.findIndex(result => 
      result.targetId === targetId && 
      result.channel === channel
    );
    
    if (resultIndex === -1) {
      logger.warn(`记录失败，找不到匹配的推送结果`, {
        taskId,
        targetId,
        channel
      });
      return false;
    }
    
    // 更新查看状态
    const updatedResults = [...task.results];
    updatedResults[resultIndex] = {
      ...updatedResults[resultIndex],
      viewed: true,
      viewedTime: new Date()
    };
    
    // 更新任务
    const updatedTask: DistributionTask = {
      ...task,
      results: updatedResults
    };
    
    this.tasksStore.set(taskId, updatedTask);
    
    logger.info(`记录内容已被查看`, {
      taskId,
      targetId,
      channel
    });
    
    return true;
  }
  
  /**
   * 记录内容互动数据
   * @param taskId 任务ID
   * @param targetId 目标ID
   * @param channel 渠道
   * @param interactionData 互动数据
   * @returns 是否记录成功
   */
  public async recordInteraction(
    taskId: string,
    targetId: string,
    channel: DistributionChannel,
    interactionData: Record<string, any>
  ): Promise<boolean> {
    if (!this.tasksStore.has(taskId)) {
      logger.warn(`记录失败，推送任务不存在: ${taskId}`);
      return false;
    }
    
    const task = this.tasksStore.get(taskId)!;
    
    if (!task.executed || !task.results) {
      logger.warn(`记录失败，推送任务未执行: ${taskId}`);
      return false;
    }
    
    // 查找匹配的结果
    const resultIndex = task.results.findIndex(result => 
      result.targetId === targetId && 
      result.channel === channel
    );
    
    if (resultIndex === -1) {
      logger.warn(`记录失败，找不到匹配的推送结果`, {
        taskId,
        targetId,
        channel
      });
      return false;
    }
    
    // 更新互动数据
    const updatedResults = [...task.results];
    updatedResults[resultIndex] = {
      ...updatedResults[resultIndex],
      interactionData: {
        ...updatedResults[resultIndex].interactionData,
        ...interactionData
      }
    };
    
    // 更新任务
    const updatedTask: DistributionTask = {
      ...task,
      results: updatedResults
    };
    
    this.tasksStore.set(taskId, updatedTask);
    
    logger.info(`记录内容互动数据`, {
      taskId,
      targetId,
      channel,
      interactionType: Object.keys(interactionData).join(',')
    });
    
    return true;
  }
  
  /**
   * 获取内容传播统计
   * @param contentId 内容ID
   * @returns 传播统计数据
   */
  public async getContentDistributionStats(contentId: string): Promise<{
    totalTasks: number;
    totalTargets: number;
    totalSent: number;
    totalViewed: number;
    viewRate: number;
    channelStats: Record<DistributionChannel, {
      sent: number;
      viewed: number;
      viewRate: number;
    }>;
  }> {
    // 查找涉及该内容的所有任务
    const relatedTasks = Array.from(this.tasksStore.values())
      .filter(task => task.contentId === contentId && task.executed);
    
    // 汇总统计数据
    let totalTargets = 0;
    let totalSent = 0;
    let totalViewed = 0;
    
    const channelStats: Record<string, {
      sent: number;
      viewed: number;
      viewRate: number;
    }> = {};
    
    // 初始化渠道统计
    Object.values(DistributionChannel).forEach(channel => {
      channelStats[channel] = {
        sent: 0,
        viewed: 0,
        viewRate: 0
      };
    });
    
    // 计算统计数据
    relatedTasks.forEach(task => {
      if (task.results) {
        task.results.forEach(result => {
          totalSent++;
          
          channelStats[result.channel].sent++;
          
          if (result.viewed) {
            totalViewed++;
            channelStats[result.channel].viewed++;
          }
        });
      }
      
      // 计算目标数量(去重)
      const uniqueTargets = new Set(task.targetIds);
      totalTargets += uniqueTargets.size;
    });
    
    // 计算查看率
    const viewRate = totalSent > 0 ? totalViewed / totalSent : 0;
    
    // 计算各渠道查看率
    Object.keys(channelStats).forEach(channel => {
      const stats = channelStats[channel];
      stats.viewRate = stats.sent > 0 ? stats.viewed / stats.sent : 0;
    });
    
    logger.info(`获取内容传播统计`, {
      contentId,
      totalTasks: relatedTasks.length,
      totalTargets,
      totalSent,
      totalViewed,
      viewRate
    });
    
    return {
      totalTasks: relatedTasks.length,
      totalTargets,
      totalSent,
      totalViewed,
      viewRate,
      channelStats: channelStats as Record<DistributionChannel, {
        sent: number;
        viewed: number;
        viewRate: number;
      }>
    };
  }
}

export default new KnowledgeDistribution();