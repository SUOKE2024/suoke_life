/**
 * 中医知识库
 * 提供五诊算法所需的中医理论知识支持
 * 包括经典理论、现代研究、临床数据等
 * @author 索克生活技术团队
 * @version 1.0.0
 */

export interface KnowledgeBaseConfig {
  version: string;
  updateInterval: number;
  sources: string[];
  caching: {
    enabled: boolean;
    ttl: number;
    maxSize: number;
  };
}

export interface TCMConcept {
  id: string;
  name: string;
  category: string;
  description: string;
  properties: Record<string, any>;
  relationships: ConceptRelationship[];
  sources: string[];
  confidence: number;
}

export interface ConceptRelationship {
  type: 'belongs_to' | 'related_to' | 'opposite_to' | 'generates' | 'restricts';
  target: string;
  strength: number;
  description: string;
}

export interface DiagnosisPattern {
  id: string;
  name: string;
  category: string;
  symptoms: string[];
  signs: string[];
  syndromes: string[];
  treatments: string[];
  confidence: number;
}

export interface SyndromeInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  mainSymptoms: string[];
  secondarySymptoms: string[];
  tongueFeatures: string[];
  pulseFeatures: string[];
  treatments: TreatmentInfo[];
  prognosis: string;
}

export interface TreatmentInfo {
  type: 'herbal' | 'acupuncture' | 'lifestyle' | 'diet';
  name: string;
  description: string;
  dosage?: string;
  duration?: string;
  contraindications: string[];
  sideEffects: string[];
}

export interface ConstitutionType {
  id: string;
  name: string;
  description: string;
  characteristics: {
    physical: string[];
    psychological: string[];
    pathological: string[];
  };
  recommendations: {
    diet: string[];
    exercise: string[];
    lifestyle: string[];
    prevention: string[];
  };
}

/**
 * 中医知识库类
 */
export class TCMKnowledgeBase {
  private config: KnowledgeBaseConfig;
  private concepts: Map<string, TCMConcept> = new Map();
  private patterns: Map<string, DiagnosisPattern> = new Map();
  private syndromes: Map<string, SyndromeInfo> = new Map();
  private constitutions: Map<string, ConstitutionType> = new Map();
  private cache: Map<string, any> = new Map();

  constructor(config: Partial<KnowledgeBaseConfig> = {}) {
    this.config = {
      version: '1.0.0',
      updateInterval: 86400000, // 24小时
      sources: ['黄帝内经', '中医基础理论', '中医诊断学'],
      caching: {
        enabled: true,
        ttl: 3600000, // 1小时
        maxSize: 1000
      },
      ...config
    };
    this.initializeKnowledgeBase();
  }

  /**
   * 初始化知识库
   */
  private async initializeKnowledgeBase(): Promise<void> {
    try {
      await this.loadBasicConcepts();
      await this.loadDiagnosisPatterns();
      await this.loadSyndromeInfo();
      await this.loadConstitutionTypes();
      console.log('TCM知识库初始化完成');
    } catch (error) {
      console.error('TCM知识库初始化失败:', error);
      throw error;
    }
  }

  /**
   * 加载基础概念
   */
  private async loadBasicConcepts(): Promise<void> {
    // 五脏六腑
    this.addConcept({
      id: "heart",
      name: '心',
      category: 'organ',
      description: '主血脉，藏神',
      properties: {
        element: '火',
        emotion: '喜',
        season: '夏',
        color: '红',
        taste: '苦'
      },
      relationships: [
        {
          type: "related_to",
          target: 'small_intestine',
          strength: 1.0,
          description: '心与小肠相表里'
        }
      ],
      sources: ['黄帝内经'],
      confidence: 1.0
    });

    this.addConcept({
      id: "liver",
      name: '肝',
      category: 'organ',
      description: '主疏泄，藏血',
      properties: {
        element: '木',
        emotion: '怒',
        season: '春',
        color: '青',
        taste: '酸'
      },
      relationships: [
        {
          type: "related_to",
          target: 'gallbladder',
          strength: 1.0,
          description: '肝与胆相表里'
        }
      ],
      sources: ['黄帝内经'],
      confidence: 1.0
    });

    this.addConcept({
      id: "spleen",
      name: '脾',
      category: 'organ',
      description: '主运化，统血',
      properties: {
        element: '土',
        emotion: '思',
        season: '长夏',
        color: '黄',
        taste: '甘'
      },
      relationships: [
        {
          type: "related_to",
          target: 'stomach',
          strength: 1.0,
          description: '脾与胃相表里'
        }
      ],
      sources: ['黄帝内经'],
      confidence: 1.0
    });

    // 气血津液
    this.addConcept({
      id: "qi",
      name: '气',
      category: 'substance',
      description: '人体生命活动的基本物质',
      properties: {
        types: ["元气", "宗气", "营气", "卫气"],
        functions: ["推动", "温煦", "防御", "固摄", "气化"]
      },
      relationships: [
        {
          type: "related_to",
          target: 'blood',
          strength: 0.9,
          description: '气血相互依存'
        }
      ],
      sources: ['中医基础理论'],
      confidence: 1.0
    });

    this.addConcept({
      id: "blood",
      name: '血',
      category: 'substance',
      description: '营养和滋润全身的红色液体',
      properties: {
        functions: ["营养", "滋润", "化神"],
        sources: ["脾胃化生", "肾精化血"]
      },
      relationships: [
        {
          type: "related_to",
          target: 'qi',
          strength: 0.9,
          description: '气为血之帅，血为气之母'
        }
      ],
      sources: ['中医基础理论'],
      confidence: 1.0
    });

    // 阴阳五行
    this.addConcept({
      id: "yin_yang",
      name: '阴阳',
      category: 'theory',
      description: '对立统一的哲学概念',
      properties: {
        yin: ["静", "寒", "下", "内", "暗"],
        yang: ["动", "热", "上", "外", "明"]
      },
      relationships: [],
      sources: ["易经", "黄帝内经"],
      confidence: 1.0
    });
  }

  /**
   * 加载诊断模式
   */
  private async loadDiagnosisPatterns(): Promise<void> {
    // 舌象模式
    this.addPattern({
      id: "red_tongue_yellow_coating",
      name: '舌红苔黄',
      category: 'tongue',
      symptoms: ["口干", "口苦", "烦躁"],
      signs: ["舌质红", "苔黄厚"],
      syndromes: ["热证", "实证"],
      treatments: ["清热泻火"],
      confidence: 0.9
    });

    this.addPattern({
      id: "pale_tongue_white_coating",
      name: '舌淡苔白',
      category: 'tongue',
      symptoms: ["乏力", "畏寒", "食欲不振"],
      signs: ["舌质淡", "苔白薄"],
      syndromes: ["虚证", "寒证"],
      treatments: ["温阳补气"],
      confidence: 0.8
    });

    // 面色模式
    this.addPattern({
      id: "pale_complexion",
      name: '面色苍白',
      category: 'face',
      symptoms: ["乏力", "气短", "心悸"],
      signs: ["面色无华", "唇色淡"],
      syndromes: ["气血不足", "阳虚"],
      treatments: ["补气养血"],
      confidence: 0.8
    });

    this.addPattern({
      id: "red_complexion",
      name: '面色潮红',
      category: 'face',
      symptoms: ["烦躁", "口渴", "便秘"],
      signs: ["面红目赤", "唇红"],
      syndromes: ["热证", "实火"],
      treatments: ["清热降火"],
      confidence: 0.85
    });
  }

  /**
   * 加载证候信息
   */
  private async loadSyndromeInfo(): Promise<void> {
    this.addSyndrome({
      id: "qi_deficiency",
      name: '气虚证',
      category: 'deficiency',
      description: '脏腑功能衰退所表现的证候',
      mainSymptoms: ["乏力", "气短", "懒言", "自汗"],
      secondarySymptoms: ["面色萎黄", "食欲不振", "大便溏薄"],
      tongueFeatures: ["舌淡", "苔白"],
      pulseFeatures: ["脉弱", "脉虚"],
      treatments: [
        {
          type: 'herbal',
          name: '四君子汤',
          description: '补气健脾的基础方剂',
          dosage: '每日一剂',
          duration: '2-4周',
          contraindications: ['实热证'],
          sideEffects: ['偶有胃胀']
        }
      ],
      prognosis: '调理得当，预后良好'
    });

    this.addSyndrome({
      id: "blood_deficiency",
      name: '血虚证',
      category: 'deficiency',
      description: '血液不足或血液濡养功能减退',
      mainSymptoms: ["面色无华", "头晕", "心悸", "失眠"],
      secondarySymptoms: ["爪甲色淡", "月经量少", "肌肤干燥"],
      tongueFeatures: ["舌淡", "苔少"],
      pulseFeatures: ["脉细", "脉弱"],
      treatments: [
        {
          type: 'herbal',
          name: '四物汤',
          description: '补血调经的经典方剂',
          dosage: '每日一剂',
          duration: '3-6周',
          contraindications: ['湿热证'],
          sideEffects: ['偶有腹胀']
        }
      ],
      prognosis: '坚持调理，可逐渐改善'
    });

    this.addSyndrome({
      id: "spleen_qi_deficiency",
      name: '脾气虚证',
      category: 'organ_deficiency',
      description: '脾脏运化功能减退的证候',
      mainSymptoms: ["食欲不振", "腹胀", "便溏", "乏力"],
      secondarySymptoms: ["面色萎黄", "肢体困重", "浮肿"],
      tongueFeatures: ["舌淡胖", "苔白腻"],
      pulseFeatures: ["脉缓弱"],
      treatments: [
        {
          type: 'herbal',
          name: '参苓白术散',
          description: '健脾益气，渗湿止泻',
          dosage: '每日两次',
          duration: '4-8周',
          contraindications: ['阴虚火旺'],
          sideEffects: ['极少']
        }
      ],
      prognosis: '配合饮食调理，效果显著'
    });
  }

  /**
   * 加载体质类型
   */
  private async loadConstitutionTypes(): Promise<void> {
    this.addConstitution({
      id: "qi_deficiency_constitution",
      name: '气虚质',
      description: '以气虚为主要特征的体质类型',
      characteristics: {
        physical: ["肌肉松软", "容易疲劳", "语声低弱", "容易出汗"],
        psychological: ["性格内向", "情绪不稳", "适应能力差"],
        pathological: ["易感冒", "内脏下垂", "消化不良"]
      },
      recommendations: {
        diet: ["山药", "大枣", "蜂蜜", "鸡肉", "避免生冷"],
        exercise: ["太极拳", "八段锦", "散步", "避免剧烈运动"],
        lifestyle: ["规律作息", "避免过劳", "保持心情愉快"],
        prevention: ["注意保暖", "预防感冒", "定期体检"]
      }
    });

    this.addConstitution({
      id: "yang_deficiency_constitution",
      name: '阳虚质',
      description: '以阳气不足为主要特征的体质类型',
      characteristics: {
        physical: ["畏寒怕冷", "手足不温", "精神不振", "面色苍白"],
        psychological: ["性格沉静", "反应较慢", "喜静恶动"],
        pathological: ["易腹泻", "小便清长", "性功能减退"]
      },
      recommendations: {
        diet: ["羊肉", "生姜", "肉桂", "核桃", "避免寒凉"],
        exercise: ["慢跑", "游泳", "瑜伽", "适度运动"],
        lifestyle: ["注意保暖", "避免熬夜", "温水洗浴"],
        prevention: ["春夏养阳", "避免贪凉", "适当进补"]
      }
    });

    this.addConstitution({
      id: "yin_deficiency_constitution",
      name: '阴虚质',
      description: '以阴液亏少为主要特征的体质类型',
      characteristics: {
        physical: ["形体偏瘦", "手足心热", "面色潮红", "眼干口燥"],
        psychological: ["性情急躁", "外向好动", "活泼"],
        pathological: ["易失眠", "大便干燥", "小便短赤"]
      },
      recommendations: {
        diet: ["银耳", "百合", "枸杞", "鸭肉", "避免辛辣"],
        exercise: ["太极拳", "瑜伽", "游泳", "避免大汗"],
        lifestyle: ["充足睡眠", "避免熬夜", "保持安静"],
        prevention: ["秋冬养阴", "避免过劳", "情志调节"]
      }
    });
  }

  /**
   * 添加概念
   */
  private addConcept(concept: TCMConcept): void {
    this.concepts.set(concept.id, concept);
  }

  /**
   * 添加诊断模式
   */
  private addPattern(pattern: DiagnosisPattern): void {
    this.patterns.set(pattern.id, pattern);
  }

  /**
   * 添加证候信息
   */
  private addSyndrome(syndrome: SyndromeInfo): void {
    this.syndromes.set(syndrome.id, syndrome);
  }

  /**
   * 添加体质类型
   */
  private addConstitution(constitution: ConstitutionType): void {
    this.constitutions.set(constitution.id, constitution);
  }

  /**
   * 获取概念
   */
  public getConcept(id: string): TCMConcept | undefined {
    return this.concepts.get(id);
  }

  /**
   * 获取所有概念
   */
  public getAllConcepts(category?: string): TCMConcept[] {
    const concepts = Array.from(this.concepts.values());
    if (category) {
      return concepts.filter(concept => concept.category === category);
    }
    return concepts;
  }

  /**
   * 获取诊断模式
   */
  public getPattern(id: string): DiagnosisPattern | undefined {
    return this.patterns.get(id);
  }

  /**
   * 获取所有诊断模式
   */
  public getAllPatterns(category?: string): DiagnosisPattern[] {
    const patterns = Array.from(this.patterns.values());
    if (category) {
      return patterns.filter(pattern => pattern.category === category);
    }
    return patterns;
  }

  /**
   * 获取证候信息
   */
  public getSyndrome(id: string): SyndromeInfo | undefined {
    return this.syndromes.get(id);
  }

  /**
   * 获取所有证候
   */
  public getAllSyndromes(category?: string): SyndromeInfo[] {
    const syndromes = Array.from(this.syndromes.values());
    if (category) {
      return syndromes.filter(syndrome => syndrome.category === category);
    }
    return syndromes;
  }

  /**
   * 获取体质类型
   */
  public getConstitution(id: string): ConstitutionType | undefined {
    return this.constitutions.get(id);
  }

  /**
   * 获取所有体质类型
   */
  public getAllConstitutions(): ConstitutionType[] {
    return Array.from(this.constitutions.values());
  }

  /**
   * 获取相关概念
   */
  public getRelatedConcepts(conceptId: string): TCMConcept[] {
    const concept = this.getConcept(conceptId);
    if (!concept) return [];

    const relatedIds = concept.relationships.map(rel => rel.target);
    return relatedIds
      .map(id => this.getConcept(id))
      .filter(c => c !== undefined) as TCMConcept[];
  }

  /**
   * 搜索概念
   */
  public searchConcepts(query: string): TCMConcept[] {
    const lowerQuery = query.toLowerCase();
    return Array.from(this.concepts.values()).filter(concept =>
      concept.name.toLowerCase().includes(lowerQuery) ||
      concept.description.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * 获取治疗建议
   */
  public getTreatmentRecommendations(syndromeIds: string[]): TreatmentInfo[] {
    const treatments: TreatmentInfo[] = [];
    
    syndromeIds.forEach(id => {
      const syndrome = this.getSyndrome(id);
      if (syndrome) {
        treatments.push(...syndrome.treatments);
      }
    });

    return treatments;
  }

  /**
   * 验证知识库
   */
  public validateKnowledgeBase(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 检查概念关系的完整性
    this.concepts.forEach(concept => {
      concept.relationships.forEach(rel => {
        if (!this.concepts.has(rel.target)) {
          errors.push(`概念 ${concept.id} 引用了不存在的目标 ${rel.target}`);
        }
      });
    });

    // 检查证候的治疗信息
    this.syndromes.forEach(syndrome => {
      if (syndrome.treatments.length === 0) {
        errors.push(`证候 ${syndrome.id} 缺少治疗信息`);
      }
    });

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * 更新知识库
   */
  public async updateKnowledgeBase(): Promise<void> {
    try {
      // 这里可以实现从外部数据源更新知识库的逻辑
      console.log('知识库更新完成');
    } catch (error) {
      console.error('知识库更新失败:', error);
      throw error;
    }
  }

  /**
   * 获取统计信息
   */
  public getStatistics(): {
    concepts: number;
    patterns: number;
    syndromes: number;
    constitutions: number;
    version: string;
  } {
    return {
      concepts: this.concepts.size,
      patterns: this.patterns.size,
      syndromes: this.syndromes.size,
      constitutions: this.constitutions.size,
      version: this.config.version
    };
  }

  /**
   * 清理缓存
   */
  public clearCache(): void {
    this.cache.clear();
  }
}

export default TCMKnowledgeBase;