/**
 * 气息分析结果接口
 */
export interface SmellAnalysisResult {
  id: string;
  userId: string;
  timestamp: Date;
  smellType: SmellType;
  intensity: number;
  description: string;
  relatedConditions: string[];
  confidence: number;
  rawData?: any;
  metadata?: Record<string, any>;
}

/**
 * 气息类型枚举
 */
export enum SmellType {
  SOUR = 'sour',           // 酸气味
  SWEET = 'sweet',         // 甜气味
  BITTER = 'bitter',       // 苦气味
  FISHY = 'fishy',         // 腥气味
  FOUL = 'foul',           // 臭气味
  PUTRID = 'putrid',       // 腐气味
  SCORCHED = 'scorched',   // 焦气味
  FRAGRANT = 'fragrant',   // 芳香气味
  ROTTEN = 'rotten',       // 腐败气味
  NORMAL = 'normal',       // 正常气味
  OTHER = 'other'          // 其他气味
}

/**
 * 音频数据分析结果
 */
export interface AudioAnalysisResult {
  smellType: SmellType;
  intensity: number;
  confidence: number;
  features: Record<string, number>;
  duration: number;
}

/**
 * 闻诊分析请求接口
 */
export interface SmellDiagnosisRequest {
  userId: string;
  diagnosisType: SmellDiagnosisType;
  description?: string;
  metadata?: Record<string, any>;
  audioData?: Buffer;
  sampleType?: SampleType;
}

/**
 * 闻诊类型枚举
 */
export enum SmellDiagnosisType {
  BREATH = 'breath',           // 呼吸气味
  SWEAT = 'sweat',             // 汗液气味
  EXCRETION = 'excretion',     // 排泄物气味
  MOUTH = 'mouth',             // 口腔气味
  BODY = 'body',               // 体表气味
  SPECIAL = 'special'          // 特殊气味分析
}

/**
 * 样本类型枚举
 */
export enum SampleType {
  AUDIO = 'audio',             // 音频样本
  TEXT_DESCRIPTION = 'text',   // 文本描述
  PATIENT_REPORT = 'report'    // 患者报告
}

/**
 * 闻诊分析结果接口
 */
export interface SmellDiagnosisResult {
  id: string;
  userId: string;
  requestId: string;
  timestamp: Date;
  diagnosisType: SmellDiagnosisType;
  analysisResults: SmellAnalysisResult[];
  tcmImplications: TcmImplication[];
  recommendations: string[];
  confidence: number;
  metadata?: Record<string, any>;
}

/**
 * 中医理论意义接口
 */
export interface TcmImplication {
  aspect: TcmAspect;
  description: string;
  significance: number; // 0-10表示重要性
}

/**
 * 中医方面枚举
 */
export enum TcmAspect {
  FIVE_ELEMENTS = 'fiveElements',   // 五行
  YIN_YANG = 'yinYang',             // 阴阳
  SIX_EXCESSES = 'sixExcesses',     // 六淫
  SEVEN_EMOTIONS = 'sevenEmotions', // 七情
  ZANG_FU = 'zangFu',               // 脏腑
  QI_BLOOD = 'qiBlood',             // 气血
  MERIDIANS = 'meridians',          // 经络
  CONSTITUTION = 'constitution'     // 体质
} 