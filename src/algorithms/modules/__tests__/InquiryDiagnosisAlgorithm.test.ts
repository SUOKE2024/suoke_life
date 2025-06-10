import { InquiryDiagnosisAlgorithm } from "../InquiryDiagnosisAlgorithm";

describe("InquiryDiagnosisAlgorithm", () => {
  let algorithm: InquiryDiagnosisAlgorithm;

  beforeEach(() => {
    jest.clearAllMocks();
    algorithm = new InquiryDiagnosisAlgorithm();
  });

  describe("基础功能测试", () => {
    it("应该能够正确初始化", () => {
      expect(algorithm).toBeDefined();
      expect(algorithm).toBeInstanceOf(InquiryDiagnosisAlgorithm);
    });

    it("应该能够处理有效输入", async () => {
      const validInput = {
        symptoms: ["头痛", "发热"],
        duration: "3天",
        severity: "中等",
        location: "头部",
        triggers: ["劳累"],
        relievingFactors: ["休息"]
      };

      const result = await algorithm.analyze(validInput);
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
      expect(result.analysis).toBeDefined();
    });

    it("应该能够处理边界情况", async () => {
      const edgeCaseInput = {
        symptoms: [],
        duration: "",
        severity: "",
        location: "",
        triggers: [],
        relievingFactors: []
      };

      const result = await algorithm.analyze(edgeCaseInput);
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThanOrEqual(0);
    });

    it("应该能够优雅地处理无效输入", async () => {
      const invalidInput = null;

      await expect(algorithm.analyze(invalidInput as any)).rejects.toThrow();
    });

    it("应该返回正确的输出格式", async () => {
      const testInput = {
        symptoms: ["咳嗽", "咽痛"],
        duration: "1周",
        severity: "轻微",
        location: "咽喉",
        triggers: ["感冒"],
        relievingFactors: ["温水"]
      };

      const result = await algorithm.analyze(testInput);
      expect(typeof result).toBe("object");
      expect(result).toHaveProperty("confidence");
      expect(result).toHaveProperty("symptoms");
      expect(result).toHaveProperty("analysis");
      expect(typeof result.confidence).toBe("number");
      expect(typeof result.analysis).toBe("string");
    });
  });

  describe("症状分析测试", () => {
    it("应该能够正确分析症状", async () => {
      const input = {
        symptoms: ["胸闷", "气短", "心悸"],
        duration: "2周",
        severity: "严重",
        location: "胸部",
        triggers: ["运动"],
        relievingFactors: ["静息"]
      };

      const result = await algorithm.analyze(input);
      expect(result.symptoms).toBeDefined();
      expect(result.symptoms.primary).toBeDefined();
      expect(result.symptoms.secondary).toBeDefined();
      expect(Array.isArray(result.symptoms.secondary)).toBe(true);
    });

    it("应该能够评估症状严重程度", async () => {
      const input = {
        symptoms: ["剧烈头痛", "恶心", "呕吐"],
        duration: "急性",
        severity: "严重",
        location: "头部",
        triggers: ["突然发作"],
        relievingFactors: []
      };

      const result = await algorithm.analyze(input);
      expect(result.severity).toBeDefined();
      expect(typeof result.severity.level).toBe("string");
      expect(result.severity.score).toBeGreaterThanOrEqual(0);
      expect(result.severity.score).toBeLessThanOrEqual(10);
    });
  });

  describe("诊断推理测试", () => {
    it("应该能够进行中医辨证", async () => {
      const input = {
        symptoms: ["乏力", "气短", "自汗"],
        duration: "1个月",
        severity: "中等",
        location: "全身",
        triggers: ["劳累"],
        relievingFactors: ["休息", "补气"]
      };

      const result = await algorithm.analyze(input);
      expect(result.tcmPattern).toBeDefined();
      expect(result.tcmPattern.syndrome).toBeDefined();
      expect(typeof result.tcmPattern.syndrome).toBe("string");
      expect(result.tcmPattern.confidence).toBeGreaterThanOrEqual(0);
    });

    it("应该能够提供治疗建议", async () => {
      const input = {
        symptoms: ["失眠", "多梦", "心烦"],
        duration: "2周",
        severity: "中等",
        location: "心神",
        triggers: ["压力"],
        relievingFactors: ["安静环境"]
      };

      const result = await algorithm.analyze(input);
      expect(result.recommendations).toBeDefined();
      expect(Array.isArray(result.recommendations.lifestyle)).toBe(true);
      expect(Array.isArray(result.recommendations.dietary)).toBe(true);
    });
  });
});

describe("InquiryDiagnosisAlgorithm 性能测试", () => {
  let algorithm: InquiryDiagnosisAlgorithm;

  beforeEach(() => {
    algorithm = new InquiryDiagnosisAlgorithm();
  });

  it("应该在性能阈值内执行", async () => {
    const iterations = 10;
    const testInput = {
      symptoms: ["头痛", "发热"],
      duration: "3天",
      severity: "中等",
      location: "头部",
      triggers: ["劳累"],
      relievingFactors: ["休息"]
    };

    const startTime = performance.now();
    
    for (let i = 0; i < iterations; i++) {
      await algorithm.analyze(testInput);
    }
    
    const endTime = performance.now();
    const averageTime = (endTime - startTime) / iterations;
    
    // 平均执行时间应该在50ms以内
    expect(averageTime).toBeLessThan(50);
  });

  it("应该能够高效处理大量数据", async () => {
    const testCases = Array.from({ length: 50 }, (_, i) => ({
      symptoms: [`症状${i}`, `症状${i + 1}`],
      duration: `${i + 1}天`,
      severity: i % 2 === 0 ? "轻微" : "中等",
      location: "全身",
      triggers: [`诱因${i}`],
      relievingFactors: [`缓解因子${i}`]
    }));

    const startTime = performance.now();
    
    const results = await Promise.all(
      testCases.map(testCase => algorithm.analyze(testCase))
    );
    
    const endTime = performance.now();
    
    // 处理50个案例应该在3秒内完成
    expect(endTime - startTime).toBeLessThan(3000);
    expect(results).toHaveLength(50);
    results.forEach(result => {
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThanOrEqual(0);
    });
  });

  it("应该不会造成内存泄漏", async () => {
    const initialMemory = process.memoryUsage().heapUsed;
    const testInput = {
      symptoms: ["测试症状"],
      duration: "1天",
      severity: "轻微",
      location: "测试位置",
      triggers: ["测试诱因"],
      relievingFactors: ["测试缓解"]
    };

    // 执行多次分析
    for (let i = 0; i < 100; i++) {
      await algorithm.analyze(testInput);
    }

    // 强制垃圾回收（如果可用）
    if (global.gc) {
      global.gc();
    }

    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;
    
    // 内存增长应该是最小的（少于5MB）
    expect(memoryIncrease).toBeLessThan(5 * 1024 * 1024);
  });
});