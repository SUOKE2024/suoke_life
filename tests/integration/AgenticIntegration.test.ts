/**
 * Agentic AI 系统集成测试
 * 测试各个组件之间的协作和整体系统功能
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { AgenticIntegration } from '../../src/core/agentic/AgenticIntegration';
import { AgenticTask } from '../../src/core/agentic/AgenticWorkflowEngine';

describe('Agentic AI Integration Tests', () => {
  let agenticSystem: AgenticIntegration;

  beforeEach(async () => {
    agenticSystem = new AgenticIntegration();
    await agenticSystem.initialize();
  });

  afterEach(async () => {
    await agenticSystem.shutdown();
    jest.clearAllMocks();
  });

  describe('完整健康管理流程', () => {
    test('应该完成完整的五诊流程', async () => {
      const healthAssessmentTask: AgenticTask = {
        id: 'health_assessment_001',
        type: 'diagnosis',
        description: '完整五诊健康评估',
        priority: 'high',
        context: {
          userId: 'patient_001',
          sessionId: 'session_001',
          currentChannel: 'health',
          userProfile: {
            id: 'patient_001',
            age: 45,
            gender: 'male',
            height: 175,
            weight: 80,
            medicalHistory: [
              {
                condition: '高血压',
                diagnosedDate: new Date('2020-01-15'),
                status: 'ongoing',
                medications: ['氨氯地平']
              }
            ],
            allergies: ['青霉素'],
            currentMedications: ['氨氯地平 5mg']
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '头晕',
              severity: 7,
              duration: '2周',
              description: '早晨起床时明显，伴有轻微恶心'
            },
            {
              name: '失眠',
              severity: 6,
              duration: '1个月',
              description: '入睡困难，多梦'
            }
          ],
          environmentalFactors: {
            location: '北京',
            temperature: 15,
            humidity: 45,
            airQuality: 65,
            season: '秋季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { agents: ['xiaoai', 'xiaoke', 'laoke'] },
            mandatory: true
          },
          {
            type: 'tool',
            specification: { toolId: 'five_diagnosis_system' },
            mandatory: true
          }
        ],
        expectedOutcome: '完整的中医诊断和治疗方案'
      };

      const result = await agenticSystem.processTask(healthAssessmentTask);

      expect(result.success).toBe(true);
      expect(result.diagnosis).toBeDefined();
      expect(result.diagnosis.syndrome).toBeDefined(); // 中医证候
      expect(result.diagnosis.constitution).toBeDefined(); // 体质类型
      expect(result.treatmentPlan).toBeDefined();
      expect(result.treatmentPlan.prescription).toBeDefined(); // 方剂
      expect(result.treatmentPlan.lifestyle).toBeDefined(); // 生活方式建议
      expect(result.treatmentPlan.diet).toBeDefined(); // 饮食建议
      
      // 验证五诊数据
      expect(result.fiveDiagnosisData).toBeDefined();
      expect(result.fiveDiagnosisData.wang).toBeDefined(); // 望诊
      expect(result.fiveDiagnosisData.wen).toBeDefined(); // 闻诊
      expect(result.fiveDiagnosisData.wen2).toBeDefined(); // 问诊
      expect(result.fiveDiagnosisData.qie).toBeDefined(); // 切诊
      expect(result.fiveDiagnosisData.suan).toBeDefined(); // 算诊

      // 验证质量分数
      expect(result.qualityScore).toBeGreaterThan(0.8);
      expect(result.confidence).toBeGreaterThan(0.85);
    });

    test('应该处理复杂的多智能体协作场景', async () => {
      const complexTask: AgenticTask = {
        id: 'complex_collaboration_001',
        type: 'treatment',
        description: '老年慢性病综合管理',
        priority: 'high',
        context: {
          userId: 'elderly_patient_001',
          sessionId: 'session_002',
          currentChannel: 'health',
          userProfile: {
            id: 'elderly_patient_001',
            age: 72,
            gender: 'female',
            height: 160,
            weight: 65,
            medicalHistory: [
              {
                condition: '糖尿病',
                diagnosedDate: new Date('2015-03-20'),
                status: 'ongoing',
                medications: ['二甲双胍', '格列齐特']
              },
              {
                condition: '骨质疏松',
                diagnosedDate: new Date('2018-11-10'),
                status: 'ongoing',
                medications: ['钙片', '维生素D']
              }
            ],
            allergies: [],
            currentMedications: ['二甲双胍 500mg', '格列齐特 80mg', '钙片']
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '腰痛',
              severity: 8,
              duration: '3个月',
              description: '持续性钝痛，活动后加重'
            },
            {
              name: '乏力',
              severity: 6,
              duration: '2个月',
              description: '全身无力，精神不振'
            }
          ],
          environmentalFactors: {
            location: '上海',
            temperature: 20,
            humidity: 70,
            airQuality: 75,
            season: '春季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { 
              agents: ['xiaoke', 'laoke', 'soer'],
              specialization: {
                xiaoke: 'tcm_diagnosis',
                laoke: 'elderly_care',
                soer: 'lifestyle_optimization'
              }
            },
            mandatory: true
          }
        ],
        expectedOutcome: '综合性老年健康管理方案'
      };

      const result = await agenticSystem.processTask(complexTask);

      expect(result.success).toBe(true);
      
      // 验证各智能体的贡献
      expect(result.agentContributions).toBeDefined();
      expect(result.agentContributions.xiaoke).toBeDefined(); // 中医诊断
      expect(result.agentContributions.laoke).toBeDefined(); // 老年护理
      expect(result.agentContributions.soer).toBeDefined(); // 生活方式

      // 验证综合治疗方案
      expect(result.treatmentPlan.tcmTreatment).toBeDefined();
      expect(result.treatmentPlan.elderlyCarePlan).toBeDefined();
      expect(result.treatmentPlan.lifestyleOptimization).toBeDefined();

      // 验证协作质量
      expect(result.collaborationMetrics).toBeDefined();
      expect(result.collaborationMetrics.consensusScore).toBeGreaterThan(0.8);
      expect(result.collaborationMetrics.knowledgeSharing).toBeGreaterThan(0.7);
    });
  });

  describe('与现有系统集成', () => {
    test('应该与五诊系统无缝集成', async () => {
      const fiveDiagnosisTask: AgenticTask = {
        id: 'five_diagnosis_integration_001',
        type: 'diagnosis',
        description: '五诊系统集成测试',
        priority: 'medium',
        context: {
          userId: 'integration_user_001',
          sessionId: 'session_003',
          currentChannel: 'health',
          userProfile: {
            id: 'integration_user_001',
            age: 30,
            gender: 'female',
            height: 165,
            weight: 55,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '月经不调',
              severity: 5,
              duration: '6个月',
              description: '周期不规律，量少'
            }
          ],
          environmentalFactors: {
            location: '广州',
            temperature: 28,
            humidity: 80,
            airQuality: 70,
            season: '夏季'
          },
          timestamp: new Date(),
          // 模拟五诊数据
          fiveDiagnosisData: {
            wang: {
              complexion: '面色萎黄',
              tongue: {
                color: '淡红',
                coating: '薄白',
                texture: '偏瘦'
              },
              spirit: '精神疲倦'
            },
            wen: {
              voice: '声音低微',
              breathing: '呼吸平稳',
              cough: null
            },
            wen2: {
              sleep: '入睡困难，多梦',
              appetite: '食欲不振',
              thirst: '不欲饮',
              urination: '正常',
              defecation: '便溏'
            },
            qie: {
              pulse: {
                position: '沉',
                rate: '缓',
                strength: '弱',
                rhythm: '规律'
              },
              abdomen: '腹部柔软，无压痛'
            },
            suan: {
              constitution: '气虚质',
              syndrome: '脾肾阳虚',
              severity: 'moderate'
            }
          }
        },
        requirements: [
          {
            type: 'tool',
            specification: { toolId: 'five_diagnosis_analyzer' },
            mandatory: true
          }
        ],
        expectedOutcome: '基于五诊的精准诊断'
      };

      const result = await agenticSystem.processTask(fiveDiagnosisTask);

      expect(result.success).toBe(true);
      expect(result.diagnosis.basedOnFiveDiagnosis).toBe(true);
      expect(result.diagnosis.syndrome).toBe('脾肾阳虚');
      expect(result.diagnosis.constitution).toBe('气虚质');
      
      // 验证治疗方案与五诊结果的一致性
      expect(result.treatmentPlan.prescription).toContain('温阳');
      expect(result.treatmentPlan.diet.recommendations).toContain('温热');
    });

    test('应该与区块链健康数据系统集成', async () => {
      const blockchainTask: AgenticTask = {
        id: 'blockchain_integration_001',
        type: 'data_analysis',
        description: '区块链健康数据分析',
        priority: 'medium',
        context: {
          userId: 'blockchain_user_001',
          sessionId: 'session_004',
          currentChannel: 'health',
          userProfile: {
            id: 'blockchain_user_001',
            age: 40,
            gender: 'male',
            height: 178,
            weight: 75,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '深圳',
            temperature: 26,
            humidity: 75,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date(),
          // 模拟区块链健康数据
          blockchainHealthData: {
            dataHash: '0x1234567890abcdef',
            verificationStatus: 'verified',
            dataIntegrity: true,
            historicalRecords: [
              {
                timestamp: new Date('2024-01-01'),
                type: 'vital_signs',
                data: { heartRate: 72, bloodPressure: '120/80' }
              },
              {
                timestamp: new Date('2024-02-01'),
                type: 'lab_results',
                data: { glucose: 95, cholesterol: 180 }
              }
            ]
          }
        },
        requirements: [
          {
            type: 'tool',
            specification: { toolId: 'blockchain_data_analyzer' },
            mandatory: true
          }
        ],
        expectedOutcome: '基于区块链数据的健康分析'
      };

      const result = await agenticSystem.processTask(blockchainTask);

      expect(result.success).toBe(true);
      expect(result.dataVerification).toBeDefined();
      expect(result.dataVerification.isVerified).toBe(true);
      expect(result.dataVerification.integrityCheck).toBe(true);
      
      // 验证历史数据分析
      expect(result.historicalAnalysis).toBeDefined();
      expect(result.historicalAnalysis.trends).toBeDefined();
      expect(result.healthScore).toBeGreaterThan(0);
    });

    test('应该与微服务架构集成', async () => {
      const microserviceTask: AgenticTask = {
        id: 'microservice_integration_001',
        type: 'comprehensive_analysis',
        description: '微服务架构集成测试',
        priority: 'high',
        context: {
          userId: 'microservice_user_001',
          sessionId: 'session_005',
          currentChannel: 'health',
          userProfile: {
            id: 'microservice_user_001',
            age: 35,
            gender: 'female',
            height: 162,
            weight: 58,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '焦虑',
              severity: 7,
              duration: '1个月',
              description: '工作压力大，心情烦躁'
            }
          ],
          environmentalFactors: {
            location: '杭州',
            temperature: 22,
            humidity: 65,
            airQuality: 85,
            season: '春季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'microservice',
            specification: { 
              services: [
                'user-service',
                'health-data-service',
                'tcm-service',
                'lifestyle-service'
              ]
            },
            mandatory: true
          }
        ],
        expectedOutcome: '跨微服务的综合健康分析'
      };

      const result = await agenticSystem.processTask(microserviceTask);

      expect(result.success).toBe(true);
      
      // 验证各微服务的响应
      expect(result.serviceResponses).toBeDefined();
      expect(result.serviceResponses['user-service']).toBeDefined();
      expect(result.serviceResponses['health-data-service']).toBeDefined();
      expect(result.serviceResponses['tcm-service']).toBeDefined();
      expect(result.serviceResponses['lifestyle-service']).toBeDefined();

      // 验证服务间数据一致性
      expect(result.dataConsistency).toBeDefined();
      expect(result.dataConsistency.isConsistent).toBe(true);
    });
  });

  describe('性能和可靠性', () => {
    test('应该在高负载下保持性能', async () => {
      const concurrentTasks = Array.from({ length: 20 }, (_, i) => ({
        id: `load_test_task_${i}`,
        type: 'consultation' as const,
        description: `负载测试任务 ${i}`,
        priority: 'medium' as const,
        context: {
          userId: `load_user_${i}`,
          sessionId: `load_session_${i}`,
          currentChannel: 'health' as const,
          userProfile: {
            id: `load_user_${i}`,
            age: 25 + i,
            gender: i % 2 === 0 ? 'male' as const : 'female' as const,
            height: 170,
            weight: 65,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '疲劳',
              severity: 5,
              duration: '1周',
              description: '工作疲劳'
            }
          ],
          environmentalFactors: {
            location: '成都',
            temperature: 20,
            humidity: 60,
            airQuality: 75,
            season: '春季'
          },
          timestamp: new Date()
        },
        requirements: [],
        expectedOutcome: '快速健康咨询'
      }));

      const startTime = performance.now();
      
      const results = await Promise.all(
        concurrentTasks.map(task => agenticSystem.processTask(task))
      );

      const endTime = performance.now();
      const totalTime = endTime - startTime;
      const avgTimePerTask = totalTime / concurrentTasks.length;

      expect(results).toHaveLength(20);
      expect(results.every(r => r.success)).toBe(true);
      expect(avgTimePerTask).toBeLessThan(1000); // 平均每个任务应在1秒内完成
      expect(totalTime).toBeLessThan(10000); // 总时间应在10秒内
    });

    test('应该处理系统故障和恢复', async () => {
      const faultTask: AgenticTask = {
        id: 'fault_tolerance_001',
        type: 'diagnosis',
        description: '故障容错测试',
        priority: 'high',
        context: {
          userId: 'fault_user_001',
          sessionId: 'fault_session_001',
          currentChannel: 'health',
          userProfile: {
            id: 'fault_user_001',
            age: 50,
            gender: 'male',
            height: 175,
            weight: 80,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '胸痛',
              severity: 8,
              duration: '30分钟',
              description: '突发性胸痛'
            }
          ],
          environmentalFactors: {
            location: '北京',
            temperature: 25,
            humidity: 60,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'tool',
            specification: { toolId: 'emergency_analyzer' },
            mandatory: true
          }
        ],
        expectedOutcome: '紧急诊断和处理建议'
      };

      // 模拟部分服务故障
      jest.spyOn(agenticSystem as any, 'callMicroservice')
        .mockImplementationOnce(() => Promise.reject(new Error('Service unavailable')))
        .mockImplementation(() => Promise.resolve({ success: true, data: {} }));

      const result = await agenticSystem.processTask(faultTask);

      // 系统应该能够容错并提供结果
      expect(result.success).toBe(true);
      expect(result.fallbackUsed).toBe(true);
      expect(result.diagnosis).toBeDefined();
    });

    test('应该监控系统健康状态', async () => {
      const healthStatus = await agenticSystem.getSystemHealth();

      expect(healthStatus).toBeDefined();
      expect(healthStatus.overall).toBeDefined();
      expect(healthStatus.components).toBeDefined();
      expect(healthStatus.components.workflowEngine).toBeDefined();
      expect(healthStatus.components.reflectionSystem).toBeDefined();
      expect(healthStatus.components.planningSystem).toBeDefined();
      expect(healthStatus.components.collaborationSystem).toBeDefined();
      
      // 验证性能指标
      expect(healthStatus.performance).toBeDefined();
      expect(healthStatus.performance.avgResponseTime).toBeGreaterThan(0);
      expect(healthStatus.performance.successRate).toBeGreaterThan(0.9);
      expect(healthStatus.performance.throughput).toBeGreaterThan(0);
    });
  });

  describe('用户体验验证', () => {
    test('应该提供个性化的用户体验', async () => {
      const personalizationTask: AgenticTask = {
        id: 'personalization_001',
        type: 'lifestyle',
        description: '个性化生活方式建议',
        priority: 'medium',
        context: {
          userId: 'personalized_user_001',
          sessionId: 'personalized_session_001',
          currentChannel: 'lifestyle',
          userProfile: {
            id: 'personalized_user_001',
            age: 28,
            gender: 'female',
            height: 160,
            weight: 52,
            medicalHistory: [],
            allergies: [],
            currentMedications: [],
            preferences: {
              exerciseType: 'yoga',
              dietStyle: 'vegetarian',
              sleepSchedule: 'early_bird',
              stressManagement: 'meditation'
            },
            lifestyle: {
              occupation: 'software_engineer',
              workSchedule: 'flexible',
              exerciseFrequency: '3_times_week',
              smokingStatus: 'never',
              drinkingStatus: 'occasional'
            }
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '西安',
            temperature: 18,
            humidity: 50,
            airQuality: 70,
            season: '秋季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'personalization',
            specification: { 
              level: 'high',
              factors: ['preferences', 'lifestyle', 'environment']
            },
            mandatory: true
          }
        ],
        expectedOutcome: '高度个性化的生活方式优化方案'
      };

      const result = await agenticSystem.processTask(personalizationTask);

      expect(result.success).toBe(true);
      expect(result.personalizationLevel).toBeGreaterThan(0.8);
      
      // 验证个性化建议
      expect(result.recommendations.exercise).toContain('瑜伽');
      expect(result.recommendations.diet).toContain('素食');
      expect(result.recommendations.sleep).toContain('早睡');
      expect(result.recommendations.stress).toContain('冥想');
      
      // 验证环境适应性
      expect(result.environmentalAdaptations).toBeDefined();
      expect(result.environmentalAdaptations.seasonal).toContain('秋季');
      expect(result.environmentalAdaptations.location).toContain('西安');
    });

    test('应该支持多语言和文化适应', async () => {
      const culturalTask: AgenticTask = {
        id: 'cultural_adaptation_001',
        type: 'consultation',
        description: '文化适应性测试',
        priority: 'medium',
        context: {
          userId: 'cultural_user_001',
          sessionId: 'cultural_session_001',
          currentChannel: 'health',
          userProfile: {
            id: 'cultural_user_001',
            age: 45,
            gender: 'male',
            height: 170,
            weight: 70,
            medicalHistory: [],
            allergies: [],
            currentMedications: [],
            culturalBackground: {
              ethnicity: 'han',
              region: 'guangdong',
              language: 'cantonese',
              traditions: ['tcm', 'food_therapy']
            }
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '湿热',
              severity: 6,
              duration: '2周',
              description: '身体沉重，口苦'
            }
          ],
          environmentalFactors: {
            location: '广州',
            temperature: 30,
            humidity: 85,
            airQuality: 65,
            season: '夏季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'cultural_adaptation',
            specification: { 
              region: 'guangdong',
              language: 'cantonese',
              traditions: ['tcm', 'food_therapy']
            },
            mandatory: true
          }
        ],
        expectedOutcome: '文化适应的健康建议'
      };

      const result = await agenticSystem.processTask(culturalTask);

      expect(result.success).toBe(true);
      expect(result.culturalAdaptation).toBeDefined();
      expect(result.culturalAdaptation.region).toBe('guangdong');
      
      // 验证地域特色建议
      expect(result.recommendations.diet).toContain('清热');
      expect(result.recommendations.herbs).toContain('广东');
      expect(result.recommendations.lifestyle).toContain('湿热');
    });
  });
});