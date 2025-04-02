/**
 * 诊断相关接口定义
 */

export interface ITCMPattern {
  name: string;
  confidence: number;
  description: string;
  symptoms: string[];
}

export interface ICategorizedSymptom {
  category: string;
  symptoms: string[];
}

export interface IConstitutionAnalysis {
  primaryType: string;
  secondaryTypes: string[];
  description: string;
  constitutionScore: Record<string, number>;
}

export interface IHealthRecommendation {
  category: 'diet' | 'lifestyle' | 'exercise' | 'herbs' | 'acupuncture' | 'general';
  content: string;
  importance: 'high' | 'medium' | 'low';
}

export interface IWarningIndicator {
  level: 'low' | 'medium' | 'high';
  content: string;
  suggestedAction: string;
}

export interface IDiagnosisResult {
  diagnosisId: string;
  sessionId: string;
  userId: string;
  timestamp: Date;
  tcmPatterns: ITCMPattern[];
  categorizedSymptoms: ICategorizedSymptom[];
  constitutionAnalysis: IConstitutionAnalysis;
  recommendations: IHealthRecommendation[];
  summary: string;
  followUpQuestions: string[];
  warningIndicators: IWarningIndicator[];
  confidence: number;
  metadata: Record<string, any>;
}

export interface IDiagnosisCreate {
  sessionId: string;
  userId: string;
  includeRecommendations?: boolean;
  deepAnalysis?: boolean;
  metadata?: Record<string, any>;
}

export interface IDiagnosisResponse {
  diagnosisId: string;
  summary: string;
  tcmPatterns: ITCMPattern[];
  constitutionAnalysis: {
    primaryType: string;
    description: string;
  };
  recommendations: IHealthRecommendation[];
  warningIndicators: IWarningIndicator[];
}

/**
 * @swagger
 * components:
 *   schemas:
 *     TCMPatternAnalysis:
 *       type: object
 *       required:
 *         - id
 *         - userId
 *         - sessionId
 *         - mainPattern
 *         - createdAt
 *       properties:
 *         id:
 *           type: string
 *           description: 诊断分析ID
 *         userId:
 *           type: string
 *           description: 用户ID
 *         sessionId:
 *           type: string
 *           description: 问诊会话ID
 *         mainPattern:
 *           type: string
 *           description: 主要证型
 *         secondaryPatterns:
 *           type: array
 *           items:
 *             type: string
 *           description: 次要证型列表
 *         symptoms:
 *           type: array
 *           items:
 *             type: string
 *           description: 相关症状列表
 *         pulseAnalysis:
 *           type: object
 *           description: 脉诊分析结果
 *         tongueAnalysis:
 *           type: object
 *           description: 舌诊分析结果
 *         recommendation:
 *           $ref: '#/components/schemas/TCMRecommendation'
 *         createdAt:
 *           type: string
 *           format: date-time
 *           description: 创建时间
 *         updatedAt:
 *           type: string
 *           format: date-time
 *           description: 更新时间
 *
 *     TCMRecommendation:
 *       type: object
 *       properties:
 *         dietSuggestions:
 *           type: array
 *           items:
 *             type: string
 *           description: 饮食建议
 *         lifestyleSuggestions:
 *           type: array
 *           items:
 *             type: string
 *           description: 生活方式建议
 *         herbFormulas:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/HerbFormula'
 *           description: 中药方剂推荐
 *         acupointsPrescription:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/Acupoint'
 *           description: 穴位推荐
 *
 *     HerbFormula:
 *       type: object
 *       required:
 *         - name
 *         - herbs
 *       properties:
 *         name:
 *           type: string
 *           description: 方剂名称
 *         description:
 *           type: string
 *           description: 方剂描述
 *         herbs:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *               dosage:
 *                 type: string
 *           description: 组成的药材及用量
 *         usage:
 *           type: string
 *           description: 使用方法
 *
 *     Acupoint:
 *       type: object
 *       required:
 *         - name
 *         - meridian
 *       properties:
 *         name:
 *           type: string
 *           description: 穴位名称
 *         meridian:
 *           type: string
 *           description: 所属经络
 *         location:
 *           type: string
 *           description: 位置描述
 *         indication:
 *           type: string
 *           description: 适应症
 */

// 中医证型分析结果接口
export interface TCMPatternAnalysis {
  id: string;
  userId: string;
  sessionId: string;
  mainPattern: string;
  secondaryPatterns?: string[];
  symptoms: string[];
  pulseAnalysis?: PulseAnalysis;
  tongueAnalysis?: TongueAnalysis;
  recommendation?: TCMRecommendation;
  createdAt: Date;
  updatedAt?: Date;
}

// 脉诊分析结果
export interface PulseAnalysis {
  type: string;
  description: string;
  characteristics: string[];
  raw?: any; // 原始脉诊数据
}

// 舌诊分析结果
export interface TongueAnalysis {
  coatingColor: string;
  coatingThickness: string;
  bodyColor: string;
  shape: string;
  moisture: string;
  description: string;
  raw?: any; // 原始舌诊数据
}

// 中医调理建议
export interface TCMRecommendation {
  dietSuggestions?: string[];
  lifestyleSuggestions?: string[];
  herbFormulas?: HerbFormula[];
  acupointsPrescription?: Acupoint[];
}

// 中药方剂
export interface HerbFormula {
  name: string;
  description?: string;
  herbs: Herb[];
  usage?: string;
}

// 药材
export interface Herb {
  name: string;
  dosage?: string;
}

// 穴位
export interface Acupoint {
  name: string;
  meridian: string;
  location?: string;
  indication?: string;
}

// 诊断请求参数
export interface TCMPatternRequest {
  sessionId: string;
  userId: string;
  symptoms: string[];
  pulseData?: any;
  tongueData?: any;
}

// 诊断服务响应格式
export interface DiagnosisResponse {
  success: boolean;
  message: string;
  data: TCMPatternAnalysis | null;
}

// 诊断历史响应格式
export interface DiagnosisHistoryResponse {
  success: boolean;
  message: string;
  data: {
    total: number;
    offset: number;
    limit: number;
    results: TCMPatternAnalysis[];
  };
} 