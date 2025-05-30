/**
 * 中医五诊算法配置管理
 *
 * 提供统一的配置管理接口，支持动态配置更新和环境适配
 *
 * @author 索克生活技术团队
 * @version 1.0.0
 */

export interface AlgorithmConfigOptions {
  version?: string;
  startTime?: number;

  // 各诊法配置
  looking?: LookingConfig;
  listening?: ListeningConfig;
  inquiry?: InquiryConfig;
  palpation?: PalpationConfig;
  calculation?: CalculationConfig;

  // 融合和分析配置
  fusion?: FusionConfig;
  syndrome?: SyndromeConfig;
  constitution?: ConstitutionConfig;
  treatment?: TreatmentConfig;

  // 系统配置
  knowledgeBase?: KnowledgeBaseConfig;
  qualityControl?: QualityControlConfig;
  monitoring?: MonitoringConfig;

  // 性能配置
  performance?: PerformanceConfig;
}

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

export interface CalculationConfig {
  enabled: boolean;
  models: {
    lunarCalculation: ModelConfig;
    fiveElementsAnalysis: ModelConfig;
    yinYangAnalysis: ModelConfig;
  };
  calculation: {
    precision: number;
    timezone: string;
    calendar: "gregorian" | "lunar" | "both";
  };
  confidence: {
    threshold: number;
    historicalDepth: number;
  };
}

export interface FusionConfig {
  enabled: boolean;
  algorithm: "weighted_average" | "neural_fusion" | "bayesian_fusion";
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
    conflictResolution: "majority" | "confidence" | "expert_system";
  };
}

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

export interface ModelConfig {
  name: string;
  version: string;
  path: string;
  type: "tensorflow" | "pytorch" | "onnx" | "custom";
  device: "cpu" | "gpu" | "auto";
  batchSize: number;
  timeout: number;
}

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
    format: "json" | "csv" | "prometheus";
  };
}

export interface PerformanceConfig {
  maxConcurrentSessions: number;
  timeoutMs: number;
  retryAttempts: number;
  caching: {
    enabled: boolean;
    strategy: "lru" | "lfu" | "ttl";
    maxSize: number;
  };
  optimization: {
    parallelProcessing: boolean;
    gpuAcceleration: boolean;
    modelQuantization: boolean;
  };
}

/**
 * 算法配置管理类
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
    this.version = options.version || "1.0.0";
    this.startTime = options.startTime || Date.now();

    // 初始化各诊法配置
    this.looking = this.initializeLookingConfig(options.looking);
    this.listening = this.initializeListeningConfig(options.listening);
    this.inquiry = this.initializeInquiryConfig(options.inquiry);
    this.palpation = this.initializePalpationConfig(options.palpation);
    this.calculation = this.initializeCalculationConfig(options.calculation);

    // 初始化融合和分析配置
    this.fusion = this.initializeFusionConfig(options.fusion);
    this.syndrome = this.initializeSyndromeConfig(options.syndrome);
    this.constitution = this.initializeConstitutionConfig(options.constitution);
    this.treatment = this.initializeTreatmentConfig(options.treatment);

    // 初始化系统配置
    this.knowledgeBase = this.initializeKnowledgeBaseConfig(
      options.knowledgeBase
    );
    this.qualityControl = this.initializeQualityControlConfig(
      options.qualityControl
    );
    this.monitoring = this.initializeMonitoringConfig(options.monitoring);
    this.performance = this.initializePerformanceConfig(options.performance);
  }

  /**
   * 初始化望诊配置
   */
  private initializeLookingConfig(
    config?: Partial<LookingConfig>
  ): LookingConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        tongueAnalysis:
          config?.models?.tongueAnalysis ||
          this.getDefaultModelConfig("tongue_analysis"),
        faceAnalysis:
          config?.models?.faceAnalysis ||
          this.getDefaultModelConfig("face_analysis"),
        bodyAnalysis:
          config?.models?.bodyAnalysis ||
          this.getDefaultModelConfig("body_analysis"),
      },
      imageProcessing: {
        maxWidth: config?.imageProcessing?.maxWidth || 1920,
        maxHeight: config?.imageProcessing?.maxHeight || 1080,
        quality: config?.imageProcessing?.quality || 0.9,
        formats: config?.imageProcessing?.formats || ["jpg", "png", "webp"],
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.7,
        minSamples: config?.confidence?.minSamples || 3,
      },
    };
  }

  /**
   * 初始化闻诊配置
   */
  private initializeListeningConfig(
    config?: Partial<ListeningConfig>
  ): ListeningConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        voiceAnalysis:
          config?.models?.voiceAnalysis ||
          this.getDefaultModelConfig("voice_analysis"),
        breathingAnalysis:
          config?.models?.breathingAnalysis ||
          this.getDefaultModelConfig("breathing_analysis"),
        coughAnalysis:
          config?.models?.coughAnalysis ||
          this.getDefaultModelConfig("cough_analysis"),
      },
      audioProcessing: {
        sampleRate: config?.audioProcessing?.sampleRate || 44100,
        channels: config?.audioProcessing?.channels || 1,
        bitDepth: config?.audioProcessing?.bitDepth || 16,
        maxDuration: config?.audioProcessing?.maxDuration || 300,
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.6,
        minSamples: config?.confidence?.minSamples || 5,
      },
    };
  }

  /**
   * 初始化问诊配置
   */
  private initializeInquiryConfig(
    config?: Partial<InquiryConfig>
  ): InquiryConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        symptomAnalysis:
          config?.models?.symptomAnalysis ||
          this.getDefaultModelConfig("symptom_analysis"),
        nlpProcessing:
          config?.models?.nlpProcessing ||
          this.getDefaultModelConfig("nlp_processing"),
        semanticAnalysis:
          config?.models?.semanticAnalysis ||
          this.getDefaultModelConfig("semantic_analysis"),
      },
      textProcessing: {
        maxLength: config?.textProcessing?.maxLength || 10000,
        languages: config?.textProcessing?.languages || ["zh-CN", "en-US"],
        encoding: config?.textProcessing?.encoding || "utf-8",
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.8,
        minKeywords: config?.confidence?.minKeywords || 3,
      },
    };
  }

  /**
   * 初始化切诊配置
   */
  private initializePalpationConfig(
    config?: Partial<PalpationConfig>
  ): PalpationConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        pulseAnalysis:
          config?.models?.pulseAnalysis ||
          this.getDefaultModelConfig("pulse_analysis"),
        pressureAnalysis:
          config?.models?.pressureAnalysis ||
          this.getDefaultModelConfig("pressure_analysis"),
        temperatureAnalysis:
          config?.models?.temperatureAnalysis ||
          this.getDefaultModelConfig("temperature_analysis"),
      },
      sensorProcessing: {
        samplingRate: config?.sensorProcessing?.samplingRate || 1000,
        filterFrequency: config?.sensorProcessing?.filterFrequency || 50,
        calibration: config?.sensorProcessing?.calibration ?? true,
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.75,
        minDuration: config?.confidence?.minDuration || 30,
      },
    };
  }

  /**
   * 初始化算诊配置
   */
  private initializeCalculationConfig(
    config?: Partial<CalculationConfig>
  ): CalculationConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        lunarCalculation:
          config?.models?.lunarCalculation ||
          this.getDefaultModelConfig("lunar_calculation"),
        fiveElementsAnalysis:
          config?.models?.fiveElementsAnalysis ||
          this.getDefaultModelConfig("five_elements"),
        yinYangAnalysis:
          config?.models?.yinYangAnalysis ||
          this.getDefaultModelConfig("yin_yang"),
      },
      calculation: {
        precision: config?.calculation?.precision || 6,
        timezone: config?.calculation?.timezone || "Asia/Shanghai",
        calendar: config?.calculation?.calendar || "both",
      },
      confidence: {
        threshold: config?.confidence?.threshold || 0.85,
        historicalDepth: config?.confidence?.historicalDepth || 100,
      },
    };
  }

  /**
   * 初始化融合配置
   */
  private initializeFusionConfig(config?: Partial<FusionConfig>): FusionConfig {
    return {
      enabled: config?.enabled ?? true,
      algorithm: config?.algorithm || "neural_fusion",
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
        conflictResolution: config?.fusion?.conflictResolution || "confidence",
      },
    };
  }

  /**
   * 初始化辨证配置
   */
  private initializeSyndromeConfig(
    config?: Partial<SyndromeConfig>
  ): SyndromeConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        patternRecognition:
          config?.models?.patternRecognition ||
          this.getDefaultModelConfig("pattern_recognition"),
        syndromeClassification:
          config?.models?.syndromeClassification ||
          this.getDefaultModelConfig("syndrome_classification"),
      },
      analysis: {
        maxSyndromes: config?.analysis?.maxSyndromes || 5,
        minConfidence: config?.analysis?.minConfidence || 0.6,
        includeSubSyndromes: config?.analysis?.includeSubSyndromes ?? true,
      },
    };
  }

  /**
   * 初始化体质配置
   */
  private initializeConstitutionConfig(
    config?: Partial<ConstitutionConfig>
  ): ConstitutionConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        constitutionClassification:
          config?.models?.constitutionClassification ||
          this.getDefaultModelConfig("constitution_classification"),
        bodyTypeAnalysis:
          config?.models?.bodyTypeAnalysis ||
          this.getDefaultModelConfig("body_type_analysis"),
      },
      analysis: {
        constitutionTypes: config?.analysis?.constitutionTypes || [
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
        adaptiveWeighting: config?.analysis?.adaptiveWeighting ?? true,
        ageFactors: config?.analysis?.ageFactors ?? true,
      },
    };
  }

  /**
   * 初始化治疗配置
   */
  private initializeTreatmentConfig(
    config?: Partial<TreatmentConfig>
  ): TreatmentConfig {
    return {
      enabled: config?.enabled ?? true,
      models: {
        recommendationEngine:
          config?.models?.recommendationEngine ||
          this.getDefaultModelConfig("recommendation_engine"),
        herbFormulation:
          config?.models?.herbFormulation ||
          this.getDefaultModelConfig("herb_formulation"),
        lifestyleAdvice:
          config?.models?.lifestyleAdvice ||
          this.getDefaultModelConfig("lifestyle_advice"),
      },
      recommendation: {
        maxRecommendations: config?.recommendation?.maxRecommendations || 10,
        personalization: config?.recommendation?.personalization ?? true,
        safetyChecks: config?.recommendation?.safetyChecks ?? true,
      },
    };
  }

  /**
   * 初始化知识库配置
   */
  private initializeKnowledgeBaseConfig(
    config?: Partial<KnowledgeBaseConfig>
  ): KnowledgeBaseConfig {
    return {
      version: config?.version || "1.0.0",
      updateInterval: config?.updateInterval || 86400000, // 24小时
      sources: config?.sources || [
        "tcm_classics",
        "modern_research",
        "clinical_data",
      ],
      caching: {
        enabled: config?.caching?.enabled ?? true,
        ttl: config?.caching?.ttl || 3600000, // 1小时
        maxSize: config?.caching?.maxSize || 1000,
      },
    };
  }

  /**
   * 初始化质量控制配置
   */
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
        minConfidence: config?.thresholds?.minConfidence || 0.5,
        maxUncertainty: config?.thresholds?.maxUncertainty || 0.3,
        consistencyCheck: config?.thresholds?.consistencyCheck || 0.8,
      },
    };
  }

  /**
   * 初始化监控配置
   */
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
        interval: config?.reporting?.interval || 300000, // 5分钟
        destination: config?.reporting?.destination || "console",
        format: config?.reporting?.format || "json",
      },
    };
  }

  /**
   * 初始化性能配置
   */
  private initializePerformanceConfig(
    config?: Partial<PerformanceConfig>
  ): PerformanceConfig {
    return {
      maxConcurrentSessions: config?.maxConcurrentSessions || 100,
      timeoutMs: config?.timeoutMs || 30000,
      retryAttempts: config?.retryAttempts || 3,
      caching: {
        enabled: config?.caching?.enabled ?? true,
        strategy: config?.caching?.strategy || "lru",
        maxSize: config?.caching?.maxSize || 1000,
      },
      optimization: {
        parallelProcessing: config?.optimization?.parallelProcessing ?? true,
        gpuAcceleration: config?.optimization?.gpuAcceleration ?? false,
        modelQuantization: config?.optimization?.modelQuantization ?? false,
      },
    };
  }

  /**
   * 获取默认模型配置
   */
  private getDefaultModelConfig(modelName: string): ModelConfig {
    return {
      name: modelName,
      version: "1.0.0",
      path: `/models/${modelName}`,
      type: "tensorflow",
      device: "auto",
      batchSize: 32,
      timeout: 10000,
    };
  }

  /**
   * 更新配置
   */
  public update(newConfig: Partial<AlgorithmConfigOptions>): void {
    // 实现配置热更新逻辑
    // 注意：某些配置可能需要重启算法模块才能生效
    Object.assign(
      this,
      new AlgorithmConfig({
        ...this.toJSON(),
        ...newConfig,
      })
    );
  }

  /**
   * 导出配置为JSON
   */
  public toJSON(): AlgorithmConfigOptions {
    return {
      version: this.version,
      startTime: this.startTime,
      looking: this.looking,
      listening: this.listening,
      inquiry: this.inquiry,
      palpation: this.palpation,
      calculation: this.calculation,
      fusion: this.fusion,
      syndrome: this.syndrome,
      constitution: this.constitution,
      treatment: this.treatment,
      knowledgeBase: this.knowledgeBase,
      qualityControl: this.qualityControl,
      monitoring: this.monitoring,
      performance: this.performance,
    };
  }

  /**
   * 验证配置有效性
   */
  public validate(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // 验证权重总和
    const weights = this.fusion.weights;
    const totalWeight = Object.values(weights).reduce(
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

    confidenceThresholds.forEach((threshold, index) => {
      if (threshold < 0 || threshold > 1) {
        errors.push(
          `置信度阈值必须在0-1之间，诊法${index}的阈值为${threshold}`
        );
      }
    });

    // 验证性能配置
    if (this.performance.maxConcurrentSessions <= 0) {
      errors.push("最大并发会话数必须大于0");
    }

    if (this.performance.timeoutMs <= 0) {
      errors.push("超时时间必须大于0");
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

export default AlgorithmConfig;
