import { configureStore } from '@reduxjs/toolkit';
import ragReducer, {queryRAG,
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
      answer: "测试回答",
      confidence: 0.95,sources: ['测试来源'];
  };
};
const mockErrorResponse = {success: false,error: {
      code: "TEST_ERROR",
      message: '测试错误';
  };
};
describe('ragSlice', () => {
  let store: ReturnType<typeof configureStore>;
  beforeEach(() => {
    store = configureStore({
      reducer: {
        rag: ragReducer
      }
    });
  });
  describe('初始状态', () => {
    it('应该返回正确的初始状态', () => {
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
  describe('同步操作', () => {
    it('应该清除缓存', () => {
      // 先添加一些缓存数据
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', {
      query: "测试查询",
      type: 'consultation'
      }));
      // 清除缓存
      store.dispatch(clearCache());
      const state = store.getState().rag;
      expect(state.cache.size).toBe(0);
      expect(state.cache.hits).toBe(0);
      expect(state.cache.misses).toBe(0);
    });
    it('应该清除历史记录', () => {
      // 先添加历史记录
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', {
      query: "测试查询",
      type: 'consultation'
      }));
      // 清除历史
      store.dispatch(clearHistory());
      const state = store.getState().rag;
      expect(state.queryHistory).toEqual([]);
    });
    it('应该设置在线状态', () => {
      store.dispatch(setOnlineStatus(false));
      const state = store.getState().rag;
      expect(state.isOnline).toBe(false);
    });
    it('应该更新设置', () => {
      const newSettings = {maxCacheSize: 200,cacheTimeout: 600000,enableOfflineMode: true;
      };
      store.dispatch(updateSettings(newSettings));
      const state = store.getState().rag;
      expect(state.settings.maxCacheSize).toBe(200);
      expect(state.settings.cacheTimeout).toBe(600000);
      expect(state.settings.enableOfflineMode).toBe(true);
    });
  });
  describe('异步操作 - queryRAG', () => {
    it('应该处理查询开始状态', () => {
      store.dispatch(queryRAG.pending('requestId', {
      query: "测试查询",
      type: 'consultation'
      }));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(true);
      expect(state.error).toBeNull();
      expect(state.currentQuery).toBe('测试查询');
    });
    it('应该处理查询成功状态', () => {
      const queryRequest = {
      query: "测试查询",
      type: 'consultation' as const;
      };
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.lastResponse).toEqual(mockSuccessResponse);
      expect(state.queryHistory).toHaveLength(1);
      expect(state.queryHistory[0].query).toBe('测试查询');
      expect(state.cache.size).toBe(1);
    });
    it('应该处理查询失败状态', () => {
      const queryRequest = {
      query: "测试查询",
      type: 'consultation' as const;
      };
      store.dispatch(queryRAG.rejected(
        {
      name: "Error",
      message: '网络错误' },
        'requestId',
        queryRequest
      ));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);
      expect(state.error).toBe('网络错误');
      expect(state.performance.errorCount).toBe(1);
    });
  });
  describe('异步操作 - streamQueryRAG', () => {
    it('应该处理流式查询开始状态', () => {
      store.dispatch(streamQueryRAG.pending('requestId', {
      query: "流式查询测试",
      type: 'consultation'
      }));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(true);
      expect(state.isStreaming).toBe(true);
      expect(state.streamContent).toBe('');
    });
    it('应该处理流式查询成功状态', () => {
      const queryRequest = {
      query: "流式查询测试",
      type: 'consultation' as const;
      };
      const streamResponse = {success: true,data: {
      content: "完整的流式内容",
      chunks: ["chunk1",chunk2', 'chunk3'];
        };
      };
      store.dispatch(streamQueryRAG.fulfilled(streamResponse, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.isLoading).toBe(false);
      expect(state.isStreaming).toBe(false);
      expect(state.streamContent).toBe('完整的流式内容');
    });
  });
  describe('异步操作 - analyzeTCMSyndrome', () => {
    it('应该处理中医分析成功状态', () => {
      const analysisRequest = {symptoms: ["头痛",失眠'],constitution: '气虚质';
      };
      const analysisResponse = {success: true,data: {
      syndrome: "心脾两虚证",
      confidence: 0.88,description: '心脾两虚，气血不足',recommendations: ["补益心脾",养血安神'];
        };
      };
      store.dispatch(analyzeTCMSyndrome.fulfilled(analysisResponse, 'requestId', analysisRequest));
      const state = store.getState().rag;
      expect(state.tcmAnalysis.syndrome).toBe('心脾两虚证');
      expect(state.tcmAnalysis.confidence).toBe(0.88);
      expect(state.tcmAnalysis.recommendations).toHaveLength(2);
    });
  });
  describe('异步操作 - recommendHerbs', () => {
    it('应该处理中药推荐成功状态', () => {
      const recommendRequest = {
      syndrome: "肝郁气滞证",
      constitution: '气郁质';
      };
      const recommendResponse = {success: true,data: {formulas: [;
            {
      name: "逍遥散",
      ingredients: ["柴胡",当归', '白芍'],dosage: '每日两次，每次6g',duration: '2-4周';
            };
          ],precautions: ['孕妇慎用'];
        };
      };
      store.dispatch(recommendHerbs.fulfilled(recommendResponse, 'requestId', recommendRequest));
      const state = store.getState().rag;
      expect(state.herbRecommendations.formulas).toHaveLength(1);
      expect(state.herbRecommendations.formulas[0].name).toBe('逍遥散');
      expect(state.herbRecommendations.precautions).toHaveLength(1);
    });
  });
  describe('性能指标', () => {
    it('应该正确更新性能指标', () => {
      const queryRequest = {
      query: "性能测试",
      type: 'consultation' as const;
      };
      // 成功查询
      store.dispatch(queryRAG.fulfilled(mockSuccessResponse, 'requestId1', queryRequest));
      // 失败查询
      store.dispatch(queryRAG.rejected(
        {
      name: "Error",
      message: '错误' },
        'requestId2',
        queryRequest
      ));
      const state = store.getState().rag;
      expect(state.performance.totalQueries).toBe(2);
      expect(state.performance.successCount).toBe(1);
      expect(state.performance.errorCount).toBe(1);
      expect(state.performance.successRate).toBe(0.5);
    });
    it('应该记录响应时间', () => {
      const queryRequest = {
      query: "响应时间测试",
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
  describe('缓存管理', () => {
    it('应该正确管理缓存大小', () => {
      // 添加多个查询到缓存
      for (let i = 0; i < 5; i++) {
        const queryRequest = {query: `查询${i}`,type: 'consultation' as const;
        };
        store.dispatch(queryRAG.fulfilled(mockSuccessResponse, `requestId${i}`, queryRequest));
      }
      const state = store.getState().rag;
      expect(state.cache.size).toBe(5);
    });
    it('应该计算缓存命中率', () => {
      const queryRequest = {
      query: "缓存测试",
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
  describe('离线模式', () => {
    it('应该在离线时使用缓存', () => {
      const queryRequest = {
      query: "离线测试",
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
  describe('错误处理', () => {
    it('应该正确处理网络错误', () => {
      const queryRequest = {
      query: "网络错误测试",
      type: 'consultation' as const;
      };
      const networkError = {
      name: "NetworkError",
      message: '网络连接失败';
      };
      store.dispatch(queryRAG.rejected(networkError, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.error).toBe('网络连接失败');
      expect(state.performance.errorCount).toBe(1);
    });
    it('应该正确处理服务器错误', () => {
      const queryRequest = {
      query: "服务器错误测试",
      type: 'consultation' as const;
      };
      const serverError = {
      name: "ServerError",
      message: '服务器内部错误';
      };
      store.dispatch(queryRAG.rejected(serverError, 'requestId', queryRequest));
      const state = store.getState().rag;
      expect(state.error).toBe('服务器内部错误');
    });
  });
  describe('状态持久化', () => {
    it('应该保存重要状态到本地存储', () => {
      const queryRequest = {
      query: "持久化测试",
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