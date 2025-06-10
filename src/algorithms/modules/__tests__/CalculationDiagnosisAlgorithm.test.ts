import { CalculationConfig } from "../../config/AlgorithmConfig";
import { TCMKnowledgeBase } from "../../knowledge/TCMKnowledgeBase";
import { CalculationData, CalculationDiagnosisAlgorithm } from "../CalculationDiagnosisAlgorithm";

// Mock dependencies
jest.mock("../../config/AlgorithmConfig");
jest.mock("../../knowledge/TCMKnowledgeBase");

describe("CalculationDiagnosisAlgorithm", () => {
  let algorithm: CalculationDiagnosisAlgorithm;
  let mockConfig: jest.Mocked<CalculationConfig>;
  let mockKnowledgeBase: jest.Mocked<TCMKnowledgeBase>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Create mock instances
    mockConfig = {} as jest.Mocked<CalculationConfig>;
    mockKnowledgeBase = {} as jest.Mocked<TCMKnowledgeBase>;
    
    algorithm = new CalculationDiagnosisAlgorithm(mockConfig, mockKnowledgeBase);
  });

  describe("基础功能测试", () => {
    it("应该能够正确初始化", () => {
      expect(algorithm).toBeDefined();
      expect(algorithm).toBeInstanceOf(CalculationDiagnosisAlgorithm);
    });

    it("应该能够处理有效输入", async () => {
      const validInput: CalculationData = {
        birthDate: "1990-01-01",
        birthTime: "08:00",
        birthPlace: "北京",
        currentDate: "2024-01-01",
        currentTime: "10:00",
        currentLocation: "上海"
      };

      const result = await algorithm.analyze(validInput);
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
      expect(result.analysis).toBeDefined();
    });

    it("应该能够处理边界情况", async () => {
      const edgeCaseInput: CalculationData = {
        birthDate: "2000-02-29", // 闰年
        birthTime: "00:00",
        birthPlace: "",
        currentDate: "2024-12-31",
        currentTime: "23:59",
        currentLocation: ""
      };

      const result = await algorithm.analyze(edgeCaseInput);
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThanOrEqual(0);
    });

    it("应该能够优雅地处理无效输入", async () => {
      const invalidInput: CalculationData = {
        birthDate: "invalid-date",
        birthTime: "25:00", // 无效时间
        birthPlace: "",
        currentDate: "",
        currentTime: "",
        currentLocation: ""
      };

      await expect(algorithm.analyze(invalidInput)).rejects.toThrow();
    });

    it("应该返回正确的输出格式", async () => {
      const testInput: CalculationData = {
        birthDate: "1985-06-15",
        birthTime: "14:30",
        birthPlace: "广州",
        currentDate: "2024-01-15",
        currentTime: "16:00",
        currentLocation: "深圳"
      };

      const result = await algorithm.analyze(testInput);
      expect(typeof result).toBe("object");
      expect(result).toHaveProperty("confidence");
      expect(result).toHaveProperty("fiveElements");
      expect(result).toHaveProperty("constitution");
      expect(result).toHaveProperty("analysis");
      expect(typeof result.confidence).toBe("number");
      expect(typeof result.analysis).toBe("string");
    });
  });

  describe("五行分析测试", () => {
    it("应该能够正确分析五行属性", async () => {
      const input: CalculationData = {
        birthDate: "1990-03-21", // 春分
        birthTime: "12:00",
        birthPlace: "北京",
        currentDate: "2024-01-01",
        currentTime: "12:00",
        currentLocation: "北京"
      };

      const result = await algorithm.analyze(input);
      expect(result.fiveElements).toBeDefined();
      expect(result.fiveElements.birthElements).toBeDefined();
      expect(result.fiveElements.currentElements).toBeDefined();
      expect(result.fiveElements.balance).toBeDefined();
    });

    it("应该能够计算五行平衡度", async () => {
      const input: CalculationData = {
        birthDate: "1988-08-08",
        birthTime: "08:08",
        birthPlace: "北京",
        currentDate: "2024-01-01",
        currentTime: "12:00",
        currentLocation: "北京"
      };

      const result = await algorithm.analyze(input);
      expect(result.fiveElements.balance).toBeDefined();
      expect(typeof result.fiveElements.balance.overall).toBe("number");
      expect(result.fiveElements.balance.overall).toBeGreaterThanOrEqual(0);
      expect(result.fiveElements.balance.overall).toBeLessThanOrEqual(1);
    });
  });

  describe("体质分析测试", () => {
    it("应该能够确定主要体质类型", async () => {
      const input: CalculationData = {
        birthDate: "1992-12-21", // 冬至
        birthTime: "06:00",
        birthPlace: "哈尔滨",
        currentDate: "2024-01-01",
        currentTime: "12:00",
        currentLocation: "哈尔滨"
      };

      const result = await algorithm.analyze(input);
      expect(result.constitution).toBeDefined();
      expect(result.constitution.primaryConstitution).toBeDefined();
      expect(typeof result.constitution.primaryConstitution).toBe("string");
      expect(result.constitution.lifeStageInfluence.characteristics).toBeDefined();
      expect(Array.isArray(result.constitution.lifeStageInfluence.characteristics)).toBe(true);
    });

    it("应该能够提供体质倾向分析", async () => {
      const input: CalculationData = {
        birthDate: "1995-07-07",
        birthTime: "18:00",
        birthPlace: "广州",
        currentDate: "2024-01-01",
        currentTime: "12:00",
        currentLocation: "广州"
      };

      const result = await algorithm.analyze(input);
      expect(result.constitution.vulnerabilities).toBeDefined();
      expect(Array.isArray(result.constitution.vulnerabilities)).toBe(true);
      expect(result.constitution.strengths).toBeDefined();
      expect(Array.isArray(result.constitution.strengths)).toBe(true);
    });
  });
});

describe("CalculationDiagnosisAlgorithm 性能测试", () => {
  let algorithm: CalculationDiagnosisAlgorithm;
  let mockConfig: jest.Mocked<CalculationConfig>;
  let mockKnowledgeBase: jest.Mocked<TCMKnowledgeBase>;

  beforeEach(() => {
    mockConfig = {} as jest.Mocked<CalculationConfig>;
    mockKnowledgeBase = {} as jest.Mocked<TCMKnowledgeBase>;
    algorithm = new CalculationDiagnosisAlgorithm(mockConfig, mockKnowledgeBase);
  });

  it("应该在性能阈值内执行", async () => {
    const iterations = 10;
    const testInput: CalculationData = {
      birthDate: "1990-01-01",
      birthTime: "12:00",
      birthPlace: "北京",
      currentDate: "2024-01-01",
      currentTime: "12:00",
      currentLocation: "北京"
    };

    const startTime = performance.now();
    
    for (let i = 0; i < iterations; i++) {
      await algorithm.analyze(testInput);
    }
    
    const endTime = performance.now();
    const averageTime = (endTime - startTime) / iterations;
    
    // 平均执行时间应该在100ms以内
    expect(averageTime).toBeLessThan(100);
  });

  it("应该能够高效处理大量数据", async () => {
    const testCases: CalculationData[] = Array.from({ length: 100 }, (_, i) => ({
      birthDate: `199${i % 10}-0${(i % 12) + 1}-${(i % 28) + 1}`,
      birthTime: `${i % 24}:${i % 60}`,
      birthPlace: "北京",
      currentDate: "2024-01-01",
      currentTime: "12:00",
      currentLocation: "北京"
    }));

    const startTime = performance.now();
    
    const results = await Promise.all(
      testCases.map(testCase => algorithm.analyze(testCase))
    );
    
    const endTime = performance.now();
    
    // 处理100个案例应该在5秒内完成
    expect(endTime - startTime).toBeLessThan(5000);
    expect(results).toHaveLength(100);
    results.forEach(result => {
      expect(result).toBeDefined();
      expect(result.confidence).toBeGreaterThanOrEqual(0);
    });
  });

  it("应该不会造成内存泄漏", async () => {
    const initialMemory = process.memoryUsage().heapUsed;
    const testInput: CalculationData = {
      birthDate: "1990-01-01",
      birthTime: "12:00",
      birthPlace: "北京",
      currentDate: "2024-01-01",
      currentTime: "12:00",
      currentLocation: "北京"
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
    
    // 内存增长应该是最小的（少于10MB）
    expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
  });
});