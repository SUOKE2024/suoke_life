/**
 * 望诊分析接口定义
 */

// 面部分析结果接口
export interface FaceAnalysisResult {
  id: string;
  userId: string;
  timestamp: Date;
  imageUrl?: string;
  imagePath?: string;
  faceDetected: boolean;
  faceFeatures?: FaceFeatures;
  tcmAnalysis?: TcmAnalysis;
  fiveElementsAnalysis?: FiveElementsAnalysis;
  spiritAnalysis?: SpiritAnalysis;
  threeZonesAnalysis?: ThreeZonesAnalysis;
  textureAnalysis?: TextureAnalysis;
  faceProportionAnalysis?: FaceProportionAnalysis;
  confidence: number;
  processingTime: number;
}

// 舌象分析结果接口
export interface TongueAnalysisResult {
  id: string;
  userId: string;
  timestamp: Date;
  imageUrl?: string;
  imagePath?: string;
  tongueDetected: boolean;
  tongueFeatures?: TongueFeatures;
  tcmAnalysis?: TcmAnalysis;
  confidence: number;
  processingTime: number;
}

// 综合诊断结果接口
export interface DiagnosticResult {
  id: string;
  userId: string;
  timestamp: Date;
  sources: {
    face?: string;
    tongue?: string;
    eye?: string;
    posture?: boolean;
    userSymptoms?: boolean;
    physique?: boolean;
    dynamicBehavior?: boolean;
  };
  constitutionAnalysis: ConstitutionAnalysis;
  healthStatus: HealthStatus;
  physiqueAnalysis?: PhysiqueAnalysis;
  dynamicFeaturesAnalysis?: DynamicFeaturesAnalysis;
  recommendations?: Recommendation[];
  confidence: number;
}

// 面部特征接口
export interface FaceFeatures {
  complexion: {
    main: string;
    secondary?: string;
    brightness: number;
    uniformity: number;
    regions?: {
      forehead: string;
      cheeks: string;
      nose: string;
      chin: string;
      around_eyes: string;
    };
  };
  eyeFeatures?: {
    color: string;
    clarity: number;
    moisture: number;
    redness: number;
  };
  facialLandmarks?: {
    eyeBrowShape: string;
    eyeShape: string;
    noseShape: string;
    lipColor: string;
    lipMoisture: number;
  };
  facialExpression?: {
    main: string;
    energy: number;
    tension: number;
  };
}

// 舌象特征接口
export interface TongueFeatures {
  tongueBody: {
    color: string;
    shape: string;
    cracks?: string[];
    spots?: string[];
    toothMarks: boolean;
    moisture: number;
  };
  tongueCoating: {
    color: string;
    thickness: number;
    distribution: string;
    rootAttachment: number; // 0-1, 表示舌苔根部附着程度
  };
  tongueMovement?: {
    flexibility: number;
    tremor: boolean;
    deviation?: 'left' | 'right' | 'none';
  };
  // 新增区域分析
  regionalAnalysis?: {
    tip: {
      color: string;
      features: string[];
      organRelation: string; // 心
    },
    center: {
      color: string;
      features: string[];
      organRelation: string; // 脾胃
    },
    sides: {
      color: string;
      features: string[];
      organRelation: string; // 肝胆
    },
    root: {
      color: string;
      features: string[];
      organRelation: string; // 肾
    }
  };
  // 新增病机推断
  pathogenicMechanism?: {
    externalPathogens: string[];
    internalImbalance: string[];
    confidence: number;
  };
  // 新增微循环状态
  microcirculation?: {
    status: 'normal' | 'impaired' | 'severely_impaired';
    features: string[];
    confidence: number;
  };
}

// 中医分析结果接口
export interface TcmAnalysis {
  mainPattern: string; // 主要证型
  secondaryPatterns?: string[]; // 次要证型
  fiveElements?: {
    wood: number; // 木 (0-100)
    fire: number; // 火 (0-100)
    earth: number; // 土 (0-100)
    metal: number; // 金 (0-100)
    water: number; // 水 (0-100)
  };
  organImbalances?: string[]; // 脏腑失调
  explanation: string; // 中医理论解释
  confidence: number; // 置信度
}

// 体质分析接口
export interface ConstitutionAnalysis {
  primaryType: string; // 主要体质类型
  secondaryTypes?: string[]; // 次要体质类型
  constitutionScores: {
    [key: string]: number; // 各体质类型的分数 (0-100)
  };
  explanation: string; // 体质分析解释
  seasonalFactor?: string; // 季节性因素影响
  ageRelatedFactor?: string; // 年龄相关因素
}

// 健康状态接口
export interface HealthStatus {
  overall: number; // 综合健康评分 (0-100)
  aspects: {
    qi: number; // 气 (0-100)
    blood: number; // 血 (0-100)
    yin: number; // 阴 (0-100)
    yang: number; // 阳 (0-100)
  };
  imbalances: string[]; // 健康失衡点
  strengths: string[]; // 健康优势点
}

// 推荐建议接口
export interface Recommendation {
  type: 'diet' | 'lifestyle' | 'exercise' | 'acupoint' | 'herb' | 'prevention';
  title: string;
  description: string;
  priority: number; // 优先级 (1-5)
  seasonalAdjustment?: string; // 季节性调整建议
  items?: {
    name: string;
    description?: string;
    frequency?: string;
    imageUrl?: string;
    contraindications?: string[];
  }[];
}

// 面部分析请求接口
export interface FaceAnalysisRequest {
  userId: string;
  imagePath?: string;
  imageUrl?: string;
  imageBase64?: string;
  includeFeatures?: boolean;
  includeTcmAnalysis?: boolean;
  // 新增面部分析请求参数
  includeFiveElements?: boolean; // 是否包含五行分析
  includeSpiritAnalysis?: boolean; // 是否包含神气分析
  includeThreeZones?: boolean; // 是否包含三停分析
  includeTextureAnalysis?: boolean; // 是否包含纹理分析
  includeFaceProportion?: boolean; // 是否包含面部比例分析
  highQualityAnalysis?: boolean; // 是否进行高质量分析（更高精度但更慢）
}

export interface TongueAnalysisRequest {
  userId: string;
  imagePath?: string;
  imageUrl?: string;
  includeFeatures?: boolean;
}

// 综合分析请求接口
export interface ComprehensiveAnalysisRequest {
  userId: string;
  faceImageId?: string;
  tongueImageId?: string;
  eyeImageId?: string;
  postureMeasurements?: any;
  userSymptoms?: any;
  includeRecommendations?: boolean;
  // 新增参数
  physiqueData?: any; // 形体数据
  dynamicBehaviorData?: any; // 动态行为数据
  advancedAnalysisOptions?: {
    includeFiveElements?: boolean; // 是否包含五行分析
    includeSpiritAnalysis?: boolean; // 是否包含神气分析
    includeThreeZones?: boolean; // 是否包含三停分析
    includeTextureAnalysis?: boolean; // 是否包含纹理分析
    includePhysiqueAnalysis?: boolean; // 是否包含形体分析
    includeDynamicFeatures?: boolean; // 是否包含动态特征分析
    includeFaceProportion?: boolean; // 是否包含面部比例分析
  };
}

// 分页查询参数
export interface PaginationOptions {
  page: number;
  limit: number;
  type?: string;
}

// 体质信息接口
export interface ConstitutionInfo {
  type: string;
  chineseName: string;
  englishName?: string;
  description: string;
  characteristics: string[];
  causesAndPathogenesis: string;
  tendencies: string[];
  recommendations: {
    diet: string[];
    lifestyle: string[];
    exercise: string[];
    seasonal: {
      spring: string[];
      summer: string[];
      autumn: string[];
      winter: string[];
    };
  };
  relatedPatterns: string[];
  acupointRecommendations?: string[];
}

// 分页结果接口
export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// 新增：面部五行分析接口
export interface FiveElementsAnalysis {
  waterArea?: { // 水区-额头
    features: string[];
    abnormalities: string[];
    score: number; // 0-100，越低越异常
  };
  woodArea?: { // 木区-两颊
    features: string[];
    abnormalities: string[];
    score: number;
  };
  fireArea?: { // 火区-口唇
    features: string[];
    abnormalities: string[];
    score: number;
  };
  earthArea?: { // 土区-鼻部
    features: string[];
    abnormalities: string[];
    score: number;
  };
  metalArea?: { // 金区-下巴
    features: string[];
    abnormalities: string[];
    score: number;
  };
  organRelations: {
    [key: string]: string[]; // 区域对应的脏腑
  };
  overallScore: number; // 0-100
  confidence: number;
}

// 新增：神气分析接口
export interface SpiritAnalysis {
  spiritStatus: {
    status: string; // 神气状态：神气充足/神气不足/神散/神乱/神衰
    score: number; // 0-100
    features: string[];
  };
  eyeVitality: {
    status: string; // 目光状态
    score: number; // 0-100
    features: string[];
  };
  emotionalState: {
    dominantEmotion: string; // 主导情绪：喜/怒/忧/思/悲/恐/惊
    secondaryEmotions: string[]; // 次要情绪
    microExpressions: string[]; // 微表情
    score: number; // 0-100
  };
  overallScore: number; // 0-100
  confidence: number;
}

// 新增：三停五骨分析接口
export interface ThreeZonesAnalysis {
  zones: {
    upperZone: { // 上停-额
      features: string[];
      score: number; // 0-100
      lifeStage: string; // 少年时期
    };
    middleZone: { // 中停-鼻
      features: string[];
      score: number; // 0-100
      lifeStage: string; // 中年时期
    };
    lowerZone: { // 下停-颌
      features: string[];
      score: number; // 0-100
      lifeStage: string; // 老年时期
    };
  };
  boneFeatures: {
    features: string[]; // 骨相特征
    analysis: string; // 骨相分析
  };
  overallScore: number; // 0-100
  confidence: number;
}

// 新增：面部纹理分析接口
export interface TextureAnalysis {
  wrinkles: {
    [key: string]: { // 纹理名称
      location: string; // 位置
      depth: string; // 深度：浅表/中度/深度
      organRelations: string[]; // 相关脏腑
      emotionRelations: string[]; // 相关情绪
      score: number; // 0-100
    };
  };
  specialTextures: {
    [key: string]: { // 特殊纹理名称
      features: string[];
      implications: string[]; // 健康含义
      score: number; // 0-100
    };
  };
  overallScore: number; // 0-100
  confidence: number;
}

// 新增：形体气质分析接口
export interface PhysiqueAnalysis {
  bodyType: {
    mainType: string; // 主要体质类型
    secondaryTypes: string[]; // 次要体质类型
    score: number; // 0-100
  };
  boneFeatures: {
    features: string[];
    analysis: string;
    score: number; // 0-100
  };
  postureFeatures: {
    features: string[];
    analysis: string;
    score: number; // 0-100
  };
  bodyShape: {
    type: string;
    features: string[];
    score: number; // 0-100
  };
  temperament: {
    traits: string[]; // 气质特征
    analysis: string;
  };
  overallScore: number; // 0-100
  confidence: number;
}

// 新增：动态特征分析接口
export interface DynamicFeaturesAnalysis {
  behavior: {
    speechPatterns: {
      features: string[];
      analysis: string;
    };
    movements: {
      features: string[];
      analysis: string;
    };
    expressions: {
      features: string[];
      analysis: string;
    };
    score: number; // 0-100
  };
  microExpressions: {
    observed: string[];
    analysis: string;
    score: number; // 0-100
  };
  breathingPatterns: {
    pattern: string;
    features: string[];
    implications: string[];
    score: number; // 0-100
  };
  voiceFeatures?: {
    features: string[];
    analysis: string;
    score: number; // 0-100
  };
  overallScore: number; // 0-100
  confidence: number;
}

// 新增：面部比例分析接口
export interface FaceProportionAnalysis {
  faceShape: {
    shape: string; // 面型
    features: string[];
    analysis: string;
  };
  proportions: {
    threeZonesRatio: string; // 三停比例
    facialSymmetry: {
      level: string; // 对称性水平
      score: number; // 0-100
      features: string[];
    };
    goldenRatio: {
      status: string; // 是否符合黄金比例
      score: number; // 0-100
      areas: string[]; // 符合的面部区域
    };
    featuresHarmony: {
      status: string; // 五官协调状态
      score: number; // 0-100
      features: string[];
    };
  };
  overallScore: number; // 0-100
  confidence: number;
} 