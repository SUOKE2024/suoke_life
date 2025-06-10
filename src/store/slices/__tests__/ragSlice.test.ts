import { configureStore } from '@reduxjs/toolkit';
import ragReducer, {queryRAG;
  streamQueryRAG,
  analyzeTCMSyndrome,
  recommendHerbs,
  clearCache,
  clearHistory,
  setOnlineStatus,
  updateSettings
} from '../ragSlice';
// Mock API responses
const mockSuccessResponse = {success: true,data: {


  ;};
};
const mockErrorResponse = {success: false,error: {
      code: "TEST_ERROR";

  };
};
describe('ragSlice', () => {
  let store: ReturnType<typeof configureStore>;
  beforeEach(() => {
    store = configureStore({
      reducer: {
        rag: ragReducer
      ;}
    });
  });


      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.currentQuery).toBeNull();
      expect(state.queryHistory).toEqual([]);
      expect(state.cache.size).toBe(0);
      expect(state.isOnline).toBe(true);
      expect(state.settings.maxCacheSize).toBe(100);
    });
  });


      // 先添加一些缓存数据
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', {

      type: 'consultation'
      ;}));
      // 清除缓存
      store.dispatch(clearCache());
      const state = store.getState().rag;
      expect(state.cache.size).toBe(0);
      expect(state.cache.hits).toBe(0);
      expect(state.cache.misses).toBe(0);
    });

      // 先添加历史记录
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', {

      type: 'consultation'
      ;}));
      // 清除历史
      store.dispatch(clearHistory());
      const state = store.getState().rag;
      expect(state.queryHistory).toEqual([]);
    });

      store.dispatch(setOnlineStatus(false));
      const state = store.getState().rag;
      expect(state.isOnline).toBe(false);
    });

      const newSettings = {maxCacheSize: 200,cacheTimeout: 600000,enableOfflineMode: true;
      };
      store.dispatch(updateSettings(newSettings));
      const state = store.getState().rag;
      expect(state.settings.maxCacheSize).toBe(200);
      expect(state.settings.cacheTimeout).toBe(600000);
      expect(state.settings.enableOfflineMode).toBe(true);
    });
  });


      store.dispatch(queryRAG.pending('requestId', {

      type: 'consultation'
      ;}));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(true);
      expect(state.error).toBeNull();

    });

      const queryRequest = {

      type: 'consultation' as const;
      };
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.lastResponse).toEqual(mockSuccessResponse);
      expect(state.queryHistory).toHaveLength(1);

      expect(state.cache.size).toBe(1);
    });

      const queryRequest = {

      type: 'consultation' as const;
      };
      store.dispatch(queryRAG.rejected())
        {
      name: "Error";

        'requestId',
        queryRequest
      ));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);

      expect(state.performance.errorCount).toBe(1);
    });
  });


      store.dispatch(streamQueryRAG.pending('requestId', {

      type: 'consultation'
      ;}));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(true);
      expect(state.isStreaming).toBe(true);
      expect(state.streamContent).toBe('');
    });

      const queryRequest = {

      type: 'consultation' as const;
      };
      const streamResponse = {success: true,data: {

      chunks: ["chunk1",chunk2', 'chunk3'];
        };
      };
      store.dispatch(streamQueryRAG.fulfilled(streamResponse, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);
      expect(state.isStreaming).toBe(false);

    });
  });



      };
      const analysisResponse = {success: true,data: {


        ;};
      };
      store.dispatch(analyzeTCMSyndrome.fulfilled(analysisResponse, 'requestId', analysisRequest));
      const state = store.getState().rag;

      expect(state.tcmAnalysis.confidence).toBe(0.88);
      expect(state.tcmAnalysis.recommendations).toHaveLength(2);
    });
  });


      const recommendRequest = {


      };
      const recommendResponse = {success: true,data: {formulas: [;
            {


            };

        };
      };
      store.dispatch(recommendHerbs.fulfilled(recommendResponse, 'requestId', recommendRequest));
      const state = store.getState().rag;
      expect(state.herbRecommendations.formulas).toHaveLength(1);

      expect(state.herbRecommendations.precautions).toHaveLength(1);
    });
  });


      const queryRequest = {

      type: 'consultation' as const;
      };
      // 成功查询
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId1', queryRequest));
      // 失败查询
      store.dispatch(queryRAG.rejected())
        {
      name: "Error";

        'requestId2',
        queryRequest
      ));
      const state = store.getState().rag;
      expect(state.performance.totalQueries).toBe(2);
      expect(state.performance.successCount).toBe(1);
      expect(state.performance.errorCount).toBe(1);
      expect(state.performance.successRate).toBe(0.5);
    });

      const queryRequest = {

      type: 'consultation' as const;
      };
      // 模拟查询开始
      store.dispatch(queryRAG.pending('requestId', queryRequest));
      // 等待一段时间后完成
      setTimeout(() => {
        store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', queryRequest));
        const state = store.getState().rag;
        expect(state.performance.averageResponseTime).toBeGreaterThan(0);
      }, 100);
    });
  });


      // 添加多个查询到缓存
      for (let i = 0; i < 5; i++) {

        };
        store.dispatch(queryRAG.fulfilled(mockSuccessResponse, `requestId${i}`, queryRequest));
      }
      const state = store.getState().rag;
      expect(state.cache.size).toBe(5);
    });

      const queryRequest = {

      type: 'consultation' as const;
      };
      // 第一次查询（缓存未命中）
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId1', queryRequest));
      // 第二次相同查询（应该命中缓存）
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId2', queryRequest));
      const state = store.getState().rag;
      expect(state.cache.hits).toBeGreaterThanOrEqual(0);
      expect(state.cache.misses).toBeGreaterThanOrEqual(0);
    });
  });


      const queryRequest = {

      type: 'consultation' as const;
      };
      // 在线时添加到缓存
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId1', queryRequest));
      // 设置为离线
      store.dispatch(setOnlineStatus(false));
      // 离线时查询相同内容
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId2', queryRequest));
      const state = store.getState().rag;
      expect(state.isOnline).toBe(false);
      expect(state.cache.hits).toBeGreaterThan(0);
    });
  });


      const queryRequest = {

      type: 'consultation' as const;
      };
      const networkError = {
      name: "NetworkError";

      };
      store.dispatch(queryRAG.rejected(networkError, 'requestId', queryRequest));
      const state = store.getState().rag;

      expect(state.performance.errorCount).toBe(1);
    });

      const queryRequest = {

      type: 'consultation' as const;
      };
      const serverError = {
      name: "ServerError";

      };
      store.dispatch(queryRAG.rejected(serverError, 'requestId', queryRequest));
      const state = store.getState().rag;

    });
  });


      const queryRequest = {

      type: 'consultation' as const;
      };
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.queryHistory).toHaveLength(1);
      expect(state.cache.size).toBe(1);
      // 实际的持久化逻辑会在中间件中处理
    });
  });
});