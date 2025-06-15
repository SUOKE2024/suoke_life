/**
 * Agentic AI 端到端测试
 * 模拟真实用户场景的完整流程测试
 */

import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { AgenticIntegration } from '../../src/core/agentic/AgenticIntegration';
import { AgenticTask } from '../../src/core/agentic/AgenticWorkflowEngine';

describe('Agentic AI End-to-End Tests', () => {
  let agenticSystem: AgenticIntegration;

  beforeEach(async () => {
    agenticSystem = new AgenticIntegration();
    await agenticSystem.initialize();
  });

  afterEach(async () => {
    await agenticSystem.shutdown();
  });

  describe('完整用户健康管理旅程', () => {
    test('新用户首次健康评估完整流程', async () => {
      // 场景：35岁女性白领，首次使用索克生活进行健康评估
      const userProfile = {
        id: 'new_user_001',
        age: 35,
        gender: 'female' as const,
        height: 165,
        weight: 60,
        medicalHistory: [],
        allergies: [],
        currentMedications: [],
        lifestyle: {
          occupation: 'office_worker',
          workSchedule: 'regular',
          exerciseFrequency: 'rarely',
          smokingStatus: 'never',
          drinkingStatus: 'occasional'
        },
        preferences: {
          communicationStyle: 'detailed',
          treatmentPreference: 'tcm_western_combined',
          privacyLevel: 'high'
        }
      };

      // 步骤1：初始健康咨询
      const initialConsultation: AgenticTask = {
        id: 'e2e_initial_consultation',
        type: 'consultation',
        description: '新用户初始健康咨询',
        priority: 'high',
        context: {
          userId: userProfile.id,
          sessionId: 'e2e_session_001',
          currentChannel: 'health',
          userProfile,
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '疲劳',
              severity: 6,
              duration: '2个月',
              description: '工作压力大，经常感到疲倦，下午尤其明显'
            },
            {
              name: '失眠',
              severity: 7,
              duration: '3周',
              description: '入睡困难，夜间易醒，早晨起床困难'
            },
            {
              name: '颈肩痛',
              severity: 5,
              duration: '1个月',
              description: '长期伏案工作导致的颈肩部酸痛'
            }
          ],
          environmentalFactors: {
            location: '北京',
            temperature: 22,
            humidity: 55,
            airQuality: 75,
            season: '春季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { agents: ['xiaoai'] }, // 首次咨询由小艾负责
            mandatory: true
          }
        ],
        expectedOutcome: '初步健康评估和后续建议'
      };

      const consultationResult = await agenticSystem.processTask(initialConsultation);
      
      expect(consultationResult.success).toBe(true);
      expect(consultationResult.recommendations).toBeDefined();
      expect(consultationResult.nextSteps).toBeDefined();
      expect(consultationResult.urgencyLevel).toBeDefined();

      // 步骤2：基于初步评估进行详细五诊
      const fiveDiagnosisTask: AgenticTask = {
        id: 'e2e_five_diagnosis',
        type: 'diagnosis',
        description: '详细五诊评估',
        priority: 'high',
        context: {
          ...initialConsultation.context,
          previousResults: consultationResult,
          // 模拟用户提供的五诊信息
          fiveDiagnosisData: {
            wang: {
              complexion: '面色略黄，有黑眼圈',
              tongue: {
                color: '淡红',
                coating: '薄白略腻',
                texture: '舌体偏胖，有齿痕'
              },
              spirit: '精神疲倦，反应稍慢'
            },
            wen: {
              voice: '声音正常',
              breathing: '呼吸平稳',
              cough: null
            },
            wen2: {
              sleep: '入睡困难，多梦，早醒',
              appetite: '食欲一般，偏爱甜食',
              thirst: '不太想喝水',
              urination: '夜尿1-2次',
              defecation: '大便偏软，不成形'
            },
            qie: {
              pulse: {
                position: '沉',
                rate: '略缓',
                strength: '弱',
                rhythm: '规律'
              },
              abdomen: '腹部柔软，按压无不适'
            },
            suan: {
              constitution: '待分析',
              syndrome: '待分析',
              severity: 'moderate'
            }
          }
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { agents: ['xiaoke'] }, // 五诊由小克负责
            mandatory: true
          },
          {
            type: 'tool',
            specification: { toolId: 'five_diagnosis_system' },
            mandatory: true
          }
        ],
        expectedOutcome: '完整的中医诊断结果'
      };

      const diagnosisResult = await agenticSystem.processTask(fiveDiagnosisTask);
      
      expect(diagnosisResult.success).toBe(true);
      expect(diagnosisResult.diagnosis).toBeDefined();
      expect(diagnosisResult.diagnosis.syndrome).toBeDefined();
      expect(diagnosisResult.diagnosis.constitution).toBeDefined();
      expect(diagnosisResult.diagnosis.severity).toBeDefined();

      // 步骤3：制定个性化治疗方案
      const treatmentPlanTask: AgenticTask = {
        id: 'e2e_treatment_plan',
        type: 'treatment',
        description: '个性化治疗方案制定',
        priority: 'high',
        context: {
          ...fiveDiagnosisTask.context,
          diagnosisResults: diagnosisResult
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { 
              agents: ['xiaoke', 'soer'], // 小克负责中医治疗，索儿负责生活方式
              specialization: {
                xiaoke: 'tcm_treatment',
                soer: 'lifestyle_optimization'
              }
            },
            mandatory: true
          }
        ],
        expectedOutcome: '综合治疗方案'
      };

      const treatmentResult = await agenticSystem.processTask(treatmentPlanTask);
      
      expect(treatmentResult.success).toBe(true);
      expect(treatmentResult.treatmentPlan).toBeDefined();
      expect(treatmentResult.treatmentPlan.tcmTreatment).toBeDefined();
      expect(treatmentResult.treatmentPlan.lifestyle).toBeDefined();
      expect(treatmentResult.treatmentPlan.diet).toBeDefined();
      expect(treatmentResult.treatmentPlan.exercise).toBeDefined();

      // 步骤4：生成个性化健康管理计划
      const healthPlanTask: AgenticTask = {
        id: 'e2e_health_plan',
        type: 'lifestyle',
        description: '个性化健康管理计划',
        priority: 'medium',
        context: {
          ...treatmentPlanTask.context,
          treatmentResults: treatmentResult
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { agents: ['soer'] },
            mandatory: true
          }
        ],
        expectedOutcome: '长期健康管理计划'
      };

      const healthPlanResult = await agenticSystem.processTask(healthPlanTask);
      
      expect(healthPlanResult.success).toBe(true);
      expect(healthPlanResult.healthPlan).toBeDefined();
      expect(healthPlanResult.healthPlan.dailyRoutine).toBeDefined();
      expect(healthPlanResult.healthPlan.weeklyGoals).toBeDefined();
      expect(healthPlanResult.healthPlan.monthlyReview).toBeDefined();

      // 验证整个流程的连贯性
      expect(healthPlanResult.healthPlan.basedOnDiagnosis).toBe(diagnosisResult.diagnosis.syndrome);
      expect(healthPlanResult.healthPlan.alignsWithTreatment).toBe(true);

      console.log(`新用户健康评估流程完成:
        初始咨询: ${consultationResult.success ? '✓' : '✗'}
        五诊评估: ${diagnosisResult.success ? '✓' : '✗'}
        治疗方案: ${treatmentResult.success ? '✓' : '✗'}
        健康计划: ${healthPlanResult.success ? '✓' : '✗'}
        总体质量分数: ${((consultationResult.qualityScore + diagnosisResult.qualityScore + treatmentResult.qualityScore + healthPlanResult.qualityScore) / 4).toFixed(2)}`);
    });

    test('老年用户慢性病管理完整流程', async () => {
      // 场景：68岁男性，患有高血压和糖尿病，需要综合管理
      const elderlyUserProfile = {
        id: 'elderly_user_001',
        age: 68,
        gender: 'male' as const,
        height: 170,
        weight: 75,
        medicalHistory: [
          {
            condition: '高血压',
            diagnosedDate: new Date('2018-03-15'),
            status: 'ongoing',
            medications: ['氨氯地平 5mg', '厄贝沙坦 150mg']
          },
          {
            condition: '2型糖尿病',
            diagnosedDate: new Date('2020-07-20'),
            status: 'ongoing',
            medications: ['二甲双胍 500mg', '格列齐特 80mg']
          }
        ],
        allergies: ['磺胺类药物'],
        currentMedications: [
          '氨氯地平 5mg 每日一次',
          '厄贝沙坦 150mg 每日一次',
          '二甲双胍 500mg 每日两次',
          '格列齐特 80mg 每日一次'
        ],
        lifestyle: {
          occupation: 'retired',
          workSchedule: 'flexible',
          exerciseFrequency: 'light_daily',
          smokingStatus: 'former_smoker',
          drinkingStatus: 'never'
        }
      };

      // 步骤1：慢性病状态评估
      const chronicDiseaseAssessment: AgenticTask = {
        id: 'e2e_chronic_assessment',
        type: 'diagnosis',
        description: '慢性病综合评估',
        priority: 'high',
        context: {
          userId: elderlyUserProfile.id,
          sessionId: 'e2e_elderly_session_001',
          currentChannel: 'health',
          userProfile: elderlyUserProfile,
          medicalHistory: elderlyUserProfile.medicalHistory,
          currentSymptoms: [
            {
              name: '血压波动',
              severity: 6,
              duration: '2周',
              description: '最近血压控制不稳定，收缩压在140-160之间'
            },
            {
              name: '血糖升高',
              severity: 7,
              duration: '1周',
              description: '餐后血糖经常超过10mmol/L'
            },
            {
              name: '下肢水肿',
              severity: 5,
              duration: '3天',
              description: '双下肢轻度水肿，按压有凹陷'
            }
          ],
          environmentalFactors: {
            location: '上海',
            temperature: 28,
            humidity: 75,
            airQuality: 70,
            season: '夏季'
          },
          timestamp: new Date(),
          // 最近的检查结果
          recentLabResults: {
            bloodPressure: { systolic: 155, diastolic: 95 },
            bloodGlucose: { fasting: 8.2, postprandial: 12.5 },
            hba1c: 8.1,
            creatinine: 95,
            urea: 6.8
          }
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { 
              agents: ['laoke', 'xiaoke'], // 老克负责老年病，小克负责中医分析
              specialization: {
                laoke: 'chronic_disease_management',
                xiaoke: 'tcm_syndrome_analysis'
              }
            },
            mandatory: true
          }
        ],
        expectedOutcome: '慢性病综合评估报告'
      };

      const assessmentResult = await agenticSystem.processTask(chronicDiseaseAssessment);
      
      expect(assessmentResult.success).toBe(true);
      expect(assessmentResult.chronicDiseaseStatus).toBeDefined();
      expect(assessmentResult.riskAssessment).toBeDefined();
      expect(assessmentResult.complications).toBeDefined();

      // 步骤2：药物调整建议
      const medicationAdjustment: AgenticTask = {
        id: 'e2e_medication_adjustment',
        type: 'treatment',
        description: '药物调整建议',
        priority: 'high',
        context: {
          ...chronicDiseaseAssessment.context,
          assessmentResults: assessmentResult
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { agents: ['laoke'] },
            mandatory: true
          },
          {
            type: 'safety_check',
            specification: { 
              checkDrugInteractions: true,
              checkAllergies: true,
              checkContraindications: true
            },
            mandatory: true
          }
        ],
        expectedOutcome: '安全的药物调整方案'
      };

      const medicationResult = await agenticSystem.processTask(medicationAdjustment);
      
      expect(medicationResult.success).toBe(true);
      expect(medicationResult.medicationPlan).toBeDefined();
      expect(medicationResult.safetyChecks).toBeDefined();
      expect(medicationResult.monitoringPlan).toBeDefined();

      // 步骤3：生活方式干预计划
      const lifestyleIntervention: AgenticTask = {
        id: 'e2e_lifestyle_intervention',
        type: 'lifestyle',
        description: '老年慢性病生活方式干预',
        priority: 'medium',
        context: {
          ...medicationAdjustment.context,
          medicationResults: medicationResult
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { 
              agents: ['soer', 'laoke'],
              specialization: {
                soer: 'lifestyle_optimization',
                laoke: 'elderly_safety'
              }
            },
            mandatory: true
          }
        ],
        expectedOutcome: '适合老年人的生活方式干预计划'
      };

      const lifestyleResult = await agenticSystem.processTask(lifestyleIntervention);
      
      expect(lifestyleResult.success).toBe(true);
      expect(lifestyleResult.dietPlan).toBeDefined();
      expect(lifestyleResult.exercisePlan).toBeDefined();
      expect(lifestyleResult.safetyGuidelines).toBeDefined();

      // 步骤4：长期监护计划
      const monitoringPlan: AgenticTask = {
        id: 'e2e_monitoring_plan',
        type: 'monitoring',
        description: '长期健康监护计划',
        priority: 'medium',
        context: {
          ...lifestyleIntervention.context,
          lifestyleResults: lifestyleResult
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { agents: ['laoke'] },
            mandatory: true
          }
        ],
        expectedOutcome: '个性化监护计划'
      };

      const monitoringResult = await agenticSystem.processTask(monitoringPlan);
      
      expect(monitoringResult.success).toBe(true);
      expect(monitoringResult.monitoringSchedule).toBeDefined();
      expect(monitoringResult.alertThresholds).toBeDefined();
      expect(monitoringResult.emergencyProtocol).toBeDefined();

      console.log(`老年慢性病管理流程完成:
        病情评估: ${assessmentResult.success ? '✓' : '✗'}
        药物调整: ${medicationResult.success ? '✓' : '✗'}
        生活干预: ${lifestyleResult.success ? '✓' : '✗'}
        监护计划: ${monitoringResult.success ? '✓' : '✗'}
        风险等级: ${assessmentResult.riskAssessment?.level || 'unknown'}`);
    });

    test('急性症状紧急处理流程', async () => {
      // 场景：45岁男性，突发胸痛，需要紧急评估和处理
      const emergencyUserProfile = {
        id: 'emergency_user_001',
        age: 45,
        gender: 'male' as const,
        height: 175,
        weight: 80,
        medicalHistory: [
          {
            condition: '高血脂',
            diagnosedDate: new Date('2022-01-10'),
            status: 'ongoing',
            medications: ['阿托伐他汀 20mg']
          }
        ],
        allergies: [],
        currentMedications: ['阿托伐他汀 20mg 每晚一次'],
        lifestyle: {
          occupation: 'manager',
          workSchedule: 'stressful',
          exerciseFrequency: 'rarely',
          smokingStatus: 'current_smoker',
          drinkingStatus: 'regular'
        }
      };

      // 步骤1：紧急症状评估
      const emergencyAssessment: AgenticTask = {
        id: 'e2e_emergency_assessment',
        type: 'emergency',
        description: '急性胸痛紧急评估',
        priority: 'urgent',
        context: {
          userId: emergencyUserProfile.id,
          sessionId: 'e2e_emergency_session_001',
          currentChannel: 'emergency',
          userProfile: emergencyUserProfile,
          medicalHistory: emergencyUserProfile.medicalHistory,
          currentSymptoms: [
            {
              name: '胸痛',
              severity: 9,
              duration: '30分钟',
              description: '突发性胸骨后压榨性疼痛，向左臂放射，伴有出汗'
            },
            {
              name: '气短',
              severity: 7,
              duration: '30分钟',
              description: '呼吸困难，感觉透不过气'
            },
            {
              name: '恶心',
              severity: 6,
              duration: '20分钟',
              description: '恶心，有呕吐感'
            }
          ],
          environmentalFactors: {
            location: '北京',
            temperature: 35,
            humidity: 80,
            airQuality: 60,
            season: '夏季'
          },
          timestamp: new Date(),
          urgencyIndicators: {
            painLevel: 9,
            vitalSigns: {
              heartRate: 110,
              bloodPressure: { systolic: 160, diastolic: 100 },
              respiratoryRate: 24,
              temperature: 37.2
            },
            consciousnessLevel: 'alert'
          }
        },
        requirements: [
          {
            type: 'emergency_protocol',
            specification: { 
              maxResponseTime: 30, // 30秒内响应
              riskLevel: 'high',
              requiresImmediate: true
            },
            mandatory: true
          },
          {
            type: 'collaboration',
            specification: { 
              agents: ['xiaoai'], // 紧急情况由小艾快速响应
              emergencyMode: true
            },
            mandatory: true
          }
        ],
        expectedOutcome: '紧急处理建议和转诊指导'
      };

      const emergencyResult = await agenticSystem.processTask(emergencyAssessment);
      
      expect(emergencyResult.success).toBe(true);
      expect(emergencyResult.urgencyLevel).toBe('high');
      expect(emergencyResult.immediateActions).toBeDefined();
      expect(emergencyResult.hospitalRecommendation).toBeDefined();
      expect(emergencyResult.responseTime).toBeLessThan(30000); // 30秒内响应

      // 步骤2：紧急指导和监护
      const emergencyGuidance: AgenticTask = {
        id: 'e2e_emergency_guidance',
        type: 'guidance',
        description: '紧急情况指导',
        priority: 'urgent',
        context: {
          ...emergencyAssessment.context,
          emergencyResults: emergencyResult
        },
        requirements: [
          {
            type: 'real_time_monitoring',
            specification: { 
              monitoringInterval: 60, // 每分钟监控
              alertThresholds: {
                heartRate: { min: 60, max: 120 },
                bloodPressure: { systolic: { max: 180 }, diastolic: { max: 110 } }
              }
            },
            mandatory: true
          }
        ],
        expectedOutcome: '实时指导和监护'
      };

      const guidanceResult = await agenticSystem.processTask(emergencyGuidance);
      
      expect(guidanceResult.success).toBe(true);
      expect(guidanceResult.guidanceSteps).toBeDefined();
      expect(guidanceResult.monitoringActive).toBe(true);
      expect(guidanceResult.emergencyContacts).toBeDefined();

      console.log(`紧急处理流程完成:
        紧急评估: ${emergencyResult.success ? '✓' : '✗'}
        响应时间: ${emergencyResult.responseTime}ms
        紧急等级: ${emergencyResult.urgencyLevel}
        建议行动: ${emergencyResult.immediateActions?.join(', ') || 'none'}
        转诊建议: ${emergencyResult.hospitalRecommendation ? '✓' : '✗'}`);
    });
  });

  describe('多智能体协作场景', () => {
    test('复杂疑难病例多智能体会诊', async () => {
      // 场景：复杂症状，需要多个智能体协作诊断
      const complexCaseProfile = {
        id: 'complex_case_001',
        age: 42,
        gender: 'female' as const,
        height: 162,
        weight: 58,
        medicalHistory: [
          {
            condition: '甲状腺功能减退',
            diagnosedDate: new Date('2021-05-15'),
            status: 'ongoing',
            medications: ['左甲状腺素钠 50μg']
          },
          {
            condition: '抑郁症',
            diagnosedDate: new Date('2022-08-20'),
            status: 'stable',
            medications: ['舍曲林 50mg']
          }
        ],
        allergies: ['阿司匹林'],
        currentMedications: ['左甲状腺素钠 50μg', '舍曲林 50mg']
      };

      const complexConsultation: AgenticTask = {
        id: 'e2e_complex_consultation',
        type: 'comprehensive_analysis',
        description: '复杂疑难病例多智能体会诊',
        priority: 'high',
        context: {
          userId: complexCaseProfile.id,
          sessionId: 'e2e_complex_session_001',
          currentChannel: 'health',
          userProfile: complexCaseProfile,
          medicalHistory: complexCaseProfile.medicalHistory,
          currentSymptoms: [
            {
              name: '慢性疲劳',
              severity: 8,
              duration: '6个月',
              description: '持续性疲劳，休息后无明显改善'
            },
            {
              name: '关节疼痛',
              severity: 6,
              duration: '4个月',
              description: '多关节疼痛，晨僵明显'
            },
            {
              name: '记忆力下降',
              severity: 7,
              duration: '3个月',
              description: '注意力不集中，记忆力明显下降'
            },
            {
              name: '皮肤干燥',
              severity: 5,
              duration: '2个月',
              description: '皮肤异常干燥，有脱屑'
            }
          ],
          environmentalFactors: {
            location: '广州',
            temperature: 30,
            humidity: 85,
            airQuality: 65,
            season: '夏季'
          },
          timestamp: new Date(),
          labResults: {
            tsh: 8.5, // 偏高
            t3: 3.2,
            t4: 65, // 偏低
            antiTpo: 120, // 偏高
            esr: 45, // 偏高
            crp: 12 // 偏高
          }
        },
        requirements: [
          {
            type: 'collaboration',
            specification: { 
              agents: ['xiaoai', 'xiaoke', 'laoke', 'soer'],
              collaborationType: 'consensus_building',
              specialization: {
                xiaoai: 'patient_communication',
                xiaoke: 'tcm_syndrome_differentiation',
                laoke: 'chronic_disease_analysis',
                soer: 'lifestyle_factors'
              }
            },
            mandatory: true
          },
          {
            type: 'consensus_threshold',
            specification: { minimumAgreement: 0.8 },
            mandatory: true
          }
        ],
        expectedOutcome: '多智能体协作诊断结果'
      };

      const collaborationResult = await agenticSystem.processTask(complexConsultation);
      
      expect(collaborationResult.success).toBe(true);
      expect(collaborationResult.agentContributions).toBeDefined();
      expect(collaborationResult.consensusScore).toBeGreaterThan(0.8);
      expect(collaborationResult.finalDiagnosis).toBeDefined();
      expect(collaborationResult.treatmentConsensus).toBeDefined();

      // 验证各智能体的贡献
      expect(collaborationResult.agentContributions.xiaoai).toBeDefined();
      expect(collaborationResult.agentContributions.xiaoke).toBeDefined();
      expect(collaborationResult.agentContributions.laoke).toBeDefined();
      expect(collaborationResult.agentContributions.soer).toBeDefined();

      // 验证协作质量
      expect(collaborationResult.collaborationMetrics).toBeDefined();
      expect(collaborationResult.collaborationMetrics.knowledgeSharing).toBeGreaterThan(0.7);
      expect(collaborationResult.collaborationMetrics.decisionQuality).toBeGreaterThan(0.8);

      console.log(`复杂病例协作诊断完成:
        参与智能体: ${Object.keys(collaborationResult.agentContributions).join(', ')}
        共识分数: ${collaborationResult.consensusScore.toFixed(2)}
        知识共享: ${collaborationResult.collaborationMetrics.knowledgeSharing.toFixed(2)}
        决策质量: ${collaborationResult.collaborationMetrics.decisionQuality.toFixed(2)}
        最终诊断: ${collaborationResult.finalDiagnosis.primary}`);
    });
  });

  describe('系统集成验证', () => {
    test('与区块链健康数据系统的完整集成', async () => {
      const blockchainIntegrationTask: AgenticTask = {
        id: 'e2e_blockchain_integration',
        type: 'data_verification',
        description: '区块链健康数据完整性验证',
        priority: 'medium',
        context: {
          userId: 'blockchain_user_001',
          sessionId: 'e2e_blockchain_session_001',
          currentChannel: 'health',
          userProfile: {
            id: 'blockchain_user_001',
            age: 38,
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
          blockchainData: {
            userDataHash: '0x1234567890abcdef1234567890abcdef12345678',
            verificationStatus: 'pending',
            dataIntegrity: true,
            lastUpdate: new Date(),
            accessPermissions: ['read', 'analyze'],
            encryptionLevel: 'high'
          }
        },
        requirements: [
          {
            type: 'blockchain_verification',
            specification: { 
              verifyIntegrity: true,
              checkPermissions: true,
              auditTrail: true
            },
            mandatory: true
          }
        ],
        expectedOutcome: '区块链数据验证和分析结果'
      };

      const blockchainResult = await agenticSystem.processTask(blockchainIntegrationTask);
      
      expect(blockchainResult.success).toBe(true);
      expect(blockchainResult.dataVerification).toBeDefined();
      expect(blockchainResult.dataVerification.isValid).toBe(true);
      expect(blockchainResult.dataVerification.integrityCheck).toBe(true);
      expect(blockchainResult.auditTrail).toBeDefined();

      console.log(`区块链集成验证完成:
        数据完整性: ${blockchainResult.dataVerification.isValid ? '✓' : '✗'}
        权限验证: ${blockchainResult.dataVerification.permissionsValid ? '✓' : '✗'}
        审计追踪: ${blockchainResult.auditTrail ? '✓' : '✗'}`);
    });

    test('微服务架构端到端集成', async () => {
      const microserviceIntegrationTask: AgenticTask = {
        id: 'e2e_microservice_integration',
        type: 'system_integration',
        description: '微服务架构端到端集成测试',
        priority: 'high',
        context: {
          userId: 'integration_user_001',
          sessionId: 'e2e_integration_session_001',
          currentChannel: 'health',
          userProfile: {
            id: 'integration_user_001',
            age: 32,
            gender: 'female',
            height: 165,
            weight: 58,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '头痛',
              severity: 6,
              duration: '2天',
              description: '持续性头痛'
            }
          ],
          environmentalFactors: {
            location: '杭州',
            temperature: 24,
            humidity: 70,
            airQuality: 85,
            season: '春季'
          },
          timestamp: new Date()
        },
        requirements: [
          {
            type: 'microservice_integration',
            specification: { 
              services: [
                'user-service',
                'health-data-service',
                'tcm-service',
                'lifestyle-service',
                'notification-service'
              ],
              testDataFlow: true,
              testServiceCommunication: true
            },
            mandatory: true
          }
        ],
        expectedOutcome: '微服务集成验证结果'
      };

      const integrationResult = await agenticSystem.processTask(microserviceIntegrationTask);
      
      expect(integrationResult.success).toBe(true);
      expect(integrationResult.serviceStatus).toBeDefined();
      expect(integrationResult.dataFlowValidation).toBeDefined();
      expect(integrationResult.communicationTest).toBeDefined();

      // 验证各服务状态
      const services = ['user-service', 'health-data-service', 'tcm-service', 'lifestyle-service', 'notification-service'];
      services.forEach(service => {
        expect(integrationResult.serviceStatus[service]).toBeDefined();
        expect(integrationResult.serviceStatus[service].status).toBe('healthy');
      });

      console.log(`微服务集成测试完成:
        服务健康状态: ${services.map(s => integrationResult.serviceStatus[s].status === 'healthy' ? '✓' : '✗').join(' ')}
        数据流验证: ${integrationResult.dataFlowValidation.isValid ? '✓' : '✗'}
        服务通信: ${integrationResult.communicationTest.allPassed ? '✓' : '✗'}`);
    });
  });
});