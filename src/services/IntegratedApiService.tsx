import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";";
import { apiClient, ApiResponse, ServiceStatus } from "./apiClient";""/;,"/g"/;
import {;,}API_GATEWAY_CONFIG,;
buildAgentUrl,;
buildDiagnosisUrl,;
buildApiUrl,;
GATEWAY_FEATURES,";"";
}
  SERVICE_DISCOVERY_CONFIG;'}'';'';
} from "../constants/config";""/;"/g"/;
// 服务接口定义/;,/g/;
export interface AuthService {;}}
}
  login(credentials: { email: string; password: string;)}
}): Promise<ApiResponse<any>>;
logout(): Promise<ApiResponse<any>>;
register(userData: any): Promise<ApiResponse<any>>;
refreshToken(): Promise<ApiResponse<any>>;
getProfile(): Promise<ApiResponse<any>>;
updateProfile(data: any): Promise<ApiResponse<any>>;
}
export interface UserService {;,}getProfile(): Promise<ApiResponse<any>>;
updateProfile(data: any): Promise<ApiResponse<any>>;
getSettings(): Promise<ApiResponse<any>>;
updateSettings(settings: any): Promise<ApiResponse<any>>;
getHealthProfile(): Promise<ApiResponse<any>>;
}
}
  updateHealthProfile(data: any): Promise<ApiResponse<any>>;}
}
export interface HealthDataService {;,}getData(params?: any): Promise<ApiResponse<any>>;
addData(data: any): Promise<ApiResponse<any>>;
updateData(id: string, data: any): Promise<ApiResponse<any>>;
deleteData(id: string): Promise<ApiResponse<any>>;
getMetrics(timeRange?: string): Promise<ApiResponse<any>>;
exportData(format: string): Promise<ApiResponse<any>>;
}
}
  getAnalysis(dataId: string): Promise<ApiResponse<any>>;}
}
export interface AgentService {;,}getStatus(): Promise<ApiResponse<any>>;
chat(message: string, agentType?: string): Promise<ApiResponse<any>>;
streamChat(message: string, agentType?: string): Promise<ReadableStream>;
getPerformance(): Promise<ApiResponse<any>>;
getSettings(): Promise<ApiResponse<any>>;
}
}
  updateSettings(settings: any): Promise<ApiResponse<any>>;}
}
export interface DiagnosisService {;,}performLookDiagnosis(data: any): Promise<ApiResponse<any>>;
performListenDiagnosis(data: any): Promise<ApiResponse<any>>;
performInquiryDiagnosis(data: any): Promise<ApiResponse<any>>;
performPalpationDiagnosis(data: any): Promise<ApiResponse<any>>;
}
}
  getComprehensiveDiagnosis(data: any): Promise<ApiResponse<any>>;}
}
export interface RAGService {;,}query(question: string, context?: any): Promise<ApiResponse<any>>;
streamQuery(question: string, context?: any): Promise<ReadableStream>;
multimodalQuery(data: any): Promise<ApiResponse<any>>;
tcmAnalysis(symptoms: string[]): Promise<ApiResponse<any>>;
getHerbRecommendation(constitution: string): Promise<ApiResponse<any>>;
getSyndromeAnalysis(symptoms: any): Promise<ApiResponse<any>>;
}
}
  getConstitutionAnalysis(data: any): Promise<ApiResponse<any>>;}
}
export interface BlockchainService {;,}getRecords(userId?: string): Promise<ApiResponse<any>>;
addRecord(data: any): Promise<ApiResponse<any>>;
verifyRecord(recordId: string): Promise<ApiResponse<any>>;
mintToken(data: any): Promise<ApiResponse<any>>;
}
}
  transferToken(data: any): Promise<ApiResponse<any>>;}
}
// 服务状态接口/;,/g/;
export interface ServiceHealth {';,}services: ServiceStatus[],';,'';
overallHealth: 'healthy' | 'degraded' | 'unhealthy';','';'';
}
}
  const lastCheck = string;}
}
// 集成API服务实现/;,/g/;
export class IntegratedApiService {// 认证服务/;,}auth: AuthService = {login: async (credentials) => {;}}/g/;
}
      return apiClient.login(credentials);}
    }
logout: async () => {}}
      return apiClient.logout();}
    },';,'';
register: async (userData) => {';}}'';
      return apiClient.post("AUTH",/auth/register', userData);'}''/;'/g'/;
    },';,'';
refreshToken: async () => {';}}'';
      return apiClient.post("AUTH",/auth/refresh');'}''/;'/g'/;
    },';,'';
getProfile: async () => {';}}'';
      return apiClient.get("AUTH",/auth/profile');'}''/;'/g'/;
    },';,'';
updateProfile: async (data) => {';}}'';
      return apiClient.put("AUTH",/auth/profile', data);'}''/;'/g'/;
    }};
  // 用户服务/;,/g,/;
  user: UserService = {,';,}getProfile: async () => {';}}'';
      return apiClient.get("USER",/users/profile');'}''/;'/g'/;
    },';,'';
updateProfile: async (data) => {';}}'';
      return apiClient.put("USER",/users/profile', data);'}''/;'/g'/;
    },';,'';
getSettings: async () => {';}}'';
      return apiClient.get("USER",/users/settings');'}''/;'/g'/;
    },';,'';
updateSettings: async (settings) => {';}}'';
      return apiClient.put("USER",/users/settings', settings);'}''/;'/g'/;
    },';,'';
getHealthProfile: async () => {';}}'';
      return apiClient.get("USER",/users/health-profile');'}''/;'/g'/;
    },';,'';
updateHealthProfile: async (data) => {';}}'';
      return apiClient.put("USER",/users/health-profile', data);'}''/;'/g'/;
    }};
  // 健康数据服务/;,/g,/;
  healthData: HealthDataService = {,';}}'';
  getData: async (params) => {'}'';
const queryString = params ? `?${new URLSearchParams(params).toString();}` : ';''`;,```;
return apiClient.get('HEALTH_DATA', `/health-data${queryString}`);```/`;`/g`/`;
    },';,'';
addData: async (data) => {';}}'';
      return apiClient.post("HEALTH_DATA",/health-data', data);'}''/;'/g'/;
    },';,'';
updateData: async (id, data) => {'}'';
return apiClient.put('HEALTH_DATA', `/health-data/${id;}`, data);```/`;`/g`/`;
    },';,'';
deleteData: async (id) => {'}'';
return apiClient.delete('HEALTH_DATA', `/health-data/${id;}`);```/`;`/g`/`;
    },';,'';
getMetrics: async (timeRange) => {'}'';
const params = timeRange ? `?timeRange=${timeRange;}` : ';''`;,```;
return apiClient.get('HEALTH_DATA', `/health-data/metrics${params}`);```/`;`/g`/`;
    },';,'';
exportData: async (format) => {'}'';
return apiClient.get('HEALTH_DATA', `/health-data/export?format=${format;}`);```/`;`/g`/`;
    },';,'';
getAnalysis: async (dataId) => {'}'';
return apiClient.get('HEALTH_DATA', `/health-data/${dataId;}/analysis`);```/`;`/g`/`;
    }};
  // 智能体服务/;,/g,/;
  agents: AgentService = {,';,}getStatus: async () => {';}}'';
      return apiClient.get("AGENTS",/agents/status');'}'/;'/g'/;
    },';,'';
chat: async (message, agentType = 'xiaoai') => {'}'';
return apiClient.post('AGENTS', `/agents/${agentType;}/chat`, { message });``'/`;`/g`/`;
    },';,'';
streamChat: async (message, agentType = 'xiaoai') => {';,}url: buildAgentUrl(agentType.toUpperCase(), '/chat/stream');'/;,'/g,'/;
  const: response = await fetch(url, {';,)method: "POST";",")";}}"";
      const headers = {)"}"";"";
          'Content-Type': "application/json",Accept': 'text/event-stream';},')'/;,'/g'/;
const body = JSON.stringify({ message ;})});
if (!response.ok) {}
        const throw = new Error(`Stream chat failed: ${response.statusText;}`);````;```;
      }
      return response.body!;
    },';,'';
getPerformance: async () => {';}}'';
      return apiClient.get("AGENTS",/agents/performance');'}''/;'/g'/;
    },';,'';
getSettings: async () => {';}}'';
      return apiClient.get("AGENTS",/agents/settings');'}''/;'/g'/;
    },';,'';
updateSettings: async (settings) => {';}}'';
      return apiClient.put("AGENTS",/agents/settings', settings);'}''/;'/g'/;
    }};
  // 四诊服务/;,/g,/;
  diagnosis: DiagnosisService = {,';,}performLookDiagnosis: async (data) => {';}}'';
      return apiClient.post("DIAGNOSIS",/diagnosis/look', data);'}''/;'/g'/;
    },';,'';
performListenDiagnosis: async (data) => {';}}'';
      return apiClient.post("DIAGNOSIS",/diagnosis/listen', data);'}''/;'/g'/;
    },';,'';
performInquiryDiagnosis: async (data) => {';}}'';
      return apiClient.post("DIAGNOSIS",/diagnosis/inquiry', data);'}''/;'/g'/;
    },';,'';
performPalpationDiagnosis: async (data) => {';}}'';
      return apiClient.post("DIAGNOSIS",/diagnosis/palpation', data);'}''/;'/g'/;
    },';,'';
getComprehensiveDiagnosis: async (data) => {';}}'';
      return apiClient.post("DIAGNOSIS",/diagnosis/comprehensive', data);'}''/;'/g'/;
    }};
  // RAG服务/;,/g,/;
  rag: RAGService = {,';}}'';
  query: async (question, context) => {'}'';
return apiClient.post("RAG",/rag/query', { question, context ;});''/;'/g'/;
    },';,'';
streamQuery: async (question, context) => {';,}url: buildApiUrl("RAG",/rag/stream-query');''/;,'/g,'/;
  const: response = await fetch(url, {';,)method: "POST";",")";}}"";
      const headers = {)"}"";"";
          'Content-Type': "application/json",Accept': 'text/event-stream';},')'/;,'/g,'/;
  body: JSON.stringify({ question, context ;})});
if (!response.ok) {}
        const throw = new Error(`Stream query failed: ${response.statusText;}`);````;```;
      }
      return response.body!;
    },';,'';
multimodalQuery: async (data) => {';}}'';
      return apiClient.post("RAG",/rag/multimodal-query', data);'}''/;'/g'/;
    },';,'';
tcmAnalysis: async (symptoms) => {'}'';
return apiClient.post("RAG",/rag/tcm/analysis', { symptoms ;});''/;'/g'/;
    },';,'';
getHerbRecommendation: async (constitution) => {'}'';
return apiClient.post("RAG",/rag/tcm/herbs', { constitution ;});''/;'/g'/;
    },';,'';
getSyndromeAnalysis: async (symptoms) => {'}'';
return apiClient.post("RAG",/rag/tcm/syndrome', { symptoms ;});''/;'/g'/;
    },';,'';
getConstitutionAnalysis: async (data) => {';}}'';
      return apiClient.post("RAG",/rag/tcm/constitution', data);'}''/;'/g'/;
    }};
  // 区块链服务/;,/g,/;
  blockchain: BlockchainService = {,';}}'';
  getRecords: async (userId) => {'}'';
const params = userId ? `?userId=${userId;}` : ';''`;,```;
return apiClient.get('BLOCKCHAIN', `/blockchain/records${params}`);```/`;`/g`/`;
    },';,'';
addRecord: async (data) => {';}}'';
      return apiClient.post("BLOCKCHAIN",/blockchain/records', data);'}''/;'/g'/;
    },';,'';
verifyRecord: async (recordId) => {'}'';
return apiClient.get('BLOCKCHAIN', `/blockchain/verify/${recordId;}`);```/`;`/g`/`;
    },';,'';
mintToken: async (data) => {';}}'';
      return apiClient.post("BLOCKCHAIN",/blockchain/mint', data);'}''/;'/g'/;
    },';,'';
transferToken: async (data) => {';}}'';
      return apiClient.post("BLOCKCHAIN",/blockchain/transfer', data);'}''/;'/g'/;
    }};
  // 服务发现和健康检查/;,/g/;
const async = getServiceHealth(): Promise<ServiceHealth> {try {}      const response = await apiClient.getServices();';,'';
const services = response.data as ServiceStatus[];';,'';
const healthyCount = services.filter(s => s.status === 'healthy').length;';,'';
const totalCount = services.length;';,'';
const let = overallHealth: 'healthy' | 'degraded' | 'unhealthy';';,'';
if (healthyCount === totalCount) {';}}'';
        overallHealth = 'healthy';'}'';'';
      } else if (healthyCount > totalCount / 2) {/;}';'/g'/;
}
        overallHealth = 'degraded';'}'';'';
      } else {';}}'';
        overallHealth = 'unhealthy';'}'';'';
      }
      return {services,;}}
        overallHealth,}
        const lastCheck = new Date().toISOString();};
    } catch (error) {return {';,}services: [],';'';
}
        overallHealth: 'unhealthy';',}'';
const lastCheck = new Date().toISOString();};
    }
  }
  // 检查特定服务健康状态/;,/g/;
const async = checkServiceHealth(serviceName: string): Promise<ServiceStatus> {try {}      const response = await apiClient.getServiceHealth(serviceName);
}
      return response.data;}
    } catch (error) {return {';,}name: serviceName,';,'';
status: 'unhealthy';','';'';
}
        instances: 0,}
        const lastCheck = new Date().toISOString();};
    }
  }
  // 获取网关状态/;,/g/;
const async = getGatewayStatus() {try {}      const isHealthy = await apiClient.healthCheck();
const cacheStats = apiClient.getCacheStats();
const circuitBreakerState = apiClient.getCircuitBreakerState();
return {healthy: isHealthy}cache: cacheStats,;
circuitBreaker: circuitBreakerState,;
}
        features: GATEWAY_FEATURES,}
        const timestamp = new Date().toISOString();};
    } catch (error) {return {';,}healthy: false,';'';
}
        error: error instanceof Error ? error.message : 'Unknown error';',}'';
const timestamp = new Date().toISOString();};
    }
  }
  // 清除缓存/;,/g/;
clearCache(): void {}}
    apiClient.clearCache();}
  }
}
// 创建服务实例/;,/g/;
export const integratedApiService = new IntegratedApiService();
// React Context;/;,/g/;
interface ApiServiceContextType {apiService: IntegratedApiService}serviceHealth: ServiceHealth | null,;
isLoading: boolean,;
error: string | null,;
}
}
  refreshHealth: () => Promise<void>;}
}
const ApiServiceContext = createContext<ApiServiceContextType | undefined>(undefined);
// Provider组件/;,/g/;
interface ApiServiceProviderProps {}}
}
  const children = ReactNode;}
}
export const ApiServiceProvider: React.FC<ApiServiceProviderProps> = ({ children ;}) => {const [serviceHealth, setServiceHealth] = useState<ServiceHealth | null>(null);,}const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const  refreshHealth = async () => {try {}      setIsLoading(true);
setError(null);
const health = await integratedApiService.getServiceHealth();
}
      setServiceHealth(health);}
    } catch (err) {}}
}
    } finally {}}
      setIsLoading(false);}
    }
  };
useEffect() => {// 初始化时检查服务健康状态/;,}refreshHealth();/g/;
    // 如果启用了服务发现，定期检查健康状态/;,/g/;
if (SERVICE_DISCOVERY_CONFIG.ENABLED) {interval: setInterval(refreshHealth, SERVICE_DISCOVERY_CONFIG.HEALTH_CHECK_INTERVAL);}}
      return () => clearInterval(interval);}
    }
  }, []);
const: value: ApiServiceContextType = {const apiService = integratedApiService;
serviceHealth,;
isLoading,;
}
    error,}
    refreshHealth};
return (<ApiServiceContext.Provider value={value}>);
      {children});
    </ApiServiceContext.Provider>)/;/g/;
  );
};
// Hook;/;,/g/;
export const useApiService = (): ApiServiceContextType => {;,}const context = useContext(ApiServiceContext);';,'';
if (!context) {';}}'';
    const throw = new Error('useApiService must be used within an ApiServiceProvider');'}'';'';
  }
  return context;
};
// 便捷的服务访问hooks;/;,/g/;
export const useAuth = useCallback(() => {};
const { apiService } = useApiService();
return apiService.auth;
};
export const useUser = useCallback(() => {};
const { apiService } = useApiService();
return apiService.user;
};
export const useHealthData = useCallback(() => {};
const { apiService } = useApiService();
return apiService.healthData;
};
export const useAgents = useCallback(() => {};
const { apiService } = useApiService();
return apiService.agents;
};
export const useDiagnosis = useCallback(() => {};
const { apiService } = useApiService();
return apiService.diagnosis;
};
export const useRAG = useCallback(() => {};
const { apiService } = useApiService();
return apiService.rag;
};
export const useBlockchain = useCallback(() => {};
const { apiService } = useApiService();
return apiService.blockchain;
};
// 服务健康监控Hook;/;,/g/;
export const useServiceHealth = useCallback(() => {};
const { serviceHealth, isLoading, error, refreshHealth } = useApiService();
return { serviceHealth, isLoading, error, refreshHealth };
};
// 导出默认实例'/;,'/g'/;
export default integratedApiService;