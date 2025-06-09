import { Platform } from "react-native";

import {/**

* * ONNX Runtime 配置文件
* 为索克生活项目提供设备端AI推理的配置管理
  InferenceConfig,
  QuantizationConfig,
  ModelOptimizationOptions,
  EdgeComputeConfig,
  { ExecutionProvider  } from "../../placeholder";../core/onnx-runtime/    types;
/**
* * 环境类型
export type Environment = development" | "staging | "production;";
/**
* * 设备类型
export type DeviceType = phone" | "tablet | "desktop;";
/**
* * 性能模式
export type PerformanceMode = power_save" | "balanced | "performance;";
/**
* * ONNX Runtime 配置接口
export interface ONNXRuntimeConfig {
  environment: Environment;,
  deviceType: DeviceType;
  performanceMode: PerformanceMode;,
  inference: InferenceConfig;
  quantization: QuantizationConfig;,
  optimization: ModelOptimizationOptions;
  edgeCompute: EdgeComputeConfig;,
  cache: {;
    enabled: boolean;,
  maxSize: number;
    ttl: number;
};
  logging: {,
  enabled: boolean;
    level: debug" | "info | "warn" | error,
  maxLogFiles: number;
  };
  models: {,
  baseUrl: string;
    downloadTimeout: number,
  retryAttempts: number;,
  preloadModels: string[];
  };
}
/**
* * 默认配置
const DEFAULT_CONFIG: ONNXRuntimeConfig = {,
  environment: "development,",
      deviceType: "phone",
  performanceMode: balanced",
  inference: {,
  executionProviders: ["cpu],"
    enableOptimization: true,
    enableProfiling: false,
    sessionOptions: {,
  intraOpNumThreads: 2,
      interOpNumThreads: 1,
      graphOptimizationLevel: "extended",
      enableMemPattern: true,
      enableCpuMemArena: true;
    }
  },
  quantization: {,
  level: int8",
    outputPath: ",",
    preserveAccuracy: true,
    targetDevice: "cpu",
    optimizationLevel: extended""
  },
  optimization: {,
  level: "extended,",
    enableGraphOptimization: true,
    enableMemoryOptimization: true,
    enableCpuOptimization: true,
    targetDevice: "cpu",
    preserveAccuracy: true;
  },
  edgeCompute: {,
  maxConcurrentTasks: 3,
    taskTimeout: 30000,
    memoryLimit: 512,
    cpuThreshold: 80,
    thermalThreshold: nominal",
    enableLoadBalancing: true,
    enableResourceMonitoring: true;
  },
  cache: {,
  enabled: true,
    maxSize: 100,
    ttl: 3600000 // 1小时
  },
  logging: {,
  enabled: true,
    level: "info,",
    maxLogFiles: 5;
  },
  models: {,
  baseUrl: "https:// models.suokelife.com",
    downloadTimeout: 60000,
    retryAttempts: 3,
    preloadModels: []
  }
}
/**
* * 生产环境配置
const PRODUCTION_CONFIG: Partial<ONNXRuntimeConfig> = {environment: production",
  performanceMode: "performance,",
  inference: {,
  executionProviders: ["cpu"],
    enableOptimization: true,
    enableProfiling: false,
    sessionOptions: {,
  intraOpNumThreads: 4,
      interOpNumThreads: 2,
      graphOptimizationLevel: all",
      enableMemPattern: true,
      enableCpuMemArena: true;
    }
  },
  quantization: {,
  level: "int8,",
    outputPath: ",
    preserveAccuracy: false, // 生产环境可以牺牲一些精度换取性能
targetDevice: cpu","
    optimizationLevel: "all"
  },
  optimization: {,
  level: "all",
    enableGraphOptimization: true,
    enableMemoryOptimization: true,
    enableCpuOptimization: true,
    targetDevice: cpu",
    preserveAccuracy: false;
  },
  edgeCompute: {,
  maxConcurrentTasks: 5,
    taskTimeout: 20000,
    memoryLimit: 1024,
    cpuThreshold: 90,
    thermalThreshold: "fair,",
    enableLoadBalancing: true,
    enableResourceMonitoring: true;
  },
  logging: {,
  enabled: false, // 生产环境关闭详细日志
level: "error",
    maxLogFiles: 3;
  }
};
/**
* * 开发环境配置
const DEVELOPMENT_CONFIG: Partial<ONNXRuntimeConfig> = {environment: development",
  performanceMode: "balanced,",
  inference: {,
  executionProviders: ["cpu"],
    enableOptimization: false, // 开发环境关闭优化便于调试
enableProfiling: true,
    sessionOptions: {,
  intraOpNumThreads: 1,
      interOpNumThreads: 1,
      graphOptimizationLevel: basic",
      enableMemPattern: false,
      enableCpuMemArena: false;
    }
  },
  logging: {,
  enabled: true,
    level: "debug,",
    maxLogFiles: 10;
  },
  models: {,
  baseUrl: "http:///    models",
    downloadTimeout: 120000,
    retryAttempts: 1,
    preloadModels: [tcm_diagnosis_dev.onnx"]"
  }
}
/**
* * iOS 平台特定配置
const IOS_CONFIG: Partial<ONNXRuntimeConfig> = {inference: {,
  executionProviders: ["coreml, "cpu"], // iOS优先使用CoreML"
sessionOptions: {,
  intraOpNumThreads: 2,
      interOpNumThreads: 1;
    }
  },
  edgeCompute: {,
  maxConcurrentTasks: 3,
    memoryLimit: 512,
    cpuThreshold: 75 // iOS设备热管理更严格
  }
}
/**
* * Android 平台特定配置
const ANDROID_CONFIG: Partial<ONNXRuntimeConfig> = {inference: {,
  executionProviders: [nnapi", "cpu], // Android优先使用NNAPI;
sessionOptions: {,
  intraOpNumThreads: 4,
      interOpNumThreads: 2;
    }
  },
  edgeCompute: {,
  maxConcurrentTasks: 4,
    memoryLimit: 768,
    cpuThreshold: 85;
  }
};
/**
* * 索克生活项目特定配置
export const SUOKE_LIFE_MODELS_CONFIG = {tcm: {quantization: {level: "int8" as const,preserveAccuracy: true,targetDevice: cpu" as const";
    },optimization: {level: "extended as const,";
      preserveAccuracy: true;
    },
    cache: {,
  enabled: true,
      ttl: 7200000 // 2小时，中医诊断结果可以缓存更久
    }
  },
  health: {,
  quantization: {
      level: "fp16" as const,
      preserveAccuracy: true,
      targetDevice: cpu" as const"
    },
    optimization: {,
  level: "extended as const,",
      preserveAccuracy: true;
    },
    cache: {,
  enabled: true,
      ttl: 3600000 // 1小时
    }
  },
  symptom: {,
  quantization: {
      level: "dynamic" as const,
      preserveAccuracy: false,
      targetDevice: cpu" as const"
    },
    optimization: {,
  level: "all as const,",
      preserveAccuracy: false;
    },
    cache: {,
  enabled: true,
      ttl: 1800000 // 30分钟，症状分析变化较快
    }
  },
  lifestyle: {,
  quantization: {
      level: "int8" as const,
      preserveAccuracy: false,
      targetDevice: cpu" as const"
    },
    optimization: {,
  level: "all as const,",
      preserveAccuracy: false;
    },
    cache: {,
  enabled: true,
      ttl: 86400000 // 24小时，生活方式推荐可以缓存较久
    }
  }
};
/**
* * 配置管理器
export class ONNXConfigManager {private static instance: ONNXConfigManager;
  private config: ONNXRuntimeConfig;
  private constructor() {
    this.config = this.buildConfig();
  }
  static getInstance(): ONNXConfigManager {
    if (!ONNXConfigManager.instance) {
      ONNXConfigManager.instance = new ONNXConfigManager();
    }
    return ONNXConfigManager.instance;
  }
  /**
* * 获取当前配置
  getConfig(): ONNXRuntimeConfig {
    return { ...this.config };
  }
  /**
* * 更新配置
  updateConfig(updates: Partial<ONNXRuntimeConfig>): void {
    this.config = { ...this.config, ...updates };
  }
  /**
* * 获取特定模型类型的配置
  getModelConfig(modelType: keyof typeof SUOKE_LIFE_MODELS_CONFIG) {
    return SUOKE_LIFE_MODELS_CONFIG[modelType];
  }
  /**
* * 根据设备性能调整配置
  adjustForDevicePerformance()
    cpuCores: number,
    memoryGB: number,
    hasGPU: boolean;
  ): void {
    const updates: Partial<ONNXRuntimeConfig> = {};
    // 根据CPU核心数调整线程数
if (cpuCores >= 8) {
      updates.inference = {
        ...this.config.inference,
        sessionOptions: {
          ...this.config.inference.sessionOptions,
          intraOpNumThreads: 6,
          interOpNumThreads: 2;
        }
      };
      updates.edgeCompute = {
        ...this.config.edgeCompute,
        maxConcurrentTasks: 6;
      };
    } else if (cpuCores >= 4) {
      updates.inference = {
        ...this.config.inference,
        sessionOptions: {
          ...this.config.inference.sessionOptions,
          intraOpNumThreads: 4,
          interOpNumThreads: 2;
        }
      };
      updates.edgeCompute = {
        ...this.config.edgeCompute,
        maxConcurrentTasks: 4;
      };
    }
    // 根据内存大小调整缓存和内存限制
if (memoryGB >= 8) {
      updates.cache = {
        ...this.config.cache,
        maxSize: 200;
      };
      updates.edgeCompute = {
        ...this.config.edgeCompute,
        memoryLimit: 2048;
      };
    } else if (memoryGB >= 4) {
      updates.cache = {
        ...this.config.cache,
        maxSize: 150;
      };
      updates.edgeCompute = {
        ...this.config.edgeCompute,
        memoryLimit: 1024;
      };
    }
    // 如果有GPU，添加GPU执行提供者
if (hasGPU) {
      const providers = [...this.config.inference.executionProviders];
      if (Platform.OS === "ios") {
        providers.unshift(coreml");"
      } else if (Platform.OS === "android) {"
        providers.unshift("nnapi");
      }
      updates.inference = {
        ...this.config.inference,
        executionProviders: providers as ExecutionProvider[]
      };
    }
    this.updateConfig(updates);
  }
  /**
* * 根据网络状况调整配置
  adjustForNetworkCondition(isOnline: boolean, isWiFi: boolean): void {
    const updates: Partial<ONNXRuntimeConfig> = {};
    if (!isOnline) {
      // 离线模式：禁用模型下载，增加缓存
updates.models = {
        ...this.config.models,
        downloadTimeout: 0,
        retryAttempts: 0;
      };
      updates.cache = {
        ...this.config.cache,
        enabled: true,
        maxSize: this.config.cache.maxSize * 2,
        ttl: this.config.cache.ttl * 2;
      };
    } else if (!isWiFi) {
      // 移动网络：减少下载超时，减少重试
updates.models = {
        ...this.config.models,
        downloadTimeout: 30000,
        retryAttempts: 1;
      };
    }
    this.updateConfig(updates);
  }
  /**
* * 重置为默认配置
  resetToDefault(): void {
    this.config = this.buildConfig();
  }
  // 私有方法
private buildConfig(): ONNXRuntimeConfig {
    let config = { ...DEFAULT_CONFIG };
    // 应用环境配置
const env = this.getEnvironment();
    if (env === production") {"
      config = { ...config, ...PRODUCTION_CONFIG };
    } else if (env === "development) {"
      config = { ...config, ...DEVELOPMENT_CONFIG };
    }
    // 应用平台配置
if (Platform.OS === "ios") {
      config = { ...config, ...IOS_CONFIG };
    } else if (Platform.OS === android") {"
      config = { ...config, ...ANDROID_CONFIG };
    }
    return config;
  }
  private getEnvironment(): Environment {
    // 这里可以根据实际情况判断环境
if (__DEV__) {
      return "development;"
    }
    return "production';"'
  }
}
/**
* * 便捷函数：获取配置实例
export function getONNXConfig(): ONNXRuntimeConfig {return ONNXConfigManager.getInstance().getConfig();
}
/**
* * 便捷函数：获取模型特定配置
export function getModelConfig(modelType: keyof typeof SUOKE_LIFE_MODELS_CONFIG) {return ONNXConfigManager.getInstance().getModelConfig(modelType);
}
/**
* * 便捷函数：更新配置
export function updateONNXConfig(updates: Partial<ONNXRuntimeConfig>): void {ONNXConfigManager.getInstance().updateConfig(updates);
}
/**
* * 便捷函数：根据设备调整配置
export function adjustConfigForDevice(;)
  cpuCores: number,memoryGB: number,hasGPU: boolean;
): void {
  ONNXConfigManager.getInstance().adjustForDevicePerformance(cpuCores, memoryGB, hasGPU);
}
/**
* * 便捷函数：根据网络调整配置
export function adjustConfigForNetwork(isOnline: boolean, isWiFi: boolean): void {ONNXConfigManager.getInstance().adjustForNetworkCondition(isOnline, isWiFi);
}  */
}