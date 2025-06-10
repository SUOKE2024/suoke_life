import {CacheConfig}EdgeComputeConfig,;
ExecutionProvider,;
ModelOptimizationOptions,;
OptimizationLevel,;
}
  QuantizationLevel,};
} from "./types";""/;"/g"/;

// 动态内存配置函数/;,/g/;
export const getDeviceMemoryInfo = async (): Promise<{totalMemory: number,";,}availableMemory: number,';'';
}
  const memoryTier = 'LOW' | 'MEDIUM' | 'HIGH';'}'';'';
}> => {// 在实际应用中，这里会调用原生模块获取设备内存信息/;,}totalMemory: 4 * 1024 * 1024 * 1024; // 默认4GB,/;,/g/;
const availableMemory = totalMemory * 0.6; // 假设60%可用'/;'/g'/;
';,'';
const let = memoryTier: 'LOW' | 'MEDIUM' | 'HIGH';';,'';
if (totalMemory < DEVICE_THRESHOLDS.MEMORY.LOW) {';}}'';
    memoryTier = 'LOW';'}'';'';
  } else if (totalMemory < DEVICE_THRESHOLDS.MEMORY.MEDIUM) {';}}'';
    memoryTier = 'MEDIUM';'}'';'';
  } else {';}}'';
    memoryTier = 'HIGH';'}'';'';
  }

  return { totalMemory, availableMemory, memoryTier };
};

// 支持的模型类型 - 优化内存需求/;,/g/;
export const SUPPORTED_MODELS = {';,}TCM_DIAGNOSIS: {,';,}id: 'tcm-diagnosis-v1';','';
inputShape: [1, 224, 224, 3],';,'';
outputShape: [1, 100],';,'';
domain: 'tcm';','';'';
}
    minMemory: 256 * 1024 * 1024, // 减少到256MB}/;/g/;
  ;},';,'';
HEALTH_ASSESSMENT: {,';,}id: 'health-assessment-v1';','';
inputShape: [1, 50],';,'';
outputShape: [1, 10],';,'';
domain: 'health';','';'';
}
    minMemory: 128 * 1024 * 1024, // 减少到128MB}/;/g/;
  ;},';,'';
SYMPTOM_ANALYSIS: {,';,}id: 'symptom-analysis-v1';','';
inputShape: [1, 768],';,'';
outputShape: [1, 200],';,'';
domain: 'medical';','';'';
}
    minMemory: 512 * 1024 * 1024, // 减少到512MB}/;/g/;
  ;},';,'';
LIFESTYLE_RECOMMENDATION: {,';,}id: 'lifestyle-rec-v1';','';
inputShape: [1, 100],';,'';
outputShape: [1, 50],';,'';
domain: 'lifestyle';','';'';
}
    minMemory: 64 * 1024 * 1024, // 减少到64MB}/;/g/;
  ;}
} as const;

// 动态配置生成函数/;,/g/;
export const createDynamicConfig = async (): Promise<{EDGE_COMPUTE: EdgeComputeConfig}MODEL_OPTIMIZATION: ModelOptimizationOptions,;
}
  const CACHE = CacheConfig;}
}> => {}
  const { totalMemory, availableMemory, memoryTier } =;
const await = getDeviceMemoryInfo();

  // 根据设备内存动态调整配置'/;,'/g'/;
const  memoryMultiplier =';,'';
memoryTier === 'LOW' ? 0.3 : memoryTier === 'MEDIUM' ? 0.5 : 0.7;';,'';
const maxMemoryLimit = Math.floor(availableMemory * memoryMultiplier);
const maxCacheSize = Math.floor(maxMemoryLimit * 0.2); // 缓存占用20%/;,/g/;
return {EDGE_COMPUTE: {,';,}enableBatching: true,';,'';
batchSize: memoryTier === 'LOW' ? 1 : 2;','';
const maxConcurrentSessions = ';,'';
memoryTier === 'LOW' ? 1 : memoryTier === 'MEDIUM' ? 2 : 3;','';
memoryLimit: maxMemoryLimit,';,'';
cpuThreads: memoryTier === 'LOW' ? 2 : 4;','';
enableGPU: memoryTier !== 'LOW';','';
enableNPU: false,';,'';
fallbackStrategy: 'cpu-only';','';'';
}
      powerOptimization: memoryTier === 'LOW' ? 'power-save' : 'balanced';'}'';'';
    } as EdgeComputeConfig,;
MODEL_OPTIMIZATION: {enableGraphOptimization: true,';,'';
enableMemoryPattern: true,';,'';
enableCPUMemArena: memoryTier !== 'LOW';','';
executionMode: memoryTier === 'LOW' ? 'sequential' : 'parallel';','';
graphOptimizationLevel: memoryTier === 'LOW' ? 'basic' : 'extended';','';
enableProfiling: false,';'';
}
      const logSeverityLevel = 'warning';'}'';'';
    } as ModelOptimizationOptions,;
CACHE: {,';,}enableModelCache: true,';,'';
enableInferenceCache: memoryTier !== 'LOW';','';
maxCacheSize: maxCacheSize,';,'';
cacheDirectory: 'onnx_cache';','';
ttl: memoryTier === 'LOW' ? 12 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000, // 低内存设备缓存时间减半'/;,'/g,'/;
  compressionEnabled: true,';'';
}
      encryptionEnabled: memoryTier !== 'LOW';'}'';'';
    } as CacheConfig,;
  };
};

// 默认配置（向后兼容）/;,/g/;
export const DEFAULT_CONFIGS = {EDGE_COMPUTE: {enableBatching: true,;
batchSize: 1,;
maxConcurrentSessions: 2, // 减少并发会话/;,/g,/;
  memoryLimit: 1 * 1024 * 1024 * 1024, // 减少到1GB,/;,/g,/;
  cpuThreads: 4,;
enableGPU: true,';,'';
enableNPU: false,';,'';
fallbackStrategy: 'cpu-only';','';'';
}
    const powerOptimization = 'balanced';'}'';'';
  } as EdgeComputeConfig,;
MODEL_OPTIMIZATION: {enableGraphOptimization: true,;
enableMemoryPattern: true,';,'';
enableCPUMemArena: true,';,'';
executionMode: 'parallel';','';
graphOptimizationLevel: 'extended';','';
enableProfiling: false,';'';
}
    const logSeverityLevel = 'warning';'}'';'';
  } as ModelOptimizationOptions,;
CACHE: {enableModelCache: true,;
enableInferenceCache: true,';,'';
maxCacheSize: 512 * 1024 * 1024, // 减少到512MB,'/;,'/g,'/;
  cacheDirectory: 'onnx_cache';','';
ttl: 24 * 60 * 60 * 1000, // 24小时/;,/g,/;
  compressionEnabled: true,;
}
    const encryptionEnabled = true;}
  } as CacheConfig,;
} as const;

// 执行提供者优先级'/;,'/g'/;
export const PROVIDER_PRIORITY: Record<string, ExecutionProvider[]> = {';,}ios: ['coreml', 'cpu'],';,'';
android: ['nnapi', 'xnnpack', 'cpu'],';,'';
web: ['webgpu', 'webgl', 'cpu'],';'';
}
  const default = ['cpu'];'}'';'';
};

// 量化级别配置/;,/g/;
export const QUANTIZATION_CONFIGS = {';,}int8: {,';,}level: 'int8' as QuantizationLevel;','';
compressionRatio: 4,;
accuracyLoss: 0.02,;
speedGain: 2.5,;
}
    const memoryReduction = 0.75;}
  },';,'';
int16: {,';,}level: 'int16' as QuantizationLevel;','';
compressionRatio: 2,;
accuracyLoss: 0.005,;
speedGain: 1.5,;
}
    const memoryReduction = 0.5;}
  },';,'';
fp16: {,';,}level: 'fp16' as QuantizationLevel;','';
compressionRatio: 2,;
accuracyLoss: 0.001,;
speedGain: 1.8,;
}
    const memoryReduction = 0.5;}
  },';,'';
dynamic: {,';,}level: 'dynamic' as QuantizationLevel;','';
compressionRatio: 3,;
accuracyLoss: 0.01,;
speedGain: 2.0,;
}
    const memoryReduction = 0.67;}
  }
} as const;

// 优化级别配置/;,/g/;
export const OPTIMIZATION_LEVELS = {';,}basic: {,';,}level: 'basic' as OptimizationLevel;','';
enableConstantFolding: true,;
enableRedundantNodeElimination: true,;
enableCommonSubexpressionElimination: false,;
}
    const enableLoopOptimization = false;}
  },';,'';
extended: {,';,}level: 'extended' as OptimizationLevel;','';
enableConstantFolding: true,;
enableRedundantNodeElimination: true,;
enableCommonSubexpressionElimination: true,;
}
    const enableLoopOptimization = true;}
  },';,'';
all: {,';,}level: 'all' as OptimizationLevel;','';
enableConstantFolding: true,;
enableRedundantNodeElimination: true,;
enableCommonSubexpressionElimination: true,;
enableLoopOptimization: true,;
enableMemoryOptimization: true,;
}
    const enableKernelFusion = true;}
  }
} as const;

// 设备能力阈值/;,/g/;
export const DEVICE_THRESHOLDS = {MEMORY: {LOW: 1 * 1024 * 1024 * 1024, // 1GB,/;,/g,/;
  MEDIUM: 4 * 1024 * 1024 * 1024, // 4GB,/;/g/;
}
    HIGH: 8 * 1024 * 1024 * 1024, // 8GB};/;/g/;
  ;}
CPU_CORES: {LOW: 2,;
MEDIUM: 4,;
}
    const HIGH = 8;}
  }
THERMAL: {SAFE_TEMPERATURE: 70, // 摄氏度/;,/g,/;
  WARNING_TEMPERATURE: 80,;
}
    const CRITICAL_TEMPERATURE = 90;}
  }
} as const;

// 性能基准/;,/g/;
export const PERFORMANCE_BENCHMARKS = {INFERENCE_TIME: {EXCELLENT: 50, // ms,/;,/g,/;
  GOOD: 100,;
ACCEPTABLE: 200,;
}
    const POOR = 500;}
  }
MEMORY_USAGE: {LOW: 100 * 1024 * 1024, // 100MB,/;,/g,/;
  MEDIUM: 500 * 1024 * 1024, // 500MB,/;/g/;
}
    HIGH: 1024 * 1024 * 1024, // 1GB}/;/g/;
  ;}
CPU_USAGE: {LOW: 20, // %/;,/g,/;
  MEDIUM: 50,;
}
    const HIGH = 80;}
  }
} as const;

// 错误消息/;,/g/;
export const ERROR_MESSAGES = {}}
};
} as const;
';'';
// 模型文件扩展名'/;,'/g'/;
export MODEL_EXTENSIONS: ['.onnx', '.ort'] as const;';'';

// 支持的张量类型'/;,'/g'/;
export const SUPPORTED_TENSOR_TYPES = [;]';'';
  'float32',';'';
  'int32',';'';
  'uint8',';'';
  'int64',';'';
  'bool',';'';
];
] as const;

// 缓存键前缀'/;,'/g'/;
export const CACHE_KEYS = {';,}MODEL: 'onnx_model_';','';
INFERENCE: 'onnx_inference_';','';
DEVICE_CAPS: 'device_capabilities_';','';'';
}
  const PERFORMANCE = 'performance_metrics_';'}'';'';
} as const;

// 事件名称'/;,'/g'/;
export const EVENT_NAMES = {';,}MODEL_LOADED: 'model_loaded';','';
MODEL_UNLOADED: 'model_unloaded';','';
INFERENCE_STARTED: 'inference_started';','';
INFERENCE_COMPLETED: 'inference_completed';','';
INFERENCE_FAILED: 'inference_failed';','';
CACHE_HIT: 'cache_hit';','';
CACHE_MISS: 'cache_miss';','';
OPTIMIZATION_COMPLETED: 'optimization_completed';','';
QUANTIZATION_COMPLETED: 'quantization_completed';','';'';
}
  const DEVICE_CAPABILITY_DETECTED = 'device_capability_detected';'}'';'';
} as const;

// 默认超时时间/;,/g/;
export const TIMEOUTS = {MODEL_LOAD: 30000, // 30秒/;,}INFERENCE: 10000, // 10秒/;,/g,/;
  QUANTIZATION: 300000, // 5分钟/;/g/;
}
  OPTIMIZATION: 180000, // 3分钟};/;/g/;
;} as const;';'';
''';