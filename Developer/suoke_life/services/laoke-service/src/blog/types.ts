/**
 * 博客相关类型定义
 */

// 博客文章状态
export enum PostStatus {
  DRAFT = 'draft',         // 草稿
  PENDING = 'pending',     // 待审核
  PUBLISHED = 'published', // 已发布
  ARCHIVED = 'archived'    // 已归档
}

// 评论状态
export enum CommentStatus {
  PENDING = 'pending',     // 待审核
  APPROVED = 'approved',   // 已批准
  SPAM = 'spam',           // 垃圾评论
  TRASHED = 'trashed'      // 已删除
}

// 博客文章
export interface BlogPost {
  id: string;              // 文章ID
  title: string;           // 标题
  content: string;         // 内容
  excerpt?: string;        // 摘要
  authorId: string;        // 作者ID
  authorName: string;      // 作者名称
  categoryId?: string;     // 分类ID
  categoryName?: string;   // 分类名称
  tags?: string[];         // 标签
  status: PostStatus;      // 状态
  featured: boolean;       // 是否推荐
  commentCount: number;    // 评论数
  viewCount: number;       // 阅读数
  likeCount: number;       // 点赞数
  shareCount: number;      // 分享数
  rating: number;          // 评分(1-5)
  ratingCount: number;     // 评分人数
  allowComments: boolean;  // 是否允许评论
  createdAt: Date;         // 创建时间
  updatedAt: Date;         // 更新时间
  publishedAt?: Date;      // 发布时间
  coverImage?: string;     // 封面图片
  seoTitle?: string;       // SEO标题
  seoDescription?: string; // SEO描述
  seoKeywords?: string[];  // SEO关键词
}

// 博客评论
export interface BlogComment {
  id: string;              // 评论ID
  postId: string;          // 文章ID
  parentId?: string;       // 父评论ID
  commenterName: string;   // 评论者名称
  commenterEmail?: string; // 评论者邮箱
  commenterAvatar?: string;// 评论者头像
  commenterUserId?: string;// 评论者用户ID
  content: string;         // 评论内容
  status: CommentStatus;   // 状态
  likeCount: number;       // 点赞数
  reportCount: number;     // 举报数
  isPinned: boolean;       // 是否置顶
  createdAt: Date;         // 创建时间
  updatedAt: Date;         // 更新时间
}

// 博客分类
export interface BlogCategory {
  id: string;              // 分类ID
  name: string;            // 分类名称
  slug: string;            // 分类别名
  description?: string;    // 分类描述
  parentId?: string;       // 父分类ID
  postCount: number;       // 文章数
  createdAt: Date;         // 创建时间
  updatedAt: Date;         // 更新时间
}

// 博客标签
export interface BlogTag {
  id: string;              // 标签ID
  name: string;            // 标签名称
  slug: string;            // 标签别名
  description?: string;    // 标签描述
  postCount: number;       // 文章数
  createdAt: Date;         // 创建时间
  updatedAt: Date;         // 更新时间
}

// 博客互动类型
export type BlogInteractionType = 'view' | 'like' | 'bookmark' | 'share' | 'rate';

// 博客互动记录
export interface BlogInteraction {
  userId: string;           // 用户ID
  postId: string;           // 文章ID
  type: BlogInteractionType;// 互动类型
  createdAt: Date;          // 创建时间
  userDevice?: string;      // 用户设备
  userIp?: string;          // 用户IP
  userAgent?: string;       // 用户代理
  referrer?: string;        // 来源
  sharePlatform?: string;   // 分享平台
  rating?: number;          // 评分(1-5)
  dwellTime?: number;       // 停留时间(秒)
  position?: number;        // 阅读位置(0-1)
}

// 博客分析数据
export interface BlogAnalytics {
  postId: string;            // 文章ID
  date: Date;                // 日期
  views: number;             // 浏览量
  uniqueVisitors: number;    // 独立访客数
  avgDwellTime: number;      // 平均停留时间
  likes: number;             // 点赞数
  comments: number;          // 评论数
  shares: number;            // 分享数
  bookmarks: number;         // 收藏数
  bounceRate: number;        // 跳出率
  conversionRate: number;    // 转化率
  trafficSources: Record<string, number>; // 流量来源
  deviceDistribution: Record<string, number>; // 设备分布
  completionRate: number;    // 阅读完成率
}

// 用户博客统计
export interface UserBlogStats {
  userId: string;           // 用户ID
  postCount: number;        // 文章数
  commentCount: number;     // 评论数
  totalViews: number;       // 总浏览量
  totalLikes: number;       // 总点赞数
  averageRating: number;    // 平均评分
  mostViewedPost?: string;  // 最受欢迎文章ID
}