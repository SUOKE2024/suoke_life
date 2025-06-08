import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { apiClient, ApiResponse, ServiceStatus } from './apiClient';
import {
  API_GATEWAY_CONFIG,
  buildAgentUrl,
  buildDiagnosisUrl,
  buildApiUrl,
  GATEWAY_FEATURES,
  SERVICE_DISCOVERY_CONFIG;
} from '../constants/config';
// 服务接口定义
export interface AuthService {
  login(credentials: { email: string; password: string;)
}): Promise<ApiResponse<any>>;
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
  auth: AuthService = {,
  login: async (credentials) => {
      return apiClient.login(credentials);
    },
    logout: async () => {
      return apiClient.logout();
    },
    register: async (userData) => {
      return apiClient.post("AUTH",/auth/register', userData);
    },
    refreshToken: async () => {
      return apiClient.post("AUTH",/auth/refresh');
    },
    getProfile: async () => {
      return apiClient.get("AUTH",/auth/profile');
    },
    updateProfile: async (data) => {
      return apiClient.put("AUTH",/auth/profile', data);
    },
  };
  // 用户服务
  user: UserService = {,
  getProfile: async () => {
      return apiClient.get("USER",/users/profile');
    },
    updateProfile: async (data) => {
      return apiClient.put("USER",/users/profile', data);
    },
    getSettings: async () => {
      return apiClient.get("USER",/users/settings');
    },
    updateSettings: async (settings) => {
      return apiClient.put("USER",/users/settings', settings);
    },
    getHealthProfile: async () => {
      return apiClient.get("USER",/users/health-profile');
    },
    updateHealthProfile: async (data) => {
      return apiClient.put("USER",/users/health-profile', data);
    },
  };
  // 健康数据服务
  healthData: HealthDataService = {,
  getData: async (params) => {
      const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
      return apiClient.get('HEALTH_DATA', `/health-data${queryString}`);
    },
    addData: async (data) => {
      return apiClient.post("HEALTH_DATA",/health-data', data);
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
  agents: AgentService = {,
  getStatus: async () => {
      return apiClient.get("AGENTS",/agents/status');
    },
    chat: async (message, agentType = 'xiaoai') => {
      return apiClient.post('AGENTS', `/agents/${agentType}/chat`, { message });
    },
    streamChat: async (message, agentType = 'xiaoai') => {
      const url = buildAgentUrl(agentType.toUpperCase(), '/chat/stream');
      const response = await fetch(url, {
      method: "POST",
      headers: {
          'Content-Type': "application/json",Accept': 'text/event-stream',
        },
        body: JSON.stringify({ message }),
      });
      if (!response.ok) {
        throw new Error(`Stream chat failed: ${response.statusText}`);
      }
      return response.body!;
    },
    getPerformance: async () => {
      return apiClient.get("AGENTS",/agents/performance');
    },
    getSettings: async () => {
      return apiClient.get("AGENTS",/agents/settings');
    },
    updateSettings: async (settings) => {
      return apiClient.put("AGENTS",/agents/settings', settings);
    },
  };
  // 四诊服务
  diagnosis: DiagnosisService = {,
  performLookDiagnosis: async (data) => {
      return apiClient.post("DIAGNOSIS",/diagnosis/look', data);
    },
    performListenDiagnosis: async (data) => {
      return apiClient.post("DIAGNOSIS",/diagnosis/listen', data);
    },
    performInquiryDiagnosis: async (data) => {
      return apiClient.post("DIAGNOSIS",/diagnosis/inquiry', data);
    },
    performPalpationDiagnosis: async (data) => {
      return apiClient.post("DIAGNOSIS",/diagnosis/palpation', data);
    },
    getComprehensiveDiagnosis: async (data) => {
      return apiClient.post("DIAGNOSIS",/diagnosis/comprehensive', data);
    },
  };
  // RAG服务
  rag: RAGService = {,
  query: async (question, context) => {
      return apiClient.post("RAG",/rag/query', { question, context });
    },
    streamQuery: async (question, context) => {
      const url = buildApiUrl("RAG",/rag/stream-query');
      const response = await fetch(url, {
      method: "POST",
      headers: {
          'Content-Type': "application/json",Accept': 'text/event-stream',
        },
        body: JSON.stringify({ question, context }),
      });
      if (!response.ok) {
        throw new Error(`Stream query failed: ${response.statusText}`);
      }
      return response.body!;
    },
    multimodalQuery: async (data) => {
      return apiClient.post("RAG",/rag/multimodal-query', data);
    },
    tcmAnalysis: async (symptoms) => {
      return apiClient.post("RAG",/rag/tcm/analysis', { symptoms });
    },
    getHerbRecommendation: async (constitution) => {
      return apiClient.post("RAG",/rag/tcm/herbs', { constitution });
    },
    getSyndromeAnalysis: async (symptoms) => {
      return apiClient.post("RAG",/rag/tcm/syndrome', { symptoms });
    },
    getConstitutionAnalysis: async (data) => {
      return apiClient.post("RAG",/rag/tcm/constitution', data);
    },
  };
  // 区块链服务
  blockchain: BlockchainService = {,
  getRecords: async (userId) => {
      const params = userId ? `?userId=${userId}` : '';
      return apiClient.get('BLOCKCHAIN', `/blockchain/records${params}`);
    },
    addRecord: async (data) => {
      return apiClient.post("BLOCKCHAIN",/blockchain/records', data);
    },
    verifyRecord: async (recordId) => {
      return apiClient.get('BLOCKCHAIN', `/blockchain/verify/${recordId}`);
    },
    mintToken: async (data) => {
      return apiClient.post("BLOCKCHAIN",/blockchain/mint', data);
    },
    transferToken: async (data) => {
      return apiClient.post("BLOCKCHAIN",/blockchain/transfer', data);
    },
  };
  // 服务发现和健康检查
  async getServiceHealth(): Promise<ServiceHealth> {
    try {
      const response = await apiClient.getServices();
      const services = response.data as ServiceStatus[];
            const healthyCount = services.filter(s => s.status === 'healthy').length;
      const totalCount = services.length;
            let overallHealth: 'healthy' | 'degraded' | 'unhealthy';
      if (healthyCount === totalCount) {
        overallHealth = 'healthy';
      } else if (healthyCount > totalCount / 2) {
        overallHealth = 'degraded';
      } else {
        overallHealth = 'unhealthy';
      }
      return {
        services,
        overallHealth,
        lastCheck: new Date().toISOString(),
      };
    } catch (error) {
      return {
        services: [],
        overallHealth: 'unhealthy',
        lastCheck: new Date().toISOString(),
      };
    }
  }
  // 检查特定服务健康状态
  async checkServiceHealth(serviceName: string): Promise<ServiceStatus> {
    try {
      const response = await apiClient.getServiceHealth(serviceName);
      return response.data;
    } catch (error) {
      return {
        name: serviceName,
        status: 'unhealthy',
        instances: 0,
        lastCheck: new Date().toISOString(),
      };
    }
  }
  // 获取网关状态
  async getGatewayStatus() {
    try {
      const isHealthy = await apiClient.healthCheck();
      const cacheStats = apiClient.getCacheStats();
      const circuitBreakerState = apiClient.getCircuitBreakerState();
      return {
        healthy: isHealthy,
        cache: cacheStats,
        circuitBreaker: circuitBreakerState,
        features: GATEWAY_FEATURES,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        healthy: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }
  }
  // 清除缓存
  clearCache(): void {
    apiClient.clearCache();
  }
}
// 创建服务实例
export const integratedApiService = new IntegratedApiService();
// React Context;
interface ApiServiceContextType {
  apiService: IntegratedApiService;
  serviceHealth: ServiceHealth | null;
  isLoading: boolean;
  error: string | null;
  refreshHealth: () => Promise<void>;
}
const ApiServiceContext = createContext<ApiServiceContextType | undefined>(undefined);
// Provider组件
interface ApiServiceProviderProps {
  children: ReactNode;
}
export const ApiServiceProvider: React.FC<ApiServiceProviderProps> = ({ children }) => {
  const [serviceHealth, setServiceHealth] = useState<ServiceHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const refreshHealth = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const health = await integratedApiService.getServiceHealth();
      setServiceHealth(health);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取服务健康状态失败');
    } finally {
      setIsLoading(false);
    }
  };
  useEffect(() => {
    // 初始化时检查服务健康状态
    refreshHealth();
    // 如果启用了服务发现，定期检查健康状态
    if (SERVICE_DISCOVERY_CONFIG.ENABLED) {
      const interval = setInterval(refreshHealth, SERVICE_DISCOVERY_CONFIG.HEALTH_CHECK_INTERVAL);
      return () => clearInterval(interval);
    }
  }, []);
  const value: ApiServiceContextType = {,
  apiService: integratedApiService,
    serviceHealth,
    isLoading,
    error,
    refreshHealth,
  };
  return (
  <ApiServiceContext.Provider value={value}>
      {children}
    </ApiServiceContext.Provider>
  );
};
// Hook;
export const useApiService = (): ApiServiceContextType => {
  const context = useContext(ApiServiceContext);
  if (!context) {
    throw new Error('useApiService must be used within an ApiServiceProvider');
  }
  return context;
};
// 便捷的服务访问hooks;
export const useAuth = () => {
  const { apiService } = useApiService();
  return apiService.auth;
};
export const useUser = () => {
  const { apiService } = useApiService();
  return apiService.user;
};
export const useHealthData = () => {
  const { apiService } = useApiService();
  return apiService.healthData;
};
export const useAgents = () => {
  const { apiService } = useApiService();
  return apiService.agents;
};
export const useDiagnosis = () => {
  const { apiService } = useApiService();
  return apiService.diagnosis;
};
export const useRAG = () => {
  const { apiService } = useApiService();
  return apiService.rag;
};
export const useBlockchain = () => {
  const { apiService } = useApiService();
  return apiService.blockchain;
};
// 服务健康监控Hook;
export const useServiceHealth = () => {
  const { serviceHealth, isLoading, error, refreshHealth } = useApiService();
  return { serviceHealth, isLoading, error, refreshHealth };
};
// 导出默认实例
export default integratedApiService;