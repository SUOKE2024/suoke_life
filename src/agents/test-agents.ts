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


    // 测试类型定义

      const agentTypes = Object.values(AgentType);
      if (agentTypes.length !== 4) {

      }
      return { agentTypes };
    });

    // 测试工具函数

      const xiaoaiCapabilities = AgentSystemUtils.getAgentCapabilities(
        AgentType.XIAOAI
      );
      const xiaokeRole = AgentSystemUtils.getAgentRole(AgentType.XIAOKE);
      const chatAgent = AgentSystemUtils.getAgentByChannel('chat');

      if (xiaoaiCapabilities.length === 0) {

      }


      }
      if (chatAgent !== AgentType.XIAOAI) {

      }

      return { xiaoaiCapabilities, xiaokeRole, chatAgent };
    });

    // 测试上下文创建

      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'suoke'
      );

      if (!AgentSystemUtils.validateContext(context)) {

      }
      if (context.currentChannel !== 'suoke') {

      }

      return { context };
    });
  }

  /**
   * 智能体创建测试
   */
  private async testAgentCreation(): Promise<void> {


    // 测试单个智能体创建
    for (const agentType of Object.values(AgentType)) {

        const agent = await createAgent(agentType);
        await agent.initialize();
        const healthStatus = await agent.getHealthStatus();

        if (!healthStatus) {

        }

        await agent.shutdown();
        return { agentType, healthStatus };
      });
    }

    // 测试批量创建

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

      return { agentCount: agents.length, statuses ;};
    });
  }

  /**
   * 协调器测试
   */
  private async testCoordinator(): Promise<void> {



      await this.coordinator.initialize();
      const statuses = await this.coordinator.getAllAgentStatus();

      if (statuses.size !== 4) {

      }

      return { agentCount: statuses.size ;};
    });


      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'chat'
      );


      if (!response.success) {

      }

      return { response: response.response ;};
    });


      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'suoke'
      );
      const response = await this.coordinator.coordinateTask(

        context
      );

      if (!response.success) {

      }

      return { response: response.response ;};
    });
  }

  /**
   * 管理器测试
   */
  private async testManager(): Promise<void> {



      await this.manager.initialize();
      const metrics = await this.manager.getSystemMetrics();

      if (!metrics) {

      }

      return { metrics };
    });


      const agent = await createAgent(AgentType.XIAOAI);
      await this.manager.registerAgent(agent);

      const registeredAgents = await this.manager.getRegisteredAgents();

      if (registeredAgents.length === 0) {

      }

      await this.manager.unregisterAgent(AgentType.XIAOAI);
      return { registeredCount: registeredAgents.length ;};
    });
  }

  /**
   * 工厂模式测试
   */
  private async testFactory(): Promise<void> {



      const agents = [];
      for (const agentType of Object.values(AgentType)) {
        const agent = this.factory.createAgent(agentType);
        agents.push(agent);
      }

      if (agents.length !== 4) {

      }

      return { createdCount: agents.length ;};
    });
  }

  /**
   * 协作测试
   */
  private async testCollaboration(): Promise<void> {



      const strategies = Object.keys(COLLABORATION_STRATEGIES);

      if (strategies.length === 0) {

      }

      return { strategies };
    });
  }

  /**
   * 性能测试
   */
  private async testPerformance(): Promise<void> {



      const startTime = Date.now();
      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'chat'
      );



      const responseTime = Date.now() - startTime;

      if (responseTime > 5000) {

      }

      return { responseTime };
    });
  }

  /**
   * 错误处理测试
   */
  private async testErrorHandling(): Promise<void> {



      const context = AgentSystemUtils.createDefaultContext(
        'test_user',
        'chat'
      );

      const response = await this.coordinator.coordinateTask('', context);

      if (response.success) {

      }

      return { handled: true ;};
    });
  }

  /**
   * 运行单个测试
   */
  private async runTest(
    testName: string;
    testFunction: () => Promise<any>
  ): Promise<void> {
    const startTime = Date.now();

    try {
      const data = await testFunction();
      const duration = Date.now() - startTime;

      this.testResults.push({
        testName,
        success: true;
        duration,
        data,
      });

      console.log(`  ✅ ${testName} (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;

      this.testResults.push({
        testName,
        success: false;
        duration,
        error: error instanceof Error ? error.message : String(error);
      });

      console.log(`  ❌ ${testName} (${duration}ms): ${error}`);
    }
  }

  /**
   * 打印测试结果
   */
  private printTestResults(): void {

    console.log('='.repeat(50));

    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter((r) => r.success).length;
    const failedTests = totalTests - passedTests;
    const totalDuration = this.testResults.reduce(
      (sum, r) => sum + r.duration,
      0
    );





    console.log(`成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

    if (failedTests > 0) {

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


  try {
    // 初始化系统
    await initializeAgentSystem();

    // 创建测试智能体
    const agent = await createAgent(AgentType.XIAOAI);
    await agent.initialize();

    // 执行简单任务
    const context = AgentSystemUtils.createDefaultContext('test_user', 'chat');





    await agent.shutdown();
  } catch (error) {

  }
}

/**
 * 运行完整测试套件
 */
export async function runFullTestSuite(): Promise<TestResult[]> {
  const tester = new AgentSystemTester();
  return await tester.runAllTests();
}
