/**
 * 知识整合服务实现
 */
import { Logger } from '../../utils/logger';
import { 
  KnowledgeIntegrationService,
  KnowledgeBaseService,
  KnowledgeGraphService,
  KnowledgeEnrichment,
  KnowledgeSearchOptions,
  KnowledgeSearchResult,
  KnowledgeItem,
  GraphNode
} from './types';
import { CacheService } from '../../core/cache';

/**
 * 知识整合服务实现类
 */
export class KnowledgeIntegrationServiceImpl implements KnowledgeIntegrationService {
  private logger = new Logger('KnowledgeIntegrationService');
  private cacheService: CacheService;
  private knowledgeBaseService: KnowledgeBaseService;
  private knowledgeGraphService: KnowledgeGraphService;
  private isInitialized = false;
  private cache = new Map<string, any>();
  
  /**
   * 缓存过期时间(毫秒)
   */
  private readonly CACHE_TTL = 2 * 60 * 60 * 1000; // 2小时
  
  /**
   * 知识增强缓存键前缀
   */
  private readonly ENRICHMENT_CACHE_PREFIX = 'enrich_';
  
  /**
   * 农产品健康知识搜索缓存键前缀
   */
  private readonly AG_HEALTH_SEARCH_PREFIX = 'ag_health_search_';
  
  /**
   * 产品健康知识缓存键前缀
   */
  private readonly PRODUCT_HEALTH_PREFIX = 'product_health_';
  
  /**
   * 节气农产品知识缓存键前缀
   */
  private readonly SOLAR_TERM_PREFIX = 'solar_term_';
  
  constructor(
    knowledgeBaseService: KnowledgeBaseService,
    knowledgeGraphService: KnowledgeGraphService
  ) {
    this.cacheService = new CacheService();
    this.knowledgeBaseService = knowledgeBaseService;
    this.knowledgeGraphService = knowledgeGraphService;
  }
  
  /**
   * 初始化服务
   */
  async initialize(): Promise<void> {
    this.logger.info('初始化知识整合服务');
    try {
      // 确保依赖服务已初始化
      if (!this.knowledgeBaseService || !this.knowledgeGraphService) {
        throw new Error('依赖服务未注入');
      }
      
      this.isInitialized = true;
      this.logger.info('知识整合服务初始化完成');
    } catch (error) {
      this.logger.error('知识整合服务初始化失败', error);
      // 设置重试逻辑
      setTimeout(() => this.initialize(), 5000); // 5秒后重试
    }
  }
  
  /**
   * 关闭服务
   */
  async shutdown(): Promise<void> {
    this.logger.info('关闭知识整合服务');
    this.isInitialized = false;
    this.cache.clear();
  }
  
  /**
   * 检查服务状态
   */
  private checkServiceReady(): void {
    if (!this.isInitialized) {
      throw new Error('知识整合服务未初始化');
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
   * 提取健康益处
   * @param concepts 关联概念节点
   * @param items 知识条目
   */
  private extractHealthBenefits(
    concepts: GraphNode[],
    items: KnowledgeItem[]
  ): string[] {
    // 从概念中找出所有健康益处
    const benefitsFromConcepts = concepts
      .filter(node => node.type === 'HealthBenefit' || node.type === 'NutritionalValue')
      .map(node => node.label);
    
    // 从知识条目中提取益处信息
    const benefitsFromItems = items
      .filter(item => 
        item.categories?.includes('健康益处') || 
        item.categories?.includes('营养价值') ||
        item.tags?.includes('益处') ||
        item.tags?.includes('功效')
      )
      .map(item => item.title)
      .filter(Boolean);
    
    // 合并并去重
    return [...new Set([...benefitsFromConcepts, ...benefitsFromItems])];
  }
  
  /**
   * 提取适宜体质信息
   * @param concepts 关联概念节点
   */
  private extractConstitutionFit(concepts: GraphNode[]): {
    suitable: string[];
    unsuitable: string[];
  } {
    // 找出所有体质相关概念
    const constitutionNodes = concepts.filter(
      node => node.type === 'Constitution' || node.type === 'ConstitutionFit'
    );
    
    const suitable: string[] = [];
    const unsuitable: string[] = [];
    
    // 分析体质适宜性
    constitutionNodes.forEach(node => {
      if (node.properties.fitType === 'suitable' || node.properties.fitType === '适宜') {
        suitable.push(node.label);
      } else if (node.properties.fitType === 'unsuitable' || node.properties.fitType === '不适宜') {
        unsuitable.push(node.label);
      }
    });
    
    return {
      suitable: [...new Set(suitable)],
      unsuitable: [...new Set(unsuitable)]
    };
  }
  
  /**
   * 提取节气和季节信息
   * @param concepts 关联概念节点
   */
  private extractSeasonalInfo(concepts: GraphNode[]): {
    solarTerms: string[];
    bestSeasons: string[];
  } {
    // 找出所有季节和节气相关概念
    const seasonalNodes = concepts.filter(
      node => node.type === 'SolarTerm' || node.type === 'Season'
    );
    
    const solarTerms: string[] = [];
    const bestSeasons: string[] = [];
    
    // 分析季节和节气信息
    seasonalNodes.forEach(node => {
      if (node.type === 'SolarTerm') {
        solarTerms.push(node.label);
      } else if (node.type === 'Season') {
        bestSeasons.push(node.label);
      }
    });
    
    return {
      solarTerms: [...new Set(solarTerms)],
      bestSeasons: [...new Set(bestSeasons)]
    };
  }
  
  /**
   * 产品知识增强
   */
  async enrichProductKnowledge(productId: string): Promise<KnowledgeEnrichment> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.ENRICHMENT_CACHE_PREFIX, productId);
    
    // 检查缓存
    const cachedEnrichment = this.getFromCache<KnowledgeEnrichment>(cacheKey);
    if (cachedEnrichment) {
      this.logger.debug(`使用缓存的产品知识增强: ${productId}`);
      return cachedEnrichment;
    }
    
    try {
      this.logger.debug(`执行产品知识增强: ${productId}`);
      
      // 首先获取产品基础信息
      const productQuery = `SELECT * FROM products WHERE id = '${productId}'`;
      const productResult = await this.knowledgeGraphService.query(productQuery);
      
      if (!productResult || productResult.length === 0) {
        throw new Error(`未找到产品信息: ${productId}`);
      }
      
      const productInfo = {
        id: productId,
        name: productResult[0].name,
        description: productResult[0].description
      };
      
      // 并行获取相关数据
      const [relatedConcepts, knowledgeItems] = await Promise.all([
        // 获取产品关联概念
        this.knowledgeGraphService.getProductConcepts(productId),
        
        // 获取产品相关知识条目
        this.knowledgeBaseService.search(productInfo.name, {
          limit: 15,
          useSemanticSearch: true,
          filters: {
            categories: ['农产品', '食品', '健康', '营养']
          }
        }).then(result => result.items)
      ]);
      
      // 提取健康益处
      const healthBenefits = this.extractHealthBenefits(relatedConcepts, knowledgeItems);
      
      // 提取体质适宜信息
      const constitutionFit = this.extractConstitutionFit(relatedConcepts);
      
      // 提取节气和季节信息
      const seasonalRelevance = this.extractSeasonalInfo(relatedConcepts);
      
      const enrichment: KnowledgeEnrichment = {
        productInfo,
        knowledgeItems,
        relatedConcepts,
        healthBenefits,
        constitutionFit,
        seasonalRelevance
      };
      
      // 保存到缓存
      this.setToCache(cacheKey, enrichment);
      
      return enrichment;
    } catch (error) {
      this.logger.error(`产品知识增强失败: ${productId}`, error);
      throw new Error(`产品知识增强失败: ${(error as Error).message}`);
    }
  }
  
  /**
   * 查询农产品与健康知识的关联
   */
  async searchAgricultureHealthKnowledge(
    query: string, 
    options?: KnowledgeSearchOptions
  ): Promise<KnowledgeSearchResult> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.AG_HEALTH_SEARCH_PREFIX, query, options);
    
    // 检查缓存
    const cachedResult = this.getFromCache<KnowledgeSearchResult>(cacheKey);
    if (cachedResult) {
      this.logger.debug(`使用缓存的农产品健康知识搜索: ${query}`);
      return cachedResult;
    }
    
    try {
      this.logger.debug(`执行农产品健康知识搜索: ${query}`);
      
      // 扩展搜索选项，确保搜索范围包含农产品和健康相关内容
      const searchOptions: KnowledgeSearchOptions = {
        ...options,
        useSemanticSearch: true,
        filters: {
          ...(options?.filters || {}),
          categories: [
            ...(options?.filters?.categories || []),
            '农产品',
            '食品',
            '健康',
            '营养'
          ]
        }
      };
      
      // 使用知识库服务进行搜索
      const searchResult = await this.knowledgeBaseService.search(query, searchOptions);
      
      // 如果搜索结果为空，尝试更宽泛的搜索
      if (searchResult.items.length === 0) {
        // 移除分类过滤器
        const broaderOptions: KnowledgeSearchOptions = {
          ...searchOptions,
          filters: {
            ...(searchOptions.filters || {}),
            categories: undefined
          }
        };
        
        return await this.knowledgeBaseService.search(query, broaderOptions);
      }
      
      // 保存到缓存
      this.setToCache(cacheKey, searchResult);
      
      return searchResult;
    } catch (error) {
      this.logger.error(`农产品健康知识搜索失败: ${query}`, error);
      throw new Error(`农产品健康知识搜索失败: ${(error as Error).message}`);
    }
  }
  
  /**
   * 获取产品相关健康知识
   */
  async getProductHealthKnowledge(productId: string): Promise<KnowledgeItem[]> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.PRODUCT_HEALTH_PREFIX, productId);
    
    // 检查缓存
    const cachedItems = this.getFromCache<KnowledgeItem[]>(cacheKey);
    if (cachedItems) {
      this.logger.debug(`使用缓存的产品健康知识: ${productId}`);
      return cachedItems;
    }
    
    try {
      this.logger.debug(`获取产品健康知识: ${productId}`);
      
      // 首先获取产品基础信息
      const productQuery = `SELECT * FROM products WHERE id = '${productId}'`;
      const productResult = await this.knowledgeGraphService.query(productQuery);
      
      if (!productResult || productResult.length === 0) {
        throw new Error(`未找到产品信息: ${productId}`);
      }
      
      const productName = productResult[0].name;
      
      // 使用产品名称搜索相关健康知识
      const searchResult = await this.knowledgeBaseService.search(`${productName} 健康 营养 功效`, {
        limit: 20,
        useSemanticSearch: true,
        filters: {
          categories: ['健康', '营养', '功效', '体质']
        }
      });
      
      const knowledgeItems = searchResult.items;
      
      // 保存到缓存
      this.setToCache(cacheKey, knowledgeItems);
      
      return knowledgeItems;
    } catch (error) {
      this.logger.error(`获取产品健康知识失败: ${productId}`, error);
      throw new Error(`获取产品健康知识失败: ${(error as Error).message}`);
    }
  }
  
  /**
   * 获取节气相关农产品知识
   */
  async getSolarTermAgricultureKnowledge(solarTerm: string): Promise<{
    solarTerm: string;
    knowledgeItems: KnowledgeItem[];
    products: string[];
  }> {
    this.checkServiceReady();
    
    // 生成缓存键
    const cacheKey = this.getCacheKey(this.SOLAR_TERM_PREFIX, solarTerm);
    
    // 检查缓存
    const cachedResult = this.getFromCache<{
      solarTerm: string;
      knowledgeItems: KnowledgeItem[];
      products: string[];
    }>(cacheKey);
    if (cachedResult) {
      this.logger.debug(`使用缓存的节气农产品知识: ${solarTerm}`);
      return cachedResult;
    }
    
    try {
      this.logger.debug(`获取节气农产品知识: ${solarTerm}`);
      
      // 查询与节气相关的农产品
      const solarTermQuery = `
        MATCH (s:SolarTerm {name: '${solarTerm}'})-[r]-(p:Product)
        RETURN p.name as productName
      `;
      
      const productResult = await this.knowledgeGraphService.query(solarTermQuery);
      const products = productResult.map((item: any) => item.productName);
      
      // 获取节气相关知识
      const searchResult = await this.knowledgeBaseService.search(`${solarTerm} 节气 农产品 养生`, {
        limit: 20,
        useSemanticSearch: true,
        filters: {
          categories: ['节气', '养生', '饮食']
        }
      });
      
      const result = {
        solarTerm,
        knowledgeItems: searchResult.items,
        products
      };
      
      // 保存到缓存
      this.setToCache(cacheKey, result);
      
      return result;
    } catch (error) {
      this.logger.error(`获取节气农产品知识失败: ${solarTerm}`, error);
      throw new Error(`获取节气农产品知识失败: ${(error as Error).message}`);
    }
  }
}