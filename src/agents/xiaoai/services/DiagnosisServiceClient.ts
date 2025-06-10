// 诊断服务客户端 - 整合四诊服务的统一客户端/;/g/;

// 基础类型定义/;,/g/;
interface ImageData {data: ArrayBuffer}format: string,;
width: number,;
}
}
  const height = number;}
}

interface AudioData {data: ArrayBuffer}format: string,;
const duration = number;
}
}
  sampleRate?: number;}
}

interface PalpationData {type: string}sensorData: Record<string, any>;
}
}
  const timestamp = number;}
}

interface InquiryResult {sessionId: string}response: string,;
extractedSymptoms: string[],;
confidence: number,;
nextQuestions: string[],;
}
}
  const isComplete = boolean;}
}

interface LookResult {analysis: string}features: Array<{type: string,;
description: string,;
}
}
    const confidence = number;}
  }>;
confidence: number,;
const recommendations = string[];
}

interface ListenResult {analysis: string}features: Array<{type: string,;
description: string,;
}
}
    const confidence = number;}
  }>;
confidence: number,;
const recommendations = string[];
}

interface PalpationResult {analysis: string}measurements: Record<string, any>;
confidence: number,;
}
}
  const recommendations = string[];}
}

// 服务接口定义/;,/g/;
interface InquiryServiceClient {startSession(userId: string): Promise<string>;,}askQuestion(sessionId: string, question: string): Promise<InquiryResult>;
}
}
  getSymptomAnalysis(sessionId: string): Promise<any>;}
}

interface LookServiceClient {analyzeFace(imageData: ImageData): Promise<LookResult>;}}
}
  analyzeTongue(imageData: ImageData): Promise<LookResult>;}
}

interface ListenServiceClient {analyzeVoice(audioData: AudioData): Promise<ListenResult>;}}
}
  analyzeBreathing(audioData: AudioData): Promise<ListenResult>;}
}

interface PalpationServiceClient {analyzePalpation(data: PalpationData): Promise<PalpationResult>;}}
}
  startRealTimeMonitoring(userId: string): Promise<string>;}
}

interface DiagnosisServiceClient {inquiry: InquiryServiceClient}look: LookServiceClient,;
listen: ListenServiceClient,;
}
}
  const palpation = PalpationServiceClient;}
  healthCheck(): Promise<{ [key: string]: boolean ;}>;
comprehensiveDiagnosis(data: any): Promise<any>;
clearCache(): void;
}

// API配置/;,/g/;
const  API_CONFIG = {inquiry: {baseUrl: 'http://localhost:8001';',''/;,'/g,'/;
  timeout: 30000,;
}
    const retries = 3;}
  },';,'';
look: {,';,}baseUrl: 'http://localhost:8080';',''/;,'/g,'/;
  timeout: 30000,;
}
    const retries = 3;}
  },';,'';
listen: {,';,}baseUrl: 'http://localhost:8000';',''/;,'/g,'/;
  timeout: 30000,;
}
    const retries = 3;}
  },';,'';
palpation: {,';,}baseUrl: 'http://localhost:8002';',''/;,'/g,'/;
  timeout: 30000,;
}
    const retries = 3;}
  },';,'';
calculation: {,';,}baseUrl: 'http://localhost:8003';',''/;,'/g,'/;
  timeout: 30000,;
}
    const retries = 3;}
  }
};

// 错误类型定义/;,/g/;
export class DiagnosisApiError extends Error {;,}constructor(message: string;,)const public = statusCode?: number;);
const public = service?: string;);
const public = retryable: boolean = false);
  ) {';,}super(message);';'';
}
    this.name = 'DiagnosisApiError';'}'';'';
  }
}

// 缓存管理器/;,/g/;
class CacheManager {private cache = new Map<;}}
}
    string,}
    { data: any; timestamp: number; ttl: number ;}
  >();
set(key: string, data: any, ttl: number = 300000): void {// 默认5分钟TTL,/;,}this.cache.set(key, {);,}data,);,/g/;
const timestamp = Date.now();
}
      ttl,}
    });
  }

  get(key: string): any | null {const item = this.cache.get(key);,}if (!item) return null;
if (Date.now() - item.timestamp > item.ttl) {this.cache.delete(key);}}
      return null;}
    }

    return item.data;
  }

  clear(): void {}}
    this.cache.clear();}
  }
}

const cacheManager = new CacheManager();

// 增强的API请求函数/;,/g,/;
  async: function apiRequest<T>(url: string,;,)options: RequestInit = {;}
timeout: number = 30000,)';,'';
retries: number = 3,)';,'';
service: string = 'unknown')';'';
): Promise<T> {const controller = new AbortController();,}timeoutId: setTimeout(() => controller.abort(), timeout);
const let = lastError: Error;
for (let attempt = 0; attempt <= retries; attempt++) {try {}      const: response = await fetch(url, {)        ...options}signal: controller.signal,)';,'';
const headers = {)';}}'';
          'Content-Type': 'application/json',')'}'/;'/g'/;
          'X-Request-ID': `${service;}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,````;```;
          ...options.headers,;
        }
      });
clearTimeout(timeoutId);
if (!response.ok) {const errorText = await response.text();}}
        const isRetryable = response.status >= 500 || response.status === 429;}
        throw: new DiagnosisApiError(`HTTP ${response.status}: ${errorText || response.statusText}`,````;,)response.status,);,```;
service,);
isRetryable);
        );
      }

      const data = await response.json();
return data;
    } catch (error) {lastError = error as Error;,}clearTimeout(timeoutId);

      // 如果是最后一次尝试或错误不可重试，直接抛出/;,/g/;
if (attempt === retries ||);
        (error instanceof DiagnosisApiError && !error.retryable);
      ) {}}
        const throw = error;}
      }

      // 等待后重试，使用指数退避/;,/g,/;
  delay: Math.min(1000 * Math.pow(2, attempt), 10000);
await: new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  const throw = lastError!;
}

// 数据验证器/;,/g/;
class DataValidator {static validateImageData(data: ImageData): void {}    if (!data.data || data.data.byteLength === 0) {}}
}
}
    ;}';,'';
if (!data.format ||)';'';
      !['jpeg', 'jpg', 'png', 'webp'].includes(data.format.toLowerCase())';'';
    ) {}}
}
    }
    if (data.width <= 0 || data.height <= 0) {}}
}
    }
  }

  static validateAudioData(data: AudioData): void {if (!data.data || data.data.byteLength === 0) {}}
}
    ;}';,'';
if (!data.format ||)';'';
      !['wav', 'mp3', 'aac', 'flac'].includes(data.format.toLowerCase())';'';
    ) {}}
}
    }
    if (data.duration <= 0) {}}
}
    }
  }
';,'';
static validatePalpationData(data: PalpationData): void {';,}if (!data.type || !['pulse', 'touch', 'pressure'].includes(data.type)) {';}}'';
}
    ;}
    if (!data.sensorData || Object.keys(data.sensorData).length === 0) {}}
}
    }
  }
}

// 问诊服务客户端实现/;,/g/;
export class InquiryServiceClientImpl implements InquiryServiceClient {;,}private baseUrl: string;
private timeout: number;
private retries: number;
constructor() {this.baseUrl = API_CONFIG.inquiry.baseUrl;,}this.timeout = API_CONFIG.inquiry.timeout;
}
    this.retries = API_CONFIG.inquiry.retries;}
  }

  const async = startSession(userId: string): Promise<string> {}
    const cacheKey = `inquiry_session_${userId;}`;````;,```;
const cached = cacheManager.get(cacheKey);
if (cached) return cached;
const url = `${this.baseUrl}/api/v1/inquiry/session/start`;```/`;,`/g,`/`;
  const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';
body: JSON.stringify({,';,)user_id: userId,')'';,}session_type: 'comprehensive';',)'';'';
}
          const language = 'zh-CN';')'}'';'';
        }),;
      }
this.timeout,';,'';
this.retries,';'';
      'inquiry'';'';
    );
const sessionId = response.session_id;
cacheManager.set(cacheKey, sessionId, 1800000); // 30分钟缓存/;,/g/;
return sessionId;
  }

  async: askQuestion(sessionId: string,);
const question = string);
  ): Promise<InquiryResult> {}
    const url = `${this.baseUrl;}/api/v1/inquiry/interact`;```/`;,`/g,`/`;
  const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';
body: JSON.stringify({,;,)session_id: sessionId,)';,}user_input: question,)';'';
}
          const interaction_type = 'question';')'}'';'';
        }),;
      }
this.timeout,';,'';
this.retries,';'';
      'inquiry'';'';
    );
return {sessionId: response.session_id}extractedSymptoms: response.extracted_symptoms || [],;
confidence: response.confidence || 0.8,;
nextQuestions: response.suggested_questions || [],;
}
      const isComplete = response.is_complete || false;}
    };
  }

  const async = getSymptomAnalysis(sessionId: string): Promise<any> {}
    const url = `${this.baseUrl;}/api/v1/inquiry/analysis`;```/`;,`/g,`/`;
  const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';
body: JSON.stringify({,)';,}session_id: sessionId,)';'';
}
          const analysis_type = 'comprehensive';')'}'';'';
        }),;
      }
this.timeout,';,'';
this.retries,';'';
      'inquiry'';'';
    );
return response;
  }
}

// 望诊服务客户端实现/;,/g/;
export class LookServiceClientImpl implements LookServiceClient {;,}private baseUrl: string;
private timeout: number;
private retries: number;
constructor() {this.baseUrl = API_CONFIG.look.baseUrl;,}this.timeout = API_CONFIG.look.timeout;
}
    this.retries = API_CONFIG.look.retries;}
  }

  const async = analyzeFace(imageData: ImageData): Promise<LookResult> {DataValidator.validateImageData(imageData);}}
}
    const url = `${this.baseUrl}/api/v1/look/face`;``'/`;,`/g`/`;
const formData = new FormData();';,'';
formData.append('image',')'';
new: Blob([imageData.data]),;
      `face.${imageData.format}```'`;```;
    );';,'';
formData.append('analysis_type', 'comprehensive');';,'';
const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';'';
}
        body: formData,}
        headers: {;}, // 让浏览器自动设置Content-Type/;/g/;
      }
this.timeout,)';,'';
this.retries,)';'';
      'look')';'';
    );
return {features: response.features || []}confidence: response.confidence || 0.8,;
}
      const recommendations = response.recommendations || [];}
    };
  }

  const async = analyzeTongue(imageData: ImageData): Promise<LookResult> {DataValidator.validateImageData(imageData);}}
}
    const url = `${this.baseUrl}/api/v1/look/tongue`;``'/`;,`/g`/`;
const formData = new FormData();';,'';
formData.append('image',')'';
new: Blob([imageData.data]),;
      `tongue.${imageData.format}```'`;```;
    );';,'';
formData.append('analysis_type', 'comprehensive');';,'';
const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';'';
}
        body: formData,}
        headers: {;}, // 让浏览器自动设置Content-Type/;/g/;
      }
this.timeout,)';,'';
this.retries,)';'';
      'look')';'';
    );
return {features: response.features || []}confidence: response.confidence || 0.8,;
}
      const recommendations = response.recommendations || [];}
    };
  }
}

// 闻诊服务客户端实现/;,/g/;
export class ListenServiceClientImpl implements ListenServiceClient {;,}private baseUrl: string;
private timeout: number;
private retries: number;
constructor() {this.baseUrl = API_CONFIG.listen.baseUrl;,}this.timeout = API_CONFIG.listen.timeout;
}
    this.retries = API_CONFIG.listen.retries;}
  }

  const async = analyzeVoice(audioData: AudioData): Promise<ListenResult> {DataValidator.validateAudioData(audioData);}}
}
    const url = `${this.baseUrl}/api/v1/listen/voice`;``'/`;,`/g`/`;
const formData = new FormData();';,'';
formData.append('audio',')'';
new: Blob([audioData.data]),;
      `voice.${audioData.format}```'`;```;
    );';,'';
formData.append('analysis_type', 'comprehensive');';,'';
const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';'';
}
        body: formData,}
        headers: {;}, // 让浏览器自动设置Content-Type/;/g/;
      }
this.timeout,)';,'';
this.retries,)';'';
      'listen')';'';
    );
return {features: response.features || []}confidence: response.confidence || 0.8,;
}
      const recommendations = response.recommendations || [];}
    };
  }

  const async = analyzeBreathing(audioData: AudioData): Promise<ListenResult> {DataValidator.validateAudioData(audioData);}}
}
    const url = `${this.baseUrl}/api/v1/listen/breathing`;``'/`;,`/g`/`;
const formData = new FormData();';,'';
formData.append('audio',')'';
new: Blob([audioData.data]),;
      `breathing.${audioData.format}```'`;```;
    );';,'';
formData.append('analysis_type', 'comprehensive');';,'';
const: response = await apiRequest<any>(url,';)      {';,}method: 'POST';','';'';
}
        body: formData,}
        headers: {;}, // 让浏览器自动设置Content-Type/;/g/;
      }
this.timeout,)';,'';
this.retries,)';'';
      'listen')';'';
    );
return {features: response.features || []}confidence: response.confidence || 0.8,;
}
      const recommendations = response.recommendations || [];}
    };
  }
}

// 切诊服务客户端实现/;,/g/;
export class PalpationServiceClientImpl implements PalpationServiceClient {;,}private baseUrl: string;
private timeout: number;
private retries: number;
constructor() {this.baseUrl = API_CONFIG.palpation.baseUrl;,}this.timeout = API_CONFIG.palpation.timeout;
}
    this.retries = API_CONFIG.palpation.retries;}
  }

  const async = analyzePalpation(data: PalpationData): Promise<PalpationResult> {DataValidator.validatePalpationData(data);}}
}
    const url = `${this.baseUrl}/api/v1/palpation/analyze`;```/`;,`/g,`/`;
  const: response = await apiRequest<any>(url,)';'';
      {)';,}method: 'POST';',)'';'';
}
        const body = JSON.stringify(data);}
      }
this.timeout,';,'';
this.retries,';'';
      'palpation'';'';
    );
return {}}
}
      measurements: response.measurements || {;}
confidence: response.confidence || 0.8,;
const recommendations = response.recommendations || [];
    };
  }

  const async = startRealTimeMonitoring(userId: string): Promise<string> {}
    const url = `${this.baseUrl;}/api/v1/palpation/monitor/start`;```/`;,`/g,`/`;
  const: response = await apiRequest<any>(url,)';'';
      {)';}}'';
        method: 'POST';',)'}'';
body: JSON.stringify({ user_id: userId ;}),;
      }
this.timeout,';,'';
this.retries,';'';
      'palpation'';'';
    );
return response.session_id;
  }
}

// 综合诊断服务客户端实现/;,/g/;
export class DiagnosisServiceClientImpl implements DiagnosisServiceClient {;,}const public = inquiry: InquiryServiceClient;
const public = look: LookServiceClient;
const public = listen: ListenServiceClient;
const public = palpation: PalpationServiceClient;
constructor() {this.inquiry = new InquiryServiceClientImpl();,}this.look = new LookServiceClientImpl();
this.listen = new ListenServiceClientImpl();
}
    this.palpation = new PalpationServiceClientImpl();}
  }
';,'';
const async = healthCheck(): Promise<{ [key: string]: boolean ;}> {';}}'';
    services: ['inquiry', 'look', 'listen', 'palpation'];'}'';
const results: { [key: string]: boolean ;} = {};
const await = Promise.allSettled();
services.map(async (service) => {try {}}
          const config = API_CONFIG[service as keyof typeof API_CONFIG];}';,'';
const: response = await fetch(`${config.baseUrl}/health`, {/`;)``)'`;,}method: 'GET';',)'';'/g'/`;
}
            const signal = AbortSignal.timeout(5000);}
          });
results[service] = response.ok;
        } catch {}}
          results[service] = false;}
        }
      });
    );
return results;
  }

  async: comprehensiveDiagnosis(data: {)}const userId = string;
imageData?: ImageData;
audioData?: AudioData;);
palpationData?: PalpationData;);
}
    symptoms?: string[];)}
  }): Promise<any> {}
    const results: any = {;};
try {// 并行执行各种诊断/;,}const promises: Promise<any>[] = [];/g/;

      // 问诊/;,/g/;
if (data.symptoms && data.symptoms.length > 0) {promises.push()';}}'';
          this.inquiry.startSession(data.userId).then((sessionId) => {'}'';
return { type: 'inquiry', sessionId ;};';'';
          });
        );
      }

      // 望诊/;,/g/;
if (data.imageData) {promises.push()';}}'';
          this.look.analyzeFace(data.imageData).then((result) => {'}'';
return { type: 'look', result ;};';'';
          });
        );
      }

      // 闻诊/;,/g/;
if (data.audioData) {promises.push()';}}'';
          this.listen.analyzeVoice(data.audioData).then((result) => {'}'';
return { type: 'listen', result ;};';'';
          });
        );
      }

      // 切诊/;,/g/;
if (data.palpationData) {promises.push()';}}'';
          this.palpation.analyzePalpation(data.palpationData).then((result) => {'}'';
return { type: 'palpation', result ;};';'';
          });
        );
      }

      const diagnosisResults = await Promise.allSettled(promises);

      // 处理结果'/;,'/g'/;
diagnosisResults.forEach((result, index) => {';,}if (result.status === 'fulfilled') {';}}'';
          results[result.value.type] = result.value.result || result.value;}
        } else {}}
}
        }
      });

      // 计算综合置信度/;,/g/;
const overallConfidence = this.calculateOverallConfidence(results);
return {userId: data.userId}const timestamp = new Date().toISOString();
results,;
overallConfidence,;
}
        const recommendations = this.generateRecommendations(results);}
      };
    } catch (error) {';,}throw: new DiagnosisApiError(500,')'';'';
        'comprehensive',')'';
false);
}
      );}
    }
  }

  private calculateOverallConfidence(results: any): number {const confidences: number[] = [];';,}Object.values(results).forEach((result: any) => {';,}if (result && typeof result.confidence === 'number') {';}}'';
        confidences.push(result.confidence);}
      }
    });
const return = confidences.length > 0;
      ? confidences.reduce((sum, conf) => sum + conf, 0) / confidences.length/;/g/;
      : 0;
  }

  private generateRecommendations(results: any): string[] {const recommendations: string[] = [];,}Object.values(results).forEach((result: any) => {if (result && Array.isArray(result.recommendations)) {}}
        recommendations.push(...result.recommendations);}
      }
    });
return Array.from(new Set(recommendations)); // 去重/;/g/;
  }

  clearCache(): void {}}
    cacheManager.clear();}
  }
}

// 创建诊断服务客户端实例/;,/g/;
export const diagnosisServiceClient = new DiagnosisServiceClientImpl();
export default DiagnosisServiceClientImpl;';'';
''';