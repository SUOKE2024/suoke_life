import { agentCollaborationSystem } from "./agentCollaborationSystem";
import { securityManager } from "./securityManager";
import { ConstitutionType, DiagnosisType, SeasonType } from "../types";



// 中医基础理论配置
const TCM_CONFIG = {
  FIVE_ELEMENTS: ["木", "火", "土", "金", "水"],
  EIGHT_PRINCIPLES: ["阴", "阳", "表", "里", "寒", "热", "虚", "实"],
  QI_BLOOD_PATTERNS: ["气虚", "气滞", "血虚", "血瘀"],
  ORGAN_SYSTEMS: [
    "心",
    "肝",
    "脾",
    "肺",
    "肾",
    "胆",
    "胃",
    "小肠",
    "大肠",
    "膀胱",
    "三焦",
  ],
  MERIDIANS: 12,
};

// 症状类型
export interface Symptom {
  id: string;
  name: string;
  category:
    | "inspection"
    | "auscultation"
    | "inquiry"
    | "palpation"
    | "calculation";
  severity: 1 | 2 | 3 | 4 | 5; // 1-轻微, 5-严重
  duration: number; // 持续时间（天）
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
      ConstitutionIdentificationEngine.instance =
        new ConstitutionIdentificationEngine();
    }
    return ConstitutionIdentificationEngine.instance;
  }

  // 体质辨识算法
  identifyConstitution(diagnosisData: FiveDiagnosisData): {
    constitution: ConstitutionType;
    confidence: number;
    characteristics: string[];
  } {
    const scores = this.calculateConstitutionScores(diagnosisData);
    const sortedScores = Object.entries(scores).sort(([, a], [, b]) => b - a);

    const primaryConstitution = sortedScores[0][0] as ConstitutionType;
    const confidence = sortedScores[0][1];

    const characteristics =
      this.getConstitutionCharacteristics(primaryConstitution);

    return {
      constitution: primaryConstitution,
      confidence,
      characteristics,
    };
  }

  private calculateConstitutionScores(
    data: FiveDiagnosisData
  ): Record<ConstitutionType, number> {
    const scores: Record<ConstitutionType, number> = {
      平和质: 0,
      气虚质: 0,
      阳虚质: 0,
      阴虚质: 0,
      痰湿质: 0,
      湿热质: 0,
      血瘀质: 0,
      气郁质: 0,
      特禀质: 0,
    };

    // 基于面色判断
    if (data.inspection.complexion.includes("红润")) {
      scores["平和质"] += 20;
    } else if (data.inspection.complexion.includes("萎黄")) {
      scores["气虚质"] += 15;
      scores["阳虚质"] += 10;
    } else if (data.inspection.complexion.includes("潮红")) {
      scores["阴虚质"] += 15;
      scores["湿热质"] += 10;
    }

    // 基于舌象判断
    const tongue = data.inspection.tongue;
    if (tongue.body_color === "淡红" && tongue.coating_color === "薄白") {
      scores["平和质"] += 20;
    } else if (tongue.body_color === "淡白") {
      scores["气虚质"] += 15;
      scores["阳虚质"] += 10;
    } else if (tongue.body_color === "红") {
      scores["阴虚质"] += 15;
      scores["湿热质"] += 10;
    }

    // 基于脉象判断
    const pulse = data.palpation.pulse;
    if (pulse.quality === "平和") {
      scores["平和质"] += 20;
    } else if (pulse.quality.includes("细弱")) {
      scores["气虚质"] += 15;
    } else if (pulse.quality.includes("沉迟")) {
      scores["阳虚质"] += 15;
    } else if (pulse.quality.includes("细数")) {
      scores["阴虚质"] += 15;
    }

    // 基于症状判断
    data.inquiry.symptoms.forEach((symptom) => {
      if (symptom.name.includes("乏力") || symptom.name.includes("气短")) {
        scores["气虚质"] += 10;
      } else if (
        symptom.name.includes("怕冷") ||
        symptom.name.includes("手足冰凉")
      ) {
        scores["阳虚质"] += 10;
      } else if (
        symptom.name.includes("口干") ||
        symptom.name.includes("盗汗")
      ) {
        scores["阴虚质"] += 10;
      } else if (
        symptom.name.includes("痰多") ||
        symptom.name.includes("身重")
      ) {
        scores["痰湿质"] += 10;
      }
    });

    return scores;
  }

  private getConstitutionCharacteristics(
    constitution: ConstitutionType
  ): string[] {
    const characteristics: Record<ConstitutionType, string[]> = {
      平和质: ["体形匀称", "面色红润", "精力充沛", "睡眠良好", "性格开朗"],
      气虚质: ["容易疲劳", "气短懒言", "容易出汗", "声音低弱", "容易感冒"],
      阳虚质: ["怕冷", "手足不温", "喜热饮食", "精神不振", "大便溏薄"],
      阴虚质: ["体形偏瘦", "手足心热", "口燥咽干", "喜冷饮", "大便干燥"],
      痰湿质: ["体形肥胖", "腹部肥满", "胸闷痰多", "口黏腻", "身重困倦"],
      湿热质: ["面垢油腻", "口苦口干", "身重困倦", "大便黏滞", "小便短黄"],
      血瘀质: ["肤色晦暗", "色素沉着", "容易出血", "口唇暗淡", "舌质紫暗"],
      气郁质: ["神情抑郁", "情感脆弱", "烦闷不乐", "胸胁胀满", "善太息"],
      特禀质: ["过敏体质", "遗传缺陷", "胎传异常", "药物过敏", "食物过敏"],
    };

    return characteristics[constitution] || [];
  }
}

// 证候辨识引擎
class SyndromePatternEngine {
  private static instance: SyndromePatternEngine;

  static getInstance(): SyndromePatternEngine {
    if (!SyndromePatternEngine.instance) {
      SyndromePatternEngine.instance = new SyndromePatternEngine();
    }
    return SyndromePatternEngine.instance;
  }

  // 辨证分析
  analyzeSyndromePatterns(
    diagnosisData: FiveDiagnosisData,
    constitution: ConstitutionType
  ): SyndromePattern[] {
    const patterns: SyndromePattern[] = [];

    // 基于八纲辨证
    const eightPrinciplesPatterns = this.analyzeEightPrinciples(diagnosisData);
    patterns.push(...eightPrinciplesPatterns);

    // 基于脏腑辨证
    const organPatterns = this.analyzeOrganSyndromes(diagnosisData);
    patterns.push(...organPatterns);

    // 基于气血辨证
    const qiBloodPatterns = this.analyzeQiBloodSyndromes(diagnosisData);
    patterns.push(...qiBloodPatterns);

    // 基于体质调整
    const adjustedPatterns = this.adjustPatternsForConstitution(
      patterns,
      constitution
    );

    // 按置信度排序
    return adjustedPatterns
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 5);
  }

  private analyzeEightPrinciples(data: FiveDiagnosisData): SyndromePattern[] {
    const patterns: SyndromePattern[] = [];

    // 表里辨证
    const hasExteriorSymptoms = data.inquiry.symptoms.some(
      (s) =>
        s.name.includes("发热") ||
        s.name.includes("恶寒") ||
        s.name.includes("头痛")
    );

    if (hasExteriorSymptoms) {
      patterns.push({
        id: "exterior_syndrome",
        name: "表证",
        category: "八纲辨证",
        description: "病位在表，邪气侵犯肌表",
        pathogenesis: "外邪侵袭，卫气抗邪",
        main_symptoms: ["发热", "恶寒", "头痛", "身痛"],
        secondary_symptoms: ["鼻塞", "流涕", "咳嗽"],
        tongue_pulse: "舌苔薄白，脉浮",
        confidence: 0.8,
        severity: "mild",
      });
    }

    // 寒热辨证
    const coldSymptoms = data.inquiry.symptoms.filter(
      (s) =>
        s.name.includes("怕冷") ||
        s.name.includes("手足冰凉") ||
        s.name.includes("喜热饮")
    ).length;

    const heatSymptoms = data.inquiry.symptoms.filter(
      (s) =>
        s.name.includes("发热") ||
        s.name.includes("口渴") ||
        s.name.includes("喜冷饮")
    ).length;

    if (coldSymptoms > heatSymptoms) {
      patterns.push({
        id: "cold_syndrome",
        name: "寒证",
        category: "八纲辨证",
        description: "机体阳气不足或感受寒邪",
        pathogenesis: "阳气虚衰，寒从内生",
        main_symptoms: ["畏寒", "四肢不温", "面色苍白"],
        secondary_symptoms: ["喜热饮", "小便清长", "大便溏薄"],
        tongue_pulse: "舌淡苔白，脉沉迟",
        confidence: 0.7 + coldSymptoms * 0.1,
        severity: "moderate",
      });
    } else if (heatSymptoms > coldSymptoms) {
      patterns.push({
        id: "heat_syndrome",
        name: "热证",
        category: "八纲辨证",
        description: "机体阳气偏盛或感受热邪",
        pathogenesis: "阳热偏盛，热从内生",
        main_symptoms: ["发热", "口渴", "面红目赤"],
        secondary_symptoms: ["喜冷饮", "小便短黄", "大便干结"],
        tongue_pulse: "舌红苔黄，脉数",
        confidence: 0.7 + heatSymptoms * 0.1,
        severity: "moderate",
      });
    }

    return patterns;
  }

  private analyzeOrganSyndromes(data: FiveDiagnosisData): SyndromePattern[] {
    const patterns: SyndromePattern[] = [];

    // 心系证候
    const heartSymptoms = data.inquiry.symptoms.filter(
      (s) =>
        s.name.includes("心悸") ||
        s.name.includes("失眠") ||
        s.name.includes("健忘")
    );

    if (heartSymptoms.length > 0) {
      patterns.push({
        id: "heart_qi_deficiency",
        name: "心气虚",
        category: "脏腑辨证",
        description: "心气不足，心神失养",
        pathogenesis: "心气虚弱，血行无力",
        main_symptoms: ["心悸", "气短", "胸闷"],
        secondary_symptoms: ["乏力", "自汗", "面色淡白"],
        tongue_pulse: "舌淡苔白，脉细弱",
        confidence: 0.6 + heartSymptoms.length * 0.1,
        severity: "mild",
      });
    }

    // 肝系证候
    const liverSymptoms = data.inquiry.symptoms.filter(
      (s) =>
        s.name.includes("胁痛") ||
        s.name.includes("易怒") ||
        s.name.includes("头晕")
    );

    if (liverSymptoms.length > 0) {
      patterns.push({
        id: "liver_qi_stagnation",
        name: "肝气郁结",
        category: "脏腑辨证",
        description: "肝失疏泄，气机郁滞",
        pathogenesis: "情志不遂，肝气郁结",
        main_symptoms: ["胁肋胀痛", "情志抑郁", "善太息"],
        secondary_symptoms: ["易怒", "胸闷", "咽中如有物阻"],
        tongue_pulse: "舌苔薄白，脉弦",
        confidence: 0.6 + liverSymptoms.length * 0.1,
        severity: "moderate",
      });
    }

    return patterns;
  }

  private analyzeQiBloodSyndromes(data: FiveDiagnosisData): SyndromePattern[] {
    const patterns: SyndromePattern[] = [];

    // 气虚证
    const qiDeficiencySymptoms = data.inquiry.symptoms.filter(
      (s) =>
        s.name.includes("乏力") ||
        s.name.includes("气短") ||
        s.name.includes("懒言")
    );

    if (qiDeficiencySymptoms.length > 0) {
      patterns.push({
        id: "qi_deficiency",
        name: "气虚证",
        category: "气血辨证",
        description: "元气不足，脏腑功能减退",
        pathogenesis: "先天不足或后天失养",
        main_symptoms: ["神疲乏力", "气短懒言", "动则汗出"],
        secondary_symptoms: ["面色淡白", "声音低微", "容易感冒"],
        tongue_pulse: "舌淡苔白，脉虚弱",
        confidence: 0.6 + qiDeficiencySymptoms.length * 0.1,
        severity: "moderate",
      });
    }

    // 血虚证
    const bloodDeficiencySymptoms = data.inquiry.symptoms.filter(
      (s) =>
        s.name.includes("头晕") ||
        s.name.includes("心悸") ||
        s.name.includes("失眠")
    );

    if (
      bloodDeficiencySymptoms.length > 0 &&
      data.inspection.complexion.includes("萎黄")
    ) {
      patterns.push({
        id: "blood_deficiency",
        name: "血虚证",
        category: "气血辨证",
        description: "血液不足，脏腑失养",
        pathogenesis: "生血不足或失血过多",
        main_symptoms: ["面色萎黄", "头晕眼花", "心悸失眠"],
        secondary_symptoms: ["爪甲不荣", "肌肤干燥", "月经量少"],
        tongue_pulse: "舌淡苔白，脉细",
        confidence: 0.6 + bloodDeficiencySymptoms.length * 0.1,
        severity: "moderate",
      });
    }

    return patterns;
  }

  private adjustPatternsForConstitution(
    patterns: SyndromePattern[],
    constitution: ConstitutionType
  ): SyndromePattern[] {
    return patterns.map((pattern) => {
      let adjustedConfidence = pattern.confidence;

      // 根据体质调整置信度
      if (constitution === "气虚质" && pattern.name.includes("气虚")) {
        adjustedConfidence += 0.2;
      } else if (constitution === "阳虚质" && pattern.name.includes("阳虚")) {
        adjustedConfidence += 0.2;
      } else if (constitution === "阴虚质" && pattern.name.includes("阴虚")) {
        adjustedConfidence += 0.2;
      }

      return {
        ...pattern,
        confidence: Math.min(adjustedConfidence, 1.0),
      };
    });
  }
}

// 方剂推荐引擎
class PrescriptionEngine {
  private static instance: PrescriptionEngine;

  static getInstance(): PrescriptionEngine {
    if (!PrescriptionEngine.instance) {
      PrescriptionEngine.instance = new PrescriptionEngine();
    }
    return PrescriptionEngine.instance;
  }

  // 推荐方剂
  recommendPrescriptions(
    syndromePatterns: SyndromePattern[],
    constitution: ConstitutionType,
    season: SeasonType
  ): Prescription[] {
    const prescriptions: Prescription[] = [];

    for (const pattern of syndromePatterns.slice(0, 3)) {
      const prescription = this.getBasePrescription(pattern);
      if (prescription) {
        const modifiedPrescription = this.modifyForConstitutionAndSeason(
          prescription,
          constitution,
          season
        );
        prescriptions.push(modifiedPrescription);
      }
    }

    return prescriptions;
  }

  private getBasePrescription(pattern: SyndromePattern): Prescription | null {
    const prescriptionDatabase: Record<string, Prescription> = {
      qi_deficiency: {
        id: "si_jun_zi_tang",
        name: "四君子汤",
        category: "补益剂",
        composition: [
          {
            herb: "人参",
            dosage: "9",
            unit: "g",
            processing: "生用",
            function: "大补元气",
          },
          {
            herb: "白术",
            dosage: "9",
            unit: "g",
            processing: "炒用",
            function: "健脾益气",
          },
          {
            herb: "茯苓",
            dosage: "9",
            unit: "g",
            processing: "生用",
            function: "健脾利湿",
          },
          {
            herb: "甘草",
            dosage: "6",
            unit: "g",
            processing: "炙用",
            function: "调和诸药",
          },
        ],
        functions: ["益气健脾", "补中益气"],
        indications: ["脾胃气虚", "食少便溏", "气短乏力"],
        contraindications: ["阴虚火旺", "实热证"],
        modifications: [
          {
            condition: "食欲不振",
            modification: "加陈皮、砂仁",
            herbs_to_add: [
              {
                herb: "陈皮",
                dosage: "6",
                unit: "g",
                processing: "生用",
                function: "理气健脾",
              },
              {
                herb: "砂仁",
                dosage: "3",
                unit: "g",
                processing: "后下",
                function: "化湿开胃",
              },
            ],
          },
        ],
        dosage: "每日1剂",
        preparation: "水煎服",
        administration: "温服，分2次服用",
      },
      blood_deficiency: {
        id: "si_wu_tang",
        name: "四物汤",
        category: "补益剂",
        composition: [
          {
            herb: "当归",
            dosage: "12",
            unit: "g",
            processing: "生用",
            function: "补血活血",
          },
          {
            herb: "川芎",
            dosage: "6",
            unit: "g",
            processing: "生用",
            function: "活血行气",
          },
          {
            herb: "白芍",
            dosage: "12",
            unit: "g",
            processing: "生用",
            function: "养血敛阴",
          },
          {
            herb: "熟地黄",
            dosage: "15",
            unit: "g",
            processing: "熟用",
            function: "滋阴补血",
          },
        ],
        functions: ["补血调血", "养血和血"],
        indications: ["血虚证", "月经不调", "面色萎黄"],
        contraindications: ["湿盛中满", "大便溏泄"],
        modifications: [],
        dosage: "每日1剂",
        preparation: "水煎服",
        administration: "温服，分2次服用",
      },
    };

    return prescriptionDatabase[pattern.id] || null;
  }

  private modifyForConstitutionAndSeason(
    prescription: Prescription,
    constitution: ConstitutionType,
    season: SeasonType
  ): Prescription {
    const modified = { ...prescription };

    // 根据体质调整
    if (constitution === "阳虚质") {
      // 阳虚体质加温阳药
      modified.composition.push({
        herb: "附子",
        dosage: "6",
        unit: "g",
        processing: "制用",
        function: "回阳救逆",
      });
    } else if (constitution === "阴虚质") {
      // 阴虚体质加滋阴药
      modified.composition.push({
        herb: "麦冬",
        dosage: "10",
        unit: "g",
        processing: "生用",
        function: "滋阴润燥",
      });
    }

    // 根据季节调整
    if (season === "春季") {
      // 春季疏肝理气
      modified.composition.push({
        herb: "柴胡",
        dosage: "6",
        unit: "g",
        processing: "生用",
        function: "疏肝解郁",
      });
    } else if (season === "夏季") {
      // 夏季清热生津
      modified.composition.push({
        herb: "石斛",
        dosage: "10",
        unit: "g",
        processing: "生用",
        function: "清热生津",
      });
    }

    return modified;
  }
}

// 主要的中医诊断引擎
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

  // 综合诊断分析
  async performDiagnosis(
    patientId: string,
    diagnosisData: FiveDiagnosisData,
    season: SeasonType = "春季"
  ): Promise<TCMDiagnosisResult> {
    try {
      // 1. 体质辨识
      const constitutionResult =
        this.constitutionEngine.identifyConstitution(diagnosisData);

      // 2. 证候辨识
      const syndromePatterns = this.syndromeEngine.analyzeSyndromePatterns(
        diagnosisData,
        constitutionResult.constitution
      );

      // 3. 治疗原则制定
      const treatmentPrinciples =
        this.generateTreatmentPrinciples(syndromePatterns);

      // 4. 方剂推荐
      const prescriptions = this.prescriptionEngine.recommendPrescriptions(
        syndromePatterns,
        constitutionResult.constitution,
        season
      );

      // 5. 生活调理建议
      const lifestyleRecommendations = this.generateLifestyleRecommendations(
        constitutionResult.constitution,
        syndromePatterns,
        season
      );

      // 6. 随访计划
      const followUpPlan = this.generateFollowUpPlan(syndromePatterns);

      // 7. 计算整体置信度
      const overallConfidence = this.calculateOverallConfidence(
        constitutionResult.confidence,
        syndromePatterns
      );

      // 8. 生成推理说明
      const reasoning = this.generateReasoning(
        constitutionResult,
        syndromePatterns,
        treatmentPrinciples
      );

      const result: TCMDiagnosisResult = {
        patient_id: patientId,
        diagnosis_date: Date.now(),
        constitution: constitutionResult.constitution,
        syndrome_patterns: syndromePatterns,
        treatment_principles: treatmentPrinciples,
        prescriptions,
        lifestyle_recommendations: lifestyleRecommendations,
        follow_up_plan: followUpPlan,
        confidence: overallConfidence,
        reasoning,
      };

      // 记录诊断事件
      securityManager.logSecurityEvent({
        type: "data_access",
        userId: patientId,
        details: {
          action: "tcm_diagnosis_performed",
          constitution: constitutionResult.constitution,
          syndrome_count: syndromePatterns.length,
          confidence: overallConfidence,
        },
        severity: "low",
      });

      // 创建智能体协作任务进行验证
      await agentCollaborationSystem.createCollaborationTask(
        "health_diagnosis",
        {
          diagnosis_result: result,
          validation_required: true,
        },
        "medium"
      );

      return result;
    } catch (error) {
      console.error("中医诊断失败:", error);
      throw new Error("中医诊断过程中发生错误");
    }
  }

  private generateTreatmentPrinciples(
    patterns: SyndromePattern[]
  ): TreatmentPrinciple[] {
    const principles: TreatmentPrinciple[] = [];

    for (const pattern of patterns.slice(0, 3)) {
      if (pattern.name.includes("气虚")) {
        principles.push({
          id: "tonify_qi",
          name: "补气",
          description: "补益元气，增强脏腑功能",
          methods: ["补气药物", "针灸补法", "食疗调养"],
          contraindications: ["实证", "热证"],
        });
      } else if (pattern.name.includes("血虚")) {
        principles.push({
          id: "nourish_blood",
          name: "养血",
          description: "滋养血液，濡润脏腑",
          methods: ["养血药物", "食疗补血", "调理月经"],
          contraindications: ["湿盛", "痰多"],
        });
      } else if (pattern.name.includes("气郁")) {
        principles.push({
          id: "regulate_qi",
          name: "理气",
          description: "疏理气机，调畅情志",
          methods: ["理气药物", "情志调摄", "运动疗法"],
          contraindications: ["气虚", "阴虚"],
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
        冬季: ["温阳补肾", "适当进补"],
      },
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
        "情绪状态",
      ],
      warning_signs: [
        "症状明显加重",
        "出现新的不适",
        "服药后不良反应",
        "持续发热",
        "剧烈疼痛",
      ],
      self_care_instructions: [
        "按时服药",
        "注意饮食调理",
        "保持规律作息",
        "适量运动",
        "情志调摄",
      ],
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
  getTCMKnowledge(
    category: "constitution" | "syndrome" | "herb" | "acupoint"
  ): any {
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
          "特禀质",
        ],
        description: "中医体质学说将人体体质分为九种基本类型",
      },
      syndrome: {
        categories: [
          "八纲辨证",
          "脏腑辨证",
          "气血辨证",
          "六经辨证",
          "卫气营血辨证",
        ],
        description: "中医辨证论治的核心理论体系",
      },
      herb: {
        categories: ["补益药", "清热药", "理气药", "活血药", "化痰药"],
        description: "中药按功效分类的基本体系",
      },
      acupoint: {
        categories: ["十二经穴", "奇穴", "阿是穴"],
        description: "针灸治疗的基础穴位体系",
      },
    };

    return knowledge[category];
  }
}

// 导出单例实例
export const tcmDiagnosisEngine = TCMDiagnosisEngine.getInstance();
