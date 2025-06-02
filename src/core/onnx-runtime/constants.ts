import { 
  EdgeComputeConfig, 
  ModelOptimizationOptions, 
  CacheConfig,
  ExecutionProvider,
  QuantizationLevel,
  { OptimizationLevel } from './types';
// 支持的模型类型
export const SUPPORTED_MODELS = {
  TCM_DIAGNOSIS: {
    id: 'tcm-diagnosis-v1',
    name: '中医诊断模型',
    inputShape: [1, 224, 224, 3],
    outputShape: [1, 100],
    domain: 'tcm',
    minMemory: 512 * 1024 * 1024, // 512MB
  },
  HEALTH_ASSESSMENT: {
    id: 'health-assessment-v1',
    name: '健康评估模型',
    inputShape: [1, 50],
    outputShape: [1, 10],
    domain: 'health',
    minMemory: 256 * 1024 * 1024, // 256MB
  },
  SYMPTOM_ANALYSIS: {
    id: 'symptom-analysis-v1',
    name: '症状分析模型',
    inputShape: [1, 768],
    outputShape: [1, 200],
    domain: 'medical',
    minMemory: 1024 * 1024 * 1024, // 1GB
  },
  LIFESTYLE_RECOMMENDATION: {
    id: 'lifestyle-rec-v1',
    name: '生活方式推荐模型',
    inputShape: [1, 100],
    outputShape: [1, 50],
    domain: 'lifestyle',
    minMemory: 128 * 1024 * 1024, // 128MB
  }
} as const;

// 默认配置
export const DEFAULT_CONFIGS = {
  EDGE_COMPUTE: {
    enableBatching: true,
    batchSize: 1,
    maxConcurrentSessions: 3,
    memoryLimit: 2 * 1024 * 1024 * 1024, // 2GB
    cpuThreads: 4,
    enableGPU: true,
    enableNPU: false,
    fallbackStrategy: 'cpu-only',
    powerOptimization: 'balanced'
  } as EdgeComputeConfig,

  MODEL_OPTIMIZATION: {
    enableGraphOptimization: true,
    enableMemoryPattern: true,
    enableCPUMemArena: true,
    executionMode: 'parallel',
    graphOptimizationLevel: 'extended',
    enableProfiling: false,
    logSeverityLevel: 'warning'
  } as ModelOptimizationOptions,

  CACHE: {
    enableModelCache: true,
    enableInferenceCache: true,
    maxCacheSize: 1024 * 1024 * 1024, // 1GB
    cacheDirectory: 'onnx_cache',
    ttl: 24 * 60 * 60 * 1000, // 24小时
    compressionEnabled: true,
    encryptionEnabled: true
  } as CacheConfig
} as const;

// 执行提供者优先级
export const PROVIDER_PRIORITY: Record<string, ExecutionProvider[]> = {
  ios: ['coreml', 'cpu'],
  android: ['nnapi', 'xnnpack', 'cpu'],
  web: ['webgpu', 'webgl', 'cpu'],
  default: ['cpu']
};

// 量化级别配置
export const QUANTIZATION_CONFIGS = {
  int8: {
    level: 'int8' as QuantizationLevel,
    compressionRatio: 4,
    accuracyLoss: 0.02,
    speedGain: 2.5,
    memoryReduction: 0.75
  },
  int16: {
    level: 'int16' as QuantizationLevel,
    compressionRatio: 2,
    accuracyLoss: 0.005,
    speedGain: 1.5,
    memoryReduction: 0.5
  },
  fp16: {
    level: 'fp16' as QuantizationLevel,
    compressionRatio: 2,
    accuracyLoss: 0.001,
    speedGain: 1.8,
    memoryReduction: 0.5
  },
  dynamic: {
    level: 'dynamic' as QuantizationLevel,
    compressionRatio: 3,
    accuracyLoss: 0.01,
    speedGain: 2.0,
    memoryReduction: 0.67
  }
} as const;

// 优化级别配置
export const OPTIMIZATION_LEVELS = {
  basic: {
    level: 'basic' as OptimizationLevel,
    enableConstantFolding: true,
    enableRedundantNodeElimination: true,
    enableCommonSubexpressionElimination: false,
    enableLoopOptimization: false
  },
  extended: {
    level: 'extended' as OptimizationLevel,
    enableConstantFolding: true,
    enableRedundantNodeElimination: true,
    enableCommonSubexpressionElimination: true,
    enableLoopOptimization: true
  },
  all: {
    level: 'all' as OptimizationLevel,
    enableConstantFolding: true,
    enableRedundantNodeElimination: true,
    enableCommonSubexpressionElimination: true,
    enableLoopOptimization: true,
    enableMemoryOptimization: true,
    enableKernelFusion: true
  }
} as const;

// 设备能力阈值
export const DEVICE_THRESHOLDS = {
  MEMORY: {
    LOW: 1 * 1024 * 1024 * 1024,    // 1GB
    MEDIUM: 4 * 1024 * 1024 * 1024, // 4GB
    HIGH: 8 * 1024 * 1024 * 1024    // 8GB
  },
  CPU_CORES: {
    LOW: 2,
    MEDIUM: 4,
    HIGH: 8
  },
  THERMAL: {
    SAFE_TEMPERATURE: 70, // 摄氏度
    WARNING_TEMPERATURE: 80,
    CRITICAL_TEMPERATURE: 90
  }
} as const;

// 性能基准
export const PERFORMANCE_BENCHMARKS = {
  INFERENCE_TIME: {
    EXCELLENT: 50,   // ms
    GOOD: 100,
    ACCEPTABLE: 200,
    POOR: 500
  },
  MEMORY_USAGE: {
    LOW: 100 * 1024 * 1024,    // 100MB
    MEDIUM: 500 * 1024 * 1024, // 500MB
    HIGH: 1024 * 1024 * 1024   // 1GB
  },
  CPU_USAGE: {
    LOW: 20,    // %
    MEDIUM: 50,
    HIGH: 80
  }
} as const;

// 错误消息
export const ERROR_MESSAGES = {
  MODEL_LOAD_FAILED: '模型加载失败',
  INFERENCE_FAILED: '推理执行失败',
  MEMORY_INSUFFICIENT: '内存不足',
  PROVIDER_NOT_AVAILABLE: '执行提供者不可用',
  INVALID_INPUT: '输入数据无效',
  QUANTIZATION_FAILED: '模型量化失败',
  OPTIMIZATION_FAILED: '模型优化失败',
  CACHE_ERROR: '缓存操作失败',
  DEVICE_NOT_SUPPORTED: '设备不支持'
} as const;

// 模型文件扩展名
export const MODEL_EXTENSIONS = ['.onnx', '.ort'] as const;

// 支持的张量类型
export const SUPPORTED_TENSOR_TYPES = [
  'float32',
  'int32',
  'uint8',
  'int64',
  'bool'
] as const;

// 缓存键前缀
export const CACHE_KEYS = {
  MODEL: 'onnx_model_',
  INFERENCE: 'onnx_inference_',
  DEVICE_CAPS: 'device_capabilities_',
  PERFORMANCE: 'performance_metrics_'
} as const;

// 事件名称
export const EVENT_NAMES = {
  MODEL_LOADED: 'model_loaded',
  MODEL_UNLOADED: 'model_unloaded',
  INFERENCE_STARTED: 'inference_started',
  INFERENCE_COMPLETED: 'inference_completed',
  INFERENCE_FAILED: 'inference_failed',
  CACHE_HIT: 'cache_hit',
  CACHE_MISS: 'cache_miss',
  OPTIMIZATION_COMPLETED: 'optimization_completed',
  QUANTIZATION_COMPLETED: 'quantization_completed',
  DEVICE_CAPABILITY_DETECTED: 'device_capability_detected'
} as const;

// 默认超时时间
export const TIMEOUTS = {
  MODEL_LOAD: 30000,      // 30秒
  INFERENCE: 10000,       // 10秒
  QUANTIZATION: 300000,   // 5分钟
  OPTIMIZATION: 180000    // 3分钟
} as const; 