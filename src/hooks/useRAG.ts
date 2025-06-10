';,'';
import { useCallback, useEffect, useState } from "react";";
import { useDispatch, useSelector } from "react-redux";";
import { ragService } from "../services/ragService";""/;,"/g"/;
import {import type {queryRAG;,}analyzeTCM,;
recommendHerbs,;
streamQueryRAG,;
selectRAGState,;
selectIsQuerying,;
selectIsStreaming,;
selectCurrentResult,;
selectQueryHistory,;
selectCacheStats,;
selectPerformanceMetrics,;
selectPreferences,;
selectOfflineStatus,;
selectTCMAnalysisResult,;
selectHerbRecommendationResult,;
clearCurrentResult,;
clearError,;
updatePreferences,;
setOfflineStatus,;
clearCache,";"";
}
  resetPerformanceMetrics;'}'';'';
} from "../store/slices/ragSlice";""/;,"/g"/;
RAGQueryRequest,;
RAGQueryResponse,;
TCMAnalysisRequest,;
HerbRecommendationRequest,';,'';
StreamResponse;';'';
} from "../services/ragService";""/;"/g"/;
// Hook返回类型定义/;,/g/;
export interface UseRAGReturn {// 状态/;,}isQuerying: boolean,;,/g,/;
  isStreaming: boolean,;
isAnalyzing: boolean,;
isRecommending: boolean,;
currentResult: RAGQueryResponse | null,;
queryHistory: RAGQueryResponse[],;
tcmAnalysisResult: any,;
herbRecommendationResult: any,;
const error = string | null;
  // 统计信息/;,/g,/;
  cacheStats: any,;
performanceMetrics: any,;
preferences: any,;
const offlineStatus = any;
  // 基础查询方法/;,/g,/;
  query: (request: RAGQueryRequest) => Promise<void>,;
streamQuery: (request: RAGQueryRequest, onChunk?: (chunk: StreamResponse) => void) => Promise<void>;
  // 中医特色功能/;,/g,/;
  analyzeTCMSymptoms: (request: TCMAnalysisRequest) => Promise<void>,;
getHerbRecommendations: (request: HerbRecommendationRequest) => Promise<void>;
  // 多模态查询/;,/g,/;
  queryWithImage: (query: string, imageUri: string, userId: string) => Promise<void>,;
queryWithAudio: (query: string, audioUri: string, userId: string) => Promise<void>,;
queryWithSensorData: (query: string, sensorData: any, userId: string) => Promise<void>;
  // 状态管理/;,/g,/;
  clearResult: () => void,;
clearError: () => void,;
updateUserPreferences: (prefs: Partial<any>) => void;
  // 缓存管理/;,/g,/;
  clearQueryCache: () => void,;
getCacheInfo: () => any;
  // 性能管理/;,/g,/;
  resetMetrics: () => void,;
getPerformanceReport: () => any;
  // 离线支持/;,/g,/;
  setOffline: (offline: boolean) => void,;
syncPendingQueries: () => Promise<void>;
  // 历史管理/;,/g,/;
  getQueryHistory: () => RAGQueryResponse[],;
searchHistory: (keyword: string) => RAGQueryResponse[],;
exportHistory: () => string,;
importHistory: (data: string) => void;
  // 智能推荐/;,/g,/;
  getSmartSuggestions: (context: string) => Promise<string[]>,;
getRelatedQueries: (query: string) => Promise<string[]>;
  // 健康评估/;,/g,/;
  performHealthAssessment: (symptoms: string[], constitution: string) => Promise<any>,;
}
}
  getPreventionAdvice: (riskFactors: string[]) => Promise<any>;}
}
// 自定义RAG Hook;/;,/g/;
export const useRAG = (): UseRAGReturn => {const dispatch = useDispatch();}  // 从Redux store获取状态/;,/g/;
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
  // 本地状态/;,/g/;
const [smartSuggestions, setSmartSuggestions] = useState<string[]>([]);
const [relatedQueries, setRelatedQueries] = useState<string[]>([]);
  // 基础查询方法/;/g/;
}
  const query = useCallback(async (request: RAGQueryRequest) => {try {await dispatch(queryRAG(request) as any);)}
    } catch (error) {}}
}
    }
  }, [dispatch]);
  // 流式查询方法/;,/g/;
const streamQuery = useCallback(async (;));
request: RAGQueryRequest,onChunk?: (chunk: StreamResponse) => void;
  ) => {try {await dispatch(streamQueryRAG({request,onChunk: onChunk || () => {);}
      }) as any);
    } catch (error) {}}
}
    }
  }, [dispatch]);
  // 中医症状分析/;,/g/;
const analyzeTCMSymptoms = useCallback(async (request: TCMAnalysisRequest) => {try {await dispatch(analyzeTCM(request) as any);)}
    } catch (error) {}}
}
    }
  }, [dispatch]);
  // 中药推荐/;,/g/;
const getHerbRecommendations = useCallback(async (request: HerbRecommendationRequest) => {try {await dispatch(recommendHerbs(request) as any);)}
    } catch (error) {}}
}
    }
  }, [dispatch]);';'';
  // 多模态查询 - 图像'/;,'/g,'/;
  queryWithImage: useCallback(async (query: string, imageUri: string, userId: string) => {const request: RAGQueryRequest = {query,userId,taskType: 'diagnosis',multimodalData: [;];)';}        {';}}'';
      type: "image";","}";,"";
data: imageUri, metadata: { format: 'jpeg' ;} };';'';
];
      ];
    };
const await = dispatch(queryRAG(request) as any);
  }, [dispatch]);';'';
  // 多模态查询 - 音频'/;,'/g,'/;
  queryWithAudio: useCallback(async (query: string, audioUri: string, userId: string) => {const request: RAGQueryRequest = {query,userId,taskType: 'consultation',multimodalData: [;];)';}        {';}}'';
      type: "audio";","}";,"";
data: audioUri, metadata: { format: 'wav' ;} };';'';
];
      ];
    };
const await = dispatch(queryRAG(request) as any);
  }, [dispatch]);';'';
  // 多模态查询 - 传感器数据'/;,'/g,'/;
  queryWithSensorData: useCallback(async (query: string, sensorData: any, userId: string) => {const request: RAGQueryRequest = {query,userId,taskType: 'diagnosis',multimodalData: [;];)';}        {';}}'';
      type: "sensor";","}";,"";
data: JSON.stringify(sensorData), metadata: { source: 'device' ;} };';'';
];
      ];
    };
const await = dispatch(queryRAG(request) as any);
  }, [dispatch]);
  // 状态管理方法/;,/g/;
const clearResult = useCallback() => {dispatch(clearCurrentResult());}
  }, [dispatch]);
const clearErrorState = useCallback() => {dispatch(clearError());}
  }, [dispatch]);
const updateUserPreferences = useCallback(prefs: Partial<any>) => {dispatch(updatePreferences(prefs));}
  }, [dispatch]);
  // 缓存管理/;,/g/;
const clearQueryCache = useCallback() => {dispatch(clearCache());}
  }, [dispatch]);
const getCacheInfo = useCallback() => {return ragService.getCacheStats();}
  }, []);
  // 性能管理/;,/g/;
const resetMetrics = useCallback() => {dispatch(resetPerformanceMetrics());}
  }, [dispatch]);
getPerformanceReport: useCallback() => {return {...performanceMetrics,cacheEfficiency: cacheStats.hitRate,totalCacheSize: cacheStats.size,timestamp: new Date().toISOString();}
    };
  }, [performanceMetrics, cacheStats]);
  // 离线支持/;,/g/;
const setOffline = useCallback(offline: boolean) => {dispatch(setOfflineStatus(offline));}
  }, [dispatch]);
const syncPendingQueries = useCallback(async () => {if (!offlineStatus.isOffline && offlineStatus.pendingQueries.length > 0) {for (const pendingQuery of offlineStatus.pendingQueries) {try {await dispatch(queryRAG(pendingQuery) as any);)}
        } catch (error) {}}
}
        }
      }
    }
  }, [dispatch, offlineStatus]);
  // 历史管理/;,/g/;
const getQueryHistory = useCallback() => {return queryHistory;}
  }, [queryHistory]);
const searchHistory = useCallback(keyword: string) => {return queryHistory.filter(item => ;);,}item.requestId.toLowerCase().includes(keyword.toLowerCase()) ||;
item.answer.toLowerCase().includes(keyword.toLowerCase());
}
    );}';'';
  }, [queryHistory]);';,'';
exportHistory: useCallback() => {return JSON.stringify({history: queryHistory,exportTime: new Date().toISOString(),version: '1.0';)'}'';'';
    });
  }, [queryHistory]);
const importHistory = useCallback(data: string) => {try {const parsed = JSON.parse(data);,}if (parsed.history && Array.isArray(parsed.history)) {// 这里需要实现导入逻辑/;}}/g/;
}
      }
    } catch (error) {}}
}
    }
  }, []);
  // 智能推荐/;,/g/;
const getSmartSuggestions = useCallback(async (context: string) => {try {// 基于上下文生成智能建议;)/;,}const suggestions: string[] = [];,/g/;
setSmartSuggestions(suggestions);
}
      return suggestions;}
    } catch (error) {}}
      return [];}
    }
  }, []);
const getRelatedQueries = useCallback(async (query: string) => {try {// 获取相关查询建议;)/;,}const related: string[] = [];,/g/;
setRelatedQueries(related);
}
      return related;}
    } catch (error) {}}
      return [];}
    }
  }, []);';'';
  // 健康评估'/;,'/g,'/;
  performHealthAssessment: useCallback(async (symptoms: string[], constitution: string) => {try {const request: TCMAnalysisRequest = {symptoms,constitutionType: constitution as any,userId: 'current-user', // 应该从用户状态获取;)'/;}}'/g'/;
        const analysisType = 'comprehensive';'}'';'';
      };
const await = dispatch(analyzeTCM(request) as any);
return tcmAnalysisResult;
    } catch (error) {}}
      return null;}
    }
  }, [dispatch, tcmAnalysisResult]);

        };
      };
const await = dispatch(queryRAG(request) as any);
return currentResult;
    } catch (error) {}}
      return null;}
    }
  }, [dispatch, currentResult]);
  // 监听网络状态变化/;,/g/;
useEffect() => {const handleOnline = () => {setOffline(false);}}
      syncPendingQueries();}
    };
const handleOffline = () => {setOffline(true);}
    };
    // 在React Native中，可以使用NetInfo来监听网络状态'/;'/g'/;
    // 这里使用浏览器API作为示例'/;,'/g'/;
if (typeof window !== 'undefined') {';,}window.addEventListener('online', handleOnline)';'';
    // 记住在组件卸载时移除监听器;'/;,'/g'/;
window.addEventListener('offline', handleOffline)';'';
    // 记住在组件卸载时移除监听器;'/;,'/g'/;
return () => {window.removeEventListener('online', handleOnline);';}}'';
        window.removeEventListener('offline', handleOffline);'}'';'';
      };
    }
  }, [setOffline, syncPendingQueries]);
  // 自动清理过期缓存/;,/g/;
useEffect() => {const cleanupInterval = setInterval() => {if (cacheStats.size > 100) { // 如果缓存过大;/;}}/g/;
        ragService.cleanupCache?.();}
      }
    }, 5 * 60 * 1000); // 每5分钟检查一次/;,/g/;
return () => clearInterval(cleanupInterval);
  }, [cacheStats.size]);
return {// 状态/;,}isQuerying,;,/g/;
isStreaming,;
isAnalyzing: ragState.isAnalyzing,;
const isRecommending = ragState.isRecommending;
currentResult,;
queryHistory,;
tcmAnalysisResult,;
herbRecommendationResult,;
const error = ragState.error;
    // 统计信息/;,/g/;
cacheStats,;
performanceMetrics,;
preferences,;
offlineStatus,;
    // 基础查询方法/;,/g/;
query,;
streamQuery,;
    // 中医特色功能/;,/g/;
analyzeTCMSymptoms,;
getHerbRecommendations,;
    // 多模态查询/;,/g/;
queryWithImage,;
queryWithAudio,;
queryWithSensorData,;
    // 状态管理/;,/g/;
clearResult,;
const clearError = clearErrorState;
updateUserPreferences,;
    // 缓存管理/;,/g/;
clearQueryCache,;
getCacheInfo,;
    // 性能管理/;,/g/;
resetMetrics,;
getPerformanceReport,;
    // 离线支持/;,/g/;
setOffline,syncPendingQueries;
    // 历史管理;/;,/g/;
getQueryHistory,searchHistory,exportHistory,importHistory;
    // 智能推荐;/;,/g/;
getSmartSuggestions,getRelatedQueries;
    // 健康评估;/;/g/;
}
    performHealthAssessment,getPreventionAdvice;}
  };
};
// 导出Hook类型'/;,'/g'/;
export type { UseRAGReturn };