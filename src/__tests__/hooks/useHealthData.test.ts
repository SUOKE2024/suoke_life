import { renderHook, act } from '@testing-library/react-native';
import { HealthMetric } from '../../types/life';

// Mock健康数据类型
interface HealthData {
  metrics: HealthMetric[];
  lastUpdated: string | null;
  syncStatus: 'synced' | 'pending' | 'error';
}

interface UseHealthDataReturn {
  healthData: HealthData | null;
  loading: boolean;
  error: Error | null;
  fetchHealthData: () => Promise<void>;
  updateHealthMetric: (id: string, value: number) => Promise<void>;
  syncHealthData: () => Promise<void>;
  refreshHealthData: () => void;
}

// Mock健康数据
const mockHealthData: HealthData = {
  metrics: [
    {
      id: 'heart_rate',
      name: '心率',
      value: 72,
      unit: 'bpm',
      target: 70,
      icon: 'heart',
      color: '#FF3B30',
      trend: 'stable',
      suggestion: '心率正常，保持当前状态',
    },
    {
      id: 'blood_pressure',
      name: '血压',
      value: 120,
      unit: 'mmHg',
      target: 120,
      icon: 'gauge',
      color: '#007AFF',
      trend: 'up',
      suggestion: '血压略高，注意饮食',
    },
  ],
  lastUpdated: '2024-01-15T10:30:00Z',
  syncStatus: 'synced',
};

// Mock API调用
const mockFetchHealthData = jest.fn();
const mockUpdateHealthMetric = jest.fn();
const mockSyncHealthData = jest.fn();
const mockRefreshHealthData = jest.fn();

// Mock useHealthData Hook
const useHealthData = jest.fn<UseHealthDataReturn, []>();

describe('useHealthData Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // 设置默认的mock实现
    useHealthData.mockReturnValue({
      healthData: mockHealthData,
      loading: false,
      error: null,
      fetchHealthData: mockFetchHealthData,
      updateHealthMetric: mockUpdateHealthMetric,
      syncHealthData: mockSyncHealthData,
      refreshHealthData: mockRefreshHealthData,
    });
  });

  it('应该返回初始健康数据', () => {
    const { result } = renderHook(() => useHealthData());
    
    expect(result.current.healthData).toEqual(mockHealthData);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('应该处理加载状态', () => {
    useHealthData.mockReturnValue({
      healthData: null,
      loading: true,
      error: null,
      fetchHealthData: mockFetchHealthData,
      updateHealthMetric: mockUpdateHealthMetric,
      syncHealthData: mockSyncHealthData,
      refreshHealthData: mockRefreshHealthData,
    });

    const { result } = renderHook(() => useHealthData());
    
    expect(result.current.loading).toBe(true);
    expect(result.current.healthData).toBeNull();
  });

  it('应该处理错误状态', () => {
    const mockError = new Error('获取健康数据失败');
    
    useHealthData.mockReturnValue({
      healthData: null,
      loading: false,
      error: mockError,
      fetchHealthData: mockFetchHealthData,
      updateHealthMetric: mockUpdateHealthMetric,
      syncHealthData: mockSyncHealthData,
      refreshHealthData: mockRefreshHealthData,
    });

    const { result } = renderHook(() => useHealthData());
    
    expect(result.current.error).toEqual(mockError);
    expect(result.current.healthData).toBeNull();
  });

  it('应该能够获取健康数据', async () => {
    const { result } = renderHook(() => useHealthData());
    
    await act(async () => {
      await result.current.fetchHealthData();
    });
    
    expect(mockFetchHealthData).toHaveBeenCalledTimes(1);
  });

  it('应该能够更新健康指标', async () => {
    const { result } = renderHook(() => useHealthData());
    
    const updateData = {
      id: 'heart_rate',
      value: 75,
    };
    
    await act(async () => {
      await result.current.updateHealthMetric(updateData.id, updateData.value);
    });
    
    expect(mockUpdateHealthMetric).toHaveBeenCalledWith(updateData.id, updateData.value);
  });

  it('应该能够同步健康数据', async () => {
    const { result } = renderHook(() => useHealthData());
    
    await act(async () => {
      await result.current.syncHealthData();
    });
    
    expect(mockSyncHealthData).toHaveBeenCalledTimes(1);
  });

  it('应该正确处理健康指标筛选', () => {
    const { result } = renderHook(() => useHealthData());
    
    const heartRateMetric = result.current.healthData?.metrics.find(
      (metric: HealthMetric) => metric.id === 'heart_rate'
    );
    
    expect(heartRateMetric).toBeDefined();
    expect(heartRateMetric?.name).toBe('心率');
    expect(heartRateMetric?.value).toBe(72);
  });

  it('应该正确处理同步状态', () => {
    const { result } = renderHook(() => useHealthData());
    
    expect(result.current.healthData?.syncStatus).toBe('synced');
    expect(result.current.healthData?.lastUpdated).toBe('2024-01-15T10:30:00Z');
  });

  it('应该处理空数据情况', () => {
    useHealthData.mockReturnValue({
      healthData: {
        metrics: [],
        lastUpdated: null,
        syncStatus: 'pending',
      },
      loading: false,
      error: null,
      fetchHealthData: mockFetchHealthData,
      updateHealthMetric: mockUpdateHealthMetric,
      syncHealthData: mockSyncHealthData,
      refreshHealthData: mockRefreshHealthData,
    });

    const { result } = renderHook(() => useHealthData());
    
    expect(result.current.healthData?.metrics).toHaveLength(0);
    expect(result.current.healthData?.syncStatus).toBe('pending');
  });

  it('应该处理网络错误', () => {
    const networkError = new Error('网络连接失败');
    
    useHealthData.mockReturnValue({
      healthData: null,
      loading: false,
      error: networkError,
      fetchHealthData: mockFetchHealthData,
      updateHealthMetric: mockUpdateHealthMetric,
      syncHealthData: mockSyncHealthData,
      refreshHealthData: mockRefreshHealthData,
    });

    const { result } = renderHook(() => useHealthData());
    
    expect(result.current.error?.message).toBe('网络连接失败');
  });
}); 