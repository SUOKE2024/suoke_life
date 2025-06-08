import React from 'react';
import { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { ragService } from '../services/ragService';
import {import type {queryRAG,
  analyzeTCM,
  recommendHerbs,
  streamQueryRAG,
  selectRAGState,
  selectIsQuerying,
  selectIsStreaming,
  selectCurrentResult,
  selectQueryHistory,
  selectCacheStats,
  selectPerformanceMetrics,
  selectPreferences,
  selectOfflineStatus,
  selectTCMAnalysisResult,
  selectHerbRecommendationResult,
  clearCurrentResult,
  clearError,
  updatePreferences,
  setOfflineStatus,
  clearCache,
  resetPerformanceMetrics;
} from '../store/slices/ragSlice';
  RAGQueryRequest,
  RAGQueryResponse,
  TCMAnalysisRequest,
  HerbRecommendationRequest,
  StreamResponse;
} from '../services/ragService';
// Hook返回类型定义
export interface UseRAGServiceReturn {
  // 状态
  isQuerying: boolean;
  isStreaming: boolean;
  isAnalyzing: boolean;
  isRecommending: boolean;
  currentResult: RAGQueryResponse | null;
  queryHistory: RAGQueryResponse[];
  tcmAnalysisResult: any;
  herbRecommendationResult: any;
  error: string | null;
  // 统计信息
  cacheStats: any;
  performanceMetrics: any;
  preferences: any;
  offlineStatus: any;
  // 基础查询方法
  query: (request: RAGQueryRequest) => Promise<void>;
  streamQuery: (request: RAGQueryRequest, onChunk?: (chunk: StreamResponse) => void) => Promise<void>;
  // 中医特色功能
  analyzeTCMSymptoms: (request: TCMAnalysisRequest) => Promise<void>;
  getHerbRecommendations: (request: HerbRecommendationRequest) => Promise<void>;
  // 多模态查询
  queryWithImage: (query: string, imageUri: string, userId: string) => Promise<void>;
  queryWithAudio: (query: string, audioUri: string, userId: string) => Promise<void>;
  queryWithSensorData: (query: string, sensorData: any, userId: string) => Promise<void>;
  // 状态管理
  clearResult: () => void;
  clearError: () => void;
  updateUserPreferences: (prefs: Partial<any>) => void;
  // 缓存管理
  clearQueryCache: () => void;
  getCacheInfo: () => any;
  // 性能管理
  resetMetrics: () => void;
  getPerformanceReport: () => any;
  // 离线支持
  setOffline: (offline: boolean) => void;
  syncPendingQueries: () => Promise<void>;
  // 历史管理
  getQueryHistory: () => RAGQueryResponse[];
  searchHistory: (keyword: string) => RAGQueryResponse[];
  exportHistory: () => string;
  importHistory: (data: string) => void;
  // 智能推荐
  getSmartSuggestions: (context: string) => Promise<string[]>;
  getRelatedQueries: (query: string) => Promise<string[]>;
  // 健康评估
  performHealthAssessment: (symptoms: string[], constitution: string) => Promise<any>;
  getPreventionAdvice: (riskFactors: string[]) => Promise<any>;
}
// 自定义RAG Hook;
export const useRAGService = (): UseRAGServiceReturn => {const dispatch = useDispatch();
  // 从Redux store获取状态
  const ragState = useSelector(selectRAGState);
  const isQuerying = useSelector(selectIsQuerying);
  const isStreaming = useSelector(selectIsStreaming);
  const currentResult = useSelector(selectCurrentResult);
  const queryHistory = useSelector(selectQueryHistory);
  const cacheStats = useSelector(selectCacheStats);
  const performanceMetrics = useSelector(selectPerformanceMetrics);
  const preferences = useSelector(selectPreferences);
  const offlineStatus = useSelector(selectOfflineStatus);
  const tcmAnalysisResult = useSelector(selectTCMAnalysisResult);
  const herbRecommendationResult = useSelector(selectHerbRecommendationResult);
  // 本地状态
  const [smartSuggestions, setSmartSuggestions] = useState<string[]>([]);
  const [relatedQueries, setRelatedQueries] = useState<string[]>([]);
  // 基础查询方法
  const query = useCallback(async (request: RAGQueryRequest) => {try {await dispatch(queryRAG(request) as any);)
    } catch (error) {
      console.error('RAG查询失败:', error);
    }
  }, [dispatch]);
  // 流式查询方法
  const streamQuery = useCallback(async (;))
    request: RAGQueryRequest,onChunk?: (chunk: StreamResponse) => void;
  ) => {try {await dispatch(streamQueryRAG({request,onChunk: onChunk || () => {);
      }) as any);
    } catch (error) {
      console.error('流式查询失败:', error);
    }
  }, [dispatch]);
  // 中医症状分析
  const analyzeTCMSymptoms = useCallback(async (request: TCMAnalysisRequest) => {try {await dispatch(analyzeTCM(request) as any);)
    } catch (error) {
      console.error('中医分析失败:', error);
    }
  }, [dispatch]);
  // 中药推荐
  const getHerbRecommendations = useCallback(async (request: HerbRecommendationRequest) => {try {await dispatch(recommendHerbs(request) as any);)
    } catch (error) {
      console.error('中药推荐失败:', error);
    }
  }, [dispatch]);
  // 多模态查询 - 图像
  const queryWithImage = useCallback(async (query: string, imageUri: string, userId: string) => {const request: RAGQueryRequest = {query,userId,taskType: 'diagnosis',multimodalData: [;)
        {
      type: "image",
      data: imageUri, metadata: { format: 'jpeg' } };
      ];
    };
    await dispatch(queryRAG(request) as any);
  }, [dispatch]);
  // 多模态查询 - 音频
  const queryWithAudio = useCallback(async (query: string, audioUri: string, userId: string) => {const request: RAGQueryRequest = {query,userId,taskType: 'consultation',multimodalData: [;)
        {
      type: "audio",
      data: audioUri, metadata: { format: 'wav' } };
      ];
    };
    await dispatch(queryRAG(request) as any);
  }, [dispatch]);
  // 多模态查询 - 传感器数据
  const queryWithSensorData = useCallback(async (query: string, sensorData: any, userId: string) => {const request: RAGQueryRequest = {query,userId,taskType: 'diagnosis',multimodalData: [;)
        {
      type: "sensor",
      data: JSON.stringify(sensorData), metadata: { source: 'device' } };
      ];
    };
    await dispatch(queryRAG(request) as any);
  }, [dispatch]);
  // 状态管理方法
  const clearResult = useCallback() => {dispatch(clearCurrentResult());
  }, [dispatch]);
  const clearErrorState = useCallback() => {dispatch(clearError());
  }, [dispatch]);
  const updateUserPreferences = useCallback(prefs: Partial<any>) => {dispatch(updatePreferences(prefs));
  }, [dispatch]);
  // 缓存管理
  const clearQueryCache = useCallback() => {dispatch(clearCache());
  }, [dispatch]);
  const getCacheInfo = useCallback() => {return ragService.getCacheStats();
  }, []);
  // 性能管理
  const resetMetrics = useCallback() => {dispatch(resetPerformanceMetrics());
  }, [dispatch]);
  const getPerformanceReport = useCallback() => {return {...performanceMetrics,cacheEfficiency: cacheStats.hitRate,totalCacheSize: cacheStats.size,timestamp: new Date().toISOString();
    };
  }, [performanceMetrics, cacheStats]);
  // 离线支持
  const setOffline = useCallback(offline: boolean) => {dispatch(setOfflineStatus(offline));
  }, [dispatch]);
  const syncPendingQueries = useCallback(async () => {if (!offlineStatus.isOffline && offlineStatus.pendingQueries.length > 0) {for (const pendingQuery of offlineStatus.pendingQueries) {try {await dispatch(queryRAG(pendingQuery) as any);)
        } catch (error) {
          console.error('同步离线查询失败:', error);
        }
      }
    }
  }, [dispatch, offlineStatus]);
  // 历史管理
  const getQueryHistory = useCallback() => {return queryHistory;
  }, [queryHistory]);
  const searchHistory = useCallback(keyword: string) => {return queryHistory.filter(item => ;)
      item.requestId.toLowerCase().includes(keyword.toLowerCase()) ||;
      item.answer.toLowerCase().includes(keyword.toLowerCase());
    );
  }, [queryHistory]);
  const exportHistory = useCallback() => {return JSON.stringify({history: queryHistory,exportTime: new Date().toISOString(),version: '1.0';)
    });
  }, [queryHistory]);
  const importHistory = useCallback(data: string) => {try {const parsed = JSON.parse(data);
      if (parsed.history && Array.isArray(parsed.history)) {
        console.log('导入历史记录:', parsed.history.length, '条');
      }
    } catch (error) {
      console.error('导入历史记录失败:', error);
    }
  }, []);
  // 智能推荐
  const getSmartSuggestions = useCallback(async (context: string) => {try {// 基于上下文生成智能建议;)
      const suggestions: string[] = [;
        "基于您的症状，建议进行中医体质辨识", "推荐查看相关的中药调理方案','建议咨询专业中医师进行详细诊断';
      ];
      setSmartSuggestions(suggestions);
      return suggestions;
    } catch (error) {
      console.error('获取智能建议失败:', error);
      return [];
    }
  }, []);
  const getRelatedQueries = useCallback(async (query: string) => {try {// 获取相关查询建议;)
      const related: string[] = [;
        "相关症状查询", "类似病症分析','推荐治疗方案';
      ];
      setRelatedQueries(related);
      return related;
    } catch (error) {
      console.error('获取相关查询失败:', error);
      return [];
    }
  }, []);
  // 健康评估
  const performHealthAssessment = useCallback(async (symptoms: string[], constitution: string) => {try {const request: TCMAnalysisRequest = {symptoms,constitutionType: constitution as any,userId: 'current-user';)
      };
      await dispatch(analyzeTCM(request) as any);
      return tcmAnalysisResult;
    } catch (error) {
      console.error('健康评估失败:", " error);
      return null;
    }
  }, [dispatch, tcmAnalysisResult]);
  const getPreventionAdvice = useCallback(async (riskFactors: string[]) => {try {const request: RAGQueryRequest = {query: `基于以下风险因素提供预防建议: ${riskFactors.join(",)}`,userId: 'current-user',taskType: 'prevention',context: {riskFactors,requestType: 'prevention_advice';)
        };
      };
      await dispatch(queryRAG(request) as any);
      return currentResult;
    } catch (error) {
      console.error('获取预防建议失败:', error);
      return null;
    }
  }, [dispatch, currentResult]);
  // 监听网络状态变化
  useEffect(() => {
    const handleOnline = () => {setOffline(false);
      syncPendingQueries();
    };
    const handleOffline = () => {setOffline(true);
    };
    // 在React Native中，可以使用NetInfo来监听网络状态
    if (typeof window !== 'undefined') {
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);
      return () => {window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }
  }, [setOffline, syncPendingQueries]);
  // 自动清理过期缓存
  useEffect(() => {
    const cleanupInterval = setInterval() => {if (cacheStats.size > 100) {ragService.clearCache();
      }
    }, 5 * 60 * 1000); // 每5分钟检查一次
    return () => clearInterval(cleanupInterval);
  }, [cacheStats.size]);
  return {
    // 状态
    isQuerying,
    isStreaming,
    isAnalyzing: ragState.isAnalyzing,
    isRecommending: ragState.isRecommending,
    currentResult,
    queryHistory,
    tcmAnalysisResult,
    herbRecommendationResult,
    error: ragState.error,
    // 统计信息
    cacheStats,
    performanceMetrics,
    preferences,
    offlineStatus,
    // 基础查询方法
    query,
    streamQuery,
    // 中医特色功能
    analyzeTCMSymptoms,
    getHerbRecommendations,
    // 多模态查询
    queryWithImage,
    queryWithAudio,
    queryWithSensorData,
    // 状态管理
    clearResult,
    clearError: clearErrorState,
    updateUserPreferences,
    // 缓存管理
    clearQueryCache,
    getCacheInfo,
    // 性能管理
    resetMetrics,
    getPerformanceReport,
    // 离线支持
    setOffline,syncPendingQueries;
    // 历史管理;
    getQueryHistory,searchHistory,exportHistory,importHistory;
    // 智能推荐;
    getSmartSuggestions,getRelatedQueries;
    // 健康评估;
    performHealthAssessment,getPreventionAdvice;
  };
};