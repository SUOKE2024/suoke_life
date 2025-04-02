/**
 * 知识传播模块类型定义
 */

/**
 * 知识内容类型枚举
 */
export enum ContentType {
  // 文章类型
  ARTICLE = 'article',
  // 课程类型
  COURSE = 'course',
  // 视频类型
  VIDEO = 'video',
  // 音频类型
  AUDIO = 'audio',
  // 问答类型
  QA = 'qa',
  // 图集类型
  GALLERY = 'gallery',
  // 资源类型
  RESOURCE = 'resource'
}

/**
 * 知识领域枚举
 */
export enum KnowledgeDomain {
  // 中医养生
  TCM = 'tcm',
  // 现代医学
  MODERN_MEDICINE = 'modern_medicine',
  // 食疗营养
  NUTRITION = 'nutrition',
  // 心理健康
  MENTAL_HEALTH = 'mental_health',
  // 运动健身
  FITNESS = 'fitness',
  // 环境健康
  ENVIRONMENTAL_HEALTH = 'environmental_health',
  // 健康科技
  HEALTH_TECH = 'health_tech',
  // 生活方式
  LIFESTYLE = 'lifestyle'
}

/**
 * 难度级别枚举
 */
export enum DifficultyLevel {
  // 入门级别
  BEGINNER = 'beginner',
  // 基础级别
  BASIC = 'basic',
  // 中级
  INTERMEDIATE = 'intermediate',
  // 高级
  ADVANCED = 'advanced',
  // 专家级别
  EXPERT = 'expert'
}

/**
 * 内容状态枚举
 */
export enum ContentStatus {
  // 草稿
  DRAFT = 'draft',
  // 审核中
  REVIEWING = 'reviewing',
  // 已发布
  PUBLISHED = 'published',
  // 已归档
  ARCHIVED = 'archived',
  // 已拒绝
  REJECTED = 'rejected'
}

/**
 * 内容格式枚举
 */
export enum ContentFormat {
  // 纯文本
  PLAIN_TEXT = 'plain_text',
  // Markdown
  MARKDOWN = 'markdown',
  // 富文本
  RICH_TEXT = 'rich_text',
  // HTML
  HTML = 'html'
}

/**
 * 知识内容基础接口
 */
export interface KnowledgeContent {
  // 内容ID
  id: string;
  // 标题
  title: string;
  // 内容类型
  type: ContentType;
  // 知识领域
  domain: KnowledgeDomain;
  // 难度级别
  difficulty: DifficultyLevel;
  // 内容状态
  status: ContentStatus;
  // 创建时间
  createdAt: Date;
  // 更新时间
  updatedAt: Date;
  // 作者ID
  authorId: string;
  // 标签
  tags: string[];
  // 简介
  summary: string;
  // 封面图URL
  coverImageUrl?: string;
  // 浏览次数
  viewCount: number;
  // 点赞次数
  likeCount: number;
  // 收藏次数
  favoriteCount: number;
  // 分享次数
  shareCount: number;
  // 评分(0-5)
  rating: number;
  // 评分人数
  ratingCount: number;
  // 元数据
  metadata: Record<string, any>;
}

/**
 * 文章内容接口
 */
export interface Article extends KnowledgeContent {
  // 文章正文
  content: string;
  // 内容格式
  format: ContentFormat;
  // 阅读时间(分钟)
  readingTime: number;
  // 引用来源
  references?: string[];
  // 相关文章ID
  relatedArticleIds?: string[];
}

/**
 * 课程内容接口
 */
export interface Course extends KnowledgeContent {
  // 课程描述
  description: string;
  // 课程目标
  objectives: string[];
  // 课程大纲
  syllabus: CourseSection[];
  // 课程时长(分钟)
  duration: number;
  // 预计完成时间(天)
  estimatedCompletion: number;
  // 先决条件课程ID
  prerequisites?: string[];
  // 讲师ID
  instructorId: string;
  // 课程价格
  price?: number;
  // 是否认证课程
  isCertified: boolean;
}

/**
 * 课程章节接口
 */
export interface CourseSection {
  // 章节ID
  id: string;
  // 章节标题
  title: string;
  // 章节简介
  description?: string;
  // 章节序号
  order: number;
  // 章节内容ID
  contentIds: string[];
  // 章节时长(分钟)
  duration: number;
}

/**
 * 视频内容接口
 */
export interface Video extends KnowledgeContent {
  // 视频URL
  videoUrl: string;
  // 视频时长(秒)
  duration: number;
  // 视频描述
  description: string;
  // 字幕URL
  subtitleUrl?: string;
  // 视频质量选项
  qualityOptions: VideoQuality[];
  // 视频缩略图URL
  thumbnailUrl: string;
  // 转录文本
  transcript?: string;
}

/**
 * 视频质量接口
 */
export interface VideoQuality {
  // 质量标签
  label: string;
  // 分辨率
  resolution: string;
  // 视频URL
  url: string;
  // 比特率
  bitrate: number;
}

/**
 * 音频内容接口
 */
export interface Audio extends KnowledgeContent {
  // 音频URL
  audioUrl: string;
  // 音频时长(秒)
  duration: number;
  // 音频描述
  description: string;
  // 转录文本
  transcript?: string;
  // 是否是播客
  isPodcast: boolean;
  // 播客系列ID
  podcastSeriesId?: string;
  // 播客集号
  episodeNumber?: number;
}

/**
 * 问答内容接口
 */
export interface QA extends KnowledgeContent {
  // 问题
  question: string;
  // 回答
  answer: string;
  // 内容格式
  format: ContentFormat;
  // 来源
  source?: string;
  // 相关问题ID
  relatedQuestionIds?: string[];
  // 问题类别
  category: string;
  // 有帮助计数
  helpfulCount: number;
}

/**
 * 图集内容接口
 */
export interface Gallery extends KnowledgeContent {
  // 图片项
  items: GalleryItem[];
  // 图集描述
  description: string;
}

/**
 * 图集项接口
 */
export interface GalleryItem {
  // 项ID
  id: string;
  // 图片URL
  imageUrl: string;
  // 标题
  title?: string;
  // 描述
  description?: string;
  // 顺序
  order: number;
  // 标签
  tags?: string[];
}

/**
 * 资源内容接口
 */
export interface Resource extends KnowledgeContent {
  // 资源URL
  resourceUrl: string;
  // 资源类型
  resourceType: string;
  // 资源大小(字节)
  size: number;
  // 文件格式
  fileFormat: string;
  // 资源描述
  description: string;
  // 下载计数
  downloadCount: number;
}

/**
 * 知识搜索参数接口
 */
export interface KnowledgeSearchParams {
  // 关键词
  keyword?: string;
  // 内容类型
  types?: ContentType[];
  // 知识领域
  domains?: KnowledgeDomain[];
  // 难度级别
  difficulties?: DifficultyLevel[];
  // 内容状态
  status?: ContentStatus[];
  // 标签
  tags?: string[];
  // 作者ID
  authorId?: string;
  // 排序字段
  sortBy?: 'createdAt' | 'updatedAt' | 'viewCount' | 'likeCount' | 'rating';
  // 排序方向
  sortDirection?: 'asc' | 'desc';
  // 页码
  page?: number;
  // 每页数量
  pageSize?: number;
}

/**
 * 知识推荐参数接口
 */
export interface KnowledgeRecommendParams {
  // 用户ID
  userId: string;
  // 内容类型
  types?: ContentType[];
  // 知识领域
  domains?: KnowledgeDomain[];
  // 难度级别
  difficulties?: DifficultyLevel[];
  // 排除的内容ID
  excludeIds?: string[];
  // 数量
  limit?: number;
  // 推荐策略
  strategy?: 'popular' | 'new' | 'personalized' | 'similar';
  // 相似内容ID(用于相似推荐)
  similarToId?: string;
}

/**
 * 知识集合接口
 */
export interface KnowledgeCollection {
  // 集合ID
  id: string;
  // 集合名称
  name: string;
  // 集合描述
  description: string;
  // 创建者ID
  creatorId: string;
  // 创建时间
  createdAt: Date;
  // 更新时间
  updatedAt: Date;
  // 内容ID列表
  contentIds: string[];
  // 是否公开
  isPublic: boolean;
  // 集合封面URL
  coverImageUrl?: string;
  // 标签
  tags?: string[];
  // 查看次数
  viewCount: number;
  // 关注者数量
  followerCount: number;
}