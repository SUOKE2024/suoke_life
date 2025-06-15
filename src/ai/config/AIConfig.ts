/**
 * AI配置文件
 * 包含各种AI模型的配置信息
 */

import { AIModelConfig, AITaskType, LLMModelType } from '../types/AITypes';

// 默认AI模型配置
export const DEFAULT_AI_CONFIGS: Record<LLMModelType, AIModelConfig> = {
  [LLMModelType.GPT4]: {
    modelType: LLMModelType.GPT4,
    baseUrl: 'https://api.openai.com/v1',
    maxTokens: 4096,
    temperature: 0.7,
    topP: 1.0,
    frequencyPenalty: 0,
    presencePenalty: 0,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.GPT4_TURBO]: {
    modelType: LLMModelType.GPT4_TURBO,
    baseUrl: 'https://api.openai.com/v1',
    maxTokens: 4096,
    temperature: 0.7,
    topP: 1.0,
    frequencyPenalty: 0,
    presencePenalty: 0,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.GPT4O]: {
    modelType: LLMModelType.GPT4O,
    baseUrl: 'https://api.openai.com/v1',
    maxTokens: 4096,
    temperature: 0.7,
    topP: 1.0,
    frequencyPenalty: 0,
    presencePenalty: 0,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.CLAUDE_3_OPUS]: {
    modelType: LLMModelType.CLAUDE_3_OPUS,
    baseUrl: 'https://api.anthropic.com',
    maxTokens: 4096,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.CLAUDE_3_SONNET]: {
    modelType: LLMModelType.CLAUDE_3_SONNET,
    baseUrl: 'https://api.anthropic.com',
    maxTokens: 4096,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.CLAUDE_3_HAIKU]: {
    modelType: LLMModelType.CLAUDE_3_HAIKU,
    baseUrl: 'https://api.anthropic.com',
    maxTokens: 4096,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.GEMINI_PRO]: {
    modelType: LLMModelType.GEMINI_PRO,
    baseUrl: 'https://generativelanguage.googleapis.com',
    maxTokens: 2048,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.GEMINI_ULTRA]: {
    modelType: LLMModelType.GEMINI_ULTRA,
    baseUrl: 'https://generativelanguage.googleapis.com',
    maxTokens: 2048,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 3
  },
  [LLMModelType.LLAMA_3_70B]: {
    modelType: LLMModelType.LLAMA_3_70B,
    baseUrl: 'http://localhost:11434',
    maxTokens: 2048,
    temperature: 0.7,
    timeout: 60000,
    retryAttempts: 2
  },
  [LLMModelType.LLAMA_3_8B]: {
    modelType: LLMModelType.LLAMA_3_8B,
    baseUrl: 'http://localhost:11434',
    maxTokens: 2048,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 2
  },
  [LLMModelType.QWEN_72B]: {
    modelType: LLMModelType.QWEN_72B,
    baseUrl: 'http://localhost:11434',
    maxTokens: 2048,
    temperature: 0.7,
    timeout: 60000,
    retryAttempts: 2
  },
  [LLMModelType.BAICHUAN_13B]: {
    modelType: LLMModelType.BAICHUAN_13B,
    baseUrl: 'http://localhost:11434',
    maxTokens: 2048,
    temperature: 0.7,
    timeout: 30000,
    retryAttempts: 2
  }
};

// 健康分析专用配置
export const HEALTH_ANALYSIS_CONFIG: Partial<AIModelConfig> = {
  temperature: 0.3, // 更低的温度以获得更一致的医疗建议
  maxTokens: 2000,
  timeout: 45000
};

// 中医诊断专用配置
export const TCM_DIAGNOSIS_CONFIG: Partial<AIModelConfig> = {
  temperature: 0.2, // 非常低的温度以确保诊断的一致性
  maxTokens: 3000,
  timeout: 60000
};

// 推荐的模型优先级（按性能和可靠性排序）
export const MODEL_PRIORITY: LLMModelType[] = [
  LLMModelType.GPT4O,
  LLMModelType.CLAUDE_3_SONNET,
  LLMModelType.GPT4_TURBO,
  LLMModelType.CLAUDE_3_OPUS,
  LLMModelType.GEMINI_PRO,
  LLMModelType.GPT4,
  LLMModelType.CLAUDE_3_HAIKU,
  LLMModelType.LLAMA_3_70B,
  LLMModelType.QWEN_72B,
  LLMModelType.LLAMA_3_8B,
  LLMModelType.BAICHUAN_13B,
  LLMModelType.GEMINI_ULTRA
];

// 任务特定的模型推荐
export const TASK_MODEL_RECOMMENDATIONS = {
  [AITaskType.HEALTH_ANALYSIS]: [
    LLMModelType.GPT4O,
    LLMModelType.CLAUDE_3_OPUS,
    LLMModelType.GPT4_TURBO
  ],
  [AITaskType.TCM_DIAGNOSIS]: [
    LLMModelType.GPT4O,
    LLMModelType.CLAUDE_3_SONNET,
    LLMModelType.QWEN_72B
  ],
  [AITaskType.TEXT_GENERATION]: [
    LLMModelType.GPT4O,
    LLMModelType.CLAUDE_3_SONNET,
    LLMModelType.GPT4_TURBO
  ],
  [AITaskType.QUESTION_ANSWERING]: [
    LLMModelType.GPT4O,
    LLMModelType.CLAUDE_3_SONNET,
    LLMModelType.GEMINI_PRO
  ],
  [AITaskType.SUMMARIZATION]: [
    LLMModelType.CLAUDE_3_SONNET,
    LLMModelType.GPT4O,
    LLMModelType.GPT4_TURBO
  ],
  [AITaskType.TRANSLATION]: [
    LLMModelType.GPT4O,
    LLMModelType.GEMINI_PRO,
    LLMModelType.CLAUDE_3_SONNET
  ]
};

// AI服务配置
export const AI_SERVICE_CONFIG = {
  // 缓存配置
  cache: {
    enabled: true,
    maxSize: 1000,
    ttl: 3600000 // 1小时
  },
  
  // 性能监控配置
  monitoring: {
    enabled: true,
    logLevel: 'info' as const,
    metricsInterval: 60000 // 1分钟
  },
  
  // 错误处理配置
  errorHandling: {
    maxRetries: 3,
    retryDelay: 1000,
    exponentialBackoff: true
  },
  
  // 并发控制
  concurrency: {
    maxConcurrentRequests: 10,
    queueTimeout: 30000
  }
};

// 获取模型配置
export function getModelConfig(modelType: LLMModelType): AIModelConfig {
  return { ...DEFAULT_AI_CONFIGS[modelType] };
}

// 获取任务推荐模型
export function getRecommendedModels(taskType: AITaskType): LLMModelType[] {
  return TASK_MODEL_RECOMMENDATIONS[taskType] || MODEL_PRIORITY.slice(0, 3);
}

// 合并配置
export function mergeConfig(
  base: AIModelConfig, 
  override: Partial<AIModelConfig>
): AIModelConfig {
  return { ...base, ...override };
} 