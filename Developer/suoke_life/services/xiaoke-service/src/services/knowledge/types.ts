/**
 * 知识服务类型定义
 */

/**
 * 基础服务接口
 */
export interface BaseService {
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
}

/**
 * 知识库服务接口
 */
export interface KnowledgeBaseService extends BaseService {
  /**
   * 搜索知识库
   * @param query 查询词
   * @param options 搜索选项
   */
  search(query: string, options?: KnowledgeSearchOptions): Promise<KnowledgeSearchResult>;
  
  /**
   * 获取知识条目
   * @param id 知识条目ID
   */
  getItem(id: string): Promise<KnowledgeItem>;
  
  /**
   * 按分类获取知识条目
   * @param category 分类名称
   * @param limit 返回数量限制
   */
  getItemsByCategory(category: string, limit?: number): Promise<KnowledgeItem[]>;
  
  /**
   * 按标签获取知识条目
   * @param tag 标签名称
   * @param limit 返回数量限制
   */
  getItemsByTag(tag: string, limit?: number): Promise<KnowledgeItem[]>;
}

/**
 * 知识图谱服务接口
 */
export interface KnowledgeGraphService extends BaseService {
  /**
   * 图谱查询
   * @param query 查询语句
   */
  query(query: string): Promise<any>;
  
  /**
   * 搜索图谱节点
   * @param query 查询词
   */
  searchNodes(query: string): Promise<GraphNode[]>;
  
  /**
   * 获取节点关系
   * @param nodeId 节点ID
   */
  getNodeRelations(nodeId: string): Promise<GraphRelation[]>;
  
  /**
   * 查找最短路径
   * @param fromId 起始节点ID
   * @param toId 目标节点ID
   */
  findShortestPath(fromId: string, toId: string): Promise<PathResult>;
  
  /**
   * 获取产品关联概念
   * @param productId 产品ID
   */
  getProductConcepts(productId: string): Promise<GraphNode[]>;
  
  /**
   * 获取农产品相关知识
   * @param productId 产品ID
   */
  getProductKnowledge(productId: string): Promise<KnowledgeConnection[]>;
}

/**
 * 知识搜索选项
 */
export interface KnowledgeSearchOptions {
  /**
   * 返回条目数量限制
   */
  limit?: number;
  
  /**
   * 结果偏移量(分页)
   */
  offset?: number;
  
  /**
   * 是否使用语义搜索
   */
  useSemanticSearch?: boolean;
  
  /**
   * 过滤条件
   */
  filters?: {
    /**
     * 分类筛选
     */
    categories?: string[];
    
    /**
     * 标签筛选
     */
    tags?: string[];
    
    /**
     * 领域筛选
     */
    domains?: string[];
  };
  
  /**
   * 排序方式
   */
  sort?: {
    field: string;
    order: 'asc' | 'desc';
  };
}

/**
 * 知识搜索结果
 */
export interface KnowledgeSearchResult {
  /**
   * 原始查询
   */
  query: string;
  
  /**
   * 结果条目
   */
  items: KnowledgeItem[];
  
  /**
   * 结果总数
   */
  total: number;
  
  /**
   * 查询耗时(毫秒)
   */
  timeTaken: number;
  
  /**
   * 搜索建议
   */
  suggestions?: string[];
}

/**
 * 知识条目
 */
export interface KnowledgeItem {
  /**
   * 条目ID
   */
  id: string;
  
  /**
   * 标题
   */
  title: string;
  
  /**
   * 内容
   */
  content: string;
  
  /**
   * 内容类型
   */
  contentType: 'text' | 'html' | 'markdown' | 'json';
  
  /**
   * 来源
   */
  source?: string;
  
  /**
   * 作者
   */
  author?: string;
  
  /**
   * 创建时间
   */
  createdAt?: Date;
  
  /**
   * 更新时间
   */
  updatedAt?: Date;
  
  /**
   * 分类
   */
  categories?: string[];
  
  /**
   * 标签
   */
  tags?: string[];
  
  /**
   * 领域
   */
  domains?: string[];
  
  /**
   * 元数据
   */
  metadata?: Record<string, any>;
  
  /**
   * 相关性得分
   */
  relevance?: number;
}

/**
 * 图谱节点
 */
export interface GraphNode {
  /**
   * 节点ID
   */
  id: string;
  
  /**
   * 节点标签
   */
  label: string;
  
  /**
   * 节点类型
   */
  type: string;
  
  /**
   * 节点属性
   */
  properties: Record<string, any>;
}

/**
 * 图谱关系
 */
export interface GraphRelation {
  /**
   * 关系ID
   */
  id: string;
  
  /**
   * 关系类型
   */
  type: string;
  
  /**
   * 起始节点ID
   */
  from: string;
  
  /**
   * 目标节点ID
   */
  to: string;
  
  /**
   * 关系属性
   */
  properties?: Record<string, any>;
}

/**
 * 路径结果
 */
export interface PathResult {
  /**
   * 路径节点
   */
  nodes: GraphNode[];
  
  /**
   * 路径关系
   */
  relations: GraphRelation[];
  
  /**
   * 路径长度
   */
  length: number;
}

/**
 * 知识图谱连接
 */
export interface KnowledgeConnection {
  /**
   * 节点
   */
  node: GraphNode;
  
  /**
   * 关系
   */
  relation: GraphRelation;
  
  /**
   * 相关知识条目
   */
  knowledgeItems?: KnowledgeItem[];
}

/**
 * 知识增强类型
 */
export interface KnowledgeEnrichment {
  /**
   * 产品信息
   */
  productInfo: {
    /**
     * 产品ID
     */
    id: string;
    
    /**
     * 产品名称
     */
    name: string;
    
    /**
     * 产品描述
     */
    description?: string;
  };
  
  /**
   * 知识条目
   */
  knowledgeItems: KnowledgeItem[];
  
  /**
   * 关联概念
   */
  relatedConcepts: GraphNode[];
  
  /**
   * 健康益处
   */
  healthBenefits: string[];
  
  /**
   * 适宜季节
   */
  seasonalRelevance?: {
    /**
     * 节气
     */
    solarTerms: string[];
    
    /**
     * 最佳季节
     */
    bestSeasons: string[];
  };
  
  /**
   * 适宜体质
   */
  constitutionFit?: {
    /**
     * 适宜体质
     */
    suitable: string[];
    
    /**
     * 不适宜体质
     */
    unsuitable: string[];
  };
}

/**
 * 整合知识服务接口
 */
export interface KnowledgeIntegrationService extends BaseService {
  /**
   * 产品知识增强
   * @param productId 产品ID
   */
  enrichProductKnowledge(productId: string): Promise<KnowledgeEnrichment>;
  
  /**
   * 查询农产品与健康知识的关联
   * @param query 查询词
   * @param options 搜索选项
   */
  searchAgricultureHealthKnowledge(query: string, options?: KnowledgeSearchOptions): Promise<KnowledgeSearchResult>;
  
  /**
   * 获取产品相关健康知识
   * @param productId 产品ID
   */
  getProductHealthKnowledge(productId: string): Promise<KnowledgeItem[]>;
  
  /**
   * 获取节气相关农产品知识
   * @param solarTerm 节气
   */
  getSolarTermAgricultureKnowledge(solarTerm: string): Promise<{
    solarTerm: string;
    knowledgeItems: KnowledgeItem[];
    products: string[];
  }>;
}