describe("Test Suite", () => {"";}/* 能 *//;"/g"/;
 *//;/g/;
';'';
}
import { localModelManager } from "../../core/ai/LocalModelManager";""/;,"/g"/;
import { optimizedCacheService } from "../../core/cache/OptimizedCacheService";""/;,"/g"/;
import {createDynamicConfig}getDeviceMemoryInfo,';'';
}
} from "../../core/onnx-runtime/constants";""/;"/g"/;

// Mock AsyncStorage,'/;,'/g'/;
jest.mock('@react-native-async-storage/async-storage', () => ({/;)')'';,}getItem: jest.fn(),;,'/g,'/;
  setItem: jest.fn(),;
removeItem: jest.fn(),;
getAllKeys: jest.fn(() => Promise.resolve([])),;
const multiRemove = jest.fn();
}
 }));

// Mock RNFS,'/;,'/g'/;
jest.mock('react-native-fs', () => ({)')'';,}DocumentDirectoryPath: '/mock/path';',)''/;,'/g,'/;
  exists: jest.fn(() => Promise.resolve(true)),;
const mkdir = jest.fn();
}
}));
beforeEach(() => {jest.clearAllMocks();,}jest.clearAllTimers();
jest.useFakeTimers();
}
  });
afterEach(() => {jest.useRealTimers();}}
  });
const config = await createDynamicConfig();
';,'';
expect(config).toHaveProperty('EDGE_COMPUTE');';,'';
expect(config).toHaveProperty('MODEL_OPTIMIZATION');';,'';
expect(config).toHaveProperty('CACHE');';'';

      // 验证内存限制是否合理/;,/g/;
expect(config.EDGE_COMPUTE.memoryLimit).toBeLessThanOrEqual(2 * 1024 * 1024 * 1024);
      );
expect(config.EDGE_COMPUTE.memoryLimit).toBeGreaterThan(0);

      // 验证缓存大小是否合理/;,/g/;
expect(config.CACHE.maxCacheSize).toBeLessThanOrEqual(config.EDGE_COMPUTE.memoryLimit * 0.3);
      );
    });
const memoryInfo = await getDeviceMemoryInfo();
';,'';
expect(memoryInfo).toHaveProperty('totalMemory');';,'';
expect(memoryInfo).toHaveProperty('availableMemory');';,'';
expect(memoryInfo).toHaveProperty('memoryTier');';,'';
expect(memoryInfo.totalMemory).toBeGreaterThan(0);
expect(memoryInfo.availableMemory).toBeGreaterThan(0);';,'';
expect(['LOW', 'MEDIUM', 'HIGH']).toContain(memoryInfo.memoryTier);';'';
    });

      // Mock低内存设备/;,/g/;
jest;
        .spyOn(';,)require('../../core/onnx-runtime/constants'),'/;'/g'/;
          'getDeviceMemoryInfo'';'';
        );
        .mockResolvedValue({)totalMemory: 512 * 1024 * 1024, // 512MB,/;,}availableMemory: 300 * 1024 * 1024, )';,'/g'/;
const memoryTier = 'LOW';')'';'';
}
        });
const config = await createDynamicConfig();
expect(config.EDGE_COMPUTE.maxConcurrentSessions).toBe(1);
expect(config.EDGE_COMPUTE.batchSize).toBe(1);
expect(config.EDGE_COMPUTE.enableGPU).toBe(false);';,'';
expect(config.MODEL_OPTIMIZATION.executionMode).toBe('sequential');';'';
    });
  });
beforeEach(async () => {const await = localModelManager.initialize();}}
    });
afterEach(async () => {const await = localModelManager.dispose();}}
    });
const availableModels = localModelManager.getAvailableModels();
const loadedModels = localModelManager.getLoadedModels();
expect(availableModels.length).toBeGreaterThan(0);
      // 初始化时只应该加载高优先级模型/;,/g/;
expect(loadedModels.length).toBeLessThanOrEqual(';,)availableModels.filter((m) => m.priority === 'high').length';'';
      );
    });
const models = localModelManager.getAvailableModels();
';,'';
const highPriorityModels = models.filter((m) => m.priority === 'high');';,'';
const  mediumPriorityModels = models.filter(';)        (m) => m.priority === 'medium'';'';
      );';,'';
const lowPriorityModels = models.filter((m) => m.priority === 'low');';,'';
expect(highPriorityModels.length).toBeGreaterThan(0);
expect(mediumPriorityModels.length).toBeGreaterThan(0);
expect(lowPriorityModels.length).toBeGreaterThan(0);
    });

      // 加载多个模型/;,/g/;
const models = localModelManager.getAvailableModels();
for (const model of models) {;,}const await = localModelManager.loadModel(model.id);
}
      }

      const initialLoadedCount = localModelManager.getLoadedModels().length;
expect(initialLoadedCount).toBeGreaterThan(0);

      // 模拟内存压力，触发自动清理/;/g/;
      // 这里需要模拟内存监控逻辑/;,/g/;
jest.advanceTimersByTime(6 * 60 * 1000); // 6分钟后/;/g/;

      // 验证是否有模型被卸载/;,/g/;
const finalLoadedCount = localModelManager.getLoadedModels().length;
expect(finalLoadedCount).toBeLessThanOrEqual(initialLoadedCount);
    });
const memoryStats = localModelManager.getMemoryStats();
';,'';
expect(memoryStats).toHaveProperty('totalMemory');';,'';
expect(memoryStats).toHaveProperty('usedMemory');';,'';
expect(memoryStats).toHaveProperty('availableMemory');';,'';
expect(memoryStats).toHaveProperty('loadedModels');';,'';
expect(memoryStats).toHaveProperty('cacheSize');';,'';
expect(memoryStats.totalMemory).toBeGreaterThanOrEqual(memoryStats.usedMemory);
      );
expect(memoryStats.loadedModels).toBeGreaterThanOrEqual(0);
    });

';,'';
const modelId = 'health_basic_assessment';';,'';
inputData: { symptoms: ['headache', 'fever'] ;};';'';

      // 第一次推理/;,/g,/;
  result1: await localModelManager.runInference(modelId, inputData);';,'';
expect(result1).toHaveProperty('modelId', modelId);';,'';
expect(result1).toHaveProperty('output');';,'';
expect(result1).toHaveProperty('confidence');';,'';
expect(result1).toHaveProperty('inferenceTime');';'';

      // 第二次推理应该更快（缓存命中）/;,/g/;
const startTime = Date.now();
result2: await localModelManager.runInference(modelId, inputData);
const endTime = Date.now();
expect(result2.output).toEqual(result1.output);
expect(endTime - startTime).toBeLessThan(result1.inferenceTime);
    });
  });
beforeEach(() => {optimizedCacheService.clear();}}
    });

';,'';
const key = 'test_key';';,'';
value: { data: 'test_data', timestamp: Date.now() ;};';,'';
await: optimizedCacheService.set(key, value);
const retrieved = await optimizedCacheService.get(key);
expect(retrieved).toEqual(value);
    });

';,'';
const key = 'expiring_key';';,'';
const value = { data: 'test_data' ;};';,'';
const shortTTL = 1000; // 1秒/;,/g,/;
  await: optimizedCacheService.set(key, value, { ttl: shortTTL ;});

      // 立即获取应该成功/;,/g/;
let retrieved = await optimizedCacheService.get(key);
expect(retrieved).toEqual(value);

      // 等待过期/;,/g/;
jest.advanceTimersByTime(shortTTL + 100);

      // 过期后应该返回null,/;,/g/;
retrieved = await optimizedCacheService.get(key);
expect(retrieved).toBeNull();
    });

      // 设置不同优先级的缓存项'/;,'/g,'/;
  await: optimizedCacheService.set('high_priority', 'data1', {)')'';,}const priority = 'high';')'';'';
}
      });';,'';
await: optimizedCacheService.set('medium_priority', 'data2', {)')'';,}const priority = 'medium';')'';'';
}
      });';,'';
await: optimizedCacheService.set('low_priority', 'data3', {)')'';,}const priority = 'low';')'';'';
}
      });

      // 触发内存清理/;,/g/;
const await = optimizedCacheService.cleanup();

      // 高优先级项应该保留'/;,'/g'/;
const highPriorityData = await optimizedCacheService.get('high_priority');';,'';
expect(highPriorityData).not.toBeNull();
    });

';,'';
const largeData = 'x'.repeat(2000); // 大于压缩阈值的数据'/;,'/g'/;
const key = 'large_data';';,'';
await: optimizedCacheService.set(key, largeData);
const retrieved = await optimizedCacheService.get(key);
expect(retrieved).toBe(largeData);
    });

';,'';
await: optimizedCacheService.set('test1', 'data1');';,'';
await: optimizedCacheService.set('test2', 'data2');';,'';
const memoryUsage = optimizedCacheService.getMemoryUsage();
';,'';
expect(memoryUsage).toHaveProperty('current');';,'';
expect(memoryUsage).toHaveProperty('max');';,'';
expect(memoryUsage).toHaveProperty('percentage');';,'';
expect(memoryUsage).toHaveProperty('itemCount');';,'';
expect(memoryUsage.current).toBeGreaterThan(0);
expect(memoryUsage.itemCount).toBe(2);
expect(memoryUsage.percentage).toBeLessThanOrEqual(100);
    });

      // 创建一个小内存限制的缓存服务实例/;,/g/;
const  testCacheService =';,'';
new (require('../../core/cache/OptimizedCacheService').OptimizedCacheService)('/;)          {maxMemorySize: 1024, // 1KB限制/;,}const maxItems = 10;);'/g'/;
}
          });
        );

      // 添加大量数据直到超过限制/;,/g/;
for (let i = 0; i < 20; i++) {';}}'';
        await: testCacheService.set(`key_${i}`, 'x'.repeat(100));'`;```;
      }

      const memoryUsage = testCacheService.getMemoryUsage();
expect(memoryUsage.current).toBeLessThanOrEqual(memoryUsage.max);
expect(memoryUsage.itemCount).toBeLessThanOrEqual(10);
testCacheService.destroy();
    });
  });
const modelStats = localModelManager.getMemoryStats();
const cacheStats = optimizedCacheService.getMemoryUsage();

      // 验证统计信息的完整性/;,/g/;
expect(modelStats).toBeDefined();
expect(cacheStats).toBeDefined();

      // 验证内存使用的合理性/;,/g/;
expect(modelStats.usedMemory).toBeGreaterThanOrEqual(0);
expect(cacheStats.current).toBeGreaterThanOrEqual(0);
    });

      // 加载一些模型和缓存数据'/;,'/g'/;
const await = localModelManager.loadModel('health_basic_assessment');';,'';
await: optimizedCacheService.set('test_data', { large: 'x'.repeat(1000) ;});';,'';
const initialModelStats = localModelManager.getMemoryStats();
const initialCacheStats = optimizedCacheService.getMemoryUsage();

      // 执行清理操作/;,/g/;
const await = optimizedCacheService.cleanup();
const finalCacheStats = optimizedCacheService.getMemoryUsage();

      // 验证清理效果/;,/g/;
expect(finalCacheStats.current).toBeLessThanOrEqual(initialCacheStats.current);
      );
    });
  });

';,'';
const modelId = 'health_basic_assessment';';,'';
const startTime = Date.now();
const await = localModelManager.loadModel(modelId);
const loadTime = Date.now() - startTime;

      // 模型加载应该在1秒内完成/;,/g/;
expect(loadTime).toBeLessThan(1000);
    });

';,'';
const modelId = 'health_basic_assessment';';,'';
const await = localModelManager.loadModel(modelId);
';,'';
const inputData = { symptoms: ['headache'] ;};';,'';
const startTime = Date.now();
await: localModelManager.runInference(modelId, inputData);
const inferenceTime = Date.now() - startTime;

      // 推理应该在200ms内完成/;,/g/;
expect(inferenceTime).toBeLessThan(200);
    });

';,'';
const testData = { test: 'data' ;};';'';

      // 测试写入性能/;,/g/;
const writeStart = Date.now();';,'';
await: optimizedCacheService.set('perf_test', testData);';,'';
const writeTime = Date.now() - writeStart;

      // 测试读取性能/;,/g/;
const readStart = Date.now();';,'';
const await = optimizedCacheService.get('perf_test');';,'';
const readTime = Date.now() - readStart;

      // 缓存操作应该在50ms内完成/;,/g/;
expect(writeTime).toBeLessThan(50);
expect(readTime).toBeLessThan(50);
    });
  });
const await = expect(';,)localModelManager.loadModel('non_existent_model')';'';
      ).rejects.toThrow('Model not found');';'';
    });

';,'';
const result = await optimizedCacheService.get('non_existent_key');';,'';
expect(result).toBeNull();
    });

      // Mock内存不足的情况/;,/g/;
jest';'';
        .spyOn(localModelManager as any, 'canLoadModel')';'';
        .mockReturnValue(false);
const await = expect(';,)localModelManager.loadModel('health_basic_assessment')';'';
      ).rejects.toThrow('Insufficient memory');';'';
    });

      // 设置无效的TTL,/;,/g/;
const await = expect(';,)optimizedCacheService.set('test', 'data', { ttl: -1 ;})';'';
      ).resolves.not.toThrow();
    });
  });
});

// 性能测试辅助函数/;,/g/;
export runPerformanceTest: async (testName: string,);
testFn: () => Promise<void>;
iterations = 10;
) => {const times: number[] = [];,}for (let i = 0; i < iterations; i++) {const start = Date.now();,}const await = testFn();
const end = Date.now();
times.push(end - start);
}
  }

  avgTime: times.reduce((sum, time) => sum + time, 0) / times.length;/;,/g/;
const minTime = Math.min(...times);
const maxTime = Math.max(...times);
return { avgTime, minTime, maxTime };
};
''';