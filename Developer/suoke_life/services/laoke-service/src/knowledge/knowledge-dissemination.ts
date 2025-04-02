/**
 * 知识传播服务
 * 负责内容创建和分享、社区互动和热门话题管理
 */
import { logger } from '../utils/logger';

/**
 * 内容类型
 */
export enum ContentType {
  ARTICLE = 'article',    // 文章
  VIDEO = 'video',        // 视频
  PODCAST = 'podcast',    // 播客
  INFOGRAPHIC = 'infographic', // 信息图表
  QUIZ = 'quiz'           // 测验
}

/**
 * 内容
 */
export interface Content {
  id: string;                // 内容ID
  type: ContentType;         // 内容类型
  title: string;             // 标题
  description: string;       // 描述
  coverImage?: string;       // 封面图片
  body: string;              // 内容主体
  authorId: string;          // 作者ID
  authorName: string;        // 作者名称
  categoryId: string;        // 分类ID
  categoryName: string;      // 分类名称
  tags: string[];            // 标签
  viewCount: number;         // 查看次数
  likeCount: number;         // 点赞次数
  commentCount: number;      // 评论次数
  shareCount: number;        // 分享次数
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
  publishedAt?: Date;        // 发布时间
  status: 'draft' | 'published' | 'archived'; // 状态
  source?: string;           // 来源
  mediaUrl?: string;         // 媒体URL
  duration?: number;         // 时长(秒)
  relatedContentIds?: string[]; // 相关内容ID
  highlights?: string[];     // 内容亮点
  isFeatured: boolean;       // 是否精选
}

/**
 * 评论
 */
export interface Comment {
  id: string;                // 评论ID
  contentId: string;         // 内容ID
  userId: string;            // 用户ID
  userName: string;          // 用户名称
  userAvatar?: string;       // 用户头像
  body: string;              // 评论内容
  likeCount: number;         // 点赞次数
  parentId?: string;         // 父评论ID
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
  status: 'active' | 'hidden' | 'deleted'; // 状态
}

/**
 * 热门话题
 */
export interface Topic {
  id: string;                // 话题ID
  title: string;             // 话题标题
  description: string;       // 话题描述
  coverImage?: string;       // 封面图片
  contentCount: number;      // 内容数量
  followerCount: number;     // 关注人数
  tags: string[];            // 标签
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
  trendingScore: number;     // 热度分数
  status: 'active' | 'inactive'; // 状态
}

class KnowledgeDisseminationService {
  // 模拟数据存储
  private contentsStore: Map<string, Content> = new Map();
  private commentsStore: Map<string, Comment[]> = new Map();
  private topicsStore: Map<string, Topic> = new Map();
  private userFavoritesStore: Map<string, string[]> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('知识传播服务初始化');
    
    // 初始化示例内容和话题
    this.initSampleContents();
    this.initSampleTopics();
  }
  
  /**
   * 初始化示例内容
   */
  private initSampleContents(): void {
    const now = new Date();
    
    // 示例文章1：中医体质辨识入门
    const article1: Content = {
      id: 'content-article-1',
      type: ContentType.ARTICLE,
      title: '中医体质辨识入门：认识你的体质类型',
      description: '本文介绍中医九种体质的基本特征和辨识方法，帮助你了解自身体质类型。',
      coverImage: 'https://placeholder.com/800x450?text=中医体质辨识',
      body: `# 中医体质辨识入门
      
中医认为，体质是人体生命过程中，在先天禀赋和后天获得的基础上所形成的形态结构、生理功能和心理状态方面综合的、相对稳定的固有特性。
      
## 九种体质类型
      
1. **平和质**：阴阳气血调和，形体适中，面色红润，精力充沛，肌肉结实，食欲睡眠正常，性格平和开朗。
2. **气虚质**：元气不足，易疲劳，声音低弱，自汗，舌淡苔薄，脉弱。
3. **阳虚质**：畏寒肢冷，面色苍白，舌淡胖，脉迟。
4. **阴虚质**：手足心热，口干舌燥，性急易怒，舌红少苔，脉细数。
5. **痰湿质**：体形肥胖，腹部松软，多汗粘腻，舌苔厚腻，脉滑。

...（更多内容）

## 如何辨识自己的体质

通过以下方法可以初步辨识：
1. 观察自身特征
2. 填写体质测评问卷
3. 咨询专业中医师

索克生活APP提供体质测评功能，欢迎使用！`,
      authorId: 'laoke',
      authorName: '老克',
      categoryId: 'category-tcm-theory',
      categoryName: '中医理论',
      tags: ['体质辨识', '中医基础', '健康养生'],
      viewCount: 2356,
      likeCount: 187,
      commentCount: 42,
      shareCount: 76,
      createdAt: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000),
      publishedAt: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
      status: 'published',
      highlights: ['中医九种体质基本特征', '体质辨识实用方法', '体质调养基本原则'],
      isFeatured: true
    };
    
    // 示例视频1：四季养生指南
    const video1: Content = {
      id: 'content-video-1',
      type: ContentType.VIDEO,
      title: '四季养生指南：中医节气养生方法详解',
      description: '本视频详细讲解中医节气养生的理论与实践，结合24节气特点，指导日常饮食起居调养。',
      coverImage: 'https://placeholder.com/800x450?text=四季养生指南',
      body: '本视频详细介绍了二十四节气养生法，从春夏秋冬四季的特点出发，结合中医理论，提供实用的养生建议。包括各节气的饮食、起居、运动等方面的详细指导。',
      authorId: 'laoke',
      authorName: '老克',
      categoryId: 'category-seasonal-health',
      categoryName: '节气养生',
      tags: ['节气养生', '四季调养', '中医养生'],
      viewCount: 1876,
      likeCount: 246,
      commentCount: 58,
      shareCount: 123,
      createdAt: new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000),
      publishedAt: new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000),
      status: 'published',
      mediaUrl: 'https://example.com/videos/seasonal-health-guide.mp4',
      duration: 1560, // 26分钟
      highlights: ['二十四节气养生法详解', '春夏秋冬饮食指南', '节气起居调养建议'],
      isFeatured: true
    };
    
    // 保存示例内容
    this.contentsStore.set(article1.id, article1);
    this.contentsStore.set(video1.id, video1);
    
    // 为示例内容创建示例评论
    this.createSampleComments(article1.id, 5);
    this.createSampleComments(video1.id, 6);
    
    logger.info('示例内容初始化完成');
  }
  
  /**
   * 初始化示例话题
   */
  private initSampleTopics(): void {
    const now = new Date();
    
    // 示例话题1：春季养生
    const topic1: Topic = {
      id: 'topic-seasonal-spring',
      title: '春季养生',
      description: '春季养生的理论、方法和实践，包括饮食、起居、运动等多方面内容。',
      coverImage: 'https://placeholder.com/800x450?text=春季养生',
      contentCount: 24,
      followerCount: 356,
      tags: ['春季', '养生', '饮食调养', '起居调摄'],
      createdAt: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000),
      trendingScore: 87,
      status: 'active'
    };
    
    // 示例话题2：艾灸疗法
    const topic2: Topic = {
      id: 'topic-moxibustion',
      title: '艾灸疗法',
      description: '艾灸的基本原理、操作方法、适应证和禁忌证，以及常见穴位的艾灸应用。',
      coverImage: 'https://placeholder.com/800x450?text=艾灸疗法',
      contentCount: 18,
      followerCount: 278,
      tags: ['艾灸', '穴位', '温灸', '隔姜灸'],
      createdAt: new Date(now.getTime() - 45 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000),
      trendingScore: 65,
      status: 'active'
    };
    
    // 保存示例话题
    this.topicsStore.set(topic1.id, topic1);
    this.topicsStore.set(topic2.id, topic2);
    
    logger.info('示例话题初始化完成');
  }
  
  /**
   * 创建示例评论
   * @param contentId 内容ID
   * @param count 评论数量
   */
  private createSampleComments(contentId: string, count: number): void {
    const now = new Date();
    const comments: Comment[] = [];
    
    // 示例用户
    const users = [
      { id: 'user1', name: '健康达人', avatar: 'https://placeholder.com/50x50?text=用户1' },
      { id: 'user2', name: '养生爱好者', avatar: 'https://placeholder.com/50x50?text=用户2' },
      { id: 'user3', name: '中医学习者', avatar: 'https://placeholder.com/50x50?text=用户3' },
      { id: 'user4', name: '生活智慧家', avatar: 'https://placeholder.com/50x50?text=用户4' }
    ];
    
    // 示例评论内容
    const commentTexts = [
      '非常实用的内容，学到了很多！',
      '感谢分享，这些知识对我帮助很大。',
      '我一直对这个话题很感兴趣，这篇文章讲解得很清晰。',
      '建议再多介绍一些实际案例，会更加生动。',
      '已经开始尝试文中的方法，效果确实不错。',
      '期待更多相关内容！',
      '这些知识很传统，但也很实用，值得传承。',
      '想请教一下作者，这个方法适合什么体质的人？'
    ];
    
    // 生成评论
    for (let i = 0; i < count; i++) {
      const user = users[i % users.length];
      const text = commentTexts[i % commentTexts.length];
      const daysAgo = Math.floor(Math.random() * 7);
      
      comments.push({
        id: `comment-${contentId}-${i}`,
        contentId,
        userId: user.id,
        userName: user.name,
        userAvatar: user.avatar,
        body: text,
        likeCount: Math.floor(Math.random() * 20),
        createdAt: new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000),
        updatedAt: new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000),
        status: 'active'
      });
    }
    
    // 保存评论
    this.commentsStore.set(contentId, comments);
  }
  
  /**
   * 获取内容列表
   * @param type 内容类型
   * @param categoryId 分类ID
   * @param tag 标签
   * @param page 页码
   * @param limit 每页数量
   * @returns 内容列表和分页信息
   */
  public async getContents(
    type?: ContentType,
    categoryId?: string,
    tag?: string,
    page: number = 1,
    limit: number = 10
  ): Promise<{
    contents: Content[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    // 获取所有已发布的内容
    let contents = Array.from(this.contentsStore.values())
      .filter(content => content.status === 'published');
    
    // 类型过滤
    if (type) {
      contents = contents.filter(content => content.type === type);
    }
    
    // 分类过滤
    if (categoryId) {
      contents = contents.filter(content => content.categoryId === categoryId);
    }
    
    // 标签过滤
    if (tag) {
      contents = contents.filter(content => content.tags.includes(tag));
    }
    
    // 计算分页信息
    const total = contents.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    
    // 按发布时间排序
    contents.sort((a, b) => 
      (b.publishedAt?.getTime() || 0) - (a.publishedAt?.getTime() || 0)
    );
    
    // 分页
    const paginatedContents = contents.slice(offset, offset + limit);
    
    logger.info(`获取内容列表`, {
      type,
      categoryId,
      tag,
      page,
      limit,
      total
    });
    
    return {
      contents: paginatedContents,
      total,
      page,
      limit,
      totalPages
    };
  }
  
  /**
   * 获取内容详情
   * @param id 内容ID
   * @returns 内容详情
   */
  public async getContentById(id: string): Promise<Content | null> {
    if (!this.contentsStore.has(id)) {
      logger.warn(`获取失败，内容不存在: ${id}`);
      return null;
    }
    
    const content = this.contentsStore.get(id)!;
    
    // 增加查看次数
    content.viewCount += 1;
    this.contentsStore.set(id, content);
    
    logger.info(`获取内容详情`, {
      id,
      title: content.title,
      type: content.type
    });
    
    return content;
  }
  
  /**
   * 获取内容评论
   * @param contentId 内容ID
   * @returns 评论列表
   */
  public async getContentComments(contentId: string): Promise<Comment[]> {
    if (!this.commentsStore.has(contentId)) {
      return [];
    }
    
    const comments = this.commentsStore.get(contentId)!;
    
    // 按时间排序
    comments.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    logger.info(`获取内容评论`, {
      contentId,
      count: comments.length
    });
    
    return comments;
  }
  
  /**
   * 添加评论
   * @param contentId 内容ID
   * @param userId 用户ID
   * @param userName 用户名称
   * @param userAvatar 用户头像
   * @param body 评论内容
   * @param parentId 父评论ID
   * @returns 新评论
   */
  public async addComment(
    contentId: string,
    userId: string,
    userName: string,
    userAvatar: string | undefined,
    body: string,
    parentId?: string
  ): Promise<Comment> {
    if (!this.contentsStore.has(contentId)) {
      throw new Error(`内容不存在: ${contentId}`);
    }
    
    const now = new Date();
    
    // 创建评论
    const comment: Comment = {
      id: `comment-${contentId}-${Date.now()}`,
      contentId,
      userId,
      userName,
      userAvatar,
      body,
      likeCount: 0,
      parentId,
      createdAt: now,
      updatedAt: now,
      status: 'active'
    };
    
    // 保存评论
    if (!this.commentsStore.has(contentId)) {
      this.commentsStore.set(contentId, []);
    }
    
    this.commentsStore.get(contentId)!.push(comment);
    
    // 更新内容评论数
    const content = this.contentsStore.get(contentId)!;
    content.commentCount += 1;
    this.contentsStore.set(contentId, content);
    
    logger.info(`添加评论`, {
      contentId,
      userId,
      commentId: comment.id
    });
    
    return comment;
  }
  
  /**
   * 点赞内容
   * @param contentId 内容ID
   * @param userId 用户ID
   * @returns 是否成功
   */
  public async likeContent(
    contentId: string,
    userId: string
  ): Promise<boolean> {
    if (!this.contentsStore.has(contentId)) {
      logger.warn(`点赞失败，内容不存在: ${contentId}`);
      return false;
    }
    
    // 检查用户是否已点赞
    if (!this.userFavoritesStore.has(userId)) {
      this.userFavoritesStore.set(userId, []);
    }
    
    const userFavorites = this.userFavoritesStore.get(userId)!;
    const hasLiked = userFavorites.includes(contentId);
    
    if (hasLiked) {
      logger.warn(`点赞失败，用户已点赞: ${contentId}`, { userId });
      return false;
    }
    
    // 更新内容点赞数
    const content = this.contentsStore.get(contentId)!;
    content.likeCount += 1;
    this.contentsStore.set(contentId, content);
    
    // 更新用户点赞记录
    userFavorites.push(contentId);
    this.userFavoritesStore.set(userId, userFavorites);
    
    logger.info(`点赞内容`, {
      contentId,
      userId,
      newLikeCount: content.likeCount
    });
    
    return true;
  }
  
  /**
   * 取消点赞内容
   * @param contentId 内容ID
   * @param userId 用户ID
   * @returns 是否成功
   */
  public async unlikeContent(
    contentId: string,
    userId: string
  ): Promise<boolean> {
    if (!this.contentsStore.has(contentId)) {
      logger.warn(`取消点赞失败，内容不存在: ${contentId}`);
      return false;
    }
    
    // 检查用户是否已点赞
    if (!this.userFavoritesStore.has(userId)) {
      logger.warn(`取消点赞失败，用户未点赞: ${contentId}`, { userId });
      return false;
    }
    
    const userFavorites = this.userFavoritesStore.get(userId)!;
    const index = userFavorites.indexOf(contentId);
    
    if (index === -1) {
      logger.warn(`取消点赞失败，用户未点赞: ${contentId}`, { userId });
      return false;
    }
    
    // 更新内容点赞数
    const content = this.contentsStore.get(contentId)!;
    content.likeCount = Math.max(0, content.likeCount - 1);
    this.contentsStore.set(contentId, content);
    
    // 更新用户点赞记录
    userFavorites.splice(index, 1);
    this.userFavoritesStore.set(userId, userFavorites);
    
    logger.info(`取消点赞内容`, {
      contentId,
      userId,
      newLikeCount: content.likeCount
    });
    
    return true;
  }
  
  /**
   * 分享内容
   * @param contentId 内容ID
   * @returns 是否成功
   */
  public async shareContent(contentId: string): Promise<boolean> {
    if (!this.contentsStore.has(contentId)) {
      logger.warn(`分享失败，内容不存在: ${contentId}`);
      return false;
    }
    
    // 更新内容分享数
    const content = this.contentsStore.get(contentId)!;
    content.shareCount += 1;
    this.contentsStore.set(contentId, content);
    
    logger.info(`分享内容`, {
      contentId,
      newShareCount: content.shareCount
    });
    
    return true;
  }
  
  /**
   * 获取热门话题
   * @param limit 数量限制
   * @returns 话题列表
   */
  public async getHotTopics(limit: number = 10): Promise<Topic[]> {
    // 获取所有活动话题
    const topics = Array.from(this.topicsStore.values())
      .filter(topic => topic.status === 'active');
    
    // 按热度排序
    topics.sort((a, b) => b.trendingScore - a.trendingScore);
    
    // 限制数量
    const hotTopics = topics.slice(0, limit);
    
    logger.info(`获取热门话题`, {
      limit,
      count: hotTopics.length
    });
    
    return hotTopics;
  }
  
  /**
   * 获取话题详情
   * @param id 话题ID
   * @returns 话题详情
   */
  public async getTopicById(id: string): Promise<Topic | null> {
    if (!this.topicsStore.has(id)) {
      logger.warn(`获取失败，话题不存在: ${id}`);
      return null;
    }
    
    const topic = this.topicsStore.get(id)!;
    
    logger.info(`获取话题详情`, {
      id,
      title: topic.title
    });
    
    return topic;
  }
  
  /**
   * 获取话题相关内容
   * @param topicId 话题ID
   * @param page 页码
   * @param limit 每页数量
   * @returns 内容列表和分页信息
   */
  public async getTopicContents(
    topicId: string,
    page: number = 1,
    limit: number = 10
  ): Promise<{
    contents: Content[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    if (!this.topicsStore.has(topicId)) {
      logger.warn(`获取失败，话题不存在: ${topicId}`);
      return {
        contents: [],
        total: 0,
        page,
        limit,
        totalPages: 0
      };
    }
    
    const topic = this.topicsStore.get(topicId)!;
    
    // 获取所有已发布的内容
    let contents = Array.from(this.contentsStore.values())
      .filter(content => 
        content.status === 'published' && 
        content.tags.some(tag => topic.tags.includes(tag))
      );
    
    // 计算分页信息
    const total = contents.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    
    // 按发布时间排序
    contents.sort((a, b) => 
      (b.publishedAt?.getTime() || 0) - (a.publishedAt?.getTime() || 0)
    );
    
    // 分页
    const paginatedContents = contents.slice(offset, offset + limit);
    
    logger.info(`获取话题相关内容`, {
      topicId,
      topicTitle: topic.title,
      page,
      limit,
      total
    });
    
    return {
      contents: paginatedContents,
      total,
      page,
      limit,
      totalPages
    };
  }
  
  /**
   * 关注话题
   * @param topicId 话题ID
   * @returns 是否成功
   */
  public async followTopic(topicId: string): Promise<boolean> {
    if (!this.topicsStore.has(topicId)) {
      logger.warn(`关注失败，话题不存在: ${topicId}`);
      return false;
    }
    
    // 更新话题关注人数
    const topic = this.topicsStore.get(topicId)!;
    topic.followerCount += 1;
    this.topicsStore.set(topicId, topic);
    
    logger.info(`关注话题`, {
      topicId,
      topicTitle: topic.title,
      newFollowerCount: topic.followerCount
    });
    
    return true;
  }
  
  /**
   * 获取精选内容
   * @param limit 数量限制
   * @returns 内容列表
   */
  public async getFeaturedContents(limit: number = 6): Promise<Content[]> {
    // 获取所有精选内容
    const featured = Array.from(this.contentsStore.values())
      .filter(content => 
        content.status === 'published' && 
        content.isFeatured
      );
    
    // 按发布时间排序
    featured.sort((a, b) => 
      (b.publishedAt?.getTime() || 0) - (a.publishedAt?.getTime() || 0)
    );
    
    // 限制数量
    const featuredContents = featured.slice(0, limit);
    
    logger.info(`获取精选内容`, {
      limit,
      count: featuredContents.length
    });
    
    return featuredContents;
  }
  
  /**
   * 搜索内容
   * @param keyword 关键词
   * @param type 内容类型
   * @param page 页码
   * @param limit 每页数量
   * @returns 内容列表和分页信息
   */
  public async searchContents(
    keyword: string,
    type?: ContentType,
    page: number = 1,
    limit: number = 10
  ): Promise<{
    contents: Content[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const keywordLower = keyword.toLowerCase();
    
    // 获取所有已发布的内容
    let contents = Array.from(this.contentsStore.values())
      .filter(content => {
        if (content.status !== 'published') return false;
        
        // 类型过滤
        if (type && content.type !== type) return false;
        
        // 关键词搜索
        return (
          content.title.toLowerCase().includes(keywordLower) ||
          content.description.toLowerCase().includes(keywordLower) ||
          content.body.toLowerCase().includes(keywordLower) ||
          content.tags.some(tag => tag.toLowerCase().includes(keywordLower))
        );
      });
    
    // 计算分页信息
    const total = contents.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    
    // 按相关度排序（简单实现为标题匹配优先）
    contents.sort((a, b) => {
      const titleA = a.title.toLowerCase().includes(keywordLower);
      const titleB = b.title.toLowerCase().includes(keywordLower);
      
      if (titleA && !titleB) return -1;
      if (!titleA && titleB) return 1;
      
      return (b.publishedAt?.getTime() || 0) - (a.publishedAt?.getTime() || 0);
    });
    
    // 分页
    const paginatedContents = contents.slice(offset, offset + limit);
    
    logger.info(`搜索内容`, {
      keyword,
      type,
      page,
      limit,
      total
    });
    
    return {
      contents: paginatedContents,
      total,
      page,
      limit,
      totalPages
    };
  }
}

// 导出单例实例
const knowledgeDisseminationService = new KnowledgeDisseminationService();
export default knowledgeDisseminationService;