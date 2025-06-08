/**
* 索克生活应用配置管理系统
* 统一管理前端应用的所有配置项
*/
import React from 'react';
import { Platform } from 'react-native';
// 环境类型
export type Environment = 'development' | 'staging' | 'production';
// API配置接口
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  enableMocking: boolean;
}
// 智能体配置接口
export interface AgentConfig {
  xiaoai: {;
  enabled: boolean;
    endpoint: string;
  timeout: number;
    maxSessions: number;
};
  xiaoke: {,
  enabled: boolean;
    endpoint: string,
  timeout: number;
    maxSessions: number;
  };
  laoke: {,
  enabled: boolean;
    endpoint: string,
  timeout: number;
    maxSessions: number;
  };
  soer: {,
  enabled: boolean;
    endpoint: string,
  timeout: number;
    maxSessions: number;
  };
}
// 五诊配置接口
export interface DiagnosisConfig {
  looking: {;
  enabled: boolean;
    aiModelEndpoint: string;
  confidenceThreshold: number;
};
  listening: {,
  enabled: boolean;
    aiModelEndpoint: string,
  confidenceThreshold: number;
  };
  inquiry: {,
  enabled: boolean;
    aiModelEndpoint: string,
  confidenceThreshold: number;
  };
  palpation: {,
  enabled: boolean;
    aiModelEndpoint: string,
  confidenceThreshold: number;
  };
  calculation: {,
  enabled: boolean;
    aiModelEndpoint: string,
  confidenceThreshold: number;
  };
}
// 性能配置接口
export interface PerformanceConfig {
  enableMonitoring: boolean;
  sampleRate: number;
  renderThreshold: number;
  memoryThreshold: number;
  networkThreshold: number;
  enableReporting: boolean;
  reportingEndpoint: string;
}
// 安全配置接口
export interface SecurityConfig {
  enableEncryption: boolean;
  jwtSecret: string;
  tokenExpiry: number;
  enableBiometric: boolean;
  enablePinCode: boolean;
  sessionTimeout: number;
}
// 功能开关配置接口
export interface FeatureFlags {
  enableFiveDiagnosis: boolean;
  enableAgentCoordination: boolean;
  enableBlockchain: boolean;
  enableOfflineMode: boolean;
  enablePushNotifications: boolean;
  enableAnalytics: boolean;
  enableCrashReporting: boolean;
  enablePerformanceMonitoring: boolean;
}
// 主配置接口
export interface AppConfiguration {
  environment: Environment;
  version: string;
  buildNumber: string;
  api: ApiConfig;
  agents: AgentConfig;
  diagnosis: DiagnosisConfig;
  performance: PerformanceConfig;
  security: SecurityConfig;
  features: FeatureFlags;
  logging: {;
    level: 'debug' | 'info' | 'warn' | 'error';
  enableConsole: boolean;
    enableRemote: boolean;
  remoteEndpoint: string;
};
  cache: {,
  enableCache: boolean;
    maxSize: number,
  ttl: number;
  };
}
// 获取当前环境
const getCurrentEnvironment = (): Environment => {
  if (__DEV__) {
    return 'development';
  }
  // 可以通过环境变量或构建配置来确定
  const env = process.env.NODE_ENV as Environment;
  return env || 'production';
};
// 开发环境配置
const developmentConfig: AppConfiguration = {,
  environment: 'development',
  version: '1.0.0',
  buildNumber: '1',
  api: {,
  baseUrl: 'http://localhost:8000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    enableMocking: true,
  },
  agents: {,
  xiaoai: {
  enabled: true,
      endpoint: 'http://localhost:8001',
      timeout: 30000,
      maxSessions: 10,
},
    xiaoke: {,
  enabled: true,
      endpoint: 'http://localhost:8002',
      timeout: 30000,
      maxSessions: 10,
    },
    laoke: {,
  enabled: true,
      endpoint: 'http://localhost:8003',
      timeout: 30000,
      maxSessions: 10,
    },
    soer: {,
  enabled: true,
      endpoint: 'http://localhost:8004',
      timeout: 30000,
      maxSessions: 10,
    },
  },
  diagnosis: {,
  looking: {
  enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/looking',
      confidenceThreshold: 0.7,
},
    listening: {,
  enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/listening',
      confidenceThreshold: 0.7,
    },
    inquiry: {,
  enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/inquiry',
      confidenceThreshold: 0.7,
    },
    palpation: {,
  enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/palpation',
      confidenceThreshold: 0.7,
    },
    calculation: {,
  enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/calculation',
      confidenceThreshold: 0.8,
    },
  },
  performance: {,
  enableMonitoring: true,
    sampleRate: 1.0,
    renderThreshold: 16,
    memoryThreshold: 100,
    networkThreshold: 5000,
    enableReporting: true,
    reportingEndpoint: 'http://localhost:8000/performance',
  },
  security: {,
  enableEncryption: false,
    jwtSecret: 'dev-secret-key',
    tokenExpiry: 3600,
    enableBiometric: false,
    enablePinCode: false,
    sessionTimeout: 1800,
  },
  features: {,
  enableFiveDiagnosis: true,
    enableAgentCoordination: true,
    enableBlockchain: false,
    enableOfflineMode: true,
    enablePushNotifications: false,
    enableAnalytics: false,
    enableCrashReporting: true,
    enablePerformanceMonitoring: true,
  },
  logging: {,
  level: 'debug',
    enableConsole: true,
    enableRemote: false,
    remoteEndpoint: 'http://localhost:8000/logs',
  },
  cache: {,
  enableCache: true,
    maxSize: 50,
    ttl: 300,
  },
};
// 生产环境配置
const productionConfig: AppConfiguration = {,
  environment: 'production',
  version: '1.0.0',
  buildNumber: '1',
  api: {,
  baseUrl: 'https://api.suokelife.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    enableMocking: false,
  },
  agents: {,
  xiaoai: {
  enabled: true,
      endpoint: 'https://xiaoai.suokelife.com',
      timeout: 30000,
      maxSessions: 100,
},
    xiaoke: {,
  enabled: true,
      endpoint: 'https://xiaoke.suokelife.com',
      timeout: 30000,
      maxSessions: 100,
    },
    laoke: {,
  enabled: true,
      endpoint: 'https://laoke.suokelife.com',
      timeout: 30000,
      maxSessions: 100,
    },
    soer: {,
  enabled: true,
      endpoint: 'https://soer.suokelife.com',
      timeout: 30000,
      maxSessions: 100,
    },
  },
  diagnosis: {,
  looking: {
  enabled: true,
      aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/looking',
      confidenceThreshold: 0.8,
},
    listening: {,
  enabled: true,
      aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/listening',
      confidenceThreshold: 0.8,
    },
    inquiry: {,
  enabled: true,
      aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/inquiry',
      confidenceThreshold: 0.8,
    },
    palpation: {,
  enabled: true,
      aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/palpation',
      confidenceThreshold: 0.8,
    },
    calculation: {,
  enabled: true,
      aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/calculation',
      confidenceThreshold: 0.9,
    },
  },
  performance: {,
  enableMonitoring: true,
    sampleRate: 0.1,
    renderThreshold: 16,
    memoryThreshold: 200,
    networkThreshold: 10000,
    enableReporting: true,
    reportingEndpoint: 'https://api.suokelife.com/performance',
  },
  security: {,
  enableEncryption: true,
    jwtSecret: process.env.JWT_SECRET || 'production-secret-key',
    tokenExpiry: 3600,
    enableBiometric: true,
    enablePinCode: true,
    sessionTimeout: 1800,
  },
  features: {,
  enableFiveDiagnosis: true,
    enableAgentCoordination: true,
    enableBlockchain: true,
    enableOfflineMode: true,
    enablePushNotifications: true,
    enableAnalytics: true,
    enableCrashReporting: true,
    enablePerformanceMonitoring: true,
  },
  logging: {,
  level: 'warn',
    enableConsole: false,
    enableRemote: true,
    remoteEndpoint: 'https://api.suokelife.com/logs',
  },
  cache: {,
  enableCache: true,
    maxSize: 100,
    ttl: 600,
  },
};
// 测试环境配置
const stagingConfig: AppConfiguration = {
  ...productionConfig,
  environment: 'staging',
  api: {
  ...productionConfig.api,
    baseUrl: 'https://staging-api.suokelife.com',
},
  agents: {,
  xiaoai: {
  ...productionConfig.agents.xiaoai,
      endpoint: 'https://staging-xiaoai.suokelife.com',
},
    xiaoke: {
  ...productionConfig.agents.xiaoke,
      endpoint: 'https://staging-xiaoke.suokelife.com',
},
    laoke: {
  ...productionConfig.agents.laoke,
      endpoint: 'https://staging-laoke.suokelife.com',
},
    soer: {
  ...productionConfig.agents.soer,
      endpoint: 'https://staging-soer.suokelife.com',
},
  },
  logging: {
  ...productionConfig.logging,
    level: 'info',
    enableConsole: true,
},
  performance: {
  ...productionConfig.performance,
    sampleRate: 0.5,
},
};
// 配置映射
const configMap: Record<Environment, AppConfiguration> = {
  development: developmentConfig,
  staging: stagingConfig,
  production: productionConfig,
};
// 配置管理类
class ConfigManager {
  private static instance: ConfigManager;
  private currentConfig: AppConfiguration;
  private listeners: Array<(config: AppConfiguration) => void> = [];
  private constructor() {
    const environment = getCurrentEnvironment();
    this.currentConfig = { ...configMap[environment] };
    // 平台特定配置调整
    this.applyPlatformSpecificConfig();
  }
  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }
  private applyPlatformSpecificConfig(): void {
    if (Platform.OS === 'ios') {
      // iOS特定配置
      this.currentConfig.security.enableBiometric = true;
    } else if (Platform.OS === 'android') {
      // Android特定配置
      this.currentConfig.security.enableBiometric = true;
    }
  }
  public getConfig(): AppConfiguration {
    return { ...this.currentConfig };
  }
  public updateConfig(updates: Partial<AppConfiguration>): void {
    this.currentConfig = {
      ...this.currentConfig,
      ...updates,
    };
    // 通知监听器
    this.listeners.forEach(listener => listener(this.currentConfig));
  }
  public getApiConfig(): ApiConfig {
    return this.currentConfig.api;
  }
  public getAgentConfig(): AgentConfig {
    return this.currentConfig.agents;
  }
  public getDiagnosisConfig(): DiagnosisConfig {
    return this.currentConfig.diagnosis;
  }
  public getPerformanceConfig(): PerformanceConfig {
    return this.currentConfig.performance;
  }
  public getSecurityConfig(): SecurityConfig {
    return this.currentConfig.security;
  }
  public getFeatureFlags(): FeatureFlags {
    return this.currentConfig.features;
  }
  public isFeatureEnabled(feature: keyof FeatureFlags): boolean {
    return this.currentConfig.features[feature];
  }
  public getEnvironment(): Environment {
    return this.currentConfig.environment;
  }
  public isDevelopment(): boolean {
    return this.currentConfig.environment === 'development';
  }
  public isProduction(): boolean {
    return this.currentConfig.environment === 'production';
  }
  public addConfigListener(listener: (config: AppConfiguration) => void): () => void {
    this.listeners.push(listener);
    // 返回取消监听的函数
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }
  public async loadRemoteConfig(): Promise<void> {
    try {
      if (!this.currentConfig.api.baseUrl) {
        return;
      }
      const controller = new AbortController();
      const timeoutId = setTimeout() => controller.abort(), 5000);
      const response = await fetch(`${this.currentConfig.api.baseUrl}/config`, {
      method: "GET",
      headers: {
  'Content-Type': 'application/json',
},
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (response.ok) {
        const remoteConfig = await response.json();
        this.updateConfig(remoteConfig);
      }
    } catch (error) {
      console.warn('Failed to load remote config:', error);
    }
  }
  public validateConfig(): boolean {
    try {
      // 验证必需的配置项
      if (!this.currentConfig.api.baseUrl) {
        throw new Error('API base URL is required');
      }
      if (!this.currentConfig.version) {
        throw new Error('App version is required');
      }
      // 验证智能体配置
      const agents = Object.values(this.currentConfig.agents);
      for (const agent of agents) {
        if (agent.enabled && !agent.endpoint) {
          throw new Error('Agent endpoint is required when enabled');
        }
      }
      return true;
    } catch (error) {
      console.error('Config validation failed:', error);
      return false;
    }
  }
  public exportConfig(): string {
    return JSON.stringify(this.currentConfig, null, 2);
  }
  public importConfig(configJson: string): boolean {
    try {
      const config = JSON.parse(configJson) as AppConfiguration;
      this.updateConfig(config);
      return this.validateConfig();
    } catch (error) {
      console.error('Failed to import config:', error);
      return false;
    }
  }
}
// 导出配置管理器实例
export const configManager = ConfigManager.getInstance();
// 便捷访问函数
export const getConfig = () => configManager.getConfig();
export const getApiConfig = () => configManager.getApiConfig();
export const getAgentConfig = () => configManager.getAgentConfig();
export const getDiagnosisConfig = () => configManager.getDiagnosisConfig();
export const getPerformanceConfig = () => configManager.getPerformanceConfig();
export const getSecurityConfig = () => configManager.getSecurityConfig();
export const getFeatureFlags = () => configManager.getFeatureFlags();
export const isFeatureEnabled = (feature: keyof FeatureFlags) => configManager.isFeatureEnabled(feature);
export const isDevelopment = () => configManager.isDevelopment();
export const isProduction = () => configManager.isProduction();
// React Hook for config;
export const useConfig = () => {
  const [config, setConfig] = React.useState(configManager.getConfig());
  React.useEffect(() => {
    const unsubscribe = configManager.addConfigListener(setConfig);
    return unsubscribe;
  }, []);
  return config;
};
// React Hook for feature flags;
export const useFeatureFlag = (feature: keyof FeatureFlags) => {
  const config = useConfig();
  return config.features[feature];
};
export default configManager;