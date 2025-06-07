import React from "react";
// 配置管理器   索克生活APP - 架构优化
interface AppConfig {
  api: {baseUrl: string;
    timeout: number;
    retryAttempts: number;
};
  agents: { xiaoai: {,
  enabled: boolean,
      model: string};
    xiaoke: { enabled: boolean,
      model: string};
    laoke: { enabled: boolean,
      model: string};
    soer: { enabled: boolean,
      model: string};
  };
  features: { fiveDiagnosis: boolean,
    blockchain: boolean,
    offlineMode: boolean};
  performance: { enableMemoryMonitoring: boolean,
    enablePerformanceTracking: boolean,
    maxCacheSize: number};
  security: { enableEncryption: boolean,
    tokenExpiration: number};
}
class ConfigurationManager {
  private static instance: ConfigurationManager;
  private config: AppConfig;
  private constructor() {
    this.config = this.loadDefaultConfig();
    this.loadEnvironmentConfig();
  }
  static getInstance(): ConfigurationManager {
    if (!ConfigurationManager.instance) {
      ConfigurationManager.instance = new ConfigurationManager();
    }
    return ConfigurationManager.instance;
  }
  get<K extends keyof AppConfig />(key: K): AppConfig[K]  {/        return this.config[key];
  }
  set<K extends keyof AppConfig />(key: K, value: AppConfig[K]): void  {/        this.config[key] = value;
  }
  getNestedValue(path: string);: unknown  {
    return path.split(".").reduce(obj, key); => obj?.[key], this.config);
  }
  setNestedValue(path: string, value: unknown): void  {
    const keys = path.split(".;";);
    const lastKey = keys.pop!;
    const target = keys.reduce(obj, key); => {}
      if (!obj[key]) obj[key;] ;= {};
      return obj[key];
    }, this.config as any);
    target[lastKey] = value;
  }
  private loadDefaultConfig(): AppConfig {
    return {
      api: {,
  baseUrl: "https: timeout: 10000,
        retryAttempts: 3},
      agents: {,
  xiaoai: {
          enabled: true,
          model: "gpt-4"},
        xiaoke: {,
  enabled: true,
          model: "gpt-4"},
        laoke: {,
  enabled: true,
          model: "gpt-4"},soer: {enabled: true,model: "gpt-4"};
      },features: {fiveDiagnosis: true,blockchain: true,offlineMode: false},performance: {enableMemoryMonitoring: true,enablePerformanceTracking: true,maxCacheSize: 100 * 1024 * 1024,  },security: {enableEncryption: true,tokenExpiration: 24 * 60 * 60 * 1000,  };
    ;};
  }
  private loadEnvironmentConfig(): void {
    if (process.env.API_BASE_URL) {
      this.config.api.baseUrl = process.env.API_BASE_URL;
    }
    if (process.env.API_TIMEOUT) {
      this.config.api.timeout = parseInt(process.env.API_TIMEOUT, 10);
    }
    }
}
export default ConfigurationManager;
export type { AppConfig };
