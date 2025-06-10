export type DataType = "float32" | "int32" | "uint8" | "int64" | "bool";";"";
// 量化配置/;,/g/;
export interface QuantizationConfig {;,}const level = QuantizationLevel;
calibrationDataPath?: string;
outputPath: string,;
preserveAccuracy: boolean,;
targetDevice: TargetDevice,;
}
}
  const optimizationLevel = OptimizationLevel;}";"";
}";,"";
export type QuantizationLevel = "int8 | "int16" | fp16" | "dynami;c;";";,"";
export type TargetDevice = "cpu" | gpu" | "npu | "auto;";";,"";
export type OptimizationLevel = basic" | "extended | "all;";";"";
// 边缘计算配置/;,/g/;
export interface EdgeComputeConfig {enableBatching: boolean}batchSize: number,;
maxConcurrentSessions: number,;
memoryLimit: number,;
cpuThreads: number,;
enableGPU: boolean,;
enableNPU: boolean,;
fallbackStrategy: FallbackStrategy,;
}
}
  const powerOptimization = PowerOptimizationLevel;}";"";
}";,"";
export type FallbackStrategy = cpu-only" | "cloud-fallback | "cache-only;";";,"";
export type PowerOptimizationLevel = performance" | "balanced | "power-save;";";"";
// 设备能力检测/;,/g/;
export interface DeviceCapabilities {cpu: CPUCapabilities}const memory = MemoryCapabilities;
gpu?: GPUCapabilities;
npu?: NPUCapabilities;
supportedProviders: ExecutionProvider[],;
}
}
  const recommendedConfig = EdgeComputeConfig;}
}
export interface CPUCapabilities {cores: number}architecture: string,;
frequency: number,;
supportedInstructions: string[],;
}
}
  const thermalThrottling = boolean;}
}
export interface MemoryCapabilities {total: number}available: number,;
type: string,;
}
}
  const bandwidth = number;}
}
export interface GPUCapabilities {vendor: string}model: string,;
memory: number,;
computeUnits: number,;
}
}
  const supportedAPIs = string[];}
}
export interface NPUCapabilities {vendor: string}model: string,;
tops: number,;
supportedPrecisions: string[],;
}
}
  const driverVersion = string;}";"";
}";,"";
export type ExecutionProvider = | cpu";"";"";
  | "coreml"";"";
  | "nnapi";";"";
  | xnnpack";"";"";
  | "webgl";";"";
  | "webgpu";";"";
  | qnn";"";"";
  | "snp;e;"";"";
// 推理结果/;,/g/;
export interface InferenceResult {sessionId: string}modelId: string,;
outputs: Map<string, TensorData>;
latency: number,;
const memoryUsage = number;
confidence?: number;
const timestamp = Date;
}
}
  metadata?: Record<string; any>;}
}
// 模型优化选项/;,/g/;
export interface ModelOptimizationOptions {enableGraphOptimization: boolean}enableMemoryPattern: boolean,;
enableCPUMemArena: boolean,;
executionMode: ExecutionMode,;
graphOptimizationLevel: GraphOptimizationLevel,;
enableProfiling: boolean,;
}
}
  const logSeverityLevel = LogLevel;}";"";
}";,"";
export type ExecutionMode = "sequential" | parallel;";,"";
export type GraphOptimizationLevel = "disabled | "basic" | extended" | "al;l;";";,"";
export type LogLevel = "verbose" | info" | "warning | "error" | fatal;";"";
// 缓存配置/;,/g/;
export interface CacheConfig {enableModelCache: boolean}enableInferenceCache: boolean,;
maxCacheSize: number,;
cacheDirectory: string,;
ttl: number,;
compressionEnabled: boolean,;
}
}
  const encryptionEnabled = boolean;}
}
// 模型加载选项/;,/g/;
export interface ModelLoadOptions {providers: ExecutionProvider[]}sessionOptions: ModelOptimizationOptions,;
enableProfiling: boolean,;
const warmupRuns = number;
}
}
  preloadInputs?: TensorData[];}
}
// 性能指标/;,/g/;
export interface PerformanceMetrics {modelLoadTime: number}firstInferenceTime: number,;
averageInferenceTime: number,;
memoryPeakUsage: number,;
const cpuUsage = number;
gpuUsage?: number;
powerConsumption?: number;
}
}
  thermalState?: ThermalState;}";"";
}";,"";
export type ThermalState = "nominal | "fair" | serious" | "critica;l;";";"";
// 错误类型/;,/g/;
export interface ONNXError {code: ONNXErrorCode}const message = string;
details?: any;
const timestamp = Date;
sessionId?: string;
}
}
  modelId?: string;}";"";
}";,"";
export type ONNXErrorCode = | "MODEL_LOAD_FAILED";";"";
  | INFERENCE_FAILED";"";
  | "MEMORY_INSUFFICIENT"";"";
  | "PROVIDER_NOT_AVAILABLE";";"";
  | INVALID_INPUT";"";"";
  | "QUANTIZATION_FAILED";";"";
  | "OPTIMIZATION_FAILED";";"";
  | CACHE_ERROR";"";"";
  | "DEVICE_NOT_SUPPORTE;D;"";"";
// 事件类型/;,/g/;
export interface ONNXEvent {type: ONNXEventType}timestamp: Date,;
const data = any;
sessionId?: string;
}
}
  modelId?: string;}";"";
}";,"";
export type ONNXEventType = | "model_loaded";";"";
  | model_unloaded";"";
  | "inference_started"";"";
  | "inference_completed"";"";
  | inference_failed";"";"";
  | "cache_hit";";"";
  | "cache_miss";";"";
  | optimization_completed";"";"";
  | "quantization_completed";";"";
  | "device_capability_detected;';"'';