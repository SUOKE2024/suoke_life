import { apiClient } from './apiClient';
import { EventEmitter } from '../utils/eventEmitter';
import { RAG_CONFIG, getCurrentEnvConfig } from '../constants/config';
// RAG查询请求接口
export interface RAGQueryRequest {
  query: string;
  userId: string;
  sessionId?: string;
  context?: Record<string, any>;
  taskType?: 'consultation' | 'diagnosis' | 'treatment' | 'prevention';
  urgency?: 'low' | 'medium' | 'high' | 'urgent';
  complexity?: 'simple' | 'moderate' | 'complex' | 'expert';
  preferredAgent?: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  multimodalData?: Array<{
    type: 'image' | 'audio' | 'video' | 'sensor';
  data: string | ArrayBuffer;
    metadata?: Record<string, any>;
}>;
  maxTokens?: number;
  temperature?: number;
  stream?: boolean;
}
// RAG查询响应接口
export interface RAGQueryResponse {
  requestId: string;
  answer: string;
  sources: Array<{;
  id: string;
    title: string;
  source: string;
    url?: string;
    snippet: string;
  score: number;
}>;
  confidence: number,
  reasoningChain: string[];
  agentInfo: {,
  agentName: string;
    agentType: string,
  processingTime: number;
  };
  processingTime: number,
  followUpQuestions: string[];
  metadata: Record<string, any>;
}
// 流式响应接口
export interface StreamResponse {
  requestId: string;
  answerFragment: string;
  isFinal: boolean;
  sources?: Array<{
    id: string;
  title: string;
    source: string;
  snippet: string;
}>;
}
// 中医分析请求接口
export interface TCMAnalysisRequest {
  symptoms: string[];
  userId: string;
  constitutionType?:
    | 'qi_deficiency'
    | 'yang_deficiency'
    | 'yin_deficiency'
    | 'phlegm_dampness'
    | 'damp_heat'
    | 'blood_stasis'
    | 'qi_stagnation'
    | 'special_constitution'
    | 'balanced';
  medicalHistory?: string[];
  currentMedications?: string[];
  lifestyleFactors?: {
    diet?: string;
    exercise?: string;
    sleep?: string;
    stress?: string;
    environment?: string;
};
  tongueImage?: string; // base64编码的舌象图片
  pulseData?: number[]; // 脉象数据
}
// 中医分析响应接口
export interface TCMAnalysisResponse {
  requestId: string;
  syndromeAnalysis: {;
    primarySyndrome: string;
  secondarySyndromes: string[];
    confidence: number;
  reasoning: string[];
};
  constitutionAssessment: {,
  constitutionType: string;
    score: number,
  characteristics: string[];
    recommendations: string[];
  };
  treatmentPrinciples: string[],
  lifestyleRecommendations: string[];
  reasoningChain: string[],
  confidence: number;
}
// 中药推荐请求接口
export interface HerbRecommendationRequest {
  syndromeType: string;
  constitutionType: string;
  userId: string;
  contraindications?: string[];
  allergies?: string[];
  age?: number;
  gender?: 'male' | 'female';
  pregnancyStatus?: boolean;
  currentSymptoms?: string[];
}
// 中药推荐响应接口
export interface HerbRecommendationResponse {
  requestId: string;
  recommendedFormulas: Array<{;
    name: string;
  composition: Array<{;
      herb: string;
  dosage: string;
      function: string;
}>;
    preparation: string,
  dosage: string;
    duration: string,
  confidence: number;
  }>;
  singleHerbs: Array<{,
  name: string;
    function: string,
  dosage: string;
    precautions: string[];
  }>;
  safetyWarnings: string[],
  usageInstructions: {
    preparation: string,
  administration: string;
    timing: string,
  duration: string;
  };
  contraindications: string[],
  monitoringAdvice: string[];
}
// 文档索引请求接口
export interface DocumentIndexRequest {
  content: string;
  title: string;
  source: string;
  metadata?: Record<string, any>;
  documentType?: string;
  collectionName?: string;
}
// RAG服务类
export class RAGService extends EventEmitter {
  private isInitialized: boolean = false;
  private queryCache: Map<string, RAGQueryResponse> = new Map();
  private performanceMetrics: Map<string, number> = new Map();
  private errorCount: number = 0;
  private lastErrorTime: number = 0;
  private config = RAG_CONFIG;
  constructor() {
    super();
    this.initialize();
  }
  // 初始化服务
  async initialize(): Promise<void> {
    if (this.isInitialized) return;
    try {
      // 检查RAG服务健康状态
      await this.checkHealth();
      this.isInitialized = true;
      this.emit('initialized');
    } catch (error) {
      this.emit('error', error);
      throw new Error(`RAG服务初始化失败: ${error}`);
    }
  }
  // 检查服务健康状态
  async checkHealth(): Promise<boolean> {
    try {
      const envConfig = getCurrentEnvConfig();
      const healthUrl = `${envConfig.RAG_SERVICE_URL}/health`;
      const controller = new AbortController();
      const timeoutId = setTimeout() => controller.abort(), this.config.PERFORMANCE.TIMEOUT);
      const response = await fetch(healthUrl, {
      method: "GET",
      signal: controller.signal;
      });
      clearTimeout(timeoutId);
      const data = await response.json();
      return data?.status === 'healthy';
    } catch (error) {
      this.recordError(error);
      throw new Error(`RAG服务健康检查失败: ${error}`);
    }
  }
  // 记录错误
  private recordError(error: any): void {
    this.errorCount++;
    this.lastErrorTime = Date.now();
    this.emit('error', {
      error,
      errorCount: this.errorCount,
      timestamp: this.lastErrorTime;
    });
  }
  // 记录性能指标
  private recordPerformance(operation: string, duration: number): void {
    this.performanceMetrics.set(operation, duration);
    this.emit('performance', {
      operation,
      duration,
      timestamp: Date.now();
    });
  }
  // 基础RAG查询
  async query(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    const startTime = Date.now();
    const cacheKey = this.generateCacheKey(request);
    // 检查缓存
    if (this.queryCache.has(cacheKey)) {
      const cachedResult = this.queryCache.get(cacheKey)!;
      this.recordPerformance('query_cache_hit', Date.now() - startTime);
      this.emit('cache_hit', { cacheKey, result: cachedResult });
      return cachedResult;
    }
    try {
      const envConfig = getCurrentEnvConfig();
      const queryUrl = `${envConfig.RAG_SERVICE_URL}${this.config.ENDPOINTS.QUERY}`;
      const controller = new AbortController();
      const timeoutId = setTimeout() => controller.abort(), this.config.PERFORMANCE.TIMEOUT);
      const response = await fetch(queryUrl, {
      method: "POST",
      headers: {'Content-Type': 'application/json';
        },body: JSON.stringify(request),signal: controller.signal;
      });
      clearTimeout(timeoutId);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result: RAGQueryResponse = await response.json();
      // 缓存结果
      this.queryCache.set(cacheKey, result);
      // 记录性能
      this.recordPerformance('query', Date.now() - startTime);
      this.emit('query_completed', { request, result });
      return result;
    } catch (error) {
      this.recordError(error);
      throw error;
    }
  }
  // 多模态查询
  async multimodalQuery(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    const startTime = Date.now();
    try {
      const envConfig = getCurrentEnvConfig();
      const queryUrl = `${envConfig.RAG_SERVICE_URL}${this.config.ENDPOINTS.MULTIMODAL_QUERY}`;
      const controller = new AbortController();
      const timeoutId = setTimeout() => controller.abort(), this.config.PERFORMANCE.TIMEOUT);
      const response = await fetch(queryUrl, {
      method: "POST",
      headers: {'Content-Type': 'application/json';
        },body: JSON.stringify(request),signal: controller.signal;
      });
      clearTimeout(timeoutId);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result: RAGQueryResponse = await response.json();
      // 记录性能
      this.recordPerformance('multimodal_query', Date.now() - startTime);
      this.emit('multimodal_query_completed', { request, result });
      return result;
    } catch (error) {
      this.recordError(error);
      throw error;
    }
  }
  // 流式RAG查询
  async streamQuery(
    request: RAGQueryRequest,
    onChunk: (chunk: StreamResponse) => void;
  ): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    const requestId = this.generateRequestId();
    try {
      this.emit('streamStart', { requestId, request });
      // 使用fetch进行流式请求
      const response = await fetch('/rag/query/stream', {
      method: "POST",
      headers: {'Content-Type': 'application/json';
        },body: JSON.stringify({ ...request, requestId });
      });
      if (!response.body) {
        throw new Error('流式响应不支持');
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          this.emit('streamComplete', requestId);
          break;
        }
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamResponse;
              onChunk(data);
              if (data.isFinal) {
                return;
              }
            } catch (parseError) {
              console.warn('解析流式数据失败:', parseError);
            }
          }
        }
      }
    } catch (error) {
      this.emit('streamError', { requestId, error });
      throw error;
    }
  }
  // 中医证候分析
  async analyzeTCM(request: TCMAnalysisRequest): Promise<TCMAnalysisResponse> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    try {
      this.emit('tcmAnalysisStart', request);
      const response = await apiClient.post('/rag/tcm/analysis', request);
      if (!response.data) {
        throw new Error('中医分析失败：无响应数据');
      }
      const result = response.data as TCMAnalysisResponse;
      this.emit('tcmAnalysisComplete', { request, result });
      return result;
    } catch (error) {
      this.emit('tcmAnalysisError', { request, error });
      throw error;
    }
  }
  // 中药推荐
  async recommendHerbs(request: HerbRecommendationRequest): Promise<HerbRecommendationResponse> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    try {
      this.emit('herbRecommendationStart', request);
      const response = await apiClient.post('/rag/tcm/herbs', request);
      if (!response.data) {
        throw new Error('中药推荐失败：无响应数据');
      }
      const result = response.data as HerbRecommendationResponse;
      this.emit('herbRecommendationComplete', { request, result });
      return result;
    } catch (error) {
      this.emit('herbRecommendationError', { request, error });
      throw error;
    }
  }
  // 文档索引
  async indexDocument(
    request: DocumentIndexRequest;
  ): Promise<{ documentId: string; success: boolean }> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    try {
      const response = await apiClient.post('/rag/documents/index', request);
      if (!response.data) {
        throw new Error('文档索引失败：无响应数据');
      }
      return response.data as { documentId: string; success: boolean };
    } catch (error) {
      throw error;
    }
  }
  // 搜索文档
  async searchDocuments(
    query: string,
    options: {
      limit?: number;
      threshold?: number;
      documentType?: string;
      collectionName?: string;
    } = {}
  ): Promise<
    Array<{
      id: string,
  title: string;
      content: string,
  score: number;
      metadata: Record<string, any>;
    }>
  > {
    if (!this.isInitialized) {
      await this.initialize();
    }
    try {
      const params = new URLSearchParams({query,limit: options.limit?.toString() || '10',threshold: options.threshold?.toString() || '0.7',...(options.documentType && { documentType: options.documentType }),...(options.collectionName && { collectionName: options.collectionName });
      });
      const response = await apiClient.get(`/rag/documents/search?${params}`);
      if (!response.data) {
        throw new Error('文档搜索失败：无响应数据');
      }
      return response.data as Array<{id: string,
  title: string;
        content: string,
  score: number;
        metadata: Record<string, any>;
      }>;
    } catch (error) {
      throw error;
    }
  }
  // 清除查询缓存
  clearCache(): void {
    this.queryCache.clear();
    this.emit('cacheCleared');
  }
  // 获取缓存统计
  getCacheStats(): { size: number; keys: string[] } {
    return {size: this.queryCache.size,keys: Array.from(this.queryCache.keys());
    };
  }
  // 生成缓存键
  private generateCacheKey(request: RAGQueryRequest): string {
    const key = {query: request.query,userId: request.userId,taskType: request.taskType,context: request.context;
    };
    return btoa(JSON.stringify(key));
  }
  // 生成请求ID;
  private generateRequestId(): string {
    return `rag_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  // 获取性能指标
  getPerformanceMetrics(): Map<string, number> {
    return new Map(this.performanceMetrics);
  }
  // 健康检查增强
  async performHealthCheck(): Promise<{
    isHealthy: boolean,
  services: {
      rag: boolean,
  tcm: boolean;
    };
    latency: number,
  timestamp: number;
  }> {
    const startTime = Date.now();
    try {
      const envConfig = getCurrentEnvConfig();
      // 并行检查RAG和TCM服务
      const [ragHealth, tcmHealth] = await Promise.allSettled([;
        this.checkServiceHealth(envConfig.RAG_SERVICE_URL),this.checkServiceHealth(envConfig.TCM_SERVICE_URL);
      ]);
      const latency = Date.now() - startTime;
      const result = {isHealthy: ragHealth.status === 'fulfilled' && tcmHealth.status === 'fulfilled',services: {rag: ragHealth.status === 'fulfilled',tcm: tcmHealth.status === 'fulfilled';
        },latency,timestamp: Date.now();
      };
      this.emit('health_check_completed', result);
      return result;
    } catch (error) {
      this.recordError(error);
      return {isHealthy: false,services: { rag: false, tcm: false },latency: Date.now() - startTime,timestamp: Date.now();
      };
    }
  }
  // 检查单个服务健康状态
  private async checkServiceHealth(serviceUrl: string): Promise<boolean> {
    const controller = new AbortController();
    const timeoutId = setTimeout() => controller.abort(), 5000); // 5秒超时
    try {
      const response = await fetch(`${serviceUrl}/health`, {
      method: "GET",
      signal: controller.signal;
      });
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }
  // 智能重试机制
  async queryWithRetry(
    request: RAGQueryRequest,
    maxRetries: number = 3;
  ): Promise<RAGQueryResponse> {
    let lastError: Error | null = null;
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const result = await this.query(request);
        // 成功时重置错误计数
        this.errorCount = 0;
        return result;
      } catch (error) {
        lastError = error as Error;
        // 如果不是最后一次尝试，等待后重试
        if (attempt < maxRetries) {
          const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000); // 指数退避，最大5秒
          await new Promise(resolve => setTimeout(resolve, delay));
          this.emit('retry_attempt', { attempt, maxRetries, delay, error });
        }
      }
    }
    throw lastError || new Error('查询失败，已达到最大重试次数');
  }
  // 批量查询
  async batchQuery(requests: RAGQueryRequest[]): Promise<RAGQueryResponse[]> {
    const startTime = Date.now();
    try {
      const results = await Promise.allSettled(requests.map(request => this.query(request)));
      const responses: RAGQueryResponse[] = [];
      const errors: Error[] = [];
      results.forEach(result, index) => {
        if (result.status === 'fulfilled') {
          responses.push(result.value);
        } else {
          errors.push(new Error(`批量查询第${index + 1}项失败: ${result.reason}`));
        }
      });
      this.recordPerformance('batch_query', Date.now() - startTime);
      this.emit('batch_query_completed', {
        total: requests.length,
        successful: responses.length,
        failed: errors.length,
        responses,
        errors;
      });
      return responses;
    } catch (error) {
      this.recordError(error);
      throw error;
    }
  }
  // 预热缓存
  async warmupCache(commonQueries: string[]): Promise<void> {
    const startTime = Date.now();
    try {
      const warmupRequests = commonQueries.map(query => ({query,userId: 'system',taskType: 'consultation' as const,context: { warmup: true };
      }));
      await this.batchQuery(warmupRequests);
      this.recordPerformance('cache_warmup', Date.now() - startTime);
      this.emit('cache_warmed_up', { queries: commonQueries.length });
    } catch (error) {
      this.recordError(error);
      throw new Error(`缓存预热失败: ${error}`);
    }
  }
  // 清理资源
  async cleanup(): Promise<void> {
    // 清除缓存
    this.queryCache.clear();
    this.isInitialized = false;
    this.emit('cleanup');
  }
}
// 创建RAG服务实例
export const ragService = new RAGService();
// 导出类型已在上面定义，无需重复导出
