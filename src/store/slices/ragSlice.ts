import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit"
import { ragService } from "../../services/ragService"
import { RAG_CONFIG } from "../../constants/config"
import AsyncStorage from "@react-native-async-storage/async-storage"
const import = type {RAGQueryRequestRAGQueryResponse,
TCMAnalysisRequest,
TCMAnalysisResponse,
HerbRecommendationRequest,"
HerbRecommendationResponse,";
}
  StreamResponse;'}
} from "../../services/ragService"/;"/g"/;
// 状态接口定义
export interface RAGState {;
// 查询状态/isQuerying: boolean,,/g,/;
  isStreaming: boolean,
currentQuery: string,
const queryHistory = RAGQueryResponse[];
  // 当前结果/,/g,/;
  currentResult: RAGQueryResponse | null,
const streamingText = string;
  // 中医分析状态/,/g,/;
  isAnalyzing: boolean,
const tcmAnalysisResult = TCMAnalysisResponse | null;
  // 中药推荐状态/,/g,/;
  isRecommending: boolean,
const herbRecommendationResult = HerbRecommendationResponse | null;
  // 错误处理/,/g,/;
  error: string | null,
const lastError = Error | null;
  // 缓存管理/,/g,/;
  cacheStats: {size: number,
keys: string[],
hitRate: number,
totalQueries: number,
}
  const cacheHits = number}
};
  // 性能监控/,/g,/;
  performance: {averageResponseTime: number,
totalQueries: number,
successRate: number,
}
  const failureCount = number}
  };
  // 用户偏好/,/g,/;
  preferences: {enableCache: boolean,
enableStreaming: boolean,"
defaultTaskType: 'consultation' | 'diagnosis' | 'treatment' | 'prevention,'';
maxHistorySize: number,
}
  const autoSaveHistory = boolean}
  };
  // 离线支持/,/g,/;
  offline: {isOffline: boolean,
pendingQueries: RAGQueryRequest[],
}
  const offlineCache = RAGQueryResponse[]}
  };
}
// 初始状态/,/g,/;
  const: initialState: RAGState = {isQuerying: false,
isStreaming: false,
currentQuery: ,
queryHistory: [],
currentResult: null,'
streamingText: ,'';
isAnalyzing: false,
tcmAnalysisResult: null,
isRecommending: false,
herbRecommendationResult: null,
error: null,
lastError: null,
cacheStats: {size: 0,
keys: [],
hitRate: 0,
totalQueries: 0,
}
    const cacheHits = 0}
  }
performance: {averageResponseTime: 0,
totalQueries: 0,
successRate: 100,
}
    const failureCount = 0}
  }
preferences: {enableCache: true,
enableStreaming: true,'
defaultTaskType: 'consultation,'';
maxHistorySize: 50,
}
    const autoSaveHistory = true}
  }
offline: {isOffline: false,
pendingQueries: [],
}
    const offlineCache = []}
  }
};
// 异步Thunk：基础RAG查询'/,'/g'/;
export const queryRAG = createAsyncThunk(;);
  'rag/query','/,'/g'/;
async (request: RAGQueryRequest, { dispatch, rejectWithValue ;}) => {try {}      const startTime = Date.now();
      // 更新查询状态
dispatch(setCurrentQuery(request.query));
const result = await ragService.query(request);
      // 计算响应时间
}
      const responseTime = Date.now() - startTime}
      dispatch(updatePerformanceMetrics({  responseTime, success: true ; }));
      // 更新缓存统计
const cacheStats = ragService.getCacheStats();
dispatch(updateCacheStats(cacheStats));
return result;
    } catch (error) {}
      dispatch(updatePerformanceMetrics({  responseTime: 0, success: false ; }));
return rejectWithValue(error as Error).message);
    }
  }
);
// 异步Thunk：中医分析'/,'/g'/;
export const analyzeTCMSyndrome = createAsyncThunk(;);
  'rag/analyzeTCMSyndrome','/,'/g'/;
async (request: TCMAnalysisRequest, { rejectWithValue ;}) => {try {}      const result = await ragService.analyzeTCM(request);
}
      return result}
    } catch (error) {}
      return rejectWithValue(error as Error).message)}
    }
  }
);
// 异步Thunk：中药推荐'/,'/g'/;
export const recommendHerbs = createAsyncThunk(;);
  'rag/recommendHerbs','/,'/g'/;
async (request: HerbRecommendationRequest, { rejectWithValue ;}) => {try {}      const result = await ragService.recommendHerbs(request);
}
      return result}
    } catch (error) {}
      return rejectWithValue(error as Error).message)}
    }
  }
);
// 异步Thunk：流式查询'/,'/g'/;
export const streamQueryRAG = createAsyncThunk(;);
  'rag/streamQuery','/,'/g'/;
async ();
    { request, onChunk }: { request: RAGQueryRequest; onChunk: (chunk: StreamResponse) => void }
    { dispatch, rejectWithValue }
  ) => {try {'dispatch(setCurrentQuery(request.query));
dispatch(setStreamingText('));'';
await: ragService.streamQuery(request, (chunk: StreamResponse) => {dispatch(appendStreamingText(chunk.answerFragment))}
        onChunk(chunk)}
      });
return true;
    } catch (error) {}
      return rejectWithValue(error as Error).message)}
    }
  }
);
// 异步Thunk：多模态查询'/,'/g'/;
export const multimodalQuery = createAsyncThunk(;);
  'rag/multimodalQuery','/,'/g'/;
async (request: RAGQueryRequest, { dispatch, rejectWithValue ;}) => {try {}      const startTime = Date.now();
const result = await ragService.multimodalQuery(request);
}
      const responseTime = Date.now() - startTime}
      dispatch(updatePerformanceMetrics({  responseTime, success: true ; }));
return result;
    } catch (error) {}
      dispatch(updatePerformanceMetrics({  responseTime: 0, success: false ; }));
return rejectWithValue(error as Error).message);
    }
  }
);
// RAG切片'/,'/g,'/;
  const: ragSlice = createSlice({)name: 'rag',initialState,reducers: {// 基础状态管理,)'/;}}'/g,'/;
  setCurrentQuery: (state, action: PayloadAction<string>) => {state.currentQuery = action.payload}
    }
clearCurrentResult: (state) => {}
      state.currentResult = null}
    }
    // 错误处理/,/g,/;
  setError: (state, action: PayloadAction<string>) => {state.error = action.payload}
      state.lastError = new Error(action.payload)}
    }
clearError: (state) => {state.error = null}
      state.lastError = null}
    }
    // 流式查询管理/,/g,/;
  setStreamingText: (state, action: PayloadAction<string>) => {}
      state.streamingText = action.payload}
    }
appendStreamingText: (state, action: PayloadAction<string>) => {}
      state.streamingText += action.payload}
    },'
clearStreamingText: (state) => {';}}
      state.streamingText = }
    }
    // 历史记录管理/,/g,/;
  addToHistory: (state, action: PayloadAction<RAGQueryResponse>) => {const maxSize = state.preferences.maxHistorySizestate.queryHistory.unshift(action.payload);
if (state.queryHistory.length > maxSize) {}
        state.queryHistory = state.queryHistory.slice(0, maxSize)}
      }
    }
clearHistory: (state) => {}
      state.queryHistory = []}
    }
removeFromHistory: (state, action: PayloadAction<string>) => {state.queryHistory = state.queryHistory.filter()item => item.requestId !== action.payload;
}
      )}
    }
    // 缓存管理/,/g,/;
  updateCacheStats: (state, action: PayloadAction<{ size: number; keys: string[] ;}>) => {}
      const { size, keys } = action.payload;
state.cacheStats.size = size;
state.cacheStats.keys = keys;
      // 计算缓存命中率
if (state.cacheStats.totalQueries > 0) {}
        state.cacheStats.hitRate = (state.cacheStats.cacheHits / state.cacheStats.totalQueries) * 100;}
      }
    }
incrementCacheHit: (state) => {state.cacheStats.cacheHits += 1}
      state.cacheStats.totalQueries += 1}
    }
incrementCacheMiss: (state) => {}
      state.cacheStats.totalQueries += 1}
    }
clearCache: (state) => {ragService.clearCache()state.cacheStats = {size: 0}keys: [],
hitRate: 0,
totalQueries: 0,
}
        const cacheHits = 0}
      };
    }
    // 性能监控
const updatePerformanceMetrics = ();
state;
const action = PayloadAction<{ responseTime: number; success: boolean ;}>;
    ) => {}
      const { responseTime, success } = action.payload;
if (success) {const totalTime = state.performance.averageResponseTime * state.performance.totalQueriesstate.performance.totalQueries += 1;
state.performance.averageResponseTime = (totalTime + responseTime) / state.performance.totalQueries;
        // 计算成功率
const totalAttempts = state.performance.totalQueries + state.performance.failureCount;
}
        state.performance.successRate = (state.performance.totalQueries / totalAttempts) * 100;}
      } else {state.performance.failureCount += 1;}        // 重新计算成功率
const totalAttempts = state.performance.totalQueries + state.performance.failureCount;
if (totalAttempts > 0) {}
          state.performance.successRate = (state.performance.totalQueries / totalAttempts) * 100;}
        }
      }
    }
resetPerformanceMetrics: (state) => {state.performance = {}        averageResponseTime: 0,
totalQueries: 0,
successRate: 100,
}
        const failureCount = 0}
      };
    },'
    // 用户偏好管理'/,'/g,'/;
  updatePreferences: (state, action: PayloadAction<Partial<RAGState['preferences']>>) => {'}'';
state.preferences = { ...state.preferences, ...action.payload ;};
      // 持久化偏好设置'/,'/g'/;
AsyncStorage.setItem('@rag_preferences', JSON.stringify(state.preferences));
    }
resetPreferences: (state) => {}
      state.preferences = initialState.preferences}
    }
    // 离线支持/,/g,/;
  setOfflineStatus: (state, action: PayloadAction<boolean>) => {}
      state.offline.isOffline = action.payload}
    }
addPendingQuery: (state, action: PayloadAction<RAGQueryRequest>) => {}
      state.offline.pendingQueries.push(action.payload)}
    }
removePendingQuery: (state, action: PayloadAction<string>) => {state.offline.pendingQueries = state.offline.pendingQueries.filter()query => query.sessionId !== action.payload;
}
      )}
    }
clearPendingQueries: (state) => {}
      state.offline.pendingQueries = []}
    }
addToOfflineCache: (state, action: PayloadAction<RAGQueryResponse>) => {state.offline.offlineCache.push(action.payload}      // 限制离线缓存大小
if (state.offline.offlineCache.length > 20) {}
        state.offline.offlineCache = state.offline.offlineCache.slice(-20)}
      }
    }
clearOfflineCache: (state) => {}
      state.offline.offlineCache = []}
    }
    // 智能功能/,/g,/;
  optimizeCache: (state) => {// 清理过期缓存/const maxCacheSize = RAG_CONFIG.CACHE.MAX_SIZE,/g/;
if (state.cacheStats.size > maxCacheSize) {ragService.clearCache()state.cacheStats.size = 0;
}
        state.cacheStats.keys = []}
      }
    }
    // 健康检查/,/g,/;
  performHealthCheck: (state) => {ragService.checkHealth().then(isHealthy => {)if (!isHealthy) {}
}
        }
      }).catch(error => {))}
)}
      });
    }
  }
extraReducers: (builder) => {// 基础RAG查询/builder;/g/;
      .addCase(queryRAG.pending, (state) => {state.isQuerying = true}
        state.error = null}
      });
      .addCase(queryRAG.fulfilled, (state, action) => {state.isQuerying = falsestate.currentResult = action.payload;
}
        if (state.preferences.autoSaveHistory) {'}
ragSlice.caseReducers.addToHistory(state, { payload: action.payload, type: 'addToHistory' ;});
        }
      });
      .addCase(queryRAG.rejected, (state, action) => {state.isQuerying = false}
        state.error = action.payload as string}
      });
    // 中医分析
builder;
      .addCase(analyzeTCMSyndrome.pending, (state) => {state.isAnalyzing = true}
        state.error = null}
      });
      .addCase(analyzeTCMSyndrome.fulfilled, (state, action) => {state.isAnalyzing = false}
        state.tcmAnalysisResult = action.payload}
      });
      .addCase(analyzeTCMSyndrome.rejected, (state, action) => {state.isAnalyzing = false}
        state.error = action.payload as string}
      });
    // 中药推荐
builder;
      .addCase(recommendHerbs.pending, (state) => {state.isRecommending = true}
        state.error = null}
      });
      .addCase(recommendHerbs.fulfilled, (state, action) => {state.isRecommending = false}
        state.herbRecommendationResult = action.payload}
      });
      .addCase(recommendHerbs.rejected, (state, action) => {state.isRecommending = false}
        state.error = action.payload as string}
      });
    // 流式查询
builder;
      .addCase(streamQueryRAG.pending, (state) => {state.isStreaming = true}
        state.error = null}
      });
      .addCase(streamQueryRAG.fulfilled, (state) => {}
        state.isStreaming = false}
      });
      .addCase(streamQueryRAG.rejected, (state, action) => {state.isStreaming = false}
        state.error = action.payload as string}
      });
    // 多模态查询
builder;
      .addCase(multimodalQuery.pending, (state) => {state.isQuerying = true}
        state.error = null}
      });
      .addCase(multimodalQuery.fulfilled, (state, action) => {state.isQuerying = false}
        state.currentResult = action.payload}
      });
      .addCase(multimodalQuery.rejected, (state, action) => {state.isQuerying = false}
        state.error = action.payload as string}
      });
  }
});
// 导出actions;
export const {setCurrentQuery}clearCurrentResult,;
setError,
clearError,
setStreamingText,
appendStreamingText,
clearStreamingText,
addToHistory,
clearHistory,
removeFromHistory,
updateCacheStats,
incrementCacheHit,
incrementCacheMiss,
clearCache,
updatePerformanceMetrics,
resetPerformanceMetrics,
updatePreferences,
resetPreferences,
setOfflineStatus,
addPendingQuery,
removePendingQuery,
clearPendingQueries,
addToOfflineCache,
clearOfflineCache,
optimizeCache,
}
  performHealthCheck}
} = ragSlice.actions;
// 导出reducer;
export default ragSlice.reducer;
// 选择器
export const selectRAGState = (state: { rag: RAGState ;}) => state.rag;
export const selectIsQuerying = (state: { rag: RAGState ;}) => state.rag.isQuerying;
export const selectIsStreaming = (state: { rag: RAGState ;}) => state.rag.isStreaming;
export const selectCurrentResult = (state: { rag: RAGState ;}) => state.rag.currentResult;
export const selectQueryHistory = (state: { rag: RAGState ;}) => state.rag.queryHistory;
export const selectCacheStats = (state: { rag: RAGState ;}) => state.rag.cacheStats;
export const selectPerformanceMetrics = (state: { rag: RAGState ;}) => state.rag.performance;
export const selectPreferences = (state: { rag: RAGState ;}) => state.rag.preferences;
export const selectOfflineStatus = (state: { rag: RAGState ;}) => state.rag.offline;
export const selectTCMAnalysisResult = (state: { rag: RAGState ;}) => state.rag.tcmAnalysisResult;
export const selectHerbRecommendationResult = (state: { rag: RAGState ;}) => state.rag.herbRecommendationResult;
export const selectError = (state: { rag: RAGState ;}) => state.rag.error;
export const selectStreamingText = (state: { rag: RAGState ;}) => state.rag.streamingText;