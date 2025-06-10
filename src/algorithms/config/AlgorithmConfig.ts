// 算法配置管理

// 模型配置接口
export interface ModelConfig {
  name: string;
  version: string;
  path: string;
  type: 'tensorflow' | 'pytorch' | 'onnx' | 'custom';
  device: 'cpu' | 'gpu' | 'auto';
  batchSize: number;
  timeout: number;
}

// 望诊配置
export interface LookingConfig {
  enabled: boolean;
  models: {
    tongueAnalysis: ModelConfig;
    faceAnalysis: ModelConfig;
    bodyAnalysis: ModelConfig;
  };
  imageProcessing: {
    maxWidth: number;
    maxHeight: number;
    quality: number;
    formats: string[];
  };
  confidence: {
    threshold: number;
    minSamples: number;
  };
}

// 闻诊配置
export interface ListeningConfig {
  enabled: boolean;
  models: {
    voiceAnalysis: ModelConfig;
    breathingAnalysis: ModelConfig;
    coughAnalysis: ModelConfig;
  };
  audioProcessing: {
    sampleRate: number;
    channels: number;
    bitDepth: number;
    maxDuration: number;
  };
  confidence: {
    threshold: number;
    minSamples: number;
  };
}

// 问诊配置
export interface InquiryConfig {
  enabled: boolean;
  models: {
    symptomAnalysis: ModelConfig;
    nlpProcessing: ModelConfig;
    semanticAnalysis: ModelConfig;
  };
  textProcessing: {
    maxLength: number;
    languages: string[];
    encoding: string;
  };
  confidence: {
    threshold: number;
    minKeywords: number;
  };
}

// 切诊配置
export interface PalpationConfig {
  enabled: boolean;
  models: {
    pulseAnalysis: ModelConfig;
    pressureAnalysis: ModelConfig;
    temperatureAnalysis: ModelConfig;
  };
  sensorProcessing: {
    samplingRate: number;
    filterFrequency: number;
    calibration: boolean;
  };
  confidence: {
    threshold: number;
    minDuration: number;
  };
}

// 运算配置
export interface CalculationConfig {
  enabled: boolean;
  models: {
    lunarCalculation: ModelConfig;
    fiveElementsAnalysis: ModelConfig;
    yinYangAnalysis: ModelConfig;
  };
  calendar: {
    type: 'gregorian' | 'lunar' | 'both';
  };
  confidence: {
    threshold: number;
    historicalDepth: number;
  };
}

// 融合配置
export interface FusionConfig {
  enabled: boolean;
  algorithm: 'weighted_average' | 'neural_fusion' | 'bayesian_fusion';
  weights: {
    looking: number;
    listening: number;
    inquiry: number;
    palpation: number;
    calculation: number;
  };
  fusion: {
    minDiagnoses: number;
    confidenceBoost: number;
    conflictResolution: 'majority' | 'confidence' | 'expert_system';
  };
}

// 证候配置
export interface SyndromeConfig {
  enabled: boolean;
  models: {
    patternRecognition: ModelConfig;
    syndromeClassification: ModelConfig;
  };
  analysis: {
    maxSyndromes: number;
    minConfidence: number;
    includeSubSyndromes: boolean;
  };
}

// 体质配置
export interface ConstitutionConfig {
  enabled: boolean;
  models: {
    constitutionClassification: ModelConfig;
    bodyTypeAnalysis: ModelConfig;
  };
  analysis: {
    constitutionTypes: string[];
    adaptiveWeighting: boolean;
    ageFactors: boolean;
  };
}

// 治疗配置
export interface TreatmentConfig {
  enabled: boolean;
  models: {
    recommendationEngine: ModelConfig;
    herbFormulation: ModelConfig;
    lifestyleAdvice: ModelConfig;
  };
  recommendation: {
    maxRecommendations: number;
    personalization: boolean;
    safetyChecks: boolean;
  };
}

// 知识库配置
export interface KnowledgeBaseConfig {
  version: string;
  updateInterval: number;
  sources: string[];
  caching: {
    enabled: boolean;
    ttl: number;
    maxSize: number;
  };
}

// 质量控制配置
export interface QualityControlConfig {
  enabled: boolean;
  checks: {
    dataValidation: boolean;
    resultValidation: boolean;
    crossValidation: boolean;
    expertReview: boolean;
  };
  thresholds: {
    minConfidence: number;
    maxUncertainty: number;
    consistencyCheck: number;
  };
}

// 监控配置
export interface MonitoringConfig {
  enabled: boolean;
  metrics: {
    performance: boolean;
    accuracy: boolean;
    usage: boolean;
    errors: boolean;
  };
  reporting: {
    interval: number;
    destination: string;
    format: 'json' | 'csv' | 'prometheus';
  };
}

// 性能配置
export interface PerformanceConfig {
  maxConcurrentSessions: number;
  timeoutMs: number;
  retryAttempts: number;
  caching: {
    enabled: boolean;
    strategy: 'lru' | 'lfu' | 'ttl';
    maxSize: number;
  };
  optimization: {
    parallelProcessing: boolean;
    gpuAcceleration: boolean;
    modelQuantization: boolean;
  };
}

// 算法配置选项
export interface AlgorithmConfigOptions {
  version?: string;
  startTime?: number;
  looking?: Partial<LookingConfig>;
  listening?: Partial<ListeningConfig>;
  inquiry?: Partial<InquiryConfig>;
  palpation?: Partial<PalpationConfig>;
  calculation?: Partial<CalculationConfig>;
  fusion?: Partial<FusionConfig>;
  syndrome?: Partial<SyndromeConfig>;
  constitution?: Partial<ConstitutionConfig>;
  treatment?: Partial<TreatmentConfig>;
  knowledgeBase?: Partial<KnowledgeBaseConfig>;
  qualityControl?: Partial<QualityControlConfig>;
  monitoring?: Partial<MonitoringConfig>;
  performance?: Partial<PerformanceConfig>;
}

/**
 * 算法配置管理类
 * 管理五诊算法的所有配置参数
 */
export class AlgorithmConfig {
  public readonly version: string;
  public readonly startTime: number;
  public readonly looking: LookingConfig;
  public readonly listening: ListeningConfig;
  public readonly inquiry: InquiryConfig;
  public readonly palpation: PalpationConfig;
  public readonly calculation: CalculationConfig;
  public readonly fusion: FusionConfig;
  public readonly syndrome: SyndromeConfig;
  public readonly constitution: ConstitutionConfig;
  public readonly treatment: TreatmentConfig;
  public readonly knowledgeBase: KnowledgeBaseConfig;
  public readonly qualityControl: QualityControlConfig;
  public readonly monitoring: MonitoringConfig;
  public readonly performance: PerformanceConfig;

  constructor(options: Partial<AlgorithmConfigOptions> = {}) {
    this.version = options.version || '1.0.0';
    this.startTime = options.startTime || Date.now();
    this.looking = this.initializeLookingConfig(options.looking);
    this.listening = this.initializeListeningConfig(options.listening);
    this.inquiry = this.initializeInquiryConfig(options.inquiry);
    this.palpation = this.initializePalpationConfig(options.palpation);
    this.calculation = this.initializeCalculationConfig(options.calculation);
    this.fusion = this.initializeFusionConfig(options.fusion);
    this.syndrome = this.initializeSyndromeConfig(options.syndrome);
    this.constitution = this.initializeConstitutionConfig(options.constitution);
    this.treatment = this.initializeTreatmentConfig(options.treatment);
    this.knowledgeBase = this.initializeKnowledgeBaseConfig(
      options.knowledgeBase
    );
    this.qualityControl = this.initializeQualityControlConfig(
      options.qualityControl
    );
    this.monitoring = this.initializeMonitoringConfig(options.monitoring);
    this.performance = this.initializePerformanceConfig(options.performance);
  }

  private initializeLookingConfig(
    config?: Partial<LookingConfig>
  ): LookingConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        tongueAnalysis:
          config?.models?.tongueAnalysis ||
          this.createDefaultModelConfig('tongue-analysis'),
        faceAnalysis:
          config?.models?.faceAnalysis ||
          this.createDefaultModelConfig('face-analysis'),
        bodyAnalysis:
          config?.models?.bodyAnalysis ||
          this.createDefaultModelConfig('body-analysis'),
      },
      imageProcessing: {
        maxWidth: config?.imageProcessing?.maxWidth || 1920,
        maxHeight: config?.imageProcessing?.maxHeight || 1080,
        quality: config?.imageProcessing?.quality || 0.8,
        formats: config?.imageProcessing?.formats || ['jpg', 'png', 'webp'],
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.7,
        minSamples: config?.confidence?.minSamples || 3,
      },
    };
  }

  private initializeListeningConfig(
    config?: Partial<ListeningConfig>
  ): ListeningConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        voiceAnalysis:
          config?.models?.voiceAnalysis ||
          this.createDefaultModelConfig('voice-analysis'),
        breathingAnalysis:
          config?.models?.breathingAnalysis ||
          this.createDefaultModelConfig('breathing-analysis'),
        coughAnalysis:
          config?.models?.coughAnalysis ||
          this.createDefaultModelConfig('cough-analysis'),
      },
      audioProcessing: {
        sampleRate: config?.audioProcessing?.sampleRate || 44100,
        channels: config?.audioProcessing?.channels || 1,
        bitDepth: config?.audioProcessing?.bitDepth || 16,
        maxDuration: config?.audioProcessing?.maxDuration || 60,
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.7,
        minSamples: config?.confidence?.minSamples || 3,
      },
    };
  }

  private initializeInquiryConfig(
    config?: Partial<InquiryConfig>
  ): InquiryConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        symptomAnalysis:
          config?.models?.symptomAnalysis ||
          this.createDefaultModelConfig('symptom-analysis'),
        nlpProcessing:
          config?.models?.nlpProcessing ||
          this.createDefaultModelConfig('nlp-processing'),
        semanticAnalysis:
          config?.models?.semanticAnalysis ||
          this.createDefaultModelConfig('semantic-analysis'),
      },
      textProcessing: {
        maxLength: config?.textProcessing?.maxLength || 5000,
        languages: config?.textProcessing?.languages || ['zh-CN', 'en'],
        encoding: config?.textProcessing?.encoding || 'utf-8',
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.7,
        minKeywords: config?.confidence?.minKeywords || 3,
      },
    };
  }

  private initializePalpationConfig(
    config?: Partial<PalpationConfig>
  ): PalpationConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        pulseAnalysis:
          config?.models?.pulseAnalysis ||
          this.createDefaultModelConfig('pulse-analysis'),
        pressureAnalysis:
          config?.models?.pressureAnalysis ||
          this.createDefaultModelConfig('pressure-analysis'),
        temperatureAnalysis:
          config?.models?.temperatureAnalysis ||
          this.createDefaultModelConfig('temperature-analysis'),
      },
      sensorProcessing: {
        samplingRate: config?.sensorProcessing?.samplingRate || 1000,
        filterFrequency: config?.sensorProcessing?.filterFrequency || 50,
        calibration: config?.sensorProcessing?.calibration ?? true,
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.7,
        minDuration: config?.confidence?.minDuration || 30,
      },
    };
  }

  private initializeCalculationConfig(
    config?: Partial<CalculationConfig>
  ): CalculationConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        lunarCalculation:
          config?.models?.lunarCalculation ||
          this.createDefaultModelConfig('lunar-calculation'),
        fiveElementsAnalysis:
          config?.models?.fiveElementsAnalysis ||
          this.createDefaultModelConfig('five-elements'),
        yinYangAnalysis:
          config?.models?.yinYangAnalysis ||
          this.createDefaultModelConfig('yin-yang'),
      },
      calendar: {
        type: config?.calendar?.type || 'both',
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.7,
        historicalDepth: config?.confidence?.historicalDepth || 365,
      },
    };
  }

  private initializeFusionConfig(config?: Partial<FusionConfig>): FusionConfig {
    return {
      enabled: config?.enabled ?? true,
      algorithm: config?.algorithm || 'weighted_average',
      weights: {
        looking: config?.weights?.looking || 0.25,
        listening: config?.weights?.listening || 0.2,
        inquiry: config?.weights?.inquiry || 0.3,
        palpation: config?.weights?.palpation || 0.15,
        calculation: config?.weights?.calculation || 0.1,
      },
      fusion: {
        minDiagnoses: config?.fusion?.minDiagnoses || 2,
        confidenceBoost: config?.fusion?.confidenceBoost || 0.1,
        conflictResolution: config?.fusion?.conflictResolution || 'confidence',
      },
    };
  }

  private initializeSyndromeConfig(
    config?: Partial<SyndromeConfig>
  ): SyndromeConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        patternRecognition:
          config?.models?.patternRecognition ||
          this.createDefaultModelConfig('pattern-recognition'),
        syndromeClassification:
          config?.models?.syndromeClassification ||
          this.createDefaultModelConfig('syndrome-classification'),
      },
      analysis: {
        maxSyndromes: config?.analysis?.maxSyndromes || 5,
        minConfidence: config?.analysis?.minConfidence || 0.6,
        includeSubSyndromes: config?.analysis?.includeSubSyndromes ?? true,
      },
    };
  }

  private initializeConstitutionConfig(
    config?: Partial<ConstitutionConfig>
  ): ConstitutionConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        constitutionClassification:
          config?.models?.constitutionClassification ||
          this.createDefaultModelConfig('constitution-classification'),
        bodyTypeAnalysis:
          config?.models?.bodyTypeAnalysis ||
          this.createDefaultModelConfig('body-type-analysis'),
      },
      analysis: {
        constitutionTypes: config?.analysis?.constitutionTypes || [
          '平和质',
          '气虚质',
          '阳虚质',
          '阴虚质',
          '痰湿质',
          '湿热质',
          '血瘀质',
          '气郁质',
          '特禀质',
        ],
        adaptiveWeighting: config?.analysis?.adaptiveWeighting ?? true,
        ageFactors: config?.analysis?.ageFactors ?? true,
      },
    };
  }

  private initializeTreatmentConfig(
    config?: Partial<TreatmentConfig>
  ): TreatmentConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        recommendationEngine:
          config?.models?.recommendationEngine ||
          this.createDefaultModelConfig('recommendation-engine'),
        herbFormulation:
          config?.models?.herbFormulation ||
          this.createDefaultModelConfig('herb-formulation'),
        lifestyleAdvice:
          config?.models?.lifestyleAdvice ||
          this.createDefaultModelConfig('lifestyle-advice'),
      },
      recommendation: {
        maxRecommendations: config?.recommendation?.maxRecommendations || 10,
        personalization: config?.recommendation?.personalization ?? true,
        safetyChecks: config?.recommendation?.safetyChecks ?? true,
      },
    };
  }

  private initializeKnowledgeBaseConfig(
    config?: Partial<KnowledgeBaseConfig>
  ): KnowledgeBaseConfig {
    return {
      version: config?.version || '1.0.0',
      updateInterval: config?.updateInterval || 86400000, // 24 hours
      sources: config?.sources || [
        'tcm_classics',
        'modern_research',
        'clinical_data',
      ],
      caching: {
        enabled: config?.caching?.enabled ?? true,
        ttl: config?.caching?.ttl || 3600000, // 1 hour
        maxSize: config?.caching?.maxSize || 1000,
      },
    };
  }

  private initializeQualityControlConfig(
    config?: Partial<QualityControlConfig>
  ): QualityControlConfig {
    return {
      enabled: config?.enabled ?? true,
      checks: {
        dataValidation: config?.checks?.dataValidation ?? true,
        resultValidation: config?.checks?.resultValidation ?? true,
        crossValidation: config?.checks?.crossValidation ?? true,
        expertReview: config?.checks?.expertReview ?? false,
      },
      thresholds: {
        minConfidence: config?.thresholds?.minConfidence || 0.6,
        maxUncertainty: config?.thresholds?.maxUncertainty || 0.4,
        consistencyCheck: config?.thresholds?.consistencyCheck || 0.8,
      },
    };
  }

  private initializeMonitoringConfig(
    config?: Partial<MonitoringConfig>
  ): MonitoringConfig {
    return {
      enabled: config?.enabled ?? true,
      metrics: {
        performance: config?.metrics?.performance ?? true,
        accuracy: config?.metrics?.accuracy ?? true,
        usage: config?.metrics?.usage ?? true,
        errors: config?.metrics?.errors ?? true,
      },
      reporting: {
        interval: config?.reporting?.interval || 300000, // 5 minutes
        destination: config?.reporting?.destination || 'console',
        format: config?.reporting?.format || 'json',
      },
    };
  }

  private initializePerformanceConfig(
    config?: Partial<PerformanceConfig>
  ): PerformanceConfig {
    return {
      maxConcurrentSessions: config?.maxConcurrentSessions || 100,
      timeoutMs: config?.timeoutMs || 30000,
      retryAttempts: config?.retryAttempts || 3,
      caching: {
        enabled: config?.caching?.enabled ?? true,
        strategy: config?.caching?.strategy || 'lru',
        maxSize: config?.caching?.maxSize || 1000,
      },
      optimization: {
        parallelProcessing: config?.optimization?.parallelProcessing ?? true,
        gpuAcceleration: config?.optimization?.gpuAcceleration ?? false,
        modelQuantization: config?.optimization?.modelQuantization ?? false,
      },
    };
  }

  private createDefaultModelConfig(name: string): ModelConfig {
    return {
      name,
      version: '1.0.0',
      path: `/models/${name}`,
      type: 'tensorflow',
      device: 'auto',
      batchSize: 32,
      timeout: 10000,
    };
  }

  // 获取配置摘要
  getConfigSummary(): Record<string, any> {
    return {
      version: this.version,
      startTime: this.startTime,
      enabledModules: {
        looking: this.looking.enabled,
        listening: this.listening.enabled,
        inquiry: this.inquiry.enabled,
        palpation: this.palpation.enabled,
        calculation: this.calculation.enabled,
        fusion: this.fusion.enabled,
        syndrome: this.syndrome.enabled,
        constitution: this.constitution.enabled,
        treatment: this.treatment.enabled,
      },
      performance: {
        maxConcurrentSessions: this.performance.maxConcurrentSessions,
        timeoutMs: this.performance.timeoutMs,
        cachingEnabled: this.performance.caching.enabled,
      },
    };
  }

  // 验证配置
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 验证权重总和
    const totalWeight = Object.values(this.fusion.weights).reduce(
      (sum, weight) => sum + weight,
      0
    );
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      errors.push(`融合权重总和应为1.0，当前为${totalWeight}`);
    }

    // 验证置信度阈值
    const confidenceThresholds = [
      this.looking.confidence.threshold,
      this.listening.confidence.threshold,
      this.inquiry.confidence.threshold,
      this.palpation.confidence.threshold,
      this.calculation.confidence.threshold,
    ];

    for (const threshold of confidenceThresholds) {
      if (threshold < 0 || threshold > 1) {
        errors.push(`置信度阈值应在0-1之间，当前为${threshold}`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// 默认配置实例
export const defaultAlgorithmConfig = new AlgorithmConfig();

// 配置工厂函数
export function createAlgorithmConfig(
  options?: Partial<AlgorithmConfigOptions>
): AlgorithmConfig {
  return new AlgorithmConfig(options);
}

export default AlgorithmConfig;
