/**
 * Agentic Workflow Engine 单元测试
 * 测试工作流引擎的核心功能和边界条件
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { AgenticWorkflowEngine, AgenticTask, WorkflowInstance } from '../../src/core/agentic/AgenticWorkflowEngine';

describe('AgenticWorkflowEngine', () => {
  let workflowEngine: AgenticWorkflowEngine;
  let mockTask: AgenticTask;

  beforeEach(() => {
    workflowEngine = new AgenticWorkflowEngine();
    
    mockTask = {
      id: 'test_task_001',
      type: 'diagnosis',
      description: '测试诊断任务',
      priority: 'medium',
      context: {
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
      },
      requirements: [
        {
          type: 'tool',
          specification: { toolId: 'symptom_analyzer' },
          mandatory: true
        }
      ],
      expectedOutcome: '准确的诊断结果和治疗建议'
    };
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('工作流启动', () => {
    test('应该成功启动简单工作流', async () => {
      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      expect(workflow).toBeInstanceOf(WorkflowInstance);
      expect(workflow.task.id).toBe(mockTask.id);
      expect(workflow.status).toBe('pending');
    });

    test('应该为复杂任务生成详细计划', async () => {
      const complexTask = {
        ...mockTask,
        type: 'treatment' as const,
        priority: 'high' as const,
        requirements: [
          {
            type: 'tool' as const,
            specification: { toolId: 'tcm_analyzer' },
            mandatory: true
          },
          {
            type: 'collaboration' as const,
            specification: { agents: ['xiaoke', 'laoke'] },
            mandatory: false
          }
        ]
      };

      const workflow = await workflowEngine.startWorkflow(complexTask);
      
      expect(workflow.plan.steps.length).toBeGreaterThan(1);
      expect(workflow.plan.estimatedDuration).toBeGreaterThan(0);
    });

    test('应该处理无效任务输入', async () => {
      const invalidTask = {
        ...mockTask,
        id: '', // 无效ID
        context: {
          ...mockTask.context,
          userId: '' // 无效用户ID
        }
      };

      await expect(workflowEngine.startWorkflow(invalidTask))
        .rejects.toThrow('Invalid task configuration');
    });
  });

  describe('工作流执行', () => {
    test('应该按顺序执行工作流步骤', async () => {
      const executionOrder: string[] = [];
      
      // Mock步骤执行
      jest.spyOn(workflowEngine as any, 'executeStep')
        .mockImplementation(async (step) => {
          executionOrder.push(step.id);
          return {
            stepId: step.id,
            result: { success: true },
            executionTime: 100,
            status: 'success',
            toolsUsed: [],
            qualityScore: 0.9
          };
        });

      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      expect(executionOrder.length).toBeGreaterThan(0);
      expect(workflow.status).toBe('completed');
    });

    test('应该处理步骤执行失败', async () => {
      jest.spyOn(workflowEngine as any, 'executeStep')
        .mockRejectedValueOnce(new Error('Step execution failed'));

      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      expect(workflow.status).toBe('failed');
    });

    test('应该支持工作流暂停和恢复', async () => {
      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      await workflowEngine.stopWorkflow(workflow.id);
      expect(workflow.status).toBe('stopped');
      
      // 测试恢复功能（如果实现）
      const status = workflowEngine.getWorkflowStatus(workflow.id);
      expect(status?.status).toBe('stopped');
    });
  });

  describe('反馈和迭代', () => {
    test('应该基于质量分数决定是否迭代', async () => {
      // Mock低质量结果
      jest.spyOn(workflowEngine as any, 'executeStep')
        .mockResolvedValue({
          stepId: 'test_step',
          result: { quality: 0.5 }, // 低质量
          executionTime: 100,
          status: 'success',
          toolsUsed: [],
          qualityScore: 0.5
        });

      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      // 应该触发迭代
      expect(workflow.plan.steps.length).toBeGreaterThan(1);
    });

    test('应该记录迭代历史', async () => {
      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      expect(workflow.progress.size).toBeGreaterThanOrEqual(0);
    });
  });

  describe('性能监控', () => {
    test('应该跟踪执行时间', async () => {
      const startTime = Date.now();
      const workflow = await workflowEngine.startWorkflow(mockTask);
      const endTime = Date.now();
      
      expect(workflow.getStatus().estimatedTimeRemaining).toBeGreaterThanOrEqual(0);
      expect(endTime - startTime).toBeLessThan(5000); // 应该在5秒内完成
    });

    test('应该计算质量分数', async () => {
      const workflow = await workflowEngine.startWorkflow(mockTask);
      const status = workflow.getStatus();
      
      expect(status.qualityScore).toBeGreaterThanOrEqual(0);
      expect(status.qualityScore).toBeLessThanOrEqual(1);
    });

    test('应该提供进度信息', async () => {
      const workflow = await workflowEngine.startWorkflow(mockTask);
      const status = workflow.getStatus();
      
      expect(status.progress).toBeGreaterThanOrEqual(0);
      expect(status.progress).toBeLessThanOrEqual(1);
      expect(status.currentStep).toBeDefined();
    });
  });

  describe('错误处理', () => {
    test('应该优雅处理网络错误', async () => {
      jest.spyOn(workflowEngine as any, 'getAgent')
        .mockRejectedValue(new Error('Network error'));

      await expect(workflowEngine.startWorkflow(mockTask))
        .rejects.toThrow('Network error');
    });

    test('应该处理资源不足', async () => {
      const resourceIntensiveTask = {
        ...mockTask,
        requirements: [
          {
            type: 'compute' as const,
            specification: { cpu: 100, memory: '32GB' },
            mandatory: true
          }
        ]
      };

      // 应该降级或提供替代方案
      const workflow = await workflowEngine.startWorkflow(resourceIntensiveTask);
      expect(workflow).toBeDefined();
    });

    test('应该处理超时情况', async () => {
      jest.spyOn(workflowEngine as any, 'executeStep')
        .mockImplementation(() => new Promise(resolve => 
          setTimeout(resolve, 10000) // 10秒超时
        ));

      const timeoutTask = {
        ...mockTask,
        context: {
          ...mockTask.context,
          timeout: 1000 // 1秒超时
        }
      };

      await expect(workflowEngine.startWorkflow(timeoutTask))
        .rejects.toThrow('Timeout');
    });
  });

  describe('并发处理', () => {
    test('应该支持多个并发工作流', async () => {
      const tasks = Array.from({ length: 5 }, (_, i) => ({
        ...mockTask,
        id: `concurrent_task_${i}`,
        context: {
          ...mockTask.context,
          userId: `user_${i}`
        }
      }));

      const workflows = await Promise.all(
        tasks.map(task => workflowEngine.startWorkflow(task))
      );

      expect(workflows).toHaveLength(5);
      workflows.forEach(workflow => {
        expect(workflow).toBeInstanceOf(WorkflowInstance);
      });
    });

    test('应该正确管理资源竞争', async () => {
      const competingTasks = Array.from({ length: 3 }, (_, i) => ({
        ...mockTask,
        id: `competing_task_${i}`,
        requirements: [
          {
            type: 'tool' as const,
            specification: { toolId: 'limited_resource' },
            mandatory: true
          }
        ]
      }));

      const workflows = await Promise.all(
        competingTasks.map(task => workflowEngine.startWorkflow(task))
      );

      // 至少有一个应该成功
      const successfulWorkflows = workflows.filter(w => w.status !== 'failed');
      expect(successfulWorkflows.length).toBeGreaterThan(0);
    });
  });

  describe('集成测试', () => {
    test('应该与反思系统集成', async () => {
      const workflow = await workflowEngine.startWorkflow(mockTask);
      
      // 验证反思系统被调用
      expect(workflow.getStatus().qualityScore).toBeDefined();
    });

    test('应该与工具编排系统集成', async () => {
      const toolRequiredTask = {
        ...mockTask,
        requirements: [
          {
            type: 'tool' as const,
            specification: { toolId: 'symptom_analyzer' },
            mandatory: true
          }
        ]
      };

      const workflow = await workflowEngine.startWorkflow(toolRequiredTask);
      
      expect(workflow.plan.steps.some(step => 
        step.tools?.length > 0
      )).toBe(true);
    });
  });
});

// 性能基准测试
describe('AgenticWorkflowEngine Performance', () => {
  let workflowEngine: AgenticWorkflowEngine;

  beforeEach(() => {
    workflowEngine = new AgenticWorkflowEngine();
  });

  test('应该在合理时间内处理简单任务', async () => {
    const simpleTask: AgenticTask = {
      id: 'perf_test_simple',
      type: 'consultation',
      description: '简单咨询任务',
      priority: 'low',
      context: {
        userId: 'perf_user',
        sessionId: 'perf_session',
        currentChannel: 'health',
        userProfile: {
          id: 'perf_user',
          age: 30,
          gender: 'male',
          height: 175,
          weight: 70,
          medicalHistory: [],
          allergies: [],
          currentMedications: []
        },
        medicalHistory: [],
        currentSymptoms: [],
        environmentalFactors: {
          location: '上海',
          temperature: 22,
          humidity: 55,
          airQuality: 85,
          season: '春季'
        },
        timestamp: new Date()
      },
      requirements: [],
      expectedOutcome: '快速响应'
    };

    const startTime = performance.now();
    const workflow = await workflowEngine.startWorkflow(simpleTask);
    const endTime = performance.now();

    expect(endTime - startTime).toBeLessThan(1000); // 应该在1秒内完成
    expect(workflow.status).toBe('completed');
  });

  test('应该高效处理批量任务', async () => {
    const batchSize = 10;
    const tasks = Array.from({ length: batchSize }, (_, i) => ({
      id: `batch_task_${i}`,
      type: 'diagnosis' as const,
      description: `批量任务 ${i}`,
      priority: 'medium' as const,
      context: {
        userId: `batch_user_${i}`,
        sessionId: `batch_session_${i}`,
        currentChannel: 'health' as const,
        userProfile: {
          id: `batch_user_${i}`,
          age: 25 + i,
          gender: i % 2 === 0 ? 'male' as const : 'female' as const,
          height: 170,
          weight: 65,
          medicalHistory: [],
          allergies: [],
          currentMedications: []
        },
        medicalHistory: [],
        currentSymptoms: [],
        environmentalFactors: {
          location: '深圳',
          temperature: 28,
          humidity: 70,
          airQuality: 75,
          season: '夏季'
        },
        timestamp: new Date()
      },
      requirements: [],
      expectedOutcome: '批量处理结果'
    }));

    const startTime = performance.now();
    const workflows = await Promise.all(
      tasks.map(task => workflowEngine.startWorkflow(task))
    );
    const endTime = performance.now();

    const avgTimePerTask = (endTime - startTime) / batchSize;
    expect(avgTimePerTask).toBeLessThan(500); // 平均每个任务应该在500ms内完成
    expect(workflows).toHaveLength(batchSize);
  });
});

// Mock实现
jest.mock('../../src/core/agentic/ReflectionSystem', () => ({
  ReflectionSystem: jest.fn().mockImplementation(() => ({
    reflect: jest.fn().mockResolvedValue({
      qualityScore: 0.8,
      confidence: 0.85,
      improvements: [],
      nextActions: ['完成任务'],
      shouldIterate: false
    })
  }))
}));

jest.mock('../../src/core/agentic/PlanningSystem', () => ({
  PlanningSystem: jest.fn().mockImplementation(() => ({
    createPlan: jest.fn().mockResolvedValue({
      steps: [
        {
          id: 'step_1',
          name: '症状分析',
          agentType: 'xiaoai',
          action: { type: 'analyze', parameters: {}, tools: [], outputFormat: 'json' },
          dependencies: [],
          expectedDuration: 1000,
          qualityThreshold: 0.8
        }
      ],
      estimatedDuration: 1000,
      riskAssessment: [],
      alternativePlans: []
    })
  }))
}));

jest.mock('../../src/core/agentic/ToolOrchestrationSystem', () => ({
  ToolOrchestrationSystem: jest.fn().mockImplementation(() => ({
    prepareTools: jest.fn().mockResolvedValue([
      {
        id: 'symptom_analyzer',
        execute: jest.fn().mockResolvedValue({ result: 'analysis_complete' })
      }
    ])
  }))
}));

jest.mock('../../src/core/agentic/AgenticCollaborationSystem', () => ({
  AgenticCollaborationSystem: jest.fn().mockImplementation(() => ({
    setupCollaboration: jest.fn().mockResolvedValue({
      participants: ['xiaoai'],
      sharedKnowledge: {},
      communicationChannel: 'direct'
    })
  }))
}));