import { DiagnosisInput, FiveDiagnosisEngine } from '../FiveDiagnosisEngine';

describe('FiveDiagnosisEngine', () => {
  let engine: FiveDiagnosisEngine;

  beforeEach(() => {
    jest.clearAllMocks();
    engine = new FiveDiagnosisEngine();
  });

  afterEach(async () => {
    // Cleanup if method exists
    if (engine && 'cleanup' in engine && typeof (engine as any).cleanup === 'function') {
      await (engine as any).cleanup();
    }
  });

  describe('基础功能测试', () => {
    it('应该能够正确初始化', () => {
      expect(engine).toBeDefined();
      expect(engine).toBeInstanceOf(FiveDiagnosisEngine);
    });

    it('应该能够处理有效输入', async () => {
      const validInput: DiagnosisInput = {
        userId: 'test_user',
        sessionId: 'test_session',
        timestamp: Date.now(),
        userProfile: {
          age: 30,
          gender: 'male',
          height: 175,
          weight: 70,
          occupation: '测试',
          medicalHistory: [],
          allergies: [],
          medications: []
        }
      };

      const result = await engine.analyze(validInput);
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThanOrEqual(0);
      expect(result.confidence).toBeLessThanOrEqual(1);
      expect(result.timestamp).toBeDefined();
    });

    it('应该优雅地处理边界情况', async () => {
      const edgeCaseInput: DiagnosisInput = {
        userId: '',
        sessionId: '',
        timestamp: 0,
        userProfile: {
          age: 0,
          gender: 'other',
          height: 0,
          weight: 0,
          occupation: '',
          medicalHistory: [],
          allergies: [],
          medications: []
        }
      };

      await expect(engine.analyze(edgeCaseInput)).resolves.toBeDefined();
    });

    it('应该返回正确的输出格式', async () => {
      const testInput: DiagnosisInput = {
        userId: 'format_test',
        sessionId: 'format_session',
        timestamp: Date.now(),
        userProfile: {
          age: 25,
          gender: 'female',
          height: 160,
          weight: 55,
          occupation: '测试',
          medicalHistory: [],
          allergies: [],
          medications: []
        }
      };

      const result = await engine.analyze(testInput);
      expect(typeof result).toBe('object');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('timestamp');
      expect(result).toHaveProperty('diagnosisResults');
    });
  });

  describe('性能测试', () => {
    it('应该在性能阈值内执行', async () => {
      const iterations = 5;
      const testInput: DiagnosisInput = {
        userId: 'perf_test',
        sessionId: 'perf_session',
        timestamp: Date.now(),
        userProfile: {
          age: 30,
          gender: 'male',
          height: 175,
          weight: 70,
          occupation: '测试',
          medicalHistory: [],
          allergies: [],
          medications: []
        }
      };

      const startTime = performance.now();
      for (let i = 0; i < iterations; i++) {
        await engine.analyze(testInput);
      }
      const endTime = performance.now();
      const averageTime = (endTime - startTime) / iterations;
      
      // 平均执行时间应该在合理范围内（小于1000ms）
      expect(averageTime).toBeLessThan(1000);
    });

    it('应该高效处理大数据集', async () => {
      const largeDataset = new Array(100).fill(0).map((_, i) => ({
        userId: `user_${i}`,
        sessionId: `session_${i}`,
        timestamp: Date.now(),
        userProfile: {
          age: 20 + (i % 60),
                     gender: (i % 2 === 0 ? 'male' : 'female') as 'male' | 'female',
          height: 150 + (i % 50),
          weight: 50 + (i % 50),
          occupation: '测试',
          medicalHistory: [],
          allergies: [],
          medications: []
        }
      }));

      const startTime = performance.now();
      
      // 批量处理测试
      const promises = largeDataset.slice(0, 10).map(input => engine.analyze(input));
      await Promise.all(promises);
      
      const endTime = performance.now();
      
      // 应该在合理时间内处理完成（小于5秒）
      expect(endTime - startTime).toBeLessThan(5000);
    });

    it('应该不会造成内存泄漏', async () => {
      const initialMemory = process.memoryUsage().heapUsed;
      
      // 执行多次分析
      for (let i = 0; i < 50; i++) {
        const testInput: DiagnosisInput = {
          userId: `memory_test_${i}`,
          sessionId: `memory_session_${i}`,
          timestamp: Date.now(),
          userProfile: {
            age: 30,
            gender: 'male',
            height: 175,
            weight: 70,
            occupation: '测试',
            medicalHistory: [],
            allergies: [],
            medications: []
          }
        };
        await engine.analyze(testInput);
      }
      
      // 强制垃圾回收（如果可用）
      if (global.gc) {
        global.gc();
      }
      
      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;
      
      // 内存增长应该是最小的（小于50MB）
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
    });
  });
});