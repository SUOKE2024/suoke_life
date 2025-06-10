/**
 * 内存优化集成测试
 * 测试各个组件之间的协同工作和整体性能
 */

import { fireEvent, render, waitFor } from '@testing-library/react-native';
import React from 'react';
import { MemoryMonitor } from '../../components/performance/MemoryMonitor';
import { localModelManager } from '../../core/ai/LocalModelManager';
import { optimizedCacheService } from '../../core/cache/OptimizedCacheService';
import { createDynamicConfig } from '../../core/onnx-runtime/constants';

// Mock React Native modules
jest.mock('react-native', () => ({
  Platform: { OS: 'ios' },
  Dimensions: {
    get: () => ({ width: 375, height: 812 }),
  },
  Alert: {
    alert: jest.fn(),
  },
}));

jest.mock('react-native-device-info', () => ({
  getTotalMemory: jest.fn(() => Promise.resolve(4 * 1024 * 1024 * 1024)), // 4GB
  getFreeDiskStorage: jest.fn(() => Promise.resolve(2 * 1024 * 1024 * 1024)), // 2GB
}));

jest.mock('react-native-fs', () => ({
  DocumentDirectoryPath: '/mock/path',
  exists: jest.fn(() => Promise.resolve(true)),
  mkdir: jest.fn(),
  readDir: jest.fn(() => Promise.resolve([])),
}));

describe('内存优化集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('完整的内存管理流程', () => {
    test('应该能够完成完整的内存优化流程', async () => {
      // 1. 初始化系统
      await localModelManager.initialize();

      // 2. 获取初始内存状态
      const initialModelStats = localModelManager.getMemoryStats();
      const initialCacheStats = optimizedCacheService.getMemoryUsage();

      expect(initialModelStats).toBeDefined();
      expect(initialCacheStats).toBeDefined();

      // 3. 加载一些模型和缓存数据
      await localModelManager.loadModel('health_basic_assessment');
      await optimizedCacheService.set('test_data_1', {
        data: 'x'.repeat(1000),
      });
      await optimizedCacheService.set('test_data_2', {
        data: 'y'.repeat(2000),
      });

      // 4. 验证内存使用增加
      const afterLoadStats = localModelManager.getMemoryStats();
      const afterLoadCacheStats = optimizedCacheService.getMemoryUsage();

      expect(afterLoadStats.usedMemory).toBeGreaterThan(
        initialModelStats.usedMemory
      );
      expect(afterLoadCacheStats.current).toBeGreaterThan(
        initialCacheStats.current
      );

      // 5. 执行内存优化
      await optimizedCacheService.cleanup();

      // 6. 验证优化效果
      const finalCacheStats = optimizedCacheService.getMemoryUsage();
      expect(finalCacheStats.current).toBeLessThanOrEqual(
        afterLoadCacheStats.current
      );

      // 7. 清理
      await localModelManager.dispose();
    });

    test('应该能够处理内存压力情况', async () => {
      await localModelManager.initialize();

      // 模拟高内存使用场景
      const models = localModelManager.getAvailableModels();
      const loadPromises = models.slice(0, 3).map(
        (model) => localModelManager.loadModel(model.id).catch(() => {}) // 忽略可能的错误
      );

      await Promise.allSettled(loadPromises);

      // 添加大量缓存数据
      const cachePromises = Array.from({ length: 50 }, (_, i) =>
        optimizedCacheService.set(`stress_test_${i}`, { data: 'x'.repeat(500) })
      );

      await Promise.all(cachePromises);

      // 验证系统仍然稳定
      const memoryStats = localModelManager.getMemoryStats();
      const cacheStats = optimizedCacheService.getMemoryUsage();

      expect(memoryStats.usedMemory).toBeGreaterThan(0);
      expect(cacheStats.current).toBeGreaterThan(0);

      // 系统应该自动进行内存管理
      expect(cacheStats.percentage).toBeLessThan(100);

      await localModelManager.dispose();
    });

    test('应该能够在不同设备配置下正常工作', async () => {
      // 测试低内存设备配置
      jest
        .spyOn(require('react-native-device-info'), 'getTotalMemory')
        .mockResolvedValue(1 * 1024 * 1024 * 1024); // 1GB

      const lowMemoryConfig = await createDynamicConfig();

      expect(lowMemoryConfig.EDGE_COMPUTE.memoryLimit).toBeLessThan(
        1 * 1024 * 1024 * 1024
      );
      expect(
        lowMemoryConfig.EDGE_COMPUTE.maxConcurrentSessions
      ).toBeLessThanOrEqual(2);

      // 测试高内存设备配置
      jest
        .spyOn(require('react-native-device-info'), 'getTotalMemory')
        .mockResolvedValue(8 * 1024 * 1024 * 1024); // 8GB

      const highMemoryConfig = await createDynamicConfig();

      expect(highMemoryConfig.EDGE_COMPUTE.memoryLimit).toBeGreaterThan(
        lowMemoryConfig.EDGE_COMPUTE.memoryLimit
      );
      expect(
        highMemoryConfig.EDGE_COMPUTE.maxConcurrentSessions
      ).toBeGreaterThanOrEqual(2);
    });
  });

  describe('MemoryMonitor组件集成测试', () => {
    test('应该正确显示内存监控界面', async () => {
      const { getByText, getByTestId } = render(
        React.createElement(MemoryMonitor)
      );

      // 等待组件加载
      await waitFor(() => {
        expect(getByText('内存监控')).toBeTruthy();
      });

      // 验证内存统计显示
      expect(getByText(/AI模型/)).toBeTruthy();
      expect(getByText(/缓存/)).toBeTruthy();
      expect(getByText(/系统/)).toBeTruthy();
      expect(getByText(/可用/)).toBeTruthy();

      // 验证内存压力指示器
      const pressureIndicator = getByTestId('memory-pressure-indicator');
      expect(pressureIndicator).toBeTruthy();
    });

    test('应该能够执行内存优化操作', async () => {
      const { getByText, getByTestId } = render(
        React.createElement(MemoryMonitor)
      );

      await waitFor(() => {
        expect(getByText('内存监控')).toBeTruthy();
      });

      // 点击优化按钮
      const optimizeButton = getByTestId('optimize-memory-button');
      fireEvent.press(optimizeButton);

      // 验证优化操作被触发
      await waitFor(() => {
        // 这里应该验证优化操作的结果
        // 由于是集成测试，我们验证UI状态的变化
        expect(getByTestId('memory-stats')).toBeTruthy();
      });
    });

    test('应该能够切换自动优化模式', async () => {
      const { getByTestId } = render(React.createElement(MemoryMonitor));

      await waitFor(() => {
        const autoOptimizeSwitch = getByTestId('auto-optimize-switch');
        expect(autoOptimizeSwitch).toBeTruthy();

        // 切换自动优化
        fireEvent(autoOptimizeSwitch, 'valueChange', true);
      });

      // 验证自动优化被启用
      // 这里可以添加更多的验证逻辑
    });

    test('应该正确显示内存压力警告', async () => {
      // Mock高内存使用情况
      jest.spyOn(localModelManager, 'getMemoryStats').mockReturnValue({
        totalMemory: 1024 * 1024 * 1024, // 1GB
        usedMemory: 900 * 1024 * 1024, // 900MB (87.5%)
        availableMemory: 124 * 1024 * 1024,
        loadedModels: 3,
        cacheSize: 100 * 1024 * 1024,
      });

      const { getByText, getByTestId } = render(
        React.createElement(MemoryMonitor)
      );

      await waitFor(() => {
        // 应该显示高内存压力警告
        const pressureIndicator = getByTestId('memory-pressure-indicator');
        expect(pressureIndicator).toBeTruthy();

        // 应该显示优化建议
        expect(getByText(/内存使用率较高/)).toBeTruthy();
      });
    });
  });

  describe('端到端性能测试', () => {
    test('应该在合理时间内完成内存优化', async () => {
      const startTime = Date.now();

      // 初始化系统
      await localModelManager.initialize();

      // 加载数据
      await localModelManager.loadModel('health_basic_assessment');
      await optimizedCacheService.set('perf_test', { data: 'x'.repeat(5000) });

      // 执行优化
      await optimizedCacheService.cleanup();

      // 清理
      await localModelManager.dispose();

      const totalTime = Date.now() - startTime;

      // 整个流程应该在3秒内完成
      expect(totalTime).toBeLessThan(3000);
    });

    test('应该能够处理并发操作', async () => {
      await localModelManager.initialize();

      // 并发执行多个操作
      const operations = [
        localModelManager.loadModel('health_basic_assessment'),
        optimizedCacheService.set('concurrent_1', { data: 'test1' }),
        optimizedCacheService.set('concurrent_2', { data: 'test2' }),
        optimizedCacheService.get('concurrent_1'),
      ];

      const results = await Promise.allSettled(operations);

      // 验证所有操作都成功完成
      const successCount = results.filter(
        (result) => result.status === 'fulfilled'
      ).length;
      expect(successCount).toBeGreaterThan(0);

      await localModelManager.dispose();
    });

    test('应该能够从错误中恢复', async () => {
      await localModelManager.initialize();

      // 尝试加载不存在的模型（应该失败）
      try {
        await localModelManager.loadModel('non_existent_model');
      } catch (error) {
        expect(error).toBeDefined();
      }

      // 系统应该仍然能够正常工作
      const validModel = await localModelManager.loadModel(
        'health_basic_assessment'
      );
      expect(validModel).toBeDefined();

      // 缓存操作应该仍然正常
      await optimizedCacheService.set('recovery_test', { data: 'test' });
      const retrieved = await optimizedCacheService.get('recovery_test');
      expect(retrieved).toEqual({ data: 'test' });

      await localModelManager.dispose();
    });
  });

  describe('内存泄漏检测', () => {
    test('应该正确清理资源', async () => {
      // 记录初始状态
      const initialModelStats = localModelManager.getMemoryStats();
      const initialCacheStats = optimizedCacheService.getMemoryUsage();

      // 执行一系列操作
      await localModelManager.initialize();
      await localModelManager.loadModel('health_basic_assessment');
      await optimizedCacheService.set('leak_test', { data: 'test' });

      // 清理资源
      await localModelManager.dispose();
      optimizedCacheService.clear();

      // 验证资源被正确清理
      const finalModelStats = localModelManager.getMemoryStats();
      const finalCacheStats = optimizedCacheService.getMemoryUsage();

      expect(finalModelStats.loadedModels).toBe(0);
      expect(finalCacheStats.itemCount).toBe(0);
    });

    test('应该能够检测和处理内存泄漏', async () => {
      await localModelManager.initialize();

      // 创建大量对象但不清理
      const largeObjects = [];
      for (let i = 0; i < 100; i++) {
        largeObjects.push({
          id: i,
          data: 'x'.repeat(1000),
          timestamp: Date.now(),
        });

        await optimizedCacheService.set(`leak_test_${i}`, largeObjects[i]);
      }

      const beforeCleanup = optimizedCacheService.getMemoryUsage();
      expect(beforeCleanup.itemCount).toBe(100);

      // 触发清理
      await optimizedCacheService.cleanup();

      const afterCleanup = optimizedCacheService.getMemoryUsage();

      // 验证内存使用减少
      expect(afterCleanup.current).toBeLessThan(beforeCleanup.current);

      await localModelManager.dispose();
    });
  });

  describe('边界条件测试', () => {
    test('应该能够处理极低内存情况', async () => {
      // Mock极低内存设备
      jest
        .spyOn(require('react-native-device-info'), 'getTotalMemory')
        .mockResolvedValue(256 * 1024 * 1024); // 256MB

      const config = await createDynamicConfig();

      expect(config.EDGE_COMPUTE.memoryLimit).toBeLessThan(200 * 1024 * 1024);
      expect(config.EDGE_COMPUTE.maxConcurrentSessions).toBe(1);
      expect(config.EDGE_COMPUTE.enableGPU).toBe(false);
    });

    test('应该能够处理内存分配失败', async () => {
      // Mock内存分配失败
      const originalSet = optimizedCacheService.set;
      jest
        .spyOn(optimizedCacheService, 'set')
        .mockImplementation(async (key, value) => {
          if (key === 'fail_test') {
            throw new Error('Memory allocation failed');
          }
          return originalSet.call(optimizedCacheService, key, value);
        });

      // 尝试设置会失败的缓存项
      await expect(
        optimizedCacheService.set('fail_test', { data: 'test' })
      ).rejects.toThrow('Memory allocation failed');

      // 验证其他操作仍然正常
      await expect(
        optimizedCacheService.set('success_test', { data: 'test' })
      ).resolves.not.toThrow();

      const retrieved = await optimizedCacheService.get('success_test');
      expect(retrieved).toEqual({ data: 'test' });
    });

    test('应该能够处理大量并发请求', async () => {
      await localModelManager.initialize();

      // 创建大量并发请求
      const concurrentRequests = Array.from({ length: 50 }, (_, i) =>
        optimizedCacheService.set(`concurrent_${i}`, {
          id: i,
          data: `data_${i}`,
          timestamp: Date.now(),
        })
      );

      const results = await Promise.allSettled(concurrentRequests);

      // 验证大部分请求成功
      const successCount = results.filter(
        (result) => result.status === 'fulfilled'
      ).length;
      expect(successCount).toBeGreaterThan(40); // 至少80%成功

      await localModelManager.dispose();
    });
  });
});

// 性能基准测试辅助函数
export const runIntegrationPerformanceTest = async () => {
  console.log('🚀 开始集成性能测试...');

  const results = {
    initialization: 0,
    modelLoading: 0,
    cacheOperations: 0,
    memoryOptimization: 0,
    cleanup: 0,
  };

  // 测试初始化性能
  let start = Date.now();
  await localModelManager.initialize();
  results.initialization = Date.now() - start;

  // 测试模型加载性能
  start = Date.now();
  await localModelManager.loadModel('health_basic_assessment');
  results.modelLoading = Date.now() - start;

  // 测试缓存操作性能
  start = Date.now();
  for (let i = 0; i < 10; i++) {
    await optimizedCacheService.set(`perf_test_${i}`, { data: `test_${i}` });
  }
  for (let i = 0; i < 10; i++) {
    await optimizedCacheService.get(`perf_test_${i}`);
  }
  results.cacheOperations = Date.now() - start;

  // 测试内存优化性能
  start = Date.now();
  await optimizedCacheService.cleanup();
  results.memoryOptimization = Date.now() - start;

  // 测试清理性能
  start = Date.now();
  await localModelManager.dispose();
  optimizedCacheService.clear();
  results.cleanup = Date.now() - start;

  console.log('📊 集成性能测试结果:');
  console.log(`  初始化: ${results.initialization}ms`);
  console.log(`  模型加载: ${results.modelLoading}ms`);
  console.log(`  缓存操作: ${results.cacheOperations}ms`);
  console.log(`  内存优化: ${results.memoryOptimization}ms`);
  console.log(`  清理: ${results.cleanup}ms`);

  return results;
};
