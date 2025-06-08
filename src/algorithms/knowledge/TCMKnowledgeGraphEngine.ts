import { EventEmitter } from 'events;';
/**
* * 中医知识图谱推理引擎
* 实现基于知识图谱的中医辨证论治推理
// 基础数据结构定义
export interface TCMEntity {
  id: string;
  name: string;
  type: EntityType;
  properties: Record<string, any>;
  aliases?: string[];
  description?: string;
  confidence?: number;
}
export interface TCMRelation {
  id: string;
  source: string;
  target: string;
  type: RelationType;
  properties: Record<string, any>;
  weight?: number;
  confidence?: number;
}
export interface TCMTriple {
  subject: TCMEntity;
  predicate: TCMRelation;
  object: TCMEntity;
}
export enum EntityType {SYMPTOM =
symptom",           // 症状"
SYNDROME = syndrome",         // 证候"
DISEASE = "disease,           // 疾病"
HERB = "herb",                 // 中药
FORMULA = formula", "           // 方剂"
ACUPOINT = "acupoint,         // 穴位"
MERIDIAN = "meridian",         // 经络
ORGAN = organ", "               // 脏腑"
CONSTITUTION = "constitution, // 体质"
TREATMENT = "treatment",       // 治法
PRINCIPLE = principle"        // 治则"
}
export enum RelationType {
  // 症状-证候关系
INDICATES = "indicates,           // 症状指示证候"
MANIFESTS_AS = "manifests_as",     // 证候表现为症状
  // 证候-疾病关系
BELONGS_TO = belongs_to", "         // 证候属于疾病"
CAUSES = "causes,                 // 导致"
  // 治疗关系
TREATS = "treats",                 // 治疗
PREVENTS = prevents", "             // 预防"
ALLEVIATES = "alleviates,         // 缓解"
  // 方药关系
CONTAINS = "contains",             // 包含
COMBINES_WITH = combines_with", "   // 配伍"
ANTAGONIZES = "antagonizes,       // 拮抗"
  // 经络穴位关系
LOCATED_ON = "located_on",         // 位于
CONNECTS_TO = connects_to", "       // 连接"
  // 脏腑关系
NOURISHES = "nourishes,           // 滋养"
RESTRAINS = "restrains",           // 制约
GENERATES = generates", "           // 生成"
  // 相似性关系
SIMILAR_TO = "similar_to,         // 相似"
OPPOSITE_TO = "opposite_to",       // 相反
  // 时间关系
PRECEDES = precedes", "             // 先于"
FOLLOWS = "follows                // 后于"
}
export interface DiagnosisInput {
  symptoms: string[];
  tongueAnalysis?: {color: string;
  coating: string;
    texture: string;
  moisture: number;
};
  pulseAnalysis?: {
    type: string,
  rate: number;
    rhythm: string,
  strength: number;
  };
  patientInfo?: {
    age: number,
  gender: string;
    constitution?: string;
    medicalHistory?: string[];
  };
  additionalInfo?: Record<string, any>;
}
export interface DiagnosisResult {
  primarySyndrome: TCMEntity;
  secondarySyndromes: TCMEntity[];
  confidence: number;
  reasoning: ReasoningPath[];
  recommendations: TreatmentRecommendation[];
  differentialDiagnosis: DifferentialDiagnosis[];
}
export interface ReasoningPath {
  step: number;
  description: string;
  entities: TCMEntity[];
  relations: TCMRelation[];
  confidence: number;
  reasoning: string;
}
export interface TreatmentRecommendation {
  type: "formula" | herb" | "acupuncture | "lifestyle";
  entity: TCMEntity;
  dosage?: string;
  duration?: string;
  frequency?: string;
  notes?: string;
  confidence: number;
}
export interface DifferentialDiagnosis {
  syndrome: TCMEntity;
  probability: number;
  supportingEvidence: string[];
  contradictingEvidence: string[];
}
export interface KnowledgeGraphConfig {
  enableFuzzyMatching: boolean;
  confidenceThreshold: number;
  maxReasoningDepth: number;
  enableTemporalReasoning: boolean;
  enableUncertaintyHandling: boolean;
  weightingStrategy: uniform" | "frequency | "expert" | ml;
}
/**
* * 中医知识图谱推理引擎
export class TCMKnowledgeGraphEngine extends EventEmitter {private entities: Map<string, TCMEntity> = new Map();
  private relations: Map<string, TCMRelation> = new Map();
  private entityIndex: Map<EntityType, Set<string>> = new Map();
  private relationIndex: Map<RelationType, Set<string>> = new Map();
  private config: KnowledgeGraphConfig;
  private reasoningCache: Map<string, DiagnosisResult> = new Map();
  constructor(config: Partial<KnowledgeGraphConfig> = {}) {
    super();
    this.config = {
      enableFuzzyMatching: true,
      confidenceThreshold: 0.6,
      maxReasoningDepth: 5,
      enableTemporalReasoning: true,
      enableUncertaintyHandling: true,
      weightingStrategy: "expert,"
      ...config;
    };
    this.initializeKnowledgeBase();
    this.buildIndices();
  }
  /**
* * 初始化知识库
  private initializeKnowledgeBase(): void {
    // 加载基础中医知识
this.loadBasicEntities();
    this.loadBasicRelations();
    this.loadSyndromePatterns();
    this.loadTreatmentProtocols();
  }
  /**
* * 加载基础实体
  private loadBasicEntities(): void {
    // 常见症状
const symptoms = [;
      {
      id: "sym_fatigue",
      name: 乏力", aliases: ["疲劳, "倦怠"] },
      { id: sym_headache", name: "头痛, aliases: ["头疼"] },
      { id: sym_dizziness", name: "头晕, aliases: ["眩晕"] },
      { id: sym_insomnia", name: "失眠, aliases: ["不寐"] },
      { id: sym_palpitation", name: "心悸, aliases: ["心慌"] },
      { id: sym_shortness_breath", name: "气短, aliases: ["呼吸短促"] },
      { id: sym_cold_limbs", name: "四肢厥冷, aliases: ["手足冰冷"] },
      { id: sym_night_sweats", name: "盗汗, aliases: ["夜间出汗"] },
      { id: sym_dry_mouth", name: "口干, aliases: ["口燥"] },
      { id: sym_poor_appetite", name: "食欲不振, aliases: ["纳差"] };
    ];
    symptoms.forEach(symptom => {})
      this.addEntity({
        id: symptom.id,
        name: symptom.name,
        type: EntityType.SYMPTOM,
        aliases: symptom.aliases,
        properties: {}
      });
    });
    // 常见证候
const syndromes = [;
      { id: syn_qi_deficiency", name: "气虚证, description: "气的推动、温煦、防御、固摄功能减退" },
      { id: syn_blood_stasis", name: "血瘀证, description: "血液运行不畅或瘀血内阻" },
      { id: syn_damp_heat", name: "湿热证, description: "湿邪与热邪相合" },
      { id: syn_yin_deficiency", name: "阴虚证, description: "阴液亏虚，虚热内生" },
      { id: syn_yang_deficiency", name: "阳虚证, description: "阳气虚衰，温煦功能减退" },
      { id: syn_liver_qi_stagnation", name: "肝气郁结, description: "肝失疏泄，气机郁滞" },
      { id: syn_spleen_deficiency", name: "脾虚证, description: "脾气虚弱，运化失职" },
      { id: syn_kidney_deficiency", name: "肾虚证, description: "肾精、肾气、肾阴、肾阳虚衰" };
    ];
    syndromes.forEach(syndrome => {})
      this.addEntity({
        id: syndrome.id,
        name: syndrome.name,
        type: EntityType.SYNDROME,
        description: syndrome.description,
        properties: {}
      });
    });
    // 常用方剂
const formulas = [;
      { id: form_sijunzi", name: "四君子汤, description: "补气健脾的基础方" },
      { id: form_liuwei_dihuang", name: "六味地黄丸, description: "滋补肾阴的代表方" },
      { id: form_xiaoyao", name: "逍遥散, description: "疏肝健脾的经典方" },
      { id: form_buyang_huanwu", name: "补阳还五汤, description: "补气活血的名方" },
      { id: form_ganlu_xiaodu", name: "甘露消毒丹, description: "清热利湿的良方" };
    ];
    formulas.forEach(formula => {})
      this.addEntity({
        id: formula.id,
        name: formula.name,
        type: EntityType.FORMULA,
        description: formula.description,
        properties: {}
      });
    });
    // 脏腑
const organs = [;
      { id: org_heart", name: "心, description: "主血脉，藏神" },
      { id: org_liver", name: "肝, description: "主疏泄，藏血" },
      { id: org_spleen", name: "脾, description: "主运化，统血" },
      { id: org_lung", name: "肺, description: "主气，司呼吸" },
      { id: org_kidney", name: "肾, description: "藏精，主水" };
    ];
    organs.forEach(organ => {})
      this.addEntity({
        id: organ.id,
        name: organ.name,
        type: EntityType.ORGAN,
        description: organ.description,
        properties: {}
      });
    });
  }
  /**
* * 加载基础关系
  private loadBasicRelations(): void {
    // 症状-证候关系
const symptomSyndromeRelations = [;
      { symptom: sym_fatigue", syndrome: "syn_qi_deficiency, weight: 0.8 },
      {
      symptom: "sym_shortness_breath",
      syndrome: syn_qi_deficiency", weight: 0.7 },"
      { symptom: "sym_poor_appetite, syndrome: "syn_spleen_deficiency", weight: 0.8 },"
      { symptom: sym_cold_limbs", syndrome: "syn_yang_deficiency, weight: 0.9 },
      {
      symptom: "sym_night_sweats",
      syndrome: syn_yin_deficiency", weight: 0.8 },"
      { symptom: "sym_dry_mouth, syndrome: "syn_yin_deficiency", weight: 0.7 },"
      { symptom: sym_palpitation", syndrome: "syn_liver_qi_stagnation, weight: 0.6 },
      {
      symptom: "sym_insomnia",
      syndrome: syn_liver_qi_stagnation", weight: 0.7 };"
    ];
    symptomSyndromeRelations.forEach(rel => {})
      this.addRelation({
        id: `rel_${rel.symptom}_${rel.syndrome}`,
        source: rel.symptom,
        target: rel.syndrome,
        type: RelationType.INDICATES,
        weight: rel.weight,
        properties: {}
      });
    });
    // 证候-方剂关系
const syndromeFormulaRelations = [;
      { syndrome: "syn_qi_deficiency, formula: "form_sijunzi", weight: 0.9 },"
      { syndrome: syn_spleen_deficiency", formula: "form_sijunzi, weight: 0.8 },
      {
      syndrome: "syn_yin_deficiency",
      formula: form_liuwei_dihuang", weight: 0.9 },"
      { syndrome: "syn_kidney_deficiency, formula: "form_liuwei_dihuang", weight: 0.8 },"
      { syndrome: syn_liver_qi_stagnation", formula: "form_xiaoyao, weight: 0.9 },
      {
      syndrome: "syn_blood_stasis",
      formula: form_buyang_huanwu", weight: 0.8 },"
      { syndrome: "syn_damp_heat, formula: "form_ganlu_xiaodu", weight: 0.9 };"
    ];
    syndromeFormulaRelations.forEach(rel => {})
      this.addRelation({
        id: `rel_${rel.syndrome}_${rel.formula}`,
        source: rel.formula,
        target: rel.syndrome,
        type: RelationType.TREATS,
        weight: rel.weight,
        properties: {}
      });
    });
    // 脏腑相关关系
const organRelations = [;
      { source: org_heart", target: "org_kidney, type: RelationType.NOURISHES, weight: 0.8 },
      {
      source: "org_liver",
      target: org_spleen", type: RelationType.RESTRAINS, weight: 0.7 },"
      { source: "org_spleen, target: "org_lung", type: RelationType.GENERATES, weight: 0.8 },"
      { source: org_lung", target: "org_kidney, type: RelationType.NOURISHES, weight: 0.7 },
      {
      source: "org_kidney",
      target: org_liver", type: RelationType.NOURISHES, weight: 0.8 };"
    ];
    organRelations.forEach(rel => {})
      this.addRelation({
        id: `rel_${rel.source}_${rel.target}_${rel.type}`,
        source: rel.source,
        target: rel.target,
        type: rel.type,
        weight: rel.weight,
        properties: {}
      });
    });
  }
  /**
* * 加载证候模式
  private loadSyndromePatterns(): void {
    // 定义证候的典型症状组合模式
const patterns = [;
      {
      syndrome: "syn_qi_deficiency,",
      requiredSymptoms: ["sym_fatigue", sym_shortness_breath"],"
        optionalSymptoms: ["sym_poor_appetite, "sym_dizziness"],"
        tonguePattern: { color: 淡白", coating: "薄白 },
        pulsePattern: {
      type: "弱脉",
      characteristics: [weak",deep] }
      },
      {
      syndrome: "syn_yin_deficiency",
      requiredSymptoms: [sym_night_sweats",sym_dry_mouth],
        optionalSymptoms: ["sym_insomnia", sym_dizziness"],"
        tonguePattern: { color: "红, coating: "少苔" },"
        pulsePattern: { type: 细数脉", characteristics: ["rapid, "weak"] }
      },
      {
        syndrome: syn_blood_stasis",
        requiredSymptoms: ["sym_palpitation],"
        optionalSymptoms: ["sym_headache"],
        tonguePattern: { color: 紫暗", coating: "薄白 },
        pulsePattern: {
      type: "涩脉",
      characteristics: [rough",irregular] }
      };
    ];
    patterns.forEach(pattern => {})
      const syndrome = this.entities.get(pattern.syndrome);
      if (syndrome) {
        syndrome.properties.pattern = pattern;
      }
    });
  }
  /**
* * 加载治疗方案
  private loadTreatmentProtocols(): void {
    // 为每个证候定义标准治疗方案
const protocols = [;
      {
      syndrome: "syn_qi_deficiency",
      treatments: [
          { type: formula", entity: "form_sijunzi, priority: 1 },
          {
      type: "lifestyle",
      recommendation: 适当运动，避免过劳", priority: 2 }"
        ]
      },
      {
      syndrome: "syn_yin_deficiency,",
      treatments: [
          {
      type: "formula",
      entity: form_liuwei_dihuang", priority: 1 },"
          { type: "lifestyle, recommendation: "避免熬夜，多食滋阴食物", priority: 2 }"
        ]
      };
    ];
    protocols.forEach(protocol => {})
      const syndrome = this.entities.get(protocol.syndrome);
      if (syndrome) {
        syndrome.properties.treatments = protocol.treatments;
      }
    });
  }
  /**
* * 构建索引
  private buildIndices(): void {
    // 构建实体类型索引
for (const entityType of Object.values(EntityType)) {
      this.entityIndex.set(entityType, new Set());
    }
    this.entities.forEach(((entity, id) => {}))
      const typeSet = this.entityIndex.get(entity.type);
      if (typeSet) {
        typeSet.add(id);
      }
    });
    // 构建关系类型索引
for (const relationType of Object.values(RelationType)) {
      this.relationIndex.set(relationType, new Set());
    }
    this.relations.forEach(((relation, id) => {}))
      const typeSet = this.relationIndex.get(relation.type);
      if (typeSet) {
        typeSet.add(id);
      }
    });
  }
  /**
* * 添加实体
  public addEntity(entity: TCMEntity): void {
    this.entities.set(entity.id, entity);
    const typeSet = this.entityIndex.get(entity.type);
    if (typeSet) {
      typeSet.add(entity.id);
    } else {
      this.entityIndex.set(entity.type, new Set([entity.id]));
    }
    this.emit(entityAdded", entity);"
  }
  /**
* * 添加关系
  public addRelation(relation: TCMRelation): void {
    this.relations.set(relation.id, relation);
    const typeSet = this.relationIndex.get(relation.type);
    if (typeSet) {
      typeSet.add(relation.id);
    } else {
      this.relationIndex.set(relation.type, new Set([relation.id]));
    }
    this.emit("relationAdded, relation);"
  }
  /**
* * 查找实体
  public findEntity(query: string, type?: EntityType): TCMEntity[] {
    const results: TCMEntity[] = [];
    const searchEntities = type ?;
      Array.from(this.entityIndex.get(type) || []).map(id => this.entities.get(id)!).filter(Boolean) :;
      Array.from(this.entities.values());
    for (const entity of searchEntities) {
      if (this.matchesQuery(entity, query)) {
        results.push(entity);
      }
    }
    return results.sort(a, b) => (b.confidence || 0) - (a.confidence || 0));
  }
  /**
* * 查询匹配
  private matchesQuery(entity: TCMEntity, query: string): boolean {
    const normalizedQuery = query.toLowerCase().trim();
    // 精确匹配名称
if (entity.name.toLowerCase() === normalizedQuery) {
      entity.confidence = 1.0;
      return true;
    }
    // 匹配别名
if (entity.aliases) {
      for (const alias of entity.aliases) {
        if (alias.toLowerCase() === normalizedQuery) {
          entity.confidence = 0.9;
          return true;
        }
      }
    }
    // 模糊匹配
if (this.config.enableFuzzyMatching) {
      const similarity = this.calculateSimilarity(entity.name, query);
      if (similarity > 0.7) {
        entity.confidence = similarity;
        return true;
      }
      // 检查别名的模糊匹配
if (entity.aliases) {
        for (const alias of entity.aliases) {
          const aliasSimilarity = this.calculateSimilarity(alias, query);
          if (aliasSimilarity > 0.7) {
            entity.confidence = aliasSimilarity * 0.9;
            return true;
          }
        }
      }
    }
    return false;
  }
  /**
* * 计算字符串相似度
  private calculateSimilarity(str1: string, str2: string): number {
    const len1 = str1.length;
    const len2 = str2.length;
    if (len1 === 0) return len2 === 0 ? 1 : 0;
    if (len2 === 0) return 0;
    const matrix: number[][] = [];
    for (let i = 0; i <= len1; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= len2; j++) {
      matrix[0][j] = j;
    }
    for (let i = 1; i <= len1; i++) {
      for (let j = 1; j <= len2; j++) {
        const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[i][j] = Math.min()
          matrix[i - 1][j] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j - 1] + cost;
        );
      }
    }
    const maxLen = Math.max(len1, len2);
    return 1 - matrix[len1][len2] /     maxLen;
  }
  /**
* * 获取相关实体
  public getRelatedEntities(entityId: string, relationType?: RelationType): TCMEntity[] {
    const related: TCMEntity[] = [];
    const searchRelations = relationType ?;
      Array.from(this.relationIndex.get(relationType) || []).map(id => this.relations.get(id)!).filter(Boolean) :;
      Array.from(this.relations.values());
    for (const relation of searchRelations) {
      if (relation.source === entityId) {
        const target = this.entities.get(relation.target);
        if (target) {
          target.confidence = relation.weight || 0.5;
          related.push(target);
        }
      } else if (relation.target === entityId) {
        const source = this.entities.get(relation.source);
        if (source) {
          source.confidence = relation.weight || 0.5;
          related.push(source);
        }
      }
    }
    return related.sort(a, b) => (b.confidence || 0) - (a.confidence || 0));
  }
  /**
* * 主要诊断推理方法
  public async diagnose(input: DiagnosisInput): Promise<DiagnosisResult> {
    const cacheKey = this.generateCacheKey(input);
    // 检查缓存
if (this.reasoningCache.has(cacheKey)) {
      return this.reasoningCache.get(cacheKey)!;
    }
    this.emit("diagnosisStarted", input);
    try {
      // 1. 症状识别和标准化
const recognizedSymptoms = await this.recognizeSymptoms(input.symptoms);
      // 2. 多模态信息融合
const fusedEvidence = this.fuseMultimodalEvidence(input, recognizedSymptoms);
      // 3. 证候推理
const syndromeHypotheses = await this.generateSyndromeHypotheses(fusedEvidence);
      // 4. 推理路径构建
const reasoningPaths = this.buildReasoningPaths(fusedEvidence, syndromeHypotheses);
      // 5. 置信度计算
const rankedSyndromes = this.calculateSyndromeConfidence(syndromeHypotheses, reasoningPaths);
      // 6. 治疗建议生成
const recommendations = await this.generateTreatmentRecommendations(rankedSyndromes);
      // 7. 鉴别诊断
const differentialDiagnosis = this.performDifferentialDiagnosis(rankedSyndromes, fusedEvidence);
      const result: DiagnosisResult = {primarySyndrome: rankedSyndromes[0],
        secondarySyndromes: rankedSyndromes.slice(1, 3),
        confidence: rankedSyndromes[0]?.confidence || 0,
        reasoning: reasoningPaths,
        recommendations,
        differentialDiagnosis;
      };
      // 缓存结果
this.reasoningCache.set(cacheKey, result);
      this.emit(diagnosisCompleted", result);"
      return result;
    } catch (error) {
      this.emit("diagnosisError, error);"
      throw error;
    }
  }
  /**
* * 症状识别
  private async recognizeSymptoms(symptoms: string[]): Promise<TCMEntity[]> {
    const recognized: TCMEntity[] = [];
    for (const symptom of symptoms) {
      const matches = this.findEntity(symptom, EntityType.SYMPTOM);
      if (matches.length > 0) {
        recognized.push(matches[0]);
      } else {
        // 创建未知症状实体
const unknownSymptom: TCMEntity = {id: `unknown_${Date.now()}_${Math.random()}`,
          name: symptom,
          type: EntityType.SYMPTOM,
          properties: { unknown: true },
          confidence: 0.3;
        };
        recognized.push(unknownSymptom);
      }
    }
    return recognized;
  }
  /**
* * 多模态证据融合
  private fuseMultimodalEvidence(input: DiagnosisInput, symptoms: TCMEntity[]): any {
    const evidence = {symptoms,
      tongueEvidence: null as any,
      pulseEvidence: null as any,
      patientContext: input.patientInfo,
      fusionScore: 0;
    };
    // 舌诊证据处理
if (input.tongueAnalysis) {
      evidence.tongueEvidence = this.processTongueEvidence(input.tongueAnalysis);
    }
    // 脉诊证据处理
if (input.pulseAnalysis) {
      evidence.pulseEvidence = this.processPulseEvidence(input.pulseAnalysis);
    }
    // 计算融合评分
evidence.fusionScore = this.calculateFusionScore(evidence);
    return evidence;
  }
  /**
* * 处理舌诊证据
  private processTongueEvidence(tongueAnalysis: any): any {
    return {color: tongueAnalysis.color,coating: tongueAnalysis.coating,texture: tongueAnalysis.texture,moisture: tongueAnalysis.moisture,syndromeIndicators: this.mapTongueToSyndromes(tongueAnalysis);
    };
  }
  /**
* * 处理脉诊证据
  private processPulseEvidence(pulseAnalysis: any): any {
    return {type: pulseAnalysis.type,rate: pulseAnalysis.rate,rhythm: pulseAnalysis.rhythm,strength: pulseAnalysis.strength,syndromeIndicators: this.mapPulseToSyndromes(pulseAnalysis);
    };
  }
  /**
* * 舌象到证候的映射
  private mapTongueToSyndromes(tongueAnalysis: any): Array<{syndrome: string, confidence: number}> {
    const mappings = [;
      {
      color: "淡白", "
      coating: 薄白", syndrome: "syn_qi_deficiency, confidence: 0.8 },
      {
      color: "红", "
      coating: 少苔", syndrome: "syn_yin_deficiency, confidence: 0.8 },
      {
      color: "紫暗", "
      coating: 薄白", syndrome: "syn_blood_stasis, confidence: 0.9 },
      {
      color: "红", "
      coating: 黄腻", syndrome: "syn_damp_heat, confidence: 0.8 };
    ];
    return mappings;
      .filter(mapping => {})
        mapping.color === tongueAnalysis.color &&
        mapping.coating === tongueAnalysis.coating;
      );
      .map(mapping => ({
        syndrome: mapping.syndrome,
        confidence: mapping.confidence;
      }));
  }
  /**
* * 脉象到证候的映射
  private mapPulseToSyndromes(pulseAnalysis: any): Array<{syndrome: string, confidence: number}> {
    const mappings = [;
      {
      type: "弱脉",
      syndrome: syn_qi_deficiency", confidence: 0.8 },"
      { type: "细数脉, syndrome: "syn_yin_deficiency", confidence: 0.8 },"
      { type: 涩脉", syndrome: "syn_blood_stasis, confidence: 0.9 },
      {
      type: "滑数脉",
      syndrome: syn_damp_heat", confidence: 0.8 };"
    ];
    return mappings;
      .filter(mapping => mapping.type === pulseAnalysis.type);
      .map(mapping => ({
        syndrome: mapping.syndrome,
        confidence: mapping.confidence;
      }));
  }
  /**
* * 计算融合评分
  private calculateFusionScore(evidence: any): number {
    let score = 0;
    let factors = 0;
    if (evidence.symptoms.length > 0) {
      score += evidence.symptoms.length * 0.3;
      factors++;
    }
    if (evidence.tongueEvidence) {
      score += 0.4;
      factors++;
    }
    if (evidence.pulseEvidence) {
      score += 0.3;
      factors++;
    }
    return factors > 0 ? score /     factors : 0;
  }
  /**
* * 生成证候假设
  private async generateSyndromeHypotheses(evidence: any): Promise<TCMEntity[]> {
    const hypotheses = new Map<string, TCMEntity>();
    // 基于症状的证候推理
for (const symptom of evidence.symptoms) {
      const relatedSyndromes = this.getRelatedEntities(symptom.id, RelationType.INDICATES);
      for (const syndrome of relatedSyndromes) {
        if (!hypotheses.has(syndrome.id)) {
          hypotheses.set(syndrome.id, { ...syndrome, confidence: 0 });
        }
        const current = hypotheses.get(syndrome.id)!;
        current.confidence = Math.max(current.confidence, syndrome.confidence || 0);
      }
    }
    // 基于舌诊的证候推理
if (evidence.tongueEvidence?.syndromeIndicators) {
      for (const indicator of evidence.tongueEvidence.syndromeIndicators) {
        const syndrome = this.entities.get(indicator.syndrome);
        if (syndrome) {
          if (!hypotheses.has(syndrome.id)) {
            hypotheses.set(syndrome.id, { ...syndrome, confidence: 0 });
          }
          const current = hypotheses.get(syndrome.id)!;
          current.confidence = Math.max(current.confidence, indicator.confidence);
        }
      }
    }
    // 基于脉诊的证候推理
if (evidence.pulseEvidence?.syndromeIndicators) {
      for (const indicator of evidence.pulseEvidence.syndromeIndicators) {
        const syndrome = this.entities.get(indicator.syndrome);
        if (syndrome) {
          if (!hypotheses.has(syndrome.id)) {
            hypotheses.set(syndrome.id, { ...syndrome, confidence: 0 });
          }
          const current = hypotheses.get(syndrome.id)!;
          current.confidence = Math.max(current.confidence, indicator.confidence);
        }
      }
    }
    return Array.from(hypotheses.values());
      .filter(syndrome => (syndrome.confidence || 0) >= this.config.confidenceThreshold);
      .sort(a, b) => (b.confidence || 0) - (a.confidence || 0));
  }
  /**
* * 构建推理路径
  private buildReasoningPaths(evidence: any, syndromes: TCMEntity[]): ReasoningPath[] {
    const paths: ReasoningPath[] = [];
    syndromes.forEach(((syndrome, index) => {}))
      const path: ReasoningPath = {step: index + 1,
        description: `推理${syndrome.name}`,
        entities: [syndrome],
        relations: [],
        confidence: syndrome.confidence || 0,
        reasoning: this.generateReasoningExplanation(syndrome, evidence);
      };
      // 找到支持该证候的症状和关系
for (const symptom of evidence.symptoms) {
        const relations = Array.from(this.relations.values()).filter(;)
          rel => rel.source === symptom.id &&
                rel.target === syndrome.id &&
                rel.type === RelationType.INDICATES;
        );
        if (relations.length > 0) {
          path.entities.push(symptom);
          path.relations.push(...relations);
        }
      }
      paths.push(path);
    });
    return paths;
  }
  /**
* * 生成推理解释
  private generateReasoningExplanation(syndrome: TCMEntity, evidence: any): string {
    const explanations: string[] = [];
    // 症状支持
const supportingSymptoms = evidence.symptoms.filter(symptom: TCMEntity) => {}
      return Array.from(this.relations.values()).some(;)
        rel => rel.source === symptom.id &&;
              rel.target === syndrome.id &&;
              rel.type === RelationType.INDICATES;
      );
    });
    if (supportingSymptoms.length > 0) {
      explanations.push(`症状${supportingSymptoms.map(s: TCMEntity) => s.name).join("、)}支持${syndrome.name}的诊断`);"
    }
    // 舌诊支持
if (evidence.tongueEvidence?.syndromeIndicators) {
      const tongueSupport = evidence.tongueEvidence.syndromeIndicators.find(;)
        (indicator: any) => indicator.syndrome === syndrome.id;
      );
      if (tongueSupport) {
        explanations.push(`舌象表现（${evidence.tongueEvidence.color}舌${evidence.tongueEvidence.coating}苔）符合${syndrome.name}特征`);
      }
    }
    // 脉诊支持
if (evidence.pulseEvidence?.syndromeIndicators) {
      const pulseSupport = evidence.pulseEvidence.syndromeIndicators.find(;)
        (indicator: any) => indicator.syndrome === syndrome.id;
      );
      if (pulseSupport) {
        explanations.push(`脉象（${evidence.pulseEvidence.type}）提示${syndrome.name}`);
      }
    }
    return explanations.join("；") || `基于综合分析推断为${syndrome.name}`;
  }
  /**
* * 计算证候置信度
  private calculateSyndromeConfidence(syndromes: TCMEntity[], paths: ReasoningPath[]): TCMEntity[] {
    return syndromes.map((syndrome, index) => {};)
      const path = paths[index];
      let confidence = syndrome.confidence || 0;
      // 基于证据数量调整置信度
const evidenceCount = path.entities.length - 1; // 减去证候本身;
const evidenceBonus = Math.min(evidenceCount * 0.1, 0.3);
      confidence = Math.min(confidence + evidenceBonus, 1.0);
      // 基于关系权重调整
const avgRelationWeight = path.relations.length > 0 ?;
        path.relations.reduce(sum, rel) => sum + (rel.weight || 0.5), 0) /     path.relations.length :;
        0.5;
      confidence = confidence * (0.7 + avgRelationWeight * 0.3);
      return { ...syndrome, confidence };
    }).sort(a, b) => (b.confidence || 0) - (a.confidence || 0));
  }
  /**
* * 生成治疗建议
  private async generateTreatmentRecommendations(syndromes: TCMEntity[]): Promise<TreatmentRecommendation[]> {
    const recommendations: TreatmentRecommendation[] = [];
    for (const syndrome of syndromes.slice(0, 2)) { // 只为前两个证候生成建议
      // 查找治疗该证候的方剂
const treatmentFormulas = this.getRelatedEntities(syndrome.id, RelationType.TREATS);
      for (const formula of treatmentFormulas.slice(0, 2)) { // 每个证候最多2个方剂
recommendations.push({
          type: formula", "
          entity: formula,
          confidence: (syndrome.confidence || 0) * (formula.confidence || 0),
          notes: `针对${syndrome.name}的经典方剂`
        });
      }
      // 添加生活方式建议
const lifestyleAdvice = this.generateLifestyleAdvice(syndrome);
      if (lifestyleAdvice) {
        recommendations.push(lifestyleAdvice);
      }
    }
    return recommendations.sort(a, b) => b.confidence - a.confidence);
  }
  /**
* * 生成生活方式建议
  private generateLifestyleAdvice(syndrome: TCMEntity): TreatmentRecommendation | null {
    const adviceMap: Record<string, string> = {"syn_qi_deficiency: "适当运动，避免过度劳累，规律作息",
      syn_yin_deficiency": "避免熬夜，多食滋阴润燥食物，保持心情平和,
      "syn_blood_stasis": 适当活动，避免久坐，注意保暖",syn_damp_heat: "饮食清淡，避免辛辣油腻，保持环境通风""
    };
    const advice = adviceMap[syndrome.id];
    if (advice) {
      return {type: lifestyle",;
        entity: {id: `lifestyle_${syndrome.id}`,name: "生活调理,", "type: EntityType.TREATMENT,properties: { advice };
        },confidence: (syndrome.confidence || 0) * 0.8,notes: advice;
      };
    }
    return null;
  }
  /**
* * 执行鉴别诊断
  private performDifferentialDiagnosis(syndromes: TCMEntity[], evidence: any): DifferentialDiagnosis[] {
    return syndromes.map(syndrome => {};)
      const supportingEvidence: string[] = [];
      const contradictingEvidence: string[] = [];
      // 分析支持和反对的证据
for (const symptom of evidence.symptoms) {
        const hasSupport = Array.from(this.relations.values()).some(;)
          rel => rel.source === symptom.id &&
                rel.target === syndrome.id &&
                rel.type === RelationType.INDICATES;
        );
        if (hasSupport) {
          supportingEvidence.push(`症状：${symptom.name}`);
        }
      }
      // 舌诊证据
if (evidence.tongueEvidence?.syndromeIndicators) {
        const tongueSupport = evidence.tongueEvidence.syndromeIndicators.find(;)
          (indicator: any) => indicator.syndrome === syndrome.id;
        );
        if (tongueSupport) {
          supportingEvidence.push(`舌象：${evidence.tongueEvidence.color}舌${evidence.tongueEvidence.coating}苔`);
        }
      }
      // 脉诊证据
if (evidence.pulseEvidence?.syndromeIndicators) {
        const pulseSupport = evidence.pulseEvidence.syndromeIndicators.find(;)
          (indicator: any) => indicator.syndrome === syndrome.id;
        );
        if (pulseSupport) {
          supportingEvidence.push(`脉象：${evidence.pulseEvidence.type}`);
        }
      }
      return {syndrome,probability: syndrome.confidence || 0,supportingEvidence,contradictingEvidence;
      };
    });
  }
  /**
* * 生成缓存键
  private generateCacheKey(input: DiagnosisInput): string {
    return JSON.stringify({symptoms: input.symptoms.sort(),tongue: input.tongueAnalysis,pulse: input.pulseAnalysis,patient: input.patientInfo;)
    });
  }
  /**
* * 清除缓存
  public clearCache(): void {
    this.reasoningCache.clear();
  }
  /**
* * 获取统计信息
  public getStatistics(): any {
    return {entities: {total: this.entities.size,byType: Object.fromEntries(;)
          Array.from(this.entityIndex.entries()).map(([type, ids]) => [type, ids.size]);
        );
      },relations: {total: this.relations.size,byType: Object.fromEntries(;)
          Array.from(this.relationIndex.entries()).map(([type, ids]) => [type, ids.size]);
        );
      },cache: {size: this.reasoningCache.size;
      }
    };
  }
  /**
* * 导出知识图谱
  public exportKnowledgeGraph(): any {
    return {entities: Array.from(this.entities.values()),relations: Array.from(this.relations.values()),metadata: {exportTime: new Date().toISOString(),version: "1.0.0",config: this.config;
      }
    };
  }
  /**
* * 导入知识图谱
  public importKnowledgeGraph(data: any): void {
    // 清空现有数据
this.entities.clear();
    this.relations.clear();
    this.entityIndex.clear();
    this.relationIndex.clear();
    // 导入实体
for (const entity of data.entities) {
      this.addEntity(entity);
    }
    // 导入关系
for (const relation of data.relations) {
      this.addRelation(relation);
    }
    this.emit(knowledgeGraphImported", data.metadata);"
  }
}  */
