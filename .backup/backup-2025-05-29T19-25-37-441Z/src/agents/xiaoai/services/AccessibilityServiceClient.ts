import {
  AccessibilityNeeds,
  UserProfile,
  ImageData,
  AudioData
} from '../types';

// 无障碍服务配置
const ACCESSIBILITY_API_CONFIG = {
  baseUrl: 'http://localhost:50051', // 无障碍服务地址
  timeout: 30000
};

// 无障碍服务响应类型
export interface AccessibilityResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export interface VoiceAssistanceResponse {
  recognized_text: string;
  response_text: string;
  response_audio: string; // base64编码的音频
  confidence: number;
  success: boolean;
  error?: string;
}

export interface ImageAssistanceResponse {
  scene_description: string;
  medical_features: Array<{
    type: string;
    description: string;
    confidence: number;
  }>;
  navigation_guidance: string;
  confidence: number;
  audio_guidance: string; // base64编码的音频
  success: boolean;
  error?: string;
}

export interface SignLanguageResponse {
  recognized_text: string;
  confidence: number;
  segments: Array<{
    text: string;
    start_time_ms: number;
    end_time_ms: number;
    confidence: number;
  }>;
  success: boolean;
  error?: string;
}

export interface AccessibleContentResponse {
  accessible_content: string;
  content_url: string;
  audio_content: string; // base64编码的音频
  tactile_content: string; // 盲文内容
  success: boolean;
  error?: string;
}

export interface ScreenReadingResponse {
  screen_description: string;
  ui_elements: Array<{
    element_type: string;
    content: string;
    action: string;
    location: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }>;
  audio_description: string; // base64编码的音频
  success: boolean;
  error?: string;
}

export interface AccessibilitySettingsResponse {
  current_preferences: {
    language: string;
    voice_type: string;
    speech_rate: number;
    high_contrast: boolean;
    screen_reader: boolean;
    font_size: string;
    [key: string]: any;
  };
  success: boolean;
  message: string;
  error?: string;
}

/**
 * 无障碍服务客户端
 * 对应后端Python的AccessibilityClient实现
 */
export class AccessibilityServiceClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = ACCESSIBILITY_API_CONFIG.baseUrl;
    this.timeout = ACCESSIBILITY_API_CONFIG.timeout;
  }

  /**
   * 处理语音输入，支持语音识别和语音辅助
   */
  async processVoiceInput(
    audioData: AudioData,
    userId: string,
    context: string = 'diagnosis',
    language: string = 'zh-CN',
    dialect: string = 'standard'
  ): Promise<VoiceAssistanceResponse> {
    try {
      const formData = new FormData();
      
      // 处理音频数据
      if (audioData.base64) {
        formData.append('audio_data', audioData.base64);
      } else {
        const response = await fetch(audioData.uri);
        const blob = await response.blob();
        formData.append('audio_file', blob);
      }
      
      formData.append('user_id', userId);
      formData.append('context', context);
      formData.append('language', language);
      formData.append('dialect', dialect);

      const response = await fetch(`${this.baseUrl}/api/v1/accessibility/voice-assistance`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      return {
        recognized_text: result.recognized_text || '',
        response_text: result.response_text || '',
        response_audio: result.response_audio || '',
        confidence: result.confidence || 0.0,
        success: true
      };

    } catch (error) {
      console.error('语音输入处理失败:', error);
      return {
        recognized_text: '',
        response_text: `语音处理失败: ${(error as Error).message}`,
        response_audio: '',
        confidence: 0.0,
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 处理图像输入，支持图像识别和描述
   */
  async processImageInput(
    imageData: ImageData,
    userId: string,
    imageType: string = 'tongue',
    context: string = 'looking_diagnosis'
  ): Promise<ImageAssistanceResponse> {
    try {
      const formData = new FormData();
      
      // 处理图像数据
      if (imageData.base64) {
        formData.append('image_data', imageData.base64);
      } else {
        const response = await fetch(imageData.uri);
        const blob = await response.blob();
        formData.append('image_file', blob);
      }
      
      formData.append('user_id', userId);
      formData.append('image_type', imageType);
      formData.append('context', context);
      formData.append('preferences', JSON.stringify({
        language: 'zh-CN',
        detail_level: 'high',
        medical_context: true
      }));

      const response = await fetch(`${this.baseUrl}/api/v1/accessibility/image-assistance`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      return {
        scene_description: result.scene_description || '',
        medical_features: result.medical_features || [],
        navigation_guidance: result.navigation_guidance || '',
        confidence: result.confidence || 0.0,
        audio_guidance: result.audio_guidance || '',
        success: true
      };

    } catch (error) {
      console.error('图像输入处理失败:', error);
      return {
        scene_description: `图像处理失败: ${(error as Error).message}`,
        medical_features: [],
        navigation_guidance: '',
        confidence: 0.0,
        audio_guidance: '',
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 处理手语输入，支持手语识别
   */
  async processSignLanguageInput(
    videoData: Blob,
    userId: string,
    language: string = 'csl'
  ): Promise<SignLanguageResponse> {
    try {
      const formData = new FormData();
      formData.append('video_file', videoData);
      formData.append('user_id', userId);
      formData.append('language', language);

      const response = await fetch(`${this.baseUrl}/api/v1/accessibility/sign-language`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      return {
        recognized_text: result.recognized_text || '',
        confidence: result.confidence || 0.0,
        segments: result.segments || [],
        success: true
      };

    } catch (error) {
      console.error('手语输入处理失败:', error);
      return {
        recognized_text: `手语处理失败: ${(error as Error).message}`,
        confidence: 0.0,
        segments: [],
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 生成无障碍健康内容
   */
  async generateAccessibleHealthContent(
    content: string,
    userId: string,
    contentType: string = 'diagnosis_result',
    targetFormat: string = 'audio'
  ): Promise<AccessibleContentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/accessibility/accessible-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          content,
          user_id: userId,
          content_type: contentType,
          target_format: targetFormat,
          preferences: {
            language: 'zh-CN',
            voice_type: 'female',
            speech_rate: 1.0,
            high_contrast: false
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      return {
        accessible_content: result.accessible_content || '',
        content_url: result.content_url || '',
        audio_content: result.audio_content || '',
        tactile_content: result.tactile_content || '',
        success: true
      };

    } catch (error) {
      console.error('无障碍内容生成失败:', error);
      return {
        accessible_content: `内容转换失败: ${(error as Error).message}`,
        content_url: '',
        audio_content: '',
        tactile_content: '',
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 提供屏幕阅读服务
   */
  async provideScreenReading(
    screenData: string, // base64编码的屏幕截图
    userId: string,
    context: string = 'diagnosis_interface'
  ): Promise<ScreenReadingResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/accessibility/screen-reading`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          screen_data: screenData,
          user_id: userId,
          context,
          preferences: {
            language: 'zh-CN',
            detail_level: 'medium',
            medical_context: true
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      return {
        screen_description: result.screen_description || '',
        ui_elements: result.ui_elements || [],
        audio_description: result.audio_description || '',
        success: true
      };

    } catch (error) {
      console.error('屏幕阅读失败:', error);
      return {
        screen_description: `屏幕阅读失败: ${(error as Error).message}`,
        ui_elements: [],
        audio_description: '',
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 管理用户的无障碍设置
   */
  async manageAccessibilitySettings(
    userId: string,
    preferences: any,
    action: string = 'update'
  ): Promise<AccessibilitySettingsResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/accessibility/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          preferences,
          action
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      return {
        current_preferences: result.current_preferences || {},
        success: result.success || false,
        message: result.message || '',
      };

    } catch (error) {
      console.error('无障碍设置管理失败:', error);
      return {
        current_preferences: {
          language: 'zh-CN',
          voice_type: 'female',
          speech_rate: 1.0,
          high_contrast: false,
          screen_reader: false,
          font_size: 'medium'
        },
        success: false,
        message: `设置管理失败: ${(error as Error).message}`,
        error: (error as Error).message
      };
    }
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.error('无障碍服务健康检查失败:', error);
      return false;
    }
  }

  /**
   * 根据用户的无障碍需求适配界面
   */
  async adaptInterfaceForAccessibility(
    accessibilityNeeds: AccessibilityNeeds
  ): Promise<any> {
    const adaptations: any = {
      visual: {},
      hearing: {},
      motor: {},
      cognitive: {}
    };

    // 视觉障碍适配
    if (accessibilityNeeds.visual) {
      adaptations.visual = {
        fontSize: accessibilityNeeds.preferences.fontSize,
        highContrast: accessibilityNeeds.preferences.highContrast,
        screenReader: accessibilityNeeds.preferences.voiceOutput,
        magnification: true,
        colorAdjustment: true
      };
    }

    // 听觉障碍适配
    if (accessibilityNeeds.hearing) {
      adaptations.hearing = {
        captions: true,
        visualIndicators: true,
        vibrationFeedback: true,
        signLanguageSupport: true
      };
    }

    // 运动障碍适配
    if (accessibilityNeeds.motor) {
      adaptations.motor = {
        largeButtons: true,
        voiceControl: true,
        eyeTracking: true,
        switchControl: true,
        gestureAlternatives: true
      };
    }

    // 认知障碍适配
    if (accessibilityNeeds.cognitive) {
      adaptations.cognitive = {
        simplifiedInterface: accessibilityNeeds.preferences.simplifiedInterface,
        stepByStep: true,
        reminders: true,
        navigationAssist: true,
        clearInstructions: true
      };
    }

    return adaptations;
  }
}

// 创建单例实例
export const accessibilityServiceClient = new AccessibilityServiceClient(); 