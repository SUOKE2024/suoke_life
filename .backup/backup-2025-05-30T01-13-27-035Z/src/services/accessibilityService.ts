/**
 * 无障碍服务集成模块
 * 为四个智能体提供accessibility-service的各种功能
 */

// 无障碍服务配置
export interface AccessibilityConfig {
  serviceUrl: string;
  apiKey?: string;
  timeout: number;
  retryAttempts: number;
}

// 用户偏好设置
export interface UserPreferences {
  fontSize: "small" | "medium" | "large" | "extra-large";
  highContrast: boolean;
  voiceType: "male" | "female" | "child";
  speechRate: number; // 0.5 - 2.0
  language: string;
  dialect?: string;
  screenReader: boolean;
  signLanguage: boolean;
  enabledFeatures: string[];
}

// 导盲服务接口
export interface BlindAssistanceRequest {
  imageData: string; // base64编码的图像数据
  userId: string;
  preferences?: UserPreferences;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface BlindAssistanceResponse {
  sceneDescription: string;
  obstacles: Array<{
    type: string;
    distance: number;
    direction: string;
    confidence: number;
  }>;
  navigationGuidance: string;
  confidence: number;
  audioGuidance?: string; // base64编码的音频数据
}

// 手语识别接口
export interface SignLanguageRequest {
  videoData: string; // base64编码的视频数据
  userId: string;
  language: string;
}

export interface SignLanguageResponse {
  text: string;
  confidence: number;
  segments: Array<{
    text: string;
    startTimeMs: number;
    endTimeMs: number;
    confidence: number;
  }>;
}

// 屏幕阅读接口
export interface ScreenReadingRequest {
  screenData: string; // base64编码的屏幕截图
  userId: string;
  context?: string;
  preferences?: UserPreferences;
}

export interface ScreenReadingResponse {
  screenDescription: string;
  elements: Array<{
    elementType: string;
    content: string;
    action: string;
    location: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }>;
  audioDescription?: string; // base64编码的音频数据
}

// 语音辅助接口
export interface VoiceAssistanceRequest {
  audioData: string; // base64编码的音频数据
  userId: string;
  context?: string;
  language: string;
  dialect?: string;
}

export interface VoiceAssistanceResponse {
  recognizedText: string;
  responseText: string;
  responseAudio?: string; // base64编码的音频数据
  confidence: number;
}

// 内容转换接口
export interface AccessibleContentRequest {
  contentId: string;
  contentType: string;
  userId: string;
  targetFormat: "audio" | "braille" | "large-text" | "high-contrast";
  preferences?: UserPreferences;
}

export interface AccessibleContentResponse {
  accessibleContent: string;
  contentUrl?: string;
  audioContent?: string; // base64编码的音频数据
  tactileContent?: string; // 盲文等触觉内容
}

// 语音翻译接口
export interface SpeechTranslationRequest {
  audioData: string; // base64编码的音频数据
  userId: string;
  sourceLanguage: string;
  targetLanguage: string;
  context?: string;
}

export interface SpeechTranslationResponse {
  originalText: string;
  translatedText: string;
  translatedAudio?: string; // base64编码的音频数据
  confidence: number;
}

// 健康数据收集接口
export interface BackgroundCollectionRequest {
  userId: string;
  dataTypes: string[];
  collectionInterval: number;
  privacyLevel: "minimal" | "standard" | "comprehensive";
}

export interface BackgroundCollectionResponse {
  success: boolean;
  message: string;
  collectionId: string;
}

// 危机报警接口
export interface HealthAlertRequest {
  userId: string;
  alertType: "emergency" | "warning" | "info";
  healthData: Record<string, any>;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface HealthAlertResponse {
  alertId: string;
  alertLevel: "critical" | "high" | "medium" | "low";
  message: string;
  recommendedActions: Array<{
    action: string;
    priority: number;
    description: string;
  }>;
  agentActions: Array<{
    agentType: string;
    action: string;
    parameters: Record<string, any>;
  }>;
}

// 无障碍服务类
export class AccessibilityService {
  private config: AccessibilityConfig;

  constructor(config: AccessibilityConfig) {
    this.config = config;
  }

  /**
   * 导盲服务 - 为视障用户提供环境描述和导航指引
   */
  async blindAssistance(
    request: BlindAssistanceRequest
  ): Promise<BlindAssistanceResponse> {
    try {
      const response = await this.makeRequest("/api/blind-assistance", request);
      return response;
    } catch (error) {
      console.error("导盲服务调用失败:", error);
      throw new Error("导盲服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 手语识别 - 将手语视频转换为文本
   */
  async signLanguageRecognition(
    request: SignLanguageRequest
  ): Promise<SignLanguageResponse> {
    try {
      const response = await this.makeRequest("/api/sign-language", request);
      return response;
    } catch (error) {
      console.error("手语识别服务调用失败:", error);
      throw new Error("手语识别服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 屏幕阅读 - 提供屏幕内容的语音描述
   */
  async screenReading(
    request: ScreenReadingRequest
  ): Promise<ScreenReadingResponse> {
    try {
      const response = await this.makeRequest("/api/screen-reading", request);
      return response;
    } catch (error) {
      console.error("屏幕阅读服务调用失败:", error);
      throw new Error("屏幕阅读服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 语音辅助 - 提供语音控制和语音响应
   */
  async voiceAssistance(
    request: VoiceAssistanceRequest
  ): Promise<VoiceAssistanceResponse> {
    try {
      const response = await this.makeRequest("/api/voice-assistance", request);
      return response;
    } catch (error) {
      console.error("语音辅助服务调用失败:", error);
      throw new Error("语音辅助服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 健康内容无障碍转换
   */
  async accessibleContent(
    request: AccessibleContentRequest
  ): Promise<AccessibleContentResponse> {
    try {
      const response = await this.makeRequest(
        "/api/accessible-content",
        request
      );
      return response;
    } catch (error) {
      console.error("内容转换服务调用失败:", error);
      throw new Error("内容转换服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 语音翻译服务
   */
  async speechTranslation(
    request: SpeechTranslationRequest
  ): Promise<SpeechTranslationResponse> {
    try {
      const response = await this.makeRequest(
        "/api/speech-translation",
        request
      );
      return response;
    } catch (error) {
      console.error("语音翻译服务调用失败:", error);
      throw new Error("语音翻译服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 配置后台健康数据收集
   */
  async configureBackgroundCollection(
    request: BackgroundCollectionRequest
  ): Promise<BackgroundCollectionResponse> {
    try {
      const response = await this.makeRequest(
        "/api/background-collection",
        request
      );
      return response;
    } catch (error) {
      console.error("后台数据收集配置失败:", error);
      throw new Error("后台数据收集服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 触发健康危机报警
   */
  async triggerHealthAlert(
    request: HealthAlertRequest
  ): Promise<HealthAlertResponse> {
    try {
      const response = await this.makeRequest("/api/health-alert", request);
      return response;
    } catch (error) {
      console.error("健康报警服务调用失败:", error);
      throw new Error("健康报警服务暂时不可用，请稍后重试");
    }
  }

  /**
   * 获取用户无障碍设置
   */
  async getUserPreferences(userId: string): Promise<UserPreferences> {
    try {
      const response = await this.makeRequest("/api/user-preferences", {
        userId,
        action: "get",
      });
      return response.preferences;
    } catch (error) {
      console.error("获取用户设置失败:", error);
      // 返回默认设置
      return {
        fontSize: "medium",
        highContrast: false,
        voiceType: "female",
        speechRate: 1.0,
        language: "zh_CN",
        screenReader: false,
        signLanguage: false,
        enabledFeatures: [],
      };
    }
  }

  /**
   * 更新用户无障碍设置
   */
  async updateUserPreferences(
    userId: string,
    preferences: Partial<UserPreferences>
  ): Promise<boolean> {
    try {
      const response = await this.makeRequest("/api/user-preferences", {
        userId,
        action: "update",
        preferences,
      });
      return response.success;
    } catch (error) {
      console.error("更新用户设置失败:", error);
      return false;
    }
  }

  /**
   * 获取支持的语言和方言列表
   */
  async getSupportedLanguages(): Promise<
    Array<{ code: string; name: string; dialects?: string[] }>
  > {
    try {
      const response = await this.makeRequest("/api/supported-languages", {});
      return response.languages;
    } catch (error) {
      console.error("获取支持语言列表失败:", error);
      // 返回默认支持的语言
      return [
        {
          code: "zh_CN",
          name: "中文（简体）",
          dialects: ["普通话", "粤语", "闽南语", "上海话"],
        },
        { code: "en_US", name: "English (US)" },
        { code: "ja_JP", name: "日本語" },
        { code: "ko_KR", name: "한국어" },
      ];
    }
  }

  /**
   * 通用请求方法
   */
  private async makeRequest(endpoint: string, data: any): Promise<any> {
    const url = `${this.config.serviceUrl}${endpoint}`;

    for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(
          () => controller.abort(),
          this.config.timeout
        );

        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(this.config.apiKey && {
              Authorization: `Bearer ${this.config.apiKey}`,
            }),
          },
          body: JSON.stringify(data),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        console.error(
          `请求失败 (尝试 ${attempt + 1}/${this.config.retryAttempts}):`,
          error
        );

        if (attempt === this.config.retryAttempts - 1) {
          throw error;
        }

        // 指数退避重试
        await new Promise<void>((resolve) =>
          setTimeout(() => resolve(), Math.pow(2, attempt) * 1000)
        );
      }
    }
  }
}

// 默认配置
export const defaultAccessibilityConfig: AccessibilityConfig = {
  serviceUrl: "http://localhost:50051", // accessibility-service的默认地址
  timeout: 30000, // 30秒超时
  retryAttempts: 3,
};

// 创建默认实例
export const accessibilityService = new AccessibilityService(
  defaultAccessibilityConfig
);

// 智能体专用的无障碍功能封装
export class AgentAccessibilityHelper {
  private service: AccessibilityService;
  private agentType: string;

  constructor(service: AccessibilityService, agentType: string) {
    this.service = service;
    this.agentType = agentType;
  }

  /**
   * 为智能体提供语音输入处理
   */
  async processVoiceInput(
    audioData: string,
    userId: string,
    language: string = "zh_CN"
  ): Promise<string> {
    try {
      const response = await this.service.voiceAssistance({
        audioData,
        userId,
        language,
        context: `agent_${this.agentType}`,
      });
      return response.recognizedText;
    } catch (error) {
      console.error(`${this.agentType}语音输入处理失败:`, error);
      throw error;
    }
  }

  /**
   * 为智能体提供语音输出生成
   */
  async generateVoiceOutput(
    text: string,
    userId: string,
    language: string = "zh_CN"
  ): Promise<string | null> {
    try {
      const preferences = await this.service.getUserPreferences(userId);

      // 这里可以调用TTS服务或使用accessibility-service的语音合成功能
      // 暂时返回null，表示使用系统默认TTS
      return null;
    } catch (error) {
      console.error(`${this.agentType}语音输出生成失败:`, error);
      return null;
    }
  }

  /**
   * 为智能体提供多语言翻译
   */
  async translateMessage(
    text: string,
    userId: string,
    targetLanguage: string
  ): Promise<string> {
    try {
      // 如果目标语言是中文，直接返回
      if (targetLanguage === "zh_CN") {
        return text;
      }

      // 这里可以集成翻译服务
      // 暂时返回原文
      return text;
    } catch (error) {
      console.error(`${this.agentType}消息翻译失败:`, error);
      return text;
    }
  }

  /**
   * 为智能体提供内容无障碍转换
   */
  async makeContentAccessible(
    content: string,
    userId: string,
    targetFormat: "audio" | "braille" | "large-text" | "high-contrast"
  ): Promise<AccessibleContentResponse> {
    try {
      const response = await this.service.accessibleContent({
        contentId: `${this.agentType}_${Date.now()}`,
        contentType: "text",
        userId,
        targetFormat,
      });
      return response;
    } catch (error) {
      console.error(`${this.agentType}内容无障碍转换失败:`, error);
      throw error;
    }
  }

  /**
   * 为智能体提供健康数据监控
   */
  async monitorHealthData(
    userId: string,
    dataTypes: string[]
  ): Promise<string> {
    try {
      const response = await this.service.configureBackgroundCollection({
        userId,
        dataTypes,
        collectionInterval: 300000, // 5分钟
        privacyLevel: "standard",
      });

      return response.collectionId;
    } catch (error) {
      console.error(`${this.agentType}健康数据监控配置失败:`, error);
      throw error;
    }
  }

  /**
   * 为智能体提供危机报警功能
   */
  async checkHealthAlert(
    userId: string,
    healthData: Record<string, any>
  ): Promise<HealthAlertResponse | null> {
    try {
      // 只有在检测到异常时才触发报警
      const hasAbnormalData = this.detectAbnormalHealthData(healthData);

      if (hasAbnormalData) {
        const response = await this.service.triggerHealthAlert({
          userId,
          alertType: "warning",
          healthData,
        });
        return response;
      }

      return null;
    } catch (error) {
      console.error(`${this.agentType}健康报警检查失败:`, error);
      return null;
    }
  }

  /**
   * 检测异常健康数据（简单实现）
   */
  private detectAbnormalHealthData(healthData: Record<string, any>): boolean {
    // 这里可以实现更复杂的异常检测逻辑
    // 暂时返回false，表示没有异常
    return false;
  }
}
