/**
* 配置管理服务
* 动态管理API网关和应用的配置
*/
export interface AppConfig {
  // API网关配置
  gateway: {;
  baseUrl: string;
    timeout: number;
  retryAttempts: number;
    retryDelay: number;
};
    // 功能开关
  features: {
    [featureName: string]: {,
  enabled: boolean;
      rolloutPercentage: number;
    };
  };
    // 用户界面配置
  ui: {,
  theme: 'light' | 'dark' | 'auto';
    language: string,
  enableAnimations: boolean;
  };
}
class ConfigService {
  private config: AppConfig;
  private defaultConfig: AppConfig;
  constructor() {
    this.defaultConfig = this.getDefaultConfig();
    this.config = { ...this.defaultConfig };
  }
  /**
  * 初始化配置服务
  */
  async initialize(): Promise<void> {
    try {
      console.log('配置服务初始化完成');
    } catch (error) {
      console.error('配置服务初始化失败:', error);
      this.config = { ...this.defaultConfig };
    }
  }
  /**
  * 获取配置值
  */
  get<T = any>(path: string, defaultValue?: T): T {
    const keys = path.split('.');
    let value: any = this.config;
        for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return defaultValue as T;
      }
    }
        return value as T;
  }
  /**
  * 设置配置值
  */
  async set(path: string, value: any): Promise<void> {
    try {
      this.setNestedValue(this.config, path, value);
      console.log(`配置已更新: ${path} = ${JSON.stringify(value)}`);
    } catch (error) {
      console.error('配置设置失败:', error);
      throw error;
    }
  }
  /**
  * 检查功能开关
  */
  isFeatureEnabled(featureName: string): boolean {
    const feature = this.get(`features.${featureName}`);
    return feature && feature.enabled;
  }
  private getDefaultConfig(): AppConfig {
    return {
      gateway: {,
  baseUrl: 'https://api.suoke-life.com',
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000;
      },
      features: {
        'ai-diagnosis': {
          enabled: true,
          rolloutPercentage: 100;
        },
        'blockchain-health': {
          enabled: true,
          rolloutPercentage: 50;
        },
        'corn-maze': {
          enabled: true,
          rolloutPercentage: 100;
        }
      },
      ui: {,
  theme: 'auto',
        language: 'zh-CN',
        enableAnimations: true;
      }
    };
  }
  private setNestedValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;
        for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }
        current[keys[keys.length - 1]] = value;
  }
}
// 创建全局实例
export const configService = new ConfigService();
// 导出类型和实例
export default ConfigService;