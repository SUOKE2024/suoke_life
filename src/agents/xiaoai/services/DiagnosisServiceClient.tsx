import {import React from "react";
  DiagnosisServiceClient,
  InquiryServiceClient,
  LookServiceClient,
  ListenServiceClient,
  PalpationServiceClient,
  ImageData,
  AudioData,
  PalpationData,
  InquiryResult,
  LookResult,
  ListenResult,
  PalpationResult;
} from "../types";
// API配置
const API_CONFIG = {
  inquiry: {,
  baseUrl: "http://localhost:8001",
    timeout: 30000,
    retries: 3;
  },
  look: {,
  baseUrl: "http://localhost:8080",
    timeout: 30000,
    retries: 3;
  },listen: {
      baseUrl: "http://localhost:8000",
      timeout: 30000,retries: 3;
  },palpation: {
      baseUrl: "http://localhost:8002",
      timeout: 30000,retries: 3;
  },calculation: {
      baseUrl: "http://localhost:8003",
      timeout: 30000,retries: 3;
  };
};
// 错误类型定义
export class DiagnosisApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public service?: string,
    public retryable: boolean = false;
  ) {
    super(message);
    this.name = 'DiagnosisApiError';
  }
}
// 缓存管理器
class CacheManager {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  set(key: string, data: any, ttl: number = 300000): void { // 默认5分钟TTL;
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl;
    });
  }
  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }
    return item.data;
  }
  clear(): void {
    this.cache.clear();
  }
}
const cacheManager = new CacheManager();
// 增强的API请求函数
async function apiRequest<T>(
  url: string,
  options: RequestInit = {},
  timeout: number = 30000,
  retries: number = 3,
  service: string = 'unknown'
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout() => controller.abort(), timeout);
  let lastError: Error;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, {...options,signal: controller.signal,headers: {"Content-Type": "application/json",X-Request-ID": `${service}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,...options.headers;
        };
      });
      clearTimeout(timeoutId);
      if (!response.ok) {
        const errorText = await response.text();
        const isRetryable = response.status >= 500 || response.status === 429;
        throw new DiagnosisApiError(;
          `HTTP ${response.status}: ${errorText || response.statusText}`,response.status,service,isRetryable;
        );
      }
      const data = await response.json();
      return data;
    } catch (error) {
      lastError = error as Error;
      clearTimeout(timeoutId);
      // 如果是最后一次尝试或错误不可重试，直接抛出
      if (attempt === retries || (error instanceof DiagnosisApiError && !error.retryable)) {
        throw error;
      }
      // 等待后重试，使用指数退避
      const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw lastError!;
}
// 数据验证器
class DataValidator {
  static validateImageData(data: ImageData): void {
    if (!data.data || data.data.byteLength === 0) {
      throw new Error("图像数据不能为空");
    }
    if (!data.format || !["jpeg",jpg', "png",webp'].includes(data.format.toLowerCase())) {
      throw new Error("不支持的图像格式");
    }
    if (data.width <= 0 || data.height <= 0) {
      throw new Error("图像尺寸无效");
    }
  }
  static validateAudioData(data: AudioData): void {
    if (!data.data || data.data.byteLength === 0) {
      throw new Error("音频数据不能为空");
    }
    if (!data.format || !["wav",mp3', "aac",flac'].includes(data.format.toLowerCase())) {
      throw new Error("不支持的音频格式");
    }
    if (data.duration <= 0) {
      throw new Error("音频时长无效");
    }
  }
  static validatePalpationData(data: PalpationData): void {
    if (!data.type || !["pulse",touch', 'pressure'].includes(data.type)) {
      throw new Error("无效的切诊类型");
    }
    if (!data.sensorData || Object.keys(data.sensorData).length === 0) {
      throw new Error("传感器数据不能为空");
    }
  }
}
// 问诊服务客户端实现
export class InquiryServiceClientImpl implements InquiryServiceClient {
  private baseUrl: string;
  private timeout: number;
  private retries: number;
  constructor() {
    this.baseUrl = API_CONFIG.inquiry.baseUrl;
    this.timeout = API_CONFIG.inquiry.timeout;
    this.retries = API_CONFIG.inquiry.retries;
  }
  async startSession(userId: string): Promise<string> {
    const cacheKey = `inquiry_session_${userId}`;
    const cached = cacheManager.get(cacheKey);
    if (cached) return cached;
    const url = `${this.baseUrl}/api/v1/inquiry/session/start`;
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({user_id: userId,session_type: "comprehensive",language: "zh-CN";
        });
      },
      this.timeout,
      this.retries,
      'inquiry';
    );
    const sessionId = response.session_id;
    cacheManager.set(cacheKey, sessionId, 1800000); // 30分钟缓存
    return sessionId;
  }
  async askQuestion(sessionId: string, question: string): Promise<InquiryResult> {
    const url = `${this.baseUrl}/api/v1/inquiry/interact`;
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({session_id: sessionId,user_input: question,interaction_type: "question";
        });
      },
      this.timeout,
      this.retries,
      'inquiry';
    );
    return {sessionId: response.session_id,response: response.ai_response || "感谢您的回答，让我继续了解您的情况。",extractedSymptoms: response.extracted_symptoms || [],confidence: response.confidence || 0.8,nextQuestions: response.suggested_questions || [],isComplete: response.is_complete || false;
    };
  }
  async getSymptomAnalysis(sessionId: string): Promise<any> {
    const url = `${this.baseUrl}/api/v1/inquiry/analysis`;
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({session_id: sessionId,analysis_type: "comprehensive";
        });
      },
      this.timeout,
      this.retries,
      'inquiry';
    );
    return {symptoms: response.symptoms || [],syndromes: response.syndromes || [],recommendations: response.recommendations || [],confidence: response.confidence || 0.8;
    };
  }
}
// 望诊服务客户端实现
export class LookServiceClientImpl implements LookServiceClient {
  private baseUrl: string;
  private timeout: number;
  private retries: number;
  constructor() {
    this.baseUrl = API_CONFIG.look.baseUrl;
    this.timeout = API_CONFIG.look.timeout;
    this.retries = API_CONFIG.look.retries;
  }
  async analyzeFace(imageData: ImageData): Promise<LookResult> {
    DataValidator.validateImageData(imageData);
    const url = `${this.baseUrl}/api/v1/look/face`;
        // 转换图像数据为base64;
    const uint8Array = new Uint8Array(imageData.data);
    const base64Data = btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({image_data: base64Data,image_format: imageData.format,analysis_type: "comprehensive",metadata: {width: imageData.width,height: imageData.height,timestamp: Date.now();
          }
        })
      },
      this.timeout,
      this.retries,
      'look';
    );
    return {analysisId: response.analysis_id,faceFeatures: response.face_features || {},complexionAnalysis: response.complexion_analysis || {},tongueAnalysis: response.tongue_analysis || {},overallAssessment: response.overall_assessment || "面部分析完成",confidence: response.confidence || 0.8,recommendations: response.recommendations || [];
    };
  }
  async analyzeTongue(imageData: ImageData): Promise<LookResult> {
    DataValidator.validateImageData(imageData);
        const url = `${this.baseUrl}/api/v1/look/tongue`;
    const uint8Array = new Uint8Array(imageData.data);
    const base64Data = btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({image_data: base64Data,image_format: imageData.format,analysis_type: "tongue_diagnosis";
        });
      },
      this.timeout,
      this.retries,
      'look';
    );
    return {analysisId: response.analysis_id,tongueAnalysis: response.tongue_analysis || {},overallAssessment: response.overall_assessment || "舌诊分析完成",confidence: response.confidence || 0.8;
    };
  }
}
// 闻诊服务客户端实现
export class ListenServiceClientImpl implements ListenServiceClient {
  private baseUrl: string;
  private timeout: number;
  private retries: number;
  constructor() {
    this.baseUrl = API_CONFIG.listen.baseUrl;
    this.timeout = API_CONFIG.listen.timeout;
    this.retries = API_CONFIG.listen.retries;
  }
  async analyzeVoice(audioData: AudioData): Promise<ListenResult> {
    DataValidator.validateAudioData(audioData);
        const url = `${this.baseUrl}/api/v1/listen/voice`;
    const uint8Array = new Uint8Array(audioData.data);
    const base64Data = btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({audio_data: base64Data,audio_format: audioData.format,duration: audioData.duration,sample_rate: audioData.sampleRate,analysis_type: "comprehensive";
        });
      },
      this.timeout,
      this.retries,
      'listen';
    );
    return {analysisId: response.analysis_id,voiceFeatures: response.voice_features || {},breathingPattern: response.breathing_pattern || {},overallAssessment: response.overall_assessment || "语音分析完成",confidence: response.confidence || 0.8;
    };
  }
  async analyzeBreathing(audioData: AudioData): Promise<ListenResult> {
    DataValidator.validateAudioData(audioData);
    const url = `${this.baseUrl}/api/v1/listen/breath`;
    const base64Data = btoa(String.fromCharCode(...new Uint8Array(audioData.data)));
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({audio_data: base64Data,audio_format: audioData.format,analysis_type: "breathing_pattern";
        });
      },
      this.timeout,
      this.retries,
      'listen';
    );
    return {analysisId: response.analysis_id,breathingPattern: response.breathing_analysis || {},overallAssessment: response.overall_assessment || "呼吸音分析完成",confidence: response.confidence || 0.8;
    };
  }
}
// 切诊服务客户端实现
export class PalpationServiceClientImpl implements PalpationServiceClient {
  private baseUrl: string;
  private timeout: number;
  private retries: number;
  constructor() {
    this.baseUrl = API_CONFIG.palpation.baseUrl;
    this.timeout = API_CONFIG.palpation.timeout;
    this.retries = API_CONFIG.palpation.retries;
  }
  async analyzePalpation(data: PalpationData): Promise<PalpationResult> {
    DataValidator.validatePalpationData(data);
    const url = `${this.baseUrl}/api/v1/palpation/analyze`;
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({palpation_type: data.type,sensor_data: data.sensorData,user_id: "current_user",metadata: data.metadata || {};
        });
      },
      this.timeout,
      this.retries,
      'palpation';
    );
    return {analysisId: response.analysis_id,pulseAnalysis: response.pulse_analysis || {},abdominalAnalysis: response.abdominal_analysis || {},skinAnalysis: response.skin_analysis || {},overallAssessment: response.overall_assessment || "切诊分析完成",confidence: response.confidence || 0.8;
    };
  }
  async startRealTimeMonitoring(userId: string): Promise<string> {
    const url = `${this.baseUrl}/api/v1/palpation/monitor/start`;
    const response = await apiRequest<any>(;
      url,{
      method: "POST",
      body: JSON.stringify({user_id: userId,monitoring_type: "real_time";
        });
      },
      this.timeout,
      this.retries,
      'palpation';
    );
    return response.session_id;
  }
}
// 主要的诊断服务客户端
export class DiagnosisServiceClientImpl implements DiagnosisServiceClient {
  public inquiry: InquiryServiceClient;
  public look: LookServiceClient;
  public listen: ListenServiceClient;
  public palpation: PalpationServiceClient;
  constructor() {
    this.inquiry = new InquiryServiceClientImpl();
    this.look = new LookServiceClientImpl();
    this.listen = new ListenServiceClientImpl();
    this.palpation = new PalpationServiceClientImpl();
  }
  // 健康检查
  async healthCheck(): Promise<{ [key: string]: boolean }> {
    const services = ["inquiry",look", "listen",palpation"];
    const results: { [key: string]: boolean } = {};
    const healthChecks = services.map(async (service) => {try {const config = API_CONFIG[service as keyof typeof API_CONFIG];
        const controller = new AbortController();
        const timeoutId = setTimeout() => controller.abort(), 5000);
        const response = await fetch(`${config.baseUrl}/health`, {
      method: "GET",
      signal: controller.signal,headers: {"Content-Type": "application/json";
          };
        });
        clearTimeout(timeoutId);
        results[service] = response.ok;
      } catch (error) {
        results[service] = false;
      }
    });
    await Promise.allSettled(healthChecks);
    return results;
  }
  // 综合诊断
  async comprehensiveDiagnosis(data: {,
  userId: string;
    imageData?: ImageData;
    audioData?: AudioData;
    palpationData?: PalpationData;
    symptoms?: string[];
  }): Promise<any> {
    const results: any = {};
    try {
      // 并行执行各项诊断
      const promises: Promise<any>[] = [];
      if (data.imageData) {
        promises.push(
          this.look.analyzeFace(data.imageData).then(result => {
            results.look = result;
          });
        );
      }
      if (data.audioData) {
        promises.push(
          this.listen.analyzeVoice(data.audioData).then(result => {
            results.listen = result;
          });
        );
      }
      if (data.palpationData) {
        promises.push(
          this.palpation.analyzePalpation(data.palpationData).then(result => {
            results.palpation = result;
          });
        );
      }
      if (data.symptoms && data.symptoms.length > 0) {
        promises.push(
          this.inquiry.startSession(data.userId).then(async sessionId => {
            // 模拟问诊过程
            for (const symptom of data.symptoms) {
              await this.inquiry.askQuestion(sessionId, symptom);
            }
            const analysis = await this.inquiry.getSymptomAnalysis(sessionId);
            results.inquiry = analysis;
          })
        );
      }
      await Promise.allSettled(promises);
      // 调用算诊服务进行综合分析
      const calculationUrl = `${API_CONFIG.calculation.baseUrl}/api/v1/calculation/comprehensive`;
      const comprehensiveResult = await apiRequest<any>(;
        calculationUrl,{
      method: "POST",
      body: JSON.stringify({user_id: data.userId,diagnosis_results: results,timestamp: Date.now();
          })
        },
        API_CONFIG.calculation.timeout,
        API_CONFIG.calculation.retries,
        'calculation';
      );
      return {...results,comprehensive: comprehensiveResult,timestamp: Date.now(),confidence: this.calculateOverallConfidence(results);
      };
    } catch (error) {
      throw new DiagnosisApiError(;
        `综合诊断失败: ${error instanceof Error ? error.message : '未知错误'}`,undefined,'comprehensive',true;
      );
    }
  }
  private calculateOverallConfidence(results: any): number {
    const confidences: number[] = [];
    Object.values(results).forEach(result: any) => {
      if (result && typeof result.confidence === 'number') {
        confidences.push(result.confidence);
      }
    });
    if (confidences.length === 0) return 0.5;
    return confidences.reduce(sum, conf) => sum + conf, 0) / confidences.length;
  }
  // 清理缓存
  clearCache(): void {
    cacheManager.clear();
  }
}
// 导出单例实例
export const diagnosisServiceClient = new DiagnosisServiceClientImpl();