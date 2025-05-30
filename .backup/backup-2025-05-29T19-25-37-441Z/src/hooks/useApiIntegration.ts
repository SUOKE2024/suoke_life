import { useState, useEffect, useCallback, useRef } from 'react';
import { apiIntegrationService } from '../services/ApiIntegrationService';

// Hook状态接口
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  success: boolean;
}

// Hook配置接口
interface UseApiIntegrationConfig {
  autoFetch?: boolean;
  retryCount?: number;
  retryDelay?: number;
  cacheTime?: number;
}

export const useApiIntegration = <T = any>(config: UseApiIntegrationConfig = {}) => {
  const {
    autoFetch = false,
    retryCount = 3,
    retryDelay = 1000,
    cacheTime = 5 * 60 * 1000, // 5分钟
  } = config;

  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
    success: false,
  });

  const retryCountRef = useRef(0);
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());

  // 重置状态
  const resetState = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      success: false,
    });
    retryCountRef.current = 0;
  }, []);

  // 设置加载状态
  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  }, []);

  // 设置错误状态
  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error, loading: false, success: false }));
  }, []);

  // 设置成功状态
  const setSuccess = useCallback((data: T) => {
    setState({
      data,
      loading: false,
      error: null,
      success: true,
    });
  }, []);

  // 缓存管理
  const getCachedData = useCallback((key: string) => {
    const cached = cacheRef.current.get(key);
    if (cached && Date.now() - cached.timestamp < cacheTime) {
      return cached.data;
    }
    return null;
  }, [cacheTime]);

  const setCachedData = useCallback((key: string, data: any) => {
    cacheRef.current.set(key, {
      data,
      timestamp: Date.now(),
    });
  }, []);

  // 通用API请求方法
  const executeRequest = useCallback(async <R = T>(
    requestFn: () => Promise<R>,
    cacheKey?: string
  ): Promise<R | null> => {
    try {
      // 检查缓存
      if (cacheKey) {
        const cachedData = getCachedData(cacheKey);
        if (cachedData) {
          setSuccess(cachedData);
          return cachedData;
        }
      }

      setLoading(true);
      setError(null);

      const result = await requestFn();

      // 缓存结果
      if (cacheKey) {
        setCachedData(cacheKey, result);
      }

      setSuccess(result as T);
      retryCountRef.current = 0;
      return result;
    } catch (error: any) {
      console.error('API请求失败:', error);

      // 重试逻辑
      if (retryCountRef.current < retryCount) {
        retryCountRef.current++;
        setTimeout(() => {
          executeRequest(requestFn, cacheKey);
        }, retryDelay * retryCountRef.current);
        return null;
      }

      setError(error.message || '请求失败');
      return null;
    }
  }, [retryCount, retryDelay, getCachedData, setCachedData, setLoading, setError, setSuccess]);

  // ==================== 认证相关方法 ====================

  const login = useCallback(async (credentials: { username: string; password: string }) => {
    return executeRequest(() => apiIntegrationService.login(credentials));
  }, [executeRequest]);

  const logout = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.logout());
  }, [executeRequest]);

  const getCurrentUser = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.getCurrentUser(), 'current-user');
  }, [executeRequest]);

  const refreshToken = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.refreshToken());
  }, [executeRequest]);

  // ==================== 健康数据相关方法 ====================

  const getHealthData = useCallback(async (userId: string, timeRange?: { start: string; end: string }) => {
    const cacheKey = `health-data-${userId}-${JSON.stringify(timeRange)}`;
    return executeRequest(() => apiIntegrationService.getHealthData(userId, timeRange), cacheKey);
  }, [executeRequest]);

  const saveHealthData = useCallback(async (data: any) => {
    return executeRequest(() => apiIntegrationService.saveHealthData(data));
  }, [executeRequest]);

  const getHealthMetrics = useCallback(async (userId: string, metric: string, period: string) => {
    const cacheKey = `health-metrics-${userId}-${metric}-${period}`;
    return executeRequest(() => apiIntegrationService.getHealthMetrics(userId, metric, period), cacheKey);
  }, [executeRequest]);

  const exportHealthData = useCallback(async (userId: string, format: 'json' | 'csv' | 'pdf' = 'json') => {
    return executeRequest(() => apiIntegrationService.exportHealthData(userId, format));
  }, [executeRequest]);

  // ==================== 智能体相关方法 ====================

  const getAgentStatus = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.getAgentStatus(), 'agent-status');
  }, [executeRequest]);

  const startAgentChat = useCallback(async (agentId: string, message: string) => {
    return executeRequest(() => apiIntegrationService.startAgentChat(agentId, message));
  }, [executeRequest]);

  const sendMessageToAgent = useCallback(async (agentId: string, message: string, context?: any) => {
    return executeRequest(() => apiIntegrationService.sendMessageToAgent(agentId, message, context));
  }, [executeRequest]);

  const getAgentPerformance = useCallback(async (agentId: string, timeRange?: { start: string; end: string }) => {
    const cacheKey = `agent-performance-${agentId}-${JSON.stringify(timeRange)}`;
    return executeRequest(() => apiIntegrationService.getAgentPerformance(agentId, timeRange), cacheKey);
  }, [executeRequest]);

  const updateAgentSettings = useCallback(async (agentId: string, settings: any) => {
    return executeRequest(() => apiIntegrationService.updateAgentSettings(agentId, settings));
  }, [executeRequest]);

  // ==================== 四诊相关方法 ====================

  const startDiagnosis = useCallback(async (type: 'look' | 'listen' | 'inquiry' | 'palpation', data: any) => {
    return executeRequest(() => apiIntegrationService.startDiagnosis(type, data));
  }, [executeRequest]);

  const getDiagnosisHistory = useCallback(async (userId: string, limit: number = 10) => {
    const cacheKey = `diagnosis-history-${userId}-${limit}`;
    return executeRequest(() => apiIntegrationService.getDiagnosisHistory(userId, limit), cacheKey);
  }, [executeRequest]);

  const getComprehensiveDiagnosis = useCallback(async (userId: string, symptoms: string[]) => {
    return executeRequest(() => apiIntegrationService.getComprehensiveDiagnosis(userId, symptoms));
  }, [executeRequest]);

  // ==================== 用户设置相关方法 ====================

  const getUserSettings = useCallback(async (userId: string) => {
    const cacheKey = `user-settings-${userId}`;
    return executeRequest(() => apiIntegrationService.getUserSettings(userId), cacheKey);
  }, [executeRequest]);

  const updateUserSettings = useCallback(async (userId: string, settings: any) => {
    return executeRequest(() => apiIntegrationService.updateUserSettings(userId, settings));
  }, [executeRequest]);

  const resetUserSettings = useCallback(async (userId: string) => {
    return executeRequest(() => apiIntegrationService.resetUserSettings(userId));
  }, [executeRequest]);

  // ==================== 区块链相关方法 ====================

  const saveHealthRecordToBlockchain = useCallback(async (userId: string, healthData: any) => {
    return executeRequest(() => apiIntegrationService.saveHealthRecordToBlockchain(userId, healthData));
  }, [executeRequest]);

  const getBlockchainHealthRecords = useCallback(async (userId: string) => {
    const cacheKey = `blockchain-records-${userId}`;
    return executeRequest(() => apiIntegrationService.getBlockchainHealthRecords(userId), cacheKey);
  }, [executeRequest]);

  const verifyHealthRecord = useCallback(async (recordId: string) => {
    return executeRequest(() => apiIntegrationService.verifyHealthRecord(recordId));
  }, [executeRequest]);

  // ==================== 医疗资源相关方法 ====================

  const searchMedicalResources = useCallback(async (query: any) => {
    const cacheKey = `medical-resources-${JSON.stringify(query)}`;
    return executeRequest(() => apiIntegrationService.searchMedicalResources(query), cacheKey);
  }, [executeRequest]);

  const getMedicalResourceDetails = useCallback(async (resourceId: string) => {
    const cacheKey = `medical-resource-${resourceId}`;
    return executeRequest(() => apiIntegrationService.getMedicalResourceDetails(resourceId), cacheKey);
  }, [executeRequest]);

  const bookMedicalAppointment = useCallback(async (resourceId: string, appointmentData: any) => {
    return executeRequest(() => apiIntegrationService.bookMedicalAppointment(resourceId, appointmentData));
  }, [executeRequest]);

  // ==================== 知识库相关方法 ====================

  const searchKnowledge = useCallback(async (query: any) => {
    const cacheKey = `knowledge-search-${JSON.stringify(query)}`;
    return executeRequest(() => apiIntegrationService.searchKnowledge(query), cacheKey);
  }, [executeRequest]);

  const getKnowledgeDetails = useCallback(async (knowledgeId: string) => {
    const cacheKey = `knowledge-${knowledgeId}`;
    return executeRequest(() => apiIntegrationService.getKnowledgeDetails(knowledgeId), cacheKey);
  }, [executeRequest]);

  const getRecommendedKnowledge = useCallback(async (userId: string, context?: any) => {
    const cacheKey = `recommended-knowledge-${userId}-${JSON.stringify(context)}`;
    return executeRequest(() => apiIntegrationService.getRecommendedKnowledge(userId, context), cacheKey);
  }, [executeRequest]);

  // ==================== 机器学习相关方法 ====================

  const trainPersonalModel = useCallback(async (userId: string, trainingData: any) => {
    return executeRequest(() => apiIntegrationService.trainPersonalModel(userId, trainingData));
  }, [executeRequest]);

  const getModelPrediction = useCallback(async (userId: string, inputData: any) => {
    return executeRequest(() => apiIntegrationService.getModelPrediction(userId, inputData));
  }, [executeRequest]);

  const getModelPerformance = useCallback(async (userId: string) => {
    const cacheKey = `model-performance-${userId}`;
    return executeRequest(() => apiIntegrationService.getModelPerformance(userId), cacheKey);
  }, [executeRequest]);

  // ==================== 无障碍相关方法 ====================

  const getAccessibilitySettings = useCallback(async (userId: string) => {
    const cacheKey = `accessibility-settings-${userId}`;
    return executeRequest(() => apiIntegrationService.getAccessibilitySettings(userId), cacheKey);
  }, [executeRequest]);

  const updateAccessibilitySettings = useCallback(async (userId: string, settings: any) => {
    return executeRequest(() => apiIntegrationService.updateAccessibilitySettings(userId, settings));
  }, [executeRequest]);

  const generateAccessibilityReport = useCallback(async (userId: string) => {
    return executeRequest(() => apiIntegrationService.generateAccessibilityReport(userId));
  }, [executeRequest]);

  // ==================== 生态服务相关方法 ====================

  const getEcoServices = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.getEcoServices(), 'eco-services');
  }, [executeRequest]);

  const subscribeToEcoService = useCallback(async (userId: string, serviceId: string, plan: string) => {
    return executeRequest(() => apiIntegrationService.subscribeToEcoService(userId, serviceId, plan));
  }, [executeRequest]);

  const getEcoServiceUsage = useCallback(async (userId: string, serviceId: string) => {
    const cacheKey = `eco-service-usage-${userId}-${serviceId}`;
    return executeRequest(() => apiIntegrationService.getEcoServiceUsage(userId, serviceId), cacheKey);
  }, [executeRequest]);

  // ==================== 反馈和支持相关方法 ====================

  const submitFeedback = useCallback(async (feedback: any) => {
    return executeRequest(() => apiIntegrationService.submitFeedback(feedback));
  }, [executeRequest]);

  const getFeedbackHistory = useCallback(async (userId: string) => {
    const cacheKey = `feedback-history-${userId}`;
    return executeRequest(() => apiIntegrationService.getFeedbackHistory(userId), cacheKey);
  }, [executeRequest]);

  const getSupportTickets = useCallback(async (userId: string) => {
    const cacheKey = `support-tickets-${userId}`;
    return executeRequest(() => apiIntegrationService.getSupportTickets(userId), cacheKey);
  }, [executeRequest]);

  const createSupportTicket = useCallback(async (ticket: any) => {
    return executeRequest(() => apiIntegrationService.createSupportTicket(ticket));
  }, [executeRequest]);

  // ==================== 系统监控相关方法 ====================

  const getSystemHealth = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.getSystemHealth(), 'system-health');
  }, [executeRequest]);

  const getSystemMetrics = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.getSystemMetrics(), 'system-metrics');
  }, [executeRequest]);

  const reportPerformanceMetrics = useCallback(async (metrics: any) => {
    return executeRequest(() => apiIntegrationService.reportPerformanceMetrics(metrics));
  }, [executeRequest]);

  // ==================== 实用工具方法 ====================

  const batchRequest = useCallback(async (requests: Array<{ name: string; request: () => Promise<any> }>) => {
    return executeRequest(() => apiIntegrationService.batchRequest(requests));
  }, [executeRequest]);

  const healthCheck = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.healthCheck(), 'health-check');
  }, [executeRequest]);

  const getApiVersion = useCallback(async () => {
    return executeRequest(() => apiIntegrationService.getApiVersion(), 'api-version');
  }, [executeRequest]);

  // 清除缓存
  const clearCache = useCallback((key?: string) => {
    if (key) {
      cacheRef.current.delete(key);
    } else {
      cacheRef.current.clear();
    }
  }, []);

  // 事件监听
  const addEventListener = useCallback((event: string, listener: (...args: any[]) => void) => {
    apiIntegrationService.on(event, listener);
  }, []);

  const removeEventListener = useCallback((event: string, listener: (...args: any[]) => void) => {
    apiIntegrationService.off(event, listener);
  }, []);

  // 清理函数
  useEffect(() => {
    return () => {
      // 组件卸载时清理缓存
      cacheRef.current.clear();
    };
  }, []);

  return {
    // 状态
    ...state,
    
    // 基础方法
    resetState,
    clearCache,
    executeRequest,
    
    // 认证相关
    login,
    logout,
    getCurrentUser,
    refreshToken,
    
    // 健康数据相关
    getHealthData,
    saveHealthData,
    getHealthMetrics,
    exportHealthData,
    
    // 智能体相关
    getAgentStatus,
    startAgentChat,
    sendMessageToAgent,
    getAgentPerformance,
    updateAgentSettings,
    
    // 四诊相关
    startDiagnosis,
    getDiagnosisHistory,
    getComprehensiveDiagnosis,
    
    // 用户设置相关
    getUserSettings,
    updateUserSettings,
    resetUserSettings,
    
    // 区块链相关
    saveHealthRecordToBlockchain,
    getBlockchainHealthRecords,
    verifyHealthRecord,
    
    // 医疗资源相关
    searchMedicalResources,
    getMedicalResourceDetails,
    bookMedicalAppointment,
    
    // 知识库相关
    searchKnowledge,
    getKnowledgeDetails,
    getRecommendedKnowledge,
    
    // 机器学习相关
    trainPersonalModel,
    getModelPrediction,
    getModelPerformance,
    
    // 无障碍相关
    getAccessibilitySettings,
    updateAccessibilitySettings,
    generateAccessibilityReport,
    
    // 生态服务相关
    getEcoServices,
    subscribeToEcoService,
    getEcoServiceUsage,
    
    // 反馈和支持相关
    submitFeedback,
    getFeedbackHistory,
    getSupportTickets,
    createSupportTicket,
    
    // 系统监控相关
    getSystemHealth,
    getSystemMetrics,
    reportPerformanceMetrics,
    
    // 实用工具
    batchRequest,
    healthCheck,
    getApiVersion,
    
    // 事件监听
    addEventListener,
    removeEventListener,
  };
}; 