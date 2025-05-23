import axios from 'axios';
import { API_BASE_URL } from '../config/constants';

// 定义API接口响应类型
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

// 望诊服务接口
export const lookService = {
  // 提交望诊数据
  submitDiagnosis: async (lookData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/look/analyze`, lookData);
      return response.data;
    } catch (error) {
      console.error('Look diagnosis API error:', error);
      return { success: false, message: '服务连接失败' };
    }
  },
  
  // 分析望诊图像
  analyzeImage: async (imageData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/look/image`, imageData);
      return response.data;
    } catch (error) {
      console.error('Image analysis API error:', error);
      return { success: false, message: '图像分析服务连接失败' };
    }
  },
  
  // 获取舌诊参考资料
  getTongueReferences: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/look/tongue-references`);
      return response.data;
    } catch (error) {
      console.error('Tongue references API error:', error);
      return { success: false, message: '获取参考资料失败', data: [] };
    }
  }
};

// 闻诊服务接口
export const listenService = {
  // 提交闻诊数据
  submitDiagnosis: async (listenData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/listen/analyze`, listenData);
      return response.data;
    } catch (error) {
      console.error('Listen diagnosis API error:', error);
      return { success: false, message: '服务连接失败' };
    }
  },
  
  // 分析声音样本
  analyzeAudio: async (audioData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/listen/audio`, audioData);
      return response.data;
    } catch (error) {
      console.error('Audio analysis API error:', error);
      return { success: false, message: '音频分析服务连接失败' };
    }
  },
  
  // 分析声音特征
  analyzeVoiceFeatures: async (audioData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/listen/voice-features`, audioData);
      return response.data;
    } catch (error) {
      console.error('Voice features analysis API error:', error);
      return { success: false, message: '声音特征分析服务连接失败' };
    }
  },
  
  // 获取声音特征参考
  getAudioReferences: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/listen/audio-references`);
      return response.data;
    } catch (error) {
      console.error('Audio references API error:', error);
      return { success: false, message: '获取参考资料失败', data: [] };
    }
  }
};

// 问诊服务接口
export const inquiryService = {
  // 提交问诊数据
  submitDiagnosis: async (inquiryData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/inquiry/analyze`, inquiryData);
      return response.data;
    } catch (error) {
      console.error('Inquiry diagnosis API error:', error);
      return { success: false, message: '服务连接失败' };
    }
  },
  
  // 获取症状推荐
  getSymptomRecommendations: async (query: string): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/inquiry/symptoms`, {
        params: { query }
      });
      return response.data;
    } catch (error) {
      console.error('Symptom recommendations API error:', error);
      return { success: false, message: '获取症状推荐失败', data: [] };
    }
  },
  
  // 获取病史模板
  getMedicalHistoryTemplates: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/inquiry/templates`);
      return response.data;
    } catch (error) {
      console.error('Medical history templates API error:', error);
      return { success: false, message: '获取病史模板失败', data: [] };
    }
  }
};

// 切诊服务接口
export const palpationService = {
  // 提交切诊数据
  submitDiagnosis: async (palpationData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/palpation/analyze`, palpationData);
      return response.data;
    } catch (error) {
      console.error('Palpation diagnosis API error:', error);
      return { success: false, message: '服务连接失败' };
    }
  },
  
  // 获取脉诊参考资料
  getPulseReferences: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/palpation/pulse-references`);
      return response.data;
    } catch (error) {
      console.error('Pulse references API error:', error);
      return { success: false, message: '获取脉诊参考资料失败', data: [] };
    }
  },
  
  // 获取腹诊参考图
  getAbdominalReferences: async (): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/palpation/abdominal-references`);
      return response.data;
    } catch (error) {
      console.error('Abdominal references API error:', error);
      return { success: false, message: '获取腹诊参考资料失败', data: [] };
    }
  }
};

// 四诊合参服务 - 提供综合分析
export const diagnosisService = {
  // 提交四诊合参分析
  submitDiagnosis: async (diagnosisData: any): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/diagnostic/analyze`, diagnosisData);
      return response.data;
    } catch (error) {
      console.error('Diagnosis API error:', error);
      return { success: false, message: '服务连接失败' };
    }
  },
  
  // 获取历史诊断记录
  getDiagnosisHistory: async (userId: string): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/history/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Diagnosis history API error:', error);
      return { success: false, message: '获取历史记录失败', data: [] };
    }
  },
  
  // 获取诊断报告
  getDiagnosisReport: async (diagnosisId: string): Promise<ApiResponse<any>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/diagnostic/report/${diagnosisId}`);
      return response.data;
    } catch (error) {
      console.error('Diagnosis report API error:', error);
      return { success: false, message: '获取诊断报告失败' };
    }
  }
}; 