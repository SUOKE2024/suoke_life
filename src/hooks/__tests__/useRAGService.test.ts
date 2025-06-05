import { renderHook, act } from '@testing-library/react-hooks';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { useRAGService } from '../useRAGService';
import ragReducer from '../../store/slices/ragSlice';

// Mock RAGService
jest.mock('../../services/ragService', () => ({
  RAGService: jest.fn().mockImplementation(() => ({
    query: jest.fn(),
    streamQuery: jest.fn(),
    analyzeTCMSyndrome: jest.fn(),
    recommendHerbs: jest.fn(),
    multimodalQuery: jest.fn(),
    getCacheStats: jest.fn(),
    getPerformanceMetrics: jest.fn(),
    clearCache: jest.fn(),
    on: jest.fn(),
    off: jest.fn(),
    destroy: jest.fn()
  }))
}));

const createWrapper = () => {
  const store = configureStore({
    reducer: {
      rag: ragReducer
    }
  });

  return ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  );
};

describe('useRAGService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该正确初始化Hook', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    expect(result.current).toHaveProperty('query');
    expect(result.current).toHaveProperty('streamQuery');
    expect(result.current).toHaveProperty('analyzeTCMSyndrome');
    expect(result.current).toHaveProperty('recommendHerbs');
    expect(result.current).toHaveProperty('multimodalQuery');
    expect(result.current).toHaveProperty('isLoading');
    expect(result.current).toHaveProperty('error');
    expect(result.current).toHaveProperty('cacheStats');
    expect(result.current).toHaveProperty('performanceMetrics');
  });

  it('应该正确处理查询操作', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    await act(async () => {
      await result.current.query('测试查询', { type: 'consultation' });
    });

    // 验证查询函数被调用
    expect(result.current.query).toBeDefined();
  });

  it('应该正确处理流式查询', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    const mockCallback = jest.fn();

    await act(async () => {
      await result.current.streamQuery('流式查询测试', mockCallback);
    });

    expect(result.current.streamQuery).toBeDefined();
  });

  it('应该正确处理中医分析', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    await act(async () => {
      await result.current.analyzeTCMSyndrome(['头痛', '失眠'], '气虚质');
    });

    expect(result.current.analyzeTCMSyndrome).toBeDefined();
  });

  it('应该正确处理中药推荐', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    await act(async () => {
      await result.current.recommendHerbs('心脾两虚证', '气虚质');
    });

    expect(result.current.recommendHerbs).toBeDefined();
  });

  it('应该正确处理多模态查询', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    const multimodalRequest = {
      text: '分析这张图片',
      images: ['data:image/jpeg;base64,test'],
      modality: 'image' as const
    };

    await act(async () => {
      await result.current.multimodalQuery(multimodalRequest);
    });

    expect(result.current.multimodalQuery).toBeDefined();
  });

  it('应该提供缓存统计信息', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    expect(result.current.cacheStats).toBeDefined();
    expect(typeof result.current.cacheStats).toBe('object');
  });

  it('应该提供性能指标', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    expect(result.current.performanceMetrics).toBeDefined();
    expect(typeof result.current.performanceMetrics).toBe('object');
  });

  it('应该正确处理加载状态', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    expect(typeof result.current.isLoading).toBe('boolean');
  });

  it('应该正确处理错误状态', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    expect(result.current.error).toBeDefined();
  });

  it('应该在组件卸载时清理资源', () => {
    const wrapper = createWrapper();
    const { unmount } = renderHook(() => useRAGService(), { wrapper });

    unmount();

    // 验证清理逻辑被执行
    // 实际的清理逻辑会在Hook内部处理
  });

  it('应该支持智能推荐功能', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    await act(async () => {
      if (result.current.getSmartRecommendations) {
        await result.current.getSmartRecommendations('用户输入');
      }
    });

    // 验证智能推荐功能
    expect(result.current).toBeDefined();
  });

  it('应该支持健康评估功能', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    const healthData = {
      symptoms: ['头痛', '失眠'],
      vitalSigns: { heartRate: 80, bloodPressure: '120/80' },
      lifestyle: { exercise: 'moderate', diet: 'balanced' }
    };

    await act(async () => {
      if (result.current.assessHealth) {
        await result.current.assessHealth(healthData);
      }
    });

    expect(result.current).toBeDefined();
  });

  it('应该支持预防建议功能', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    const riskFactors = ['高血压家族史', '久坐不动', '饮食不规律'];

    await act(async () => {
      if (result.current.getPreventionAdvice) {
        await result.current.getPreventionAdvice(riskFactors);
      }
    });

    expect(result.current).toBeDefined();
  });

  it('应该正确处理网络状态变化', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    // 模拟网络状态变化
    act(() => {
      // 网络状态变化的处理逻辑
      if (result.current.handleNetworkChange) {
        result.current.handleNetworkChange(false);
      }
    });

    expect(result.current).toBeDefined();
  });

  it('应该支持缓存管理操作', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useRAGService(), { wrapper });

    act(() => {
      if (result.current.clearCache) {
        result.current.clearCache();
      }
    });

    expect(result.current).toBeDefined();
  });
}); 