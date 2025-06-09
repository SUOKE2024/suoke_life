import { AgentCoordinator } from "./AgentCoordinator";
import { AgentManager } from "./AgentManager";
import { AgentFactory } from "./factory/AgentFactory";
import {
    AgentSystemUtils,
    COLLABORATION_STRATEGIES,
    createAgent,
    executeAgentTask,
    initializeAgentSystem;
} from "./index";
import { AgentType } from "./types";

/**
 * 测试结果接口
 */
interface TestResult {
  testName: string;,
  success: boolean;,
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
    console.log("🚀 开始智能体系统测试...\n");
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
    console.log("📋 基础功能测试");

    // 测试类型定义
    await this.runTest("类型定义测试", async () => {
      const agentTypes = Object.values(AgentType);
      if (agentTypes.length !== 4) {
        throw new Error(`期望4个智能体类型，实际${agentTypes.length}个`);
      }
      return { agentTypes };
    });

    // 测试工具函数
    await this.runTest("工具函数测试", async () => {
      const xiaoaiCapabilities = AgentSystemUtils.getAgentCapabilities(
        AgentType.XIAOAI;
      );
      const xiaokeRole = AgentSystemUtils.getAgentRole(AgentType.XIAOKE);
      const chatAgent = AgentSystemUtils.getAgentByChannel("chat");

      if (xiaoaiCapabilities.length === 0) {
        throw new Error("小艾能力列表为空");
      }
      if (!xiaokeRole || xiaokeRole.name !== "小克") {
        throw new Error("小克角色信息错误");
      }
      if (chatAgent !== AgentType.XIAOAI) {
        throw new Error("聊天频道应该对应小艾");
      }

      return { xiaoaiCapabilities, xiaokeRole, chatAgent };
    });

    // 测试上下文创建
    await this.runTest("上下文创建测试", async () => {
      const context = AgentSystemUtils.createDefaultContext(
        "test_user",
        "suoke"
      );

      if (!AgentSystemUtils.validateContext(context)) {
        throw new Error("上下文验证失败");
      }
      if (context.currentChannel !== "suoke") {
        throw new Error("频道设置错误");
      }

      return { context };
    });
  }

  /**
   * 智能体创建测试
   */
  private async testAgentCreation(): Promise<void> {
    console.log("🤖 智能体创建测试");

    // 测试单个智能体创建
    for (const agentType of Object.values(AgentType)) {
      await this.runTest(`创建${agentType}智能体`, async () => {
        const agent = await createAgent(agentType);
        await agent.initialize();
        const healthStatus = await agent.getHealthStatus();

        if (!healthStatus) {
          throw new Error("健康状态获取失败");
        }

        await agent.shutdown();
        return { agentType, healthStatus };
      });
    }

    // 测试批量创建
    await this.runTest("批量创建智能体", async () => {
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
        agents.map(agent) => agent.getHealthStatus())
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
    console.log("🎯 协调器测试");

    await this.runTest("协调器初始化", async () => {
      await this.coordinator.initialize();
      const statuses = await this.coordinator.getAllAgentStatus();

      if (statuses.size !== 4) {
        throw new Error(`期望4个智能体，实际${statuses.size}个`);
      }

      return { agentCount: statuses.size };
    });

    await this.runTest("单智能体任务处理", async () => {
      const context = AgentSystemUtils.createDefaultContext(
        "test_user",
        "chat"
      );
      const response = await this.coordinator.coordinateTask("你好", context);

      if (!response.success) {
        throw new Error("任务处理失败");
      }

      return { response: response.response };
    });

    await this.runTest("多智能体协作任务", async () => {
      const context = AgentSystemUtils.createDefaultContext(
        "test_user",
        "chat"
      );
      const response = await this.coordinator.coordinateTask(
        "我感觉头痛，请帮我分析一下可能的原因并推荐相关服务",
        context;
      );

      if (!response.success) {
        throw new Error("协作任务处理失败");
      }

      return {
        response: response.response,
        collaborationType: response.metadata?.collaborationType,
      };
    });
  }

  /**
   * 管理器测试
   */
  private async testManager(): Promise<void> {
    console.log("📊 管理器测试");

    await this.runTest("管理器初始化", async () => {
      await this.manager.initialize();
      const overview = this.manager.getSystemOverview();

      if (overview.totalAgents === 0) {
        throw new Error("没有检测到智能体");
      }

      return { overview };
    });

    await this.runTest("任务处理", async () => {
      const context = AgentSystemUtils.createDefaultContext("test_user");
      const result = await this.manager.processTask("测试消息", context);

      if (!result.success) {
        throw new Error("任务处理失败");
      }

      return { result };
    });

    await this.runTest("性能指标获取", async () => {
      const metrics = this.manager.getMetrics();
      return { metrics };
    });
  }

  /**
   * 工厂模式测试
   */
  private async testFactory(): Promise<void> {
    console.log("🏭 工厂模式测试");

    await this.runTest("工厂实例获取", async () => {
      const factory1 = AgentFactory.getInstance();
      const factory2 = AgentFactory.getInstance();

      if (factory1 !== factory2) {
        throw new Error("工厂不是单例模式");
      }

      return { isSingleton: true };
    });
  }

  /**
   * 协作测试
   */
  private async testCollaboration(): Promise<void> {
    console.log("🤝 协作测试");

    await this.runTest("协作策略测试", async () => {
      const strategies = Object.keys(COLLABORATION_STRATEGIES);
      if (strategies.length === 0) {
        throw new Error("没有协作策略");
      }
      return { strategies };
    });
  }

  /**
   * 性能测试
   */
  private async testPerformance(): Promise<void> {
    console.log("⚡ 性能测试");

    await this.runTest("响应时间测试", async () => {
      const startTime = Date.now();
      const context = AgentSystemUtils.createDefaultContext("test_user");
      await this.coordinator.coordinateTask("测试消息", context);
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
    console.log("🚨 错误处理测试");

    await this.runTest("无效输入处理", async () => {
      try {
        const context = AgentSystemUtils.createDefaultContext("test_user");
        await this.coordinator.coordinateTask("", context);
        throw new Error("应该抛出错误");
      } catch (error) {
        return { errorHandled: true };
      }
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
      console.log(`✅ ${testName} (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;
      this.testResults.push({
        testName,
        success: false,
        duration,
        error: error instanceof Error ? error.message : String(error),
      });
      console.log(`❌ ${testName} (${duration}ms): ${error}`);
    }
  }

  /**
   * 打印测试结果
   */
  private printTestResults(): void {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r) => r.success).length;
    const failedTests = totalTests - passedTests;
    const totalDuration = this.testResults.reduce(sum, r) => sum + r.duration,
      0;
    );

    console.log("\n📊 测试结果汇总:");
    console.log(`总测试数: ${totalTests}`);
    console.log(`通过: ${passedTests}`);
    console.log(`失败: ${failedTests}`);
    console.log(`总耗时: ${totalDuration}ms`);
    console.log(`成功率: ${(passedTests / totalTests) * 100).toFixed(2)}%`);

    if (failedTests > 0) {
      console.log("\n❌ 失败的测试:");
      this.testResults;
        .filter(r) => !r.success)
        .forEach(r) => {
          console.log(`  - ${r.testName}: ${r.error}`);
        });
    }
  }
}

/**
 * 快速测试函数
 */
export async function quickTest(): Promise<void> {
  console.log("🚀 快速智能体系统测试");
  
  try {
    // 初始化系统
    await initializeAgentSystem();
    console.log("✅ 系统初始化成功");

    // 创建测试智能体
    const xiaoai = await createAgent(AgentType.XIAOAI);
    await xiaoai.initialize();
    console.log("✅ 小艾创建成功");

    // 执行简单任务
    const context = AgentSystemUtils.createDefaultContext("test_user");
    const result = await executeAgentTask("你好", context);
    console.log("✅ 任务执行成功:", result);

    // 清理
    await xiaoai.shutdown();
    console.log("✅ 清理完成");

  } catch (error) {
    console.error("❌ 快速测试失败:", error);
  }
}

/**
 * 运行完整测试套件
 */
export async function runFullTestSuite(): Promise<TestResult[]> {
  const tester = new AgentSystemTester();
  return await tester.runAllTests();
}

// 默认导出
export default {
  AgentSystemTester,
  quickTest,
  runFullTestSuite,
};