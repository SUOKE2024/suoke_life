import { AgentCoordinator } from './AgentCoordinator';
import { AgentManager } from './AgentManager';
import { AgentFactory } from './factory/AgentFactory';
import {
  AgentSystemUtils,
  COLLABORATION_STRATEGIES,
  createAgent,
  executeAgentTask,
  initializeAgentSystem,
} from './index';
import { AgentType } from './types';

/**
 * 测试结果接口
 */
interface TestResult {
  testName: string;
  success: boolean;
  duration: number;
  error?: string;
  data?: any;
}

/**
 * 智能体系统测试类
 */
export class AgentSystemTester {
  private coordinator: AgentCoordinator;
  private manager: AgentManager;
  private factory: AgentFactory;
  private testResults: TestResult[] = [];

  constructor() {
    this.coordinator = new AgentCoordinator();
    this.manager = new AgentManager();
    this.factory = AgentFactory.getInstance();
  }

  /**
   * 运行所有测试
   */
  async runAllTests(): Promise<TestResult[]> {
    console.log('🚀 开始智能体系统测试...\n');
    this.testResults = [];

    // 基础功能测试
    await this.testBasicFunctionality();
    // 智能体创建测试
    await this.testAgentCreation();
    // 协调器测试
    await this.testCoordinator();
    // 管理器测试
    await this.testManager();
    // 工厂模式测试
    await this.testFactory();
    // 协作测试
    await this.testCollaboration();
    // 性能测试
    await this.testPerformance();
    // 错误处理测试
    await this.testErrorHandling();

    // 输出测试结果
    this.printTestResults();
    return this.testResults;
  }

  /**
   * 基础功能测试
   */
  private async testBasicFunctionality(): Promise<void> {
    console.log('📋 基础功能测试');

    // 测试类型定义
    await this.runTest('类型定义测试', async () => {
      const agentTypes = Object.values(AgentType);
      if (agentTypes.length !== 4) {
        throw new Error(`期望4个智能体类型，实际${agentTypes.length}个`);
      }
      return { agentTypes };
    });

    // 测试工具函数
    await this.runTest('工具函数测试', async () => {
      const xiaoaiCapabilities = AgentSystemUtils.getAgentCapabilities(
        AgentType.XIAOAI
      );
      const xiaokeRole = AgentSystemUtils.getAgentRole(AgentType.XIAOKE);
      const chatAgent = AgentSystemUtils.getAgentByChannel('chat');

      if (xiaoaiCapabilities.length === 0) {
        throw new Error('小艾能力列表为空');
      }
      if (!xiaokeRole || xiaokeRole.name !== '小克') {
        throw new Error('小克角色信息错误');
      }
      if (chatAgent !== AgentType.XIAOAI) {
        throw new Error('聊天频道应该对应小艾');
      }

      return { xiaoaiCapabilities, xiaokeRole, chatAgent };
    });

    // 测试上下文创建
    await this.runTest('上下文创建测试', async () => {
      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'suoke'
      );

      if (!AgentSystemUtils.validateContext(context)) {
        throw new Error('上下文验证失败');
      }
      if (context.currentChannel !== 'suoke') {
        throw new Error('频道设置错误');
      }

      return { context };
    });
  }

  /**
   * 智能体创建测试
   */
  private async testAgentCreation(): Promise<void> {
    console.log('🤖 智能体创建测试');

    // 测试单个智能体创建
    for (const agentType of Object.values(AgentType)) {
      await this.runTest(`创建${agentType}智能体`, async () => {
        const agent = await createAgent(agentType);
        await agent.initialize();
        const healthStatus = await agent.getHealthStatus();

        if (!healthStatus) {
          throw new Error('健康状态获取失败');
        }

        await agent.shutdown();
        return { agentType, healthStatus };
      });
    }

    // 测试批量创建
    await this.runTest('批量创建智能体', async () => {
      const agents = await Promise.all([
        createAgent(AgentType.XIAOAI),
        createAgent(AgentType.XIAOKE),
        createAgent(AgentType.LAOKE),
        createAgent(AgentType.SOER),
      ]);

      for (const agent of agents) {
        await agent.initialize();
      }

      const statuses = await Promise.all(
        agents.map((agent) => agent.getHealthStatus())
      );

      for (const agent of agents) {
        await agent.shutdown();
      }

      return { agentCount: agents.length, statuses };
    });
  }

  /**
   * 协调器测试
   */
  private async testCoordinator(): Promise<void> {
    console.log('🎯 协调器测试');

    await this.runTest('协调器初始化', async () => {
      await this.coordinator.initialize();
      const statuses = await this.coordinator.getAllAgentStatus();

      if (statuses.size !== 4) {
        throw new Error(`期望4个智能体，实际${statuses.size}个`);
      }

      return { agentCount: statuses.size };
    });

    await this.runTest('单智能体任务处理', async () => {
      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'chat'
      );
      const response = await this.coordinator.coordinateTask('你好', context);

      if (!response.success) {
        throw new Error('任务处理失败');
      }

      return { response: response.response };
    });

    await this.runTest('多智能体协作任务', async () => {
      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'suoke'
      );
      const response = await this.coordinator.coordinateTask(
        '我需要健康建议和产品推荐',
        context
      );

      if (!response.success) {
        throw new Error('协作任务失败');
      }

      return { response: response.response };
    });
  }

  /**
   * 管理器测试
   */
  private async testManager(): Promise<void> {
    console.log('📊 管理器测试');

    await this.runTest('管理器初始化', async () => {
      await this.manager.initialize();
      const metrics = await this.manager.getSystemMetrics();

      if (!metrics) {
        throw new Error('系统指标获取失败');
      }

      return { metrics };
    });

    await this.runTest('智能体注册', async () => {
      const agent = await createAgent(AgentType.XIAOAI);
      await this.manager.registerAgent(agent);

      const registeredAgents = await this.manager.getRegisteredAgents();

      if (registeredAgents.length === 0) {
        throw new Error('智能体注册失败');
      }

      await this.manager.unregisterAgent(AgentType.XIAOAI);
      return { registeredCount: registeredAgents.length };
    });
  }

  /**
   * 工厂模式测试
   */
  private async testFactory(): Promise<void> {
    console.log('🏭 工厂模式测试');

    await this.runTest('工厂创建智能体', async () => {
      const agents = [];
      for (const agentType of Object.values(AgentType)) {
        const agent = this.factory.createAgent(agentType);
        agents.push(agent);
      }

      if (agents.length !== 4) {
        throw new Error(`期望创建4个智能体，实际${agents.length}个`);
      }

      return { createdCount: agents.length };
    });
  }

  /**
   * 协作测试
   */
  private async testCollaboration(): Promise<void> {
    console.log('🤝 协作测试');

    await this.runTest('协作策略测试', async () => {
      const strategies = Object.keys(COLLABORATION_STRATEGIES);

      if (strategies.length === 0) {
        throw new Error('协作策略为空');
      }

      return { strategies };
    });
  }

  /**
   * 性能测试
   */
  private async testPerformance(): Promise<void> {
    console.log('⚡ 性能测试');

    await this.runTest('响应时间测试', async () => {
      const startTime = Date.now();
      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'chat'
      );

      await this.coordinator.coordinateTask('性能测试', context);

      const responseTime = Date.now() - startTime;

      if (responseTime > 5000) {
        throw new Error(`响应时间过长: ${responseTime}ms`);
      }

      return { responseTime };
    });
  }

  /**
   * 错误处理测试
   */
  private async testErrorHandling(): Promise<void> {
    console.log('🚨 错误处理测试');

    await this.runTest('无效输入处理', async () => {
      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'chat'
      );

      const response = await this.coordinator.coordinateTask('', context);

      if (response.success) {
        throw new Error('应该处理空输入错误');
      }

      return { handled: true };
    });
  }

  /**
   * 运行单个测试
   */
  private async runTest(
    testName: string,
    testFunction: () => Promise<any>
  ): Promise<void> {
    const startTime = Date.now();

    try {
      const data = await testFunction();
      const duration = Date.now() - startTime;

      this.testResults.push({
        testName,
        success: true,
        duration,
        data,
      });

      console.log(`  ✅ ${testName} (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;

      this.testResults.push({
        testName,
        success: false,
        duration,
        error: error instanceof Error ? error.message : String(error),
      });

      console.log(`  ❌ ${testName} (${duration}ms): ${error}`);
    }
  }

  /**
   * 打印测试结果
   */
  private printTestResults(): void {
    console.log('\n📊 测试结果汇总');
    console.log('='.repeat(50));

    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter((r) => r.success).length;
    const failedTests = totalTests - passedTests;
    const totalDuration = this.testResults.reduce(
      (sum, r) => sum + r.duration,
      0
    );

    console.log(`总测试数: ${totalTests}`);
    console.log(`通过: ${passedTests}`);
    console.log(`失败: ${failedTests}`);
    console.log(`总耗时: ${totalDuration}ms`);
    console.log(`成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

    if (failedTests > 0) {
      console.log('\n❌ 失败的测试:');
      this.testResults
        .filter((r) => !r.success)
        .forEach((r) => {
          console.log(`  - ${r.testName}: ${r.error}`);
        });
    }

    console.log('\n' + '='.repeat(50));
  }
}

/**
 * 快速测试函数
 */
export async function quickTest(): Promise<void> {
  console.log('🚀 运行快速测试...\n');

  try {
    // 初始化系统
    await initializeAgentSystem();

    // 创建测试智能体
    const agent = await createAgent(AgentType.XIAOAI);
    await agent.initialize();

    // 执行简单任务
    const context = AgentSystemUtils.createDefaultContext('test_user', 'chat');
    const task = await executeAgentTask(agent, '你好', context);

    console.log('✅ 快速测试通过');
    console.log(`响应: ${task.response}`);

    await agent.shutdown();
  } catch (error) {
    console.log('❌ 快速测试失败:', error);
  }
}

/**
 * 运行完整测试套件
 */
export async function runFullTestSuite(): Promise<TestResult[]> {
  const tester = new AgentSystemTester();
  return await tester.runAllTests();
}
