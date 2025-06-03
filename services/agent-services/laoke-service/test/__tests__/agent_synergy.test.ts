/**
 * 老克智能体协同测试
 * 测试老克在四智能体协同决策中的中医辨证论治功能
 */

import { describe, test, expect, beforeEach, afterEach, jest } from "@jest/globals";
import { CollaborativeDecisionBus } from "../../../collaborative_decision_bus";
import { LaokeService } from ../../laoke/core/laoke_service";
import { 
  DecisionType, 
  DecisionPriority, 
  VotingStrategy,
  AgentType,
  DecisionContext 
} from "../../../common/types/decision_types";

describe("老克智能体协同测试", () => {
  let decisionBus: CollaborativeDecisionBus;
  let laokeService: LaokeService;
  let mockRedis: any;
  let mockRegistry: any;

  beforeEach(async () => {
    // 模拟Redis连接
mockRedis = {
      ping: jest.fn().mockResolvedValue(PONG"),
      publish: jest.fn().mockResolvedValue(1),
      subscribe: jest.fn().mockResolvedValue(undefined),
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue("OK),
      del: jest.fn().mockResolvedValue(1)
    }

    // 模拟服务注册中心
mockRegistry = {
      getAvailableAgents: jest.fn().mockResolvedValue([
        { type: AgentType.XIAOAI, serviceId: "xiaoai-001", capabilities: [health_monitoring"] },
        { type: AgentType.XIAOKE, serviceId: "xiaoke-001, capabilities: ["diagnosis"] },
        { type: AgentType.LAOKE, serviceId: laoke-001", capabilities: ["tcm_syndrome, "herbal_medicine"] },
        { type: AgentType.SOER, serviceId: soer-001", capabilities: ["lifestyle] });
      ]),
      getAgentService: jest.fn().mockImplementation((agentType) => ({
        callMethod: jest.fn().mockResolvedValue({
          confidence: 0.88,
          recommendation: { 
            syndrome: "脾胃虚寒",
            treatment: 温中健脾",
            formula: "理中汤加减
          },
          reasoning: "基于四诊合参的中医辨证分析"
        });
      }))
    };

    decisionBus = new CollaborativeDecisionBus(redis:// localhost:6379")
    decisionBus.redis = mockRedis
    decisionBus.registry = mockRegistry;

    laokeService = new LaokeService();
    await laokeService.initialize();
  });

  afterEach(async () => {
    await decisionBus.close();
    await laokeService.shutdown();
  });

  describe("中医辨证论治协同决策, () => {
    test("应该基于四诊信息进行准确的证候辨识", async () => {
      const tcmContext: DecisionContext = {;
        userId: user-tcm-123",
        sessionId: "session-tcm-456,
        healthData: {
          // 望诊信息
complexion: "pale",
          tongueBody: pale_tender",
          tongueCoating: "white_thin,
          spirit: "listless",
          // 闻诊信息
voice: low_weak",
          breathing: "shallow,
          // 问诊信息
chills: true,
          coldLimbs: true,
          appetite: "poor",
          stoolCharacter: loose",
          urination: "clear_long,
          // 切诊信息
pulsePosition: "deep",
          pulseRate: slow",
          pulseStrength: "weak
        },
        symptoms: ["畏寒肢冷", 神疲乏力", "食少腹胀, "大便溏薄", 小便清长"],
        medicalHistory: {
          constitution: "阳虚质,
          chronicConditions: ["慢性胃炎", 功能性消化不良"],
          previousTcmDiagnosis: ["脾胃虚寒],
          seasonalPattern: "冬重夏轻"
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-tcm-syndrome-001",
        decisionType: DecisionType.SYNDROME_DIFFERENTIATION,
        priority: DecisionPriority.MEDIUM,
        context: tcmContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOAI, AgentType.SOER]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.status).toBe("completed);

      // 验证老克的中医辨证结果
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote).toBeDefined();
      expect(laokeVote?.confidence).toBeGreaterThan(0.8);
      expect(laokeVote?.recommendation).toHaveProperty("syndrome");
      expect(laokeVote?.recommendation).toHaveProperty(pathogenesis");
      expect(laokeVote?.recommendation).toHaveProperty("treatmentPrinciple);
      expect(laokeVote?.recommendation.syndrome).toContain("脾胃虚寒");
    });

    test(应该制定个性化的中医治疗方案", async () => {
      const treatmentContext: DecisionContext = {;
        userId: "user-treatment-001,
        sessionId: "session-treatment-001",
        healthData: {
          syndrome: 肝郁脾虚",
          constitution: "气郁质,
          severity: "moderate",
          duration: 3个月",
          triggers: ["工作压力, "饮食不规律"]
        },
        symptoms: [胸胁胀痛", "善太息, "食少腹胀", 大便不调", "情志不畅],
        medicalHistory: {
          westernDiagnosis: ["功能性消化不良", 焦虑状态"],
          currentMedications: ["奥美拉唑, "多潘立酮"],
          allergies: [青霉素"],
          contraindications: ["孕妇禁用药物]
        },
        preferences: {
          treatmentType: "herbal_medicine",
          administrationRoute: oral",
          treatmentDuration: "moderate_term
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-tcm-treatment-001",
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.HIGH,
        context: treatmentContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的治疗方案
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty(herbalFormula");
      expect(laokeVote?.recommendation).toHaveProperty("acupuncturePoints);
      expect(laokeVote?.recommendation).toHaveProperty("dietaryTherapy");
      expect(laokeVote?.recommendation).toHaveProperty(lifestyleAdjustment");

      // 验证方剂组成
const formula = laokeVote?.recommendation.herbalFormula;
      expect(formula).toHaveProperty("baseFormula);
      expect(formula).toHaveProperty("modifications");
      expect(formula).toHaveProperty(dosage");
      expect(formula).toHaveProperty("administration);

      // 验证安全性考虑
expect(laokeVote?.recommendation).toHaveProperty("safetyConsiderations")
      expect(laokeVote?.recommendation).toHaveProperty(drugInteractions");
    });
  });

  describe("中西医结合协同诊疗, () => {
    test("应该与小克协同进行中西医结合诊断", async () => {
      const integratedContext: DecisionContext = {;
        userId: user-integrated-001",
        sessionId: "session-integrated-001,
        healthData: {
          // 西医检查结果
labResults: {
            bloodGlucose: 8.5, // mmol/L
hba1c: 7.2, // %
            lipidProfile: {
              totalCholesterol: 6.2,
              ldl: 4.1,
              hdl: 1.0,
              triglycerides: 2.8
            });
          },
          // 中医四诊信息
tcmFindings: {
            tongue: "red_thick_greasy_coating",
            pulse: slippery_rapid",
            complexion: "red,
            thirst: "excessive",
            urination: frequent_yellow"
          });
        },
        symptoms: ["多饮, "多尿", 多食", "乏力, "口干", 便秘"],
        medicalHistory: {
          westernDiagnosis: ["2型糖尿病, "血脂异常"],
          tcmDiagnosis: [消渴病"],
          familyHistory: ["糖尿病, "高血压"],
          lifestyle: [久坐", "高糖饮食, "熬夜"]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-integrated-diagnosis-001",
        decisionType: DecisionType.DIAGNOSIS_ANALYSIS,
        priority: DecisionPriority.HIGH,
        context: integratedContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的中医诊断
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("tcmDiagnosis);
      expect(laokeVote?.recommendation).toHaveProperty("syndromeType");
      expect(laokeVote?.recommendation.tcmDiagnosis).toBe(消渴病");
      expect(laokeVote?.recommendation.syndromeType).toContain("胃热炽盛);

      // 验证中西医结合的共识
expect(result?.consensusScore).toBeGreaterThan(0.7);
      expect(result?.finalRecommendation).toHaveProperty("integratedDiagnosis");
      expect(result?.finalRecommendation).toHaveProperty(combinedTreatment");
    });

    test("应该协调中药与西药的联合使用, async () => {
      const medicationContext: DecisionContext = {;
        userId: "user-medication-001",
        sessionId: session-medication-001",
        healthData: {
          currentMedications: [
            { name: "二甲双胍, dosage: "500mg", frequency: bid" },
            { name: "格列齐特, dosage: "30mg", frequency: qd" });
          ],
          tcmSyndrome: "气阴两虚,
          bloodGlucose: {
            fasting: 7.8,
            postprandial: 12.3,
            hba1c: 7.5
          });
        },
        symptoms: ["乏力", 口干", "多尿, "心悸", 失眠"],
        medicalHistory: {
          diabetesDuration: "5年,
          complications: ["糖尿病肾病早期"],
          allergies: [磺胺类药物"],
          liverFunction: "normal,
          kidneyFunction: "mild_impairment"
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-medication-coordination-001",
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.HIGH,
        context: medicationContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.UNANIMOUS,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的中药方案
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("herbalFormula);
      expect(laokeVote?.recommendation).toHaveProperty("drugInteractionCheck");
      expect(laokeVote?.recommendation).toHaveProperty(administrationTiming");

      // 验证药物相互作用评估
expect(laokeVote?.recommendation.drugInteractionCheck).toHaveProperty("safetyLevel)
      expect(laokeVote?.recommendation.drugInteractionCheck).toHaveProperty("recommendations");

      // 验证给药时间安排
expect(laokeVote?.recommendation.administrationTiming).toHaveProperty(herbalMedicine")
      expect(laokeVote?.recommendation.administrationTiming).toHaveProperty("westernMedicine);
      expect(laokeVote?.recommendation.administrationTiming).toHaveProperty("interval");
    });
  });

  describe(养生保健协同指导", () => {
    test("应该与索儿协同制定季节性养生方案, async () => {
      const seasonalContext: DecisionContext = {;
        userId: "user-seasonal-001",
        sessionId: session-seasonal-001",
        healthData: {
          constitution: "阳虚质,
          currentSeason: "winter",
          climateCharacteristics: [寒冷", "干燥, "风大"],
          healthStatus: suboptimal",
          vulnerabilities: ["易感冒, "关节疼痛", 情绪低落"]
        },
        symptoms: ["畏寒, "乏力", 关节酸痛", "情绪低落, "食欲不振"],
        medicalHistory: {
          seasonalPatterns: [冬季症状加重", "春夏症状缓解],
          chronicConditions: ["慢性关节炎", 轻度抑郁"],
          previousInterventions: ["艾灸, "温阳中药", 运动疗法"]
        },
        preferences: {
          interventionTypes: ["中医养生, "饮食调理", 运动指导"],
          timeAvailability: "moderate,
          economicConsiderations: "budget_conscious"
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: req-seasonal-wellness-001",
        decisionType: DecisionType.PREVENTIVE_CARE,
        priority: DecisionPriority.MEDIUM,
        context: seasonalContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.SOER, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.WEIGHTED,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的中医养生建议
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("seasonalRegimen);
      expect(laokeVote?.recommendation).toHaveProperty("dietaryTherapy");
      expect(laokeVote?.recommendation).toHaveProperty(exerciseGuidance");
      expect(laokeVote?.recommendation).toHaveProperty("emotionalRegulation);

      // 验证季节性调养方案
const regimen = laokeVote?.recommendation.seasonalRegimen;
      expect(regimen).toHaveProperty("yangNourishing");
      expect(regimen).toHaveProperty(warmingMethods");
      expect(regimen).toHaveProperty("preventiveMeasures);

      // 验证与索儿的协同
expect(result?.finalRecommendation).toHaveProperty("integratedLifestyle")
      expect(result?.finalRecommendation).toHaveProperty(practicalImplementation");
    });

    test("应该提供体质调理的长期方案, async () => {
      const constitutionContext: DecisionContext = {;
        userId: "user-constitution-001",
        sessionId: session-constitution-001",
        healthData: {
          constitutionType: "痰湿质,
          constitutionScore: 0.75,
          manifestations: [
            "形体肥胖", 胸闷痰多", "口黏腻, "身重困倦",
            喜食肥甘", "大便黏腻, "舌苔厚腻"
          ],
          riskFactors: [代谢综合征", "心血管疾病, "糖尿病"],
          currentHealth: suboptimal"
        },
        symptoms: ["身重困倦, "胸闷", 痰多", "口黏, "大便黏腻"],
        medicalHistory: {
          bmi: 28.5,
          waistCircumference: 95, // cm
bloodPressure: { systolic: 135, diastolic: 85 },
          bloodLipids: elevated",
          familyHistory: ["糖尿病, "高血压", 肥胖"]
        },
        preferences: {
          treatmentDuration: "long_term,
          interventionIntensity: "gradual",
          followUpFrequency: monthly"
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-constitution-regulation-001,
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.MEDIUM,
        context: constitutionContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.SOER, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的体质调理方案
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("constitutionRegulation");
      expect(laokeVote?.recommendation).toHaveProperty(phasedTreatment");
      expect(laokeVote?.recommendation).toHaveProperty("progressMonitoring);

      // 验证分期治疗方案
const phasedTreatment = laokeVote?.recommendation.phasedTreatment;
      expect(phasedTreatment).toHaveProperty("phase1"); // 化痰除湿期
expect(phasedTreatment).toHaveProperty(phase2") // 健脾益气期
expect(phasedTreatment).toHaveProperty("phase3) // 巩固调养期

      // 验证进展监测指标
expect(laokeVote?.recommendation.progressMonitoring).toHaveProperty("constitutionAssessment")
      expect(laokeVote?.recommendation.progressMonitoring).toHaveProperty(symptomTracking");
      expect(laokeVote?.recommendation.progressMonitoring).toHaveProperty("objectiveMarkers);
    });
  });

  describe("协同决策质量保证", () => {
    test(应该在决策冲突时提供专业调解", async () => {
      const conflictContext: DecisionContext = {;
        userId: "user-conflict-001,
        sessionId: "session-conflict-001",
        healthData: {
          condition: 慢性疲劳综合征",
          westernFindings: ["免疫功能低下, "神经内分泌紊乱"],
          tcmFindings: [肾阳虚", "脾气虚, "心血虚"],
          conflictingRecommendations: true
        },
        symptoms: [极度疲劳", "认知障碍, "睡眠障碍", 肌肉疼痛"],
        medicalHistory: {
          duration: "2年,
          previousTreatments: [
            { type: "western", result: limited_improvement" },
            { type: "tcm, result: "moderate_improvement" });
          ],
          comorbidities: [焦虑", "抑郁]
        });
      };

      // 模拟决策冲突
mockRegistry.getAgentService = jest.fn().mockImplementation((agentType) => {
        if (agentType === AgentType.XIAOKE) {
          return {
            callMethod: jest.fn().mockResolvedValue({
              confidence: 0.7,
              recommendation: { approach: "western_medicine", priority: symptom_management" },
              reasoning: "基于循证医学证据
            });
          };
        } else if (agentType === AgentType.LAOKE) {
          return {
            callMethod: jest.fn().mockResolvedValue({
              confidence: 0.85,
              recommendation: { approach: "tcm_holistic", priority: root_cause_treatment" },
              reasoning: "基于整体观念和辨证论治
            });
          };
        });
        return {
          callMethod: jest.fn().mockResolvedValue({
            confidence: 0.6,
            recommendation: { approach: "supportive" },
            reasoning: 支持性建议"
          });
        };
      });

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-conflict-resolution-001,
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.HIGH,
        context: conflictContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克在冲突解决中的作用
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.confidence).toBeGreaterThan(0.8);
      expect(laokeVote?.recommendation).toHaveProperty("conflictResolution");
      expect(laokeVote?.recommendation).toHaveProperty(integratedApproach");

      // 验证最终决策的整合性
expect(result?.finalRecommendation).toHaveProperty("combinedStrategy)
      expect(result?.consensusScore).toBeGreaterThan(0.6);
    });

    test("应该确保中医治疗的安全性和有效性", async () => {
      const safetyContext: DecisionContext = {;
        userId: user-safety-001",
        sessionId: "session-safety-001,
        healthData: {
          age: 75,
          gender: "female",
          weight: 55, // kg
height: 160, // cm
comorbidities: [高血压", "糖尿病, "慢性肾病"],
          currentMedications: [
            氨氯地平", "二甲双胍, "阿司匹林", 阿托伐他汀"
          ],
          allergyHistory: ["青霉素, "磺胺"],
          organFunction: {
            liver: mild_impairment",
            kidney: "moderate_impairment,
            heart: "normal"
          });
        },
        symptoms: [腰膝酸软", "头晕耳鸣, "夜尿频多", 畏寒肢冷"],
        medicalHistory: {
          tcmDiagnosis: "肾阳虚,
          riskFactors: ["高龄", 多重用药", "器官功能减退]
        });
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-safety-assessment-001",
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.HIGH,
        context: safetyContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.UNANIMOUS,;
        timeoutSeconds: 300;
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的安全性评估
const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty(safetyAssessment");
      expect(laokeVote?.recommendation).toHaveProperty("dosageAdjustment);
      expect(laokeVote?.recommendation).toHaveProperty("monitoringPlan");
      expect(laokeVote?.recommendation).toHaveProperty(contraindications");

      // 验证特殊人群用药考虑
const safetyAssessment = laokeVote?.recommendation.safetyAssessment;
      expect(safetyAssessment).toHaveProperty("ageConsiderations);
      expect(safetyAssessment).toHaveProperty("organFunctionAdjustment");
      expect(safetyAssessment).toHaveProperty(drugInteractionRisk");

      // 验证监测方案
expect(laokeVote?.recommendation.monitoringPlan).toHaveProperty("clinicalParameters)
      expect(laokeVote?.recommendation.monitoringPlan).toHaveProperty("laboratoryTests");
      expect(laokeVote?.recommendation.monitoringPlan).toHaveProperty(followUpSchedule");
    });
  });

  describe("性能和可靠性测试, () => {
    test("应该在高并发情况下保持决策质量", async () => {
      const concurrentRequests = Array.from({ length: 10 }, (_, i) => ({;
        requestId: `req-concurrent-${i}`,
        decisionType: DecisionType.SYNDROME_DIFFERENTIATION,
        priority: DecisionPriority.MEDIUM,
        context: {
          userId: `user-${i}`,
          sessionId: `session-${i}`,
          healthData: { syndrome: 气血两虚" },;
          symptoms: ["乏力, "面色萎黄", 心悸", "失眠],;
          medicalHistory: {});
        },
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      }));

      const startTime = Date.now();
      const promises = concurrentRequests.map(req => ;
        decisionBus.submitDecisionRequest(req);
      );

      const requestIds = await Promise.all(promises);
      expect(requestIds).toHaveLength(10);

      // 等待所有决策完成
await new Promise(resolve => setTimeout(resolve, 200))

      const results = await Promise.all(;
        requestIds.map(id => decisionBus.getDecisionResult(id));
      );

      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // 验证性能
expect(totalTime).toBeLessThan(5000) // 5秒内完成

      // 验证所有决策都成功
results.forEach(result => {
        expect(result).toBeDefined()
        expect(result?.status).toBe("completed");

        const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
        expect(laokeVote?.confidence).toBeGreaterThan(0.7);
      });
    });

    test(应该正确处理超时和错误情况", async () => {
      // 模拟服务超时
mockRegistry.getAgentService = jest.fn().mockImplementation(() => ({
        callMethod: jest.fn().mockImplementation(() => 
          new Promise(resolve => setTimeout(resolve, 400)) // 超时
        )
      }))

      const timeoutContext: DecisionContext = {;
        userId: "user-timeout-001,
        sessionId: "session-timeout-001",
        healthData: { condition: test" },
        symptoms: ["测试症状],
        medicalHistory: {});
      };

      const requestId = await decisionBus.submitDecisionRequest({;
        requestId: "req-timeout-001",
        decisionType: DecisionType.SYNDROME_DIFFERENTIATION,
        priority: DecisionPriority.MEDIUM,
        context: timeoutContext,
        requiredAgents: new Set([AgentType.LAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 1 // 1秒超时
      });

      await new Promise(resolve => setTimeout(resolve, 1500));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.status).toBe(failed");
      expect(result?.errorMessage).toContain('timeout');
    });
  });
}); 