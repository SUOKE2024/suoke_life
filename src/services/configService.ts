/* 置 *//;/g/;
*//;,/g/;
export interface AppConfig {// API网关配置/;,}gateway: {baseUrl: string,;,/g,/;
  timeout: number,;
retryAttempts: number,;
}
}
  const retryDelay = number;}
};
    // 功能开关/;,/g/;
const features = {[featureName: string]: {enabled: boolean,;
}
  const rolloutPercentage = number;}
    };
  };
    // 用户界面配置/;,/g,/;
  ui: {theme: 'light' | 'dark' | 'auto';','';
language: string,;
}
  const enableAnimations = boolean;}
  };
}
class ConfigService {private config: AppConfig;,}private defaultConfig: AppConfig;
constructor() {}}
}
    this.defaultConfig = this.getDefaultConfig();}
    this.config = { ...this.defaultConfig };
  }
  /* 务 *//;/g/;
  *//;,/g/;
const async = initialize(): Promise<void> {try {}}
}
    } catch (error) {}}
}
      this.config = { ...this.defaultConfig };
    }
  }
  /* 值 *//;/g/;
  */'/;,'/g'/;
get<T = any>(path: string, defaultValue?: T): T {';,}const keys = path.split('.');';,'';
let value: any = this.config;';,'';
for (const key of keys) {';,}if (value && typeof value === 'object' && key in value) {';}}'';
        value = value[key];}
      } else {}}
        return defaultValue as T;}
      }
    }
        return value as T;
  }
  /* 值 *//;/g/;
  *//;,/g,/;
  async: set(path: string, value: any): Promise<void> {try {}      this.setNestedValue(this.config, path, value);
}
}
    } catch (error) {}}
      const throw = error;}
    }
  }
  /* 关 *//;/g/;
  *//;,/g/;
isFeatureEnabled(featureName: string): boolean {}
    const feature = this.get(`features.${featureName;}`);````;,```;
return feature && feature.enabled;
  }
  private getDefaultConfig(): AppConfig {return {';,}gateway: {,';,}baseUrl: 'https://api.suoke-life.com';',''/;,'/g,'/;
  timeout: 30000,;
retryAttempts: 3,;
}
        const retryDelay = 1000;}
      },';,'';
const features = {';}        'ai-diagnosis': {';,}enabled: true,;'';
}
          const rolloutPercentage = 100;}';'';
        },';'';
        'blockchain-health': {';,}enabled: true,;'';
}
          const rolloutPercentage = 50;}';'';
        },';'';
        'corn-maze': {';,}enabled: true,;'';
}
          const rolloutPercentage = 100;}
        }
      },';,'';
ui: {,';,}theme: 'auto';','';
language: 'zh-CN';','';'';
}
        const enableAnimations = true;}
      }
    };
  }';,'';
private setNestedValue(obj: any, path: string, value: any): void {';,}const keys = path.split('.');';,'';
let current = obj;
for (let i = 0; i < keys.length - 1; i++) {';,}const key = keys[i];';'';
}
      if (!(key in current) || typeof current[key] !== 'object') {'}'';
current[key] = {};
      }
      current = current[key];
    }
        current[keys[keys.length - 1]] = value;
  }
}
// 创建全局实例/;,/g/;
export const configService = new ConfigService();
// 导出类型和实例'/;,'/g'/;
export default ConfigService;