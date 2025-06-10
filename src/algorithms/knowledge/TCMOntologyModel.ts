/**
 * 中医本体模型
 * 提供中医理论的结构化表示和推理能力
 * @author 索克生活技术团队
 * @version 1.0.0
 */

// 体质类型枚举
export enum ConstitutionType {
  BALANCED = 'balanced',
  QI_DEFICIENCY = 'qi_deficiency',
  YANG_DEFICIENCY = 'yang_deficiency',
  YIN_DEFICIENCY = 'yin_deficiency',
  PHLEGM_DAMPNESS = 'phlegm_dampness',
  DAMP_HEAT = 'damp_heat',
  BLOOD_STASIS = 'blood_stasis',
  QI_STAGNATION = 'qi_stagnation',
  SPECIAL_DIATHESIS = 'special_diathesis'
}

/**
 * 中医本体模型类
 */
export class TCMOntologyModel {
  private syndromePatterns: Map<string, SyndromePattern> = new Map();
  private constitutionProfiles: Map<ConstitutionType, ConstitutionProfile> = new Map();
  private herbDatabase: Map<string, HerbProfile> = new Map();
  private formulaDatabase: Map<string, FormulaProfile> = new Map();
  private meridianSystem: Map<string, MeridianProfile> = new Map();
  private organSystem: Map<string, OrganProfile> = new Map();

  constructor() {
    this.initializeOntology();
  }

  /**
   * 初始化本体模型
   */
  private initializeOntology(): void {
    this.initializeConstitutionProfiles();
    this.initializeSyndromePatterns();
    this.initializeHerbDatabase();
    this.initializeFormulaDatabase();
    this.initializeMeridianSystem();
    this.initializeOrganSystem();
  }

  /**
   * 初始化体质档案
   */
  private initializeConstitutionProfiles(): void {
    // 平和质
    this.constitutionProfiles.set(ConstitutionType.BALANCED, {
      name: '平和质',
      characteristics: [
        '体形匀称健壮',
        '面色润泽，精力充沛',
        '睡眠良好',
        '食欲正常'
      ],
      physicalTraits: {
        complexion: '红润有光泽',
        bodyType: '匀称',
        energy: '充沛',
        sleep: '良好',
        appetite: '正常'
      },
      psychologicalTraits: {
        personality: '性格随和开朗',
        emotion: '情绪稳定',
        stress: '适应能力强'
      },
      susceptibleDiseases: ['感冒', '外感'],
      adaptationCapacity: {
        climate: '适应性强',
        season: '四季皆宜',
        environment: '环境适应性好'
      },
      healthMaintenance: {
        diet: '饮食有节',
        exercise: '适度运动',
        lifestyle: '起居有常',
        emotion: '调畅情志'
      }
    });

    // 气虚质
    this.constitutionProfiles.set(ConstitutionType.QI_DEFICIENCY, {
      name: '气虚质',
      characteristics: [
        '元气不足',
        '疲乏无力',
        '气短懒言，容易出汗',
        '舌淡苔白'
      ],
      physicalTraits: {
        complexion: '面色偏黄或淡白',
        bodyType: '肌肉松软',
        energy: '精神不振',
        sleep: '容易疲劳',
        appetite: '食欲不振'
      },
      psychologicalTraits: {
        personality: '性格内向',
        emotion: '情绪不稳',
        stress: '不耐受风、寒、暑、湿邪'
      },
      susceptibleDiseases: ['感冒', '内脏下垂', '虚劳'],
      adaptationCapacity: {
        climate: '不耐受风寒',
        season: '春夏较好',
        environment: '易感外邪'
      },
      healthMaintenance: {
        diet: '益气健脾',
        exercise: '柔和运动',
        lifestyle: '避风寒',
        emotion: '调养心神'
      }
    });

    // 阳虚质
    this.constitutionProfiles.set(ConstitutionType.YANG_DEFICIENCY, {
      name: '阳虚质',
      characteristics: [
        '阳气不足',
        '畏寒怕冷',
        '手足不温',
        '精神不振'
      ],
      physicalTraits: {
        complexion: '面色苍白',
        bodyType: '形体白胖',
        energy: '精神不振',
        sleep: '嗜睡',
        appetite: '食欲不振'
      },
      psychologicalTraits: {
        personality: '性格沉静内向',
        emotion: '情绪不稳',
        stress: '不耐受寒邪'
      },
      susceptibleDiseases: ['泄泻', '阳痿', '水肿'],
      adaptationCapacity: {
        climate: '不耐受寒湿',
        season: '夏季较好',
        environment: '喜暖怕凉'
      },
      healthMaintenance: {
        diet: '温阳散寒',
        exercise: '慢跑、散步',
        lifestyle: '春夏养阳',
        emotion: '调畅情志'
      }
    });

    // 阴虚质
    this.constitutionProfiles.set(ConstitutionType.YIN_DEFICIENCY, {
      name: '阴虚质',
      characteristics: [
        '阴液亏少',
        '口燥咽干',
        '手足心热',
        '潮热盗汗'
      ],
      physicalTraits: {
        complexion: '面色潮红',
        bodyType: '体形偏瘦',
        energy: '容易疲劳',
        sleep: '失眠多梦',
        appetite: '食欲正常'
      },
      psychologicalTraits: {
        personality: '性情急躁',
        emotion: '情绪波动',
        stress: '不耐受暑热燥邪'
      },
      susceptibleDiseases: ['失眠', '便秘', '更年期综合征'],
      adaptationCapacity: {
        climate: '不耐受暑热',
        season: '秋冬较好',
        environment: '喜润恶燥'
      },
      healthMaintenance: {
        diet: '滋阴润燥',
        exercise: '太极拳、瑜伽',
        lifestyle: '秋冬养阴',
        emotion: '静神少虑'
      }
    });
  }

  /**
   * 初始化证候模式
   */
  private initializeSyndromePatterns(): void {
    // 气虚证
    this.syndromePatterns.set('qi_deficiency_syndrome', {
      name: '气虚证',
      category: '虚证',
      pathogenesis: '脏腑功能衰退，气的推动、温煦、防御、固摄和气化功能减退',
      mainSymptoms: [
        { name: '神疲乏力', weight: 0.9, required: true },
        { name: '气短懒言', weight: 0.8, required: true },
        { name: '动则汗出', weight: 0.7, required: false },
        { name: '食欲不振', weight: 0.6, required: false }
      ],
      tongueManifestations: {
        tongueBody: '舌淡',
        tongueCoating: '苔白'
      },
      pulseManifestations: ['脉弱', '脉虚'],
      treatmentPrinciple: '补气',
      recommendedFormulas: ['四君子汤', '补中益气汤'],
      contraindications: ['实热证', '邪实证'],
      prognosis: '调理得当，预后良好',
      differentialDiagnosis: ['血虚证', '阳虚证']
    });

    // 血虚证
    this.syndromePatterns.set('blood_deficiency_syndrome', {
      name: '血虚证',
      category: '虚证',
      pathogenesis: '血液不足或血的濡养功能减退',
      mainSymptoms: [
        { name: '面色无华', weight: 0.9, required: true },
        { name: '唇甲色淡', weight: 0.8, required: true },
        { name: '头晕眼花', weight: 0.7, required: false },
        { name: '心悸失眠', weight: 0.6, required: false }
      ],
      tongueManifestations: {
        tongueBody: '舌淡',
        tongueCoating: '苔少'
      },
      pulseManifestations: ['脉细', '脉弱'],
      treatmentPrinciple: '补血',
      recommendedFormulas: ['四物汤', '当归补血汤'],
      contraindications: ['湿热证', '痰湿证'],
      prognosis: '坚持调理，可逐渐改善',
      differentialDiagnosis: ['气虚证', '阴虚证']
    });
  }

  /**
   * 初始化中药数据库
   */
  private initializeHerbDatabase(): void {
    // 人参
    this.herbDatabase.set('人参', {
      name: '人参',
      latinName: 'Panax ginseng',
      category: '补虚药',
      subCategory: '补气药',
      nature: '微温',
      flavor: ['甘', '微苦'],
      meridians: ['脾', '肺', '心', '肾'],
      functions: ['大补元气', '复脉固脱', '补脾益肺', '生津养血', '安神益智'],
      indications: ['气虚欲脱', '脾肺气虚', '热病气津两伤', '心神不安'],
      dosage: '3-9g',
      contraindications: ['实热证', '湿热证'],
      incompatibilities: ['藜芦'],
      processing: ['生晒参', '红参', '白参'],
      modernPharmacology: {
        activeComponents: ['人参皂苷', '人参多糖', '人参多肽'],
        pharmacologicalEffects: ['增强免疫', '抗疲劳', '调节血糖'],
        clinicalApplications: ['免疫功能低下', '慢性疲劳综合征', '糖尿病']
      }
    });

    // 当归
    this.herbDatabase.set('当归', {
      name: '当归',
      latinName: 'Angelica sinensis',
      category: '补虚药',
      subCategory: '补血药',
      nature: '温',
      flavor: ['甘', '辛'],
      meridians: ['肝', '心', '脾'],
      functions: ['补血活血', '调经止痛', '润肠通便'],
      indications: ['血虚萎黄', '月经不调', '经闭痛经', '虚寒腹痛'],
      dosage: '6-12g',
      contraindications: ['湿盛中满', '大便溏泄'],
      incompatibilities: [],
      processing: ['当归头', '当归身', '当归尾'],
      modernPharmacology: {
        activeComponents: ['阿魏酸', '当归多糖', '挥发油'],
        pharmacologicalEffects: ['补血', '活血', '调节免疫'],
        clinicalApplications: ['贫血', '月经不调', '血栓性疾病']
      }
    });
  }

  /**
   * 初始化方剂数据库
   */
  private initializeFormulaDatabase(): void {
    // 四君子汤
    this.formulaDatabase.set('四君子汤', {
      name: '四君子汤',
      category: '补益剂',
      subCategory: '补气剂',
      composition: [
        { herb: '人参', dosage: '9g', role: '君药' },
        { herb: '白术', dosage: '9g', role: '臣药' },
        { herb: '茯苓', dosage: '9g', role: '佐药' },
        { herb: '甘草', dosage: '6g', role: '使药' }
      ],
      functions: ['益气健脾'],
      indications: ['脾胃气虚证'],
      contraindications: ['邪实证'],
      modifications: [
        {
          condition: '兼有气滞',
          addition: ['陈皮', '木香'],
          removal: []
        },
        {
          condition: '兼有血虚',
          addition: ['当归', '白芍'],
          removal: []
        }
      ],
      preparation: '水煎服',
      dosage: '每日1剂，分2次服',
      modernApplications: ['慢性胃炎', '功能性消化不良', '免疫功能低下']
    });

    // 四物汤
    this.formulaDatabase.set('四物汤', {
      name: '四物汤',
      category: '补益剂',
      subCategory: '补血剂',
      composition: [
        { herb: '当归', dosage: '10g', role: '君药' },
        { herb: '川芎', dosage: '8g', role: '臣药' },
        { herb: '白芍', dosage: '12g', role: '佐药' },
        { herb: '熟地黄', dosage: '12g', role: '佐药' }
      ],
      functions: ['补血调血'],
      indications: ['营血虚滞证'],
      contraindications: ['脾胃虚弱', '痰湿内盛'],
      modifications: [
        {
          condition: '血虚有热',
          addition: ['黄芩', '地骨皮'],
          removal: []
        },
        {
          condition: '血虚有寒',
          addition: ['桂枝', '干姜'],
          removal: []
        }
      ],
      preparation: '水煎服',
      dosage: '每日1剂，分2次服',
      modernApplications: ['月经不调', '贫血', '产后血虚']
    });
  }

  /**
   * 初始化经络系统
   */
  private initializeMeridianSystem(): void {
    // 手太阴肺经
    this.meridianSystem.set('手太阴肺经', {
      name: '手太阴肺经',
      abbreviation: 'LU',
      type: '手三阴经',
      pairedOrgan: '大肠',
      flowDirection: '从胸走手',
      peakTime: '3-5时',
      mainFunctions: ['主气司呼吸', '通调水道', '朝百脉'],
      pathology: ['咳嗽', '气喘', '胸闷', '咽喉肿痛'],
      keyPoints: [
        { name: '中府', location: '胸外侧部，云门下1寸', functions: ['宣肺理气', '止咳平喘'] },
        { name: '尺泽', location: '肘横纹中，肱二头肌腱桡侧凹陷处', functions: ['清肺泻火', '降逆止咳'] },
        { name: '太渊', location: '腕掌侧横纹桡侧，桡动脉搏动处', functions: ['补肺益气', '通脉'] }
      ]
    });
  }

  /**
   * 初始化脏腑系统
   */
  private initializeOrganSystem(): void {
    // 心
    this.organSystem.set('心', {
      name: '心',
      category: '五脏',
      element: '火',
      season: '夏',
      emotion: '喜',
      tissue: '血脉',
      sensoryOrgan: '舌',
      fluid: '汗',
      mainFunctions: ['主血脉', '主神明'],
      physiologicalCharacteristics: ['心主血脉', '心藏神', '心开窍于舌', '心其华在面'],
      pathologicalManifestations: ['心悸', '胸痛', '失眠', '健忘', '神志异常'],
      commonSyndromes: ['心气虚', '心血虚', '心阳虚', '心火亢盛']
    });

    // 肝
    this.organSystem.set('肝', {
      name: '肝',
      category: '五脏',
      element: '木',
      season: '春',
      emotion: '怒',
      tissue: '筋',
      sensoryOrgan: '目',
      fluid: '泪',
      mainFunctions: ['主疏泄', '主藏血'],
      physiologicalCharacteristics: ['肝主疏泄', '肝藏血', '肝主筋', '肝开窍于目'],
      pathologicalManifestations: ['胁痛', '头痛', '眩晕', '情志异常', '月经不调'],
      commonSyndromes: ['肝气郁结', '肝火上炎', '肝阳上亢', '肝血虚']
    });
  }

  /**
   * 分析症状并返回证候模式
   */
  public analyzeSymptoms(symptoms: SymptomInput[]): PatternAnalysisResult {
    const patternMatches: PatternMatch[] = [];
    
    // 遍历所有证候模式进行匹配
    for (const [patternId, pattern] of this.syndromePatterns) {
      const matchResult = this.matchPattern(symptoms, pattern);
      if (matchResult.score > 0.3) { // 设置最低匹配阈值
        patternMatches.push({
          patternId,
          pattern,
          score: matchResult.score,
          matchedSymptoms: matchResult.matchedSymptoms,
          confidence: matchResult.confidence
        });
      }
    }

    // 按分数排序
    patternMatches.sort((a, b) => b.score - a.score);

    const recommendations: TreatmentRecommendation[] = [];
    
    if (patternMatches.length > 0) {
      const primaryPattern = patternMatches[0];
      
      // 添加治疗原则建议
      recommendations.push({
        type: 'principle',
        title: '治疗原则',
        content: primaryPattern.pattern.treatmentPrinciple,
        priority: 'high'
      });

      // 添加方剂建议
      primaryPattern.pattern.recommendedFormulas.forEach(formula => {
        recommendations.push({
          type: 'formula',
          title: '推荐方剂',
          content: formula,
          priority: 'high'
        });
      });

      // 添加禁忌症
      if (primaryPattern.pattern.contraindications.length > 0) {
        recommendations.push({
          type: 'contraindication',
          title: '注意事项',
          content: `禁忌：${primaryPattern.pattern.contraindications.join('、')}`,
          priority: 'medium'
        });
      }
    }

    return {
      primaryPattern: patternMatches.length > 0 ? patternMatches[0] : null,
      alternativePatterns: patternMatches.slice(1, 4), // 取前3个备选
      confidence: patternMatches.length > 0 ? patternMatches[0].confidence : 0,
      recommendations,
      timestamp: new Date()
    };
  }

  /**
   * 匹配单个证候模式
   */
  private matchPattern(symptoms: SymptomInput[], pattern: SyndromePattern): PatternMatchResult {
    const matchedSymptoms: MatchedSymptom[] = [];
    let totalScore = 0;
    let maxPossibleScore = 0;

    // 计算症状匹配度
    pattern.mainSymptoms.forEach(patternSymptom => {
      maxPossibleScore += patternSymptom.weight;
      
      const userSymptom = symptoms.find(s => s.name === patternSymptom.name);
      if (userSymptom) {
        const score = patternSymptom.weight * (userSymptom.severity / 10);
        totalScore += score;
        
        matchedSymptoms.push({
          symptomName: patternSymptom.name,
          userSeverity: userSymptom.severity,
          patternWeight: patternSymptom.weight,
          score
        });
      } else if (patternSymptom.required) {
        // 必需症状缺失，降低匹配度
        totalScore -= patternSymptom.weight * 0.5;
      }
    });

    const score = maxPossibleScore > 0 ? totalScore / maxPossibleScore : 0;
    const confidence = Math.min(score * (matchedSymptoms.length / pattern.mainSymptoms.length), 1);

    return {
      score: Math.max(score, 0),
      matchedSymptoms,
      confidence: Math.max(confidence, 0)
    };
  }

  /**
   * 获取体质档案
   */
  public getConstitutionProfile(constitution: ConstitutionType): ConstitutionProfile | null {
    return this.constitutionProfiles.get(constitution) || null;
  }

  /**
   * 获取证候模式
   */
  public getSyndromePattern(patternId: string): SyndromePattern | null {
    return this.syndromePatterns.get(patternId) || null;
  }

  /**
   * 获取中药信息
   */
  public getHerbProfile(herbName: string): HerbProfile | null {
    return this.herbDatabase.get(herbName) || null;
  }

  /**
   * 获取方剂信息
   */
  public getFormulaProfile(formulaName: string): FormulaProfile | null {
    return this.formulaDatabase.get(formulaName) || null;
  }

  /**
   * 获取经络信息
   */
  public getMeridianProfile(meridianName: string): MeridianProfile | null {
    return this.meridianSystem.get(meridianName) || null;
  }

  /**
   * 获取脏腑信息
   */
  public getOrganProfile(organName: string): OrganProfile | null {
    return this.organSystem.get(organName) || null;
  }
}

// 接口定义
export interface SyndromePattern {
  name: string;
  category: string;
  pathogenesis: string;
  mainSymptoms: PatternSymptom[];
  tongueManifestations: TongueManifestations;
  pulseManifestations: string[];
  treatmentPrinciple: string;
  recommendedFormulas: string[];
  contraindications: string[];
  prognosis: string;
  differentialDiagnosis: string[];
}

export interface PatternSymptom {
  name: string;
  weight: number;
  required: boolean;
}

export interface TongueManifestations {
  tongueBody: string;
  tongueCoating: string;
}

export interface ConstitutionProfile {
  name: string;
  characteristics: string[];
  physicalTraits: PhysicalTraits;
  psychologicalTraits: PsychologicalTraits;
  susceptibleDiseases: string[];
  adaptationCapacity: AdaptationCapacity;
  healthMaintenance: HealthMaintenance;
}

export interface PhysicalTraits {
  complexion: string;
  bodyType: string;
  energy: string;
  sleep: string;
  appetite: string;
}

export interface PsychologicalTraits {
  personality: string;
  emotion: string;
  stress: string;
}

export interface AdaptationCapacity {
  climate: string;
  season: string;
  environment: string;
}

export interface HealthMaintenance {
  diet: string;
  exercise: string;
  lifestyle: string;
  emotion: string;
}

export interface HerbProfile {
  name: string;
  latinName: string;
  category: string;
  subCategory: string;
  nature: string;
  flavor: string[];
  meridians: string[];
  functions: string[];
  indications: string[];
  dosage: string;
  contraindications: string[];
  incompatibilities: string[];
  processing: string[];
  modernPharmacology: ModernPharmacology;
}

export interface ModernPharmacology {
  activeComponents: string[];
  pharmacologicalEffects: string[];
  clinicalApplications: string[];
}

export interface FormulaProfile {
  name: string;
  category: string;
  subCategory: string;
  composition: FormulaComponent[];
  functions: string[];
  indications: string[];
  contraindications: string[];
  modifications: FormulaModification[];
  preparation: string;
  dosage: string;
  modernApplications: string[];
}

export interface FormulaComponent {
  herb: string;
  dosage: string;
  role: string;
}

export interface FormulaModification {
  condition: string;
  addition: string[];
  removal: string[];
}

export interface MeridianProfile {
  name: string;
  abbreviation: string;
  type: string;
  pairedOrgan: string;
  flowDirection: string;
  peakTime: string;
  mainFunctions: string[];
  pathology: string[];
  keyPoints: AcupointProfile[];
}

export interface AcupointProfile {
  name: string;
  location: string;
  functions: string[];
}

export interface OrganProfile {
  name: string;
  category: string;
  element: string;
  season: string;
  emotion: string;
  tissue: string;
  sensoryOrgan: string;
  fluid: string;
  mainFunctions: string[];
  physiologicalCharacteristics: string[];
  pathologicalManifestations: string[];
  commonSyndromes: string[];
}

export interface SymptomInput {
  name: string;
  severity: number;
  duration?: string;
  frequency?: string;
}

export interface PatternAnalysisResult {
  primaryPattern: PatternMatch | null;
  alternativePatterns: PatternMatch[];
  confidence: number;
  recommendations: TreatmentRecommendation[];
  timestamp: Date;
}

export interface PatternMatch {
  patternId: string;
  pattern: SyndromePattern;
  score: number;
  matchedSymptoms: MatchedSymptom[];
  confidence: number;
}

export interface PatternMatchResult {
  score: number;
  matchedSymptoms: MatchedSymptom[];
  confidence: number;
}

export interface MatchedSymptom {
  symptomName: string;
  userSeverity: number;
  patternWeight: number;
  score: number;
}

export interface TreatmentRecommendation {
  type: 'formula' | 'principle' | 'contraindication' | 'lifestyle';
  title: string;
  content: string;
  priority: 'high' | 'medium' | 'low';
}

export default TCMOntologyModel;
