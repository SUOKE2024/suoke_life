import {

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
  PalpationResult,
} from "../types";

// API配置
const API_CONFIG = {
  inquiry: {
    baseUrl: "http://localhost:50052",
    timeout: 30000,
  },
  look: {
    baseUrl: "http://localhost:50053",
    timeout: 30000,
  },
  listen: {
    baseUrl: "http://localhost:50052",
    timeout: 30000,
  },
  palpation: {
    baseUrl: "http://localhost:8000",
    timeout: 30000,
  },
};

// 通用API请求函数
async function apiRequest<T>(
  url: string,
  options: RequestInit = {},
  timeout: number = 30000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// 问诊服务客户端实现
class InquiryServiceClientImpl implements InquiryServiceClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.inquiry.baseUrl;
    this.timeout = API_CONFIG.inquiry.timeout;
  }

  async startSession(userId: string): Promise<any> {
    const url = `${this.baseUrl}/api/v1/inquiry/session/start`;
    return apiRequest(
      url,
      {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
          session_type: "general",
          language_preference: "zh-CN",
        }),
      },
      this.timeout
    );
  }

  async interact(sessionId: string, message: string): Promise<any> {
    const url = `${this.baseUrl}/api/v1/inquiry/session/interact`;
    return apiRequest(
      url,
      {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          user_message: message,
          timestamp: Date.now(),
        }),
      },
      this.timeout
    );
  }

  async endSession(sessionId: string): Promise<InquiryResult> {
    const url = `${this.baseUrl}/api/v1/inquiry/session/end`;
    const response = await apiRequest<any>(
      url,
      {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          feedback: "completed",
        }),
      },
      this.timeout
    );

    // 转换为标准格式
    return {
      sessionId: response.session_id,
      detectedSymptoms: response.detected_symptoms || [],
      tcmPatterns: response.tcm_patterns || [],
      healthProfile: response.health_profile || {},
      recommendations: response.recommendations || [],
      confidence: response.confidence || 0.8,
    };
  }

  async extractSymptoms(text: string, userId?: string): Promise<any> {
    const url = `${this.baseUrl}/api/v1/inquiry/symptoms/extract`;
    return apiRequest(
      url,
      {
        method: "POST",
        body: JSON.stringify({
          text_content: text,
          user_id: userId,
          language: "zh-CN",
        }),
      },
      this.timeout
    );
  }
}

// 望诊服务客户端实现
class LookServiceClientImpl implements LookServiceClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.look.baseUrl;
    this.timeout = API_CONFIG.look.timeout;
  }

  async analyzeImage(imageData: ImageData): Promise<LookResult> {
    const url = `${this.baseUrl}/api/v1/look/analyze`;

    const formData = new FormData();
    formData.append("image_type", imageData.type);
    formData.append("user_id", "current_user"); // 应该从context获取

    if (imageData.base64) {
      formData.append("image_data", imageData.base64);
    } else {
      // 处理文件上传
      const response = await fetch(imageData.uri);
      const blob = await response.blob();
      formData.append("image_file", blob);
    }

    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    return {
      analysisId: result.analysis_id,
      faceAnalysis: result.face_analysis,
      tongueAnalysis: result.tongue_analysis,
      bodyAnalysis: result.body_analysis,
      overallAssessment: result.overall_assessment || "分析完成",
      confidence: result.confidence || 0.8,
    };
  }

  async batchAnalyze(images: ImageData[]): Promise<LookResult[]> {
    const results: LookResult[] = [];

    for (const image of images) {
      try {
        const result = await this.analyzeImage(image);
        results.push(result);
      } catch (error) {
        console.error(`分析图片失败: ${image.id}`, error);
        // 继续处理其他图片
      }
    }

    return results;
  }
}

// 闻诊服务客户端实现
class ListenServiceClientImpl implements ListenServiceClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.listen.baseUrl;
    this.timeout = API_CONFIG.listen.timeout;
  }

  async analyzeAudio(audioData: AudioData): Promise<ListenResult> {
    const url = `${this.baseUrl}/api/v1/listen/analyze`;

    const formData = new FormData();
    formData.append("audio_type", audioData.type);
    formData.append("user_id", "current_user");

    if (audioData.base64) {
      formData.append("audio_data", audioData.base64);
    } else {
      const response = await fetch(audioData.uri);
      const blob = await response.blob();
      formData.append("audio_file", blob);
    }

    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    return {
      analysisId: result.analysis_id,
      voiceFeatures: result.voice_features || {},
      emotionalState: result.emotional_state || {},
      respiratoryAnalysis: result.respiratory_analysis,
      overallAssessment: result.overall_assessment || "分析完成",
      confidence: result.confidence || 0.8,
    };
  }

  async analyzeVoiceFeatures(audioData: AudioData): Promise<any> {
    const url = `${this.baseUrl}/api/v1/listen/voice-features`;

    const formData = new FormData();
    if (audioData.base64) {
      formData.append("audio_data", audioData.base64);
    } else {
      const response = await fetch(audioData.uri);
      const blob = await response.blob();
      formData.append("audio_file", blob);
    }

    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

// 切诊服务客户端实现
class PalpationServiceClientImpl implements PalpationServiceClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.palpation.baseUrl;
    this.timeout = API_CONFIG.palpation.timeout;
  }

  async analyzePalpation(data: PalpationData): Promise<PalpationResult> {
    const url = `${this.baseUrl}/api/v1/palpation/analyze`;

    const response = await apiRequest<any>(
      url,
      {
        method: "POST",
        body: JSON.stringify({
          palpation_type: data.type,
          sensor_data: data.sensorData,
          user_id: "current_user",
          metadata: data.metadata,
        }),
      },
      this.timeout
    );

    return {
      analysisId: response.analysis_id,
      pulseAnalysis: response.pulse_analysis,
      abdominalAnalysis: response.abdominal_analysis,
      skinAnalysis: response.skin_analysis,
      overallAssessment: response.overall_assessment || "分析完成",
      confidence: response.confidence || 0.8,
    };
  }

  async startRealTimeMonitoring(userId: string): Promise<string> {
    const url = `${this.baseUrl}/api/v1/palpation/monitor/start`;

    const response = await apiRequest<any>(
      url,
      {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
          monitoring_type: "real_time",
        }),
      },
      this.timeout
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
    const services = ["inquiry", "look", "listen", "palpation"];
    const results: { [key: string]: boolean } = {};

    for (const service of services) {
      try {
        const config = API_CONFIG[service as keyof typeof API_CONFIG];
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const response = await fetch(`${config.baseUrl}/health`, {
          method: "GET",
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        results[service] = response.ok;
      } catch (error) {
        results[service] = false;
      }
    }

    return results;
  }
}

// 创建单例实例
export const diagnosisServiceClient = new DiagnosisServiceClientImpl();
