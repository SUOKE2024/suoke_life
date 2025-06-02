import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';

// 模拟的性能监控器
const performanceMonitor = {
  recordMetric: (name: string, value: number) => {
    console.log(`Performance metric ${name}: ${value}ms`);
  },
  recordRender: () => {
    console.log('Render performance recorded');
  }
};

// 模拟的安全管理器
const securityManager = {
  logSecurityEvent: (event: any) => {
    console.log('Security event logged:', event);
  }
};

// 模拟的智能体协作系统
const agentCollaborationSystem = {
  createCollaborationTask: async (type: string, data: any, priority: string) => {
    console.log(`Collaboration task created: ${type}`, data);
  }
};

// 中医基础理论配置
const TCM_CONFIG = {
  FIVE_ELEMENTS: ["木", "火", "土", "金", "水"],
  EIGHT_PRINCIPLES: ["阴", "阳", "表", "里", "寒", "热", "虚", "实"],
  QI_BLOOD_PATTERNS: ["气虚", "气滞", "血虚", "血瘀"],
  ORGAN_SYSTEMS: ["心", "肝", "脾", "肺", "肾", "胆", "胃", "小肠", "大肠", "膀胱", "三焦"],
  MERIDIANS: 12
};

// 症状类型
export interface Symptom {
  id: string;
  name: string;
  category: | "inspection" | "auscultation" | "inquiry" | "palpation" | "calculation";
  severity: 1 | 2 | 3 | 4 | 5; // 1-轻微, 5-严重
  duration: number;
  frequency: "occasional" | "frequent" | "constant";
  location?: string;
  quality?: string;
  triggers?: string[];
  relievers?: string[];
}

// 五诊数据
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

// 辨证结果
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

// 治疗原则
export interface TreatmentPrinciple {
  id: string;
  name: string;
  description: string;
  methods: string[];
  contraindications: string[];
}

// 方剂
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

// 生活调理建议
export interface LifestyleRecommendation {
  category: "diet" | "exercise" | "emotion" | "sleep" | "environment";
  recommendations: string[];
  foods_to_eat: string[];
  foods_to_avoid: string[];
  exercises: string[];
  acupoint_massage: string[];
  seasonal_adjustments: Record<SeasonType, string[]>;
}

// 诊断结果
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

// 体质辨识引擎
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
    // 体质辨识逻辑
    const scores: Record<ConstitutionType, number> = {
      "平和质": 0,
      "气虚质": 0,
      "阳虚质": 0,
      "阴虚质": 0,
      "痰湿质": 0,
      "湿热质": 0,
      "血瘀质": 0,
      "气郁质": 0,
      "特禀质": 0
    };

    // 基于面色判断
    if (inspectionData.complexion.includes("萎黄") || inspectionData.complexion.includes("淡白")) {
      scores["气虚质"] += 0.3;
    }
    if (inspectionData.complexion.includes("晦暗") || inspectionData.complexion.includes("青紫")) {
      scores["血瘀质"] += 0.3;
    }

    // 基于舌象判断
    if (inspectionData.tongue.body_color.includes("淡")) {
      scores["气虚质"] += 0.2;
      scores["阳虚质"] += 0.2;
    }
    if (inspectionData.tongue.coating_thickness.includes("厚腻")) {
      scores["痰湿质"] += 0.3;
    }

    // 基于脉象判断
    if (palpationData.pulse.strength.includes("弱") || palpationData.pulse.strength.includes("虚")) {
      scores["气虚质"] += 0.3;
    }
    if (palpationData.pulse.quality.includes("滑")) {
      scores["痰湿质"] += 0.2;
    }

    // 基于症状判断
    for (const symptom of inquiryData.symptoms) {
      if (symptom.name.includes("乏力") || symptom.name.includes("气短")) {
        scores["气虚质"] += 0.2;
      }
      if (symptom.name.includes("怕冷") || symptom.name.includes("手足冰凉")) {
        scores["阳虚质"] += 0.2;
      }
      if (symptom.name.includes("口干") || symptom.name.includes("盗汗")) {
        scores["阴虚质"] += 0.2;
      }
    }

    // 找出得分最高的体质
    const maxScore = Math.max(...Object.values(scores));
    const constitution = Object.keys(scores).find(
      key => scores[key as ConstitutionType] === maxScore
    ) as ConstitutionType;

    const confidence = Math.min(maxScore, 1.0);
    const characteristics = this.getConstitutionCharacteristics(constitution);

    return { constitution, confidence, characteristics };
  }

  private getConstitutionCharacteristics(constitution: ConstitutionType): string[] {
    const characteristicsMap: Record<ConstitutionType, string[]> = {
      "平和质": ["体态适中", "面色润泽", "精力充沛", "睡眠良好"],
      "气虚质": ["容易疲劳", "气短懒言", "容易出汗", "抵抗力差"],
      "阳虚质": ["畏寒怕冷", "手足不温", "精神不振", "大便溏薄"],
      "阴虚质": ["形体偏瘦", "口燥咽干", "手足心热", "潮热盗汗"],
      "痰湿质": ["形体肥胖", "腹部肥满", "胸闷痰多", "身重困倦"],
      "湿热质": ["面垢油腻", "口苦口干", "身重困倦", "大便黏滞"],
      "血瘀质": ["肤色晦暗", "色素沉着", "易生黄褐斑", "舌质紫暗"],
      "气郁质": ["神情抑郁", "情感脆弱", "烦闷不乐", "胸胁胀满"],
      "特禀质": ["过敏体质", "遗传缺陷", "胎传异常", "药物过敏"]
    };

    return characteristicsMap[constitution] || [];
  }
}

// 辨证引擎
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

    // 气虚证
    if (this.checkQiDeficiency(inquiryData, palpationData)) {
      patterns.push({
        id: "qi_deficiency",
        name: "气虚证",
        category: "气血辨证",
        description: "脏腑功能减退，气的推动、温煦、防御功能减弱",
        pathogenesis: "先天禀赋不足，或后天失养，或久病耗气",
        main_symptoms: ["乏力", "气短", "自汗", "脉弱"],
        secondary_symptoms: ["声低懒言", "头晕", "食欲不振"],
        tongue_pulse: "舌淡苔白，脉虚弱",
        confidence: 0.8,
        severity: "moderate"
      });
    }

    // 血瘀证
    if (this.checkBloodStasis(inspectionData, inquiryData, palpationData)) {
      patterns.push({
        id: "blood_stasis",
        name: "血瘀证",
        category: "气血辨证",
        description: "血液运行不畅，瘀血内阻",
        pathogenesis: "气滞、寒凝、热结、外伤等导致血行不畅",
        main_symptoms: ["疼痛固定", "面色晦暗", "舌质紫暗", "脉涩"],
        secondary_symptoms: ["肌肤甲错", "瘀斑", "包块"],
        tongue_pulse: "舌质紫暗或有瘀斑，脉涩或结代",
        confidence: 0.7,
        severity: "moderate"
      });
    }

    return patterns.sort((a, b) => b.confidence - a.confidence);
  }

  private checkQiDeficiency(inquiryData: InquiryData, palpationData: PalpationData): boolean {
    let score = 0;

    // 检查主要症状
    for (const symptom of inquiryData.symptoms) {
      if (symptom.name.includes("乏力") || symptom.name.includes("疲劳")) score += 0.3;
      if (symptom.name.includes("气短") || symptom.name.includes("呼吸困难")) score += 0.3;
      if (symptom.name.includes("自汗") || symptom.name.includes("出汗")) score += 0.2;
    }

    // 检查脉象
    if (palpationData.pulse.strength.includes("弱") || palpationData.pulse.strength.includes("虚")) {
      score += 0.3;
    }

    return score >= 0.6;
  }

  private checkBloodStasis(
    inspectionData: InspectionData,
    inquiryData: InquiryData,
    palpationData: PalpationData
  ): boolean {
    let score = 0;

    // 检查面色
    if (inspectionData.complexion.includes("晦暗") || inspectionData.complexion.includes("青紫")) {
      score += 0.3;
    }

    // 检查舌象
    if (inspectionData.tongue.body_color.includes("紫") || inspectionData.tongue.body_color.includes("暗")) {
      score += 0.3;
    }

    // 检查症状
    for (const symptom of inquiryData.symptoms) {
      if (symptom.name.includes("疼痛") && symptom.name.includes("固定")) score += 0.3;
      if (symptom.name.includes("瘀斑") || symptom.name.includes("紫斑")) score += 0.2;
    }

    // 检查脉象
    if (palpationData.pulse.quality.includes("涩") || palpationData.pulse.quality.includes("结")) {
      score += 0.2;
    }

    return score >= 0.6;
  }
}

// 方剂引擎
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
      name: "四君子汤",
      category: "补益剂",
      composition: [
        { herb: "人参", dosage: "9", unit: "g", processing: "生用", function: "大补元气" },
        { herb: "白术", dosage: "9", unit: "g", processing: "炒用", function: "健脾燥湿" },
        { herb: "茯苓", dosage: "9", unit: "g", processing: "生用", function: "健脾利湿" },
        { herb: "甘草", dosage: "6", unit: "g", processing: "炙用", function: "调和诸药" }
      ],
      functions: ["益气健脾", "补中益气"],
      indications: ["脾胃气虚", "食少便溏", "气短乏力"],
      contraindications: ["实证", "热证"],
      modifications: [
        {
          condition: "食欲不振明显",
          modification: "加陈皮、砂仁",
          herbs_to_add: [
            { herb: "陈皮", dosage: "6", unit: "g", processing: "生用", function: "理气健脾" }
          ]
        }
      ],
      dosage: "每日1剂",
      preparation: "水煎服",
      administration: "温服，每日2次"
    };
  }

  private getBloodActivatingPrescription(): Prescription {
    return {
      id: "xue_fu_zhu_yu_tang",
      name: "血府逐瘀汤",
      category: "理血剂",
      composition: [
        { herb: "桃仁", dosage: "12", unit: "g", processing: "去皮尖", function: "活血祛瘀" },
        { herb: "红花", dosage: "9", unit: "g", processing: "生用", function: "活血通经" },
        { herb: "当归", dosage: "9", unit: "g", processing: "酒洗", function: "补血活血" },
        { herb: "生地黄", dosage: "9", unit: "g", processing: "生用", function: "清热凉血" },
        { herb: "川芎", dosage: "4.5", unit: "g", processing: "生用", function: "活血行气" },
        { herb: "赤芍", dosage: "6", unit: "g", processing: "生用", function: "清热凉血" }
      ],
      functions: ["活血祛瘀", "行气止痛"],
      indications: ["胸中血瘀", "胸痛头痛", "痛如针刺"],
      contraindications: ["孕妇", "月经过多"],
      modifications: [],
      dosage: "每日1剂",
      preparation: "水煎服",
      administration: "温服，每日2次"
    };
  }
}

// 主诊断引擎
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
    try {
      // 记录性能开始
      const startTime = performance.now();

      // 1. 体质辨识
      const constitutionResult = this.constitutionEngine.identifyConstitution(
        inspectionData,
        inquiryData,
        palpationData
      );

      // 2. 辨证分析
      const syndromePatterns = this.syndromeEngine.identifyPatterns(
        inspectionData,
        auscultationData,
        inquiryData,
        palpationData
      );

      // 3. 治疗原则
      const principles = this.generateTreatmentPrinciples(syndromePatterns);

      // 4. 方剂推荐
      const prescriptions = this.prescriptionEngine.generatePrescriptions(syndromePatterns);

      // 5. 生活调理建议
      const lifestyleRecommendations = this.generateLifestyleRecommendations(
        constitutionResult.constitution,
        syndromePatterns,
        calculationData.currentSeason
      );

      // 6. 随访计划
      const followUpPlan = this.generateFollowUpPlan(syndromePatterns);

      // 7. 计算总体置信度
      const overallConfidence = this.calculateOverallConfidence(
        constitutionResult.confidence,
        syndromePatterns
      );

      // 8. 生成诊断推理
      const reasoning = this.generateReasoning(
        constitutionResult,
        syndromePatterns,
        principles
      );

      // 记录性能结束
      const endTime = performance.now();
      performanceMonitor.recordMetric('tcm_diagnosis_duration', endTime - startTime);

      const result: TCMDiagnosisResult = {
        patient_id: patientId,
        diagnosis_date: Date.now(),
        constitution: constitutionResult.constitution,
        syndrome_patterns: syndromePatterns,
        treatment_principles: principles,
        prescriptions,
        lifestyle_recommendations: lifestyleRecommendations,
        follow_up_plan: followUpPlan,
        confidence: overallConfidence,
        reasoning
      };

      // 记录诊断事件
      securityManager.logSecurityEvent({
        type: "data_access",
        userId: patientId,
        details: {
          action: "tcm_diagnosis_performed",
          constitution: constitutionResult.constitution,
          syndrome_count: syndromePatterns.length,
          confidence: overallConfidence
        },
        severity: "low"
      });

      // 创建智能体协作任务进行验证
      await agentCollaborationSystem.createCollaborationTask(
        "health_diagnosis",
        {
          diagnosis_result: result,
          validation_required: true
        },
        "medium"
      );

      return result;
    } catch (error) {
      console.error("中医诊断失败:", error);
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
      ],
      warning_signs: [
        "症状明显加重",
        "出现新的不适",
        "服药后不良反应",
        "持续发热",
        "剧烈疼痛"
      ],
      self_care_instructions: [
        "按时服药",
        "注意饮食调理",
        "保持规律作息",
        "适量运动",
        "情志调摄"
      ]
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

    // 记录渲染性能
    performanceMonitor.recordRender();

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

    reasoning += `1. 体质辨识：患者为${
      constitutionResult.constitution
    }，置信度${(constitutionResult.confidence * 100).toFixed(1)}%\n`;
    reasoning += `   主要特征：${constitutionResult.characteristics
      .slice(0, 3)
      .join("、")}\n\n`;

    reasoning += `2. 证候分析：\n`;
    patterns.slice(0, 3).forEach((pattern, index) => {
      reasoning += `   ${index + 1}. ${pattern.name}（${
        pattern.category
      }）- 置信度${(pattern.confidence * 100).toFixed(1)}%\n`;
      reasoning += `      病机：${pattern.pathogenesis}\n`;
    });

    reasoning += `\n3. 治疗原则：${principles
      .map((p) => p.name)
      .join("、")}\n\n`;

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
          "脏腑辨证",
          "气血辨证",
          "六经辨证",
          "卫气营血辨证"
        ],
        description: "中医辨证论治的核心理论体系"
      },
      herb: {
        categories: ["补益药", "清热药", "理气药", "活血药", "化痰药"],
        description: "中药按功效分类的基本体系"
      },
      acupoint: {
        categories: ["十二经穴", "奇穴", "阿是穴"],
        description: "针灸治疗的基础穴位体系"
      }
    };

    return knowledge[category];
  }
}

// 导出单例实例
export const tcmDiagnosisEngine = TCMDiagnosisEngine.getInstance();