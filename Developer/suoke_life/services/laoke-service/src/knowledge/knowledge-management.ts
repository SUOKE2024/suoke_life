/**
 * 知识管理服务
 * 负责知识内容的增删改查和管理
 */
import { 
  KnowledgeContent, 
  ContentType, 
  KnowledgeDomain, 
  DifficultyLevel,
  ContentStatus,
  KnowledgeSearchParams,
  Article,
  Course,
  Video,
  Audio,
  QA,
  Gallery,
  Resource,
  KnowledgeCollection
} from './types';
import { logger } from '../utils/logger';

class KnowledgeManagement {
  // 模拟数据存储
  private contentStore: Map<string, KnowledgeContent> = new Map();
  private collectionsStore: Map<string, KnowledgeCollection> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('知识管理服务初始化');
  }
  
  /**
   * 创建知识内容
   * @param content 知识内容
   * @returns 创建的内容ID
   */
  public async createContent<T extends KnowledgeContent>(content: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
    const id = `content-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    const newContent = {
      ...content,
      id,
      createdAt: now,
      updatedAt: now,
      viewCount: 0,
      likeCount: 0,
      favoriteCount: 0,
      shareCount: 0,
      rating: 0,
      ratingCount: 0
    } as T;
    
    this.contentStore.set(id, newContent);
    
    logger.info(`创建知识内容: ${id}`, { 
      title: content.title, 
      type: content.type,
      domain: content.domain
    });
    
    return id;
  }
  
  /**
   * 更新知识内容
   * @param id 内容ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateContent<T extends KnowledgeContent>(
    id: string, 
    updates: Partial<Omit<T, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<boolean> {
    if (!this.contentStore.has(id)) {
      logger.warn(`更新失败，内容不存在: ${id}`);
      return false;
    }
    
    const content = this.contentStore.get(id) as T;
    
    const updatedContent = {
      ...content,
      ...updates,
      updatedAt: new Date()
    } as T;
    
    this.contentStore.set(id, updatedContent);
    
    logger.info(`更新知识内容: ${id}`);
    
    return true;
  }
  
  /**
   * 获取知识内容
   * @param id 内容ID
   * @returns 知识内容或null
   */
  public async getContent<T extends KnowledgeContent>(id: string): Promise<T | null> {
    if (!this.contentStore.has(id)) {
      logger.warn(`获取失败，内容不存在: ${id}`);
      return null;
    }
    
    const content = this.contentStore.get(id) as T;
    
    // 更新浏览次数
    this.updateContent(id, { viewCount: content.viewCount + 1 });
    
    logger.info(`获取知识内容: ${id}`);
    
    return content;
  }
  
  /**
   * 删除知识内容
   * @param id 内容ID
   * @returns 是否删除成功
   */
  public async deleteContent(id: string): Promise<boolean> {
    if (!this.contentStore.has(id)) {
      logger.warn(`删除失败，内容不存在: ${id}`);
      return false;
    }
    
    this.contentStore.delete(id);
    
    // 同时从所有集合中移除该内容
    for (const [collectionId, collection] of this.collectionsStore.entries()) {
      if (collection.contentIds.includes(id)) {
        const updatedCollection = {
          ...collection,
          contentIds: collection.contentIds.filter(contentId => contentId !== id),
          updatedAt: new Date()
        };
        this.collectionsStore.set(collectionId, updatedCollection);
      }
    }
    
    logger.info(`删除知识内容: ${id}`);
    
    return true;
  }
  
  /**
   * 归档知识内容
   * @param id 内容ID
   * @returns 是否归档成功
   */
  public async archiveContent(id: string): Promise<boolean> {
    if (!this.contentStore.has(id)) {
      logger.warn(`归档失败，内容不存在: ${id}`);
      return false;
    }
    
    return await this.updateContent(id, { status: ContentStatus.ARCHIVED });
  }
  
  /**
   * 发布知识内容
   * @param id 内容ID
   * @returns 是否发布成功
   */
  public async publishContent(id: string): Promise<boolean> {
    if (!this.contentStore.has(id)) {
      logger.warn(`发布失败，内容不存在: ${id}`);
      return false;
    }
    
    return await this.updateContent(id, { status: ContentStatus.PUBLISHED });
  }
  
  /**
   * 搜索知识内容
   * @param params 搜索参数
   * @returns 搜索结果
   */
  public async searchContent(params: KnowledgeSearchParams): Promise<{
    items: KnowledgeContent[];
    total: number;
    page: number;
    pageSize: number;
  }> {
    logger.info('搜索知识内容', params);
    
    const {
      keyword,
      types,
      domains,
      difficulties,
      status,
      tags,
      authorId,
      sortBy = 'createdAt',
      sortDirection = 'desc',
      page = 1,
      pageSize = 20
    } = params;
    
    // 过滤内容
    let filteredContents = Array.from(this.contentStore.values());
    
    // 关键词过滤
    if (keyword) {
      const lowerKeyword = keyword.toLowerCase();
      filteredContents = filteredContents.filter(content => 
        content.title.toLowerCase().includes(lowerKeyword) || 
        content.summary.toLowerCase().includes(lowerKeyword) ||
        content.tags.some(tag => tag.toLowerCase().includes(lowerKeyword))
      );
    }
    
    // 类型过滤
    if (types && types.length > 0) {
      filteredContents = filteredContents.filter(content => 
        types.includes(content.type)
      );
    }
    
    // 领域过滤
    if (domains && domains.length > 0) {
      filteredContents = filteredContents.filter(content => 
        domains.includes(content.domain)
      );
    }
    
    // 难度过滤
    if (difficulties && difficulties.length > 0) {
      filteredContents = filteredContents.filter(content => 
        difficulties.includes(content.difficulty)
      );
    }
    
    // 状态过滤
    if (status && status.length > 0) {
      filteredContents = filteredContents.filter(content => 
        status.includes(content.status)
      );
    }
    
    // 标签过滤
    if (tags && tags.length > 0) {
      filteredContents = filteredContents.filter(content => 
        tags.some(tag => content.tags.includes(tag))
      );
    }
    
    // 作者过滤
    if (authorId) {
      filteredContents = filteredContents.filter(content => 
        content.authorId === authorId
      );
    }
    
    // 排序
    filteredContents.sort((a, b) => {
      let valueA: any = a[sortBy as keyof KnowledgeContent];
      let valueB: any = b[sortBy as keyof KnowledgeContent];
      
      // 日期类型特殊处理
      if (valueA instanceof Date && valueB instanceof Date) {
        valueA = valueA.getTime();
        valueB = valueB.getTime();
      }
      
      if (sortDirection === 'asc') {
        return valueA > valueB ? 1 : -1;
      } else {
        return valueA < valueB ? 1 : -1;
      }
    });
    
    // 分页
    const total = filteredContents.length;
    const offset = (page - 1) * pageSize;
    const items = filteredContents.slice(offset, offset + pageSize);
    
    return {
      items,
      total,
      page,
      pageSize
    };
  }
  
  /**
   * 创建知识集合
   * @param collection 知识集合
   * @returns 创建的集合ID
   */
  public async createCollection(
    collection: Omit<KnowledgeCollection, 'id' | 'createdAt' | 'updatedAt' | 'viewCount' | 'followerCount'>
  ): Promise<string> {
    const id = `collection-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    const newCollection = {
      ...collection,
      id,
      createdAt: now,
      updatedAt: now,
      viewCount: 0,
      followerCount: 0
    };
    
    this.collectionsStore.set(id, newCollection);
    
    logger.info(`创建知识集合: ${id}`, { 
      name: collection.name,
      contentCount: collection.contentIds.length
    });
    
    return id;
  }
  
  /**
   * 更新知识集合
   * @param id 集合ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateCollection(
    id: string,
    updates: Partial<Omit<KnowledgeCollection, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<boolean> {
    if (!this.collectionsStore.has(id)) {
      logger.warn(`更新失败，集合不存在: ${id}`);
      return false;
    }
    
    const collection = this.collectionsStore.get(id)!;
    
    const updatedCollection = {
      ...collection,
      ...updates,
      updatedAt: new Date()
    };
    
    this.collectionsStore.set(id, updatedCollection);
    
    logger.info(`更新知识集合: ${id}`);
    
    return true;
  }
  
  /**
   * 获取知识集合
   * @param id 集合ID
   * @returns 知识集合或null
   */
  public async getCollection(id: string): Promise<KnowledgeCollection | null> {
    if (!this.collectionsStore.has(id)) {
      logger.warn(`获取失败，集合不存在: ${id}`);
      return null;
    }
    
    const collection = this.collectionsStore.get(id)!;
    
    // 更新浏览次数
    this.updateCollection(id, { viewCount: collection.viewCount + 1 });
    
    logger.info(`获取知识集合: ${id}`);
    
    return collection;
  }
  
  /**
   * 删除知识集合
   * @param id 集合ID
   * @returns 是否删除成功
   */
  public async deleteCollection(id: string): Promise<boolean> {
    if (!this.collectionsStore.has(id)) {
      logger.warn(`删除失败，集合不存在: ${id}`);
      return false;
    }
    
    this.collectionsStore.delete(id);
    
    logger.info(`删除知识集合: ${id}`);
    
    return true;
  }
  
  /**
   * 向集合中添加内容
   * @param collectionId 集合ID
   * @param contentId 内容ID
   * @returns 是否添加成功
   */
  public async addContentToCollection(collectionId: string, contentId: string): Promise<boolean> {
    if (!this.collectionsStore.has(collectionId)) {
      logger.warn(`添加失败，集合不存在: ${collectionId}`);
      return false;
    }
    
    if (!this.contentStore.has(contentId)) {
      logger.warn(`添加失败，内容不存在: ${contentId}`);
      return false;
    }
    
    const collection = this.collectionsStore.get(collectionId)!;
    
    // 如果内容已在集合中，不重复添加
    if (collection.contentIds.includes(contentId)) {
      return true;
    }
    
    const updatedCollection = {
      ...collection,
      contentIds: [...collection.contentIds, contentId],
      updatedAt: new Date()
    };
    
    this.collectionsStore.set(collectionId, updatedCollection);
    
    logger.info(`向集合添加内容`, {
      collectionId,
      contentId
    });
    
    return true;
  }
  
  /**
   * 从集合中移除内容
   * @param collectionId 集合ID
   * @param contentId 内容ID
   * @returns 是否移除成功
   */
  public async removeContentFromCollection(collectionId: string, contentId: string): Promise<boolean> {
    if (!this.collectionsStore.has(collectionId)) {
      logger.warn(`移除失败，集合不存在: ${collectionId}`);
      return false;
    }
    
    const collection = this.collectionsStore.get(collectionId)!;
    
    // 如果内容不在集合中，无需移除
    if (!collection.contentIds.includes(contentId)) {
      return true;
    }
    
    const updatedCollection = {
      ...collection,
      contentIds: collection.contentIds.filter(id => id !== contentId),
      updatedAt: new Date()
    };
    
    this.collectionsStore.set(collectionId, updatedCollection);
    
    logger.info(`从集合移除内容`, {
      collectionId,
      contentId
    });
    
    return true;
  }
  
  /**
   * 获取热门知识内容
   * @param limit 限制数量
   * @param domain 知识领域
   * @returns 热门内容列表
   */
  public async getHotContent(limit: number = 10, domain?: KnowledgeDomain): Promise<KnowledgeContent[]> {
    let contents = Array.from(this.contentStore.values())
      .filter(content => content.status === ContentStatus.PUBLISHED);
    
    // 按领域过滤
    if (domain) {
      contents = contents.filter(content => content.domain === domain);
    }
    
    // 按热度排序(根据浏览、点赞、收藏等)
    contents.sort((a, b) => {
      const scoreA = a.viewCount * 1 + a.likeCount * 2 + a.favoriteCount * 3;
      const scoreB = b.viewCount * 1 + b.likeCount * 2 + b.favoriteCount * 3;
      return scoreB - scoreA;
    });
    
    logger.info(`获取热门知识内容`, {
      limit,
      domain
    });
    
    return contents.slice(0, limit);
  }
  
  /**
   * 获取推荐知识内容
   * @param userId 用户ID
   * @param limit 限制数量
   * @returns 推荐内容列表
   */
  public async getRecommendedContent(userId: string, limit: number = 10): Promise<KnowledgeContent[]> {
    // 这里应该实现基于用户兴趣和行为的推荐逻辑
    // 目前简单返回热门内容作为示例
    
    logger.info(`获取推荐知识内容`, {
      userId,
      limit
    });
    
    return this.getHotContent(limit);
  }
  
  /**
   * 获取相似知识内容
   * @param contentId 内容ID
   * @param limit 限制数量
   * @returns 相似内容列表
   */
  public async getSimilarContent(contentId: string, limit: number = 5): Promise<KnowledgeContent[]> {
    if (!this.contentStore.has(contentId)) {
      logger.warn(`获取相似内容失败，内容不存在: ${contentId}`);
      return [];
    }
    
    const content = this.contentStore.get(contentId)!;
    
    // 按相同领域和标签查找相似内容
    let similarContents = Array.from(this.contentStore.values())
      .filter(c => 
        c.id !== contentId && 
        c.status === ContentStatus.PUBLISHED &&
        c.domain === content.domain
      );
    
    // 计算标签匹配度
    similarContents.forEach(c => {
      const commonTags = c.tags.filter(tag => content.tags.includes(tag));
      (c as any).similarity = commonTags.length;
    });
    
    // 按相似度排序
    similarContents.sort((a, b) => {
      return (b as any).similarity - (a as any).similarity;
    });
    
    logger.info(`获取相似知识内容`, {
      contentId,
      limit
    });
    
    return similarContents.slice(0, limit);
  }
  
  /**
   * 获取用户知识集合
   * @param userId 用户ID
   * @returns 集合列表
   */
  public async getUserCollections(userId: string): Promise<KnowledgeCollection[]> {
    const collections = Array.from(this.collectionsStore.values())
      .filter(collection => 
        collection.creatorId === userId || 
        (collection.isPublic && collection.followerCount > 0)
      );
    
    logger.info(`获取用户知识集合`, {
      userId,
      count: collections.length
    });
    
    return collections;
  }
}

export default new KnowledgeManagement();