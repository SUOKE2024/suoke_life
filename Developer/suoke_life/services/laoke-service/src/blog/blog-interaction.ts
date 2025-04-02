/**
 * 博客互动服务
 * 负责博客评论、点赞、分享等互动功能
 */
import {
  BlogComment,
  CommentStatus,
  BlogInteraction,
  BlogAnalytics
} from './types';
import { logger } from '../utils/logger';
import blogManagement from './blog-management';

class BlogInteractionService {
  // 模拟数据存储
  private commentsStore: Map<string, BlogComment> = new Map();
  private interactionsStore: Map<string, BlogInteraction[]> = new Map();
  private analyticsStore: Map<string, Map<string, BlogAnalytics>> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('博客互动服务初始化');
  }
  
  /**
   * 创建评论
   * @param comment 评论
   * @returns 创建的评论ID
   */
  public async createComment(
    comment: Omit<BlogComment, 'id' | 'createdAt' | 'updatedAt' | 'likeCount' | 'reportCount' | 'isPinned'>
  ): Promise<string> {
    // 验证博客存在
    const post = await blogManagement.getPost(comment.postId, false);
    if (!post) {
      throw new Error(`博客文章不存在: ${comment.postId}`);
    }
    
    // 验证是否允许评论
    if (!post.allowComments) {
      throw new Error(`该博客不允许评论`);
    }
    
    // 验证父评论存在
    if (comment.parentId) {
      const parentComment = await this.getComment(comment.parentId);
      if (!parentComment) {
        throw new Error(`父评论不存在: ${comment.parentId}`);
      }
      
      // 验证父评论属于同一博客
      if (parentComment.postId !== comment.postId) {
        throw new Error(`父评论不属于同一博客`);
      }
    }
    
    const id = `comment-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    const newComment: BlogComment = {
      ...comment,
      id,
      createdAt: now,
      updatedAt: now,
      likeCount: 0,
      reportCount: 0,
      isPinned: false
    };
    
    this.commentsStore.set(id, newComment);
    
    // 增加博客评论计数
    await blogManagement.updatePost(comment.postId, {
      commentCount: post.commentCount + 1
    });
    
    logger.info(`创建评论: ${id}`, {
      postId: comment.postId,
      commenterName: comment.commenterName,
      parentId: comment.parentId
    });
    
    return id;
  }
  
  /**
   * 获取评论
   * @param id 评论ID
   * @returns 评论或null
   */
  public async getComment(id: string): Promise<BlogComment | null> {
    if (!this.commentsStore.has(id)) {
      logger.warn(`获取失败，评论不存在: ${id}`);
      return null;
    }
    
    logger.info(`获取评论: ${id}`);
    
    return this.commentsStore.get(id)!;
  }
  
  /**
   * 更新评论
   * @param id 评论ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateComment(
    id: string,
    updates: Partial<Pick<BlogComment, 'content' | 'status' | 'isPinned'>>
  ): Promise<boolean> {
    if (!this.commentsStore.has(id)) {
      logger.warn(`更新失败，评论不存在: ${id}`);
      return false;
    }
    
    const comment = this.commentsStore.get(id)!;
    
    const updatedComment: BlogComment = {
      ...comment,
      ...updates,
      updatedAt: new Date()
    };
    
    this.commentsStore.set(id, updatedComment);
    
    logger.info(`更新评论: ${id}`);
    
    return true;
  }
  
  /**
   * 删除评论
   * @param id 评论ID
   * @returns 是否删除成功
   */
  public async deleteComment(id: string): Promise<boolean> {
    if (!this.commentsStore.has(id)) {
      logger.warn(`删除失败，评论不存在: ${id}`);
      return false;
    }
    
    const comment = this.commentsStore.get(id)!;
    
    // 查找所有子评论
    const childComments = Array.from(this.commentsStore.values())
      .filter(c => c.parentId === id);
    
    // 递归删除子评论
    for (const childComment of childComments) {
      await this.deleteComment(childComment.id);
    }
    
    this.commentsStore.delete(id);
    
    // 减少博客评论计数
    const post = await blogManagement.getPost(comment.postId, false);
    if (post) {
      await blogManagement.updatePost(comment.postId, {
        commentCount: Math.max(0, post.commentCount - 1)
      });
    }
    
    logger.info(`删除评论: ${id}`, {
      postId: comment.postId
    });
    
    return true;
  }
  
  /**
   * 获取博客评论
   * @param postId 博客ID
   * @param status 评论状态
   * @param parentId 父评论ID，如果为undefined则获取顶层评论
   * @returns 评论列表
   */
  public async getPostComments(
    postId: string,
    status: CommentStatus[] = [CommentStatus.APPROVED],
    parentId?: string
  ): Promise<BlogComment[]> {
    // 验证博客存在
    const post = await blogManagement.getPost(postId, false);
    if (!post) {
      throw new Error(`博客文章不存在: ${postId}`);
    }
    
    let comments = Array.from(this.commentsStore.values())
      .filter(comment => comment.postId === postId);
    
    // 按状态过滤
    if (status && status.length > 0) {
      comments = comments.filter(comment => 
        status.includes(comment.status)
      );
    }
    
    // 按父评论过滤
    if (parentId !== undefined) {
      comments = comments.filter(comment => 
        comment.parentId === parentId
      );
    } else {
      // 获取顶层评论
      comments = comments.filter(comment => 
        !comment.parentId
      );
    }
    
    // 置顶评论显示在前面，然后按创建时间倒序排序
    comments.sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return b.createdAt.getTime() - a.createdAt.getTime();
    });
    
    logger.info(`获取博客评论列表`, {
      postId,
      count: comments.length,
      status,
      parentId
    });
    
    return comments;
  }
  
  /**
   * 审核评论
   * @param id 评论ID
   * @param approved 是否批准
   * @returns 是否审核成功
   */
  public async moderateComment(id: string, approved: boolean): Promise<boolean> {
    const status = approved ? CommentStatus.APPROVED : CommentStatus.SPAM;
    return await this.updateComment(id, { status });
  }
  
  /**
   * 置顶评论
   * @param id 评论ID
   * @param pinned 是否置顶
   * @returns 是否操作成功
   */
  public async pinComment(id: string, pinned: boolean): Promise<boolean> {
    return await this.updateComment(id, { isPinned: pinned });
  }
  
  /**
   * 点赞评论
   * @param id 评论ID
   * @param userId 用户ID
   * @returns 是否点赞成功
   */
  public async likeComment(id: string, userId: string): Promise<boolean> {
    if (!this.commentsStore.has(id)) {
      logger.warn(`点赞失败，评论不存在: ${id}`);
      return false;
    }
    
    const comment = this.commentsStore.get(id)!;
    
    // 检查评论状态是否已批准
    if (comment.status !== CommentStatus.APPROVED) {
      logger.warn(`点赞失败，评论未批准: ${id}`);
      return false;
    }
    
    const interactionKey = `${id}:${userId}:like`;
    
    // 检查是否已点赞
    const interactionExists = this.checkInteractionExists(interactionKey);
    if (interactionExists) {
      logger.info(`用户已点赞评论: ${id}`, { userId });
      return true;
    }
    
    // 增加点赞计数
    const updatedComment: BlogComment = {
      ...comment,
      likeCount: comment.likeCount + 1
    };
    
    this.commentsStore.set(id, updatedComment);
    
    // 记录点赞行为
    this.recordInteraction(interactionKey);
    
    logger.info(`点赞评论: ${id}`, { userId });
    
    return true;
  }
  
  /**
   * 举报评论
   * @param id 评论ID
   * @param userId 用户ID
   * @param reason 举报原因
   * @returns 是否举报成功
   */
  public async reportComment(id: string, userId: string, reason: string): Promise<boolean> {
    if (!this.commentsStore.has(id)) {
      logger.warn(`举报失败，评论不存在: ${id}`);
      return false;
    }
    
    const comment = this.commentsStore.get(id)!;
    
    const interactionKey = `${id}:${userId}:report`;
    
    // 检查是否已举报
    const interactionExists = this.checkInteractionExists(interactionKey);
    if (interactionExists) {
      logger.info(`用户已举报评论: ${id}`, { userId });
      return true;
    }
    
    // 增加举报计数
    const updatedComment: BlogComment = {
      ...comment,
      reportCount: comment.reportCount + 1
    };
    
    this.commentsStore.set(id, updatedComment);
    
    // 记录举报行为
    this.recordInteraction(interactionKey, { reason });
    
    // 如果举报次数达到阈值，自动将评论状态改为待审核
    if (updatedComment.reportCount >= 5) {
      await this.updateComment(id, { status: CommentStatus.PENDING });
    }
    
    logger.info(`举报评论: ${id}`, { userId, reason });
    
    return true;
  }
  
  /**
   * 记录博客互动
   * @param postId 博客ID
   * @param interaction 互动数据
   * @returns 是否记录成功
   */
  public async recordBlogInteraction(
    postId: string,
    interaction: Omit<BlogInteraction, 'createdAt'>
  ): Promise<boolean> {
    // 验证博客存在
    const post = await blogManagement.getPost(postId, false);
    if (!post) {
      logger.warn(`记录失败，博客文章不存在: ${postId}`);
      return false;
    }
    
    // 创建互动记录
    const newInteraction: BlogInteraction = {
      ...interaction,
      postId,
      createdAt: new Date()
    };
    
    // 存储互动记录
    if (!this.interactionsStore.has(postId)) {
      this.interactionsStore.set(postId, []);
    }
    
    this.interactionsStore.get(postId)!.push(newInteraction);
    
    // 更新博客相关计数
    switch (interaction.type) {
      case 'like':
        await blogManagement.updatePost(postId, {
          likeCount: post.likeCount + 1
        });
        break;
      case 'share':
        await blogManagement.updatePost(postId, {
          shareCount: post.shareCount + 1
        });
        break;
      case 'rate':
        if (interaction.rating !== undefined) {
          // 计算新的平均评分
          const newRatingCount = post.ratingCount + 1;
          const newRating = ((post.rating * post.ratingCount) + interaction.rating) / newRatingCount;
          
          await blogManagement.updatePost(postId, {
            rating: newRating,
            ratingCount: newRatingCount
          });
        }
        break;
    }
    
    // 更新分析数据
    await this.updateAnalytics(postId, interaction);
    
    logger.info(`记录博客互动`, {
      postId,
      type: interaction.type,
      userId: interaction.userId
    });
    
    return true;
  }
  
  /**
   * 获取博客互动列表
   * @param postId 博客ID
   * @param type 互动类型
   * @returns 互动列表
   */
  public async getBlogInteractions(
    postId: string,
    type?: 'view' | 'like' | 'bookmark' | 'share' | 'rate'
  ): Promise<BlogInteraction[]> {
    if (!this.interactionsStore.has(postId)) {
      return [];
    }
    
    let interactions = this.interactionsStore.get(postId)!;
    
    // 按类型过滤
    if (type) {
      interactions = interactions.filter(interaction => 
        interaction.type === type
      );
    }
    
    // 按时间倒序排序
    interactions.sort((a, b) => 
      b.createdAt.getTime() - a.createdAt.getTime()
    );
    
    logger.info(`获取博客互动列表`, {
      postId,
      type,
      count: interactions.length
    });
    
    return interactions;
  }
  
  /**
   * 获取用户博客互动
   * @param userId 用户ID
   * @param type 互动类型
   * @returns 互动列表
   */
  public async getUserInteractions(
    userId: string,
    type?: 'view' | 'like' | 'bookmark' | 'share' | 'rate'
  ): Promise<BlogInteraction[]> {
    const allInteractions: BlogInteraction[] = [];
    
    // 收集所有博客的互动
    for (const [postId, interactions] of this.interactionsStore.entries()) {
      const userInteractions = interactions.filter(interaction => 
        interaction.userId === userId &&
        (type === undefined || interaction.type === type)
      );
      
      allInteractions.push(...userInteractions);
    }
    
    // 按时间倒序排序
    allInteractions.sort((a, b) => 
      b.createdAt.getTime() - a.createdAt.getTime()
    );
    
    logger.info(`获取用户博客互动`, {
      userId,
      type,
      count: allInteractions.length
    });
    
    return allInteractions;
  }
  
  /**
   * 获取博客分析数据
   * @param postId 博客ID
   * @param startDate 开始日期
   * @param endDate 结束日期
   * @returns 分析数据列表
   */
  public async getBlogAnalytics(
    postId: string,
    startDate?: Date,
    endDate?: Date
  ): Promise<BlogAnalytics[]> {
    if (!this.analyticsStore.has(postId)) {
      return [];
    }
    
    let analytics = Array.from(this.analyticsStore.get(postId)!.values());
    
    // 按日期过滤
    if (startDate) {
      analytics = analytics.filter(data => data.date >= startDate);
    }
    
    if (endDate) {
      analytics = analytics.filter(data => data.date <= endDate);
    }
    
    // 按日期排序
    analytics.sort((a, b) => a.date.getTime() - b.date.getTime());
    
    logger.info(`获取博客分析数据`, {
      postId,
      startDate,
      endDate,
      count: analytics.length
    });
    
    return analytics;
  }
  
  /**
   * 获取博客汇总分析
   * @param postId 博客ID
   * @returns 汇总分析数据
   */
  public async getBlogAnalyticsSummary(postId: string): Promise<{
    totalViews: number;
    uniqueVisitors: number;
    avgDwellTime: number;
    completionRate: number;
    topTrafficSources: { source: string; count: number }[];
    deviceDistribution: { device: string; percentage: number }[];
  }> {
    const analytics = await this.getBlogAnalytics(postId);
    
    if (analytics.length === 0) {
      return {
        totalViews: 0,
        uniqueVisitors: 0,
        avgDwellTime: 0,
        completionRate: 0,
        topTrafficSources: [],
        deviceDistribution: []
      };
    }
    
    // 计算总浏览量
    const totalViews = analytics.reduce((sum, data) => sum + data.views, 0);
    
    // 计算总访客数(可能有重复)
    const totalVisitors = analytics.reduce((sum, data) => sum + data.uniqueVisitors, 0);
    
    // 计算平均停留时间
    const totalDwellTime = analytics.reduce((sum, data) => sum + data.avgDwellTime * data.views, 0);
    const avgDwellTime = totalViews > 0 ? totalDwellTime / totalViews : 0;
    
    // 计算平均完成率
    const totalCompletionRate = analytics.reduce((sum, data) => sum + data.completionRate * data.views, 0);
    const avgCompletionRate = totalViews > 0 ? totalCompletionRate / totalViews : 0;
    
    // 合并流量来源
    const trafficSourcesMap = new Map<string, number>();
    analytics.forEach(data => {
      Object.entries(data.trafficSources).forEach(([source, count]) => {
        const currentCount = trafficSourcesMap.get(source) || 0;
        trafficSourcesMap.set(source, currentCount + count);
      });
    });
    
    // 排序流量来源
    const topTrafficSources = Array.from(trafficSourcesMap.entries())
      .map(([source, count]) => ({ source, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
    
    // 合并设备分布
    const deviceMap = new Map<string, number>();
    analytics.forEach(data => {
      Object.entries(data.deviceDistribution).forEach(([device, count]) => {
        const currentCount = deviceMap.get(device) || 0;
        deviceMap.set(device, currentCount + count);
      });
    });
    
    // 计算设备百分比
    const totalDeviceCount = Array.from(deviceMap.values()).reduce((sum, count) => sum + count, 0);
    const deviceDistribution = Array.from(deviceMap.entries())
      .map(([device, count]) => ({
        device,
        percentage: totalDeviceCount > 0 ? (count * 100) / totalDeviceCount : 0
      }))
      .sort((a, b) => b.percentage - a.percentage);
    
    logger.info(`获取博客汇总分析`, {
      postId,
      totalViews,
      uniqueVisitors: totalVisitors
    });
    
    return {
      totalViews,
      uniqueVisitors: totalVisitors,
      avgDwellTime,
      completionRate: avgCompletionRate,
      topTrafficSources,
      deviceDistribution
    };
  }
  
  /**
   * 检查互动是否存在
   * @param key 互动键
   * @returns 是否存在
   */
  private checkInteractionExists(key: string): boolean {
    // 这里简化实现，实际应该使用数据库
    return false;
  }
  
  /**
   * 记录互动
   * @param key 互动键
   * @param data 互动数据
   */
  private recordInteraction(key: string, data: any = {}): void {
    // 这里简化实现，实际应该使用数据库
    logger.info(`记录互动: ${key}`, data);
  }
  
  /**
   * 更新分析数据
   * @param postId 博客ID
   * @param interaction 互动数据
   */
  private async updateAnalytics(postId: string, interaction: BlogInteraction): Promise<void> {
    // 获取当天日期(不含时间)
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const dateKey = today.toISOString().split('T')[0];
    
    // 初始化分析存储
    if (!this.analyticsStore.has(postId)) {
      this.analyticsStore.set(postId, new Map());
    }
    
    const postAnalytics = this.analyticsStore.get(postId)!;
    
    // 获取或创建当天分析数据
    if (!postAnalytics.has(dateKey)) {
      postAnalytics.set(dateKey, {
        postId,
        date: today,
        views: 0,
        uniqueVisitors: 0,
        avgDwellTime: 0,
        likes: 0,
        comments: 0,
        shares: 0,
        bookmarks: 0,
        bounceRate: 0,
        conversionRate: 0,
        trafficSources: {},
        deviceDistribution: {},
        completionRate: 0
      });
    }
    
    const analytics = postAnalytics.get(dateKey)!;
    
    // 更新相关指标
    switch (interaction.type) {
      case 'view':
        analytics.views += 1;
        
        // 记录访问者(简化处理，实际应去重)
        analytics.uniqueVisitors += 1;
        
        // 记录停留时间
        if (interaction.dwellTime) {
          const totalTime = analytics.avgDwellTime * (analytics.views - 1) + interaction.dwellTime;
          analytics.avgDwellTime = totalTime / analytics.views;
        }
        
        // 记录阅读完成率
        if (interaction.position !== undefined) {
          const totalCompletion = analytics.completionRate * (analytics.views - 1) + interaction.position;
          analytics.completionRate = totalCompletion / analytics.views;
        }
        
        // 记录流量来源
        if (interaction.userDevice) {
          const device = interaction.userDevice;
          analytics.deviceDistribution[device] = (analytics.deviceDistribution[device] || 0) + 1;
        }
        
        break;
      case 'like':
        analytics.likes += 1;
        break;
      case 'share':
        analytics.shares += 1;
        
        // 记录分享平台
        if (interaction.sharePlatform) {
          const source = `share:${interaction.sharePlatform}`;
          analytics.trafficSources[source] = (analytics.trafficSources[source] || 0) + 1;
        }
        
        break;
      case 'bookmark':
        analytics.bookmarks += 1;
        break;
    }
    
    // 更新分析数据
    postAnalytics.set(dateKey, analytics);
  }
}

export default new BlogInteractionService();