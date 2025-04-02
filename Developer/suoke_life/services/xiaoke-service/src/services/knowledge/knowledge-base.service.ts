/**
 * 知识库服务实现
 */
import axios from 'axios';
import { Logger } from '../../utils/logger';
import { 
  KnowledgeBaseService,
  KnowledgeSearchOptions,
  KnowledgeSearchResult,
  KnowledgeItem
} from './types';
import { CacheService } from '../../core/cache';
import config from '../../config';

/**
 * 知识库服务实现类
 */
export class KnowledgeBaseServiceImpl implements KnowledgeBaseService {
  private logger = new Logger('KnowledgeBaseService');
  private cacheService: CacheService;
  private apiEndpoint: string;
  private isInitialized = false;
  private cache = new Map<string, any>();
  
  /**
   * 缓存过期时间(毫秒)
   */
  private readonly CACHE_TTL = 30 * 60 * 1000; // 30分钟
  
  /**
   * 搜索缓存键前缀
   */
  private readonly SEARCH_CACHE_PREFIX = 'kb_search_';
  
  /**
   * 知识条目缓存键前缀
   */
  private readonly ITEM_CACHE_PREFIX = 'kb_item_';
  
  /**
   * 分类条目缓存键前缀
   */
  private readonly CATEGORY_CACHE_PREFIX = 'kb_category_';
  
  /**
   * 标签条目缓存键前缀
   */
  private readonly TAG_CACHE_PREFIX = 'kb_tag_';
  
  constructor() {
    this.cacheService = new CacheService();
    this.apiEndpoint = config.KNOWLEDGE_SERVICE_URL || 'http://localhost:3002/api/knowledge';
  }
  
  /**
   * 初始化服务
   */
  async initialize(): Promise<void> {
    this.logger.info('初始化知识库服务');
    try {
      // 验证API连接
      await axios.get(`${this.apiEndpoint}/health`);
      this.isInitialized = true;
      this.logger.info('知识库服务初始化完成');
    } catch (error) {
      this.logger.error('知识库服务初始化失败', error);
      // 设置重试逻辑
      setTimeout(() => this.initialize(), 10000); // 10秒后重试
    }
  }
  
  /**
   * 关闭服务
   */
  async shutdown(): Promise<void> {
    this.logger.info('关闭知识库服务');
    this.isInitialized = false;
    this.cache.clear();
  }
  
  /**
   * 检查服务状态
   */
  private checkServiceReady(): void {
    if (!this.isInitialized) {
      throw new Error('知识库服务未初始化');
    }
  }
  
  /**
   * 生成缓存键
   */
  private getCacheKey(prefix: string, key: string, params?: any): string {
    if (params) {
      return `${prefix}${key}_${JSON.stringify(params)}`;
    }
    return `${prefix}${key}`;
  }
  
  /**
   * 从缓存获取数据
   */
  private getFromCache<T>(key: string): T | null {
    const cachedItem = this.cache.get(key);
    if (cachedItem && cachedItem.expiry > Date.now()) {
      return cachedItem.data as T;
    }
    this.cache.delete(key);
    return null;
  }
  
  /**
   * 存入缓存
   */
  private setToCache<T>(key: string, data: T, ttl = this.CACHE_TTL): void {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttl
    });
  }
  
  /**
   * 搜索知识库
   */
  async search(query: string, options?: KnowledgeSearchOptions): Promise<KnowledgeSearchResult> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.SEARCH_CACHE_PREFIX, query, options);
    
    // 检查缓存
    const cachedResult = this.getFromCache<KnowledgeSearchResult>(cacheKey);
    if (cachedResult) {
      this.logger.debug(`使用缓存的搜索结果: ${query}`);
      return cachedResult;
    }
    
    try {
      this.logger.debug(`执行知识库搜索: ${query}`);
      const startTime = Date.now();
      
      const response = await axios.post(`${this.apiEndpoint}/search`, {
        query,
        options
      });
      
      const result: KnowledgeSearchResult = {
        ...response.data,
        timeTaken: Date.now() - startTime
      };
      
      // 保存到缓存
      this.setToCache(cacheKey, result);
      
      return result;
    } catch (error) {
      this.logger.error(`知识库搜索失败: ${query}`, error);
      throw new Error(`知识库搜索失败: ${(error as Error).message}`);
    }
  }
  
  /**
   * 获取知识条目
   */
  async getItem(id: string): Promise<KnowledgeItem> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.ITEM_CACHE_PREFIX, id);
    
    // 检查缓存
    const cachedItem = this.getFromCache<KnowledgeItem>(cacheKey);
    if (cachedItem) {
      this.logger.debug(`使用缓存的知识条目: ${id}`);
      return cachedItem;
    }
    
    try {
      this.logger.debug(`获取知识条目: ${id}`);
      
      const response = await axios.get(`${this.apiEndpoint}/items/${id}`);
      const item: KnowledgeItem = response.data;
      
      // 保存到缓存
      this.setToCache(cacheKey, item);
      
      return item;
    } catch (error) {
      this.logger.error(`获取知识条目失败: ${id}`, error);
      throw new Error(`获取知识条目失败: ${(error as Error).message}`);
    }
  }
  
  /**
   * 按分类获取知识条目
   */
  async getItemsByCategory(category: string, limit = 20): Promise<KnowledgeItem[]> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.CATEGORY_CACHE_PREFIX, category, { limit });
    
    // 检查缓存
    const cachedItems = this.getFromCache<KnowledgeItem[]>(cacheKey);
    if (cachedItems) {
      this.logger.debug(`使用缓存的分类条目: ${category}`);
      return cachedItems;
    }
    
    try {
      this.logger.debug(`获取分类条目: ${category}`);
      
      const response = await axios.get(`${this.apiEndpoint}/categories/${category}`, {
        params: { limit }
      });
      
      const items: KnowledgeItem[] = response.data;
      
      // 保存到缓存
      this.setToCache(cacheKey, items);
      
      return items;
    } catch (error) {
      this.logger.error(`获取分类条目失败: ${category}`, error);
      throw new Error(`获取分类条目失败: ${(error as Error).message}`);
    }
  }
  
  /**
   * 按标签获取知识条目
   */
  async getItemsByTag(tag: string, limit = 20): Promise<KnowledgeItem[]> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.TAG_CACHE_PREFIX, tag, { limit });
    
    // 检查缓存
    const cachedItems = this.getFromCache<KnowledgeItem[]>(cacheKey);
    if (cachedItems) {
      this.logger.debug(`使用缓存的标签条目: ${tag}`);
      return cachedItems;
    }
    
    try {
      this.logger.debug(`获取标签条目: ${tag}`);
      
      const response = await axios.get(`${this.apiEndpoint}/tags/${tag}`, {
        params: { limit }
      });
      
      const items: KnowledgeItem[] = response.data;
      
      // 保存到缓存
      this.setToCache(cacheKey, items);
      
      return items;
    } catch (error) {
      this.logger.error(`获取标签条目失败: ${tag}`, error);
      throw new Error(`获取标签条目失败: ${(error as Error).message}`);
    }
  }
}