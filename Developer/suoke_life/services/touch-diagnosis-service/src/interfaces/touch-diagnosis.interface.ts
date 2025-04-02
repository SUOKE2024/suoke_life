/**
 * 脉象类型枚举
 */
export enum PulseType {
  FLOATING = 'floating', // 浮脉
  SINKING = 'sinking',   // 沉脉
  SLOW = 'slow',         // 迟脉
  RAPID = 'rapid',       // 数脉
  SLIPPERY = 'slippery', // 滑脉
  ROUGH = 'rough',       // 涩脉
  WIRY = 'wiry',         // 弦脉
  SOFT = 'soft',         // 软脉
  FULL = 'full',         // 实脉
  EMPTY = 'empty',       // 虚脉
  LONG = 'long',         // 长脉
  SHORT = 'short',       // 短脉
  FAINT = 'faint',       // 微脉
  LARGE = 'large',       // 洪脉
  MODERATE = 'moderate', // 缓脉
  HASTY = 'hasty',       // 促脉
  INTERMITTENT = 'intermittent', // 代脉
  HIDDEN = 'hidden'      // 伏脉
}

/**
 * 腹诊发现类型枚举
 */
export enum AbdominalFindingType {
  TENDERNESS = 'tenderness',       // 压痛
  MASSES = 'masses',               // 包块
  BLOATING = 'bloating',           // 腹胀
  RIGIDITY = 'rigidity',           // 腹肌紧张
  FLUID = 'fluid',                 // 腹水
  NORMAL = 'normal',               // 正常
  COLD = 'cold',                   // 腹部畏寒
  HEAT = 'heat',                   // 腹部灼热
  PULSATION = 'pulsation'          // 搏动
}

/**
 * 触诊位置
 */
export enum TouchLocation {
  LEFT_WRIST = 'LEFT_WRIST',
  RIGHT_WRIST = 'RIGHT_WRIST',
  ABDOMEN = 'ABDOMEN'
}

/**
 * 脉位位置枚举
 */
export enum PulsePosition {
  LEFT_CUN = 'LEFT_CUN',  // 左寸
  LEFT_GUAN = 'LEFT_GUAN', // 左关
  LEFT_CHI = 'LEFT_CHI',  // 左尺
  RIGHT_CUN = 'RIGHT_CUN', // 右寸
  RIGHT_GUAN = 'RIGHT_GUAN', // 右关
  RIGHT_CHI = 'RIGHT_CHI'  // 右尺
}

/**
 * 脉诊深度枚举
 */
export enum PulseDepth {
  SUPERFICIAL = 'SUPERFICIAL', // 浮脉
  MIDDLE = 'MIDDLE',          // 中脉
  DEEP = 'DEEP'               // 沉脉
}

/**
 * 脉象特性枚举
 */
export enum PulseCharacteristic {
  FLOATING = 'FLOATING',       // 浮
  SINKING = 'SINKING',         // 沉
  SLOW = 'SLOW',               // 迟
  RAPID = 'RAPID',             // 数
  SURGING = 'SURGING',         // 洪
  FINE = 'FINE',               // 细
  EMPTY = 'EMPTY',             // 虚
  REPLETE = 'REPLETE',         // 实
  SLIPPERY = 'SLIPPERY',       // 滑
  ROUGH = 'ROUGH',             // 涩
  WIRY = 'WIRY',               // 弦
  TIGHT = 'TIGHT',             // 紧
  MODERATE = 'MODERATE',       // 缓
  SOGGY = 'SOGGY',             // 濡
  LEATHER = 'LEATHER',         // 革
  HIDDEN = 'HIDDEN',           // 伏
  INTERMITTENT = 'INTERMITTENT', // 代
  MOVING = 'MOVING'            // 动
}

/**
 * 脉搏强度枚举
 */
export enum PulseStrength {
  WEAK = 'WEAK',      // 弱
  MODERATE = 'MODERATE', // 中等
  STRONG = 'STRONG'   // 强
}

/**
 * 腹部区域枚举
 */
export enum AbdominalRegion {
  EPIGASTRIUM = 'EPIGASTRIUM',           // 上腹部
  RIGHT_HYPOCHONDRIUM = 'RIGHT_HYPOCHONDRIUM', // 右季肋部
  LEFT_HYPOCHONDRIUM = 'LEFT_HYPOCHONDRIUM',   // 左季肋部
  UMBILICAL = 'UMBILICAL',               // 脐部
  RIGHT_LUMBAR = 'RIGHT_LUMBAR',         // 右腰部
  LEFT_LUMBAR = 'LEFT_LUMBAR',           // 左腰部
  HYPOGASTRIUM = 'HYPOGASTRIUM',         // 下腹部
  RIGHT_ILIAC = 'RIGHT_ILIAC',           // 右下腹部
  LEFT_ILIAC = 'LEFT_ILIAC'              // 左下腹部
}

/**
 * 腹部状态枚举
 */
export enum AbdominalStatus {
  DISTENSION = 'DISTENSION',     // 胀满
  TENDERNESS = 'TENDERNESS',     // 压痛
  MASS = 'MASS',                 // 包块
  RIGIDITY = 'RIGIDITY',         // 僵硬
  FLUID = 'FLUID',               // 腹水
  GURGLING = 'GURGLING',         // 肠鸣
  PULSATION = 'PULSATION',       // 搏动
  NORMAL = 'NORMAL'              // 正常
}

/**
 * 脉诊数据接口
 */
export interface PulseType {
  position: TouchLocation;
  type: string;
  strength: string;
  rhythm: string;
  notes?: string;
}

/**
 * 腹诊发现接口
 */
export interface AbdominalFindingType {
  location: string;
  finding: string;
  severity: string;
  notes?: string;
}

/**
 * 触诊分析数据接口
 */
export interface TouchDiagnosisAnalysis {
  patientId: string;
  pulseFindings: PulseDiagnosisData[];
  abdominalFindings: AbdominalDiagnosisData[];
  overallAssessment: string;
  diagnosisTime: Date;
  practitionerId: string;
}

/**
 * 触诊请求接口
 */
export interface TouchDiagnosisRequest {
  patientId: string;
  practitioners: string;
  pulseData?: Partial<PulseDiagnosisData>[];
  abdominalData?: Partial<AbdominalDiagnosisData>[];
  notes?: string;
}

/**
 * 触诊响应接口
 */
export interface TouchDiagnosisResponse {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

/**
 * 触诊分析请求接口
 */
export interface AnalysisRequest {
  patientId: string;
  diagnosisId?: string;
}

/**
 * 触诊历史查询接口
 */
export interface HistoryQuery {
  patientId: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
} 