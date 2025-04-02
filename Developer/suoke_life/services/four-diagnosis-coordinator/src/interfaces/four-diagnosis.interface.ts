/**
 * 四诊类型枚举
 */
export enum DiagnosisType {
  LOOKING = 'looking',
  SMELL = 'smell',
  INQUIRY = 'inquiry',
  TOUCH = 'touch'
}

/**
 * 阴阳平衡状态枚举
 */
export enum YinYangBalance {
  BALANCED = 'balanced',
  SLIGHT_YIN_DEFICIENCY = 'slight_yin_deficiency',
  MODERATE_YIN_DEFICIENCY = 'moderate_yin_deficiency',
  SEVERE_YIN_DEFICIENCY = 'severe_yin_deficiency',
  SLIGHT_YANG_DEFICIENCY = 'slight_yang_deficiency',
  MODERATE_YANG_DEFICIENCY = 'moderate_yang_deficiency',
  SEVERE_YANG_DEFICIENCY = 'severe_yang_deficiency',
  SLIGHT_YIN_EXCESS = 'slight_yin_excess',
  MODERATE_YIN_EXCESS = 'moderate_yin_excess',
  SEVERE_YIN_EXCESS = 'severe_yin_excess',
  SLIGHT_YANG_EXCESS = 'slight_yang_excess',
  MODERATE_YANG_EXCESS = 'moderate_yang_excess',
  SEVERE_YANG_EXCESS = 'severe_yang_excess'
}

/**
 * 五行元素枚举
 */
export enum FiveElement {
  WOOD = 'wood',
  FIRE = 'fire',
  EARTH = 'earth',
  METAL = 'metal',
  WATER = 'water'
}

/**
 * 体质类型枚举
 */
export enum ConstitutionType {
  BALANCED = 'balanced', // 平和质
  QI_DEFICIENCY = 'qi_deficiency', // 气虚质
  YANG_DEFICIENCY = 'yang_deficiency', // 阳虚质
  YIN_DEFICIENCY = 'yin_deficiency', // 阴虚质
  PHLEGM_DAMPNESS = 'phlegm_dampness', // 痰湿质
  DAMP_HEAT = 'damp_heat', // 湿热质
  BLOOD_STASIS = 'blood_stasis', // 血瘀质
  QI_STAGNATION = 'qi_stagnation', // 气郁质
  SPECIAL_CONSTITUTION = 'special_constitution' // 特禀质
}

/**
 * 单个诊断分析结果接口
 */
export interface DiagnosisAnalysis {
  diagnosisType: DiagnosisType;
  timestamp: Date;
  findings: string[];
  overallAssessment: string;
  confidence: number;
  rawData?: any;
}

/**
 * 五行分析结果接口
 */
export interface FiveElementsAnalysis {
  wood: number;
  fire: number;
  earth: number;
  metal: number;
  water: number;
  dominantElement: FiveElement;
  deficientElement: FiveElement;
}

/**
 * 阴阳平衡分析结果接口
 */
export interface YinYangAnalysis {
  yin: number;
  yang: number;
  balance: YinYangBalance;
}

/**
 * 脏腑分析结果接口
 */
export interface OrganAnalysis {
  heart: number;
  liver: number;
  spleen: number;
  lung: number;
  kidney: number;
  stomach: number;
  gallbladder: number;
  anomalies: string[];
}

/**
 * 身体状况分析结果接口
 */
export interface BodyConditionAnalysis {
  balance: {
    yinYang: YinYangAnalysis;
    fiveElements: FiveElementsAnalysis;
    organs: OrganAnalysis;
  };
  energyLevel: number;
  constitutionType: ConstitutionType | string;
}

/**
 * 四诊合参综合分析结果接口
 */
export interface IntegratedAssessment {
  timestamp: Date;
  summary: string;
  bodyCondition: BodyConditionAnalysis;
  healthSuggestions: string[];
  diagnosticConfidence: number;
}

/**
 * 四诊合参数据接口
 */
export interface FourDiagnosisData {
  patientId: string;
  diagnosisId: string;
  timestamp: Date;
  looking?: DiagnosisAnalysis;
  smell?: DiagnosisAnalysis;
  inquiry?: DiagnosisAnalysis;
  touch?: DiagnosisAnalysis;
  integratedAssessment?: IntegratedAssessment;
}

/**
 * 四诊协调请求接口
 */
export interface FourDiagnosisRequest {
  patientId: string;
  diagnosisTypes?: DiagnosisType[];
  startDate?: string;
  endDate?: string;
}

/**
 * 四诊协调响应接口
 */
export interface FourDiagnosisResponse {
  success: boolean;
  message: string;
  data?: FourDiagnosisData;
  errors?: string[];
}

/**
 * 望诊数据接口
 */
export interface LookingDiagnosisData {
  patientId: string;
  timestamp: Date;
  rawData: {
    faceColor?: string;
    tongueColor?: string;
    tongueCoating?: string;
    eyeCondition?: string;
    bodyShape?: string;
    skinCondition?: string;
    lipColor?: string;
    nail?: string;
    other?: any;
  };
  images?: {
    face?: string;
    tongue?: string;
    eyes?: string;
    fullBody?: string;
  };
  overallAssessment: string;
  analyzedBy: DiagnosisSource;
}

/**
 * 闻诊数据接口
 */
export interface SmellDiagnosisData {
  patientId: string;
  timestamp: Date;
  rawData: {
    bodyOdor?: string;
    breathOdor?: string;
    excretionOdor?: string;
    secretionOdor?: string;
    other?: any;
  };
  audioRecordings?: {
    breathing?: string;
    coughing?: string;
    voice?: string;
  };
  overallAssessment: string;
  analyzedBy: DiagnosisSource;
}

/**
 * 问诊数据接口
 */
export interface InquiryDiagnosisData {
  patientId: string;
  timestamp: Date;
  rawData: {
    chiefComplaint?: string;
    medicalHistory?: string[];
    familyHistory?: string[];
    emotionalState?: string;
    sleepQuality?: string;
    appetiteLevel?: string;
    urination?: string;
    bowelMovements?: string;
    menstruation?: string;
    painAreas?: string[];
    symptoms?: string[];
    energyLevel?: string;
    preferences?: {
      temperature?: string;
      food?: string;
      flavor?: string;
      season?: string;
    }
  };
  conversationRecord?: string;
  overallAssessment: string;
  analyzedBy: DiagnosisSource;
}

/**
 * 切诊数据接口
 */
export interface TouchDiagnosisData {
  patientId: string;
  timestamp: Date;
  rawData: {
    pulseType?: string;
    pulseStrength?: string;
    pulseRhythm?: string;
    pulseDepth?: string;
    touchSensitiveAreas?: string[];
    skinTemperature?: string;
    skinMoisture?: string;
    skinTexture?: string;
    abdominalExamination?: string;
    other?: any;
  };
  pulseRecords?: {
    leftCun?: string;
    leftGuan?: string;
    leftChi?: string;
    rightCun?: string;
    rightGuan?: string;
    rightChi?: string;
  };
  overallAssessment: string;
  analyzedBy: DiagnosisSource;
}

/**
 * 诊断来源枚举
 */
export enum DiagnosisSource {
  AI_MODEL = 'ai_model',         // AI模型
  TRADITIONAL_DOCTOR = 'doctor', // 传统医生
  PATIENT_SELF = 'patient',      // 患者自诊
  DEVICE = 'device'              // 设备测量
}

/**
 * 五行分析结果接口
 */
export interface FivePhasesAnalysisResult {
  wood: number;          // 木元素值
  fire: number;          // 火元素值
  earth: number;         // 土元素值
  metal: number;         // 金元素值
  water: number;         // 水元素值
  dominantElement: FiveElement;  // 优势元素
  deficientElement: FiveElement; // 不足元素
  imbalances: string[];  // 失衡描述
  [key: string]: any;    // 允许索引访问
}

/**
 * 脏腑平衡结果接口
 */
export interface OrganBalanceResult {
  heart: number;         // 心
  liver: number;         // 肝
  spleen: number;        // 脾
  lung: number;          // 肺
  kidney: number;        // 肾
  stomach: number;       // 胃
  gallbladder: number;   // 胆
  smallIntestine?: number; // 小肠
  largeIntestine?: number; // 大肠
  bladder?: number;      // 膀胱
  anomalies: string[];   // 异常情况描述
  [key: string]: any;    // 允许索引访问
}

/**
 * 阴阳平衡结果接口
 */
export interface YinYangBalanceResult {
  yinValue: number;      // 阴值
  yangValue: number;     // 阳值
  balance: YinYangBalance; // 平衡状态
  description: string;   // 状态描述
}

/**
 * 综合分析结果接口
 */
export interface IntegratedAssessmentResult {
  timestamp: Date;
  summary: string;       // 总结
  bodyCondition: {
    balance: {
      yinYang: YinYangBalanceResult;      // 阴阳平衡
      fiveElements: FivePhasesAnalysisResult; // 五行分析
      organs: OrganBalanceResult;        // 脏腑平衡
    };
    energyLevel: number;                 // 能量水平
    constitutionType: ConstitutionType;  // 体质类型
  };
  healthSuggestions: HealthSuggestion[]; // 健康建议
  diagnosticConfidence: number;          // 诊断置信度 (0-100)
  usedDiagnostics: DiagnosisType[];      // 使用的诊断类型
}

/**
 * 健康建议接口
 */
export interface HealthSuggestion {
  category: SuggestionCategory;  // 建议类别
  content: string;               // 建议内容
  priority: 'high' | 'medium' | 'low'; // 优先级
  reasoningBasis: string;        // 建议依据
}

/**
 * 建议类别枚举
 */
export enum SuggestionCategory {
  DIET = 'diet',             // 饮食
  EXERCISE = 'exercise',     // 运动
  LIFESTYLE = 'lifestyle',   // 生活方式
  HERBAL = 'herbal',         // 草药
  ACUPUNCTURE = 'acupuncture', // 针灸
  MEDITATION = 'meditation', // 冥想
  SLEEP = 'sleep',           // 睡眠
  EMOTIONAL = 'emotional'    // 情绪管理
}

/**
 * 患者诊断结果
 */
export interface PatientDiagnosisResult {
  patientId: string;
  assessmentId: string;
  timestamp: Date;
  integratedAssessment: IntegratedAssessmentResult;
  rawData: FourDiagnosisData;
  diagnosisConfidence: number;
  constitutionHistory?: {
    timestamp: Date;
    constitutionType: ConstitutionType;
    mainImbalances: string[];
  }[];
}

/**
 * 四诊协调请求接口
 */
export interface FourDiagnosisCoordinatorRequest {
  patientId: string;
  lookingDiagnosisId?: string;
  smellDiagnosisId?: string;
  inquiryDiagnosisId?: string;
  touchDiagnosisId?: string;
  includeRawData?: boolean;
  includeHealthSuggestions?: boolean;
  includeHistoricalData?: boolean;
}

/**
 * 四诊协调响应接口
 */
export interface FourDiagnosisCoordinatorResponse {
  success: boolean;
  data?: PatientDiagnosisResult;
  error?: {
    message: string;
    code: number;
    details?: any;
  };
  metadata: {
    processingTime: number;
    requestId: string;
    timestamp: Date;
  };
} 