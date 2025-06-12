import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { apiClient, ApiResponse, ServiceStatus } from "./apiClient";
import {
  API_GATEWAY_CONFIG,
  buildAgentUrl,
  buildDiagnosisUrl,
  buildApiUrl,
  GATEWAY_FEATURES,
  SERVICE_DISCOVERY_CONFIG,
} from "../constants/config";

// 服务接口定义
export interface AuthService {
  login(credentials: { email: string; password: string }): Promise<ApiResponse<any>>;
  logout(): Promise<ApiResponse<any>>;
  register(userData: any): Promise<ApiResponse<any>>;
  refreshToken(): Promise<ApiResponse<any>>;
  getProfile(): Promise<ApiResponse<any>>;
  updateProfile(data: any): Promise<ApiResponse<any>>;
}

export interface UserService {
  getProfile(): Promise<ApiResponse<any>>;
  updateProfile(data: any): Promise<ApiResponse<any>>;
  getSettings(): Promise<ApiResponse<any>>;
  updateSettings(settings: any): Promise<ApiResponse<any>>;
  getHealthProfile(): Promise<ApiResponse<any>>;
  updateHealthProfile(data: any): Promise<ApiResponse<any>>;
}

export interface HealthDataService {
  getData(params?: any): Promise<ApiResponse<any>>;
  addData(data: any): Promise<ApiResponse<any>>;
  updateData(id: string, data: any): Promise<ApiResponse<any>>;
  deleteData(id: string): Promise<ApiResponse<any>>;
  getMetrics(timeRange?: string): Promise<ApiResponse<any>>;
  exportData(format: string): Promise<ApiResponse<any>>;
  getAnalysis(dataId: string): Promise<ApiResponse<any>>;
}

export interface AgentService {
  getStatus(): Promise<ApiResponse<any>>;
  chat(message: string, agentType?: string): Promise<ApiResponse<any>>;
  streamChat(message: string, agentType?: string): Promise<ReadableStream>;
  getPerformance(): Promise<ApiResponse<any>>;
  getSettings(): Promise<ApiResponse<any>>;
  updateSettings(settings: any): Promise<ApiResponse<any>>;
  // 新增小艾智能体专用接口
  xiaoaiChat(message: string, context?: any): Promise<ApiResponse<any>>;
  xiaoaiDiagnosis(data: any): Promise<ApiResponse<any>>;
  xiaoaiAnalysis(data: any): Promise<ApiResponse<any>>;
}

export interface DiagnosisService {
  performLookDiagnosis(data: any): Promise<ApiResponse<any>>;
  performListenDiagnosis(data: any): Promise<ApiResponse<any>>;
  performInquiryDiagnosis(data: any): Promise<ApiResponse<any>>;
  performPalpationDiagnosis(data: any): Promise<ApiResponse<any>>;
  getComprehensiveDiagnosis(data: any): Promise<ApiResponse<any>>;
}

export interface RAGService {
  query(question: string, context?: any): Promise<ApiResponse<any>>;
  streamQuery(question: string, context?: any): Promise<ReadableStream>;
  multimodalQuery(data: any): Promise<ApiResponse<any>>;
  tcmAnalysis(symptoms: string[]): Promise<ApiResponse<any>>;
  getHerbRecommendation(constitution: string): Promise<ApiResponse<any>>;
  getSyndromeAnalysis(symptoms: any): Promise<ApiResponse<any>>;
  getConstitutionAnalysis(data: any): Promise<ApiResponse<any>>;
}

export interface BlockchainService {
  getRecords(userId?: string): Promise<ApiResponse<any>>;
  addRecord(data: any): Promise<ApiResponse<any>>;
  verifyRecord(recordId: string): Promise<ApiResponse<any>>;
  mintToken(data: any): Promise<ApiResponse<any>>;
  transferToken(data: any): Promise<ApiResponse<any>>;
}

// 服务状态接口
export interface ServiceHealth {
  services: ServiceStatus[];
  overallHealth: 'healthy' | 'degraded' | 'unhealthy';
  lastCheck: string;
}

// 集成API服务实现
export class IntegratedApiService {
  // 认证服务
  auth: AuthService = {
    login: async (credentials) => {
      return apiClient.login(credentials);
    },
    logout: async () => {
      return apiClient.logout();
    },
    register: async (userData) => {
      return apiClient.post('AUTH', '/auth/register', userData);
    },
    refreshToken: async () => {
      return apiClient.post('AUTH', '/auth/refresh');
    },
    getProfile: async () => {
      return apiClient.get('AUTH', '/auth/profile');
    },
    updateProfile: async (data) => {
      return apiClient.put('AUTH', '/auth/profile', data);
    },
  };

  // 用户服务
  user: UserService = {
    getProfile: async () => {
      return apiClient.get('USER', '/users/profile');
    },
    updateProfile: async (data) => {
      return apiClient.put('USER', '/users/profile', data);
    },
    getSettings: async () => {
      return apiClient.get('USER', '/users/settings');
    },
    updateSettings: async (settings) => {
      return apiClient.put('USER', '/users/settings', settings);
    },
    getHealthProfile: async () => {
      return apiClient.get('USER', '/users/health-profile');
    },
    updateHealthProfile: async (data) => {
      return apiClient.put('USER', '/users/health-profile', data);
    },
  };

  // 健康数据服务
  healthData: HealthDataService = {
    getData: async (params) => {
      const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
      return apiClient.get('HEALTH_DATA', `/health-data${queryString}`);
    },
    addData: async (data) => {
      return apiClient.post('HEALTH_DATA', '/health-data', data);
    },
    updateData: async (id, data) => {
      return apiClient.put('HEALTH_DATA', `/health-data/${id}`, data);
    },
    deleteData: async (id) => {
      return apiClient.delete('HEALTH_DATA', `/health-data/${id}`);
    },
    getMetrics: async (timeRange) => {
      const params = timeRange ? `?timeRange=${timeRange}` : '';
      return apiClient.get('HEALTH_DATA', `/health-data/metrics${params}`);
    },
    exportData: async (format) => {
      return apiClient.get('HEALTH_DATA', `/health-data/export?format=${format}`);
    },
    getAnalysis: async (dataId) => {
      return apiClient.get('HEALTH_DATA', `/health-data/${dataId}/analysis`);
    },
  };

  // 智能体服务
  agents: AgentService = {
    getStatus: async () => {
      return apiClient.get('AGENTS', '/agents/status');
    },
    chat: async (message, agentType = 'xiaoai') => {
      try {
        // 根据智能体类型构建不同的API端点
        const endpoint = `/agents/${agentType}/chat`;
        const response = await apiClient.post('AGENTS', endpoint, { 
          message,
          timestamp: new Date().toISOString(),
          sessionId: `session_${Date.now()}`,
          agentType,
        });
        
        return response;
      } catch (error) {
        console.error(`Chat with ${agentType} failed:`, error);
        return {
          success: false,
          message: `与${agentType}聊天失败`,
          data: null,
        };
      }
    },
    streamChat: async (message, agentType = 'xiaoai') => {
      const url = buildAgentUrl(agentType.toUpperCase(), '/chat/stream');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({ message }),
      });
      
      if (!response.ok) {
        throw new Error(`Stream chat failed: ${response.statusText}`);
      }
      
      return response.body!;
    },
    getPerformance: async () => {
      return apiClient.get('AGENTS', '/agents/performance');
    },
    getSettings: async () => {
      return apiClient.get('AGENTS', '/agents/settings');
    },
    updateSettings: async (settings) => {
      return apiClient.put('AGENTS', '/agents/settings', settings);
    },
    // 小艾智能体专用接口
    xiaoaiChat: async (message, context) => {
      try {
        const response = await apiClient.post('AGENTS', '/agents/xiaoai/chat', {
          message,
          context,
          timestamp: new Date().toISOString(),
          sessionId: `xiaoai_session_${Date.now()}`,
        });
        
        // 模拟小艾智能体的响应格式
        if (response.success) {
          return {
            ...response,
            data: {
              response: response.data?.response || `小艾收到您的消息："${message}"，正在为您分析...`,
              confidence: response.data?.confidence || 0.85,
              suggestions: response.data?.suggestions || [
                '您可以告诉我更多症状',
                '需要进行健康检测吗？',
                '我可以为您分析体质',
              ],
              agentType: 'xiaoai',
              timestamp: new Date().toISOString(),
            },
          };
        }
        
        return response;
      } catch (error) {
        console.error('Xiaoai chat failed:', error);
        return {
          success: false,
          message: '与小艾聊天失败',
          data: {
            response: '抱歉，我现在无法回复您的消息。请稍后再试。',
            confidence: 0.0,
            agentType: 'xiaoai',
            timestamp: new Date().toISOString(),
          },
        };
      }
    },
    xiaoaiDiagnosis: async (data) => {
      try {
        return await apiClient.post('AGENTS', '/agents/xiaoai/diagnosis', data);
      } catch (error) {
        console.error('Xiaoai diagnosis failed:', error);
        return {
          success: false,
          message: '小艾诊断服务暂时不可用',
          data: null,
        };
      }
    },
    xiaoaiAnalysis: async (data) => {
      try {
        return await apiClient.post('AGENTS', '/agents/xiaoai/analysis', data);
      } catch (error) {
        console.error('Xiaoai analysis failed:', error);
        return {
          success: false,
          message: '小艾分析服务暂时不可用',
          data: null,
        };
      }
    },
  };

  // 四诊服务
  diagnosis: DiagnosisService = {
    performLookDiagnosis: async (data) => {
      return apiClient.post('DIAGNOSIS', '/diagnosis/look', data);
    },
    performListenDiagnosis: async (data) => {
      return apiClient.post('DIAGNOSIS', '/diagnosis/listen', data);
    },
    performInquiryDiagnosis: async (data) => {
      return apiClient.post('DIAGNOSIS', '/diagnosis/inquiry', data);
    },
    performPalpationDiagnosis: async (data) => {
      return apiClient.post('DIAGNOSIS', '/diagnosis/palpation', data);
    },
    getComprehensiveDiagnosis: async (data) => {
      return apiClient.post('DIAGNOSIS', '/diagnosis/comprehensive', data);
    },
  };

  // RAG服务
  rag: RAGService = {
    query: async (question, context) => {
      return apiClient.post('RAG', '/rag/query', { question, context });
    },
    streamQuery: async (question, context) => {
      const url = buildApiUrl('RAG', '/rag/stream-query');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({ question, context }),
      });
      
      if (!response.ok) {
        throw new Error(`Stream query failed: ${response.statusText}`);
      }
      
      return response.body!;
    },
    multimodalQuery: async (data) => {
      return apiClient.post('RAG', '/rag/multimodal-query', data);
    },
    tcmAnalysis: async (symptoms) => {
      return apiClient.post('RAG', '/rag/tcm-analysis', { symptoms });
    },
    getHerbRecommendation: async (constitution) => {
      return apiClient.get('RAG', `/rag/herb-recommendation?constitution=${constitution}`);
    },
    getSyndromeAnalysis: async (symptoms) => {
      return apiClient.post('RAG', '/rag/syndrome-analysis', { symptoms });
    },
    getConstitutionAnalysis: async (data) => {
      return apiClient.post('RAG', '/rag/constitution-analysis', data);
    },
  };

  // 区块链服务
  blockchain: BlockchainService = {
    getRecords: async (userId) => {
      const params = userId ? `?userId=${userId}` : '';
      return apiClient.get('BLOCKCHAIN', `/blockchain/records${params}`);
    },
    addRecord: async (data) => {
      return apiClient.post('BLOCKCHAIN', '/blockchain/records', data);
    },
    verifyRecord: async (recordId) => {
      return apiClient.get('BLOCKCHAIN', `/blockchain/records/${recordId}/verify`);
    },
    mintToken: async (data) => {
      return apiClient.post('BLOCKCHAIN', '/blockchain/tokens/mint', data);
    },
    transferToken: async (data) => {
      return apiClient.post('BLOCKCHAIN', '/blockchain/tokens/transfer', data);
    },
  };

  // 获取服务健康状态
  async getServiceHealth(): Promise<ServiceHealth> {
    try {
      const response = await apiClient.get('GATEWAY', '/health');
      return response.data;
    } catch (error) {
      console.error('Failed to get service health:', error);
      return {
        services: [],
        overallHealth: 'unhealthy',
        lastCheck: new Date().toISOString(),
      };
    }
  }

  // 测试所有服务连接
  async testConnections(): Promise<Record<string, boolean>> {
    const services = ['AUTH', 'USER', 'HEALTH_DATA', 'AGENTS', 'DIAGNOSIS', 'RAG', 'BLOCKCHAIN'];
    const results: Record<string, boolean> = {};

    await Promise.all(
      services.map(async (service) => {
        try {
          await apiClient.get(service as any, '/health');
          results[service] = true;
        } catch (error) {
          console.error(`Service ${service} connection failed:`, error);
          results[service] = false;
        }
      })
    );

    return results;
  }
}

// 服务上下文
const ApiServiceContext = createContext<IntegratedApiService | null>(null);

// 服务提供者组件
export const ApiServiceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiService] = useState(() => new IntegratedApiService());

  return (
    <ApiServiceContext.Provider value={apiService}>
      {children}
    </ApiServiceContext.Provider>
  );
};

// 使用服务的Hook
export const useApiService = (): IntegratedApiService => {
  const context = useContext(ApiServiceContext);
  if (!context) {
    throw new Error('useApiService must be used within an ApiServiceProvider');
  }
  return context;
};

// 服务健康监控Hook
export const useServiceHealth = () => {
  const [health, setHealth] = useState<ServiceHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const apiService = useApiService();

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await apiService.getServiceHealth();
        setHealth(healthData);
      } catch (error) {
        console.error('Health check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // 每30秒检查一次

    return () => clearInterval(interval);
  }, [apiService]);

  return { health, loading };
};

export default IntegratedApiService;