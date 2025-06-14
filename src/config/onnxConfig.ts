import { Platform } from "react-native";
/* 理 */
 */"
// 基础类型定义'/,'/g'/;
export type Environment = 'development' | 'staging' | 'production;
export type DeviceType = 'phone' | 'tablet' | 'desktop;
export type PerformanceMode = 'power_save' | 'balanced' | 'performance;
export type ExecutionProvider = 'cpu' | 'coreml' | 'nnapi';
// 配置接口
export interface InferenceConfig {executionProviders: ExecutionProvider[]}enableOptimization: boolean,;
enableProfiling: boolean,
sessionOptions: {intraOpNumThreads: number,
interOpNumThreads: number,
graphOptimizationLevel: string,
enableMemPattern: boolean,
}
}
    const enableCpuMemArena = boolean}
  };
}
export interface QuantizationConfig {level: string}outputPath: string,;
preserveAccuracy: boolean,
targetDevice: string,
}
}
  const optimizationLevel = string}
}
export interface ModelOptimizationOptions {level: string}enableGraphOptimization: boolean,;
enableMemoryOptimization: boolean,
enableCpuOptimization: boolean,
targetDevice: string,
}
}
  const preserveAccuracy = boolean}
}
export interface EdgeComputeConfig {maxConcurrentTasks: number}taskTimeout: number,;
memoryLimit: number,
cpuThreshold: number,
thermalThreshold: string,
enableLoadBalancing: boolean,
}
}
  const enableResourceMonitoring = boolean}
}
export interface ONNXRuntimeConfig {environment: Environment}deviceType: DeviceType,;
performanceMode: PerformanceMode,
inference: InferenceConfig,
quantization: QuantizationConfig,
optimization: ModelOptimizationOptions,
edgeCompute: EdgeComputeConfig,
cache: {enabled: boolean,
maxSize: number,
}
}
    const ttl = number}
  };
logging: {,'enabled: boolean,'
level: 'debug' | 'info' | 'warn' | 'error,'
}
    const maxLogFiles = number}
  };
models: {baseUrl: string,
downloadTimeout: number,
retryAttempts: number,
}
    const preloadModels = string[]}
  };
}
// 默认配置'/,'/g,'/;
  const: DEFAULT_CONFIG: ONNXRuntimeConfig = {,'environment: 'development,'
deviceType: 'phone,'
performanceMode: 'balanced,'
inference: {,'executionProviders: ['cpu'];','';
enableOptimization: true,
enableProfiling: false,
sessionOptions: {intraOpNumThreads: 2,
interOpNumThreads: 1,'
graphOptimizationLevel: 'extended,'';
enableMemPattern: true,
}
      const enableCpuMemArena = true}
    }
  },'
quantization: {,'level: 'int8,'';
outputPath: ,
preserveAccuracy: true,'
targetDevice: 'cpu,'
}
    const optimizationLevel = 'extended}
  },'
optimization: {,'level: 'extended,'';
enableGraphOptimization: true,
enableMemoryOptimization: true,
enableCpuOptimization: true,'
targetDevice: 'cpu,'
}
    const preserveAccuracy = true}
  }
edgeCompute: {maxConcurrentTasks: 3,
taskTimeout: 30000,
memoryLimit: 512,
cpuThreshold: 80,'
thermalThreshold: 'nominal,'';
enableLoadBalancing: true,
}
    const enableResourceMonitoring = true}
  }
cache: {enabled: true,
maxSize: 100,
}
    ttl: 3600000, // 1小时}
  }
logging: {,'enabled: true,'
level: 'info,'
}
    const maxLogFiles = 5}
  },'
models: {,'baseUrl: 'https://models.suoke.life,''/,'/g,'/;
  downloadTimeout: 60000,
retryAttempts: 3,
}
    const preloadModels = []}
  }
};
// 生产环境配置'/,'/g,'/;
  const: PRODUCTION_CONFIG: Partial<ONNXRuntimeConfig> = {,'environment: 'production,'
performanceMode: 'performance,'
inference: {,'executionProviders: ['cpu'];','';
enableOptimization: true,
enableProfiling: false,
sessionOptions: {intraOpNumThreads: 4,
interOpNumThreads: 2,'
graphOptimizationLevel: 'all,'';
enableMemPattern: true,
}
      const enableCpuMemArena = true}
    }
  },'
quantization: {,'level: 'int8,'';
outputPath: ,
preserveAccuracy: false,'
targetDevice: 'cpu,'
}
    const optimizationLevel = 'all}
  },'
optimization: {,'level: 'all,'';
enableGraphOptimization: true,
enableMemoryOptimization: true,
enableCpuOptimization: true,'
targetDevice: 'cpu,'
}
    const preserveAccuracy = false}
  }
edgeCompute: {maxConcurrentTasks: 5,
taskTimeout: 20000,
memoryLimit: 1024,
cpuThreshold: 90,'
thermalThreshold: 'fair,'';
enableLoadBalancing: true,
}
    const enableResourceMonitoring = true}
  }
logging: {,'enabled: false,'
level: 'error,'
}
    const maxLogFiles = 3}
  }
};
// 开发环境配置'/,'/g,'/;
  const: DEVELOPMENT_CONFIG: Partial<ONNXRuntimeConfig> = {,'environment: 'development,'
performanceMode: 'balanced,'
inference: {,'executionProviders: ['cpu'];','';
enableOptimization: false,
enableProfiling: true,
sessionOptions: {intraOpNumThreads: 1,
interOpNumThreads: 1,'
graphOptimizationLevel: 'basic,'';
enableMemPattern: false,
}
      const enableCpuMemArena = false}
    }
  }
logging: {,'enabled: true,'
level: 'debug,'
}
    const maxLogFiles = 10}
  },'
models: {,'baseUrl: 'http://localhost:8000/models,''/,'/g,'/;
  downloadTimeout: 120000,
retryAttempts: 1,
}
    const preloadModels = ['tcm_diagnosis_dev.onnx'];'}
  }
};
// iOS 平台特定配置/,/g,/;
  const: IOS_CONFIG: Partial<ONNXRuntimeConfig> = {,'inference: {,'executionProviders: ['coreml', 'cpu'],
enableOptimization: true,
enableProfiling: false,
sessionOptions: {intraOpNumThreads: 2,
interOpNumThreads: 1,'
graphOptimizationLevel: 'extended,'';
enableMemPattern: true,
}
      const enableCpuMemArena = true}
    }
  }
edgeCompute: {maxConcurrentTasks: 3,
taskTimeout: 30000,
memoryLimit: 512,
cpuThreshold: 75,'
thermalThreshold: 'nominal,'';
enableLoadBalancing: true,
}
    const enableResourceMonitoring = true}
  }
};
// Android 平台特定配置/,/g,/;
  const: ANDROID_CONFIG: Partial<ONNXRuntimeConfig> = {,'inference: {,'executionProviders: ['nnapi', 'cpu'],
enableOptimization: true,
enableProfiling: false,
sessionOptions: {intraOpNumThreads: 3,
interOpNumThreads: 1,'
graphOptimizationLevel: 'extended,'';
enableMemPattern: true,
}
      const enableCpuMemArena = true}
    }
  }
edgeCompute: {maxConcurrentTasks: 4,
taskTimeout: 30000,
memoryLimit: 768,
cpuThreshold: 85,'
thermalThreshold: 'nominal,'';
enableLoadBalancing: true,
}
    const enableResourceMonitoring = true}
  }
};
// 索克生活特定模型配置'
export const SUOKE_LIFE_MODELS_CONFIG = {tcm_diagnosis: {,'quantization: {,'level: 'int8' as const;','';
preserveAccuracy: true,
}
      const targetDevice = 'cpu' as const;'}
    },'
optimization: {,'level: 'extended' as const;','
}
      const preserveAccuracy = true}
    }
cache: {enabled: true,
}
      ttl: 3600000, // 1小时，诊断结果需要及时更新}
    }
  }
symptom_analysis: {,'quantization: {,'level: 'int8' as const;','';
preserveAccuracy: false,
}
      const targetDevice = 'cpu' as const;'}
    },'
optimization: {,'level: 'all' as const;','
}
      const preserveAccuracy = false}
    }
cache: {enabled: true,
}
      ttl: 1800000, // 30分钟，症状分析变化较快}
    }
  }
lifestyle: {,'quantization: {,'level: 'int8' as const;','';
preserveAccuracy: false,
}
      const targetDevice = 'cpu' as const;'}
    },'
optimization: {,'level: 'all' as const;','
}
      const preserveAccuracy = false}
    }
cache: {enabled: true,
}
      ttl: 86400000, // 24小时，生活方式推荐可以缓存较久}
    }
  }
};
/* 器 */
 */
export class ONNXConfigManager {private static instance: ONNXConfigManager;
private config: ONNXRuntimeConfig;
private constructor() {}
}
    this.config = this.buildConfig()}
  }
  static getInstance(): ONNXConfigManager {if (!ONNXConfigManager.instance) {}
      ONNXConfigManager.instance = new ONNXConfigManager()}
    }
    return ONNXConfigManager.instance;
  }
  /* 置 */
   */
getConfig(): ONNXRuntimeConfig {}
    return { ...this.config };
  }
  /* 置 */
   */
updateConfig(updates: Partial<ONNXRuntimeConfig>): void {}
    this.config = { ...this.config, ...updates ;};
  }
  /* 置 */
   */
getModelConfig(modelType: keyof typeof SUOKE_LIFE_MODELS_CONFIG) {}
    return SUOKE_LIFE_MODELS_CONFIG[modelType]}
  }
  /* 置 */
   */
adjustForDevicePerformance(cpuCores: number,);
memoryGB: number,);
const hasGPU = boolean);
  ): void {}
    const updates: Partial<ONNXRuntimeConfig> = {;
    // 根据CPU核心数调整线程数
if (cpuCores >= 8) {updates.inference = {}        ...this.config.inference,
const sessionOptions = {...this.config.inference.sessionOptions}intraOpNumThreads: 6,
}
          const interOpNumThreads = 2}
        }
      };
updates.edgeCompute = {...this.config.edgeCompute,}
        const maxConcurrentTasks = 6}
      };
    } else if (cpuCores >= 4) {updates.inference = {}        ...this.config.inference,
const sessionOptions = {...this.config.inference.sessionOptions}intraOpNumThreads: 4,
}
          const interOpNumThreads = 2}
        }
      };
updates.edgeCompute = {...this.config.edgeCompute,}
        const maxConcurrentTasks = 4}
      };
    }
    // 根据内存大小调整缓存和内存限制
if (memoryGB >= 8) {updates.cache = {}        ...this.config.cache,
}
        const maxSize = 200}
      };
updates.edgeCompute = {...this.config.edgeCompute,}
        const memoryLimit = 2048}
      };
    } else if (memoryGB >= 4) {updates.cache = {}        ...this.config.cache,
}
        const maxSize = 150}
      };
updates.edgeCompute = {...this.config.edgeCompute,}
        const memoryLimit = 1024}
      };
    }
    // 如果有GPU，添加GPU执行提供者'
if (hasGPU) {'const providers = [...this.config.inference.executionProviders];
if (Platform.OS === 'ios') {';}}
        providers.unshift('coreml');'}
      } else if (Platform.OS === 'android') {';}}
        providers.unshift('nnapi');'}
      }
      updates.inference = {...this.config.inference,}
        const executionProviders = providers}
      };
    }
    this.updateConfig(updates);
  }
  /* 置 */
   */
adjustForNetworkCondition(isOnline: boolean, isWiFi: boolean): void {}
    const updates: Partial<ONNXRuntimeConfig> = {;
if (!isOnline) {// 离线模式：禁用模型下载，增加缓存/updates.models = {...this.config.models}downloadTimeout: 0,/g/;
}
        const retryAttempts = 0}
      };
updates.cache = {...this.config.cache}enabled: true,
maxSize: this.config.cache.maxSize * 2,
}
        const ttl = this.config.cache.ttl * 2}
      };
    } else if (!isWiFi) {// 移动网络：减少下载超时，减少重试/updates.models = {...this.config.models}downloadTimeout: 30000,/g/;
}
        const retryAttempts = 1}
      };
    }
    this.updateConfig(updates);
  }
  /* 置 */
   */
resetToDefault(): void {}
    this.config = this.buildConfig()}
  }
  // 私有方法
private buildConfig(): ONNXRuntimeConfig {}
    let config = { ...DEFAULT_CONFIG };
    // 应用环境配置'/,'/g'/;
const env = this.getEnvironment();
if (env === 'production') {'}'';
config = { ...config, ...PRODUCTION_CONFIG };
    } else if (env === 'development') {'}'';
config = { ...config, ...DEVELOPMENT_CONFIG };
    }
    // 应用平台配置'/,'/g'/;
if (Platform.OS === 'ios') {'}'';
config = { ...config, ...IOS_CONFIG };
    } else if (Platform.OS === 'android') {'}'';
config = { ...config, ...ANDROID_CONFIG };
    }
    return config;
  }
  private getEnvironment(): Environment {// 这里可以根据实际情况判断环境'/if (__DEV__) {';}}'/g'/;
      return 'development}
    }
return 'production';
  }
}
/* 例 */
 */
export function getONNXConfig(): ONNXRuntimeConfig {};
  return ONNXConfigManager.getInstance().getConfig()}
}
/* 置 */
 */
export function getModelConfig(modelType: keyof typeof SUOKE_LIFE_MODELS_CONFIG);
) {}
  return ONNXConfigManager.getInstance().getModelConfig(modelType)}
}
/* 置 */
 */
export function updateONNXConfig(updates: Partial<ONNXRuntimeConfig>): void {};
  ONNXConfigManager.getInstance().updateConfig(updates)}
}
/* 置 */
 */
export function adjustConfigForDevice(cpuCores: number,);
memoryGB: number,);
const hasGPU = boolean);
): void {ONNXConfigManager.getInstance().adjustForDevicePerformance(cpuCores,)memoryGB,);
hasGPU);
}
  )}
}
/* 置 */
 */
export function adjustConfigForNetwork(isOnline: boolean,);
const isWiFi = boolean);
): void {}
  ONNXConfigManager.getInstance().adjustForNetworkCondition(isOnline, isWiFi)}
}
''