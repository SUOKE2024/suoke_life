import { describe, test, expect, beforeEach, afterEach, jest } from "@jest/globals";
  DiagnosticResult,
  AgentResponse,
  { CoordinationSession  } from "../coordination/DiagnosticAgentCoordinator";
describe("诊断服务与智能体协同验证集成测试, () => {", () => {
  let coordinator: DiagnosticAgentCoordinator;
  let aiFramework: EdgeAIInferenceFramework;
  let testUserId: string;
  let testSessionId: string;
  beforeEach(async () => {
    coordinator = new DiagnosticAgentCoordinator();
    aiFramework = new EdgeAIInferenceFramework();
    testUserId = "test_user_12345";
    testSessionId = await coordinator.startCoordinationSession(testUserId);
    // 初始化AI推理框架
await aiFramework.initialize();
  });
  afterEach(async () => {
    if (testSessionId) {
      await coordinator.endSession(testSessionId);
    });
  });
  describe("1. 基础协同功能测试", () => {
    test("应该能够启动协同会话, async () => {"
      const sessionId = await coordinator.startCoordinationSession(testUserId);
      expect(sessionId).toBeDefined();
      expect(sessionId).toMatch(/^coord_\d+_[a-z0-9]+$/);
      const session = coordinator.getSessionStatus(sessionId);
      expect(session).toBeDefined();
      expect(session?.userId).toBe(testUserId);
      expect(session?.status).toBe("active");
    });
    test(应该能够接收诊断结果", async () => {"
      const diagnosticResult: DiagnosticResult = {
      serviceType: "calculation,",
      timestamp: Date.now(),
        data: {
          ziwu_analysis: {
      current_meridian: "lung",
      energy_level: 0.85
          });
        },
        confidence: 0.92,
        metadata: {
          sessionId: testSessionId,
          userId: testUserId,
          version: 1.0.0""
        });
      };
      await coordinator.receiveDiagnosticResult(testSessionId, diagnosticResult);
      const session = coordinator.getSessionStatus(testSessionId);
      expect(session?.diagnosticResults).toHaveLength(1);
      expect(session?.diagnosticResults[0].serviceType).toBe("calculation);"
    });
    test("应该能够接收智能体响应", async () => {
      const agentResponse: AgentResponse = {agentType: xiaoai",
        timestamp: Date.now(),
        analysis: {
      syndrome: "qi_deficiency,",
      severity: "moderate"
        },
        recommendations: [深呼吸练习",适量运动],
        confidence: 0.89,
        metadata: {
          sessionId: testSessionId,
          userId: testUserId,
          version: "1.0.0"
        });
      };
      await coordinator.receiveAgentResponse(testSessionId, agentResponse);
      const session = coordinator.getSessionStatus(testSessionId);
      expect(session?.agentResponses).toHaveLength(1);
      expect(session?.agentResponses[0].agentType).toBe(xiaoai");"
    });
  });
  describe("2. 五诊服务协同测试, () => {", () => {
    test("应该能够处理完整的五诊数据", async () => {
      const diagnosticResults: DiagnosticResult[] = [;
        {
          serviceType: calculation",
          timestamp: Date.now(),
          data: {
            ziwu_analysis: { current_meridian: "lung, energy_level: 0.85 },"
            constitution_analysis: {
      primary_type: "qi_deficiency",
      confidence: 0.92 });
          },
          confidence: 0.92,
          metadata: { sessionId: testSessionId, userId: testUserId, version: 1.0.0" });"
        },
        {
      serviceType: "look,",
      timestamp: Date.now(),
          data: {
            face_analysis: {
      complexion: "pale",
      confidence: 0.88 },
            tongue_analysis: { coating: thin_white", confidence: 0.85 });"
          },
          confidence: 0.88,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        },
        {
      serviceType: "listen",
      timestamp: Date.now(),
          data: {
            voice_analysis: { tone_quality: weak", confidence: 0.79 },"
            breathing_analysis: { pattern: "shallow, confidence: 0.82 });"
          },
          confidence: 0.79,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0" });
        },
        {
          serviceType: inquiry",
          timestamp: Date.now(),
          data: {
            symptoms: ["fatigue, "cold_limbs", poor_appetite"],
            severity_scores: [8, 6, 7]
          },
          confidence: 0.95,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        },
        {
      serviceType: "palpation",
      timestamp: Date.now(),
          data: {
            pulse_analysis: { type: weak_slow", rate: 58, confidence: 0.91 });"
          },
          confidence: 0.91,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        });
      ];
      // 依次接收所有诊断结果
for (const result of diagnosticResults) {
        await coordinator.receiveDiagnosticResult(testSessionId, result);
      });
      const session = coordinator.getSessionStatus(testSessionId);
      expect(session?.diagnosticResults).toHaveLength(5);
      // 验证所有五诊类型都已收集
const serviceTypes = session?.diagnosticResults.map(r => r.serviceType);
      expect(serviceTypes).toContain("calculation");
      expect(serviceTypes).toContain(look");"
      expect(serviceTypes).toContain("listen);"
      expect(serviceTypes).toContain("inquiry");
      expect(serviceTypes).toContain(palpation");"
    });
    test("应该在收集足够诊断数据后触发智能体分析, async () => {"
      const mockTriggerHandler = jest.fn();
      coordinator.on("triggerAgentAnalysis", mockTriggerHandler);
      // 添加3个诊断结果（达到触发阈值）
      const diagnosticResults = [;
        { serviceType: calculation" as const, confidence: 0.92 },"
        { serviceType: "look as const, confidence: 0.88 },"
        { serviceType: "inquiry" as const, confidence: 0.95 });
      ];
      for (const result of diagnosticResults) {
        await coordinator.receiveDiagnosticResult(testSessionId, {
          ...result,
          timestamp: Date.now(),
          data: { test: data" },"
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        });
      });
      expect(mockTriggerHandler).toHaveBeenCalledWith({
        sessionId: testSessionId,
        diagnosticResults: expect.any(Array);
      });
    });
  });
  describe("3. 四智能体协同测试", () => {
    test(应该能够处理四个智能体的响应", async () => {"
      const agentResponses: AgentResponse[] = [;
        {
      agentType: "xiaoai,",
      timestamp: Date.now(),
          analysis: {
      syndrome: "qi_deficiency",
      confidence: 0.89 },
          recommendations: [补气养血"],"
          confidence: 0.89,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        },
        {
      agentType: "xiaoke",
      timestamp: Date.now(),
          analysis: { treatment_plan: [tonify_spleen_qi"], confidence: 0.87 },"
          recommendations: ["中药调理],"
          confidence: 0.87,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0" });
        },
        {
          agentType: laoke",
          timestamp: Date.now(),
          analysis: { lifestyle_advice: ["regular_sleep], confidence: 0.93 },"
          recommendations: ["规律作息"],
          confidence: 0.93,
          metadata: { sessionId: testSessionId, userId: testUserId, version: 1.0.0" });"
        },
        {
      agentType: "soer,",
      timestamp: Date.now(),
          analysis: { emotional_support: ["stress_reduction"], confidence: 0.85 },
          recommendations: [冥想放松"],"
          confidence: 0.85,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        });
      ];
      for (const response of agentResponses) {
        await coordinator.receiveAgentResponse(testSessionId, response);
      });
      const session = coordinator.getSessionStatus(testSessionId);
      expect(session?.agentResponses).toHaveLength(4);
      // 验证所有智能体类型都已响应
const agentTypes = session?.agentResponses.map(r => r.agentType);
      expect(agentTypes).toContain("xiaoai");
      expect(agentTypes).toContain(xiaoke");"
      expect(agentTypes).toContain("laoke);"
      expect(agentTypes).toContain("soer");
    });
    test(应该在收集足够智能体响应后达成共识", async () => {"
      const mockConsensusHandler = jest.fn();
      coordinator.on("consensusReached, mockConsensusHandler);"
      // 添加两个智能体响应（达到共识阈值）
      const agentResponses = [;
        {
          agentType: "xiaoai" as const,
          analysis: { syndrome: qi_deficiency", score: 0.9 },"
          confidence: 0.89
        },
        {
      agentType: "xiaoke as const,",
      analysis: {
      syndrome: "qi_deficiency",
      score: 0.85 },
          confidence: 0.87
        });
      ];
      for (const response of agentResponses) {
        await coordinator.receiveAgentResponse(testSessionId, {
          ...response,
          timestamp: Date.now(),
          recommendations: [],
          metadata: { sessionId: testSessionId, userId: testUserId, version: 1.0.0" });"
        });
      });
      expect(mockConsensusHandler).toHaveBeenCalledWith({
        sessionId: testSessionId,
        consensus: expect.any(Object),
        confidence: expect.any(Number);
      });
    });
  });
  describe("4. 数据一致性验证测试, () => {", () => {
    test("应该能够验证诊断结果一致性", async () => {
      const baseTime = Date.now();
      // 添加时间一致的诊断结果
const consistentResults: DiagnosticResult[] = [;
        {
          serviceType: calculation",
          timestamp: baseTime,
          data: { test: "data1 },"
          confidence: 0.90,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0" });
        },
        {
          serviceType: look",
          timestamp: baseTime + 1000, // 1秒后
data: { test: "data2 },"
          confidence: 0.88,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0" });
        });
      ];
      for (const result of consistentResults) {
        await coordinator.receiveDiagnosticResult(testSessionId, result);
      });
      const validation = await coordinator.validateDiagnosticConsistency(testSessionId);
      expect(validation.isConsistent).toBe(true);
      expect(validation.inconsistencies).toHaveLength(0);
      expect(validation.confidence).toBeGreaterThan(0.8);
    });
    test(应该能够检测时间不一致的诊断结果", async () => {"
      const baseTime = Date.now();
      // 添加时间跨度过大的诊断结果
const inconsistentResults: DiagnosticResult[] = [;
        {
      serviceType: "calculation,",
      timestamp: baseTime,
          data: { test: "data1" },
          confidence: 0.90,
          metadata: { sessionId: testSessionId, userId: testUserId, version: 1.0.0" });"
        },
        {
      serviceType: "look,",
      timestamp: baseTime + 35 * 60 * 1000, // 35分钟后
data: { test: "data2" },
          confidence: 0.88,
          metadata: { sessionId: testSessionId, userId: testUserId, version: 1.0.0" });"
        });
      ];
      for (const result of inconsistentResults) {
        await coordinator.receiveDiagnosticResult(testSessionId, result);
      });
      const validation = await coordinator.validateDiagnosticConsistency(testSessionId);
      expect(validation.isConsistent).toBe(false);
      expect(validation.inconsistencies).toContain("诊断时间跨度过大);"
    });
    test("应该能够检测置信度差异过大的诊断结果", async () => {
      const baseTime = Date.now();
      // 添加置信度差异过大的诊断结果
const inconsistentResults: DiagnosticResult[] = [;
        {
          serviceType: calculation",
          timestamp: baseTime,
          data: { test: "data1 },"
          confidence: 0.95, // 高置信度
metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0" });
        },
        {
          serviceType: look",
          timestamp: baseTime + 1000,
          data: { test: "data2 },"
          confidence: 0.45, // 低置信度
metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0" });
        });
      ];
      for (const result of inconsistentResults) {
        await coordinator.receiveDiagnosticResult(testSessionId, result);
      });
      const validation = await coordinator.validateDiagnosticConsistency(testSessionId);
      expect(validation.isConsistent).toBe(false);
      expect(validation.inconsistencies).toContain(诊断置信度差异过大");"
    });
  });
  describe("5. 边缘AI推理集成测试, () => {", () => {
    test("应该能够与边缘AI推理框架集成", async () => {
      // 模拟加载诊断模型
const modelConfig = {modelId: tcm_diagnosis_model",
        modelType: "onnx as const,",
        modelPath: "/models/tcm_diagnosis.onnx",
        inputShape: [1, 128],
        outputShape: [1, 10],
        precision: fp32" as const,"
        deviceType: "cpu as const,",
        maxBatchSize: 8,
        warmupIterations: 3;
      };
      await aiFramework.loadModel(modelConfig);
      // 执行推理请求
const inferenceRequest = {
      requestId: "test_inference_001",
      modelId: tcm_diagnosis_model",
        inputData: [0.1, 0.2, 0.3], // 模拟诊断特征
priority: "normal as const,",
        timeout: 5000,
        metadata: {
          userId: testUserId,
          sessionId: testSessionId,
          timestamp: Date.now();
        });
      };
      const result = await aiFramework.inference(inferenceRequest);
      expect(result.requestId).toBe("test_inference_001");
      expect(result.confidence).toBeGreaterThan(0);
      expect(result.latency).toBeGreaterThan(0);
    });
    test(应该能够处理批量推理请求", async () => {"
      const modelConfig = {
      modelId: "batch_diagnosis_model,",
      modelType: "onnx" as const,
        modelPath: /models/batch_diagnosis.onnx",
        inputShape: [1, 64],
        outputShape: [1, 5],
        precision: "fp32 as const,",
        deviceType: "cpu" as const,
        maxBatchSize: 4,warmupIterations: 2;
      };
      await aiFramework.loadModel(modelConfig);
      // 创建批量推理请求
const batchRequests = Array.from({ length: 6 }, (_, i) => ({requestId: `batch_request_${i}`,
        modelId: batch_diagnosis_model",
        inputData: Array.from({ length: 64 }, () => Math.random()),
        priority: "normal as const,",
        timeout: 5000,
        metadata: {
          userId: testUserId,
          sessionId: testSessionId,
          timestamp: Date.now();
        });
      }));
      const results = await aiFramework.batchInference(batchRequests);
      expect(results).toHaveLength(6);
      results.forEach((result, index) => {
        expect(result.requestId).toBe(`batch_request_${index}`);
        expect(result.confidence).toBeGreaterThan(0);
      });
    });
  });
  describe("6. 性能和可靠性测试", () => {
    test(应该能够处理高并发协同请求", async () => {"
      const concurrentSessions = 10;
      const sessionPromises = Array.from({ length: concurrentSessions }, async (_, i) => {const sessionId = await coordinator.startCoordinationSession(`user_${i}`);
        // 并发添加诊断结果
const diagnosticResult: DiagnosticResult = {
      serviceType: "calculation,",
      timestamp: Date.now(),
          data: { test: `data_${i}` },
          confidence: 0.9,
          metadata: { sessionId, userId: `user_${i}`, version: "1.0.0" });
        };
        await coordinator.receiveDiagnosticResult(sessionId, diagnosticResult);
        return sessionId;
      });
      const sessionIds = await Promise.all(sessionPromises);
      expect(sessionIds).toHaveLength(concurrentSessions);
      // 清理会话
await Promise.all(sessionIds.map(id => coordinator.endSession(id)))
    });
    test(应该能够获取协同统计信息", async () => {"
      // 创建几个会话
const session1 = await coordinator.startCoordinationSession("user1);"
      const session2 = await coordinator.startCoordinationSession("user2");
      const stats = coordinator.getCoordinationStats();
      expect(stats.activeSessions).toBeGreaterThanOrEqual(2);
      expect(stats.totalSessions).toBeGreaterThanOrEqual(2);
      // 清理
await coordinator.endSession(session1);
      await coordinator.endSession(session2);
    });
    test(应该能够处理错误情况", async () => {"
      // 测试不存在的会话
await expect(
        coordinator.receiveDiagnosticResult("non_existent_session, {"
          serviceType: "calculation",
          timestamp: Date.now(),
          data: {},
          confidence: 0.9,
          metadata: { sessionId: non_existent_session", userId: "test, version: "1.0.0" });
        });
      ).rejects.toThrow(会话不存在");"
      // 测试无效的模型加载
await expect(
        aiFramework.loadModel({
      modelId: "invalid_model,",
      modelType: "invalid" as any,
          modelPath: /invalid/path",
          inputShape: [],
          outputShape: [],
          precision: "fp32,",
          deviceType: "cpu",
          maxBatchSize: 1,
          warmupIterations: 1
        });
      ).rejects.toThrow();
    });
  });
  describe("7. 端到端工作流测试", () => {
    test("应该能够完成完整的诊断-智能体协同工作流, async () => {"
      const workflowResults: any = {};
      // 1. 收集五诊数据
const diagnosticResults: DiagnosticResult[] = [;
        {
      serviceType: "calculation",
      timestamp: Date.now(),
          data: { ziwu_analysis: { meridian: lung", energy: 0.85 } },"
          confidence: 0.92,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        },
        {
      serviceType: "look",
      timestamp: Date.now(),
          data: { face_analysis: { complexion: pale" } },"
          confidence: 0.88,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        },
        {
      serviceType: "listen",
      timestamp: Date.now(),
          data: { voice_analysis: { tone: weak" } },"
          confidence: 0.79,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        });
      ];
      for (const result of diagnosticResults) {
        await coordinator.receiveDiagnosticResult(testSessionId, result);
      });
      workflowResults.diagnosticPhase = "completed";
      // 2. 智能体分析
const agentResponses: AgentResponse[] = [;
        {
          agentType: xiaoai",
          timestamp: Date.now(),
          analysis: { syndrome: "qi_deficiency },"
          recommendations: ["补气"],
          confidence: 0.89,
          metadata: { sessionId: testSessionId, userId: testUserId, version: 1.0.0" });"
        },
        {
      agentType: "xiaoke,",
      timestamp: Date.now(),
          analysis: { treatment: "tonify_qi" },
          recommendations: [中药"],"
          confidence: 0.87,
          metadata: { sessionId: testSessionId, userId: testUserId, version: "1.0.0 });"
        });
      ];
      for (const response of agentResponses) {
        await coordinator.receiveAgentResponse(testSessionId, response);
      });
      workflowResults.agentPhase = "completed";
      // 3. 验证最终状态
const session = coordinator.getSessionStatus(testSessionId);
      expect(session?.status).toBe(completed");"
      expect(session?.consensusResult).toBeDefined();
      workflowResults.consensusPhase = "completed;"
      // 4. 验证数据一致性
const validation = await coordinator.validateDiagnosticConsistency(testSessionId);
      expect(validation.isConsistent).toBe(true);
      workflowResults.validationPhase = "completed";
      // 验证完整工作流
expect(workflowResults.diagnosticPhase).toBe(completed");"
      expect(workflowResults.agentPhase).toBe("completed);"
      expect(workflowResults.consensusPhase).toBe("completed");
      expect(workflowResults.validationPhase).toBe(completed");"
    });
  });
});
});});});});});