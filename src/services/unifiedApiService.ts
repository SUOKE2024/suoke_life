import { apiClient, ApiResponse } from "./apiClient";""/;,"/g"/;
import { API_GATEWAY_CONFIG } from "../constants/config";""/;"/g"/;
/* 由 *//;/g/;
*//;,/g/;
export class UnifiedApiService {}}
}
    // ==================== 认证服务 API ====================}";/;,"/g"/;
const async = login(credentials: { email: string; password: string; deviceId?: string; rememberMe?: boolean }) {';}}'';
    return apiClient.post("AUTH",/login', credentials);'}''/;'/g'/;
  }';,'';
const async = register(userData: { username: string; email: string; password: string; phone?: string; deviceId?: string }) {';}}'';
    return apiClient.post("AUTH",/register', userData);'}''/;'/g'/;
  }';,'';
const async = logout() {';}}'';
    return apiClient.post("AUTH",/logout');'}''/;'/g'/;
  }';,'';
const async = refreshToken(refreshToken: string) {'}'';
return apiClient.post("AUTH",/refresh', { refreshToken ;});''/;'/g'/;
  }';,'';
const async = getCurrentUser() {';}}'';
    return apiClient.get("AUTH",/me');'}''/;'/g'/;
  }';,'';
const async = forgotPassword(email: string) {'}'';
return apiClient.post("AUTH",/forgot-password', { email ;});''/;'/g'/;
  }';,'';
const async = resetPassword(data: { email: string; code: string; newPassword: string ;}) {';}}'';
    return apiClient.post("AUTH",/reset-password', data);'}''/;'/g'/;
  }';,'';
async: changePassword(oldPassword: string, newPassword: string) {'}'';
return apiClient.post("AUTH",/change-password', { oldPassword, newPassword ;});''/;'/g'/;
  }';,'';
const async = verifyPassword(password: string) {'}'';
return apiClient.post("AUTH",/verify-password', { password ;});''/;'/g'/;
  }';,'';
const async = checkEmailExists(email: string) {'}'';
return apiClient.get('AUTH', `/check-email?email=${encodeURIComponent(email);}`);```/`;`/g`/`;
  }';,'';
const async = checkUsernameExists(username: string) {'}'';
return apiClient.get('AUTH', `/check-username?username=${encodeURIComponent(username);}`);```/`;`/g`/`;
  }
  // ==================== 用户服务 API ===================='/;,'/g'/;
const async = getUserProfile(userId?: string) {'}'';
const endpoint = userId ? `/profile/${userId}` : '/profile';'/`;,`/g`/`;
return apiClient.get('USER', endpoint);';'';
  }';,'';
const async = updateUserProfile(profileData: any) {';}}'';
    return apiClient.put("USER",/profile', profileData);'}''/;'/g'/;
  }';,'';
const async = getUserSettings() {';}}'';
    return apiClient.get("USER",/settings');'}''/;'/g'/;
  }';,'';
const async = updateUserSettings(settings: any) {';}}'';
    return apiClient.put("USER",/settings', settings);'}''/;'/g'/;
  }';,'';
const async = getUserPreferences() {';}}'';
    return apiClient.get("USER",/preferences');'}''/;'/g'/;
  }';,'';
const async = updateUserPreferences(preferences: any) {';}}'';
    return apiClient.put("USER",/preferences', preferences);'}''/;'/g'/;
  }';,'';
const async = getHealthProfile() {';}}'';
    return apiClient.get("USER",/health-profile');'}''/;'/g'/;
  }';,'';
const async = updateHealthProfile(healthProfile: any) {';}}'';
    return apiClient.put("USER",/health-profile', healthProfile);'}''/;'/g'/;
  }
  // ==================== 健康数据服务 API ====================/;,/g/;
const async = getHealthData(params?: { type?: string; startDate?: string; endDate?: string; limit?: number }) {const queryParams = new URLSearchParams();,}if (params) {Object.entries(params).forEach([key, value]) => {}        if (value !== undefined) {}}
          queryParams.append(key, value.toString());}
        }
      });';'';
    }';,'';
const endpoint = queryParams.toString() ? `/data?${queryParams.toString()}` : '/data';'/`;,`/g`/`;
return apiClient.get('HEALTH_DATA', endpoint);';'';
  }';,'';
const async = addHealthData(data: any) {';}}'';
    return apiClient.post("HEALTH_DATA",/data', data);'}''/;'/g'/;
  }';,'';
const async = addHealthDataBatch(dataList: any[]) {'}'';
return apiClient.post("HEALTH_DATA",/data/batch', { data: dataList ;});''/;'/g'/;
  }';,'';
async: updateHealthData(id: string, updates: any) {'}'';
return apiClient.put('HEALTH_DATA', `/data/${id;}`, updates);```/`;`/g`/`;
  }';,'';
const async = deleteHealthData(id: string) {'}'';
return apiClient.delete('HEALTH_DATA', `/data/${id;}`);```/`;`/g`/`;
  }';,'';
const async = getHealthMetrics(timeRange: string) {'}'';
return apiClient.get('HEALTH_DATA', `/metrics?timeRange=${timeRange;}`);``'/`;`/g`/`;
  }';,'';
const async = exportHealthData(format: string = 'json') {'}'';
return apiClient.get('HEALTH_DATA', `/export?format=${format;}`);```/`;`/g`/`;
  }';,'';
const async = syncHealthData() {';}}'';
    return apiClient.get("HEALTH_DATA",/sync');'}''/;'/g'/;
  }
  // ==================== 智能体服务 API ===================='/;,'/g'/;
const async = getAgentStatus(agentId?: string) {'}'';
const endpoint = agentId ? `/status/${agentId}` : '/status';'/`;,`/g`/`;
return apiClient.get('AGENTS', endpoint);';'';
  }';,'';
async: startAgentChat(agentId: string, userId: string) {'}'';
return apiClient.post("AGENTS",/chat/start', { agentId, userId ;});''/;'/g'/;
  }';,'';
async: sendAgentMessage(sessionId: string, message: string, type: string = 'text') {'}'';
return apiClient.post("AGENTS",/chat/message', { sessionId, message, type ;});''/;'/g'/;
  }';,'';
const async = endAgentChat(sessionId: string) {'}'';
return apiClient.post("AGENTS",/chat/end', { sessionId ;});''/;'/g'/;
  }';,'';
const async = getAgentPerformance(agentId?: string) {'}'';
const endpoint = agentId ? `/performance/${agentId}` : '/performance';'/`;,`/g`/`;
return apiClient.get('AGENTS', endpoint);';'';
  }';,'';
async: updateAgentSettings(agentId: string, settings: any) {'}'';
return apiClient.put('AGENTS', `/settings/${agentId;}`, settings);```/`;`/g`/`;
  }
  // ==================== 五诊服务 API (原四诊升级) ====================/;/g/;
    // 传统四诊方法'/;,'/g'/;
const async = performLookDiagnosis(imageData: any) {';}}'';
    return apiClient.post("DIAGNOSIS",/look', imageData);'}''/;'/g'/;
  }';,'';
const async = performListenDiagnosis(audioData: any) {';}}'';
    return apiClient.post("DIAGNOSIS",/listen', audioData);'}''/;'/g'/;
  }';,'';
const async = performInquiryDiagnosis(inquiryData: any) {';}}'';
    return apiClient.post("DIAGNOSIS",/inquiry', inquiryData);'}''/;'/g'/;
  }';,'';
const async = performPalpationDiagnosis(palpationData: any) {';}}'';
    return apiClient.post("DIAGNOSIS",/palpation', palpationData);'}''/;'/g'/;
  }
  // 新增算诊方法 (第五诊)'/;,'/g'/;
const async = performCalculationDiagnosis(calculationData: any) {';}}'';
    return apiClient.post("DIAGNOSIS",/calculation', calculationData);'}''/;'/g'/;
  }
  // 算诊专用方法'/;,'/g'/;
const async = performZiwuAnalysis(birthData: { birthTime: string; currentTime?: string }) {';}}'';
    return apiClient.post("DIAGNOSIS",/ziwu', birthData);'}''/;'/g'/;
  }
  async: performConstitutionAnalysis(personalData: {))}birthYear: number,;
birthMonth: number,;
birthDay: number,;
birthHour: number,;
const gender = string;
}
    location?: string;}';'';
  }) {';}}'';
    return apiClient.post("DIAGNOSIS",/constitution', personalData);'}''/;'/g'/;
  }
  async: performBaguaAnalysis(baguaData: {))}birthDate: string,;
const gender = string;
}
    question?: string;}';'';
  }) {';}}'';
    return apiClient.post("DIAGNOSIS",/bagua', baguaData);'}''/;'/g'/;
  }
  async: performWuyunAnalysis(timeData: {))}year: number,;
month: number,;
const day = number;
}
    location?: string;}';'';
  }) {';}}'';
    return apiClient.post("DIAGNOSIS",/wuyun', timeData);'}''/;'/g'/;
  }
  async: performCalculationComprehensive(comprehensiveData: {))}const personalInfo = any;
healthData?: any;
}
    preferences?: any;}';'';
  }) {';}}'';
    return apiClient.post("DIAGNOSIS",/calculationComprehensive', comprehensiveData);'}''/;'/g'/;
  }
  // 五诊综合分析/;,/g/;
const async = performFiveDiagnosisComprehensive(fiveDiagnosisData: {)lookData?: any;,}listenData?: any;
inquiryData?: any;
palpationData?: any;
calculationData?: any;);
const userId = string;);
}
    sessionId?: string;)}';'';
  }) {';}}'';
    return apiClient.post("DIAGNOSIS",/fiveDiagnosis', fiveDiagnosisData);'}''/;'/g'/;
  }';,'';
const async = getComprehensiveDiagnosis(diagnosisId: string) {'}'';
return apiClient.get('DIAGNOSIS', `/comprehensive/${diagnosisId;}`);```/`;`/g`/`;
  }';,'';
const async = getDiagnosisHistory(userId?: string) {'}'';
const endpoint = userId ? `/history/${userId}` : '/history';'/`;,`/g`/`;
return apiClient.get('DIAGNOSIS', endpoint);';'';
  }
  // ==================== RAG服务 API ===================='/;,'/g,'/;
  async: queryRAG(query: string, context?: any) {'}'';
return apiClient.post("RAG";/query', { query, context });''/;'/g'/;
  }';,'';
async: streamQueryRAG(query: string, context?: any) {'}'';
return apiClient.post("RAG";/stream-query', { query, context });''/;'/g'/;
  }';,'';
async: multimodalQueryRAG(query: string, files?: any[]; context?: any) {'}'';
return apiClient.post("RAG";/multimodal-query', { query, files, context });''/;'/g'/;
  }';,'';
async: getTCMAnalysis(symptoms: string[], constitution?: string) {'}'';
return apiClient.post("RAG";/tcm/analysis', { symptoms, constitution });''/;'/g'/;
  }';,'';
async: getHerbRecommendation(constitution: string, symptoms: string[]) {'}'';
return apiClient.post("RAG",/tcm/herbs', { constitution, symptoms ;});''/;'/g'/;
  }';,'';
const async = getSyndromeAnalysis(symptoms: string[]) {'}'';
return apiClient.post("RAG",/tcm/syndrome', { symptoms ;});''/;'/g'/;
  }';,'';
const async = getConstitutionAnalysis(userData: any) {';}}'';
    return apiClient.post("RAG",/tcm/constitution', userData);'}''/;'/g'/;
  }
  // ==================== 区块链服务 API ===================='/;,'/g'/;
const async = getBlockchainRecords(userId?: string) {'}'';
const endpoint = userId ? `/records/${userId}` : '/records';'/`;,`/g`/`;
return apiClient.get('BLOCKCHAIN', endpoint);';'';
  }';,'';
const async = verifyRecord(recordId: string) {'}'';
return apiClient.post("BLOCKCHAIN",/verify', { recordId ;});''/;'/g'/;
  }';,'';
const async = mintHealthNFT(healthData: any) {';}}'';
    return apiClient.post("BLOCKCHAIN",/mint', healthData);'}''/;'/g'/;
  }';,'';
async: transferHealthNFT(tokenId: string, toAddress: string) {'}'';
return apiClient.post("BLOCKCHAIN",/transfer', { tokenId, toAddress ;});''/;'/g'/;
  }
  // ==================== 消息总线服务 API ===================='/;,'/g,'/;
  async: publishMessage(topic: string, message: any) {'}'';
return apiClient.post("MESSAGE_BUS",/publish', { topic, message ;});''/;'/g'/;
  }';,'';
async: subscribeToTopic(topic: string, callback: string) {'}'';
return apiClient.post("MESSAGE_BUS",/subscribe', { topic, callback ;});''/;'/g'/;
  }';,'';
async: createTopic(topicName: string, config?: any) {'}'';
return apiClient.post("MESSAGE_BUS";/topics', { name: topicName, config ;});''/;'/g'/;
  }';,'';
const async = getTopics() {';}}'';
    return apiClient.get("MESSAGE_BUS",/topics');'}''/;'/g'/;
  }
  // ==================== 其他服务 API ====================/;,/g/;
const async = getMedicalResources(location?: string; type?: string) {';,}const params = new URLSearchParams();';,'';
if (location) params.append('location', location);';'';
}
    if (type) params.append('type', type);'}'';
const endpoint = params.toString() ? `/resources?${params.toString()}` : '/resources';'/`;,`/g`/`;
return apiClient.get('MEDICAL_RESOURCE', endpoint);';'';
  }';,'';
const async = getCornMazeStatus() {';}}'';
    return apiClient.get("CORN_MAZE",/status');'}''/;'/g'/;
  }';,'';
const async = startCornMazeGame(difficulty: string) {'}'';
return apiClient.post("CORN_MAZE",/start', { difficulty ;});''/;'/g'/;
  }';,'';
const async = getAccessibilitySettings() {';}}'';
    return apiClient.get("ACCESSIBILITY",/settings');'}''/;'/g'/;
  }';,'';
const async = updateAccessibilitySettings(settings: any) {';}}'';
    return apiClient.put("ACCESSIBILITY",/settings', settings);'}''/;'/g'/;
  }';,'';
const async = runBenchmark(config: any) {';}}'';
    return apiClient.post("SUOKE_BENCH",/run', config);'}''/;'/g'/;
  }';,'';
const async = getBenchmarkResults(benchmarkId?: string) {'}'';
const endpoint = benchmarkId ? `/results/${benchmarkId}` : '/results';'/`;,`/g`/`;
return apiClient.get('SUOKE_BENCH', endpoint);';'';
  }
  // ==================== 网关管理 API ===================='/;,'/g'/;
const async = getGatewayStatus() {';}}'';
    return apiClient.get("",/health');'}''/;'/g'/;
  }';,'';
const async = getServiceHealth(serviceName?: string) {'}'';
const endpoint = serviceName ? `/services/${serviceName}/health` : '/services';'/`;,`/g`/`;
return apiClient.get(', endpoint);'';'';
  }';,'';
const async = getGatewayMetrics() {';}}'';
    return apiClient.get("",/metrics');'}''/;'/g'/;
  }';,'';
const async = getGatewayConfig() {';}}'';
    return apiClient.get("",/config');'}''/;'/g'/;
  }
  // ==================== 工具方法 ====================/;/g/;
    /* ' *//;'/g'/;
  */'/;,'/g'/;
const async = batchRequest(requests: Array<{ service: string; endpoint: string; method: 'GET' | 'POST' | 'PUT' | 'DELETE'; data?: any }>) {';,}const  promises = useMemo(() => requests.map(req => {)';,}switch (req.method) {';,}case 'GET': ';,'';
return apiClient.get(req.service, req.endpoint);';,'';
case 'POST': ';,'';
return apiClient.post(req.service, req.endpoint, req.data);';,'';
case 'PUT': ';,'';
return apiClient.put(req.service, req.endpoint, req.data);';,'';
case 'DELETE': ';,'';
return apiClient.delete(req.service, req.endpoint), []);
}
        const default = }
          const throw = new Error(`Unsupported method: ${req.method;}`);````;```;
      }
    });
return Promise.allSettled(promises);
  }
  /* 务 *//;/g/;
  *//;,/g/;
const async = healthCheckAllServices() {const services = Object.keys(API_GATEWAY_CONFIG.SERVICES);}}
    const  healthChecks = useMemo(() => services.map(service =>)}
      this.getServiceHealth(service).catch(error => ({ service, error: error.message ;}), []));
    );
return Promise.allSettled(healthChecks);
  }
  /* 息 *//;/g/;
  *//;,/g/;
const async = getApiStats() {return {}      cacheStats: apiClient.getCacheStats(),;
}
      circuitBreakerState: apiClient.getCircuitBreakerState(),}
      const gatewayHealth = await apiClient.healthCheck();};
  }
}
// 导出单例实例/;,/g/;
export const unifiedApiService = new UnifiedApiService();';,'';
export default unifiedApiService;