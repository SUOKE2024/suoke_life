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

      characteristics: [




      ],
      physicalTraits: {





      ;},
      psychologicalTraits: {



      ;},

      adaptationCapacity: {



      ;},
      healthMaintenance: {




      ;}
    });

    // 气虚质
    this.constitutionProfiles.set(ConstitutionType.QI_DEFICIENCY, {

      characteristics: [




      ],
      physicalTraits: {





      ;},
      psychologicalTraits: {



      ;},

      adaptationCapacity: {



      ;},
      healthMaintenance: {




      ;}
    });

    // 阳虚质
    this.constitutionProfiles.set(ConstitutionType.YANG_DEFICIENCY, {

      characteristics: [




      ],
      physicalTraits: {





      ;},
      psychologicalTraits: {



      ;},

      adaptationCapacity: {



      ;},
      healthMaintenance: {




      ;}
    });

    // 阴虚质
    this.constitutionProfiles.set(ConstitutionType.YIN_DEFICIENCY, {

      characteristics: [




      ],
      physicalTraits: {





      ;},
      psychologicalTraits: {



      ;},

      adaptationCapacity: {



      ;},
      healthMaintenance: {




      ;}
    });
  }

  /**
   * 初始化证候模式
   */
  private initializeSyndromePatterns(): void {
    // 气虚证
    this.syndromePatterns.set('qi_deficiency_syndrome', {



      mainSymptoms: [




      ],
      tongueManifestations: {


      ;},






    });

    // 血虚证
    this.syndromePatterns.set('blood_deficiency_syndrome', {



      mainSymptoms: [




      ],
      tongueManifestations: {


      ;},






    });
  }

  /**
   * 初始化中药数据库
   */
  private initializeHerbDatabase(): void {
    // 人参


      latinName: 'Panax ginseng';







      dosage: '3-9g';



      modernPharmacology: {



      ;}
    });

    // 当归


      latinName: 'Angelica sinensis';







      dosage: '6-12g';

      incompatibilities: [];

      modernPharmacology: {



      ;}
    });
  }

  /**
   * 初始化方剂数据库
   */
  private initializeFormulaDatabase(): void {
    // 四君子汤




      composition: [




      ],



      modifications: [
        {


          removal: []
        ;},
        {


          removal: []
        ;}
      ],



    });

    // 四物汤




      composition: [




      ],



      modifications: [
        {


          removal: []
        ;},
        {


          removal: []
        ;}
      ],



    });
  }

  /**
   * 初始化经络系统
   */
  private initializeMeridianSystem(): void {
    // 手太阴肺经


      abbreviation: 'LU';






      keyPoints: [



      ]
    ;});
  }

  /**
   * 初始化脏腑系统
   */
  private initializeOrganSystem(): void {
    // 心













    });

    // 肝













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
          score: matchResult.score;
          matchedSymptoms: matchResult.matchedSymptoms;
          confidence: matchResult.confidence
        ;});
      }
    }

    // 按分数排序
    patternMatches.sort((a, b) => b.score - a.score);

    const recommendations: TreatmentRecommendation[] = [];
    
    if (patternMatches.length > 0) {
      const primaryPattern = patternMatches[0];
      
      // 添加治疗原则建议
      recommendations.push({
        type: 'principle';

        content: primaryPattern.pattern.treatmentPrinciple;
        priority: 'high'
      ;});

      // 添加方剂建议
      primaryPattern.pattern.recommendedFormulas.forEach(formula => {
        recommendations.push({
          type: 'formula';

          content: formula;
          priority: 'high'
        ;});
      });

      // 添加禁忌症
      if (primaryPattern.pattern.contraindications.length > 0) {
        recommendations.push({
          type: 'contraindication';


          priority: 'medium'
        ;});
      }
    }

    return {
      primaryPattern: patternMatches.length > 0 ? patternMatches[0] : null;
      alternativePatterns: patternMatches.slice(1, 4), // 取前3个备选
      confidence: patternMatches.length > 0 ? patternMatches[0].confidence : 0;
      recommendations,
      timestamp: new Date()
    ;};
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
          symptomName: patternSymptom.name;
          userSeverity: userSymptom.severity;
          patternWeight: patternSymptom.weight;
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
    ;};
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
