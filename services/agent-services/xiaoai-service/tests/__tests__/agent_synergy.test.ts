/**
 * 小艾智能体协同测试
 * 测试小艾在四智能体协同决策中的健康监测和数据收集功能
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { CollaborativeDecisionBus } from '../../../collaborative_decision_bus';
import { XiaoaiService } from '../../xiaoai/core/xiaoai_service';
import { 
  DecisionType, 
  DecisionPriority, 
  VotingStrategy,
  AgentType,
  DecisionContext 
} from '../../../common/types/decision_types';

describe('小艾智能体协同测试', () => {
  let decisionBus: CollaborativeDecisionBus;
  let xiaoaiService: XiaoaiService;
  let mockRedis: any;
  let mockRegistry: any;

  beforeEach(async () => {
    // 模拟Redis连接
    mockRedis = {
      ping: jest.fn().mockResolvedValue('PONG'),
      publish: jest.fn().mockResolvedValue(1),
      subscribe: jest.fn().mockResolvedValue(undefined),
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue('OK'),
      del: jest.fn().mockResolvedValue(1)
    };

    // 模拟服务注册中心
    mockRegistry = {
      getAvailableAgents: jest.fn().mockResolvedValue([
        { type: AgentType.XIAOAI, serviceId: 'xiaoai-001', capabilities: ['health_monitoring'] },
        { type: AgentType.XIAOKE, serviceId: 'xiaoke-001', capabilities: ['diagnosis'] },
        { type: AgentType.LAOKE, serviceId: 'laoke-001', capabilities: ['tcm_syndrome'] },
        { type: AgentType.SOER, serviceId: 'soer-001', capabilities: ['lifestyle'] }
      ]),
      getAgentService: jest.fn().mockImplementation((agentType) => ({
        callMethod: jest.fn().mockResolvedValue({
          confidence: 0.85,
          recommendation: { action: 'monitor_vitals' },
          reasoning: '基于当前健康数据分析'
        })
      }))
    };

    decisionBus = new CollaborativeDecisionBus('redis://localhost:6379');
    decisionBus.redis = mockRedis;
    decisionBus.registry = mockRegistry;

    xiaoaiService = new XiaoaiService();
    await xiaoaiService.initialize();
  });

  afterEach(async () => {
    await decisionBus.close();
    await xiaoaiService.shutdown();
  });

  describe('健康评估协同决策', () => {
    test('应该在健康评估中提供准确的生理数据', async () => {
      const context: DecisionContext = {
        userId: 'user-123',
        sessionId: 'session-456',
        healthData: {
          heartRate: 75,
          bloodPressure: { systolic: 120, diastolic: 80 },
          temperature: 36.5,
          oxygenSaturation: 98
        },
        symptoms: ['轻微头痛', '疲劳'],
        medicalHistory: {
          chronicConditions: [],
          medications: [],
          allergies: []
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-health-001',
        decisionType: DecisionType.HEALTH_ASSESSMENT,
        priority: DecisionPriority.MEDIUM,
        context,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.WEIGHTED,
        timeoutSeconds: 300
      });

      // 等待决策完成
      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.status).toBe('completed');
      
      // 验证小艾的投票包含健康数据分析
      const xiaoaiVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOAI);
      expect(xiaoaiVote).toBeDefined();
      expect(xiaoaiVote?.confidence).toBeGreaterThan(0.7);
      expect(xiaoaiVote?.recommendation).toHaveProperty('vitalSigns');
    });

    test('应该检测异常健康指标并触发紧急协同', async () => {
      const emergencyContext: DecisionContext = {
        userId: 'user-emergency',
        sessionId: 'session-emergency',
        healthData: {
          heartRate: 150, // 异常心率
          bloodPressure: { systolic: 180, diastolic: 110 }, // 高血压
          temperature: 39.2, // 高烧
          oxygenSaturation: 88 // 低血氧
        },
        symptoms: ['胸痛', '呼吸困难', '头晕'],
        medicalHistory: {
          chronicConditions: ['高血压'],
          medications: ['降压药'],
          allergies: []
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-emergency-001',
        decisionType: DecisionType.EMERGENCY_RESPONSE,
        priority: DecisionPriority.EMERGENCY,
        context: emergencyContext,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.XIAOKE, AgentType.LAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 60
      });

      await new Promise(resolve => setTimeout(resolve, 100));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.priority).toBe(DecisionPriority.EMERGENCY);
      
      // 验证小艾识别了紧急情况
      const xiaoaiVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOAI);
      expect(xiaoaiVote?.recommendation).toHaveProperty('urgencyLevel', 'high');
      expect(xiaoaiVote?.recommendation).toHaveProperty('immediateActions');
    });
  });

  describe('中医辨证协同流程', () => {
    test('应该为中医辨证提供客观生理数据支持', async () => {
      const tcmContext: DecisionContext = {
        userId: 'user-tcm-001',
        sessionId: 'session-tcm-001',
        healthData: {
          heartRate: 68, // 偏慢
          bloodPressure: { systolic: 110, diastolic: 70 },
          temperature: 36.2, // 偏低
          skinMoisture: 'dry', // 皮肤干燥
          tongueColor: 'pale', // 舌色淡
          pulseCharacter: 'weak' // 脉象弱
        },
        symptoms: ['乏力', '畏寒', '食欲不振', '大便溏薄'],
        medicalHistory: {
          tcmConstitution: '阳虚质',
          previousDiagnosis: ['脾阳虚'],
          seasonalPatterns: ['冬季症状加重']
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-tcm-syndrome-001',
        decisionType: DecisionType.SYNDROME_DIFFERENTIATION,
        priority: DecisionPriority.MEDIUM,
        context: tcmContext,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.LAOKE, AgentType.SOER]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      
      // 验证小艾提供了支持中医辨证的客观数据
      const xiaoaiVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOAI);
      expect(xiaoaiVote?.recommendation).toHaveProperty('objectiveFindings');
      expect(xiaoaiVote?.recommendation.objectiveFindings).toHaveProperty('vitalSigns');
      expect(xiaoaiVote?.recommendation.objectiveFindings).toHaveProperty('physicalSigns');
      
      // 验证数据支持阳虚证候
      expect(xiaoaiVote?.supportingEvidence).toContain('心率偏慢');
      expect(xiaoaiVote?.supportingEvidence).toContain('体温偏低');
    });

    test('应该监测治疗效果并提供反馈数据', async () => {
      const treatmentContext: DecisionContext = {
        userId: 'user-treatment-001',
        sessionId: 'session-treatment-001',
        healthData: {
          heartRate: 72, // 治疗后改善
          bloodPressure: { systolic: 115, diastolic: 75 },
          temperature: 36.6, // 体温回升
          sleepQuality: 7, // 睡眠改善
          energyLevel: 6 // 精力恢复
        },
        symptoms: ['乏力减轻', '食欲改善'],
        medicalHistory: {
          currentTreatment: {
            tcmFormula: '理中汤加减',
            startDate: '2024-01-01',
            duration: '2周'
          },
          treatmentResponse: 'improving'
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-treatment-monitor-001',
        decisionType: DecisionType.TREATMENT_PLANNING,
        priority: DecisionPriority.MEDIUM,
        context: treatmentContext,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.LAOKE, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.WEIGHTED,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      
      // 验证小艾提供了治疗效果监测数据
      const xiaoaiVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOAI);
      expect(xiaoaiVote?.recommendation).toHaveProperty('treatmentResponse');
      expect(xiaoaiVote?.recommendation.treatmentResponse).toHaveProperty('improvement', true);
      expect(xiaoaiVote?.recommendation).toHaveProperty('continueTreatment', true);
    });
  });

  describe('多智能体数据共享', () => {
    test('应该与其他智能体共享实时健康数据', async () => {
      const sharedContext: DecisionContext = {
        userId: 'user-shared-001',
        sessionId: 'session-shared-001',
        healthData: {
          heartRate: 85,
          bloodPressure: { systolic: 130, diastolic: 85 },
          stressLevel: 7,
          activityLevel: 'moderate',
          sleepHours: 6
        },
        symptoms: ['压力大', '睡眠不足'],
        preferences: {
          treatmentPreference: 'natural',
          lifestyleGoals: ['减压', '改善睡眠']
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-shared-data-001',
        decisionType: DecisionType.LIFESTYLE_GUIDANCE,
        priority: DecisionPriority.MEDIUM,
        context: sharedContext,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.SOER, AgentType.LAOKE]),
        votingStrategy: VotingStrategy.MAJORITY,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      
      // 验证数据在智能体间有效共享
      expect(result?.agentVotes).toHaveLength(3);
      
      // 每个智能体都应该基于小艾提供的健康数据做出建议
      result?.agentVotes.forEach(vote => {
        expect(vote.recommendation).toHaveProperty('basedOnHealthData', true);
      });
    });

    test('应该处理数据冲突和一致性问题', async () => {
      const conflictContext: DecisionContext = {
        userId: 'user-conflict-001',
        sessionId: 'session-conflict-001',
        healthData: {
          heartRate: 95, // 小艾检测
          selfReportedHeartRate: 80, // 用户自报
          bloodPressure: { systolic: 140, diastolic: 90 },
          selfReportedBP: { systolic: 120, diastolic: 80 }
        },
        symptoms: ['心悸', '头晕'],
        metadata: {
          dataConflicts: ['heartRate', 'bloodPressure']
        }
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-conflict-001',
        decisionType: DecisionType.HEALTH_ASSESSMENT,
        priority: DecisionPriority.HIGH,
        context: conflictContext,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.EXPERT_LEAD,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      
      // 验证小艾处理了数据冲突
      const xiaoaiVote = result?.agentVotes.find(v => v.agentType === AgentType.XIAOAI);
      expect(xiaoaiVote?.recommendation).toHaveProperty('dataReliability');
      expect(xiaoaiVote?.recommendation).toHaveProperty('recommendedMeasurement');
      expect(xiaoaiVote?.reasoning).toContain('数据冲突');
    });
  });

  describe('协同决策性能测试', () => {
    test('应该在规定时间内完成协同决策', async () => {
      const startTime = Date.now();
      
      const context: DecisionContext = {
        userId: 'user-perf-001',
        sessionId: 'session-perf-001',
        healthData: {
          heartRate: 78,
          bloodPressure: { systolic: 125, diastolic: 82 }
        },
        symptoms: ['轻微不适']
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-perf-001',
        decisionType: DecisionType.HEALTH_ASSESSMENT,
        priority: DecisionPriority.MEDIUM,
        context,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.MAJORITY,
        timeoutSeconds: 10 // 短超时测试
      });

      const result = await decisionBus.getDecisionResult(requestId);
      const endTime = Date.now();
      
      expect(result).toBeDefined();
      expect(endTime - startTime).toBeLessThan(10000); // 10秒内完成
      expect(result?.status).toBe('completed');
    });

    test('应该处理并发协同决策请求', async () => {
      const requests = [];
      
      for (let i = 0; i < 5; i++) {
        const context: DecisionContext = {
          userId: `user-concurrent-${i}`,
          sessionId: `session-concurrent-${i}`,
          healthData: {
            heartRate: 70 + i * 5,
            bloodPressure: { systolic: 120 + i * 2, diastolic: 80 + i }
          },
          symptoms: [`症状${i}`]
        };

        const promise = decisionBus.submitDecisionRequest({
          requestId: `req-concurrent-${i}`,
          decisionType: DecisionType.HEALTH_ASSESSMENT,
          priority: DecisionPriority.MEDIUM,
          context,
          requiredAgents: new Set([AgentType.XIAOAI, AgentType.XIAOKE]),
          votingStrategy: VotingStrategy.WEIGHTED,
          timeoutSeconds: 300
        });
        
        requests.push(promise);
      }

      const requestIds = await Promise.all(requests);
      expect(requestIds).toHaveLength(5);
      
      // 等待所有决策完成
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // 验证所有决策都完成了
      for (const requestId of requestIds) {
        const result = await decisionBus.getDecisionResult(requestId);
        expect(result).toBeDefined();
        expect(result?.status).toBe('completed');
      }
    });
  });

  describe('错误处理和容错', () => {
    test('应该处理智能体服务不可用的情况', async () => {
      // 模拟小克服务不可用
      mockRegistry.getAgentService.mockImplementation((agentType) => {
        if (agentType === AgentType.XIAOKE) {
          throw new Error('Service unavailable');
        }
        return {
          callMethod: jest.fn().mockResolvedValue({
            confidence: 0.8,
            recommendation: { action: 'continue_monitoring' },
            reasoning: '基于可用数据分析'
          })
        };
      });

      const context: DecisionContext = {
        userId: 'user-error-001',
        sessionId: 'session-error-001',
        healthData: {
          heartRate: 82,
          bloodPressure: { systolic: 128, diastolic: 84 }
        },
        symptoms: ['轻微不适']
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-error-001',
        decisionType: DecisionType.HEALTH_ASSESSMENT,
        priority: DecisionPriority.MEDIUM,
        context,
        requiredAgents: new Set([AgentType.XIAOAI, AgentType.XIAOKE]),
        votingStrategy: VotingStrategy.MAJORITY,
        timeoutSeconds: 300
      });

      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      
      // 应该只有小艾的投票
      expect(result?.agentVotes).toHaveLength(1);
      expect(result?.agentVotes[0].agentType).toBe(AgentType.XIAOAI);
      
      // 决策应该仍然完成，但共识度较低
      expect(result?.status).toBe('completed');
      expect(result?.consensusScore).toBeLessThan(0.8);
    });

    test('应该处理超时情况', async () => {
      // 模拟服务响应缓慢
      mockRegistry.getAgentService.mockImplementation(() => ({
        callMethod: jest.fn().mockImplementation(() => 
          new Promise(resolve => setTimeout(() => resolve({
            confidence: 0.8,
            recommendation: { action: 'delayed_response' },
            reasoning: '延迟响应'
          }), 5000)) // 5秒延迟
        )
      }));

      const context: DecisionContext = {
        userId: 'user-timeout-001',
        sessionId: 'session-timeout-001',
        healthData: {
          heartRate: 76,
          bloodPressure: { systolic: 122, diastolic: 78 }
        },
        symptoms: ['测试症状']
      };

      const requestId = await decisionBus.submitDecisionRequest({
        requestId: 'req-timeout-001',
        decisionType: DecisionType.HEALTH_ASSESSMENT,
        priority: DecisionPriority.MEDIUM,
        context,
        requiredAgents: new Set([AgentType.XIAOAI]),
        votingStrategy: VotingStrategy.MAJORITY,
        timeoutSeconds: 2 // 2秒超时
      });

      await new Promise(resolve => setTimeout(resolve, 3000));

      const result = await decisionBus.getDecisionResult(requestId);
      expect(result).toBeDefined();
      expect(result?.status).toBe('failed');
      expect(result?.errorMessage).toContain('timeout');
    });
  });
}); 