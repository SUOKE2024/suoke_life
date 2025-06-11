/* 项目配置文件 */

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
  xiaoai: {
    enabled: boolean;
    endpoint: string;
    timeout: number;
    maxSessions: number;
  };
  xiaoke: {
    enabled: boolean;
    endpoint: string;
    timeout: number;
    maxSessions: number;
  };
  laoke: {
    enabled: boolean;
    endpoint: string;
    timeout: number;
    maxSessions: number;
  };
  soer: {
    enabled: boolean;
    endpoint: string;
    timeout: number;
    maxSessions: number;
  };
}

// 五诊配置接口
export interface DiagnosisConfig {
  looking: {
    enabled: boolean;
    aiModelEndpoint: string;
    confidenceThreshold: number;
  };
  listening: {
    enabled: boolean;
    aiModelEndpoint: string;
    confidenceThreshold: number;
  };
  inquiry: {
    enabled: boolean;
    aiModelEndpoint: string;
    confidenceThreshold: number;
  };
  palpation: {
    enabled: boolean;
    aiModelEndpoint: string;
    confidenceThreshold: number;
  };
  calculation: {
    enabled: boolean;
    aiModelEndpoint: string;
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
  logging: {
    level: 'debug' | 'info' | 'warn' | 'error';
    enableConsole: boolean;
    enableRemote: boolean;
    remoteEndpoint: string;
  };
  cache: {
    enableCache: boolean;
    maxSize: number;
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
const developmentConfig: AppConfiguration = {
  environment: 'development',
  version: '1.0.0',
  buildNumber: '1',
  api: {
    baseUrl: 'http://localhost:8000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    enableMocking: true
  },
  agents: {
    xiaoai: {
      enabled: true,
      endpoint: 'http://localhost:8001',
      timeout: 30000,
      maxSessions: 10
    },
    xiaoke: {
      enabled: true,
      endpoint: 'http://localhost:8002',
      timeout: 30000,
      maxSessions: 10
    },
    laoke: {
      enabled: true,
      endpoint: 'http://localhost:8003',
      timeout: 30000,
      maxSessions: 10
    },
    soer: {
      enabled: true,
      endpoint: 'http://localhost:8004',
      timeout: 30000,
      maxSessions: 10
    }
  },
  diagnosis: {
    looking: {
      enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/looking',
      confidenceThreshold: 0.7
    },
    listening: {
      enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/listening',
      confidenceThreshold: 0.7
    },
    inquiry: {
      enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/inquiry',
      confidenceThreshold: 0.7
    },
    palpation: {
      enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/palpation',
      confidenceThreshold: 0.7
    },
    calculation: {
      enabled: true,
      aiModelEndpoint: 'http://localhost:8001/diagnosis/calculation',
      confidenceThreshold: 0.8
    }
  },
  performance: {
    enableMonitoring: true,
    sampleRate: 1.0,
    renderThreshold: 16,
    memoryThreshold: 100,
    networkThreshold: 5000,
    enableReporting: true,
    reportingEndpoint: 'http://localhost:8000/performance'
  },
  security: {
    enableEncryption: false,
    jwtSecret: 'dev-secret-key',
    tokenExpiry: 3600000,
    enableBiometric: false,
    enablePinCode: false,
    sessionTimeout: 1800000
  },
  features: {
    enableFiveDiagnosis: true,
    enableAgentCoordination: true,
    enableBlockchain: false,
    enableOfflineMode: true,
    enablePushNotifications: true,
    enableAnalytics: true,
    enableCrashReporting: true,
    enablePerformanceMonitoring: true
  },
  logging: {
    level: 'debug',
    enableConsole: true,
    enableRemote: false,
    remoteEndpoint: 'http://localhost:8000/logs'
  },
  cache: {
    enableCache: true,
    maxSize: 50,
    ttl: 300000
  }
};

// 生产环境配置
const productionConfig: AppConfiguration = {
  environment: 'production',
  version: '1.0.0',
  buildNumber: '1',
  api: {
    baseUrl: 'https://api.suokelife.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    enableMocking: false
  },
  agents: {
    xiaoai: {
      enabled: true,
      endpoint: 'https://xiaoai.suokelife.com',
      timeout: 30000,
      maxSessions: 100
    },
    xiaoke: {
      enabled: true,
      endpoint: 'https://xiaoke.suokelife.com',
      timeout: 30000,
      maxSessions: 100
    },
    laoke: {
      enabled: true,
      endpoint: 'https://laoke.suokelife.com',
      timeout: 30000,
      maxSessions: 100
    },
    soer: {
      enabled: true,
      endpoint: 'https://soer.suokelife.com',
      timeout: 30000,
      maxSessions: 100
    }
  },
  diagnosis: {
    looking: {
      enabled: true,
      aiModelEndpoint: 'https://ai.suokelife.com/diagnosis/looking',
      confidenceThreshold: 0.8
    },
    listening: {
      enabled: true,
      aiModelEndpoint: 'https://ai.suokelife.com/diagnosis/listening',
      confidenceThreshold: 0.8
    },
    inquiry: {
      enabled: true,
      aiModelEndpoint: 'https://ai.suokelife.com/diagnosis/inquiry',
      confidenceThreshold: 0.8
    },
    palpation: {
      enabled: true,
      aiModelEndpoint: 'https://ai.suokelife.com/diagnosis/palpation',
      confidenceThreshold: 0.8
    },
    calculation: {
      enabled: true,
      aiModelEndpoint: 'https://ai.suokelife.com/diagnosis/calculation',
      confidenceThreshold: 0.9
    }
  },
  performance: {
    enableMonitoring: true,
    sampleRate: 0.1,
    renderThreshold: 16,
    memoryThreshold: 200,
    networkThreshold: 10000,
    enableReporting: true,
    reportingEndpoint: 'https://analytics.suokelife.com/performance'
  },
  security: {
    enableEncryption: true,
    jwtSecret: process.env.JWT_SECRET || 'production-secret-key',
    tokenExpiry: 3600000,
    enableBiometric: true,
    enablePinCode: true,
    sessionTimeout: 1800000
  },
  features: {
    enableFiveDiagnosis: true,
    enableAgentCoordination: true,
    enableBlockchain: true,
    enableOfflineMode: true,
    enablePushNotifications: true,
    enableAnalytics: true,
    enableCrashReporting: true,
    enablePerformanceMonitoring: true
  },
  logging: {
    level: 'error',
    enableConsole: false,
    enableRemote: true,
    remoteEndpoint: 'https://logs.suokelife.com'
  },
  cache: {
    enableCache: true,
    maxSize: 100,
    ttl: 600000
  }
};

// 配置管理器
class ConfigManager {
  private config: AppConfiguration;

  constructor() {
    const environment = getCurrentEnvironment();
    this.config = environment === 'development' ? developmentConfig : productionConfig;
  }

  getConfig(): AppConfiguration {
    return this.config;
  }

  getApiConfig(): ApiConfig {
    return this.config.api;
  }

  getAgentConfig(): AgentConfig {
    return this.config.agents;
  }

  getDiagnosisConfig(): DiagnosisConfig {
    return this.config.diagnosis;
  }

  getPerformanceConfig(): PerformanceConfig {
    return this.config.performance;
  }

  getSecurityConfig(): SecurityConfig {
    return this.config.security;
  }

  getFeatureFlags(): FeatureFlags {
    return this.config.features;
  }

  isFeatureEnabled(feature: keyof FeatureFlags): boolean {
    return this.config.features[feature];
  }

  updateConfig(updates: Partial<AppConfiguration>): void {
    this.config = { ...this.config, ...updates };
  }
}

// 导出配置管理器实例
export const configManager = new ConfigManager();
export default configManager;