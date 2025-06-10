import AsyncStorage from '@react-native-async-storage/async-storage';
import React from 'react';
import { APP_CONFIG, CACHE_CONFIG } from '../../../constants/config';
import { usePerformanceMonitor } from '../../../hooks/usePerformanceMonitor';
import {
  AccessibilityConfig,
  DiagnosisConfig,
  HealthAnalysisConfig,
  LanguageConfig,
  NotificationConfig,
  PerformanceConfig,
  PersonalityTraits,
  PrivacyConfig,
  VoiceProfile,
  XiaoaiConfig,
} from '../types';

// 配置键前缀
const CONFIG_KEY_PREFIX = 'xiaoai_config_';
const CONFIG_VERSION = '1.0.0';

const DEFAULT_CONFIG: XiaoaiConfig = {
  version: CONFIG_VERSION,
  enabled: true,
  debugMode: false,
  personality: {
    style: 'caring',
    tone: 'warm',
    expertise: 'health',
    patience: 'high',
    empathy: 'high',
    culturalSensitivity: 'high',
  },
  voice: {
    gender: 'female',
    age: 'adult',
    tone: 'warm',
    speed: 'normal',
    language: 'zh',
    dialect: undefined,
  },
  diagnosis: {
    look: {
      enabled: true,
      faceAnalysis: true,
      tongueAnalysis: true,
      bodyAnalysis: true,
      imageQuality: 'high',
      confidenceThreshold: 0.7,
    },
    listen: {
      enabled: true,
      voiceAnalysis: true,
      breathingAnalysis: true,
      coughAnalysis: true,
      audioQuality: 'high',
      noiseReduction: true,
      confidenceThreshold: 0.7,
    },
    inquiry: {
      enabled: true,
      maxQuestions: 20,
      adaptiveQuestioning: true,
      followUpEnabled: true,
      contextAware: true,
      multiLanguageSupport: true,
    },
    palpation: {
      enabled: true,
      pulseAnalysis: true,
      pressurePointAnalysis: true,
      sensorCalibration: 'auto',
      dataQuality: 'high',
      confidenceThreshold: 0.7,
    },
    calculation: {
      enabled: true,
      algorithmType: 'hybrid',
      mlModelVersion: 'latest',
      ruleEngineVersion: 'v2',
      confidenceThreshold: 0.8,
      explainabilityLevel: 'detailed',
    },
    integration: {
      enabled: true,
      weightDistribution: {
        look: 0.25,
        listen: 0.25,
        inquiry: 0.25,
        palpation: 0.25,
      },
      minimumDiagnosisTypes: 2,
      confidenceAggregation: 'weighted_average',
    },
  },
  healthAnalysis: {
    dataCollection: {
      enabled: true,
      frequency: 'daily',
      autoSync: true,
      dataTypes: ['vitals', 'symptoms', 'lifestyle', 'environment'],
      privacyMode: 'standard',
    },
    trendAnalysis: {
      enabled: true,
      lookbackPeriod: 30, // 天
      predictionHorizon: 7, // 天
      patternRecognition: true,
    },
    riskAssessment: {
      enabled: true,
      factors: ['genetic', 'lifestyle', 'environmental', 'medical_history'],
      updateFrequency: 'weekly',
      alertThresholds: {
        low: 0.3,
        medium: 0.6,
        high: 0.8,
        critical: 0.95,
      },
    },
    recommendations: {
      enabled: true,
      personalized: true,
      evidenceBased: true,
      culturallyAdapted: true,
      maxRecommendations: 10,
      updateFrequency: 'daily',
    },
  },
  accessibility: {
    enabled: false,
    features: {
      visualImpairment: {
        enabled: false,
        screenReader: true,
        highContrast: false,
        largeText: false,
        colorBlindMode: 'none',
      },
      hearingImpairment: {
        enabled: false,
        visualAlerts: true,
        captioning: true,
        signLanguageSupport: false,
      },
      motorImpairment: {
        enabled: false,
        voiceControl: true,
        gestureSimplification: true,
        dwellClicking: false,
      },
      cognitiveSupport: {
        enabled: false,
        simplifiedInterface: true,
        stepByStepGuidance: true,
        memoryAids: true,
      },
    },
    elderlyMode: {
      enabled: false,
      largerButtons: true,
      simplifiedNavigation: true,
      voiceGuidance: true,
      reminderSupport: true,
    },
  },
  language: {
    primary: 'zh',
    secondary: [],
    autoDetect: true,
    dialectSupport: true,
    supportedDialects: ['mandarin', 'cantonese', 'shanghainese'],
    translationQuality: 'high',
    culturalAdaptation: true,
  },
  notification: {
    enabled: true,
    channels: {
      health_alerts: true,
      medication_reminders: true,
      appointment_reminders: true,
      health_tips: true,
      diagnosis_results: true,
      emergency_alerts: true,
    },
    quietHours: {
      enabled: true,
      start: '22:00',
      end: '08:00',
    },
    frequency: {
      health_tips: 'daily',
      check_in_reminders: 'weekly',
    },
  },
  privacy: {
    dataCollection: {
      analytics: true,
      diagnosticData: true,
      usageStatistics: true,
      personalizedAds: false,
    },
    dataSharing: {
      withHealthProviders: true,
      withFamilyMembers: false,
      withResearchers: false,
      anonymizedOnly: true,
    },
    dataRetention: {
      healthRecords: 'permanent',
      conversationHistory: 90, // 天
      diagnosticImages: 365, // 天
    },
    encryption: {
      atRest: true,
      inTransit: true,
      endToEnd: true,
    },
  },
  performance: {
    caching: {
      enabled: true,
      ttl: CACHE_CONFIG.TTL.MEDIUM,
      maxSize: 100 * 1024 * 1024, // 100MB
      strategy: 'lru',
    },
    network: {
      timeout: APP_CONFIG.AGENTS.RESPONSE_TIMEOUT,
      retryAttempts: 3,
      retryDelay: 1000,
      offlineMode: true,
    },
    processing: {
      maxConcurrentTasks: 5,
      priorityQueue: true,
      backgroundProcessing: true,
      lowPowerMode: 'adaptive',
    },
  },
  experimental: {
    advancedDiagnostics: false,
    aiPoweredPredictions: false,
    augmentedRealitySupport: false,
    blockchainIntegration: false,
    quantumAlgorithms: false,
  },
};

// 配置接口
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
  experimental: ExperimentalFeatures;
}

interface ExperimentalFeatures {
  advancedDiagnostics: boolean;
  aiPoweredPredictions: boolean;
  augmentedRealitySupport: boolean;
  blockchainIntegration: boolean;
  quantumAlgorithms: boolean;
}

/**
 * 小艾配置管理器
 * 负责管理小艾智能体的所有配置选项
 */
export class XiaoaiConfigManager {
  private config: XiaoaiConfig;
  private configCache: Map<string, any>;
  private listeners: Set<(config: XiaoaiConfig) => void>;
  private performanceMonitor: any;

  constructor() {
    this.config = { ...DEFAULT_CONFIG };
    this.configCache = new Map();
    this.listeners = new Set();
    this.performanceMonitor = usePerformanceMonitor();
    this.loadConfig();
  }

  /**
   * 加载配置
   */
  async loadConfig(): Promise<void> {
    try {
      const savedConfig = await AsyncStorage.getItem(
        `${CONFIG_KEY_PREFIX}main`
      );
      if (savedConfig) {
        const parsedConfig = JSON.parse(savedConfig);
        this.config = this.migrateConfig(parsedConfig);
      }
    } catch (error) {
      console.error('加载小艾配置失败:', error);
      this.config = { ...DEFAULT_CONFIG };
    }
  }

  /**
   * 保存配置
   */
  async saveConfig(): Promise<void> {
    try {
      await AsyncStorage.setItem(
        `${CONFIG_KEY_PREFIX}main`,
        JSON.stringify(this.config)
      );
      this.notifyListeners();
    } catch (error) {
      console.error('保存小艾配置失败:', error);
      throw error;
    }
  }

  /**
   * 获取完整配置
   */
  getConfig(): XiaoaiConfig {
    return { ...this.config };
  }

  /**
   * 更新配置
   */
  async updateConfig(updates: Partial<XiaoaiConfig>): Promise<void> {
    this.config = { ...this.config, ...updates };
    await this.saveConfig();
  }

  /**
   * 重置配置
   */
  async resetConfig(): Promise<void> {
    this.config = { ...DEFAULT_CONFIG };
    await this.saveConfig();
  }

  /**
   * 获取特定配置值
   */
  getConfigValue(path: string): any {
    const keys = path.split('.');
    let current: any = this.config;

    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        return undefined;
      }
    }

    return current;
  }

  /**
   * 设置特定配置值
   */
  async setConfigValue(path: string, value: any): Promise<void> {
    const keys = path.split('.');
    const lastKey = keys.pop();
    let current: any = this.config;

    for (const key of keys) {
      if (!(key in current)) {
        current[key] = {};
      }
      current = current[key];
    }

    if (lastKey) {
      current[lastKey] = value;
      await this.saveConfig();
    }
  }

  /**
   * 检查功能是否启用
   */
  isFeatureEnabled(featurePath: string): boolean {
    const keys = featurePath.split('.');
    let current: any = this.config;

    for (const part of keys) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        return false;
      }
    }

    return current === true;
  }

  /**
   * 获取性能指标
   */
  getPerformanceMetrics(): {
    cacheHitRate: number;
    configSize: number;
    lastSaved: Date | null;
  } {
    const cacheSize = this.configCache.size;
    const totalKeys = Object.keys(this.config).length;

    return {
      cacheHitRate: totalKeys > 0 ? cacheSize / totalKeys : 0,
      configSize: JSON.stringify(this.config).length,
      lastSaved: new Date(),
    };
  }

  /**
   * 配置迁移
   */
  private migrateConfig(config: any): XiaoaiConfig {
    // 版本检查和迁移逻辑
    if (!config.version || config.version !== CONFIG_VERSION) {
      return this.migrateToLatest(config);
    }

    return config;
  }

  /**
   * 迁移到最新版本
   */
  private migrateToLatest(config: any): XiaoaiConfig {
    const migratedConfig = { ...DEFAULT_CONFIG };

    // 保留用户自定义的配置
    if (config.personality) {
      migratedConfig.personality = {
        ...migratedConfig.personality,
        ...config.personality,
      };
    }

    if (config.voice) {
      migratedConfig.voice = { ...migratedConfig.voice, ...config.voice };
    }

    // 更新版本号
    migratedConfig.version = CONFIG_VERSION;

    return migratedConfig;
  }

  /**
   * 添加配置监听器
   */
  addListener(listener: (config: XiaoaiConfig) => void): void {
    this.listeners.add(listener);
  }

  /**
   * 移除配置监听器
   */
  removeListener(listener: (config: XiaoaiConfig) => void): void {
    this.listeners.delete(listener);
  }

  /**
   * 通知所有监听器
   */
  private notifyListeners(): void {
    this.listeners.forEach((listener) => {
      try {
        listener(this.config);
      } catch (error) {
        console.error('配置监听器执行失败:', error);
      }
    });
  }

  /**
   * 验证配置
   */
  validateConfig(config: Partial<XiaoaiConfig>): boolean {
    // 基本验证逻辑
    if (config.personality && typeof config.personality !== 'object') {
      return false;
    }

    if (config.voice && typeof config.voice !== 'object') {
      return false;
    }

    return true;
  }

  /**
   * 导出配置
   */
  exportConfig(): string {
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * 导入配置
   */
  async importConfig(configJson: string): Promise<void> {
    try {
      const importedConfig = JSON.parse(configJson);

      if (this.validateConfig(importedConfig)) {
        this.config = this.migrateConfig(importedConfig);
        await this.saveConfig();
      } else {
        throw new Error('配置格式无效');
      }
    } catch (error) {
      console.error('导入配置失败:', error);
      throw error;
    }
  }
}

// 单例实例
export const xiaoaiConfigManager = new XiaoaiConfigManager();

// React Hook
export const useXiaoaiConfig = () => {
  const [config, setConfig] = React.useState<XiaoaiConfig>(
    xiaoaiConfigManager.getConfig()
  );

  React.useEffect(() => {
    const listener = (newConfig: XiaoaiConfig) => {
      setConfig(newConfig);
    };

    xiaoaiConfigManager.addListener(listener);

    return () => {
      xiaoaiConfigManager.removeListener(listener);
    };
  }, []);

  const updateConfig = React.useCallback(
    async (updates: Partial<XiaoaiConfig>) => {
      await xiaoaiConfigManager.updateConfig(updates);
    },
    []
  );

  const resetConfig = React.useCallback(async () => {
    await xiaoaiConfigManager.resetConfig();
  }, []);

  return {
    config,
    updateConfig,
    resetConfig,
    isFeatureEnabled:
      xiaoaiConfigManager.isFeatureEnabled.bind(xiaoaiConfigManager),
    getConfigValue:
      xiaoaiConfigManager.getConfigValue.bind(xiaoaiConfigManager),
    setConfigValue:
      xiaoaiConfigManager.setConfigValue.bind(xiaoaiConfigManager),
  };
};
