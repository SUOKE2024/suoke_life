import { FiveDiagnosisExample, runFiveDiagnosisExamples } from "../FiveDiagnosisExample";

describe("FiveDiagnosisExample", () => {
  let example: FiveDiagnosisExample;

  beforeEach(() => {
    jest.clearAllMocks();
    example = new FiveDiagnosisExample();
  });

  afterEach(async () => {
    if (example) {
      await example.cleanup();
    }
  });



      expect(example).toBeDefined();
      expect(example).toBeInstanceOf(FiveDiagnosisExample);
    });


      // 模拟控制台输出
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      await expect(example.runCompleteDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
    });


      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      await expect(example.runLookingDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
    });


      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      await expect(example.runCalculationDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
    });


      await expect(example.cleanup()).resolves.not.toThrow();
    });
  });



      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      await expect(runFiveDiagnosisExamples()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
      errorSpy.mockRestore();
    });
  });



      const iterations = 3;
      const startTime = performance.now();
      
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      for (let i = 0; i < iterations; i++) {
        await example.runLookingDiagnosisExample();
      }
      
      const endTime = performance.now();
      const averageTime = (endTime - startTime) / iterations;
      
      // 平均执行时间应该在合理范围内（小于2000ms）
      expect(averageTime).toBeLessThan(2000);
      
      consoleSpy.mockRestore();
    });


      const initialMemory = process.memoryUsage().heapUsed;
      
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      // 执行多次示例
      for (let i = 0; i < 10; i++) {
        const testExample = new FiveDiagnosisExample();
        await testExample.runLookingDiagnosisExample();
        await testExample.cleanup();
      }
      
      // 强制垃圾回收（如果可用）
      if (global.gc) {
        global.gc();
      }
      
      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;
      
      // 内存增长应该是最小的（小于100MB）
      expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024);
      
      consoleSpy.mockRestore();
    });
  });



      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      // 即使引擎出错，示例也应该能够处理
      await expect(example.runCompleteDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
      errorSpy.mockRestore();
    });
  });
}); 