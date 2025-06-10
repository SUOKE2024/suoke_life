import { EventEmitter } from 'events';

/**
 * 中医知识类型枚举
 */
export enum TCMKnowledgeType {
  SYNDROME = 'syndrome',           // 证候
  SYMPTOM = 'symptom',            // 症状
  HERB = 'herb',                  // 中药
  FORMULA = 'formula',            // 方剂
  ACUPOINT = 'acupoint',          // 穴位
  MERIDIAN = 'meridian',          // 经络
  CONSTITUTION = 'constitution',   // 体质
  DISEASE = 'disease',            // 疾病
  TREATMENT = 'treatment',        // 治法
  THEORY = 'theory',              // 理论
  DIAGNOSTIC_METHOD = 'diagnostic_method', // 诊法
  LIFESTYLE = 'lifestyle'         // 养生
}

/**
 * 中医知识实体接口
 */
export interface TCMKnowledgeEntity {
  id: string;
  name: string;
  type: TCMKnowledgeType;
  aliases: string[];
  description: string;
  properties: Record<string, any>;
  relationships: TCMRelationship[];
  sources: string[];
  confidence: number;
  lastUpdated: number;
  metadata: {
    category: string;
    subcategory?: string;
    difficulty: 'basic' | 'intermediate' | 'advanced';
    clinicalRelevance: number;
    evidenceLevel: 'high' | 'medium' | 'low';
  };
}

/**
 * 中医关系接口
 */
export interface TCMRelationship {
  id: string;
  fromEntity: string;
  toEntity: string;
  relationshipType: string;
  strength: number;
  direction: 'bidirectional' | 'unidirectional';
  context?: string;
  evidence: string[];
  confidence: number;
}

/**
 * 中医诊断推理结果接口
 */
export interface TCMDiagnosisReasoning {
  syndrome: string;
  confidence: number;
  supportingSymptoms: string[];
  contradictingSymptoms: string[];
  recommendedFormulas: string[];
  recommendedHerbs: string[];
  recommendedAcupoints: string[];
  treatmentPrinciples: string[];
  lifestyleRecommendations: string[];
  reasoning: {
    steps: string[];
    evidenceChain: string[];
    alternativeDiagnoses: Array<{
      syndrome: string;
      confidence: number;
      reasoning: string;
    }>;
  };
}

/**
 * 中医知识查询接口
 */
export interface TCMKnowledgeQuery {
  query: string;
  type?: TCMKnowledgeType[];
  filters?: {
    category?: string;
    difficulty?: string;
    clinicalRelevance?: number;
    evidenceLevel?: string;
  };
  limit?: number;
  includeRelated?: boolean;
  language?: string;
}

/**
 * 中医知识搜索结果接口
 */
export interface TCMKnowledgeSearchResult {
  entities: TCMKnowledgeEntity[];
  totalCount: number;
  searchTime: number;
  suggestions: string[];
  relatedQueries: string[];
  facets: {
    types: Array<{ type: string; count: number ;}>;
    categories: Array<{ category: string; count: number ;}>;
    evidenceLevels: Array<{ level: string; count: number ;}>;
  };
}

/**
 * 扩展中医知识库服务
 * 提供全面的中医知识管理、查询和推理功能
 */
export class ExpandedTCMKnowledgeService extends EventEmitter {
  private knowledgeGraph: Map<string, TCMKnowledgeEntity> = new Map();
  private relationships: Map<string, TCMRelationship> = new Map();
  private indexedTerms: Map<string, Set<string>> = new Map();
  private synonyms: Map<string, string[]> = new Map();
  private categories: Map<string, string[]> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    super();
    this.initializeKnowledgeBase();
  }

  /**
   * 初始化中医知识库
   */
  private async initializeKnowledgeBase(): Promise<void> {
    try {
      await this.loadCoreKnowledge();
      await this.buildIndexes();
      await this.loadSynonyms();
      this.isInitialized = true;
      
      this.emit('knowledgeBaseInitialized', {
        entityCount: this.knowledgeGraph.size;
        relationshipCount: this.relationships.size;
        timestamp: Date.now()
      ;});


    } catch (error) {

      throw error;
    }
  }

  /**
   * 加载核心中医知识
   */
  private async loadCoreKnowledge(): Promise<void> {
    // 加载基础证候
    const syndromes = this.getCoreSyndromes();
    syndromes.forEach(syndrome => this.addEntity(syndrome));

    // 加载常见症状
    const symptoms = this.getCoreSymptoms();
    symptoms.forEach(symptom => this.addEntity(symptom));

    // 加载常用中药
    const herbs = this.getCoreHerbs();
    herbs.forEach(herb => this.addEntity(herb));

    // 加载经典方剂
    const formulas = this.getCoreFormulas();
    formulas.forEach(formula => this.addEntity(formula));

    // 加载重要穴位
    const acupoints = this.getCoreAcupoints();
    acupoints.forEach(acupoint => this.addEntity(acupoint));

    // 加载经络系统
    const meridians = this.getCoreMeridians();
    meridians.forEach(meridian => this.addEntity(meridian));

    // 加载体质类型
    const constitutions = this.getCoreConstitutions();
    constitutions.forEach(constitution => this.addEntity(constitution));

    // 建立关系
    await this.buildCoreRelationships();
  }

  /**
   * 获取核心证候
   */
  private getCoreSyndromes(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'syndrome_qi_deficiency';

        type: TCMKnowledgeType.SYNDROME;


        properties: {





        ;},
        relationships: [];

        confidence: 0.95;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'basic';
          clinicalRelevance: 0.9;
          evidenceLevel: 'high'
        ;}
      },
      {
        id: 'syndrome_blood_stasis';

        type: TCMKnowledgeType.SYNDROME;


        properties: {





        ;},
        relationships: [];

        confidence: 0.93;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'intermediate';
          clinicalRelevance: 0.85;
          evidenceLevel: 'high'
        ;}
      },
      {
        id: 'syndrome_yin_deficiency';

        type: TCMKnowledgeType.SYNDROME;


        properties: {





        ;},
        relationships: [];

        confidence: 0.94;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'intermediate';
          clinicalRelevance: 0.88;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 获取核心症状
   */
  private getCoreSymptoms(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'symptom_fatigue';

        type: TCMKnowledgeType.SYMPTOM;


        properties: {




        ;},
        relationships: [];

        confidence: 0.96;
        lastUpdated: Date.now();
        metadata: {

          difficulty: 'basic';
          clinicalRelevance: 0.9;
          evidenceLevel: 'high'
        ;}
      },
      {
        id: 'symptom_palpitation';

        type: TCMKnowledgeType.SYMPTOM;


        properties: {




        ;},
        relationships: [];

        confidence: 0.94;
        lastUpdated: Date.now();
        metadata: {

          difficulty: 'intermediate';
          clinicalRelevance: 0.85;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 获取核心中药
   */
  private getCoreHerbs(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'herb_ginseng';

        type: TCMKnowledgeType.HERB;


        properties: {





          dosage: '3-9g';


        },
        relationships: [];

        confidence: 0.98;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'basic';
          clinicalRelevance: 0.95;
          evidenceLevel: 'high'
        ;}
      },
      {
        id: 'herb_angelica';

        type: TCMKnowledgeType.HERB;


        properties: {





          dosage: '6-12g';


        },
        relationships: [];

        confidence: 0.97;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'basic';
          clinicalRelevance: 0.92;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 获取核心方剂
   */
  private getCoreFormulas(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'formula_sijunzi';

        type: TCMKnowledgeType.FORMULA;


        properties: {
          composition: {




          ;},





        },
        relationships: [];

        confidence: 0.98;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'basic';
          clinicalRelevance: 0.95;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 获取核心穴位
   */
  private getCoreAcupoints(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'acupoint_zusanli';

        type: TCMKnowledgeType.ACUPOINT;


        properties: {







        ;},
        relationships: [];

        confidence: 0.98;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'basic';
          clinicalRelevance: 0.95;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 获取核心经络
   */
  private getCoreMeridians(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'meridian_lung';

        type: TCMKnowledgeType.MERIDIAN;


        properties: {



          acupointCount: 11;



        },
        relationships: [];

        confidence: 0.97;
        lastUpdated: Date.now();
        metadata: {


          difficulty: 'intermediate';
          clinicalRelevance: 0.9;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 获取核心体质类型
   */
  private getCoreConstitutions(): TCMKnowledgeEntity[] {
    return [
      {
        id: 'constitution_peaceful';

        type: TCMKnowledgeType.CONSTITUTION;


        properties: {




          percentage: '32.8%'
        ;},
        relationships: [];

        confidence: 0.96;
        lastUpdated: Date.now();
        metadata: {

          difficulty: 'basic';
          clinicalRelevance: 0.85;
          evidenceLevel: 'high'
        ;}
      }
    ];
  }

  /**
   * 建立核心关系
   */
  private async buildCoreRelationships(): Promise<void> {
    // 证候与症状的关系
    this.addRelationship({
      id: 'rel_qi_deficiency_fatigue';
      fromEntity: 'syndrome_qi_deficiency';
      toEntity: 'symptom_fatigue';
      relationshipType: 'manifests_as';
      strength: 0.9;
      direction: 'unidirectional';

      confidence: 0.95
    ;});

    // 中药与证候的关系
    this.addRelationship({
      id: 'rel_ginseng_qi_deficiency';
      fromEntity: 'herb_ginseng';
      toEntity: 'syndrome_qi_deficiency';
      relationshipType: 'treats';
      strength: 0.95;
      direction: 'unidirectional';

      confidence: 0.98
    ;});

    // 方剂与证候的关系
    this.addRelationship({
      id: 'rel_sijunzi_qi_deficiency';
      fromEntity: 'formula_sijunzi';
      toEntity: 'syndrome_qi_deficiency';
      relationshipType: 'treats';
      strength: 0.92;
      direction: 'unidirectional';

      confidence: 0.96
    ;});

    // 穴位与证候的关系
    this.addRelationship({
      id: 'rel_zusanli_qi_deficiency';
      fromEntity: 'acupoint_zusanli';
      toEntity: 'syndrome_qi_deficiency';
      relationshipType: 'treats';
      strength: 0.85;
      direction: 'unidirectional';

      confidence: 0.9
    ;});
  }

  /**
   * 添加知识实体
   */
  public addEntity(entity: TCMKnowledgeEntity): void {
    this.knowledgeGraph.set(entity.id, entity);
    this.indexEntity(entity);
    
    this.emit('entityAdded', {
      entityId: entity.id;
      name: entity.name;
      type: entity.type;
      timestamp: Date.now()
    ;});
  }

  /**
   * 添加关系
   */
  public addRelationship(relationship: TCMRelationship): void {
    this.relationships.set(relationship.id, relationship);
    
    // 更新实体的关系列表
    const fromEntity = this.knowledgeGraph.get(relationship.fromEntity);
    if (fromEntity) {
      fromEntity.relationships.push(relationship);
    }

    this.emit('relationshipAdded', {
      relationshipId: relationship.id;
      fromEntity: relationship.fromEntity;
      toEntity: relationship.toEntity;
      type: relationship.relationshipType;
      timestamp: Date.now()
    ;});
  }

  /**
   * 搜索知识
   */
  public async searchKnowledge(query: TCMKnowledgeQuery): Promise<TCMKnowledgeSearchResult> {
    const startTime = Date.now();
    
    try {
      // 预处理查询
      const processedQuery = this.preprocessQuery(query.query);
      
      // 执行搜索
      const entities = this.executeSearch(processedQuery, query);
      
      // 生成建议和相关查询
      const suggestions = this.generateSuggestions(processedQuery);
      const relatedQueries = this.generateRelatedQueries(processedQuery);
      
      // 生成分面统计
      const facets = this.generateFacets(entities);
      
      const searchTime = Date.now() - startTime;
      
      const result: TCMKnowledgeSearchResult = {
        entities: entities.slice(0, query.limit || 20),
        totalCount: entities.length;
        searchTime,
        suggestions,
        relatedQueries,
        facets
      };

      this.emit('knowledgeSearched', {
        query: query.query;
        resultCount: result.totalCount;
        searchTime,
        timestamp: Date.now()
      ;});

      return result;

    } catch (error) {
      this.emit('knowledgeSearchError', {
        query: query.query;
        error: error instanceof Error ? error.message : String(error);
        timestamp: Date.now()
      ;});
      throw error;
    }
  }

  /**
   * 中医诊断推理
   */
  public async diagnosisReasoning(symptoms: string[], context?: any): Promise<TCMDiagnosisReasoning> {
    try {
      // 症状标准化
      const normalizedSymptoms = this.normalizeSymptoms(symptoms);
      
      // 查找相关证候
      const candidateSyndromes = this.findCandidateSyndromes(normalizedSymptoms);
      
      // 计算证候匹配度
      const syndromeScores = this.calculateSyndromeScores(normalizedSymptoms, candidateSyndromes);
      
      // 选择最佳证候
      const bestSyndrome = syndromeScores[0];
      
      if (!bestSyndrome) {

      }

      // 生成推理结果
      const reasoning = await this.generateDiagnosisReasoning(
        bestSyndrome,
        normalizedSymptoms,
        syndromeScores
      );

      this.emit('diagnosisCompleted', {
        syndrome: reasoning.syndrome;
        confidence: reasoning.confidence;
        symptomCount: symptoms.length;
        timestamp: Date.now()
      ;});

      return reasoning;

    } catch (error) {
      this.emit('diagnosisError', {
        symptoms,
        error: error instanceof Error ? error.message : String(error);
        timestamp: Date.now()
      ;});
      throw error;
    }
  }

  /**
   * 获取实体详情
   */
  public getEntityDetails(entityId: string, includeRelated: boolean = true): TCMKnowledgeEntity | null {
    const entity = this.knowledgeGraph.get(entityId);
    if (!entity) return null;

    if (includeRelated) {
      // 添加相关实体信息
      const relatedEntities = this.getRelatedEntities(entityId);
      (entity as any).relatedEntities = relatedEntities;
    }

    return entity;
  }

  /**
   * 获取知识统计
   */
  public getKnowledgeStatistics(): {
    totalEntities: number;
    totalRelationships: number;
    entityTypes: Record<string, number>;
    categories: Record<string, number>;
    lastUpdated: number;
  } {
    const entityTypes: Record<string, number> = {;};
    const categories: Record<string, number> = {;};

    for (const entity of this.knowledgeGraph.values()) {
      entityTypes[entity.type] = (entityTypes[entity.type] || 0) + 1;
      categories[entity.metadata.category] = (categories[entity.metadata.category] || 0) + 1;
    }

    return {
      totalEntities: this.knowledgeGraph.size;
      totalRelationships: this.relationships.size;
      entityTypes,
      categories,
      lastUpdated: Date.now()
    ;};
  }

  // 私有方法

  private indexEntity(entity: TCMKnowledgeEntity): void {
    // 索引实体名称和别名
    const terms = [entity.name, ...entity.aliases];
    terms.forEach(term => {
      const normalizedTerm = term.toLowerCase();
      if (!this.indexedTerms.has(normalizedTerm)) {
        this.indexedTerms.set(normalizedTerm, new Set());
      }
      this.indexedTerms.get(normalizedTerm)!.add(entity.id);
    });
  }

  private async buildIndexes(): Promise<void> {
    // 构建分类索引
    for (const entity of this.knowledgeGraph.values()) {
      const category = entity.metadata.category;
      if (!this.categories.has(category)) {
        this.categories.set(category, []);
      }
      this.categories.get(category)!.push(entity.id);
    }
  }

  private async loadSynonyms(): Promise<void> {
    // 加载同义词映射
    const synonymMappings = [





    ];

    synonymMappings.forEach(group => {
      const primary = group[0];
      const synonyms = group.slice(1);
      this.synonyms.set(primary, synonyms);
      synonyms.forEach(synonym => {
        this.synonyms.set(synonym, [primary]);
      });
    });
  }

  private preprocessQuery(query: string): string {
    // 查询预处理：去除标点、转换同义词等
    let processed = query.toLowerCase().trim();
    
    // 同义词替换
    for (const [term, synonyms] of this.synonyms) {
      if (processed.includes(term)) {
        return term; // 返回标准术语
      }
      for (const synonym of synonyms) {
        if (processed.includes(synonym)) {
          return term; // 返回标准术语
        }
      }
    }
    
    return processed;
  }

  private executeSearch(query: string, searchQuery: TCMKnowledgeQuery): TCMKnowledgeEntity[] {
    const results: Array<{ entity: TCMKnowledgeEntity; score: number ;}> = [];

    for (const entity of this.knowledgeGraph.values()) {
      // 类型过滤
      if (searchQuery.type && !searchQuery.type.includes(entity.type)) {
        continue;
      }

      // 其他过滤条件
      if (searchQuery.filters) {
        if (searchQuery.filters.category && entity.metadata.category !== searchQuery.filters.category) {
          continue;
        }
        if (searchQuery.filters.difficulty && entity.metadata.difficulty !== searchQuery.filters.difficulty) {
          continue;
        }
        if (searchQuery.filters.clinicalRelevance && entity.metadata.clinicalRelevance < searchQuery.filters.clinicalRelevance) {
          continue;
        }
      }

      // 计算匹配分数
      const score = this.calculateMatchScore(query, entity);
      if (score > 0) {
        results.push({ entity, score });
      }
    }

    // 按分数排序
    results.sort((a, b) => b.score - a.score);
    
    return results.map(r => r.entity);
  }

  private calculateMatchScore(query: string, entity: TCMKnowledgeEntity): number {
    let score = 0;
    
    // 名称匹配
    if (entity.name.toLowerCase().includes(query)) {
      score += 10;
    }
    
    // 别名匹配
    for (const alias of entity.aliases) {
      if (alias.toLowerCase().includes(query)) {
        score += 8;
      }
    }
    
    // 描述匹配
    if (entity.description.toLowerCase().includes(query)) {
      score += 5;
    }
    
    // 属性匹配
    const propertiesStr = JSON.stringify(entity.properties).toLowerCase();
    if (propertiesStr.includes(query)) {
      score += 3;
    }
    
    return score;
  }

  private generateSuggestions(query: string): string[] {
    const suggestions: string[] = [];
    
    // 基于索引生成建议
    for (const [term, entityIds] of this.indexedTerms) {
      if (term.includes(query) && term !== query) {
        suggestions.push(term);
      }
    }
    
    return suggestions.slice(0, 5);
  }

  private generateRelatedQueries(query: string): string[] {
    // 生成相关查询建议
    const related = [




    ];
    
    return related;
  }

  private generateFacets(entities: TCMKnowledgeEntity[]): any {
    const types: Record<string, number> = {;};
    const categories: Record<string, number> = {;};
    const evidenceLevels: Record<string, number> = {;};

    entities.forEach(entity => {
      types[entity.type] = (types[entity.type] || 0) + 1;
      categories[entity.metadata.category] = (categories[entity.metadata.category] || 0) + 1;
      evidenceLevels[entity.metadata.evidenceLevel] = (evidenceLevels[entity.metadata.evidenceLevel] || 0) + 1;
    });

    return {
      types: Object.entries(types).map(([type, count]) => ({ type, count ;})),
      categories: Object.entries(categories).map(([category, count]) => ({ category, count ;})),
      evidenceLevels: Object.entries(evidenceLevels).map(([level, count]) => ({ level, count ;}))
    };
  }

  private normalizeSymptoms(symptoms: string[]): string[] {
    return symptoms.map(symptom => {
      const normalized = symptom.toLowerCase().trim();
      // 同义词标准化
      for (const [standard, synonyms] of this.synonyms) {
        if (synonyms.includes(normalized) || standard === normalized) {
          return standard;
        }
      }
      return normalized;
    });
  }

  private findCandidateSyndromes(symptoms: string[]): TCMKnowledgeEntity[] {
    const candidates: TCMKnowledgeEntity[] = [];
    
    for (const entity of this.knowledgeGraph.values()) {
      if (entity.type === TCMKnowledgeType.SYNDROME) {
        // 检查症状匹配
        const syndromeSymptoms = entity.properties.mainSymptoms || [];
        const hasMatchingSymptom = symptoms.some(symptom => 
          syndromeSymptoms.some((ss: string) => ss.includes(symptom) || symptom.includes(ss))
        );
        
        if (hasMatchingSymptom) {
          candidates.push(entity);
        }
      }
    }
    
    return candidates;
  }

  private calculateSyndromeScores(symptoms: string[], syndromes: TCMKnowledgeEntity[]): Array<{
    syndrome: TCMKnowledgeEntity;
    score: number;
    matchingSymptoms: string[];
  }> {
    const scores = syndromes.map(syndrome => {
      const mainSymptoms = syndrome.properties.mainSymptoms || [];
      const secondarySymptoms = syndrome.properties.secondarySymptoms || [];
      
      let score = 0;
      const matchingSymptoms: string[] = [];
      
      // 主症状匹配
      symptoms.forEach(symptom => {
        mainSymptoms.forEach((mainSymptom: string) => {
          if (mainSymptom.includes(symptom) || symptom.includes(mainSymptom)) {
            score += 10;
            matchingSymptoms.push(symptom);
          }
        });
        
        // 次症状匹配
        secondarySymptoms.forEach((secondarySymptom: string) => {
          if (secondarySymptom.includes(symptom) || symptom.includes(secondarySymptom)) {
            score += 5;
            matchingSymptoms.push(symptom);
          }
        });
      });
      
      return { syndrome, score, matchingSymptoms };
    });
    
    return scores.sort((a, b) => b.score - a.score);
  }

  private async generateDiagnosisReasoning(
    bestMatch: { syndrome: TCMKnowledgeEntity; score: number; matchingSymptoms: string[] ;},
    symptoms: string[];
    allMatches: Array<{ syndrome: TCMKnowledgeEntity; score: number; matchingSymptoms: string[] ;}>
  ): Promise<TCMDiagnosisReasoning> {
    const syndrome = bestMatch.syndrome;
    
    // 查找推荐的治疗方法
    const recommendedFormulas = this.findRelatedEntities(syndrome.id, TCMKnowledgeType.FORMULA);
    const recommendedHerbs = this.findRelatedEntities(syndrome.id, TCMKnowledgeType.HERB);
    const recommendedAcupoints = this.findRelatedEntities(syndrome.id, TCMKnowledgeType.ACUPOINT);
    
    return {
      syndrome: syndrome.name;
      confidence: Math.min(bestMatch.score / 100, 1),
      supportingSymptoms: bestMatch.matchingSymptoms;
      contradictingSymptoms: symptoms.filter(s => !bestMatch.matchingSymptoms.includes(s));
      recommendedFormulas: recommendedFormulas.map(f => f.name);
      recommendedHerbs: recommendedHerbs.map(h => h.name);
      recommendedAcupoints: recommendedAcupoints.map(a => a.name);
      treatmentPrinciples: syndrome.properties.treatmentPrinciples || [];
      lifestyleRecommendations: syndrome.properties.lifestyleRecommendations || [];
      reasoning: {
        steps: [


          `匹配度: ${(bestMatch.score / 100 * 100).toFixed(1);}%`
        ],
        evidenceChain: syndrome.sources;
        alternativeDiagnoses: allMatches.slice(1, 4).map(match => ({
          syndrome: match.syndrome.name;
          confidence: Math.min(match.score / 100, 1),

        ;}))
      }
    };
  }

  private findRelatedEntities(entityId: string, targetType: TCMKnowledgeType): TCMKnowledgeEntity[] {
    const related: TCMKnowledgeEntity[] = [];
    
    for (const relationship of this.relationships.values()) {
      if (relationship.fromEntity === entityId || relationship.toEntity === entityId) {
        const relatedEntityId = relationship.fromEntity === entityId ? 
          relationship.toEntity : relationship.fromEntity;
        
        const relatedEntity = this.knowledgeGraph.get(relatedEntityId);
        if (relatedEntity && relatedEntity.type === targetType) {
          related.push(relatedEntity);
        }
      }
    }
    
    return related;
  }

  private getRelatedEntities(entityId: string): TCMKnowledgeEntity[] {
    const related: TCMKnowledgeEntity[] = [];
    
    for (const relationship of this.relationships.values()) {
      if (relationship.fromEntity === entityId || relationship.toEntity === entityId) {
        const relatedEntityId = relationship.fromEntity === entityId ? 
          relationship.toEntity : relationship.fromEntity;
        
        const relatedEntity = this.knowledgeGraph.get(relatedEntityId);
        if (relatedEntity) {
          related.push(relatedEntity);
        }
      }
    }
    
    return related;
  }
}

export default ExpandedTCMKnowledgeService; 