/**
 * Agentic AI 性能基准测试
 * 测试系统在各种负载条件下的性能表现
 */

import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { AgenticIntegration } from '../../src/core/agentic/AgenticIntegration';
import { AgenticTask } from '../../src/core/agentic/AgenticWorkflowEngine';

describe('Agentic AI Performance Tests', () => {
  let agenticSystem: AgenticIntegration;
  let performanceMetrics: {
    responseTime: number[];
    throughput: number;
    memoryUsage: number[];
    cpuUsage: number[];
    errorRate: number;
  };

  beforeEach(async () => {
    agenticSystem = new AgenticIntegration();
    await agenticSystem.initialize();
    
    performanceMetrics = {
      responseTime: [],
      throughput: 0,
      memoryUsage: [],
      cpuUsage: [],
      errorRate: 0
    };
  });

  afterEach(async () => {
    await agenticSystem.shutdown();
  });

  describe('响应时间基准测试', () => {
    test('简单咨询任务应在200ms内响应', async () => {
      const simpleTask: AgenticTask = {
        id: 'perf_simple_001',
        type: 'consultation',
        description: '简单健康咨询',
        priority: 'low',
        context: {
          userId: 'perf_user_001',
          sessionId: 'perf_session_001',
          currentChannel: 'health',
          userProfile: {
            id: 'perf_user_001',
            age: 30,
            gender: 'male',
            height: 175,
            weight: 70,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '轻微头痛',
              severity: 3,
              duration: '1小时',
              description: '工作疲劳引起'
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
        expectedOutcome: '快速健康建议'
      };

      const iterations = 10;
      const responseTimes: number[] = [];

      for (let i = 0; i < iterations; i++) {
        const startTime = performance.now();
        const result = await agenticSystem.processTask({
          ...simpleTask,
          id: `perf_simple_${i}`
        });
        const endTime = performance.now();
        
        const responseTime = endTime - startTime;
        responseTimes.push(responseTime);
        
        expect(result.success).toBe(true);
      }

      const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      const maxResponseTime = Math.max(...responseTimes);
      const minResponseTime = Math.min(...responseTimes);

      console.log(`简单咨询性能指标:
        平均响应时间: ${avgResponseTime.toFixed(2)}ms
        最大响应时间: ${maxResponseTime.toFixed(2)}ms
        最小响应时间: ${minResponseTime.toFixed(2)}ms
        目标: <200ms`);

      expect(avgResponseTime).toBeLessThan(200);
      expect(maxResponseTime).toBeLessThan(500); // 最大不超过500ms
    });

    test('复杂诊断任务应在2秒内响应', async () => {
      const complexTask: AgenticTask = {
        id: 'perf_complex_001',
        type: 'diagnosis',
        description: '复杂中医诊断',
        priority: 'high',
        context: {
          userId: 'perf_user_002',
          sessionId: 'perf_session_002',
          currentChannel: 'health',
          userProfile: {
            id: 'perf_user_002',
            age: 55,
            gender: 'female',
            height: 160,
            weight: 65,
            medicalHistory: [
              {
                condition: '高血压',
                diagnosedDate: new Date('2020-01-01'),
                status: 'ongoing',
                medications: ['氨氯地平']
              },
              {
                condition: '糖尿病',
                diagnosedDate: new Date('2018-06-15'),
                status: 'ongoing',
                medications: ['二甲双胍']
              }
            ],
            allergies: ['青霉素'],
            currentMedications: ['氨氯地平 5mg', '二甲双胍 500mg']
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '胸闷',
              severity: 7,
              duration: '1周',
              description: '活动后明显，伴有气短'
            },
            {
              name: '失眠',
              severity: 8,
              duration: '2周',
              description: '入睡困难，早醒'
            },
            {
              name: '腰酸',
              severity: 6,
              duration: '1个月',
              description: '持续性酸痛'
            }
          ],
          environmentalFactors: {
            location: '上海',
            temperature: 28,
            humidity: 75,
            airQuality: 70,
            season: '夏季'
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
        expectedOutcome: '全面的中医诊断和治疗方案'
      };

      const iterations = 5;
      const responseTimes: number[] = [];

      for (let i = 0; i < iterations; i++) {
        const startTime = performance.now();
        const result = await agenticSystem.processTask({
          ...complexTask,
          id: `perf_complex_${i}`
        });
        const endTime = performance.now();
        
        const responseTime = endTime - startTime;
        responseTimes.push(responseTime);
        
        expect(result.success).toBe(true);
        expect(result.diagnosis).toBeDefined();
        expect(result.treatmentPlan).toBeDefined();
      }

      const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      const maxResponseTime = Math.max(...responseTimes);

      console.log(`复杂诊断性能指标:
        平均响应时间: ${avgResponseTime.toFixed(2)}ms
        最大响应时间: ${maxResponseTime.toFixed(2)}ms
        目标: <2000ms`);

      expect(avgResponseTime).toBeLessThan(2000);
      expect(maxResponseTime).toBeLessThan(5000); // 最大不超过5秒
    });
  });

  describe('吞吐量测试', () => {
    test('应支持每秒处理50个并发请求', async () => {
      const concurrentRequests = 50;
      const testDuration = 1000; // 1秒

      const createTask = (id: number): AgenticTask => ({
        id: `throughput_task_${id}`,
        type: 'consultation',
        description: `吞吐量测试任务 ${id}`,
        priority: 'medium',
        context: {
          userId: `throughput_user_${id}`,
          sessionId: `throughput_session_${id}`,
          currentChannel: 'health',
          userProfile: {
            id: `throughput_user_${id}`,
            age: 25 + (id % 50),
            gender: id % 2 === 0 ? 'male' : 'female',
            height: 160 + (id % 30),
            weight: 50 + (id % 40),
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '疲劳',
              severity: 3 + (id % 5),
              duration: '1天',
              description: '工作疲劳'
            }
          ],
          environmentalFactors: {
            location: '北京',
            temperature: 20 + (id % 15),
            humidity: 50 + (id % 30),
            airQuality: 70 + (id % 20),
            season: '春季'
          },
          timestamp: new Date()
        },
        requirements: [],
        expectedOutcome: '快速健康建议'
      });

      const startTime = performance.now();
      
      const tasks = Array.from({ length: concurrentRequests }, (_, i) => createTask(i));
      const results = await Promise.all(
        tasks.map(task => agenticSystem.processTask(task))
      );

      const endTime = performance.now();
      const actualDuration = endTime - startTime;
      const throughput = (concurrentRequests / actualDuration) * 1000; // 每秒处理数

      console.log(`吞吐量测试结果:
        并发请求数: ${concurrentRequests}
        实际耗时: ${actualDuration.toFixed(2)}ms
        吞吐量: ${throughput.toFixed(2)} 请求/秒
        成功率: ${(results.filter(r => r.success).length / concurrentRequests * 100).toFixed(2)}%
        目标: ≥50 请求/秒`);

      expect(results.filter(r => r.success).length).toBe(concurrentRequests);
      expect(throughput).toBeGreaterThan(50);
    });

    test('应在高负载下保持稳定性', async () => {
      const loadLevels = [10, 25, 50, 75, 100];
      const results: Array<{
        load: number;
        throughput: number;
        avgResponseTime: number;
        successRate: number;
      }> = [];

      for (const load of loadLevels) {
        const tasks = Array.from({ length: load }, (_, i) => ({
          id: `load_test_${load}_${i}`,
          type: 'consultation' as const,
          description: `负载测试 ${load}/${i}`,
          priority: 'medium' as const,
          context: {
            userId: `load_user_${load}_${i}`,
            sessionId: `load_session_${load}_${i}`,
            currentChannel: 'health' as const,
            userProfile: {
              id: `load_user_${load}_${i}`,
              age: 30,
              gender: 'male' as const,
              height: 175,
              weight: 70,
              medicalHistory: [],
              allergies: [],
              currentMedications: []
            },
            medicalHistory: [],
            currentSymptoms: [
              {
                name: '头痛',
                severity: 5,
                duration: '2小时',
                description: '轻微头痛'
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
          expectedOutcome: '健康建议'
        }));

        const startTime = performance.now();
        const taskResults = await Promise.all(
          tasks.map(task => agenticSystem.processTask(task))
        );
        const endTime = performance.now();

        const duration = endTime - startTime;
        const throughput = (load / duration) * 1000;
        const avgResponseTime = duration / load;
        const successRate = taskResults.filter(r => r.success).length / load;

        results.push({
          load,
          throughput,
          avgResponseTime,
          successRate
        });

        console.log(`负载 ${load}: 吞吐量=${throughput.toFixed(2)}, 响应时间=${avgResponseTime.toFixed(2)}ms, 成功率=${(successRate * 100).toFixed(2)}%`);
      }

      // 验证系统在不同负载下的表现
      results.forEach(result => {
        expect(result.successRate).toBeGreaterThan(0.95); // 95%以上成功率
        expect(result.avgResponseTime).toBeLessThan(1000); // 平均响应时间小于1秒
      });

      // 验证吞吐量随负载的变化趋势
      const throughputTrend = results.map(r => r.throughput);
      expect(Math.max(...throughputTrend)).toBeGreaterThan(50); // 峰值吞吐量大于50
    });
  });

  describe('资源使用测试', () => {
    test('应控制内存使用在合理范围内', async () => {
      const initialMemory = process.memoryUsage();
      const memorySnapshots: NodeJS.MemoryUsage[] = [initialMemory];

      // 执行大量任务
      const taskCount = 100;
      const tasks = Array.from({ length: taskCount }, (_, i) => ({
        id: `memory_test_${i}`,
        type: 'consultation' as const,
        description: `内存测试任务 ${i}`,
        priority: 'medium' as const,
        context: {
          userId: `memory_user_${i}`,
          sessionId: `memory_session_${i}`,
          currentChannel: 'health' as const,
          userProfile: {
            id: `memory_user_${i}`,
            age: 30,
            gender: 'male' as const,
            height: 175,
            weight: 70,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '疲劳',
              severity: 4,
              duration: '1天',
              description: '轻微疲劳'
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
        expectedOutcome: '健康建议'
      }));

      // 分批处理任务，监控内存使用
      const batchSize = 10;
      for (let i = 0; i < taskCount; i += batchSize) {
        const batch = tasks.slice(i, i + batchSize);
        await Promise.all(batch.map(task => agenticSystem.processTask(task)));
        
        // 记录内存使用
        const currentMemory = process.memoryUsage();
        memorySnapshots.push(currentMemory);
        
        // 强制垃圾回收（如果可用）
        if (global.gc) {
          global.gc();
        }
      }

      const finalMemory = process.memoryUsage();
      const memoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;
      const memoryIncreasePerTask = memoryIncrease / taskCount;

      console.log(`内存使用测试结果:
        初始内存: ${(initialMemory.heapUsed / 1024 / 1024).toFixed(2)}MB
        最终内存: ${(finalMemory.heapUsed / 1024 / 1024).toFixed(2)}MB
        内存增长: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB
        每任务内存: ${(memoryIncreasePerTask / 1024).toFixed(2)}KB`);

      // 验证内存使用合理性
      expect(memoryIncreasePerTask).toBeLessThan(100 * 1024); // 每个任务内存增长小于100KB
      expect(finalMemory.heapUsed).toBeLessThan(500 * 1024 * 1024); // 总内存使用小于500MB
    });

    test('应及时释放不再使用的资源', async () => {
      const resourceTask: AgenticTask = {
        id: 'resource_cleanup_test',
        type: 'diagnosis',
        description: '资源清理测试',
        priority: 'high',
        context: {
          userId: 'resource_user',
          sessionId: 'resource_session',
          currentChannel: 'health',
          userProfile: {
            id: 'resource_user',
            age: 40,
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
              name: '复杂症状',
              severity: 8,
              duration: '1周',
              description: '需要大量资源分析的复杂症状'
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
            type: 'collaboration',
            specification: { agents: ['xiaoai', 'xiaoke', 'laoke', 'soer'] },
            mandatory: true
          },
          {
            type: 'tool',
            specification: { toolId: 'comprehensive_analyzer' },
            mandatory: true
          }
        ],
        expectedOutcome: '全面诊断分析'
      };

      const beforeMemory = process.memoryUsage();
      
      // 执行资源密集型任务
      const result = await agenticSystem.processTask(resourceTask);
      expect(result.success).toBe(true);

      // 等待资源清理
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 强制垃圾回收
      if (global.gc) {
        global.gc();
      }

      const afterMemory = process.memoryUsage();
      const memoryDifference = afterMemory.heapUsed - beforeMemory.heapUsed;

      console.log(`资源清理测试结果:
        任务前内存: ${(beforeMemory.heapUsed / 1024 / 1024).toFixed(2)}MB
        任务后内存: ${(afterMemory.heapUsed / 1024 / 1024).toFixed(2)}MB
        内存差异: ${(memoryDifference / 1024 / 1024).toFixed(2)}MB`);

      // 验证资源得到适当清理
      expect(memoryDifference).toBeLessThan(50 * 1024 * 1024); // 内存增长小于50MB
    });
  });

  describe('可扩展性测试', () => {
    test('应支持智能体数量的动态扩展', async () => {
      const scalabilityTask: AgenticTask = {
        id: 'scalability_test',
        type: 'comprehensive_analysis',
        description: '可扩展性测试',
        priority: 'high',
        context: {
          userId: 'scalability_user',
          sessionId: 'scalability_session',
          currentChannel: 'health',
          userProfile: {
            id: 'scalability_user',
            age: 35,
            gender: 'male',
            height: 175,
            weight: 75,
            medicalHistory: [],
            allergies: [],
            currentMedications: []
          },
          medicalHistory: [],
          currentSymptoms: [
            {
              name: '综合症状',
              severity: 7,
              duration: '2周',
              description: '需要多智能体协作分析'
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
            type: 'collaboration',
            specification: { 
              agents: ['xiaoai', 'xiaoke', 'laoke', 'soer'],
              scalable: true,
              maxAgents: 8
            },
            mandatory: true
          }
        ],
        expectedOutcome: '可扩展的协作分析'
      };

      // 测试不同智能体数量的性能
      const agentCounts = [2, 4, 6, 8];
      const scalabilityResults: Array<{
        agentCount: number;
        responseTime: number;
        qualityScore: number;
        resourceUsage: number;
      }> = [];

      for (const agentCount of agentCounts) {
        const testTask = {
          ...scalabilityTask,
          id: `scalability_test_${agentCount}`,
          requirements: [
            {
              type: 'collaboration' as const,
              specification: { 
                agents: ['xiaoai', 'xiaoke', 'laoke', 'soer'].slice(0, agentCount),
                scalable: true,
                maxAgents: agentCount
              },
              mandatory: true
            }
          ]
        };

        const beforeMemory = process.memoryUsage();
        const startTime = performance.now();
        
        const result = await agenticSystem.processTask(testTask);
        
        const endTime = performance.now();
        const afterMemory = process.memoryUsage();

        const responseTime = endTime - startTime;
        const resourceUsage = afterMemory.heapUsed - beforeMemory.heapUsed;

        scalabilityResults.push({
          agentCount,
          responseTime,
          qualityScore: result.qualityScore || 0,
          resourceUsage
        });

        expect(result.success).toBe(true);
      }

      // 分析可扩展性趋势
      console.log('可扩展性测试结果:');
      scalabilityResults.forEach(result => {
        console.log(`智能体数量: ${result.agentCount}, 响应时间: ${result.responseTime.toFixed(2)}ms, 质量分数: ${result.qualityScore.toFixed(2)}, 资源使用: ${(result.resourceUsage / 1024 / 1024).toFixed(2)}MB`);
      });

      // 验证可扩展性特征
      const responseTimeGrowth = scalabilityResults[scalabilityResults.length - 1].responseTime / scalabilityResults[0].responseTime;
      const qualityImprovement = scalabilityResults[scalabilityResults.length - 1].qualityScore / scalabilityResults[0].qualityScore;

      expect(responseTimeGrowth).toBeLessThan(3); // 响应时间增长不超过3倍
      expect(qualityImprovement).toBeGreaterThan(1.1); // 质量至少提升10%
    });
  });

  describe('性能回归测试', () => {
    test('应保持与基准版本相当的性能', async () => {
      // 基准性能指标（模拟历史数据）
      const baselineMetrics = {
        simpleTaskResponseTime: 150, // ms
        complexTaskResponseTime: 1800, // ms
        throughput: 60, // requests/sec
        memoryUsagePerTask: 80 * 1024, // bytes
        successRate: 0.98
      };

      // 执行性能测试
      const performanceTest = async () => {
        const simpleTasks = Array.from({ length: 10 }, (_, i) => ({
          id: `regression_simple_${i}`,
          type: 'consultation' as const,
          description: '回归测试简单任务',
          priority: 'low' as const,
          context: {
            userId: `regression_user_${i}`,
            sessionId: `regression_session_${i}`,
            currentChannel: 'health' as const,
            userProfile: {
              id: `regression_user_${i}`,
              age: 30,
              gender: 'male' as const,
              height: 175,
              weight: 70,
              medicalHistory: [],
              allergies: [],
              currentMedications: []
            },
            medicalHistory: [],
            currentSymptoms: [
              {
                name: '轻微不适',
                severity: 3,
                duration: '1小时',
                description: '轻微不适'
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
          expectedOutcome: '快速建议'
        }));

        // 测试简单任务性能
        const simpleTaskTimes: number[] = [];
        for (const task of simpleTasks) {
          const startTime = performance.now();
          const result = await agenticSystem.processTask(task);
          const endTime = performance.now();
          
          if (result.success) {
            simpleTaskTimes.push(endTime - startTime);
          }
        }

        const avgSimpleTaskTime = simpleTaskTimes.reduce((a, b) => a + b, 0) / simpleTaskTimes.length;

        // 测试吞吐量
        const throughputTasks = Array.from({ length: 50 }, (_, i) => ({
          ...simpleTasks[0],
          id: `throughput_regression_${i}`
        }));

        const throughputStartTime = performance.now();
        const throughputResults = await Promise.all(
          throughputTasks.map(task => agenticSystem.processTask(task))
        );
        const throughputEndTime = performance.now();

        const throughputDuration = throughputEndTime - throughputStartTime;
        const actualThroughput = (throughputTasks.length / throughputDuration) * 1000;
        const successRate = throughputResults.filter(r => r.success).length / throughputTasks.length;

        return {
          avgSimpleTaskTime,
          actualThroughput,
          successRate
        };
      };

      const currentMetrics = await performanceTest();

      console.log(`性能回归测试结果:
        简单任务响应时间: ${currentMetrics.avgSimpleTaskTime.toFixed(2)}ms (基准: ${baselineMetrics.simpleTaskResponseTime}ms)
        吞吐量: ${currentMetrics.actualThroughput.toFixed(2)} req/s (基准: ${baselineMetrics.throughput} req/s)
        成功率: ${(currentMetrics.successRate * 100).toFixed(2)}% (基准: ${(baselineMetrics.successRate * 100).toFixed(2)}%)`);

      // 验证性能不低于基准
      expect(currentMetrics.avgSimpleTaskTime).toBeLessThan(baselineMetrics.simpleTaskResponseTime * 1.2); // 允许20%的性能波动
      expect(currentMetrics.actualThroughput).toBeGreaterThan(baselineMetrics.throughput * 0.8); // 吞吐量不低于基准的80%
      expect(currentMetrics.successRate).toBeGreaterThan(baselineMetrics.successRate * 0.95); // 成功率不低于基准的95%
    });
  });
});