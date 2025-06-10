/* 项 *//;/g/;
 *//;/g/;
';,'';
import { Platform } from "react-native";"";"";
// 环境类型'/;,'/g'/;
export type Environment = 'development' | 'staging' | 'production';';'';
// API配置接口/;,/g/;
export interface ApiConfig {baseUrl: string}timeout: number,;
retryAttempts: number,;
retryDelay: number,;
}
}
  const enableMocking = boolean;}
}
// 智能体配置接口/;,/g/;
export interface AgentConfig {xiaoai: {enabled: boolean,;
endpoint: string,;
timeout: number,;
}
}
    const maxSessions = number;}
  };
xiaoke: {enabled: boolean,;
endpoint: string,;
timeout: number,;
}
    const maxSessions = number;}
  };
laoke: {enabled: boolean,;
endpoint: string,;
timeout: number,;
}
    const maxSessions = number;}
  };
soer: {enabled: boolean,;
endpoint: string,;
timeout: number,;
}
    const maxSessions = number;}
  };
}
// 五诊配置接口/;,/g/;
export interface DiagnosisConfig {looking: {enabled: boolean,;
aiModelEndpoint: string,;
}
}
    const confidenceThreshold = number;}
  };
listening: {enabled: boolean,;
aiModelEndpoint: string,;
}
    const confidenceThreshold = number;}
  };
inquiry: {enabled: boolean,;
aiModelEndpoint: string,;
}
    const confidenceThreshold = number;}
  };
palpation: {enabled: boolean,;
aiModelEndpoint: string,;
}
    const confidenceThreshold = number;}
  };
calculation: {enabled: boolean,;
aiModelEndpoint: string,;
}
    const confidenceThreshold = number;}
  };
}
// 性能配置接口/;,/g/;
export interface PerformanceConfig {enableMonitoring: boolean}sampleRate: number,;
renderThreshold: number,;
memoryThreshold: number,;
networkThreshold: number,;
enableReporting: boolean,;
}
}
  const reportingEndpoint = string;}
}
// 安全配置接口/;,/g/;
export interface SecurityConfig {enableEncryption: boolean}jwtSecret: string,;
tokenExpiry: number,;
enableBiometric: boolean,;
enablePinCode: boolean,;
}
}
  const sessionTimeout = number;}
}
// 功能开关配置接口/;,/g/;
export interface FeatureFlags {enableFiveDiagnosis: boolean}enableAgentCoordination: boolean,;
enableBlockchain: boolean,;
enableOfflineMode: boolean,;
enablePushNotifications: boolean,;
enableAnalytics: boolean,;
enableCrashReporting: boolean,;
}
}
  const enablePerformanceMonitoring = boolean;}
}
// 主配置接口/;,/g/;
export interface AppConfiguration {environment: Environment}version: string,;
buildNumber: string,;
api: ApiConfig,;
agents: AgentConfig,;
diagnosis: DiagnosisConfig,;
performance: PerformanceConfig,;
security: SecurityConfig,;
features: FeatureFlags,';,'';
logging: {,';,}level: 'debug' | 'info' | 'warn' | 'error';','';
enableConsole: boolean,;
enableRemote: boolean,;
}
}
    const remoteEndpoint = string;}
  };
cache: {enableCache: boolean,;
maxSize: number,;
}
    const ttl = number;}
  };
}
// 获取当前环境/;,/g/;
const  getCurrentEnvironment = (): Environment => {';,}if (__DEV__) {';}}'';
    return 'development';'}'';'';
  }
  // 可以通过环境变量或构建配置来确定'/;,'/g'/;
const env = process.env.NODE_ENV as Environment;';,'';
return env || 'production';';'';
};
// 开发环境配置'/;,'/g,'/;
  const: developmentConfig: AppConfiguration = {,';,}environment: 'development';','';
version: '1.0.0';','';
buildNumber: '1';','';
api: {,';,}baseUrl: 'http://localhost:8000';',''/;,'/g,'/;
  timeout: 30000,;
retryAttempts: 3,;
retryDelay: 1000,;
}
    const enableMocking = true;}
  }
agents: {xiaoai: {,';,}enabled: true,';,'';
endpoint: 'http://localhost:8001';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 10;}
    }
xiaoke: {,';,}enabled: true,';,'';
endpoint: 'http://localhost:8002';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 10;}
    }
laoke: {,';,}enabled: true,';,'';
endpoint: 'http://localhost:8003';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 10;}
    }
soer: {,';,}enabled: true,';,'';
endpoint: 'http://localhost:8004';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 10;}
    }
  }
diagnosis: {looking: {,';,}enabled: true,';,'';
aiModelEndpoint: 'http://localhost:8001/diagnosis/looking';',''/;'/g'/;
}
      const confidenceThreshold = 0.7;}
    }
listening: {,';,}enabled: true,';,'';
aiModelEndpoint: 'http://localhost:8001/diagnosis/listening';',''/;'/g'/;
}
      const confidenceThreshold = 0.7;}
    }
inquiry: {,';,}enabled: true,';,'';
aiModelEndpoint: 'http://localhost:8001/diagnosis/inquiry';',''/;'/g'/;
}
      const confidenceThreshold = 0.7;}
    }
palpation: {,';,}enabled: true,';,'';
aiModelEndpoint: 'http://localhost:8001/diagnosis/palpation';',''/;'/g'/;
}
      const confidenceThreshold = 0.7;}
    }
calculation: {,';,}enabled: true,';,'';
aiModelEndpoint: 'http://localhost:8001/diagnosis/calculation';',''/;'/g'/;
}
      const confidenceThreshold = 0.8;}
    }
  }
performance: {enableMonitoring: true,;
sampleRate: 1.0,;
renderThreshold: 16,;
memoryThreshold: 100,;
networkThreshold: 5000,';,'';
enableReporting: true,';'';
}
    const reportingEndpoint = 'http: //localhost:8000/performance';'}''/;'/g'/;
  }
security: {,';,}enableEncryption: false,';,'';
jwtSecret: 'dev-secret-key';','';
tokenExpiry: 3600,;
enableBiometric: false,;
enablePinCode: false,;
}
    const sessionTimeout = 1800;}
  }
features: {enableFiveDiagnosis: true,;
enableAgentCoordination: true,;
enableBlockchain: false,;
enableOfflineMode: true,;
enablePushNotifications: false,;
enableAnalytics: false,;
enableCrashReporting: true,;
}
    const enablePerformanceMonitoring = true;}
  },';,'';
logging: {,';,}level: 'debug';','';
enableConsole: true,';,'';
enableRemote: false,';'';
}
    const remoteEndpoint = 'http: //localhost:8000/logs';'}''/;'/g'/;
  }
cache: {enableCache: true,;
maxSize: 50,;
}
    const ttl = 300;}
  }
};
// 生产环境配置'/;,'/g,'/;
  const: productionConfig: AppConfiguration = {,';,}environment: 'production';','';
version: '1.0.0';','';
buildNumber: '1';','';
api: {,';,}baseUrl: 'https://api.suokelife.com';',''/;,'/g,'/;
  timeout: 30000,;
retryAttempts: 3,;
retryDelay: 1000,;
}
    const enableMocking = false;}
  }
agents: {xiaoai: {,';,}enabled: true,';,'';
endpoint: 'https://xiaoai.suokelife.com';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 100;}
    }
xiaoke: {,';,}enabled: true,';,'';
endpoint: 'https://xiaoke.suokelife.com';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 100;}
    }
laoke: {,';,}enabled: true,';,'';
endpoint: 'https://laoke.suokelife.com';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 100;}
    }
soer: {,';,}enabled: true,';,'';
endpoint: 'https://soer.suokelife.com';',''/;,'/g,'/;
  timeout: 30000,;
}
      const maxSessions = 100;}
    }
  }
diagnosis: {looking: {,';,}enabled: true,';,'';
aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/looking';',''/;'/g'/;
}
      const confidenceThreshold = 0.8;}
    }
listening: {,';,}enabled: true,';,'';
aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/listening';',''/;'/g'/;
}
      const confidenceThreshold = 0.8;}
    }
inquiry: {,';,}enabled: true,';,'';
aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/inquiry';',''/;'/g'/;
}
      const confidenceThreshold = 0.8;}
    }
palpation: {,';,}enabled: true,';,'';
aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/palpation';',''/;'/g'/;
}
      const confidenceThreshold = 0.8;}
    }
calculation: {,';,}enabled: true,';,'';
aiModelEndpoint: 'https://xiaoai.suokelife.com/diagnosis/calculation';',''/;'/g'/;
}
      const confidenceThreshold = 0.9;}
    }
  }
performance: {enableMonitoring: true,;
sampleRate: 0.1,;
renderThreshold: 16,;
memoryThreshold: 200,;
networkThreshold: 10000,';,'';
enableReporting: true,';'';
}
    const reportingEndpoint = 'https: //api.suokelife.com/performance';'}''/;'/g'/;
  }
security: {,';,}enableEncryption: true,';,'';
jwtSecret: process.env.JWT_SECRET || 'production-secret-key';','';
tokenExpiry: 3600,;
enableBiometric: true,;
enablePinCode: true,;
}
    const sessionTimeout = 1800;}
  }
features: {enableFiveDiagnosis: true,;
enableAgentCoordination: true,;
enableBlockchain: true,;
enableOfflineMode: true,;
enablePushNotifications: true,;
enableAnalytics: true,;
enableCrashReporting: true,;
}
    const enablePerformanceMonitoring = true;}
  },';,'';
logging: {,';,}level: 'warn';','';
enableConsole: false,';,'';
enableRemote: true,';'';
}
    const remoteEndpoint = 'https: //api.suokelife.com/logs';'}''/;'/g'/;
  }
cache: {enableCache: true,;
maxSize: 100,;
}
    const ttl = 600;}
  }
};
// 测试环境配置/;,/g/;
const  stagingConfig: AppConfiguration = {';}  ...productionConfig,';,'';
environment: 'staging';','';
const api = {';}    ...productionConfig.api,';'';
}
    const baseUrl = 'https: //staging-api.suokelife.com';'}''/;'/g'/;
  }
agents: {const xiaoai = {';}      ...productionConfig.agents.xiaoai,';'';
}
      const endpoint = 'https: //staging-xiaoai.suokelife.com';'}''/;'/g'/;
    }
const xiaoke = {';}      ...productionConfig.agents.xiaoke,';'';
}
      const endpoint = 'https: //staging-xiaoke.suokelife.com';'}''/;'/g'/;
    }
const laoke = {';}      ...productionConfig.agents.laoke,';'';
}
      const endpoint = 'https: //staging-laoke.suokelife.com';'}''/;'/g'/;
    }
const soer = {';}      ...productionConfig.agents.soer,';'';
}
      const endpoint = 'https: //staging-soer.suokelife.com';'}''/;'/g'/;
    }
  }
const logging = {';}    ...productionConfig.logging,';,'';
level: 'info';','';'';
}
    const enableConsole = true;}
  }
const performance = {...productionConfig.performance,;}}
    const sampleRate = 0.5;}
  }
};
// 配置映射/;,/g,/;
  const: configMap: Record<Environment, AppConfiguration> = {development: developmentConfig}staging: stagingConfig,;
}
  const production = productionConfig;}
};
// 配置管理类/;,/g/;
class ConfigManager {private static instance: ConfigManager;,}private currentConfig: AppConfiguration;
private listeners: Array<(config: AppConfiguration) => void> = [];
private constructor() {}}
}
    const environment = getCurrentEnvironment();}
    this.currentConfig = { ...configMap[environment] };
    // 平台特定配置调整/;,/g/;
this.applyPlatformSpecificConfig();
  }
  const public = static getInstance(): ConfigManager {if (!ConfigManager.instance) {}}
      ConfigManager.instance = new ConfigManager();}
    }
    return ConfigManager.instance;
  }';,'';
private applyPlatformSpecificConfig(): void {';,}if (Platform.OS === 'ios') {';}      // iOS特定配置'/;'/g'/;
}
      this.currentConfig.security.enableBiometric = true;'}'';'';
    } else if (Platform.OS === 'android') {';}      // Android特定配置/;'/g'/;
}
      this.currentConfig.security.enableBiometric = true;}
    }
  }
  const public = getConfig(): AppConfiguration {}
    return { ...this.currentConfig };
  }
  const public = updateConfig(updates: Partial<AppConfiguration>): void {this.currentConfig = {}      ...this.currentConfig,;
}
      ...updates,}
    ;};
    // 通知监听器/;,/g/;
this.listeners.forEach((listener) => listener(this.currentConfig));
  }
  const public = getApiConfig(): ApiConfig {}}
    return this.currentConfig.api;}
  }
  const public = getAgentConfig(): AgentConfig {}}
    return this.currentConfig.agents;}
  }
  const public = getDiagnosisConfig(): DiagnosisConfig {}}
    return this.currentConfig.diagnosis;}
  }
  const public = getPerformanceConfig(): PerformanceConfig {}}
    return this.currentConfig.performance;}
  }
  const public = getSecurityConfig(): SecurityConfig {}}
    return this.currentConfig.security;}
  }
  const public = getFeatureFlags(): FeatureFlags {}}
    return this.currentConfig.features;}
  }
  const public = isFeatureEnabled(feature: keyof FeatureFlags): boolean {}}
    return this.currentConfig.features[feature];}
  }
  const public = getEnvironment(): Environment {}}
    return this.currentConfig.environment;}
  }';,'';
const public = isDevelopment(): boolean {';}}'';
    return this.currentConfig.environment === 'development';'}'';'';
  }';,'';
const public = isProduction(): boolean {';}}'';
    return this.currentConfig.environment === 'production';'}'';'';
  }
  const public = addConfigListener();
listener: (config: AppConfiguration) => void;
  ): () => void {this.listeners.push(listener);}    // 返回取消监听的函数/;,/g/;
return () => {const index = this.listeners.indexOf(listener);,}if (index > -1) {}}
        this.listeners.splice(index, 1);}
      }
    };
  }
  const public = async loadRemoteConfig(): Promise<void> {try {}      if (!this.currentConfig.api.baseUrl) {}}
        return;}
      }
      const controller = new AbortController();
timeoutId: setTimeout(() => controller.abort(), 5000);';,'';
const: response = await fetch(`${this.currentConfig.api.baseUrl}/config`, {/`;)``'`;,}method: 'GET';','';,'/g'/`;
const headers = {';}}'';
          'Content-Type': 'application/json',')}''/;'/g'/;
        ;},);
const signal = controller.signal;);
      });
clearTimeout(timeoutId);
if (response.ok) {const remoteConfig = await response.json();}}
        this.updateConfig(remoteConfig);}
      }';'';
    } catch (error) {';}}'';
      console.warn('Failed to load remote config:', error);'}'';'';
    }
  }
  const public = validateConfig(): boolean {try {}      // 验证必需的配置项'/;,'/g'/;
if (!this.currentConfig.api.baseUrl) {';}}'';
        const throw = new Error('API base URL is required');'}'';'';
      }';,'';
if (!this.currentConfig.version) {';}}'';
        const throw = new Error('App version is required');'}'';'';
      }
      // 验证智能体配置/;,/g/;
const agents = Object.values(this.currentConfig.agents);
for (const agent of agents) {';,}if (agent.enabled && !agent.endpoint) {';}};,'';
const throw = new Error('Agent endpoint is required when enabled');'}'';'';
        }
      }
      return true;';'';
    } catch (error) {';,}console.error('Config validation failed:', error);';'';
}
      return false;}
    }
  }
  const public = exportConfig(): string {}}
    return JSON.stringify(this.currentConfig, null, 2);}
  }
  const public = importConfig(configJson: string): boolean {try {}      const config = JSON.parse(configJson) as AppConfiguration;
this.updateConfig(config);
}
      return this.validateConfig();}';'';
    } catch (error) {';,}console.error('Failed to import config:', error);';'';
}
      return false;}
    }
  }
}
// 导出配置管理器实例/;,/g/;
export const configManager = ConfigManager.getInstance();
// 便捷访问函数/;,/g/;
export const getConfig = () => configManager.getConfig();
export const getApiConfig = () => configManager.getApiConfig();
export const getAgentConfig = () => configManager.getAgentConfig();
export const getDiagnosisConfig = () => configManager.getDiagnosisConfig();
export const getPerformanceConfig = () => configManager.getPerformanceConfig();
export const getSecurityConfig = () => configManager.getSecurityConfig();
export const getFeatureFlags = () => configManager.getFeatureFlags();
export const isFeatureEnabled = (feature: keyof FeatureFlags) =>;
configManager.isFeatureEnabled(feature);
export const isDevelopment = () => configManager.isDevelopment();
export const isProduction = () => configManager.isProduction();
// React Hook for config;/;,/g/;
export const useConfig = useCallback(() => {;,}const [config, setConfig] = React.useState(configManager.getConfig());
React.useEffect(() => {const unsubscribe = configManager.addConfigListener(setConfig);}}
    return unsubscribe;}
  }, []);
return config;
};
// React Hook for feature flags;/;,/g/;
export const useFeatureFlag = useCallback((feature: keyof FeatureFlags) => {;,}const config = useConfig();
}
  return config.features[feature];}
};
export default configManager;';'';
''';