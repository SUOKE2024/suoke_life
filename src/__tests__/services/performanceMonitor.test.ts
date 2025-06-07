import { renderHook, act } from '@testing-library/react-hooks';
import { usePerformanceMonitor, usePerformanceContext } from '../../hooks/usePerformanceMonitor';

// Mock global performance API
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  memory: {
    usedJSHeapSize: 1024 * 1024 * 10, // 10MB
    totalJSHeapSize: 1024 * 1024 * 50, // 50MB
    jsHeapSizeLimit: 1024 * 1024 * 100, // 100MB
  }
};

Object.defineProperty(global, 'performance', {
  value: mockPerformance,
  writable: true
});

describe('usePerformanceMonitor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockPerformance.now.mockReturnValue(Date.now());
  });

  it('应该正确初始化性能监控', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    expect(result.current.isMonitoring).toBe(true);
    expect(result.current.config.trackRender).toBe(true);
    expect(result.current.config.enableLogging).toBe(true);
  });

  it('应该能够记录渲染性能', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    act(() => {
      result.current.recordRender();
    });

    const metrics = result.current.getCurrentMetrics();
    expect(metrics.updateCount).toBeGreaterThan(0);
  });

  it('应该能够记录内存使用', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent', { trackMemory: true })
    );

    act(() => {
      result.current.recordMemory();
    });

    const metrics = result.current.getCurrentMetrics();
    expect(metrics.memoryUsage).toBeGreaterThan(0);
  });

  it('应该能够记录网络性能', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent', { trackNetwork: true })
    );

    act(() => {
      result.current.recordNetwork('https://api.example.com', 150, true);
    });

    const metrics = result.current.getCurrentMetrics();
    expect(metrics.networkLatency).toBe(150);
  });

  it('应该能够记录自定义指标', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    act(() => {
      result.current.recordMetric('custom_metric', 100, { type: 'test' });
    });

    const events = result.current.getRecentEvents();
    expect(events).toHaveLength(1);
    expect(events[0].metadata?.metricName).toBe('custom_metric');
  });

  it('应该能够记录错误', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    const testError = new Error('Test error');

    act(() => {
      result.current.recordError(testError, { context: 'test' });
    });

    const metrics = result.current.getCurrentMetrics();
    expect(metrics.errorCount).toBe(1);

    const events = result.current.getRecentEvents();
    const errorEvent = events.find(e => e.type === 'error');
    expect(errorEvent).toBeDefined();
    expect(errorEvent?.metadata?.error.message).toBe('Test error');
  });

  it('应该正确处理性能阈值', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent', {
        warnThreshold: 10,
        errorThreshold: 50
      })
    );

    // 记录超过警告阈值的事件
    act(() => {
      result.current.recordEvent({
        type: 'render',
        timestamp: Date.now(),
        duration: 20, // 超过警告阈值10ms
        metadata: { test: true }
      });
    });

    const events = result.current.getRecentEvents();
    const warningEvent = events.find(e => e.type === 'warning');
    expect(warningEvent).toBeDefined();

    // 记录超过错误阈值的事件
    act(() => {
      result.current.recordEvent({
        type: 'render',
        timestamp: Date.now(),
        duration: 60, // 超过错误阈值50ms
        metadata: { test: true }
      });
    });

    const updatedEvents = result.current.getRecentEvents();
    const errorEvent = updatedEvents.find(e => e.type === 'error');
    expect(errorEvent).toBeDefined();
  });

  it('应该能够获取性能摘要', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    // 记录一些性能数据
    act(() => {
      result.current.recordRender();
      result.current.recordMemory();
      result.current.recordNetwork('https://api.example.com', 100);
    });

    const summary = result.current.getPerformanceSummary();
    
    expect(summary.componentName).toBe('TestComponent');
    expect(summary.totalRenders).toBeGreaterThan(0);
    expect(summary.mountTime).toBeGreaterThan(0);
    expect(summary.metrics).toBeDefined();
  });

  it('应该能够清除性能数据', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    // 记录一些数据
    act(() => {
      result.current.recordRender();
      result.current.recordError(new Error('Test'));
    });

    let metrics = result.current.getCurrentMetrics();
    expect(metrics.updateCount).toBeGreaterThan(0);
    expect(metrics.errorCount).toBeGreaterThan(0);

    // 清除数据
    act(() => {
      result.current.clearPerformanceData();
    });

    metrics = result.current.getCurrentMetrics();
    expect(metrics.updateCount).toBe(0);
    expect(metrics.errorCount).toBe(0);
  });

  it('应该能够启动和停止监控', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent')
    );

    expect(result.current.isMonitoring).toBe(true);

    act(() => {
      result.current.stopMonitoring();
    });

    expect(result.current.isMonitoring).toBe(false);

    act(() => {
      result.current.startMonitoring();
    });

    expect(result.current.isMonitoring).toBe(true);
  });

  it('应该正确处理采样率', () => {
    const { result } = renderHook(() => 
      usePerformanceMonitor('TestComponent', { sampleRate: 0 })
    );

    // 记录事件，但由于采样率为0，不应该被记录
    act(() => {
      result.current.recordEvent({
        type: 'render',
        timestamp: Date.now(),
        duration: 10
      });
    });

    const events = result.current.getRecentEvents();
    expect(events).toHaveLength(0);
  });

  it('应该正确处理配置更新', () => {
    const { result, rerender } = renderHook(
      ({ config }) => usePerformanceMonitor('TestComponent', config),
      {
        initialProps: { config: { trackRender: true, trackMemory: false } }
      }
    );

    expect(result.current.config.trackRender).toBe(true);
    expect(result.current.config.trackMemory).toBe(false);

    rerender({ config: { trackRender: false, trackMemory: true } });

    expect(result.current.config.trackRender).toBe(false);
    expect(result.current.config.trackMemory).toBe(true);
  });
});

describe('usePerformanceContext', () => {
  it('应该正确管理全局性能指标', () => {
    const { result } = renderHook(() => usePerformanceContext());

    const mockMetrics = {
      totalRenders: 10,
      averageRenderTime: 5.5,
      errorCount: 0
    };

    act(() => {
      result.current.registerComponent('TestComponent1', mockMetrics);
    });

    expect(result.current.globalMetrics['TestComponent1']).toEqual(mockMetrics);

    const summary = result.current.getGlobalSummary();
    expect(summary.totalComponents).toBe(1);
    expect(summary.totalRenders).toBe(10);
    expect(summary.averageRenderTime).toBe(5.5);
  });

  it('应该能够注销组件', () => {
    const { result } = renderHook(() => usePerformanceContext());

    const mockMetrics = { totalRenders: 5 };

    act(() => {
      result.current.registerComponent('TestComponent', mockMetrics);
    });

    expect(result.current.globalMetrics['TestComponent']).toBeDefined();

    act(() => {
      result.current.unregisterComponent('TestComponent');
    });

    expect(result.current.globalMetrics['TestComponent']).toBeUndefined();
  });

  it('应该正确计算全局摘要', () => {
    const { result } = renderHook(() => usePerformanceContext());

    act(() => {
      result.current.registerComponent('Component1', {
        totalRenders: 10,
        averageRenderTime: 5
      });
      result.current.registerComponent('Component2', {
        totalRenders: 20,
        averageRenderTime: 3
      });
    });

    const summary = result.current.getGlobalSummary();
    expect(summary.totalComponents).toBe(2);
    expect(summary.totalRenders).toBe(30);
    expect(summary.averageRenderTime).toBe(4); // (5 + 3) / 2
  });
}); 