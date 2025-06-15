/**
 * Reflection System 单元测试
 * 测试反思系统的自我评估和改进能力
 */

import { beforeEach, describe, expect, jest, test } from '@jest/globals';
import { ExecutionResult, ReflectionSystem } from '../../src/core/agentic/ReflectionSystem';

describe('ReflectionSystem', () => {
  let reflectionSystem: ReflectionSystem;

  beforeEach(() => {
    reflectionSystem = new ReflectionSystem();
  });

  describe('质量评估', () => {
    test('应该正确评估高质量结果', async () => {
      const highQualityResult: ExecutionResult = {
        stepId: 'diagnosis_step',
        result: {
          diagnosis: '风寒感冒',
          confidence: 0.95,
          evidence: ['症状匹配度高', '舌象典型', '脉象符合'],
          treatment: {
            prescription: '荆防败毒散',
            dosage: '每日三次，每次6g',
            duration: '7天'
          }
        },
        executionTime: 1200,
        status: 'success',
        toolsUsed: ['tcm_analyzer', 'symptom_matcher'],
        qualityScore: 0.95
      };

      const task = {
        id: 'test_task_001',
        type: 'diagnosis',
        description: '测试诊断任务',
        priority: 'medium' as const,
        context: {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health' as const,
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '头痛',
              severity: 6,
              duration: '3天',
              description: '持续性钝痛'
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
        requirements: [],
        expectedOutcome: '准确的诊断结果'
      };

      const reflectionContext = {
        userId: 'user_123',
        sessionId: 'session_456',
        taskType: 'diagnosis',
        executionHistory: [],
        userFeedback: null,
        environmentalFactors: task.context.environmentalFactors,
        timestamp: new Date()
      };

      const reflection = await reflectionSystem.reflect(
        highQualityResult,
        task,
        reflectionContext
      );

      expect(reflection.qualityScore).toBeGreaterThan(0.9);
      expect(reflection.confidence).toBeGreaterThan(0.9);
      expect(reflection.shouldIterate).toBe(false);
      expect(reflection.improvements).toHaveLength(0);
    });

    test('应该识别低质量结果并建议改进', async () => {
      const lowQualityResult: ExecutionResult = {
        stepId: 'diagnosis_step',
        result: {
          diagnosis: '不确定',
          confidence: 0.3,
          evidence: ['症状模糊'],
          treatment: null
        },
        executionTime: 500,
        status: 'success',
        toolsUsed: ['basic_analyzer'],
        qualityScore: 0.3
      };

      const task = {
        id: 'test_task_001',
        type: 'diagnosis',
        description: '测试诊断任务',
        priority: 'medium' as const,
        context: {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health' as const,
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '不适',
              severity: 3,
              duration: '1天',
              description: '说不清楚'
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
        requirements: [],
        expectedOutcome: '准确的诊断结果'
      };

      const reflectionContext = {
        userId: 'user_123',
        sessionId: 'session_456',
        taskType: 'diagnosis',
        executionHistory: [],
        userFeedback: null,
        environmentalFactors: task.context.environmentalFactors,
        timestamp: new Date()
      };

      const reflection = await reflectionSystem.reflect(
        lowQualityResult,
        task,
        reflectionContext
      );

      expect(reflection.qualityScore).toBeLessThan(0.5);
      expect(reflection.shouldIterate).toBe(true);
      expect(reflection.improvements.length).toBeGreaterThan(0);
      expect(reflection.nextActions.length).toBeGreaterThan(0);
    });

    test('应该基于用户反馈调整评估', async () => {
      const result: ExecutionResult = {
        stepId: 'treatment_step',
        result: {
          treatment: '建议多休息',
          confidence: 0.7
        },
        executionTime: 800,
        status: 'success',
        toolsUsed: ['lifestyle_advisor'],
        qualityScore: 0.7
      };

      const userFeedback = {
        rating: 2, // 用户不满意
        comments: '建议太简单，没有针对性',
        helpful: false
      };

      const reflection = await reflectionSystem.reflect(
        'treatment',
        result,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '北京',
            temperature: 25,
            humidity: 60,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date()
        },
        userFeedback
      );

      expect(reflection.qualityScore).toBeLessThan(0.5); // 应该降低质量分数
      expect(reflection.shouldIterate).toBe(true);
      expect(reflection.improvements.some(imp => 
        imp.includes('针对性') || imp.includes('个性化')
      )).toBe(true);
    });
  });

  describe('改进建议生成', () => {
    test('应该为诊断错误提供具体改进建议', async () => {
      const incorrectDiagnosis: ExecutionResult = {
        stepId: 'diagnosis_step',
        result: {
          diagnosis: '热证',
          confidence: 0.8,
          evidence: ['面色红润'],
          treatment: {
            prescription: '清热解毒汤'
          }
        },
        executionTime: 1000,
        status: 'success',
        toolsUsed: ['tcm_analyzer'],
        qualityScore: 0.8
      };

      // 模拟专家反馈指出诊断错误
      const expertFeedback = {
        rating: 1,
        comments: '患者实际为寒证，面色红润是假热现象',
        helpful: false,
        expertCorrection: {
          correctDiagnosis: '寒证',
          reasoning: '舌淡苔白，脉沉迟，为寒证典型表现'
        }
      };

      const reflection = await reflectionSystem.reflect(
        'diagnosis',
        incorrectDiagnosis,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '怕冷',
              severity: 7,
              duration: '5天',
              description: '手脚冰凉'
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
        expertFeedback
      );

      expect(reflection.shouldIterate).toBe(true);
      expect(reflection.improvements.some(imp => 
        imp.includes('舌象') || imp.includes('脉象')
      )).toBe(true);
      expect(reflection.nextActions.some(action => 
        action.includes('重新分析') || action.includes('四诊合参')
      )).toBe(true);
    });

    test('应该识别工具使用不当', async () => {
      const inappropriateToolUse: ExecutionResult = {
        stepId: 'lifestyle_advice',
        result: {
          advice: '建议手术治疗',
          confidence: 0.9
        },
        executionTime: 300,
        status: 'success',
        toolsUsed: ['surgical_advisor'], // 不合适的工具
        qualityScore: 0.2 // 系统检测到不合适
      };

      const reflection = await reflectionSystem.reflect(
        'lifestyle',
        inappropriateToolUse,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'lifestyle',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '北京',
            temperature: 25,
            humidity: 60,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date()
        }
      );

      expect(reflection.shouldIterate).toBe(true);
      expect(reflection.improvements.some(imp => 
        imp.includes('工具选择') || imp.includes('生活方式')
      )).toBe(true);
    });
  });

  describe('学习和适应', () => {
    test('应该从历史反馈中学习', async () => {
      // 模拟多次类似场景的反馈
      const historicalFeedback = [
        {
          scenario: 'headache_diagnosis',
          userRating: 5,
          improvements: ['详细询问病史'],
          outcome: 'successful'
        },
        {
          scenario: 'headache_diagnosis',
          userRating: 3,
          improvements: ['考虑环境因素'],
          outcome: 'partial'
        },
        {
          scenario: 'headache_diagnosis',
          userRating: 4,
          improvements: ['结合舌诊'],
          outcome: 'successful'
        }
      ];

      // 设置历史学习数据
      (reflectionSystem as any).learningHistory = historicalFeedback;

      const currentResult: ExecutionResult = {
        stepId: 'headache_diagnosis',
        result: {
          diagnosis: '偏头痛',
          confidence: 0.75
        },
        executionTime: 1500,
        status: 'success',
        toolsUsed: ['symptom_analyzer'],
        qualityScore: 0.75
      };

      const reflection = await reflectionSystem.reflect(
        'diagnosis',
        currentResult,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '头痛',
              severity: 6,
              duration: '3天',
              description: '持续性钝痛'
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
        }
      );

      // 应该包含从历史中学到的改进建议
      expect(reflection.improvements.some(imp => 
        imp.includes('病史') || imp.includes('环境') || imp.includes('舌诊')
      )).toBe(true);
    });

    test('应该适应不同用户偏好', async () => {
      const userPreferences = {
        preferredTreatmentStyle: 'conservative',
        communicationStyle: 'detailed',
        trustLevel: 'high'
      };

      const result: ExecutionResult = {
        stepId: 'treatment_recommendation',
        result: {
          treatment: '立即服用强效药物',
          confidence: 0.8
        },
        executionTime: 600,
        status: 'success',
        toolsUsed: ['aggressive_treatment_advisor'],
        qualityScore: 0.8
      };

      const reflection = await reflectionSystem.reflect(
        'treatment',
        result,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: [],
            preferences: userPreferences
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '北京',
            temperature: 25,
            humidity: 60,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date()
        }
      );

      // 应该识别治疗风格与用户偏好不匹配
      expect(reflection.improvements.some(imp => 
        imp.includes('保守') || imp.includes('温和')
      )).toBe(true);
    });
  });

  describe('性能优化', () => {
    test('应该快速完成反思过程', async () => {
      const result: ExecutionResult = {
        stepId: 'quick_consultation',
        result: { advice: '多喝水' },
        executionTime: 100,
        status: 'success',
        toolsUsed: ['basic_advisor'],
        qualityScore: 0.6
      };

      const startTime = performance.now();
      
      const reflection = await reflectionSystem.reflect(
        'consultation',
        result,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '北京',
            temperature: 25,
            humidity: 60,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date()
        }
      );

      const endTime = performance.now();
      
      expect(endTime - startTime).toBeLessThan(500); // 应该在500ms内完成
      expect(reflection).toBeDefined();
    });

    test('应该处理大量并发反思请求', async () => {
      const results = Array.from({ length: 10 }, (_, i) => ({
        stepId: `concurrent_step_${i}`,
        result: { data: `result_${i}` },
        executionTime: 100 + i * 10,
        status: 'success' as const,
        toolsUsed: [`tool_${i}`],
        qualityScore: 0.7 + i * 0.02
      }));

      const context = {
        userId: 'user_123',
        sessionId: 'session_456',
        currentChannel: 'health' as const,
        userProfile: {
          id: 'user_123',
          age: 35,
          gender: 'female' as const,
          height: 165,
          weight: 60,
          medicalHistory: [],
          allergies: [],
          currentMedications: []
        },
        medicalHistory: [],
        currentSymptoms: [],
        environmentalFactors: {
          location: '北京',
          temperature: 25,
          humidity: 60,
          airQuality: 80,
          season: '夏季'
        },
        timestamp: new Date()
      };

      const startTime = performance.now();
      
      const reflections = await Promise.all(
        results.map(result => 
          reflectionSystem.reflect('general', result, context)
        )
      );

      const endTime = performance.now();
      
      expect(reflections).toHaveLength(10);
      expect(endTime - startTime).toBeLessThan(2000); // 应该在2秒内完成所有反思
    });
  });

  describe('错误处理', () => {
    test('应该处理无效输入', async () => {
      const invalidResult = {
        stepId: '',
        result: null,
        executionTime: -1,
        status: 'unknown' as any,
        toolsUsed: [],
        qualityScore: 2.0 // 无效分数
      };

      await expect(reflectionSystem.reflect(
        'invalid',
        invalidResult,
        {} as any
      )).rejects.toThrow();
    });

    test('应该优雅处理系统错误', async () => {
      // Mock内部错误
      jest.spyOn(reflectionSystem as any, 'analyzeQuality')
        .mockRejectedValue(new Error('Internal analysis error'));

      const result: ExecutionResult = {
        stepId: 'error_test',
        result: { data: 'test' },
        executionTime: 100,
        status: 'success',
        toolsUsed: [],
        qualityScore: 0.8
      };

      const reflection = await reflectionSystem.reflect(
        'test',
        result,
        {
          userId: 'user_123',
          sessionId: 'session_456',
          currentChannel: 'health',
          userProfile: {
            id: 'user_123',
            age: 35,
            gender: 'female',
            height: 165,
            weight: 60,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [],
          environmentalFactors: {
            location: '北京',
            temperature: 25,
            humidity: 60,
            airQuality: 80,
            season: '夏季'
          },
          timestamp: new Date()
        }
      );

      // 应该返回默认的安全反思结果
      expect(reflection.qualityScore).toBeGreaterThanOrEqual(0);
      expect(reflection.shouldIterate).toBeDefined();
    });
  });
});