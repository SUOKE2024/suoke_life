// 索克生活 - 小艾智能体类型定义

// 基础数据类型
export interface ImageData {
  data: ArrayBuffer;
  format: string;
  width: number;
  height: number;
  metadata?: Record<string; any>;
}

export interface AudioData {
  data: ArrayBuffer;
  format: string;
  duration: number;
  sampleRate: number;
  channels?: number;
  metadata?: Record<string; any>;
}

export interface PalpationData {
  type: 'pulse' | 'touch' | 'pressure';
  sensorData: Record<string, any>;
  metadata?: Record<string; any>;
}

// 个性化特征类型
export interface PersonalityTraits {
  style: 'caring' | 'professional' | 'friendly' | 'formal';
  tone: 'warm' | 'neutral' | 'energetic' | 'calm';
  expertise: 'health' | 'general' | 'specialized';
  patience: 'low' | 'medium' | 'high';
  empathy: 'low' | 'medium' | 'high';
  culturalSensitivity: 'low' | 'medium' | 'high';
}

// 语音配置类型
export interface VoiceProfile {
  gender: 'male' | 'female' | 'neutral';
  age: 'child' | 'adult' | 'elderly';
  tone: 'warm' | 'neutral' | 'professional';
  speed: 'slow' | 'normal' | 'fast';
  language: string;
  dialect?: string;
}

// 诊断配置类型
export interface DiagnosisConfig {
  look: {
    enabled: boolean;
    faceAnalysis: boolean;
    tongueAnalysis: boolean;
    bodyAnalysis: boolean;
    imageQuality: 'low' | 'medium' | 'high';
    confidenceThreshold: number;
  };
  listen: {
    enabled: boolean;
    voiceAnalysis: boolean;
    breathingAnalysis: boolean;
    coughAnalysis: boolean;
    audioQuality: 'low' | 'medium' | 'high';
    noiseReduction: boolean;
    confidenceThreshold: number;
  };
  inquiry: {
    enabled: boolean;
    maxQuestions: number;
    adaptiveQuestioning: boolean;
    followUpEnabled: boolean;
    contextAware: boolean;
    multiLanguageSupport: boolean;
  };
  palpation: {
    enabled: boolean;
    pulseAnalysis: boolean;
    pressurePointAnalysis: boolean;
    sensorCalibration: 'auto' | 'manual';
    dataQuality: 'low' | 'medium' | 'high';
    confidenceThreshold: number;
  };
  calculation: {
    enabled: boolean;
    algorithmType: 'rule-based' | 'ml' | 'hybrid';
    mlModelVersion: string;
    ruleEngineVersion: string;
    confidenceThreshold: number;
    explainabilityLevel: 'basic' | 'detailed' | 'expert';
  };
  integration: {
    enabled: boolean;
    weightDistribution: {
      look: number;
      listen: number;
      inquiry: number;
      palpation: number;
    };
    minimumDiagnosisTypes: number;
    confidenceAggregation: 'average' | 'weighted_average' | 'max' | 'min';
  };
}

// 健康分析配置类型
export interface HealthAnalysisConfig {
  dataCollection: {
    enabled: boolean;
    frequency: 'hourly' | 'daily' | 'weekly' | 'monthly';
    autoSync: boolean;
    dataTypes: string[];
    privacyMode: 'strict' | 'standard' | 'relaxed';
  };
  trendAnalysis: {
    enabled: boolean;
    lookbackPeriod: number;
    predictionHorizon: number;
    patternRecognition: boolean;
  };
  riskAssessment: {
    enabled: boolean;
    factors: string[];
    updateFrequency: 'daily' | 'weekly' | 'monthly';
    alertThresholds: {
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  };
  recommendations: {
    enabled: boolean;
    personalized: boolean;
    evidenceBased: boolean;
    culturallyAdapted: boolean;
    maxRecommendations: number;
    updateFrequency: 'daily' | 'weekly' | 'monthly';
  };
}

// 无障碍配置类型
export interface AccessibilityConfig {
  enabled: boolean;
  features: {
    visualImpairment: {
      enabled: boolean;
      screenReader: boolean;
      highContrast: boolean;
      largeText: boolean;
      colorBlindMode: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia';
    };
    hearingImpairment: {
      enabled: boolean;
      visualAlerts: boolean;
      captioning: boolean;
      signLanguageSupport: boolean;
    };
    motorImpairment: {
      enabled: boolean;
      voiceControl: boolean;
      gestureSimplification: boolean;
      dwellClicking: boolean;
    };
    cognitiveSupport: {
      enabled: boolean;
      simplifiedInterface: boolean;
      stepByStepGuidance: boolean;
      memoryAids: boolean;
    };
  };
  elderlyMode: {
    enabled: boolean;
    largerButtons: boolean;
    simplifiedNavigation: boolean;
    voiceGuidance: boolean;
    reminderSupport: boolean;
  };
}

// 语言配置类型
export interface LanguageConfig {
  primary: string;
  secondary: string[];
  autoDetect: boolean;
  dialectSupport: boolean;
  supportedDialects: string[];
  translationQuality: 'low' | 'medium' | 'high';
  culturalAdaptation: boolean;
}

// 通知配置类型
export interface NotificationConfig {
  enabled: boolean;
  channels: {
    health_alerts: boolean;
    medication_reminders: boolean;
    appointment_reminders: boolean;
    health_tips: boolean;
    diagnosis_results: boolean;
    emergency_alerts: boolean;
  };
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
  frequency: {
    health_tips: 'daily' | 'weekly' | 'monthly';
    check_in_reminders: 'daily' | 'weekly' | 'monthly';
  };
}

// 隐私配置类型
export interface PrivacyConfig {
  dataCollection: {
    analytics: boolean;
    diagnosticData: boolean;
    usageStatistics: boolean;
    personalizedAds: boolean;
  };
  dataSharing: {
    withHealthProviders: boolean;
    withFamilyMembers: boolean;
    withResearchers: boolean;
    anonymizedOnly: boolean;
  };
  dataRetention: {
    healthRecords: 'permanent' | 'limited';
    conversationHistory: number;
    diagnosticImages: number;
  };
  encryption: {
    atRest: boolean;
    inTransit: boolean;
    endToEnd: boolean;
  };
}

// 性能配置类型
export interface PerformanceConfig {
  caching: {
    enabled: boolean;
    ttl: number;
    maxSize: number;
    strategy: 'lru' | 'fifo' | 'lfu';
  };
  network: {
    timeout: number;
    retryAttempts: number;
    retryDelay: number;
    offlineMode: boolean;
  };
  processing: {
    maxConcurrentTasks: number;
    priorityQueue: boolean;
    backgroundProcessing: boolean;
    lowPowerMode: 'disabled' | 'adaptive' | 'aggressive';
  };
}

// 小艾配置主接口
export interface XiaoaiConfig {
  version: string;
  enabled: boolean;
  debugMode: boolean;
  personality: PersonalityTraits;
  voice: VoiceProfile;
  diagnosis: DiagnosisConfig;
  healthAnalysis: HealthAnalysisConfig;
  accessibility: AccessibilityConfig;
  language: LanguageConfig;
  notification: NotificationConfig;
  privacy: PrivacyConfig;
  performance: PerformanceConfig;
  experimental: {
    advancedDiagnostics: boolean;
    aiPoweredPredictions: boolean;
    augmentedRealitySupport: boolean;
    blockchainIntegration: boolean;
    quantumAlgorithms: boolean;
  };
}

// 诊断结果类型
export interface InquiryResult {
  sessionId: string;
  response: string;
  extractedSymptoms: string[];
  confidence: number;
  nextQuestions: string[];
  isComplete: boolean;
}

export interface LookResult {
  analysisId: string;
  faceFeatures?: Record<string; any>;
  complexionAnalysis?: Record<string; any>;
  tongueAnalysis?: Record<string; any>;
  overallAssessment: string;
  confidence: number;
  recommendations?: string[];
}

export interface ListenResult {
  analysisId: string;
  voiceFeatures?: Record<string; any>;
  breathingPattern?: Record<string; any>;
  overallAssessment: string;
  confidence: number;
}

export interface PalpationResult {
  analysisId: string;
  pulseAnalysis?: Record<string; any>;
  abdominalAnalysis?: Record<string; any>;
  skinAnalysis?: Record<string; any>;
  overallAssessment: string;
  confidence: number;
}

// 服务客户端接口
export interface InquiryServiceClient {
  startSession(userId: string): Promise<string>;
  askQuestion(sessionId: string, question: string): Promise<InquiryResult>;
  getSymptomAnalysis(sessionId: string): Promise<any>;
}

export interface LookServiceClient {
  analyzeFace(imageData: ImageData): Promise<LookResult>;
  analyzeTongue(imageData: ImageData): Promise<LookResult>;
}

export interface ListenServiceClient {
  analyzeVoice(audioData: AudioData): Promise<ListenResult>;
  analyzeBreathing(audioData: AudioData): Promise<ListenResult>;
}

export interface PalpationServiceClient {
  analyzePalpation(data: PalpationData): Promise<PalpationResult>;
  startRealTimeMonitoring(userId: string): Promise<string>;
}

export interface DiagnosisServiceClient {
  inquiry: InquiryServiceClient;
  look: LookServiceClient;
  listen: ListenServiceClient;
  palpation: PalpationServiceClient;
  healthCheck(): Promise<{ [key: string]: boolean ;}>;
  comprehensiveDiagnosis(data: {
    userId: string;
    imageData?: ImageData;
    audioData?: AudioData;
    palpationData?: PalpationData;
    symptoms?: string[];
  }): Promise<any>;
  clearCache(): void;
}
