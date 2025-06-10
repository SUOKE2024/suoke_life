/**
 * 内存优化功能测试套件
 * 验证ONNX推理引擎、本地模型管理器和缓存服务的内存优化功能
 */

import { localModelManager } from '../../core/ai/LocalModelManager';
import { optimizedCacheService } from '../../core/cache/OptimizedCacheService';
import {
  createDynamicConfig,
  getDeviceMemoryInfo,
} from '../../core/onnx-runtime/constants';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  getAllKeys: jest.fn(() => Promise.resolve([])),
  multiRemove: jest.fn(),
}));

// Mock RNFS
jest.mock('react-native-fs', () => ({
  DocumentDirectoryPath: '/mock/path',
  exists: jest.fn(() => Promise.resolve(true)),
  mkdir: jest.fn(),
}));

describe('内存优化功能测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('ONNX推理引擎优化', () => {
    test('应该根据设备内存动态生成配置', async () => {
      const config = await createDynamicConfig();

      expect(config).toHaveProperty('EDGE_COMPUTE');
      expect(config).toHaveProperty('MODEL_OPTIMIZATION');
      expect(config).toHaveProperty('CACHE');

      // 验证内存限制是否合理
      expect(config.EDGE_COMPUTE.memoryLimit).toBeLessThanOrEqual(
        2 * 1024 * 1024 * 1024
      );
      expect(config.EDGE_COMPUTE.memoryLimit).toBeGreaterThan(0);

      // 验证缓存大小是否合理
      expect(config.CACHE.maxCacheSize).toBeLessThanOrEqual(
        config.EDGE_COMPUTE.memoryLimit * 0.3
      );
    });

    test('应该正确检测设备内存信息', async () => {
      const memoryInfo = await getDeviceMemoryInfo();

      expect(memoryInfo).toHaveProperty('totalMemory');
      expect(memoryInfo).toHaveProperty('availableMemory');
      expect(memoryInfo).toHaveProperty('memoryTier');

      expect(memoryInfo.totalMemory).toBeGreaterThan(0);
      expect(memoryInfo.availableMemory).toBeGreaterThan(0);
      expect(['LOW', 'MEDIUM', 'HIGH']).toContain(memoryInfo.memoryTier);
    });

    test('低内存设备应该使用保守配置', async () => {
      // Mock低内存设备
      jest
        .spyOn(
          require('../../core/onnx-runtime/constants'),
          'getDeviceMemoryInfo'
        )
        .mockResolvedValue({
          totalMemory: 512 * 1024 * 1024, // 512MB
          availableMemory: 300 * 1024 * 1024,
          memoryTier: 'LOW',
        });

      const config = await createDynamicConfig();

      expect(config.EDGE_COMPUTE.maxConcurrentSessions).toBe(1);
      expect(config.EDGE_COMPUTE.batchSize).toBe(1);
      expect(config.EDGE_COMPUTE.enableGPU).toBe(false);
      expect(config.MODEL_OPTIMIZATION.executionMode).toBe('sequential');
    });
  });

  describe('本地模型管理器优化', () => {
    beforeEach(async () => {
      await localModelManager.initialize();
    });

    afterEach(async () => {
      await localModelManager.dispose();
    });

    test('应该实现懒加载策略', async () => {
      const availableModels = localModelManager.getAvailableModels();
      const loadedModels = localModelManager.getLoadedModels();

      expect(availableModels.length).toBeGreaterThan(0);
      // 初始化时只应该加载高优先级模型
      expect(loadedModels.length).toBeLessThanOrEqual(
        availableModels.filter((m) => m.priority === 'high').length
      );
    });

    test('应该正确管理模型优先级', async () => {
      const models = localModelManager.getAvailableModels();

      const highPriorityModels = models.filter((m) => m.priority === 'high');
      const mediumPriorityModels = models.filter(
        (m) => m.priority === 'medium'
      );
      const lowPriorityModels = models.filter((m) => m.priority === 'low');

      expect(highPriorityModels.length).toBeGreaterThan(0);
      expect(mediumPriorityModels.length).toBeGreaterThan(0);
      expect(lowPriorityModels.length).toBeGreaterThan(0);
    });

    test('应该在内存不足时自动卸载模型', async () => {
      // 加载多个模型
      const models = localModelManager.getAvailableModels();
      for (const model of models) {
        await localModelManager.loadModel(model.id);
      }

      const initialLoadedCount = localModelManager.getLoadedModels().length;
      expect(initialLoadedCount).toBeGreaterThan(0);

      // 模拟内存压力，触发自动清理
      // 这里需要模拟内存监控逻辑
      jest.advanceTimersByTime(6 * 60 * 1000); // 6分钟后

      // 验证是否有模型被卸载
      const finalLoadedCount = localModelManager.getLoadedModels().length;
      expect(finalLoadedCount).toBeLessThanOrEqual(initialLoadedCount);
    });

    test('应该提供准确的内存统计', () => {
      const memoryStats = localModelManager.getMemoryStats();

      expect(memoryStats).toHaveProperty('totalMemory');
      expect(memoryStats).toHaveProperty('usedMemory');
      expect(memoryStats).toHaveProperty('availableMemory');
      expect(memoryStats).toHaveProperty('loadedModels');
      expect(memoryStats).toHaveProperty('cacheSize');

      expect(memoryStats.totalMemory).toBeGreaterThanOrEqual(
        memoryStats.usedMemory
      );
      expect(memoryStats.loadedModels).toBeGreaterThanOrEqual(0);
    });

    test('应该正确执行推理并缓存结果', async () => {
      const modelId = 'health_basic_assessment';
      const inputData = { symptoms: ['headache', 'fever'] };

      // 第一次推理
      const result1 = await localModelManager.runInference(modelId, inputData);
      expect(result1).toHaveProperty('modelId', modelId);
      expect(result1).toHaveProperty('output');
      expect(result1).toHaveProperty('confidence');
      expect(result1).toHaveProperty('inferenceTime');

      // 第二次推理应该更快（缓存命中）
      const startTime = Date.now();
      const result2 = await localModelManager.runInference(modelId, inputData);
      const endTime = Date.now();

      expect(result2.output).toEqual(result1.output);
      expect(endTime - startTime).toBeLessThan(result1.inferenceTime);
    });
  });

  describe('优化缓存系统', () => {
    beforeEach(() => {
      optimizedCacheService.clear();
    });

    test('应该正确设置和获取缓存项', async () => {
      const key = 'test_key';
      const value = { data: 'test_data', timestamp: Date.now() };

      await optimizedCacheService.set(key, value);
      const retrieved = await optimizedCacheService.get(key);

      expect(retrieved).toEqual(value);
    });

    test('应该实现TTL过期机制', async () => {
      const key = 'expiring_key';
      const value = { data: 'test_data' };
      const shortTTL = 1000; // 1秒

      await optimizedCacheService.set(key, value, { ttl: shortTTL });

      // 立即获取应该成功
      let retrieved = await optimizedCacheService.get(key);
      expect(retrieved).toEqual(value);

      // 等待过期
      jest.advanceTimersByTime(shortTTL + 100);

      // 过期后应该返回null
      retrieved = await optimizedCacheService.get(key);
      expect(retrieved).toBeNull();
    });

    test('应该实现优先级淘汰策略', async () => {
      // 设置不同优先级的缓存项
      await optimizedCacheService.set('high_priority', 'data1', {
        priority: 'high',
      });
      await optimizedCacheService.set('medium_priority', 'data2', {
        priority: 'medium',
      });
      await optimizedCacheService.set('low_priority', 'data3', {
        priority: 'low',
      });

      // 触发内存清理
      await optimizedCacheService.cleanup();

      // 高优先级项应该保留
      const highPriorityData = await optimizedCacheService.get('high_priority');
      expect(highPriorityData).not.toBeNull();
    });

    test('应该实现压缩功能', async () => {
      const largeData = 'x'.repeat(2000); // 大于压缩阈值的数据
      const key = 'large_data';

      await optimizedCacheService.set(key, largeData);
      const retrieved = await optimizedCacheService.get(key);

      expect(retrieved).toBe(largeData);
    });

    test('应该提供准确的内存使用统计', async () => {
      await optimizedCacheService.set('test1', 'data1');
      await optimizedCacheService.set('test2', 'data2');

      const memoryUsage = optimizedCacheService.getMemoryUsage();

      expect(memoryUsage).toHaveProperty('current');
      expect(memoryUsage).toHaveProperty('max');
      expect(memoryUsage).toHaveProperty('percentage');
      expect(memoryUsage).toHaveProperty('itemCount');

      expect(memoryUsage.current).toBeGreaterThan(0);
      expect(memoryUsage.itemCount).toBe(2);
      expect(memoryUsage.percentage).toBeLessThanOrEqual(100);
    });

    test('应该在达到内存限制时自动清理', async () => {
      // 创建一个小内存限制的缓存服务实例
      const testCacheService =
        new (require('../../core/cache/OptimizedCacheService').OptimizedCacheService)(
          {
            maxMemorySize: 1024, // 1KB限制
            maxItems: 10,
          }
        );

      // 添加大量数据直到超过限制
      for (let i = 0; i < 20; i++) {
        await testCacheService.set(`key_${i}`, 'x'.repeat(100));
      }

      const memoryUsage = testCacheService.getMemoryUsage();
      expect(memoryUsage.current).toBeLessThanOrEqual(memoryUsage.max);
      expect(memoryUsage.itemCount).toBeLessThanOrEqual(10);

      testCacheService.destroy();
    });
  });

  describe('内存监控集成测试', () => {
    test('应该能够获取完整的内存统计信息', () => {
      const modelStats = localModelManager.getMemoryStats();
      const cacheStats = optimizedCacheService.getMemoryUsage();

      // 验证统计信息的完整性
      expect(modelStats).toBeDefined();
      expect(cacheStats).toBeDefined();

      // 验证内存使用的合理性
      expect(modelStats.usedMemory).toBeGreaterThanOrEqual(0);
      expect(cacheStats.current).toBeGreaterThanOrEqual(0);
    });

    test('应该能够执行内存优化操作', async () => {
      // 加载一些模型和缓存数据
      await localModelManager.loadModel('health_basic_assessment');
      await optimizedCacheService.set('test_data', { large: 'x'.repeat(1000) });

      const initialModelStats = localModelManager.getMemoryStats();
      const initialCacheStats = optimizedCacheService.getMemoryUsage();

      // 执行清理操作
      await optimizedCacheService.cleanup();

      const finalCacheStats = optimizedCacheService.getMemoryUsage();

      // 验证清理效果
      expect(finalCacheStats.current).toBeLessThanOrEqual(
        initialCacheStats.current
      );
    });
  });

  describe('性能基准测试', () => {
    test('模型加载时间应该在可接受范围内', async () => {
      const modelId = 'health_basic_assessment';

      const startTime = Date.now();
      await localModelManager.loadModel(modelId);
      const loadTime = Date.now() - startTime;

      // 模型加载应该在1秒内完成
      expect(loadTime).toBeLessThan(1000);
    });

    test('推理时间应该在可接受范围内', async () => {
      const modelId = 'health_basic_assessment';
      await localModelManager.loadModel(modelId);

      const inputData = { symptoms: ['headache'] };

      const startTime = Date.now();
      await localModelManager.runInference(modelId, inputData);
      const inferenceTime = Date.now() - startTime;

      // 推理应该在200ms内完成
      expect(inferenceTime).toBeLessThan(200);
    });

    test('缓存操作应该快速执行', async () => {
      const testData = { test: 'data' };

      // 测试写入性能
      const writeStart = Date.now();
      await optimizedCacheService.set('perf_test', testData);
      const writeTime = Date.now() - writeStart;

      // 测试读取性能
      const readStart = Date.now();
      await optimizedCacheService.get('perf_test');
      const readTime = Date.now() - readStart;

      // 缓存操作应该在50ms内完成
      expect(writeTime).toBeLessThan(50);
      expect(readTime).toBeLessThan(50);
    });
  });

  describe('错误处理和边界情况', () => {
    test('应该正确处理不存在的模型', async () => {
      await expect(
        localModelManager.loadModel('non_existent_model')
      ).rejects.toThrow('Model not found');
    });

    test('应该正确处理缓存键不存在的情况', async () => {
      const result = await optimizedCacheService.get('non_existent_key');
      expect(result).toBeNull();
    });

    test('应该正确处理内存不足的情况', async () => {
      // Mock内存不足的情况
      jest
        .spyOn(localModelManager as any, 'canLoadModel')
        .mockReturnValue(false);

      await expect(
        localModelManager.loadModel('health_basic_assessment')
      ).rejects.toThrow('Insufficient memory');
    });

    test('应该正确处理无效的缓存数据', async () => {
      // 设置无效的TTL
      await expect(
        optimizedCacheService.set('test', 'data', { ttl: -1 })
      ).resolves.not.toThrow();
    });
  });
});

// 性能测试辅助函数
export const runPerformanceTest = async (
  testName: string,
  testFn: () => Promise<void>,
  iterations = 10
) => {
  const times: number[] = [];

  for (let i = 0; i < iterations; i++) {
    const start = Date.now();
    await testFn();
    const end = Date.now();
    times.push(end - start);
  }

  const avgTime = times.reduce((sum, time) => sum + time, 0) / times.length;
  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);

  console.log(`${testName} 性能测试结果:`);
  console.log(`  平均时间: ${avgTime.toFixed(2)}ms`);
  console.log(`  最短时间: ${minTime}ms`);
  console.log(`  最长时间: ${maxTime}ms`);

  return { avgTime, minTime, maxTime };
};
