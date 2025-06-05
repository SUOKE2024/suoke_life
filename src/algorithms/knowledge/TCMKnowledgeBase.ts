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
  type: "belongs_to" | "related_to" | "opposite_to" | "generates" | "restricts";
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
  type: "herbal" | "acupuncture" | "lifestyle" | "diet";
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

// 中医知识库类
export class TCMKnowledgeBase {
  private config: KnowledgeBaseConfig;
  private concepts: Map<string, TCMConcept> = new Map();
  private patterns: Map<string, DiagnosisPattern> = new Map();
  private syndromes: Map<string, SyndromeInfo> = new Map();
  private constitutions: Map<string, ConstitutionType> = new Map();
  private cache: Map<string, any> = new Map();

  constructor(config: KnowledgeBaseConfig) {
    this.config = config;
    this.initializeKnowledgeBase();
  }

  // 初始化知识库
  private async initializeKnowledgeBase(): Promise<void> {
    try {
      await this.loadBasicConcepts();
      await this.loadDiagnosisPatterns();
      await this.loadSyndromeInfo();
      await this.loadConstitutionTypes();
      // 记录加载完成
    } catch (error) {
      throw error;
    }
  }

  // 加载基础概念
  private async loadBasicConcepts(): Promise<void> {
    // 五脏六腑
    this.addConcept({
      id: "heart",
      name: "心",
      category: "organ",
      description: "主血脉，藏神",
      properties: {
        element: "火",
        emotion: "喜",
        season: "夏",
        color: "红",
        taste: "苦",
      },
      relationships: [
        {
          type: "related_to",
          target: "small_intestine",
          strength: 1.0,
          description: "心与小肠相表里",
        },
      ],
      sources: ["黄帝内经"],
      confidence: 1.0,
    });

    // 气血津液
    this.addConcept({
      id: "qi",
      name: "气",
      category: "substance",
      description: "人体生命活动的基本物质",
      properties: {
        types: ["元气", "宗气", "营气", "卫气"],
        functions: ["推动", "温煦", "防御", "固摄", "气化"],
      },
      relationships: [
        {
          type: "related_to",
          target: "blood",
          strength: 0.9,
          description: "气血相互依存",
        },
      ],
      sources: ["中医基础理论"],
      confidence: 1.0,
    });

    // 阴阳五行
    this.addConcept({
      id: "yin_yang",
      name: "阴阳",
      category: "theory",
      description: "对立统一的哲学概念",
      properties: {
        yin: ["静", "寒", "下", "内", "暗"],
        yang: ["动", "热", "上", "外", "明"],
      },
      relationships: [],
      sources: ["易经", "黄帝内经"],
      confidence: 1.0,
    });
  }

  // 加载诊断模式
  private async loadDiagnosisPatterns(): Promise<void> {
    // 舌象模式
    this.addPattern({
      id: "red_tongue_yellow_coating",
      name: "舌红苔黄",
      category: "tongue",
      symptoms: ["口干", "口苦", "烦躁"],
      signs: ["舌质红", "苔黄厚"],
      syndromes: ["热证", "实证"],
      treatments: ["清热泻火"],
      confidence: 0.9,
    });

    // 面色模式
    this.addPattern({
      id: "pale_complexion",
      name: "面色苍白",
      category: "face",
      symptoms: ["乏力", "气短", "心悸"],
      signs: ["面色无华", "唇色淡"],
      syndromes: ["气血不足", "阳虚"],
      treatments: ["补气养血"],
      confidence: 0.8,
    });
  }

  // 加载证候信息
  private async loadSyndromeInfo(): Promise<void> {
    this.addSyndrome({
      id: "qi_deficiency",
      name: "气虚证",
      category: "deficiency",
      description: "脏腑功能衰退所表现的证候",
      mainSymptoms: ["乏力", "气短", "懒言", "自汗"],
      secondarySymptoms: ["面色萎黄", "食欲不振", "大便溏薄"],
      tongueFeatures: ["舌淡", "苔白"],
      pulseFeatures: ["脉弱"],
      treatments: [
        {
          type: "herbal",
          name: "四君子汤",
          description: "补气健脾的基础方",
          dosage: "每日一剂",
          duration: "2-4周",
          contraindications: ["实热证"],
          sideEffects: ["偶有胃胀"],
        },
      ],
      prognosis: "调理得当，预后良好",
    });
  }

  // 加载体质类型
  private async loadConstitutionTypes(): Promise<void> {
    this.addConstitution({
      id: "balanced",
      name: "平和质",
      description: "阴阳气血调和的体质状态",
      characteristics: {
        physical: ["体形匀称", "面色红润", "精力充沛"],
        psychological: ["性格开朗", "情绪稳定", "适应力强"],
        pathological: ["不易生病", "病后恢复快"],
      },
      recommendations: {
        diet: ["饮食有节", "营养均衡", "不偏食"],
        exercise: ["适度运动", "动静结合"],
        lifestyle: ["作息规律", "劳逸结合"],
        prevention: ["顺应自然", "调畅情志"],
      },
    });
  }

  // 添加概念
  private addConcept(concept: TCMConcept): void {
    this.concepts.set(concept.id, concept);
  }

  // 添加模式
  private addPattern(pattern: DiagnosisPattern): void {
    this.patterns.set(pattern.id, pattern);
  }

  // 添加证候
  private addSyndrome(syndrome: SyndromeInfo): void {
    this.syndromes.set(syndrome.id, syndrome);
  }

  // 添加体质
  private addConstitution(constitution: ConstitutionType): void {
    this.constitutions.set(constitution.id, constitution);
  }

  // 获取概念
  public getConcept(id: string): TCMConcept | undefined {
    return this.concepts.get(id);
  }

  // 搜索概念
  public searchConcepts(query: string, category?: string): TCMConcept[] {
    const results: TCMConcept[] = [];
    for (const concept of this.concepts.values()) {
      if (category && concept.category !== category) {
        continue;
      }
      if (concept.name.includes(query) || concept.description.includes(query)) {
        results.push(concept);
      }
    }
    return results.sort((a, b) => b.confidence - a.confidence);
  }

  // 获取诊断模式
  public getPattern(id: string): DiagnosisPattern | undefined {
    return this.patterns.get(id);
  }

  // 搜索诊断模式
  public searchPatterns(
    symptoms: string[],
    category?: string
  ): DiagnosisPattern[] {
    const results: DiagnosisPattern[] = [];
    for (const pattern of this.patterns.values()) {
      if (category && pattern.category !== category) {
        continue;
      }
      const matchCount = symptoms.filter(
        (symptom) =>
          pattern.symptoms.includes(symptom) || pattern.signs.includes(symptom)
      ).length;
      if (matchCount > 0) {
        results.push(pattern);
      }
    }
    return results.sort((a, b) => b.confidence - a.confidence);
  }

  // 获取证候信息
  public getSyndrome(id: string): SyndromeInfo | undefined {
    return this.syndromes.get(id);
  }

  // 搜索证候
  public searchSyndromes(symptoms: string[]): SyndromeInfo[] {
    const results: SyndromeInfo[] = [];
    for (const syndrome of this.syndromes.values()) {
      const matchCount = symptoms.filter(
        (symptom) =>
          syndrome.mainSymptoms.includes(symptom) ||
          syndrome.secondarySymptoms.includes(symptom)
      ).length;
      if (matchCount > 0) {
        results.push(syndrome);
      }
    }
    return results;
  }

  // 获取体质类型
  public getConstitution(id: string): ConstitutionType | undefined {
    return this.constitutions.get(id);
  }

  // 获取所有体质类型
  public getAllConstitutions(): ConstitutionType[] {
    return Array.from(this.constitutions.values());
  }

  // 获取相关概念
  public getRelatedConcepts(conceptId: string): TCMConcept[] {
    const concept = this.getConcept(conceptId);
    if (!concept) {
      return [];
    }

    const related: TCMConcept[] = [];
    for (const relationship of concept.relationships) {
      const relatedConcept = this.getConcept(relationship.target);
      if (relatedConcept) {
        related.push(relatedConcept);
      }
    }
    return related.sort((a, b) => b.confidence - a.confidence);
  }

  // 获取治疗建议
  public getTreatmentRecommendations(syndromeIds: string[]): TreatmentInfo[] {
    const treatments: TreatmentInfo[] = [];
    for (const syndromeId of syndromeIds) {
      const syndrome = this.getSyndrome(syndromeId);
      if (syndrome) {
        treatments.push(...syndrome.treatments);
      }
    }
    return treatments;
  }

  // 验证知识库完整性
  public validateKnowledgeBase(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 检查概念关系的完整性
    for (const concept of this.concepts.values()) {
      for (const relationship of concept.relationships) {
        if (!this.concepts.has(relationship.target)) {
          errors.push(
            `概念 ${concept.name} 引用了不存在的目标概念: ${relationship.target}`
          );
        }
      }
    }

    // 检查模式中证候的存在性
    for (const pattern of this.patterns.values()) {
      for (const syndrome of pattern.syndromes) {
        if (!this.syndromes.has(syndrome)) {
          errors.push(`模式 ${pattern.name} 引用了不存在的证候: ${syndrome}`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  // 更新知识库
  public async updateKnowledgeBase(): Promise<void> {
    try {
      // 清空现有数据
      this.concepts.clear();
      this.patterns.clear();
      this.syndromes.clear();
      this.constitutions.clear();
      this.cache.clear();

      // 重新加载
      await this.initializeKnowledgeBase();
    } catch (error) {
      throw new Error(`知识库更新失败: ${error}`);
    }
  }

  // 获取统计信息
  public getStatistics(): object {
    return {
      concepts: this.concepts.size,
      patterns: this.patterns.size,
      syndromes: this.syndromes.size,
      constitutions: this.constitutions.size,
      cacheSize: this.cache.size,
      version: this.config.version,
      lastUpdate: new Date().toISOString(),
    };
  }
}

export default TCMKnowledgeBase;
