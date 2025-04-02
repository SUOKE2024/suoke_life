/**
 * 博客管理服务
 * 负责博客文章、分类、标签的增删改查
 */
import { 
  BlogPost, 
  BlogCategory, 
  BlogTag, 
  PostStatus,
  UserBlogStats
} from './types';
import { logger } from '../utils/logger';

class BlogManagementService {
  // 模拟数据存储
  private postsStore: Map<string, BlogPost> = new Map();
  private categoriesStore: Map<string, BlogCategory> = new Map();
  private tagsStore: Map<string, BlogTag> = new Map();
  private userStatsStore: Map<string, UserBlogStats> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('博客管理服务初始化');
    
    // 初始化默认分类
    this.initDefaultCategories();
  }
  
  /**
   * 初始化默认分类
   */
  private initDefaultCategories(): void {
    const defaultCategories: Omit<BlogCategory, 'id' | 'createdAt' | 'updatedAt' | 'postCount'>[] = [
      {
        name: '健康养生',
        slug: 'health',
        description: '健康生活方式、养生保健、疾病预防等相关内容'
      },
      {
        name: '中医知识',
        slug: 'tcm',
        description: '中医理论、体质辨识、针灸推拿、中药应用等相关内容'
      },
      {
        name: '饮食营养',
        slug: 'nutrition',
        description: '食疗养生、健康饮食、营养搭配等相关内容'
      },
      {
        name: '科技创新',
        slug: 'tech',
        description: '人工智能、科技创新、数字健康等相关内容'
      },
      {
        name: '生活方式',
        slug: 'lifestyle',
        description: '生活方式、环保理念、绿色出行等相关内容'
      }
    ];
    
    // 创建默认分类
    defaultCategories.forEach(category => {
      const now = new Date();
      const id = `category-${category.slug}`;
      
      this.categoriesStore.set(id, {
        ...category,
        id,
        postCount: 0,
        createdAt: now,
        updatedAt: now
      });
      
      logger.info(`创建默认分类: ${category.name}`);
    });
  }
  
  /**
   * 创建博客文章
   * @param post 文章数据（不含id、创建时间等）
   * @returns 创建的文章ID
   */
  public async createPost(
    post: Omit<BlogPost, 'id' | 'createdAt' | 'updatedAt' | 'commentCount' | 'viewCount' | 'likeCount' | 'shareCount' | 'rating' | 'ratingCount'>
  ): Promise<string> {
    // 验证必填字段
    if (!post.title || !post.content || !post.authorId || !post.authorName) {
      throw new Error('文章标题、内容、作者ID和作者名称为必填项');
    }
    
    // 如果提供了分类ID，验证分类是否存在
    if (post.categoryId && !this.categoriesStore.has(post.categoryId)) {
      throw new Error(`分类不存在: ${post.categoryId}`);
    }
    
    // 生成文章ID
    const id = `post-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    // 设置文章发布时间
    let publishedAt: Date | undefined;
    if (post.status === PostStatus.PUBLISHED) {
      publishedAt = now;
    }
    
    // 创建新文章
    const newPost: BlogPost = {
      ...post,
      id,
      createdAt: now,
      updatedAt: now,
      publishedAt,
      commentCount: 0,
      viewCount: 0,
      likeCount: 0,
      shareCount: 0,
      rating: 0,
      ratingCount: 0
    };
    
    // 保存文章
    this.postsStore.set(id, newPost);
    
    // 如果文章有分类，更新分类的文章计数
    if (newPost.categoryId) {
      const category = this.categoriesStore.get(newPost.categoryId);
      if (category) {
        category.postCount += 1;
        this.categoriesStore.set(newPost.categoryId, category);
      }
    }
    
    // 如果文章有标签，更新或创建标签
    if (newPost.tags && newPost.tags.length > 0) {
      await this.updateTagsForPost(newPost.tags);
    }
    
    // 更新用户的博客统计
    await this.updateUserBlogStats(newPost.authorId);
    
    logger.info(`创建博客文章: ${id}`, {
      title: newPost.title,
      authorId: newPost.authorId,
      status: newPost.status
    });
    
    return id;
  }
  
  /**
   * 更新博客文章
   * @param id 文章ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updatePost(
    id: string,
    updates: Partial<BlogPost>
  ): Promise<boolean> {
    if (!this.postsStore.has(id)) {
      logger.warn(`更新失败，文章不存在: ${id}`);
      return false;
    }
    
    const post = this.postsStore.get(id)!;
    const oldCategoryId = post.categoryId;
    const oldTags = post.tags || [];
    
    // 如果要更新分类，验证新分类是否存在
    if (updates.categoryId && updates.categoryId !== oldCategoryId) {
      if (!this.categoriesStore.has(updates.categoryId)) {
        throw new Error(`分类不存在: ${updates.categoryId}`);
      }
    }
    
    // 如果状态从非发布变为发布，设置发布时间
    if (
      updates.status === PostStatus.PUBLISHED &&
      post.status !== PostStatus.PUBLISHED
    ) {
      updates.publishedAt = new Date();
    }
    
    // 更新文章
    const updatedPost: BlogPost = {
      ...post,
      ...updates,
      updatedAt: new Date()
    };
    
    // 保存更新后的文章
    this.postsStore.set(id, updatedPost);
    
    // 如果分类发生变化，更新分类的文章计数
    if (updates.categoryId && updates.categoryId !== oldCategoryId) {
      // 减少旧分类的文章计数
      if (oldCategoryId && this.categoriesStore.has(oldCategoryId)) {
        const oldCategory = this.categoriesStore.get(oldCategoryId)!;
        oldCategory.postCount = Math.max(0, oldCategory.postCount - 1);
        this.categoriesStore.set(oldCategoryId, oldCategory);
      }
      
      // 增加新分类的文章计数
      if (this.categoriesStore.has(updates.categoryId)) {
        const newCategory = this.categoriesStore.get(updates.categoryId)!;
        newCategory.postCount += 1;
        this.categoriesStore.set(updates.categoryId, newCategory);
      }
    }
    
    // 如果标签发生变化，更新标签
    if (updates.tags) {
      const newTags = updates.tags || [];
      
      // 删除的标签
      const removedTags = oldTags.filter(tag => !newTags.includes(tag));
      if (removedTags.length > 0) {
        await this.removeTagsFromPost(removedTags);
      }
      
      // 新增的标签
      const addedTags = newTags.filter(tag => !oldTags.includes(tag));
      if (addedTags.length > 0) {
        await this.updateTagsForPost(addedTags);
      }
    }
    
    logger.info(`更新博客文章: ${id}`, {
      title: updatedPost.title,
      status: updatedPost.status
    });
    
    return true;
  }
  
  /**
   * 删除博客文章
   * @param id 文章ID
   * @returns 是否删除成功
   */
  public async deletePost(id: string): Promise<boolean> {
    if (!this.postsStore.has(id)) {
      logger.warn(`删除失败，文章不存在: ${id}`);
      return false;
    }
    
    const post = this.postsStore.get(id)!;
    
    // 减少分类的文章计数
    if (post.categoryId && this.categoriesStore.has(post.categoryId)) {
      const category = this.categoriesStore.get(post.categoryId)!;
      category.postCount = Math.max(0, category.postCount - 1);
      this.categoriesStore.set(post.categoryId, category);
    }
    
    // 减少标签的文章计数
    if (post.tags && post.tags.length > 0) {
      await this.removeTagsFromPost(post.tags);
    }
    
    // 更新用户的博客统计
    await this.updateUserBlogStats(post.authorId, true);
    
    // 删除文章
    this.postsStore.delete(id);
    
    logger.info(`删除博客文章: ${id}`, {
      title: post.title,
      authorId: post.authorId
    });
    
    return true;
  }
  
  /**
   * 获取博客文章
   * @param id 文章ID
   * @param withComments 是否包含评论
   * @returns 文章或null
   */
  public async getPost(
    id: string,
    withComments: boolean = false
  ): Promise<BlogPost | null> {
    if (!this.postsStore.has(id)) {
      logger.warn(`获取失败，文章不存在: ${id}`);
      return null;
    }
    
    const post = this.postsStore.get(id)!;
    
    // 如果请求包含评论，可以在这里从评论服务获取评论数据
    // 由于我们已经实现了博客互动服务，实际应用中应该从那里获取评论
    
    logger.info(`获取博客文章: ${id}`, {
      title: post.title,
      withComments
    });
    
    return post;
  }
  
  /**
   * 获取博客文章列表
   * @param authorId 作者ID过滤
   * @param categoryId 分类ID过滤
   * @param tag 标签过滤
   * @param status 状态过滤
   * @param page 页码
   * @param limit 每页数量
   * @returns 文章列表和总数
   */
  public async getPosts(
    authorId?: string,
    categoryId?: string,
    tag?: string,
    status?: string,
    page: number = 1,
    limit: number = 10
  ): Promise<{
    posts: BlogPost[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    let posts = Array.from(this.postsStore.values());
    
    // 作者过滤
    if (authorId) {
      posts = posts.filter(post => post.authorId === authorId);
    }
    
    // 分类过滤
    if (categoryId) {
      posts = posts.filter(post => post.categoryId === categoryId);
    }
    
    // 标签过滤
    if (tag) {
      posts = posts.filter(post => post.tags && post.tags.includes(tag));
    }
    
    // 状态过滤
    if (status) {
      posts = posts.filter(post => post.status === status);
    }
    
    // 默认排序：置顶的在前，然后按创建时间倒序
    posts.sort((a, b) => {
      if (a.featured && !b.featured) return -1;
      if (!a.featured && b.featured) return 1;
      return b.createdAt.getTime() - a.createdAt.getTime();
    });
    
    // 计算分页信息
    const total = posts.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    
    // 分页
    const paginatedPosts = posts.slice(offset, offset + limit);
    
    logger.info(`获取博客文章列表`, {
      authorId,
      categoryId,
      tag,
      status,
      page,
      limit,
      total
    });
    
    return {
      posts: paginatedPosts,
      total,
      page,
      limit,
      totalPages
    };
  }
  
  /**
   * 创建博客分类
   * @param category 分类数据
   * @returns 创建的分类ID
   */
  public async createCategory(
    category: Omit<BlogCategory, 'id' | 'createdAt' | 'updatedAt' | 'postCount'>
  ): Promise<string> {
    // 验证必填字段
    if (!category.name || !category.slug) {
      throw new Error('分类名称和别名为必填项');
    }
    
    // 检查别名是否已存在
    const existingCategory = Array.from(this.categoriesStore.values())
      .find(c => c.slug === category.slug);
    
    if (existingCategory) {
      throw new Error(`分类别名已存在: ${category.slug}`);
    }
    
    // 如果提供了父分类ID，验证父分类是否存在
    if (category.parentId && !this.categoriesStore.has(category.parentId)) {
      throw new Error(`父分类不存在: ${category.parentId}`);
    }
    
    // 生成分类ID
    const id = `category-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    // 创建新分类
    const newCategory: BlogCategory = {
      ...category,
      id,
      postCount: 0,
      createdAt: now,
      updatedAt: now
    };
    
    // 保存分类
    this.categoriesStore.set(id, newCategory);
    
    logger.info(`创建博客分类: ${id}`, {
      name: newCategory.name,
      slug: newCategory.slug
    });
    
    return id;
  }
  
  /**
   * 更新博客分类
   * @param id 分类ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateCategory(
    id: string,
    updates: Partial<Omit<BlogCategory, 'id' | 'createdAt' | 'updatedAt' | 'postCount'>>
  ): Promise<boolean> {
    if (!this.categoriesStore.has(id)) {
      logger.warn(`更新失败，分类不存在: ${id}`);
      return false;
    }
    
    const category = this.categoriesStore.get(id)!;
    
    // 如果要更新别名，检查别名是否已存在
    if (updates.slug && updates.slug !== category.slug) {
      const existingCategory = Array.from(this.categoriesStore.values())
        .find(c => c.slug === updates.slug && c.id !== id);
      
      if (existingCategory) {
        throw new Error(`分类别名已存在: ${updates.slug}`);
      }
    }
    
    // 如果要更新父分类，验证父分类是否存在
    if (updates.parentId && updates.parentId !== category.parentId) {
      if (!this.categoriesStore.has(updates.parentId)) {
        throw new Error(`父分类不存在: ${updates.parentId}`);
      }
      
      // 检查循环引用
      if (updates.parentId === id) {
        throw new Error('分类不能将自己设为父分类');
      }
    }
    
    // 更新分类
    const updatedCategory: BlogCategory = {
      ...category,
      ...updates,
      updatedAt: new Date()
    };
    
    // 保存更新后的分类
    this.categoriesStore.set(id, updatedCategory);
    
    logger.info(`更新博客分类: ${id}`, {
      name: updatedCategory.name,
      slug: updatedCategory.slug
    });
    
    return true;
  }
  
  /**
   * 删除博客分类
   * @param id 分类ID
   * @param reassignTo 将该分类下的文章重新分配到的分类ID
   * @returns 是否删除成功
   */
  public async deleteCategory(
    id: string,
    reassignTo?: string
  ): Promise<boolean> {
    if (!this.categoriesStore.has(id)) {
      logger.warn(`删除失败，分类不存在: ${id}`);
      return false;
    }
    
    const category = this.categoriesStore.get(id)!;
    
    // 检查是否有子分类
    const hasChildren = Array.from(this.categoriesStore.values())
      .some(c => c.parentId === id);
    
    if (hasChildren) {
      throw new Error('无法删除有子分类的分类');
    }
    
    // 检查是否有文章使用此分类
    if (category.postCount > 0) {
      // 如果提供了重新分配的分类，将文章重新分配
      if (reassignTo) {
        if (!this.categoriesStore.has(reassignTo)) {
          throw new Error(`重新分配的分类不存在: ${reassignTo}`);
        }
        
        // 找到使用此分类的所有文章
        const postsWithCategory = Array.from(this.postsStore.values())
          .filter(post => post.categoryId === id);
        
        // 更新文章的分类
        for (const post of postsWithCategory) {
          await this.updatePost(post.id, {
            categoryId: reassignTo,
            categoryName: this.categoriesStore.get(reassignTo)!.name
          });
        }
      } else {
        throw new Error('无法删除有文章的分类，请提供重新分配的分类ID');
      }
    }
    
    // 删除分类
    this.categoriesStore.delete(id);
    
    logger.info(`删除博客分类: ${id}`, {
      name: category.name,
      reassignTo
    });
    
    return true;
  }
  
  /**
   * 获取博客分类
   * @param id 分类ID
   * @returns 分类或null
   */
  public async getCategory(id: string): Promise<BlogCategory | null> {
    if (!this.categoriesStore.has(id)) {
      logger.warn(`获取失败，分类不存在: ${id}`);
      return null;
    }
    
    const category = this.categoriesStore.get(id)!;
    
    logger.info(`获取博客分类: ${id}`, {
      name: category.name
    });
    
    return category;
  }
  
  /**
   * 获取博客分类列表
   * @param parentId 父分类ID
   * @returns 分类列表
   */
  public async getCategories(
    parentId?: string
  ): Promise<BlogCategory[]> {
    let categories = Array.from(this.categoriesStore.values());
    
    // 父分类过滤
    if (parentId !== undefined) {
      categories = categories.filter(
        category => category.parentId === parentId
      );
    }
    
    // 按名称排序
    categories.sort((a, b) => a.name.localeCompare(b.name));
    
    logger.info(`获取博客分类列表`, {
      parentId,
      count: categories.length
    });
    
    return categories;
  }
  
  /**
   * 获取博客标签列表
   * @param limit 数量限制
   * @returns 标签列表
   */
  public async getTags(limit?: number): Promise<BlogTag[]> {
    let tags = Array.from(this.tagsStore.values());
    
    // 按文章数量排序
    tags.sort((a, b) => b.postCount - a.postCount);
    
    // 如果有数量限制
    if (limit) {
      tags = tags.slice(0, limit);
    }
    
    logger.info(`获取博客标签列表`, {
      limit,
      count: tags.length
    });
    
    return tags;
  }
  
  /**
   * 获取用户博客统计
   * @param userId 用户ID
   * @returns 用户统计数据
   */
  public async getUserBlogStats(userId: string): Promise<UserBlogStats | null> {
    if (!this.userStatsStore.has(userId)) {
      logger.warn(`获取失败，用户博客统计不存在: ${userId}`);
      return null;
    }
    
    const stats = this.userStatsStore.get(userId)!;
    
    logger.info(`获取用户博客统计: ${userId}`);
    
    return stats;
  }
  
  /**
   * 为文章更新标签
   * @param tags 标签列表
   */
  private async updateTagsForPost(tags: string[]): Promise<void> {
    for (const tagName of tags) {
      // 规范化标签名
      const normalizedName = tagName.trim();
      if (!normalizedName) continue;
      
      // 生成标签别名
      const slug = normalizedName
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]/g, '');
      
      const tagId = `tag-${slug}`;
      
      // 检查标签是否已存在
      if (this.tagsStore.has(tagId)) {
        // 更新现有标签
        const tag = this.tagsStore.get(tagId)!;
        tag.postCount += 1;
        this.tagsStore.set(tagId, tag);
      } else {
        // 创建新标签
        const now = new Date();
        const newTag: BlogTag = {
          id: tagId,
          name: normalizedName,
          slug,
          postCount: 1,
          createdAt: now,
          updatedAt: now
        };
        
        this.tagsStore.set(tagId, newTag);
      }
    }
  }
  
  /**
   * 从文章移除标签
   * @param tags 标签列表
   */
  private async removeTagsFromPost(tags: string[]): Promise<void> {
    for (const tagName of tags) {
      // 规范化标签名
      const normalizedName = tagName.trim();
      if (!normalizedName) continue;
      
      // 生成标签别名
      const slug = normalizedName
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]/g, '');
      
      const tagId = `tag-${slug}`;
      
      // 检查标签是否已存在
      if (this.tagsStore.has(tagId)) {
        // 更新标签的文章计数
        const tag = this.tagsStore.get(tagId)!;
        tag.postCount = Math.max(0, tag.postCount - 1);
        
        // 如果标签没有关联文章，可以选择删除它
        if (tag.postCount === 0) {
          this.tagsStore.delete(tagId);
        } else {
          this.tagsStore.set(tagId, tag);
        }
      }
    }
  }
  
  /**
   * 更新用户博客统计
   * @param userId 用户ID
   * @param isDelete 是否是删除操作
   */
  private async updateUserBlogStats(
    userId: string,
    isDelete: boolean = false
  ): Promise<void> {
    // 获取用户的所有文章
    const userPosts = Array.from(this.postsStore.values())
      .filter(post => post.authorId === userId);
    
    // 如果用户没有文章且不是删除操作，初始化统计
    if (userPosts.length === 0 && !isDelete) {
      const newStats: UserBlogStats = {
        userId,
        postCount: 0,
        commentCount: 0,
        totalViews: 0,
        totalLikes: 0,
        averageRating: 0
      };
      
      this.userStatsStore.set(userId, newStats);
      return;
    }
    
    // 如果用户没有文章且是删除操作，可能需要删除统计
    if (userPosts.length === 0 && isDelete) {
      this.userStatsStore.delete(userId);
      return;
    }
    
    // 计算统计数据
    const postCount = userPosts.length;
    const totalViews = userPosts.reduce((sum, post) => sum + post.viewCount, 0);
    const totalLikes = userPosts.reduce((sum, post) => sum + post.likeCount, 0);
    const commentCount = userPosts.reduce((sum, post) => sum + post.commentCount, 0);
    
    // 计算平均评分
    let averageRating = 0;
    const ratedPosts = userPosts.filter(post => post.ratingCount > 0);
    if (ratedPosts.length > 0) {
      const totalRatingPoints = ratedPosts.reduce(
        (sum, post) => sum + (post.rating * post.ratingCount),
        0
      );
      const totalRatings = ratedPosts.reduce(
        (sum, post) => sum + post.ratingCount,
        0
      );
      
      averageRating = totalRatingPoints / totalRatings;
    }
    
    // 找出浏览量最高的文章
    let mostViewedPost: string | undefined;
    if (userPosts.length > 0) {
      mostViewedPost = userPosts.sort((a, b) => 
        b.viewCount - a.viewCount
      )[0].id;
    }
    
    // 更新或创建用户统计
    const stats: UserBlogStats = {
      userId,
      postCount,
      commentCount,
      totalViews,
      totalLikes,
      averageRating,
      mostViewedPost
    };
    
    this.userStatsStore.set(userId, stats);
  }
}

// 导出单例实例
const blogManagement = new BlogManagementService();
export default blogManagement;