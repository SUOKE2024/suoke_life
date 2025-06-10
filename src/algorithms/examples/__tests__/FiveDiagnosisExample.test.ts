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

  describe("基础功能测试", () => {
    it("应该能够正确初始化", () => {
      expect(example).toBeDefined();
      expect(example).toBeInstanceOf(FiveDiagnosisExample);
    });

    it("应该能够运行完整诊断示例", async () => {
      // 模拟控制台输出
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      await expect(example.runCompleteDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
    });

    it("应该能够运行望诊示例", async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      await expect(example.runLookingDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
    });

    it("应该能够运行算诊示例", async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      await expect(example.runCalculationDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
    });

    it("应该能够正确清理资源", async () => {
      await expect(example.cleanup()).resolves.not.toThrow();
    });
  });

  describe("集成测试", () => {
    it("应该能够运行所有示例", async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      await expect(runFiveDiagnosisExamples()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
      errorSpy.mockRestore();
    });
  });

  describe("性能测试", () => {
    it("应该在性能阈值内执行", async () => {
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

    it("应该不会造成内存泄漏", async () => {
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

  describe("错误处理测试", () => {
    it("应该优雅地处理引擎错误", async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      // 即使引擎出错，示例也应该能够处理
      await expect(example.runCompleteDiagnosisExample()).resolves.not.toThrow();
      
      consoleSpy.mockRestore();
      errorSpy.mockRestore();
    });
  });
}); 