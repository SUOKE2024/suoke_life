import axios from 'axios';
import { API_URL, AGENT_SERVICE_PORTS } from '../../config/constants';

// 聊天请求类型
export interface ChatRequest {
  userId: string;
  message: string;
  sessionId: string;
  contextSize?: number;
  metadata?: Record<string, string>;
}

// 诊断协调请求类型
export interface DiagnosisCoordinationRequest {
  userId: string;
  sessionId: string;
  includeLooking?: boolean;
  includeListening?: boolean;
  includeInquiry?: boolean;
  includePalpation?: boolean;
  lookingData?: Blob;
  listeningData?: Blob;
  inquiryData?: string;
  palpationData?: Blob;
  settings?: Record<string, string>;
}

// 多模态请求类型
export interface MultimodalRequest {
  userId: string;
  sessionId: string;
  voiceData?: {
    audioData: Blob;
    audioFormat: string;
    sampleRate?: number;
    channels?: number;
    noiseReduction?: boolean;
    dialectDetection?: boolean;
  };
  imageData?: {
    imageData: Blob;
    imageFormat: string;
    imageType: string;
    applyPreprocessing?: boolean;
  };
  textData?: {
    text: string;
    language?: string;
  };
  metadata?: Record<string, string>;
}

// 健康记录请求类型
export interface HealthRecordRequest {
  userId: string;
  startDate?: string;
  endDate?: string;
  recordTypes?: string[];
  limit?: number;
  offset?: number;
}

// 健康摘要请求类型
export interface HealthSummaryRequest {
  userId: string;
  timeFrame?: string;
  includeMetrics?: string[];
  includePredictions?: boolean;
}

// 创建专门的小艾服务客户端
const xiaoaiClient = axios.create({
  baseURL: `http://localhost:${AGENT_SERVICE_PORTS.XIAOAI}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 四诊会话信息类型
export interface DiagnosisSession {
  sessionId: string;
  userId: string;
  status: 'active' | 'completed' | 'paused';
  createdAt: string;
  completedSteps: string[];
  currentStep?: string;
}

// 四诊分析结果类型
export interface DiagnosisAnalysis {
  analysisId: string;
  sessionId: string;
  constitutions: Array<{
    type: string;
    score: number;
    description: string;
    dominant: boolean;
  }>;
  syndrome: {
    primarySyndrome: string;
    secondarySyndromes: string[];
    confidence: number;
  };
  recommendations: Array<{
    category: string;
    content: string;
    priority: number;
  }>;
  detailedAnalysis: Record<string, any>;
}

// 小艾智能体API服务
const xiaoaiApi = {
  /**
   * 创建四诊会话
   * @param userId 用户ID
   * @returns 会话信息
   */
  createDiagnosisSession: async (userId: string): Promise<DiagnosisSession> => {
    try {
      const response = await xiaoaiClient.post('/api/v1/diagnosis/session', {
        userId,
        timestamp: new Date().toISOString()
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '创建诊断会话失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 与小艾进行普通聊天
   * @param data 聊天请求信息
   * @returns 聊天响应
   */
  chat: async (data: ChatRequest) => {
    try {
      const response = await xiaoaiClient.post('/api/v1/chat', {
        user_id: data.userId,
        message: data.message,
        session_id: data.sessionId,
        context_size: data.contextSize || 10,
        metadata: data.metadata || {}
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '聊天请求失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 与小艾进行流式聊天
   * @param data 聊天请求信息
   * @returns 流式聊天响应
   */
  chatStream: async (data: ChatRequest) => {
    try {
      const response = await xiaoaiClient.post('/api/v1/chat/stream', {
        user_id: data.userId,
        message: data.message,
        session_id: data.sessionId,
        context_size: data.contextSize || 10,
        metadata: data.metadata || {}
      }, {
        responseType: 'stream'
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '聊天请求失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 进行四诊协调
   * @param data 四诊协调请求数据
   * @returns 四诊协调结果
   */
  coordinateDiagnosis: async (data: DiagnosisCoordinationRequest) => {
    try {
      // 创建FormData对象用于上传文件
      const formData = new FormData();
      formData.append('user_id', data.userId);
      formData.append('session_id', data.sessionId);

      // 构建诊断配置
      const diagnosisConfig = {
        include_looking: data.includeLooking,
        include_listening: data.includeListening,
        include_inquiry: data.includeInquiry,
        include_palpation: data.includePalpation,
        settings: data.settings || {}
      };
      formData.append('config', JSON.stringify(diagnosisConfig));

      // 添加文件数据
      if (data.lookingData) {
        formData.append('looking_file', data.lookingData, 'tongue_image.jpg');
      }
      if (data.listeningData) {
        formData.append('listening_file', data.listeningData, 'voice_sample.wav');
      }
      if (data.inquiryData) {
        formData.append('inquiry_data', data.inquiryData);
      }
      if (data.palpationData) {
        formData.append('palpation_file', data.palpationData, 'pulse_data.json');
      }

      const response = await xiaoaiClient.post('/api/v1/diagnosis/coordinate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000 // 四诊协调可能需要更长时间
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '诊断协调失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 处理多模态输入
   * @param data 多模态输入数据
   * @returns 处理结果
   */
  processMultimodalInput: async (data: MultimodalRequest) => {
    try {
      // 创建FormData对象用于上传文件
      const formData = new FormData();
      formData.append('user_id', data.userId);
      formData.append('session_id', data.sessionId);

      if (data.voiceData) {
        formData.append('audio_file', data.voiceData.audioData, `audio.${data.voiceData.audioFormat}`);
        formData.append('audio_config', JSON.stringify({
          format: data.voiceData.audioFormat,
          sample_rate: data.voiceData.sampleRate,
          channels: data.voiceData.channels,
          noise_reduction: data.voiceData.noiseReduction,
          dialect_detection: data.voiceData.dialectDetection
        }));
      }

      if (data.imageData) {
        formData.append('image_file', data.imageData.imageData, `image.${data.imageData.imageFormat}`);
        formData.append('image_config', JSON.stringify({
          format: data.imageData.imageFormat,
          type: data.imageData.imageType,
          apply_preprocessing: data.imageData.applyPreprocessing
        }));
      }

      if (data.textData) {
        formData.append('text_data', JSON.stringify(data.textData));
      }

      if (data.metadata) {
        formData.append('metadata', JSON.stringify(data.metadata));
      }

      const response = await xiaoaiClient.post('/api/v1/multimodal/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '多模态处理失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取诊断分析结果
   * @param sessionId 会话ID
   * @returns 分析结果
   */
  getDiagnosisAnalysis: async (sessionId: string): Promise<DiagnosisAnalysis> => {
    try {
      const response = await xiaoaiClient.get(`/api/v1/diagnosis/${sessionId}/analysis`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取分析结果失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取健康建议
   * @param userId 用户ID
   * @param analysisId 分析ID
   * @returns 健康建议
   */
  getHealthRecommendations: async (userId: string, analysisId: string) => {
    try {
      const response = await xiaoaiClient.get(`/api/v1/health/recommendations`, {
        params: { user_id: userId, analysis_id: analysisId }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取健康建议失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 查询健康记录
   * @param data 健康记录请求数据
   * @returns 健康记录
   */
  queryHealthRecord: async (data: HealthRecordRequest) => {
    try {
      const response = await xiaoaiClient.get('/api/v1/health/records', { 
        params: {
          user_id: data.userId,
          start_date: data.startDate,
          end_date: data.endDate,
          record_types: data.recordTypes?.join(','),
          limit: data.limit,
          offset: data.offset
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '查询健康记录失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 生成健康摘要
   * @param data 健康摘要请求数据
   * @returns 健康摘要
   */
  generateHealthSummary: async (data: HealthSummaryRequest) => {
    try {
      const response = await xiaoaiClient.post('/api/v1/health/summary', {
        user_id: data.userId,
        time_frame: data.timeFrame,
        include_metrics: data.includeMetrics,
        include_predictions: data.includePredictions
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '生成健康摘要失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 健康检查
   * @returns 健康状态
   */
  healthCheck: async () => {
    try {
      const response = await xiaoaiClient.get('/health');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '健康检查失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },
};

export default xiaoaiApi;