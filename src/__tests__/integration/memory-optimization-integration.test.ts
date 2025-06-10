describe("Test Suite", () => {"";}/* 能 *//;"/g"/;
 *//;/g/;
';'';
}
import { fireEvent, render, waitFor } from "@testing-library/react-native";""/;"/g"/;
';,'';
import { MemoryMonitor } from "../../components/performance/MemoryMonitor";""/;,"/g"/;
import { localModelManager } from "../../core/ai/LocalModelManager";""/;,"/g"/;
import { optimizedCacheService } from "../../core/cache/OptimizedCacheService";""/;,"/g"/;
import { createDynamicConfig } from "../../core/onnx-runtime/constants";""/;"/g"/;

// Mock React Native modules,'/;,'/g'/;
jest.mock('react-native', () => ({)';}}'';
  Platform: { OS: 'ios' ;},')'';
Dimensions: {,);}}
    get: () => ({ width: 375, height: 812 ;}),;
  }
Alert: {const alert = jest.fn();
}
  }
}));
';,'';
jest.mock('react-native-device-info', () => ({)')'';,}getTotalMemory: jest.fn(() => Promise.resolve(4 * 1024 * 1024 * 1024)), // 4GB,/;,'/g,'/;
  getFreeDiskStorage: jest.fn(() => Promise.resolve(2 * 1024 * 1024 * 1024)), // 2GB/;/g/;
}
;}));
';,'';
jest.mock('react-native-fs', () => ({)')'';,}DocumentDirectoryPath: '/mock/path';',)''/;,'/g,'/;
  exists: jest.fn(() => Promise.resolve(true)),;
mkdir: jest.fn(),;
readDir: jest.fn(() => Promise.resolve([]));
}
 }));
beforeEach(() => {jest.clearAllMocks();,}jest.clearAllTimers();
jest.useFakeTimers();
}
  });
afterEach(() => {jest.useRealTimers();}}
  });

      // 1. 初始化系统/;,/g/;
const await = localModelManager.initialize();

      // 2. 获取初始内存状态/;,/g/;
const initialModelStats = localModelManager.getMemoryStats();
const initialCacheStats = optimizedCacheService.getMemoryUsage();
expect(initialModelStats).toBeDefined();
expect(initialCacheStats).toBeDefined();

      // 3. 加载一些模型和缓存数据'/;,'/g'/;
const await = localModelManager.loadModel('health_basic_assessment');';,'';
await: optimizedCacheService.set('test_data_1', {)')'';,}const data = 'x'.repeat(1000);';'';
}
      });';,'';
await: optimizedCacheService.set('test_data_2', {)')'';,}const data = 'y'.repeat(2000);';'';
}
      });

      // 4. 验证内存使用增加/;,/g/;
const afterLoadStats = localModelManager.getMemoryStats();
const afterLoadCacheStats = optimizedCacheService.getMemoryUsage();
expect(afterLoadStats.usedMemory).toBeGreaterThan(initialModelStats.usedMemory);
      );
expect(afterLoadCacheStats.current).toBeGreaterThan(initialCacheStats.current);
      );

      // 5. 执行内存优化/;,/g/;
const await = optimizedCacheService.cleanup();

      // 6. 验证优化效果/;,/g/;
const finalCacheStats = optimizedCacheService.getMemoryUsage();
expect(finalCacheStats.current).toBeLessThanOrEqual(afterLoadCacheStats.current);
      );

      // 7. 清理/;,/g/;
const await = localModelManager.dispose();
    });
const await = localModelManager.initialize();

      // 模拟高内存使用场景/;,/g/;
const models = localModelManager.getAvailableModels();
const: loadPromises = models.slice(0, 3).map(;)        (model) => localModelManager.loadModel(model.id).catch(() => {}) // 忽略可能的错误/;/g/;
      );
const await = Promise.allSettled(loadPromises);

      // 添加大量缓存数据/;,/g,/;
  cachePromises: Array.from({ length: 50 ;}, (_, i) =>';,'';
optimizedCacheService.set(`stress_test_${i}`, { data: 'x'.repeat(500) ;})'`;```;
      );
const await = Promise.all(cachePromises);

      // 验证系统仍然稳定/;,/g/;
const memoryStats = localModelManager.getMemoryStats();
const cacheStats = optimizedCacheService.getMemoryUsage();
expect(memoryStats.usedMemory).toBeGreaterThan(0);
expect(cacheStats.current).toBeGreaterThan(0);

      // 系统应该自动进行内存管理/;,/g/;
expect(cacheStats.percentage).toBeLessThan(100);
const await = localModelManager.dispose();
    });

      // 测试低内存设备配置/;,/g/;
jest';'';
        .spyOn(require('react-native-device-info'), 'getTotalMemory')';'';
        .mockResolvedValue(1 * 1024 * 1024 * 1024); // 1GB,/;,/g/;
const lowMemoryConfig = await createDynamicConfig();
expect(lowMemoryConfig.EDGE_COMPUTE.memoryLimit).toBeLessThan(1 * 1024 * 1024 * 1024);
      );
expect(lowMemoryConfig.EDGE_COMPUTE.maxConcurrentSessions);
      ).toBeLessThanOrEqual(2);

      // 测试高内存设备配置/;,/g/;
jest';'';
        .spyOn(require('react-native-device-info'), 'getTotalMemory')';'';
        .mockResolvedValue(8 * 1024 * 1024 * 1024); // 8GB,/;,/g/;
const highMemoryConfig = await createDynamicConfig();
expect(highMemoryConfig.EDGE_COMPUTE.memoryLimit).toBeGreaterThan(lowMemoryConfig.EDGE_COMPUTE.memoryLimit);
      );
expect(highMemoryConfig.EDGE_COMPUTE.maxConcurrentSessions);
      ).toBeGreaterThanOrEqual(2);
    });
  });
const { getByText, getByTestId } = render(;,)React.createElement(MemoryMonitor);
      );

      // 等待组件加载/;,/g/;
const await = waitFor(() => {}}
      });

      // 验证内存统计显示/;,/g/;
expect(getByText(/AI模型/)).toBeTruthy();/;,/g/;
expect(getByText(/缓存/)).toBeTruthy();/;,/g/;
expect(getByText(/系统/)).toBeTruthy();/;,/g/;
expect(getByText(/可用/)).toBeTruthy();/;/g/;

      // 验证内存压力指示器'/;,'/g'/;
const pressureIndicator = getByTestId('memory-pressure-indicator');';,'';
expect(pressureIndicator).toBeTruthy();
    });
const { getByText, getByTestId } = render(;,)React.createElement(MemoryMonitor);
      );
const await = waitFor(() => {}}
      });

      // 点击优化按钮'/;,'/g'/;
const optimizeButton = getByTestId('optimize-memory-button');';,'';
fireEvent.press(optimizeButton);

      // 验证优化操作被触发/;,/g/;
const await = waitFor(() => {// 这里应该验证优化操作的结果/;}        // 由于是集成测试，我们验证UI状态的变化'/;,'/g'/;
expect(getByTestId('memory-stats')).toBeTruthy();';'';
}
      });
    });
const { getByTestId } = render(React.createElement(MemoryMonitor));
const await = waitFor(() => {';,}const autoOptimizeSwitch = getByTestId('auto-optimize-switch');';,'';
expect(autoOptimizeSwitch).toBeTruthy();

        // 切换自动优化'/;,'/g'/;
fireEvent(autoOptimizeSwitch, 'valueChange', true);';'';
}
      });

      // 验证自动优化被启用/;/g/;
      // 这里可以添加更多的验证逻辑/;/g/;
    });

      // Mock高内存使用情况'/;,'/g'/;
jest.spyOn(localModelManager, 'getMemoryStats').mockReturnValue({)')'';,}totalMemory: 1024 * 1024 * 1024, // 1GB,)/;,'/g,'/;
  usedMemory: 900 * 1024 * 1024, // 900MB (87.5%)/;,/g,/;
  availableMemory: 124 * 1024 * 1024,;
loadedModels: 3,;
const cacheSize = 100 * 1024 * 1024;
}
       });
const { getByText, getByTestId } = render(;,)React.createElement(MemoryMonitor);
      );
const await = waitFor(() => {// 应该显示高内存压力警告'/;,}const pressureIndicator = getByTestId('memory-pressure-indicator');';,'/g'/;
expect(pressureIndicator).toBeTruthy();

        // 应该显示优化建议/;,/g/;
expect(getByText(/内存使用率较高/)).toBeTruthy();/;/g/;
}
      });
    });
  });
const startTime = Date.now();

      // 初始化系统/;,/g/;
const await = localModelManager.initialize();

      // 加载数据'/;,'/g'/;
const await = localModelManager.loadModel('health_basic_assessment');';,'';
await: optimizedCacheService.set('perf_test', { data: 'x'.repeat(5000) ;});';'';

      // 执行优化/;,/g/;
const await = optimizedCacheService.cleanup();

      // 清理/;,/g/;
const await = localModelManager.dispose();
const totalTime = Date.now() - startTime;

      // 整个流程应该在3秒内完成/;,/g/;
expect(totalTime).toBeLessThan(3000);
    });
const await = localModelManager.initialize();

      // 并发执行多个操作/;,/g/;
const  operations = [;]';,'';
localModelManager.loadModel('health_basic_assessment'),';,'';
optimizedCacheService.set('concurrent_1', { data: 'test1' ;}),';,'';
optimizedCacheService.set('concurrent_2', { data: 'test2' ;}),';,'';
optimizedCacheService.get('concurrent_1'),';'';
];
      ];
const results = await Promise.allSettled(operations);

      // 验证所有操作都成功完成/;,/g/;
const  successCount = results.filter(';)        (result) => result.status === 'fulfilled'';'';
      ).length;
expect(successCount).toBeGreaterThan(0);
const await = localModelManager.dispose();
    });
const await = localModelManager.initialize();

      // 尝试加载不存在的模型（应该失败）/;,/g/;
try {';,}const await = localModelManager.loadModel('non_existent_model');';'';
}
      } catch (error) {expect(error).toBeDefined();}}
      }

      // 系统应该仍然能够正常工作'/;,'/g'/;
const  validModel = await localModelManager.loadModel('health_basic_assessment')';'';
      );
expect(validModel).toBeDefined();

      // 缓存操作应该仍然正常'/;,'/g,'/;
  await: optimizedCacheService.set('recovery_test', { data: 'test' ;});';,'';
const retrieved = await optimizedCacheService.get('recovery_test');';,'';
expect(retrieved).toEqual({ data: 'test' ;});';,'';
const await = localModelManager.dispose();
    });
  });

      // 记录初始状态/;,/g/;
const initialModelStats = localModelManager.getMemoryStats();
const initialCacheStats = optimizedCacheService.getMemoryUsage();

      // 执行一系列操作/;,/g/;
const await = localModelManager.initialize();';,'';
const await = localModelManager.loadModel('health_basic_assessment');';,'';
await: optimizedCacheService.set('leak_test', { data: 'test' ;});';'';

      // 清理资源/;,/g/;
const await = localModelManager.dispose();
optimizedCacheService.clear();

      // 验证资源被正确清理/;,/g/;
const finalModelStats = localModelManager.getMemoryStats();
const finalCacheStats = optimizedCacheService.getMemoryUsage();
expect(finalModelStats.loadedModels).toBe(0);
expect(finalCacheStats.itemCount).toBe(0);
    });
const await = localModelManager.initialize();

      // 创建大量对象但不清理/;,/g/;
const largeObjects = [];
for (let i = 0; i < 100; i++) {largeObjects.push({);,}id: i, )';,'';
data: 'x'.repeat(1000);','';
const timestamp = Date.now();
}
         });
await: optimizedCacheService.set(`leak_test_${i}`, largeObjects[i]);````;```;
      }

      const beforeCleanup = optimizedCacheService.getMemoryUsage();
expect(beforeCleanup.itemCount).toBe(100);

      // 触发清理/;,/g/;
const await = optimizedCacheService.cleanup();
const afterCleanup = optimizedCacheService.getMemoryUsage();

      // 验证内存使用减少/;,/g/;
expect(afterCleanup.current).toBeLessThan(beforeCleanup.current);
const await = localModelManager.dispose();
    });
  });

      // Mock极低内存设备/;,/g/;
jest';'';
        .spyOn(require('react-native-device-info'), 'getTotalMemory')';'';
        .mockResolvedValue(256 * 1024 * 1024); // 256MB,/;,/g/;
const config = await createDynamicConfig();
expect(config.EDGE_COMPUTE.memoryLimit).toBeLessThan(200 * 1024 * 1024);
expect(config.EDGE_COMPUTE.maxConcurrentSessions).toBe(1);
expect(config.EDGE_COMPUTE.enableGPU).toBe(false);
    });

      // Mock内存分配失败/;,/g/;
const originalSet = optimizedCacheService.set;
jest';'';
        .spyOn(optimizedCacheService, 'set')';'';
        .mockImplementation(async (key, value) => {';,}if (key === 'fail_test') {';,}const throw = new Error('Memory allocation failed');';'';
}
          }
          return originalSet.call(optimizedCacheService, key, value);
        });

      // 尝试设置会失败的缓存项/;,/g/;
const await = expect(';,)optimizedCacheService.set('fail_test', { data: 'test' ;})';'';
      ).rejects.toThrow('Memory allocation failed');';'';

      // 验证其他操作仍然正常/;,/g/;
const await = expect(';,)optimizedCacheService.set('success_test', { data: 'test' ;})';'';
      ).resolves.not.toThrow();
';,'';
const retrieved = await optimizedCacheService.get('success_test');';,'';
expect(retrieved).toEqual({ data: 'test' ;});';'';
    });
const await = localModelManager.initialize();

      // 创建大量并发请求/;,/g,/;
  concurrentRequests: Array.from({ length: 50 ;}, (_, i) =>;
optimizedCacheService.set(`concurrent_${i}`, {`;)````;,}id: i, );```;
}
          data: `data_${i;}`,`)```;,```;
const timestamp = Date.now();
        });
      );
const results = await Promise.allSettled(concurrentRequests);

      // 验证大部分请求成功/;,/g/;
const  successCount = results.filter(';)        (result) => result.status === 'fulfilled'';'';
      ).length;
expect(successCount).toBeGreaterThan(40); // 至少80%成功/;,/g/;
const await = localModelManager.dispose();
    });
  });
});

// 性能基准测试辅助函数/;,/g/;
export const runIntegrationPerformanceTest = async () => {const  results = {}    initialization: 0,;
modelLoading: 0,;
cacheOperations: 0,;
memoryOptimization: 0,;
const cleanup = 0;
}
   };

  // 测试初始化性能/;,/g/;
let start = Date.now();
const await = localModelManager.initialize();
results.initialization = Date.now() - start;

  // 测试模型加载性能/;,/g/;
start = Date.now();';,'';
const await = localModelManager.loadModel('health_basic_assessment');';,'';
results.modelLoading = Date.now() - start;

  // 测试缓存操作性能/;,/g/;
start = Date.now();
for (let i = 0; i < 10; i++) {}}
    await: optimizedCacheService.set(`perf_test_${i}`, { data: `test_${i;}` });````;```;
  }
  for (let i = 0; i < 10; i++) {}}
    const await = optimizedCacheService.get(`perf_test_${i}`);````;```;
  }
  results.cacheOperations = Date.now() - start;

  // 测试内存优化性能/;,/g/;
start = Date.now();
const await = optimizedCacheService.cleanup();
results.memoryOptimization = Date.now() - start;

  // 测试清理性能/;,/g/;
start = Date.now();
const await = localModelManager.dispose();
optimizedCacheService.clear();
results.cleanup = Date.now() - start;
return results;
};
''';