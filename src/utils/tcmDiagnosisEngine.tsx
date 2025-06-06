import { performanceMonitor } from './performanceMonitor';

import React from "react";

// 类型定义
export type ConstitutionType  = | "平和质" ;
  | "气虚质" ;
  | "阳虚质" ;
  | "阴虚质" ;
  | "痰湿质" ;
  | "湿热质" ;
  | "血瘀质" ;
  | "气郁质" ;
  | "特禀质";

export type SeasonType = "春季" | "夏季" | "秋季" | "冬季";

export interface Symptom {
  id: string;
  name: string;
  category: "inspection" | "auscultation" | "inquiry" | "palpation" | "calculation";
  severity: 1 | 2 | 3 | 4 | 5; // 1-轻微, 5-严重
  duration: number;
  frequency: "occasional" | "frequent" | "constant";
  location?: string;
  quality?: string;
  triggers?: string[];
  relievers?: string[];
}

export interface FiveDiagnosisData {
  inspection: InspectionData;
  auscultation: AuscultationData;
  inquiry: InquiryData;
  palpation: PalpationData;
  calculation: CalculationData;
  additional: AdditionalData;
}

export interface InspectionData {
  complexion: string; // 面色
  tongue: TongueData;
  spirit: string; // 神态
  body_build: string; // 体型
  posture: string; // 姿态
  movements: string; // 动作
}

export interface TongueData {
  body_color: string; // 舌体颜色
  coating_color: string; // 苔色
  coating_thickness: string; // 苔厚薄
  moisture: string; // 润燥
  texture: string; // 质地
  shape: string; // 形状
  size: string; // 大小
}

export interface AuscultationData {
  voice: string; // 声音
  breathing: string; // 呼吸
  cough: string; // 咳嗽
  speech: string; // 语言
  odor: string; // 气味
}

export interface InquiryData {
  chief_complaint: string; // 主诉
  present_illness: string; // 现病史
  past_history: string; // 既往史
  family_history: string; // 家族史
  personal_history: string; // 个人史
  symptoms: Symptom[];
  sleep: SleepData;
  appetite: AppetiteData;
  bowel_movement: BowelData;
  urination: UrinationData;
  menstruation?: MenstruationData;
}

export interface SleepData {
  quality: string;
  duration: number;
  difficulty_falling_asleep: boolean;
  frequent_awakening: boolean;
  early_awakening: boolean;
  dreams: string;
}

export interface AppetiteData {
  appetite: string;
  taste: string;
  thirst: string;
  food_preferences: string[];
  food_aversions: string[];
}

export interface BowelData {
  frequency: string;
  consistency: string;
  color: string;
  odor: string;
  difficulty: boolean;
}

export interface UrinationData {
  frequency: string;
  color: string;
  clarity: string;
  volume: string;
  urgency: boolean;
  pain: boolean;
}

export interface MenstruationData {
  cycle_length: number;
  duration: number;
  flow: string;
  color: string;
  clots: boolean;
  pain: boolean;
  regularity: string;
}

export interface PalpationData {
  pulse: PulseData;
  abdomen: AbdomenData;
  acupoints: AcupointData[];
}

export interface PulseData {
  rate: number; // 脉率
  rhythm: string; // 节律
  strength: string; // 力度
  depth: string; // 深浅
  width: string; // 宽窄
  length: string; // 长短
  quality: string; // 脉象
  position: "left" | "right" | "both";
}

export interface AbdomenData {
  tenderness: string[];
  masses: string[];
  distension: boolean;
  temperature: string;
  elasticity: string;
}

export interface AcupointData {
  point: string;
  tenderness: boolean;
  temperature: string;
  texture: string;
}

export interface CalculationData {
  birthDate: string; // 出生日期
  birthTime: string; // 出生时辰
  currentSeason: SeasonType; // 当前季节
  lunarCalendar: LunarData; // 农历信息
  fiveElements: FiveElementsData; // 五行分析
  yinYangBalance: YinYangData; // 阴阳平衡
  qiFlowAnalysis: QiFlowData; // 气机分析
}

export interface LunarData {
  year: string;
  month: string;
  day: string;
  hour: string;
  zodiac: string; // 生肖
  heavenlyStem: string; // 天干
  earthlyBranch: string; // 地支
}

export interface FiveElementsData {
  wood: number; // 木
  fire: number; // 火
  earth: number; // 土
  metal: number; // 金
  water: number; // 水
  dominantElement: string;
  deficientElement: string;
}

export interface YinYangData {
  yinScore: number;
  yangScore: number;
  balance: "yin_excess" | "yang_excess" | "balanced";
  tendency: string;
}

export interface QiFlowData {
  meridianFlow: Record<string, number>;
  blockages: string[];
  deficiencies: string[];
  recommendations: string[];
}

export interface AdditionalData {
  // Additional data fields would be defined here
}

export interface SyndromePattern {
  id: string;
  name: string;
  category: string;
  description: string;
  pathogenesis: string; // 病机
  main_symptoms: string[];
  secondary_symptoms: string[];
  tongue_pulse: string;
  confidence: number;
  severity: "mild" | "moderate" | "severe";
}

export interface TreatmentPrinciple {
  id: string;
  name: string;
  description: string;
  methods: string[];
  contraindications: string[];
}

export interface Prescription {
  id: string;
  name: string;
  category: string;
  composition: HerbComponent[];
  functions: string[];
  indications: string[];
  contraindications: string[];
  modifications: PrescriptionModification[];
  dosage: string;
  preparation: string;
  administration: string;
}

export interface HerbComponent {
  herb: string;
  dosage: string;
  unit: string;
  processing: string;
  function: string;
}

export interface PrescriptionModification {
  condition: string;
  modification: string;
  herbs_to_add?: HerbComponent[];
  herbs_to_remove?: string[];
  dosage_changes?: { herb: string; new_dosage: string }[];
}

export interface LifestyleRecommendation {
  category: "diet" | "exercise" | "emotion" | "sleep" | "environment";
  recommendations: string[];
  foods_to_eat: string[];
  foods_to_avoid: string[];
  exercises: string[];
  acupoint_massage: string[];
  seasonal_adjustments: Record<SeasonType, string[]>;
}

export interface TCMDiagnosisResult {
  patient_id: string;
  diagnosis_date: number;
  constitution: ConstitutionType;
  syndrome_patterns: SyndromePattern[];
  treatment_principles: TreatmentPrinciple[];
  prescriptions: Prescription[];
  lifestyle_recommendations: LifestyleRecommendation;
  follow_up_plan: FollowUpPlan;
  confidence: number;
  reasoning: string;
}

export interface FollowUpPlan {
  next_visit: number;
  monitoring_points: string[];
  warning_signs: string[];
  self_care_instructions: string[];
}

class ConstitutionIdentificationEngine {
  private static instance: ConstitutionIdentificationEngine;

  static getInstance(): ConstitutionIdentificationEngine {
    if (!ConstitutionIdentificationEngine.instance) {
      ConstitutionIdentificationEngine.instance = new ConstitutionIdentificationEngine();
    }
    return ConstitutionIdentificationEngine.instance;
  }

  identifyConstitution(
    inspectionData: InspectionData,
    inquiryData: InquiryData,
    palpationData: PalpationData
  ): { constitution: ConstitutionType; confidence: number; characteristics: string[] } {
    // 简化的体质辨识逻辑
    let constitution: ConstitutionType = "平和质";
    let confidence = 0.7;
    let characteristics: string[] = [];

    // 基于舌象判断
    if (inspectionData.tongue.body_color === "淡红") {
      constitution = "平和质";
      confidence = 0.8;
      characteristics = ["舌淡红", "苔薄白", "精神饱满"];
    } else if (inspectionData.tongue.body_color === "淡白") {
      constitution = "气虚质";
      confidence = 0.75;
      characteristics = ["舌淡白", "气短乏力", "容易疲劳"];
    } else if (inspectionData.tongue.body_color === "红") {
      constitution = "阴虚质";
      confidence = 0.8;
      characteristics = ["舌红少苔", "五心烦热", "口干咽燥"];
    }

    // 基于脉象调整
    if (palpationData.pulse.strength === "弱") {
      if (constitution === "平和质") {
        constitution = "气虚质";
        confidence = 0.7;
      }
    }

    return {constitution,confidence,characteristics: this.getConstitutionCharacteristics(constitution);
    };
  }

  private getConstitutionCharacteristics(constitution: ConstitutionType): string[] {
    const characteristics: Record<ConstitutionType, string[]> = {
      "平和质": ["体形匀称", "面色润泽", "精力充沛", "睡眠良好"],
      "气虚质": ["气短懒言", "容易疲劳", "自汗", "舌淡苔白"],
      "阳虚质": ["畏寒怕冷", "四肢不温", "精神不振", "舌淡胖"],
      "阴虚质": ["五心烦热", "口燥咽干", "舌红少苔", "脉细数"],
      "痰湿质": ["形体肥胖", "腹部肥满", "口黏腻", "舌胖苔腻"],
      "湿热质": ["面垢油腻", "口苦口干", "身重困倦", "舌红苔黄腻"],
      "血瘀质": ["肤色晦暗", "色素沉着", "易出血", "舌暗有瘀点"],
      "气郁质": ["神情抑郁", "情绪不稳", "胸胁胀满", "舌淡红"],
      "特禀质": ["过敏体质", "遗传缺陷", "胎传异常", "禀赋不足"]
    };
    return characteristics[constitution] || [];
  }
}

class SyndromePatternEngine {
  private static instance: SyndromePatternEngine;

  static getInstance(): SyndromePatternEngine {
    if (!SyndromePatternEngine.instance) {
      SyndromePatternEngine.instance = new SyndromePatternEngine();
    }
    return SyndromePatternEngine.instance;
  }

  identifyPatterns(
    inspectionData: InspectionData,
    auscultationData: AuscultationData,
    inquiryData: InquiryData,
    palpationData: PalpationData
  ): SyndromePattern[] {
    const patterns: SyndromePattern[] = [];

    // 检查气虚证
    if (this.checkQiDeficiency(inquiryData, palpationData)) {
      patterns.push({
        id: "qi_deficiency",
        name: "气虚证",
        category: "气血辨证",
        description: "脏腑功能衰退所表现的证候",
        pathogenesis: "元气不足，脏腑功能减退",
        main_symptoms: ["气短", "乏力", "自汗", "脉弱"],
        secondary_symptoms: ["声低", "懒言", "头晕", "食少"],
        tongue_pulse: "舌淡苔白，脉虚弱",
        confidence: 0.8,
        severity: "moderate"
      });
    }

    // 检查血瘀证
    if (this.checkBloodStasis(inspectionData, inquiryData, palpationData)) {
      patterns.push({
        id: "blood_stasis",
        name: "血瘀证",
        category: "气血辨证",
        description: "血液运行不畅所表现的证候",
        pathogenesis: "血行瘀滞，脉络不通",
        main_symptoms: ["疼痛", "肿块", "出血", "面色晦暗"],
        secondary_symptoms: ["舌暗", "瘀点", "脉涩", "肌肤甲错"],
        tongue_pulse: "舌质暗或有瘀点，脉涩",
        confidence: 0.75,
        severity: "moderate"
      });
    }

    return patterns.sort((a, b) => b.confidence - a.confidence);
  }

  private checkQiDeficiency(inquiryData: InquiryData, palpationData: PalpationData): boolean {
    let score = 0;

    // 检查症状
    const qiDeficiencySymptoms = ["气短", "乏力", "自汗", "懒言"];
    for (const symptom of inquiryData.symptoms) {
      if (qiDeficiencySymptoms.includes(symptom.name)) {
        score += symptom.severity;
      }
    }

    // 检查脉象
    if (palpationData.pulse.strength === "弱" || palpationData.pulse.quality === "虚") {
      score += 3;
    }

    return score >= 8;
  }

  private checkBloodStasis(
    inspectionData: InspectionData,
    inquiryData: InquiryData,
    palpationData: PalpationData
  ): boolean {
    let score = 0;

    // 检查面色
    if (inspectionData.complexion.includes("晦暗") || inspectionData.complexion.includes("紫暗")) {
      score += 3;
    }

    // 检查舌象
    if (inspectionData.tongue.body_color.includes("暗") || inspectionData.tongue.body_color.includes("紫")) {
      score += 3;
    }

    // 检查症状
    const bloodStasisSymptoms = ["疼痛", "肿块", "出血"];
    for (const symptom of inquiryData.symptoms) {
      if (bloodStasisSymptoms.some(s => symptom.name.includes(s))) {
        score += symptom.severity;
      }
    }

    // 检查脉象
    if (palpationData.pulse.quality === "涩" || palpationData.pulse.quality === "结") {
      score += 3;
    }

    return score >= 8;
  }
}

class PrescriptionEngine {
  private static instance: PrescriptionEngine;

  static getInstance(): PrescriptionEngine {
    if (!PrescriptionEngine.instance) {
      PrescriptionEngine.instance = new PrescriptionEngine();
    }
    return PrescriptionEngine.instance;
  }

  generatePrescriptions(patterns: SyndromePattern[]): Prescription[] {
    const prescriptions: Prescription[] = [];

    for (const pattern of patterns.slice(0, 2)) {
      if (pattern.name.includes("气虚")) {
        prescriptions.push(this.getQiTonicPrescription());
      } else if (pattern.name.includes("血瘀")) {
        prescriptions.push(this.getBloodActivatingPrescription());
      }
    }

    return prescriptions;
  }

  private getQiTonicPrescription(): Prescription {
    return {
      id: "si_jun_zi_tang",
      name: "四君子汤",category: "补益剂",composition: [;
        { herb: "人参", dosage: "9", unit: "g", processing: "生用", function: "大补元气" },{ herb: "白术", dosage: "9", unit: "g", processing: "炒用", function: "健脾燥湿" },{ herb: "茯苓", dosage: "9", unit: "g", processing: "生用", function: "健脾利湿" },{ herb: "甘草", dosage: "6", unit: "g", processing: "炙用", function: "调和诸药" };
      ],functions: ["益气健脾", "补中益气"],indications: ["脾胃气虚", "食少便溏", "气短乏力"],contraindications: ["阴虚火旺", "实热证"],modifications: [],dosage: "每日1剂",preparation: "水煎服",administration: "温服，每日2次";
    };
  }

  private getBloodActivatingPrescription(): Prescription {
    return {
      id: "xue_fu_zhu_yu_tang",
      name: "血府逐瘀汤",category: "理血剂",composition: [;
        { herb: "桃仁", dosage: "12", unit: "g", processing: "去皮尖", function: "活血祛瘀" },{ herb: "红花", dosage: "9", unit: "g", processing: "生用", function: "活血通经" },{ herb: "当归", dosage: "9", unit: "g", processing: "酒洗", function: "补血活血" },{ herb: "生地黄", dosage: "9", unit: "g", processing: "生用", function: "清热凉血" };
      ],functions: ["活血化瘀", "行气止痛"],indications: ["胸中血瘀", "胸痛头痛", "痛如针刺"],contraindications: ["孕妇", "月经过多"],modifications: [],dosage: "每日1剂",preparation: "水煎服",administration: "温服，每日2次";
    };
  }
}

export class TCMDiagnosisEngine {
  private static instance: TCMDiagnosisEngine;
  private constitutionEngine: ConstitutionIdentificationEngine;
  private syndromeEngine: SyndromePatternEngine;
  private prescriptionEngine: PrescriptionEngine;

  private constructor() {
    this.constitutionEngine = ConstitutionIdentificationEngine.getInstance();
    this.syndromeEngine = SyndromePatternEngine.getInstance();
    this.prescriptionEngine = PrescriptionEngine.getInstance();
  }

  static getInstance(): TCMDiagnosisEngine {
    if (!TCMDiagnosisEngine.instance) {
      TCMDiagnosisEngine.instance = new TCMDiagnosisEngine();
    }
    return TCMDiagnosisEngine.instance;
  }

  async performDiagnosis(
    patientId: string,
    inspectionData: InspectionData,
    auscultationData: AuscultationData,
    inquiryData: InquiryData,
    palpationData: PalpationData,
    calculationData: CalculationData,
    additionalData?: AdditionalData
  ): Promise<TCMDiagnosisResult> {
    const startTime = Date.now();
    try {
      // 1. 体质辨识
      const constitutionResult = this.constitutionEngine.identifyConstitution(;
        inspectionData,inquiryData,palpationData;
      );

      // 2. 证候辨识
      const patterns = this.syndromeEngine.identifyPatterns(;
        inspectionData,auscultationData,inquiryData,palpationData;
      );

      // 3. 治疗原则
      const principles = this.generateTreatmentPrinciples(patterns);

      // 4. 方药推荐
      const prescriptions = this.prescriptionEngine.generatePrescriptions(patterns);

      // 5. 生活调理建议
      const lifestyleRecommendations = this.generateLifestyleRecommendations(;
        constitutionResult.constitution,patterns,calculationData.currentSeason;
      );

      // 6. 随访计划
      const followUpPlan = this.generateFollowUpPlan(patterns);

      // 7. 计算总体置信度
      const confidence = this.calculateOverallConfidence(;
        constitutionResult.confidence,patterns;
      );

      // 8. 生成诊断推理
      const reasoning = this.generateReasoning(;
        constitutionResult,patterns,principles;
      );

      const result: TCMDiagnosisResult = {
        patient_id: patientId,
        diagnosis_date: Date.now(),
        constitution: constitutionResult.constitution,
        syndrome_patterns: patterns,
        treatment_principles: principles,
        prescriptions,
        lifestyle_recommendations: lifestyleRecommendations,
        follow_up_plan: followUpPlan,
        confidence,
        reasoning
      };

             // 记录诊断性能
       performanceMonitor.recordUserInteraction(
         "tcm_diagnosis",
         "diagnosis_completed",
         Date.now() - startTime
       );

      return result;
    } catch (error) {
      throw new Error("中医诊断过程中发生错误");
    }
  }

  private generateTreatmentPrinciples(patterns: SyndromePattern[]): TreatmentPrinciple[] {
    const principles: TreatmentPrinciple[] = [];

    for (const pattern of patterns.slice(0, 3)) {
      if (pattern.name.includes("气虚")) {
        principles.push({
          id: "tonify_qi",
          name: "补气",
          description: "补益元气，增强脏腑功能",
          methods: ["补气药物", "针灸补法", "食疗调养"],
          contraindications: ["实证", "热证"]
        });
      } else if (pattern.name.includes("血虚")) {
        principles.push({
          id: "nourish_blood",
          name: "养血",
          description: "滋养血液，濡润脏腑",
          methods: ["养血药物", "食疗补血", "调理月经"],
          contraindications: ["湿盛", "痰多"]
        });
      } else if (pattern.name.includes("气郁")) {
        principles.push({
          id: "regulate_qi",
          name: "理气",
          description: "疏理气机，调畅情志",
          methods: ["理气药物", "情志调摄", "运动疗法"],
          contraindications: ["气虚", "阴虚"]
        });
      }
    }

    return principles;
  }

  private generateLifestyleRecommendations(
    constitution: ConstitutionType,
    patterns: SyndromePattern[],
    season: SeasonType
  ): LifestyleRecommendation {
    const baseRecommendations: LifestyleRecommendation = {
      category: "diet",
      recommendations: [],
      foods_to_eat: [],
      foods_to_avoid: [],
      exercises: [],
      acupoint_massage: [],
      seasonal_adjustments: {
        春季: ["疏肝理气", "适量运动"],
        夏季: ["清热生津", "避免过劳"],
        秋季: ["润燥养阴", "早睡早起"],
        冬季: ["温阳补肾", "适当进补"]
      }
    };

    // 根据体质调整
    if (constitution === "气虚质") {
      baseRecommendations.foods_to_eat.push("山药", "大枣", "黄芪", "人参");
      baseRecommendations.foods_to_avoid.push("生冷食物", "辛辣刺激");
      baseRecommendations.exercises.push("太极拳", "八段锦", "散步");
      baseRecommendations.acupoint_massage.push("足三里", "气海", "关元");
    } else if (constitution === "阴虚质") {
      baseRecommendations.foods_to_eat.push("银耳", "百合", "枸杞", "麦冬");
      baseRecommendations.foods_to_avoid.push("辛辣燥热", "煎炸食品");
      baseRecommendations.exercises.push("瑜伽", "游泳", "慢跑");
      baseRecommendations.acupoint_massage.push("三阴交", "太溪", "照海");
    }

    // 根据证候调整
    for (const pattern of patterns) {
      if (pattern.name.includes("肝气郁结")) {
        baseRecommendations.recommendations.push(
          "保持心情舒畅",
          "避免情绪激动"
        );
        baseRecommendations.acupoint_massage.push("太冲", "期门", "膻中");
      }
    }

    return baseRecommendations;
  }

  private generateFollowUpPlan(patterns: SyndromePattern[]): FollowUpPlan {
    const severity = patterns[0]?.severity || "mild";
    let nextVisitDays = 14; // 默认2周

    if (severity === "severe") {
      nextVisitDays = 7; // 1周
    } else if (severity === "mild") {
      nextVisitDays = 30; // 1个月
    }

    return {
      next_visit: Date.now() + nextVisitDays * 24 * 60 * 60 * 1000,
      monitoring_points: [
        "症状变化情况",
        "服药后反应",
        "睡眠质量",
        "饮食情况",
        "情绪状态"
      ],warning_signs: [;
        "症状明显加重","出现新的不适","服药后不良反应","持续发热","剧烈疼痛";
      ],self_care_instructions: [;
        "按时服药","注意饮食调理","保持规律作息","适量运动","情志调摄";
      ];
    };
  }

  private calculateOverallConfidence(
    constitutionConfidence: number,
    patterns: SyndromePattern[]
  ): number {
    if (patterns.length === 0) {
      return constitutionConfidence;
    }

    const avgPatternConfidence =
      patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;

         // 记录计算性能
     // performanceMonitor.recordRender();

    return (constitutionConfidence + avgPatternConfidence) / 2;
  }

  private generateReasoning(
    constitutionResult: {
      constitution: ConstitutionType;
      confidence: number;
      characteristics: string[];
    },
    patterns: SyndromePattern[],
    principles: TreatmentPrinciple[]
  ): string {
    let reasoning = `基于五诊合参的综合分析：\n\n`;

    reasoning += `1. 体质辨识：患者为${constitutionResult.constitution}，置信度${(constitutionResult.confidence * 100).toFixed(1)}%\n`;
    reasoning += `   主要特征：${constitutionResult.characteristics.slice(0, 3).join("、")}\n\n`;

    reasoning += `2. 证候分析：\n`;
    patterns.slice(0, 3).forEach((pattern, index) => {
      reasoning += `   ${index + 1}. ${pattern.name}（${pattern.category}）- 置信度${(pattern.confidence * 100).toFixed(1)}%\n`;
      reasoning += `      病机：${pattern.pathogenesis}\n`;
    });

    reasoning += `\n3. 治疗原则：${principles.map((p) => p.name).join("、")}\n\n`;
    reasoning += `4. 诊断依据：结合患者的症状表现、舌脉象征，运用中医理论进行综合分析得出上述诊断。`;

    return reasoning;
  }

  // 获取中医知识库信息
  getTCMKnowledge(category: "constitution" | "syndrome" | "herb" | "acupoint"): unknown {
    const knowledge = {
      constitution: {
        types: [
          "平和质",
          "气虚质",
          "阳虚质",
          "阴虚质",
          "痰湿质",
          "湿热质",
          "血瘀质",
          "气郁质",
          "特禀质"
        ],
        description: "中医体质学说将人体体质分为九种基本类型"
      },
      syndrome: {
        categories: [
          "八纲辨证",
          "脏腑辨证","气血辨证","六经辨证","卫气营血辨证";
        ],description: "中医辨证论治的核心理论体系";
      },herb: {categories: ["补益药", "清热药", "理气药", "活血药", "化痰药"],description: "中药按功效分类的基本体系";
      },acupoint: {categories: ["十二经穴", "奇穴", "阿是穴"],description: "针灸治疗的基础穴位体系";
      };
    };
    return knowledge[category];
  }
}

// 导出单例实例
export const tcmDiagnosisEngine = TCMDiagnosisEngine.getInstance();
