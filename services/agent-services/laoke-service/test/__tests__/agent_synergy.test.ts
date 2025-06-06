import React from 'react';
/**
 * 老克智能体协同测试
 * 测试老克在四智能体协同决策中的中医辨证论治功能
 */

import { describe, test, expect, beforeEach, afterEach, jest } from "@jest/globals";
import { CollaborativeDecisionBus } from "../../../collaborative_decision_bus";
import { LaokeService } from "../../laoke/core/laoke_service";
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
      ping: jest.fn().mockResolvedValue("PONG"),
      publish: jest.fn().mockResolvedValue(1),
      subscribe: jest.fn().mockResolvedValue(undefined),
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue("OK"),
      del: jest.fn().mockResolvedValue(1)
    };

    // 模拟服务注册中心
    mockRegistry = {
      getAvailableAgents: jest.fn().mockResolvedValue([
        { type: AgentType.XIAOAI, serviceId: "xiaoai-001", capabilities: ["health_monitoring"] },
        { type: AgentType.XIAOKE, serviceId: "xiaoke-001", capabilities: ["diagnosis"] },
        { type: AgentType.LAOKE, serviceId: "laoke-001", capabilities: ["tcm_syndrome", "herbal_medicine"] },
        { type: AgentType.SOER, serviceId: "soer-001", capabilities: ["lifestyle"] }
      ]),
      getAgentService: jest.fn().mockImplementation((agentType) => ({
        callMethod: jest.fn().mockResolvedValue({
          confidence: 0.88,
          recommendation: { 
            syndrome: "脾胃虚寒",
            treatment: "温中健脾",
            formula: "理中汤加减"
          },
          reasoning: "基于四诊合参的中医辨证分析"
        })
      }))
    };

    decisionBus = new CollaborativeDecisionBus("redis://localhost:6379");
    decisionBus.redis = mockRedis;
    decisionBus.registry = mockRegistry;

    laokeService = new LaokeService();
    await laokeService.initialize();
  });

  afterEach(async () => {
    await decisionBus.close();
    await laokeService.shutdown();
  });

  describe("中医辨证论治协同决策", () => {
    test(""应该基于四诊信息进行准确的证候辨识", async () => {
      const tcmContext: DecisionContext = {
        userId: "user-tcm-123",
        sessionId: "session-tcm-456",
        healthData: {
          // 望诊信息
          complexion: "pale",
          tongueBody: "pale_tender",
          tongueCoating: "white_thin",
          spirit: "listless",
          // 闻诊信息
          voice: "low_weak",
          breathing: "shallow",
          // 问诊信息
          chills: true,
          coldLimbs: true,
          appetite: "poor",
          stoolCharacter: "loose",
          urination: "clear_long",
          // 切诊信息
          pulsePosition: "deep",
          pulseRate: "slow",
          pulseStrength: "weak"
        },
        symptoms: ["畏寒肢冷", "神疲乏力", "食少腹胀", "大便溏薄", "小便清长"],
        medicalHistory: {
          constitution: "阳虚质",
          chronicConditions: ["慢性胃炎", "功能性消化不良"],
          previousTcmDiagnosis: ["脾胃虚寒"],
          seasonalPattern: "冬重夏轻"
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-tcm-syndrome-001",
        decisionType: DecisionType.SYNDROME_DIFFERENTIATION,
        priority: DecisionPriority.MEDIUM,
        context: tcmContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOAI, AgentType.SOER]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.status).toBe("completed");

      // 验证老克的中医辨证结果
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote).toBeDefined();
      expect(laokeVote?.confidence).toBeGreaterThan(0.8);
      expect(laokeVote?.recommendation).toHaveProperty("syndrome");
      expect(laokeVote?.recommendation).toHaveProperty("pathogenesis");
      expect(laokeVote?.recommendation).toHaveProperty("treatmentPrinciple");
      expect(laokeVote?.recommendation.syndrome).toContain("脾胃虚寒");
    });

    test(""应该制定个性化的中医治疗方案", async () => {
      const treatmentContext: DecisionContext = {
        userId: "user-treatment-001",
        sessionId: "session-treatment-001",
        healthData: {
          syndrome: "肝郁脾虚",
          constitution: "气郁质",
          severity: "moderate",
          duration: "3个月",
          triggers: ["工作压力", "饮食不规律"]
        },
        symptoms: ["胸胁胀痛", "善太息", "食少腹胀", "大便不调", "情志不畅"],
        medicalHistory: {
          westernDiagnosis: ["功能性消化不良", "焦虑状态"],
          currentMedications: ["奥美拉唑", "多潘立酮"],
          allergies: ["青霉素"],
          contraindications: ["孕妇禁用药物"]
        },
        preferences: {
          treatmentType: "herbal_medicine",
          administrationRoute: "oral",
          treatmentDuration: "moderate_term"
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-tcm-treatment-001",
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.HIGH,
        context: treatmentContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的治疗方案
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("herbalFormula");
      expect(laokeVote?.recommendation).toHaveProperty("acupuncturePoints");
      expect(laokeVote?.recommendation).toHaveProperty("dietaryTherapy");
      expect(laokeVote?.recommendation).toHaveProperty("lifestyleAdjustment");

      // 验证方剂组成
      const formula = laokeVote?.recommendation.herbalFormula;
      expect(formula).toHaveProperty("baseFormula");
      expect(formula).toHaveProperty("modifications");
      expect(formula).toHaveProperty("dosage");
      expect(formula).toHaveProperty("administration");

      // 验证安全性考虑
      expect(laokeVote?.recommendation).toHaveProperty("safetyConsiderations");
      expect(laokeVote?.recommendation).toHaveProperty("drugInteractions");
    });
  });

  describe("中西医结合协同诊疗", () => {
    test(""应该与小克协同进行中西医结合诊断", async () => {
      const integratedContext: DecisionContext = {
        userId: "user-integrated-001",
        sessionId: "session-integrated-001",
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
            },
            kidneyFunction: {
              creatinine: 95,
              urea: 6.8,
              gfr: 85
            }
          },
          // 中医四诊信息
          tcmFindings: {
            tongue: "红苔黄腻",
            pulse: "滑数",
            complexion: "面色潮红",
            thirst: "口渴喜冷饮",
            urination: "小便黄赤",
            stool: "大便干结"
          }
        },
        symptoms: ["多饮", "多尿", "多食", "消瘦", "乏力", "口干"],
        medicalHistory: {
          familyHistory: ["糖尿病", "高血压"],
          duration: "6个月",
          westernDiagnosis: ["2型糖尿病", "血脂异常"],
          tcmConstitution: "湿热质"
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-integrated-001",
        decisionType: DecisionType.INTEGRATED_DIAGNOSIS,
        priority: DecisionPriority.HIGH,
        context: integratedContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.CONSENSUS,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的中医诊断
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("tcmSyndrome");
      expect(laokeVote?.recommendation).toHaveProperty("pathogenesis");
      expect(laokeVote?.recommendation.tcmSyndrome).toContain("消渴");

      // 验证中西医结合治疗建议
      expect(laokeVote?.recommendation).toHaveProperty("integratedTreatment");
      expect(laokeVote?.recommendation.integratedTreatment).toHaveProperty("westernMedicine");
      expect(laokeVote?.recommendation.integratedTreatment).toHaveProperty("tcmTreatment");
    });

    test(""应该评估中药与西药的相互作用", async () => {
      const drugInteractionContext: DecisionContext = {
        userId: "user-interaction-001",
        sessionId: "session-interaction-001",
        healthData: {
          currentMedications: [
            "二甲双胍",
            "阿卡波糖",
            "氨氯地平",
            "阿司匹林"
          ],
          proposedTcmFormula: {
            name: "消渴方",
            ingredients: [
              "黄连", "黄芩", "栀子", "大黄",
              "生地黄", "玄参", "麦冬", "五味子"
            ]
          },
          labResults: {
            liverFunction: { alt: 45, ast: 38 },
            kidneyFunction: { creatinine: 88, gfr: 90 }
          }
        },
        medicalHistory: {
          allergies: ["磺胺类"],
          chronicConditions: ["糖尿病", "高血压"],
          previousAdverseReactions: []
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-drug-interaction-001",
        decisionType: DecisionType.DRUG_INTERACTION_CHECK,
        priority: DecisionPriority.HIGH,
        context: drugInteractionContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的药物相互作用分析
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("interactionRisk");
      expect(laokeVote?.recommendation).toHaveProperty("safetyProfile");
      expect(laokeVote?.recommendation).toHaveProperty("dosageAdjustment");
      expect(laokeVote?.recommendation).toHaveProperty("monitoringPlan");
    });
  });

  describe("体质辨识与调理", () => {
    test(""应该准确识别中医体质类型", async () => {
      const constitutionContext: DecisionContext = {
        userId: "user-constitution-001",
        sessionId: "session-constitution-001",
        healthData: {
          physicalCharacteristics: {
            bodyType: "偏瘦",
            complexion: "面色萎黄",
            energy: "精神不振",
            coldTolerance: "畏寒怕冷",
            heatTolerance: "正常"
          },
          digestiveFunction: {
            appetite: "食欲不振",
            digestion: "消化不良",
            stoolPattern: "大便溏薄",
            bloating: "餐后腹胀"
          },
          emotionalState: {
            mood: "情绪低落",
            anxiety: "轻度焦虑",
            sleep: "入睡困难",
            stress: "压力敏感"
          },
          menstrualHistory: {
            cycle: "月经不调",
            flow: "量少色淡",
            pain: "轻度痛经"
          }
        },
        lifestyle: {
          diet: "偏爱温热食物",
          exercise: "运动量少",
          work: "久坐办公",
          sleep: "晚睡早起"
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-constitution-001",
        decisionType: DecisionType.CONSTITUTION_ASSESSMENT,
        priority: DecisionPriority.MEDIUM,
        context: constitutionContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.WEIGHTED,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的体质辨识结果
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("primaryConstitution");
      expect(laokeVote?.recommendation).toHaveProperty("secondaryConstitution");
      expect(laokeVote?.recommendation).toHaveProperty("constitutionScore");
      expect(laokeVote?.recommendation.primaryConstitution).toBe("气虚质");

      // 验证调理方案
      expect(laokeVote?.recommendation).toHaveProperty("regulationPlan");
      expect(laokeVote?.recommendation.regulationPlan).toHaveProperty("herbalRegimen");
      expect(laokeVote?.recommendation.regulationPlan).toHaveProperty("dietaryGuidance");
      expect(laokeVote?.recommendation.regulationPlan).toHaveProperty("exerciseRecommendation");
    });
  });

  describe("季节性养生指导", () => {
    test(""应该提供个性化的季节养生建议", async () => {
      const seasonalContext: DecisionContext = {
        userId: "user-seasonal-001",
        sessionId: "session-seasonal-001",
        healthData: {
          constitution: "阳虚质",
          currentSeason: "冬季",
          climate: {
            temperature: -5,
            humidity: 45,
            region: "北方"
          },
          symptoms: ["手脚冰凉", "腰膝酸软", "夜尿频多", "精神萎靡"],
          seasonalPattern: {
            winter: "症状加重",
            summer: "症状减轻",
            springAutumn: "症状一般"
          }
        },
        lifestyle: {
          occupation: "室外工作",
          exerciseHabits: "运动量少",
          dietPreferences: "喜食生冷",
          sleepPattern: "早睡晚起"
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: "req-seasonal-001",
        decisionType: DecisionType.SEASONAL_WELLNESS,
        priority: DecisionPriority.LOW,
        context: seasonalContext,
        requiredAgents: new Set([AgentType.LAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.COLLABORATIVE,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();

      // 验证老克的季节养生建议
      const laokeVote = result?.agentVotes.find(v => v.agentType === AgentType.LAOKE);
      expect(laokeVote?.recommendation).toHaveProperty("seasonalDiet");
      expect(laokeVote?.recommendation).toHaveProperty("seasonalExercise");
      expect(laokeVote?.recommendation).toHaveProperty("seasonalHerbs");
      expect(laokeVote?.recommendation).toHaveProperty("lifestyleAdjustment");

      // 验证温阳补肾的建议
      expect(laokeVote?.recommendation.seasonalDiet).toContain("温热");
      expect(laokeVote?.recommendation.seasonalHerbs).toContain("补阳");
    });
  });
}); 