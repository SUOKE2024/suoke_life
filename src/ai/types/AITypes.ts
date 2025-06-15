/**
 * AI模块类型定义
 * 支持最新LLM模型和AI框架
 */

// LLM模型类型
export enum LLMModelType {
  GPT4 = 'gpt-4',
  GPT4_TURBO = 'gpt-4-turbo',
  GPT4O = 'gpt-4o',
  CLAUDE_3_OPUS = 'claude-3-opus',
  CLAUDE_3_SONNET = 'claude-3-sonnet',
  CLAUDE_3_HAIKU = 'claude-3-haiku',
  GEMINI_PRO = 'gemini-pro',
  GEMINI_ULTRA = 'gemini-ultra',
  LLAMA_3_70B = 'llama-3-70b',
  LLAMA_3_8B = 'llama-3-8b',
  QWEN_72B = 'qwen-72b',
  BAICHUAN_13B = 'baichuan-13b'
}

// AI任务类型
export enum AITaskType {
  TEXT_GENERATION = 'text_generation',
  TEXT_CLASSIFICATION = 'text_classification',
  QUESTION_ANSWERING = 'question_answering',
  SUMMARIZATION = 'summarization',
  TRANSLATION = 'translation',
  SENTIMENT_ANALYSIS = 'sentiment_analysis',
  NAMED_ENTITY_RECOGNITION = 'ner',
  IMAGE_CLASSIFICATION = 'image_classification',
  OBJECT_DETECTION = 'object_detection',
  SPEECH_TO_TEXT = 'speech_to_text',
  TEXT_TO_SPEECH = 'text_to_speech',
  TCM_DIAGNOSIS = 'tcm_diagnosis',
  HEALTH_ANALYSIS = 'health_analysis'
}

// AI模型配置
export interface AIModelConfig {
  modelType: LLMModelType;
  apiKey?: string;
  baseUrl?: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  timeout?: number;
  retryAttempts?: number;
}

// AI请求接口
export interface AIRequest {
  taskType: AITaskType;
  input: string | ArrayBuffer | File;
  modelConfig?: Partial<AIModelConfig>;
  context?: Record<string, any>;
  metadata?: Record<string, any>;
}

// AI响应接口
export interface AIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  metadata?: {
    modelUsed: LLMModelType;
    tokensUsed?: number;
    processingTime: number;
    confidence?: number;
  };
}

// 流式响应接口
export interface AIStreamResponse {
  chunk: string;
  isComplete: boolean;
  metadata?: Record<string, any>;
}

// AI服务接口
export interface IAIService {
  initialize(): Promise<void>;
  process(request: AIRequest): Promise<AIResponse>;
  processStream?(request: AIRequest): AsyncGenerator<AIStreamResponse>;
  dispose(): Promise<void>;
}

// 装饰器元数据
export interface AIDecoratorMetadata {
  modelType?: LLMModelType;
  taskType?: AITaskType;
  cacheEnabled?: boolean;
  retryAttempts?: number;
  timeout?: number;
}

// 健康分析特定类型
export interface HealthAnalysisRequest extends AIRequest {
  patientData: {
    age: number;
    gender: 'male' | 'female';
    symptoms: string[];
    vitalSigns?: Record<string, number>;
    medicalHistory?: string[];
  };
  analysisType: 'tcm' | 'western' | 'integrated';
}

export interface HealthAnalysisResponse extends AIResponse {
  data: {
    diagnosis: string;
    confidence: number;
    recommendations: string[];
    riskFactors: string[];
    followUpActions: string[];
    tcmAnalysis?: {
      syndrome: string;
      constitution: string;
      treatment: string;
    };
  };
} 