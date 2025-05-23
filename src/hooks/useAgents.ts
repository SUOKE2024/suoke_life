/**
 * 智能体服务使用钩子
 * 提供便捷的智能体服务调用接口
 */
import React, { useState, useCallback, useContext } from 'react';
import xiaoaiApi from '../api/agents/xiaoaiApi';
import xiaokeApi from '../api/agents/xiaokeApi';
import laokeApi from '../api/agents/laokeApi';
import soerApi from '../api/agents/soerApi';

interface AgentState {
  loading: boolean;
  error: string | null;
  data: any;
}

interface UseAgentsReturn {
  // 状态
  xiaoai: AgentState;
  xiaoke: AgentState;
  laoke: AgentState;
  soer: AgentState;
  
  // 小艾服务方法
  createDiagnosisSession: (data: any) => Promise<any>;
  coordinateDiagnosis: (sessionId: string, data: any) => Promise<any>;
  
  // 小克服务方法
  scheduleResources: (data: any) => Promise<any>;
  recommendProducts: (data: any) => Promise<any>;
  generateDietPlan: (data: any) => Promise<any>;
  
  // 老克服务方法
  getKnowledgeArticles: (params: any) => Promise<any>;
  getPersonalizedLearningPaths: (data: any) => Promise<any>;
  askQuestion: (data: any) => Promise<any>;
  
  // 索儿服务方法
  generateHealthPlan: (data: any) => Promise<any>;
  trackNutrition: (userId: string, data: any) => Promise<any>;
  getHealthProfile: (userId: string, summary?: boolean) => Promise<any>;
  
  // 通用方法
  checkAllServicesHealth: () => Promise<boolean>;
  resetAllStates: () => void;
}

export function useAgents(): UseAgentsReturn {
  // 各智能体状态
  const [xiaoaiState, setXiaoaiState] = useState<AgentState>({
    loading: false,
    error: null,
    data: null,
  });
  
  const [xiaokeState, setXiaokeState] = useState<AgentState>({
    loading: false,
    error: null,
    data: null,
  });
  
  const [laokeState, setLaokeState] = useState<AgentState>({
    loading: false,
    error: null,
    data: null,
  });
  
  const [soerState, setSoerState] = useState<AgentState>({
    loading: false,
    error: null,
    data: null,
  });

  // 通用的异步请求处理器
  const withAsyncHandler = useCallback(
    <T>(
      apiCall: () => Promise<T>,
      setState: React.Dispatch<React.SetStateAction<AgentState>>
    ) => {
      return async (): Promise<T | null> => {
        setState(prev => ({ ...prev, loading: true, error: null }));
        try {
          const result = await apiCall();
          setState(prev => ({ ...prev, loading: false, data: result }));
          return result;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '请求失败';
          setState(prev => ({ ...prev, loading: false, error: errorMessage }));
          return null;
        }
      };
    },
    []
  );

  // 小艾服务方法
  const createDiagnosisSession = useCallback(
    (data: any) => 
      withAsyncHandler(() => xiaoaiApi.createDiagnosisSession(data), setXiaoaiState)(),
    [withAsyncHandler]
  );

  const coordinateDiagnosis = useCallback(
    (sessionId: string, data: any) =>
      withAsyncHandler(() => xiaoaiApi.coordinateDiagnosis(sessionId, data), setXiaoaiState)(),
    [withAsyncHandler]
  );

  // 小克服务方法
  const scheduleResources = useCallback(
    (data: any) =>
      withAsyncHandler(() => xiaokeApi.scheduleResources(data), setXiaokeState)(),
    [withAsyncHandler]
  );

  const recommendProducts = useCallback(
    (data: any) =>
      withAsyncHandler(() => xiaokeApi.recommendProducts(data), setXiaokeState)(),
    [withAsyncHandler]
  );

  const generateDietPlan = useCallback(
    (data: any) =>
      withAsyncHandler(() => xiaokeApi.generateDietPlan(data), setXiaokeState)(),
    [withAsyncHandler]
  );

  // 老克服务方法
  const getKnowledgeArticles = useCallback(
    (params: any) =>
      withAsyncHandler(() => laokeApi.getKnowledgeArticles(params), setLaokeState)(),
    [withAsyncHandler]
  );

  const getPersonalizedLearningPaths = useCallback(
    (data: any) =>
      withAsyncHandler(() => laokeApi.getPersonalizedLearningPaths(data), setLaokeState)(),
    [withAsyncHandler]
  );

  const askQuestion = useCallback(
    (data: any) =>
      withAsyncHandler(() => laokeApi.askQuestion(data), setLaokeState)(),
    [withAsyncHandler]
  );

  // 索儿服务方法
  const generateHealthPlan = useCallback(
    (data: any) =>
      withAsyncHandler(() => soerApi.generateHealthPlan(data), setSoerState)(),
    [withAsyncHandler]
  );

  const trackNutrition = useCallback(
    (userId: string, data: any) =>
      withAsyncHandler(() => soerApi.trackNutrition(userId, data), setSoerState)(),
    [withAsyncHandler]
  );

  const getHealthProfile = useCallback(
    (userId: string, summary = false) =>
      withAsyncHandler(() => soerApi.getHealthProfile(userId, summary), setSoerState)(),
    [withAsyncHandler]
  );

  // 检查所有服务健康状态
  const checkAllServicesHealth = useCallback(async (): Promise<boolean> => {
    try {
      const results = await Promise.all([
        xiaoaiApi.healthCheck(),
        xiaokeApi.healthCheck(),
        laokeApi.healthCheck(),
        soerApi.healthCheck(),
      ]);
      
      return results.every(result => result.status === 'healthy');
    } catch (error) {
      console.error('健康检查失败:', error);
      return false;
    }
  }, []);

  // 重置所有状态
  const resetAllStates = useCallback(() => {
    const initialState: AgentState = { loading: false, error: null, data: null };
    setXiaoaiState(initialState);
    setXiaokeState(initialState);
    setLaokeState(initialState);
    setSoerState(initialState);
  }, []);

  return {
    // 状态
    xiaoai: xiaoaiState,
    xiaoke: xiaokeState,
    laoke: laokeState,
    soer: soerState,
    
    // 小艾服务方法
    createDiagnosisSession,
    coordinateDiagnosis,
    
    // 小克服务方法
    scheduleResources,
    recommendProducts,
    generateDietPlan,
    
    // 老克服务方法
    getKnowledgeArticles,
    getPersonalizedLearningPaths,
    askQuestion,
    
    // 索儿服务方法
    generateHealthPlan,
    trackNutrition,
    getHealthProfile,
    
    // 通用方法
    checkAllServicesHealth,
    resetAllStates,
  };
}

// 智能体服务上下文
export interface AgentContextType {
  services: {
    xiaoai: typeof xiaoaiApi;
    xiaoke: typeof xiaokeApi;
    laoke: typeof laokeApi;
    soer: typeof soerApi;
  };
  
  // 全局状态
  servicesHealthy: boolean;
  lastHealthCheck: Date | null;
  
  // 方法
  refreshHealthStatus: () => Promise<void>;
}

export const AgentContext = React.createContext<AgentContextType | null>(null);

// 智能体服务提供者组件
export function AgentProvider({ children }: { children: React.ReactNode }) {
  const [servicesHealthy, setServicesHealthy] = useState(false);
  const [lastHealthCheck, setLastHealthCheck] = useState<Date | null>(null);

  const refreshHealthStatus = useCallback(async () => {
    try {
      const results = await Promise.all([
        xiaoaiApi.healthCheck(),
        xiaokeApi.healthCheck(),
        laokeApi.healthCheck(),
        soerApi.healthCheck(),
      ]);
      
      const healthy = results.every(result => result.status === 'healthy');
      setServicesHealthy(healthy);
      setLastHealthCheck(new Date());
    } catch (error) {
      console.error('健康状态刷新失败:', error);
      setServicesHealthy(false);
      setLastHealthCheck(new Date());
    }
  }, []);

  const contextValue: AgentContextType = {
    services: {
      xiaoai: xiaoaiApi,
      xiaoke: xiaokeApi,
      laoke: laokeApi,
      soer: soerApi,
    },
    servicesHealthy,
    lastHealthCheck,
    refreshHealthStatus,
  };

  return (
    <AgentContext.Provider value={contextValue}>
      {children}
    </AgentContext.Provider>
  );
}

// 使用智能体上下文的钩子
export function useAgentContext(): AgentContextType {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
}

export default useAgents;