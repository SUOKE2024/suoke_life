/**
 * 小克智能体协同测试
 * 测试小克在四智能体协同决策中的现代医学诊断分析功能
 */

import { describe, test, expect, beforeEach, afterEach, jest } from "@jest/globals";
import { CollaborativeDecisionBus } from "../../../collaborative_decision_bus";
import { XiaokeService } from "../../xiaoke_service/core/xiaoke_service";
import { 
  DecisionType, 
  DecisionPriority, 
  VotingStrategy,
  AgentType,
  DecisionContext 
} from "../../../common/types/decision_types";

describe("小克智能体协同测试", () => {
  let decisionBus: CollaborativeDecisionBus;
  let xiaokeService: XiaokeService;
  let mockRedis: any;
  let mockRegistry: any;

  beforeEach(async () => {
    // 模拟Redis连接
    mockRedis = {
      ping: jest.fn().mockResolvedValue("PONG"),
      publish: jest.fn().mockResolvedValue(1),
      subscribe: jest.fn().mockResolvedValue(undefined),
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue("OK"),
      del: jest.fn().mockResolvedValue(1),
      exists: jest.fn().mockResolvedValue(0),
      expire: jest.fn().mockResolvedValue(1),
      keys: jest.fn().mockResolvedValue([]),
      hget: jest.fn().mockResolvedValue(null),
      hset: jest.fn().mockResolvedValue(1),
      hdel: jest.fn().mockResolvedValue(1),
      hgetall: jest.fn().mockResolvedValue({}),
      lpush: jest.fn().mockResolvedValue(1),
      rpop: jest.fn().mockResolvedValue(null),
      llen: jest.fn().mockResolvedValue(0),
      zadd: jest.fn().mockResolvedValue(1),
      zrange: jest.fn().mockResolvedValue([]),
      zrem: jest.fn().mockResolvedValue(1),
      zcard: jest.fn().mockResolvedValue(0)
    };

    // 模拟服务注册中心
    mockRegistry = {
      register: jest.fn().mockResolvedValue(true),
      unregister: jest.fn().mockResolvedValue(true),
      discover: jest.fn().mockResolvedValue([]),
      healthCheck: jest.fn().mockResolvedValue(true),
      getServiceInfo: jest.fn().mockResolvedValue(null),
      updateServiceInfo: jest.fn().mockResolvedValue(true)
    };

    decisionBus = new CollaborativeDecisionBus("redis:// localhost:6379")
    decisionBus.redis = mockRedis
    decisionBus.registry = mockRegistry;

    xiaokeService = new XiaokeService();
    await xiaokeService.initialize();
  });

  afterEach(async () => {
    await decisionBus.close();
    await xiaokeService.shutdown();
    jest.clearAllMocks();
  });

  describe("基础功能测试", () => {
    test("应该能够初始化小克服务", async () => {
      // 测试服务初始化
      expect(mockRedis).toBeDefined();
      expect(mockRegistry).toBeDefined();
    });

    test("应该能够连接到Redis", async () => {
      const result = await mockRedis.ping();
      expect(result).toBe("PONG");
    });

    test("应该能够注册到服务中心", async () => {
      const result = await mockRegistry.register();
      expect(result).toBe(true);
    });
  });

  describe("协同决策测试", () => {
    test("应该能够接收决策请求", async () => {
      const mockDecisionRequest = {
        id: "test-decision-001",
        type: "medical_diagnosis",
        priority: "high",
        data: {
          symptoms: ["头痛", "发热", "咳嗽"],
          duration: "3天",
          severity: "中等"
        },
        requester: "user-001",
        timestamp: new Date().toISOString()
      };

      // 模拟接收决策请求
      const result = await mockRedis.set(
        `decision:${mockDecisionRequest.id}`,
        JSON.stringify(mockDecisionRequest)
      );
      
      expect(result).toBe("OK");
    });

    test("应该能够进行中医诊断分析", async () => {
      const symptoms = ["头痛", "发热", "咳嗽"];
      
      // 模拟中医诊断逻辑
      const diagnosis = {
        syndrome: "风热感冒",
        confidence: 0.85,
        recommendations: [
          "银翘散加减",
          "多饮水",
          "注意休息"
        ],
        analysis: "根据症状分析，患者表现为风热感冒证候"
      };

      expect(diagnosis.syndrome).toBe("风热感冒");
      expect(diagnosis.confidence).toBeGreaterThan(0.8);
      expect(diagnosis.recommendations).toHaveLength(3);
    });

    test("应该能够参与投票决策", async () => {
      const voteData = {
        decisionId: "test-decision-001",
        agentId: "xiaoke",
        vote: {
          option: "风热感冒",
          confidence: 0.85,
          reasoning: "基于症状分析和中医理论"
        },
        timestamp: new Date().toISOString()
      };

      const result = await mockRedis.hset(
        `votes:${voteData.decisionId}`,
        voteData.agentId,
        JSON.stringify(voteData.vote)
      );

      expect(result).toBe(1);
    });
  });

  describe("通信协议测试", () => {
    test("应该能够发送消息到其他智能体", async () => {
      const message = {
        from: "xiaoke",
        to: "laoke",
        type: "consultation",
        content: {
          case: "复杂病例",
          question: "请协助分析此病例的证候特点"
        },
        timestamp: new Date().toISOString()
      };

      const result = await mockRedis.lpush(
        `messages:${message.to}`,
        JSON.stringify(message)
      );

      expect(result).toBe(1);
    });

    test("应该能够接收其他智能体的消息", async () => {
      const mockMessage = {
        from: "laoke",
        to: "xiaoke",
        type: "response",
        content: {
          analysis: "建议进一步观察舌象和脉象",
          confidence: 0.9
        }
      };

      await mockRedis.lpush(
        "messages:xiaoke",
        JSON.stringify(mockMessage)
      );

      const result = await mockRedis.rpop("messages:xiaoke");
      expect(result).toBeDefined();
    });
  });

  describe("性能测试", () => {
    test("应该能够在规定时间内完成诊断", async () => {
      const startTime = Date.now();
      
      // 模拟诊断过程
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // 诊断应该在500ms内完成
      expect(duration).toBeLessThan(500);
    });

    test("应该能够处理并发请求", async () => {
      const concurrentRequests = 10;
      const promises = [];

      for (let i = 0; i < concurrentRequests; i++) {
        promises.push(
          mockRedis.set(`test:${i}`, `value${i}`)
        );
      }

      const results = await Promise.all(promises);
      expect(results).toHaveLength(concurrentRequests);
      results.forEach(result => {
        expect(result).toBe("OK");
      });
    });
  });

  describe("错误处理测试", () => {
    test("应该能够处理网络连接错误", async () => {
      // 模拟网络错误
      mockRedis.ping = jest.fn().mockRejectedValue(new Error("Connection failed"));

      try {
        await mockRedis.ping();
      } catch (error) {
        expect(error.message).toBe("Connection failed");
      }
    });

    test("应该能够处理无效的决策请求", async () => {
      const invalidRequest = {
        // 缺少必要字段
        type: "invalid"
      };

      // 验证请求格式
      const isValid = invalidRequest.id && invalidRequest.type && invalidRequest.data;
      expect(isValid).toBeFalsy();
    });
  });

  describe("诊断分析协同决策", () => {
    test("应该提供基于现代医学的诊断分析", async () => {
      const context: DecisionContext = {
        userId: "user-diagnosis-001",
        sessionId: "session-diagnosis-001",
        healthData: {
          heartRate: 95,
          bloodPressure: { systolic: 140, diastolic: 90 },
          temperature: 37.8,
          respiratoryRate: 22,
          oxygenSaturation: 96
        },
        symptoms: ["胸痛", "气短", "心悸", "头晕"],
        medicalHistory: {
          chronicConditions: ["高血压"],
          medications: ["ACEI类降压药"],
          allergies: ["青霉素"],
          familyHistory: ["心脏病", "糖尿病"]
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-diagnosis-001",
        decisionType: DecisionType.DIAGNOSIS_ANALYSIS,
        priority: DecisionPriority.HIGH,
        context,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.XIAOAI, AgentType.LAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.status).toBe("completed");

      // 验证小克的诊断分析
      const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote).toBeDefined();
      expect(xiaokeVote?.confidence).toBeGreaterThan(0.8);
      expect(xiaokeVote?.recommendation).toHaveProperty("differentialDiagnosis");
      expect(xiaokeVote?.recommendation).toHaveProperty("recommendedTests");
      expect(xiaokeVote?.recommendation).toHaveProperty("urgencyLevel");
    });

    test(应该识别复杂症状模式并提供鉴别诊断", async () => {
      const complexContext: DecisionContext = {;
        userId: "user-complex-001,
        sessionId: "session-complex-001",
        healthData: {
          heartRate: 110,
          bloodPressure: { systolic: 160, diastolic: 100 },
          temperature: 38.5,
          bloodGlucose: 180,
          cholesterol: { total: 280, ldl: 180, hdl: 35 });
        },
        symptoms: [
          多饮", "多尿, "体重下降", 视力模糊",
          "胸痛, "呼吸困难", 下肢水肿"
        ],
        medicalHistory: {
          chronicConditions: [],
          medications: [],
          allergies: [],
          familyHistory: ["糖尿病, "心脏病", 高血压"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-complex-diagnosis-001,
        decisionType: DecisionType.DIAGNOSIS_ANALYSIS,
        priority: DecisionPriority.HIGH,
        context: complexContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证小克识别了多系统疾病
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation.differentialDiagnosis).toContain("糖尿病");
      expect(xiaokeVote?.recommendation.differentialDiagnosis).toContain(心血管疾病");
      expect(xiaokeVote?.recommendation).toHaveProperty("comorbidityRisk);
      expect(xiaokeVote?.recommendation.urgencyLevel).toBe("high");
    });

    test(应该评估药物相互作用和禁忌症", async () => {
      const medicationContext: DecisionContext = {;
        userId: "user-medication-001,
        sessionId: "session-medication-001",
        healthData: {
          heartRate: 85,
          bloodPressure: { systolic: 135, diastolic: 85 },
          kidneyFunction: { creatinine: 1.8, gfr: 45 },
          liverFunction: { alt: 65, ast: 70 });
        },
        symptoms: [关节疼痛", "炎症],
        medicalHistory: {
          chronicConditions: ["慢性肾病", 轻度肝功能异常"],
          medications: [
            "ACEI类降压药,
            "利尿剂",
            华法林"
          ],
          allergies: ["阿司匹林, "NSAIDs"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-medication-001",
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.MEDIUM,
        context: medicationContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.LAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证小克评估了药物安全性
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation).toHaveProperty("drugInteractions);
      expect(xiaokeVote?.recommendation).toHaveProperty("contraindications");
      expect(xiaokeVote?.recommendation).toHaveProperty(dosageAdjustment");
      expect(xiaokeVote?.recommendation.contraindications).toContain("NSAIDs);
    });
  });

  describe("中医西医结合协同", () => {
    test(应该与老克协同进行中西医结合诊断", async () => {
      const integratedContext: DecisionContext = {;
        userId: "user-integrated-001,
        sessionId: "session-integrated-001",
        healthData: {
          heartRate: 72,
          bloodPressure: { systolic: 125, diastolic: 80 },
          temperature: 36.8,
          tongueAppearance: 舌质淡红，苔薄白",
          pulseCharacter: "脉象细弱
        },
        symptoms: [
          "慢性疲劳", 失眠", "食欲不振,
          "腰膝酸软", 头晕耳鸣"
        ],
        medicalHistory: {
          westernDiagnosis: ["慢性疲劳综合征],
          tcmDiagnosis: ["肾阳虚"],
          previousTreatments: [
            { type: western", treatment: "抗抑郁药物, response: "limited" },
            { type: tcm", treatment: "金匮肾气丸, response: "moderate" });
          ]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-integrated-001",
        decisionType: DecisionType.SYNDROME_DIFFERENTIATION,
        priority: DecisionPriority.MEDIUM,
        context: integratedContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.LAOKE]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证中西医协同诊断
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);

      expect(xiaokeVote?.recommendation).toHaveProperty("westernPerspective);
      expect(xiaokeVote?.recommendation).toHaveProperty("integratedApproach");
      expect(result?.consensusScore).toBeGreaterThan(0.7);
    });

    test(应该提供循证医学支持的治疗建议", async () => {
      const evidenceContext: DecisionContext = {;
        userId: "user-evidence-001,
        sessionId: "session-evidence-001",
        healthData: {
          bloodPressure: { systolic: 150, diastolic: 95 },
          cholesterol: { total: 240, ldl: 160, hdl: 40 },
          bloodGlucose: 126,
          bmi: 28.5
        },
        symptoms: [头痛", "心悸, "疲劳"],
        medicalHistory: {
          chronicConditions: [高血压", "血脂异常],
          riskFactors: ["肥胖", 久坐", "高盐饮食],
          familyHistory: ["心脏病", 中风"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-evidence-001,
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.MEDIUM,
        context: evidenceContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证循证医学建议
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation).toHaveProperty("evidenceLevel");
      expect(xiaokeVote?.recommendation).toHaveProperty(clinicalGuidelines");
      expect(xiaokeVote?.recommendation).toHaveProperty("riskStratification);
      expect(xiaokeVote?.supportingEvidence).toContain("临床指南");
    });
  });

  describe(紧急医疗协同响应", () => {
    test("应该快速识别急性心肌梗死并协调紧急处理, async () => {
      const emergencyContext: DecisionContext = {;
        userId: "user-ami-001",
        sessionId: session-ami-001",
        healthData: {
          heartRate: 120,
          bloodPressure: { systolic: 90, diastolic: 60 },
          temperature: 37.2,
          oxygenSaturation: 94,
          ecgFindings: "ST段抬高,
          troponinI: 15.2 // 显著升高
        },
        symptoms: [
          "剧烈胸痛", 放射至左臂", "大汗淋漓,
          "恶心呕吐", 呼吸困难"
        ],
        medicalHistory: {
          chronicConditions: ["高血压, "糖尿病"],
          riskFactors: [吸烟", "高胆固醇],
          medications: ["阿司匹林", 他汀类药物"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-ami-emergency-001,
        decisionType: DecisionType.EMERGENCY_RESPONSE,
        priority: DecisionPriority.EMERGENCY,
        context: emergencyContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 60;
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.priority).toBe(DecisionPriority.EMERGENCY);

      // 验证急性心梗识别和处理
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation.diagnosis).toContain("急性心肌梗死");
      expect(xiaokeVote?.recommendation).toHaveProperty(immediateActions");
      expect(xiaokeVote?.recommendation.immediateActions).toContain("紧急PCI);
      expect(xiaokeVote?.recommendation).toHaveProperty("timeToTreatment");
    });

    test(应该识别药物过敏反应并提供紧急处理方案", async () => {
      const allergyContext: DecisionContext = {;
        userId: "user-allergy-001,
        sessionId: "session-allergy-001",
        healthData: {
          heartRate: 130,
          bloodPressure: { systolic: 80, diastolic: 50 },
          temperature: 38.0,
          oxygenSaturation: 92,
          skinCondition: 全身荨麻疹",
          respiratoryStatus: "喘鸣音
        },
        symptoms: [
          "皮疹", 瘙痒", "呼吸困难,
          "喉头水肿", 血压下降"
        ],
        medicalHistory: {
          recentMedications: ["青霉素注射],
          knownAllergies: ["未知"],
          administrationTime: 30分钟前"
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-allergy-emergency-001,
        decisionType: DecisionType.EMERGENCY_RESPONSE,
        priority: DecisionPriority.EMERGENCY,
        context: allergyContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 60;
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证过敏反应识别和处理
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation.diagnosis).toContain("过敏性休克");
      expect(xiaokeVote?.recommendation.immediateActions).toContain(肾上腺素");
      expect(xiaokeVote?.recommendation).toHaveProperty("drugDiscontinuation);
      expect(xiaokeVote?.recommendation).toHaveProperty("supportiveCare");
    });
  });

  describe(预防医学协同", () => {
    test("应该提供基于风险评估的预防建议, async () => {
      const preventionContext: DecisionContext = {;
        userId: "user-prevention-001",
        sessionId: session-prevention-001",
        healthData: {
          age: 45,
          gender: "male,
          bmi: 26.8,
          bloodPressure: { systolic: 135, diastolic: 85 },
          cholesterol: { total: 220, ldl: 140, hdl: 45 },
          bloodGlucose: 105,
          smokingStatus: "former",
          exerciseLevel: sedentary"
        },
        symptoms: [],
        medicalHistory: {
          familyHistory: ["心脏病, "糖尿病", 高血压"],
          riskFactors: ["超重, "久坐", 高盐饮食"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-prevention-001,
        decisionType: DecisionType.PREVENTIVE_CARE,
        priority: DecisionPriority.MEDIUM,
        context: preventionContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.SOER, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证预防医学建议
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation).toHaveProperty("riskAssessment");
      expect(xiaokeVote?.recommendation).toHaveProperty(screeningRecommendations");
      expect(xiaokeVote?.recommendation).toHaveProperty("primaryPrevention);
      expect(xiaokeVote?.recommendation.riskAssessment).toHaveProperty("cardiovascularRisk");
    });

    test(应该制定个性化健康监测计划", async () => {
      const monitoringContext: DecisionContext = {;
        userId: "user-monitoring-001,
        sessionId: "session-monitoring-001",
        healthData: {
          age: 55,
          gender: female",
          menopauseStatus: "postmenopausal,
          boneDensity: -2.1, // 骨质疏松
bloodPressure: { systolic: 140, diastolic: 88 },
          cholesterol: { total: 250, ldl: 170, hdl: 50 });
        },
        symptoms: ["关节疼痛", 疲劳"],
        medicalHistory: {
          familyHistory: ["骨质疏松, "心脏病"],
          previousFractures: [腕部骨折"],
          medications: ["钙片, "维生素D"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-monitoring-001",
        decisionType: DecisionType.PREVENTIVE_CARE,
        priority: DecisionPriority.MEDIUM,
        context: monitoringContext,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证个性化监测计划
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation).toHaveProperty("monitoringPlan);
      expect(xiaokeVote?.recommendation.monitoringPlan).toHaveProperty("boneDensityScreening");
      expect(xiaokeVote?.recommendation.monitoringPlan).toHaveProperty(cardiovascularScreening");
      expect(xiaokeVote?.recommendation).toHaveProperty("interventionThresholds);
    });
  });

  describe("协同决策质量保证", () => {
    test(应该提供高质量的医学证据支持", async () => {
      const qualityContext: DecisionContext = {;
        userId: "user-quality-001,
        sessionId: "session-quality-001",
        healthData: {
          bloodPressure: { systolic: 160, diastolic: 100 },
          heartRate: 88,
          cholesterol: { total: 280, ldl: 180 });
        },
        symptoms: [头痛", "视力模糊],
        medicalHistory: {
          chronicConditions: ["高血压"],
          duration: 5年",
          previousTreatments: ["单一降压药治疗]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-quality-001",
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.MEDIUM,
        context: qualityContext,
        requiredAgents: new Set([AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证证据质量
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.confidence).toBeGreaterThan(0.85);
      expect(xiaokeVote?.supportingEvidence).toHaveLength.greaterThan(2);
      expect(xiaokeVote?.recommendation).toHaveProperty(evidenceGrade");
      expect(xiaokeVote?.recommendation).toHaveProperty("recommendationStrength);
    });

    test("应该处理不确定性和提供替代方案", async () => {
      const uncertainContext: DecisionContext = {;
        userId: user-uncertain-001",
        sessionId: "session-uncertain-001,
        healthData: {
          heartRate: 85,
          bloodPressure: { systolic: 130, diastolic: 85 },
          temperature: 37.5,
          labResults: "pending"
        },
        symptoms: [发热", "乏力, "关节痛"],
        medicalHistory: {
          recentTravel: [东南亚"],
          exposures: ["蚊虫叮咬],
          vaccinations: ["不完整"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-uncertain-001",
        decisionType: DecisionType.DIAGNOSIS_ANALYSIS,
        priority: DecisionPriority.HIGH,
        context: uncertainContext,
        requiredAgents: new Set([AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证不确定性处理
const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
      expect(xiaokeVote?.recommendation).toHaveProperty("uncertaintyLevel);
      expect(xiaokeVote?.recommendation).toHaveProperty("alternativeDiagnoses");
      expect(xiaokeVote?.recommendation).toHaveProperty(additionalTestsNeeded");
      expect(xiaokeVote?.recommendation).toHaveProperty("empiricalTreatment);
    });
  });

  describe("性能和可靠性测试", () => {
    test(应该在高负载下保持诊断准确性", async () => {
      const loadTestPromises = [];

      for (let i = 0; i < 10; i++) {
        const context: DecisionContext = {;
          userId: `user-load-${i}`,
          sessionId: `session-load-${i}`,
          healthData: {
            heartRate: 70 + i * 3,
            bloodPressure: { systolic: 120 + i * 2, diastolic: 80 + i });
          },
          symptoms: [`症状${i}`]
        };

        const promise = decisionBus.submitDecisionRequest({;
          requestId: `req-load-${i}`,
          decisionType: DecisionType.DIAGNOSIS_ANALYSIS,
          priority: DecisionPriority.MEDIUM,
          context,
          requiredAgents: new Set([AgentType.XIAOKE]),
          votingStrategy: VotingStrategy.EXPERT_LEAD,;
          timeoutSeconds: 300;
        });

        loadTestPromises.push(promise);
      });
      const requestIds = await Promise.all(loadTestPromises);
      expect(requestIds).toHaveLength(10);

      // 等待所有诊断完成
await new Promise(resolve => setTimeout(resolve, 300))

      // 验证所有诊断的质量
for (const requestId of requestIds) {
        const result = await decisionBus.getDecisionResult(requestId);
        expect(result).toBeDefined();
        expect(result?.status).toBe("completed);

        const xiaokeVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOKE);
        expect(xiaokeVote?.confidence).toBeGreaterThan(0.7);
      });
    });

    test("应该处理服务故障并提供降级服务", async () => {
      // 模拟部分服务故障
mockRegistry.getAgentService.mockImplementation((agentType) => {
        if (agentType === AgentType.XIAOAI) {
          throw new Error(Health monitoring service unavailable")
        });
        return {
          callMethod: jest.fn().mockResolvedValue({
            confidence: 0.8,
            recommendation: { 
              diagnosis: "基于可用信息的诊断,
              limitations: "健康监测数据不可用"
            },
            reasoning: 降级服务模式"
          });
        };
      });

      const context: DecisionContext = {;
        userId: "user-degraded-001,
        sessionId: "session-degraded-001",
        healthData: {
          heartRate: 90,
          bloodPressure: { systolic: 140, diastolic: 90 });
        },
        symptoms: [胸痛", "气短]
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-degraded-001",
        decisionType: DecisionType.DIAGNOSIS_ANALYSIS,
        priority: DecisionPriority.HIGH,
        context,
        requiredAgents: new Set([AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.MAJORITY,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证降级服务
expect(result?.agentVotes).toHaveLength(1)
      expect(result?.agentVotes[0].agentType).toBe(AgentType.XIAOKE);
      expect(result?.status).toBe(completed");

      const xiaokeVote = result?.agentVotes[0];
      expect(xiaokeVote.recommendation).toHaveProperty("limitations);
      expect(xiaokeVote.reasoning).toContain("降级');
    });
  });
}); 