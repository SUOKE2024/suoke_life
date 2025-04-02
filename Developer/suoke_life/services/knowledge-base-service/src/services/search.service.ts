/**
 * 搜索服务
 * 处理知识搜索相关的业务逻辑
 */
import { KnowledgeEntryModel } from '../models/knowledge-entry.model';
import { TraditionalCultureKnowledgeModel } from '../models/traditional-culture-knowledge.model';
import { ModernMedicineKnowledgeModel } from '../models/modern-medicine-knowledge.model';
import { VectorDBService } from './vector-db.service';
import { logger } from '../utils/logger';

export interface SearchResult {
  type: string;
  id: string;
  title: string;
  summary?: string;
  content: string;
  categories: any[];
  tags: any[];
  score: number;
  additionalInfo?: any;
}

export interface SearchFilter {
  knowledgeType?: string[];
  category?: string[];
  tag?: string[];
  medicalSystem?: string[];
  culturalSystem?: string[];
  researchSupport?: string[];
  historicalPeriod?: string[];
}

export class SearchService {
  private vectorDBService: VectorDBService;

  constructor() {
    this.vectorDBService = new VectorDBService();
  }

  /**
   * 全文搜索知识
   * @param query 搜索查询字符串
   * @param page 页码
   * @param limit 每页数量
   * @param filter 过滤条件
   * @returns 搜索结果及分页信息
   */
  async searchKnowledge(
    query: string,
    page: number = 1,
    limit: number = 20,
    filter: SearchFilter = {}
  ) {
    try {
      const skip = (page - 1) * limit;
      
      // 构建过滤条件
      const baseFilter: any = {};
      
      if (filter.category && filter.category.length > 0) {
        baseFilter.categories = { $in: filter.category };
      }
      
      if (filter.tag && filter.tag.length > 0) {
        baseFilter.tags = { $in: filter.tag };
      }
      
      // 根据知识类型决定搜索哪些集合
      const collections = this.getCollectionsToSearch(filter.knowledgeType);
      
      // 准备搜索结果
      let results: SearchResult[] = [];
      let total = 0;
      
      // 执行全文搜索
      for (const collection of collections) {
        // 为每个集合构建特定的过滤条件
        const collectionFilter = { ...baseFilter };
        
        if (collection === 'traditional-culture' && filter.culturalSystem && filter.culturalSystem.length > 0) {
          collectionFilter.culturalSystem = { $in: filter.culturalSystem };
        }
        
        if (collection === 'traditional-culture' && filter.historicalPeriod && filter.historicalPeriod.length > 0) {
          collectionFilter.historicalPeriod = { $in: filter.historicalPeriod };
        }
        
        if (collection === 'modern-medicine' && filter.medicalSystem && filter.medicalSystem.length > 0) {
          collectionFilter.medicalSystem = { $in: filter.medicalSystem };
        }
        
        if (collection === 'modern-medicine' && filter.researchSupport && filter.researchSupport.length > 0) {
          collectionFilter.researchSupport = { $in: filter.researchSupport };
        }
        
        const collectionResults = await this.searchInCollection(collection, query, collectionFilter);
        
        total += collectionResults.total;
        results = results.concat(collectionResults.results);
      }
      
      // 按照相关性排序
      results.sort((a, b) => b.score - a.score);
      
      // 分页处理
      const paginatedResults = results.slice(skip, skip + limit);
      
      return {
        results: paginatedResults,
        pagination: {
          total,
          page,
          limit,
          pages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      logger.error(`搜索知识失败, 查询: ${query}`, error);
      throw error;
    }
  }

  /**
   * 语义搜索知识
   * @param query 搜索查询字符串
   * @param page 页码
   * @param limit 每页数量
   * @param filter 过滤条件
   * @returns 搜索结果及分页信息
   */
  async semanticSearchKnowledge(
    query: string,
    page: number = 1,
    limit: number = 20,
    filter: SearchFilter = {}
  ) {
    try {
      const skip = (page - 1) * limit;
      
      // 准备元数据过滤条件
      const metadataFilter: any = {};
      
      if (filter.knowledgeType && filter.knowledgeType.length > 0) {
        metadataFilter.type = { $in: filter.knowledgeType };
      }
      
      if (filter.culturalSystem && filter.culturalSystem.length > 0) {
        metadataFilter.culturalSystem = { $in: filter.culturalSystem };
      }
      
      if (filter.medicalSystem && filter.medicalSystem.length > 0) {
        metadataFilter.medicalSystem = { $in: filter.medicalSystem };
      }
      
      if (filter.researchSupport && filter.researchSupport.length > 0) {
        metadataFilter.researchSupport = { $in: filter.researchSupport };
      }
      
      if (filter.historicalPeriod && filter.historicalPeriod.length > 0) {
        metadataFilter.historicalPeriod = { $in: filter.historicalPeriod };
      }
      
      // 执行向量搜索
      const vectorResults = await this.vectorDBService.searchVectors(query, limit * 3, metadataFilter);
      
      // 获取详细信息
      const enrichedResults = await this.enrichVectorResults(vectorResults, filter);
      
      // 分页处理
      const paginatedResults = enrichedResults.slice(skip, skip + limit);
      
      return {
        results: paginatedResults,
        pagination: {
          total: enrichedResults.length,
          page,
          limit,
          pages: Math.ceil(enrichedResults.length / limit)
        }
      };
    } catch (error) {
      logger.error(`语义搜索知识失败, 查询: ${query}`, error);
      throw error;
    }
  }

  /**
   * 混合搜索知识（全文+语义）
   * @param query 搜索查询字符串
   * @param page 页码
   * @param limit 每页数量
   * @param filter 过滤条件
   * @returns 搜索结果及分页信息
   */
  async hybridSearchKnowledge(
    query: string,
    page: number = 1,
    limit: number = 20,
    filter: SearchFilter = {}
  ) {
    try {
      // 并行执行全文搜索和语义搜索
      const [textResults, semanticResults] = await Promise.all([
        this.searchKnowledge(query, 1, limit * 2, filter),
        this.semanticSearchKnowledge(query, 1, limit * 2, filter)
      ]);
      
      // 合并结果
      const mergedResults = this.mergeSearchResults(
        textResults.results,
        semanticResults.results
      );
      
      // 计算起始和结束索引
      const skip = (page - 1) * limit;
      const end = skip + limit;
      
      // 分页处理
      const paginatedResults = mergedResults.slice(skip, end);
      
      return {
        results: paginatedResults,
        pagination: {
          total: mergedResults.length,
          page,
          limit,
          pages: Math.ceil(mergedResults.length / limit)
        }
      };
    } catch (error) {
      logger.error(`混合搜索知识失败, 查询: ${query}`, error);
      throw error;
    }
  }

  /**
   * 根据知识类型筛选需要搜索的集合
   * @param knowledgeTypes 知识类型数组
   * @returns 集合列表
   */
  private getCollectionsToSearch(knowledgeTypes?: string[]): string[] {
    if (!knowledgeTypes || knowledgeTypes.length === 0) {
      return ['general', 'traditional-culture', 'modern-medicine'];
    }
    
    const collections: string[] = [];
    
    if (knowledgeTypes.includes('general')) {
      collections.push('general');
    }
    
    if (knowledgeTypes.includes('traditional-culture')) {
      collections.push('traditional-culture');
    }
    
    if (knowledgeTypes.includes('modern-medicine')) {
      collections.push('modern-medicine');
    }
    
    return collections.length > 0 ? collections : ['general', 'traditional-culture', 'modern-medicine'];
  }

  /**
   * 在特定集合中执行全文搜索
   * @param collection 集合名称
   * @param query 搜索查询
   * @param filter 过滤条件
   * @returns 搜索结果
   */
  private async searchInCollection(
    collection: string,
    query: string,
    filter: any
  ): Promise<{ results: SearchResult[], total: number }> {
    let model;
    let type;
    
    // 根据集合选择模型
    switch (collection) {
      case 'traditional-culture':
        model = TraditionalCultureKnowledgeModel;
        type = 'traditional-culture';
        break;
      case 'modern-medicine':
        model = ModernMedicineKnowledgeModel;
        type = 'modern-medicine';
        break;
      default:
        model = KnowledgeEntryModel;
        type = 'general';
    }
    
    // 执行全文搜索
    const searchFilter = {
      ...filter,
      $text: { $search: query }
    };
    
    const documents = await model.find(
      searchFilter,
      { score: { $meta: 'textScore' } }
    )
      .populate('categories')
      .populate('tags')
      .sort({ score: { $meta: 'textScore' } })
      .exec();
    
    // 转换为统一格式
    const results: SearchResult[] = documents.map(doc => {
      const result: SearchResult = {
        type,
        id: doc._id.toString(),
        title: doc.title,
        summary: doc.summary,
        content: doc.content,
        categories: doc.categories,
        tags: doc.tags,
        score: doc.get('score') || 0,
        additionalInfo: {}
      };
      
      // 添加特定类型的额外信息
      if (type === 'traditional-culture') {
        result.additionalInfo = {
          culturalSystem: doc.culturalSystem,
          historicalPeriod: doc.historicalPeriod
        };
      } else if (type === 'modern-medicine') {
        result.additionalInfo = {
          medicalSystem: doc.medicalSystem,
          researchSupport: doc.researchSupport
        };
      }
      
      return result;
    });
    
    return {
      results,
      total: documents.length
    };
  }

  /**
   * 丰富向量搜索结果
   * @param vectorResults 向量搜索结果
   * @param filter 过滤条件
   * @returns 丰富后的搜索结果
   */
  private async enrichVectorResults(
    vectorResults: any[],
    filter: SearchFilter
  ): Promise<SearchResult[]> {
    // 按类型分组向量结果
    const idsByType: { [key: string]: string[] } = {};
    
    vectorResults.forEach(result => {
      const type = result.metadata.type || 'general';
      
      if (!idsByType[type]) {
        idsByType[type] = [];
      }
      
      idsByType[type].push(result.id);
    });
    
    // 为每种类型批量获取详细信息
    const detailsPromises = Object.entries(idsByType).map(async ([type, ids]) => {
      let model;
      
      switch (type) {
        case 'traditional-culture':
          model = TraditionalCultureKnowledgeModel;
          break;
        case 'modern-medicine':
          model = ModernMedicineKnowledgeModel;
          break;
        default:
          model = KnowledgeEntryModel;
      }
      
      let query = model.find({ _id: { $in: ids } });
      
      // 应用过滤器
      if (type === 'general' || type === 'traditional-culture' || type === 'modern-medicine') {
        if (filter.category && filter.category.length > 0) {
          query = query.where('categories').in(filter.category);
        }
        
        if (filter.tag && filter.tag.length > 0) {
          query = query.where('tags').in(filter.tag);
        }
      }
      
      if (type === 'traditional-culture') {
        if (filter.culturalSystem && filter.culturalSystem.length > 0) {
          query = query.where('culturalSystem').in(filter.culturalSystem);
        }
        
        if (filter.historicalPeriod && filter.historicalPeriod.length > 0) {
          query = query.where('historicalPeriod').in(filter.historicalPeriod);
        }
      }
      
      if (type === 'modern-medicine') {
        if (filter.medicalSystem && filter.medicalSystem.length > 0) {
          query = query.where('medicalSystem').in(filter.medicalSystem);
        }
        
        if (filter.researchSupport && filter.researchSupport.length > 0) {
          query = query.where('researchSupport').in(filter.researchSupport);
        }
      }
      
      const documents = await query
        .populate('categories')
        .populate('tags')
        .exec();
      
      // 创建ID到文档的映射
      const docMap = new Map();
      documents.forEach(doc => {
        docMap.set(doc._id.toString(), doc);
      });
      
      return { type, docMap };
    });
    
    const detailsResults = await Promise.all(detailsPromises);
    
    // 创建类型到文档映射的映射
    const typeToDocMap = new Map();
    detailsResults.forEach(result => {
      typeToDocMap.set(result.type, result.docMap);
    });
    
    // 合并向量结果与详细信息
    const enrichedResults: SearchResult[] = [];
    
    for (const vectorResult of vectorResults) {
      const type = vectorResult.metadata.type || 'general';
      const docMap = typeToDocMap.get(type);
      
      if (docMap && docMap.has(vectorResult.id)) {
        const doc = docMap.get(vectorResult.id);
        
        const result: SearchResult = {
          type,
          id: doc._id.toString(),
          title: doc.title,
          summary: doc.summary,
          content: doc.content,
          categories: doc.categories,
          tags: doc.tags,
          score: vectorResult.score,
          additionalInfo: {}
        };
        
        // 添加特定类型的额外信息
        if (type === 'traditional-culture') {
          result.additionalInfo = {
            culturalSystem: doc.culturalSystem,
            historicalPeriod: doc.historicalPeriod
          };
        } else if (type === 'modern-medicine') {
          result.additionalInfo = {
            medicalSystem: doc.medicalSystem,
            researchSupport: doc.researchSupport
          };
        }
        
        enrichedResults.push(result);
      }
    }
    
    return enrichedResults;
  }

  /**
   * 合并全文搜索和语义搜索结果
   * @param textResults 全文搜索结果
   * @param semanticResults 语义搜索结果
   * @returns 合并后的搜索结果
   */
  private mergeSearchResults(
    textResults: SearchResult[],
    semanticResults: SearchResult[]
  ): SearchResult[] {
    // 创建ID到结果的映射
    const resultMap = new Map<string, SearchResult>();
    
    // 处理全文搜索结果
    textResults.forEach(result => {
      resultMap.set(result.id, {
        ...result,
        score: result.score
      });
    });
    
    // 处理语义搜索结果
    semanticResults.forEach(result => {
      if (resultMap.has(result.id)) {
        // 如果结果已存在，更新分数
        const existingResult = resultMap.get(result.id)!;
        // 语义搜索结果的分数范围通常是0-1，将其调整为与全文搜索兼容
        const adjustedScore = result.score * 10;
        
        // 合并分数: 以较高分数为准，略微提高同时出现在两个结果中的项
        resultMap.set(result.id, {
          ...existingResult,
          score: Math.max(existingResult.score, adjustedScore) * 1.1
        });
      } else {
        // 否则，添加新结果
        resultMap.set(result.id, {
          ...result,
          // 语义搜索结果的分数范围通常是0-1，将其调整为与全文搜索兼容
          score: result.score * 10
        });
      }
    });
    
    // 转换回数组并排序
    return Array.from(resultMap.values()).sort((a, b) => b.score - a.score);
  }
}