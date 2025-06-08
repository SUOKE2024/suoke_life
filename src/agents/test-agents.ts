import { AgentType, AgentContext, AgentResponse } from "./types";
import { AgentCoordinator } from "./AgentCoordinator";
import { AgentManager } from "./AgentManager";
import { AgentFactory } from "./factory/AgentFactory";
import {createAgent,
  initializeAgentSystem,
  executeAgentTask,
  AgentSystemUtils,
  AGENT_CAPABILITIES,
  COLLABORATION_STRATEGIES;
} from "./index";
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
    await this.runTest("类型定义测试", " async () => {
      const agentTypes = Object.values(AgentType);
      if (agentTypes.length !== 4) {
        throw new Error(`期望4个智能体类型，实际${agentTypes.length}个`);
      }
      return { agentTypes };
    });
    // 测试工具函数
    await this.runTest("工具函数测试", async () => {
      const xiaoaiCapabilities = AgentSystemUtils.getAgentCapabilities(;)
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
      const context = AgentSystemUtils.createDefaultContext(;)
        "test_user",suoke";
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
    await this.runTest("批量创建智能体", " async () => {
      const agents = await Promise.all([;)
        createAgent(AgentType.XIAOAI),createAgent(AgentType.XIAOKE),createAgent(AgentType.LAOKE),createAgent(AgentType.SOER);
      ]);
      for (const agent of agents) {
        await agent.initialize();
      }
      const statuses = await Promise.all(;)
        agents.map(agent) => agent.getHealthStatus());
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
    await this.runTest("协调器初始化", " async () => {
      await this.coordinator.initialize();
      const statuses = await this.coordinator.getAllAgentStatus();
      if (statuses.size !== 4) {
        throw new Error(`期望4个智能体，实际${statuses.size}个`);
      }
      return { agentCount: statuses.size };
    });
    await this.runTest("单智能体任务处理", async () => {
      const context = AgentSystemUtils.createDefaultContext(;)
        "test_user",chat";
      );
      const response = await this.coordinator.coordinateTask("你好", context);
      if (!response.success) {
        throw new Error("任务处理失败");
      }
      return { response: response.response };
    });
    await this.runTest("多智能体协作任务", async () => {
      const context = AgentSystemUtils.createDefaultContext(;)
        "test_user",chat";
      );
      const response = await this.coordinator.coordinateTask(;)
        "我感觉头痛，请帮我分析一下可能的原因并推荐相关服务",context;
      );
      if (!response.success) {
        throw new Error("协作任务处理失败");
      }
      return {response: response.response,collaborationType: response.metadata?.collaborationType;
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
      if (!metrics || (metrics instanceof Map && metrics.size === 0)) {
        throw new Error("性能指标为空");
      }
      return { metricsCount: metrics instanceof Map ? metrics.size : 1 };
    });
  }
  /**
  * 工厂模式测试
  */
  private async testFactory(): Promise<void> {
    console.log("🏭 工厂模式测试");
    await this.runTest("工厂创建智能体", async () => {
      const instance = await this.factory.createAgent({agentType: AgentType.XIAOAI,enableLogging: true,maxConcurrentTasks: 3;)
      });
      if (!instance.isActive) {
        throw new Error("智能体实例未激活");
      }
      await this.factory.releaseAgent(instance.id);
      return { instanceId: instance.id };
    });
    await this.runTest("批量创建和管理", async () => {
      const configs = [;
        { agentType: AgentType.XIAOAI },{ agentType: AgentType.XIAOKE },{ agentType: AgentType.LAOKE };
      ];
      const instances = await this.factory.createAgentBatch(configs);
      const activeInstances = this.factory.getActiveInstances();
      if (instances.length !== 3) {
        throw new Error("批量创建失败");
      }
      // 清理
      for (const instance of instances) {
        await this.factory.releaseAgent(instance.id);
      }
      return {createdCount: instances.length,activeCount: activeInstances.length;
      };
    });
    await this.runTest("工厂统计信息", " async () => {
      const stats = this.factory.getStatistics();
      return { stats };
    });
  }
  /**
  * 协作测试
  */
  private async testCollaboration(): Promise<void> {
    console.log("🤝 协作测试");
    const collaborationScenarios = [
      {
      name: "健康诊断协作",
      message: "我最近总是感到疲劳，睡眠质量也不好，请帮我分析一下",
        expectedMode: "sequential"
      },{
      name: "服务推荐协作",
      message: "我想找一个好的中医医生，最好是专门看失眠的",expectedMode: "sequential";
      },{
      name: "知识学习协作",
      message: "我想学习中医养生知识，请为我制定一个学习计划",expectedMode: "single";
      },{
      name: "紧急情况协作",
      message: "紧急！我突然胸痛，需要立即帮助",expectedMode: "parallel";
      };
    ];
    for (const scenario of collaborationScenarios) {
      await this.runTest(scenario.name, async () => {
        const context = AgentSystemUtils.createDefaultContext("test_user");
        const response = await executeAgentTask(scenario.message, context);
        if (!response.success) {
          throw new Error("协作任务失败");
        }
        return {response: response.response,collaborationType: response.metadata?.collaborationType,expectedMode: scenario.expectedMode;
        };
      });
    }
  }
  /**
  * 性能测试
  */
  private async testPerformance(): Promise<void> {
    console.log("⚡ 性能测试");
    await this.runTest("并发处理测试", async () => {
      const context = AgentSystemUtils.createDefaultContext("test_user");
      const tasks = Array.from({ length: 5 }, (_, i) =>;)
        executeAgentTask(`测试消息 ${i + 1}`, context);
      );
      const startTime = Date.now();
      const results = await Promise.all(tasks);
      const duration = Date.now() - startTime;
      const successCount = results.filter(r) => r.success).length;
      if (successCount !== 5) {
        throw new Error(`期望5个成功，实际${successCount}个`);
      }
      return {totalTasks: 5,successCount,duration,avgDuration: duration / 5;
      };
    });
    await this.runTest("响应时间测试", async () => {
      const context = AgentSystemUtils.createDefaultContext("test_user");
      const measurements = [];
      for (let i = 0; i < 3; i++) {
        const startTime = Date.now();
        await executeAgentTask("简单测试消息", " context);
        const duration = Date.now() - startTime;
        measurements.push(duration);
      }
      const avgResponseTime =
        measurements.reduce(a, b) => a + b, 0) / measurements.length;
      if (avgResponseTime > 5000) {
        throw new Error(`响应时间过长: ${avgResponseTime}ms`);
      }
      return {measurements,avgResponseTime,maxResponseTime: Math.max(...measurements),minResponseTime: Math.min(...measurements);
      };
    });
  }
  /**
  * 错误处理测试
  */
  private async testErrorHandling(): Promise<void> {
    console.log("🚨 错误处理测试");
    await this.runTest("无效上下文处理", async () => {
      try {
        const invalidContext = {} as AgentContext;
        await executeAgentTask("测试消息", invalidContext);
        throw new Error("应该抛出错误");
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        if (errorMessage === "应该抛出错误") {
          throw error;
        }
        return { errorHandled: true, errorMessage };
      }
    });
    await this.runTest("空消息处理", async () => {
      const context = AgentSystemUtils.createDefaultContext("test_user");
      const response = await executeAgentTask("", context);
      // 应该有某种形式的响应，即使是空消息
      return {responseReceived: !!response,responseContent: response.response;
      };
    });
    await this.runTest("超长消息处理", async () => {
      const context = AgentSystemUtils.createDefaultContext("test_user");
      const longMessage = "a".repeat(10000);
      const response = await executeAgentTask(longMessage, context);
      return {messageLength: longMessage.length,responseReceived: !!response,success: response.success;
      };
    });
  }
  /**
  * 运行单个测试
  */
  private async runTest()
    testName: string,
    testFn: () => Promise<any>
  ): Promise<void> {
    const startTime = Date.now();
    try {
      const data = await testFn();
      const duration = Date.now() - startTime;
      this.testResults.push({
        testName,
        success: true,
        duration,
        data;
      });
      console.log(`  ✅ ${testName} (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      this.testResults.push({
        testName,
        success: false,
        duration,
        error: errorMessage;
      });
      console.log(`  ❌ ${testName} (${duration}ms): ${errorMessage}`);
    }
  }
  /**
  * 打印测试结果
  */
  private printTestResults(): void {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r) => r.success).length;
    const failedTests = totalTests - passedTests;
    const totalDuration = this.testResults.reduce((acc, item) => acc + item, 0);
      (sum, r) => sum + r.duration,0;
    );
    console.log("\n📊 测试结果汇总:");
    console.log(`总测试数: ${totalTests}`);
    console.log(`通过: ${passedTests}`);
    console.log(`失败: ${failedTests}`);
    console.log(`成功率: ${(passedTests / totalTests) * 100).toFixed(1)}%`);
    console.log(`总耗时: ${totalDuration}ms`);
    console.log(`平均耗时: ${(totalDuration / totalTests).toFixed(1)}ms`);
    if (failedTests > 0) {
      console.log("\n❌ 失败的测试:");
      this.testResults;
        .filter(r) => !r.success)
        .forEach(((r) => console.log(`  - ${r.testName}: ${r.error}`));)
    }
    console.log("\n🎉 智能体系统测试完成!\n");
  }
  /**
  * 清理资源
  */
  async cleanup(): Promise<void> {
    try {
      await this.coordinator.shutdown();
      await this.manager.shutdown();
      await this.factory.shutdown();
    } catch (error) {
      console.error("清理资源时出错:", " error);
    }
  }
}
/**
* 快速测试函数
*/
export async function quickTest(): Promise<void> {
  console.log("🚀 快速智能体测试");
  try {
    // 测试基本功能
    const context = AgentSystemUtils.createDefaultContext("quick_test_user");
    const response = await executeAgentTask("你好，请介绍一下你自己", context);
    console.log("✅ 基本功能测试通过");
    console.log(`响应: ${response.response.substring(0, 100)}...`);
    // 测试智能体切换
    const suokeContext = AgentSystemUtils.createDefaultContext(;)
      "quick_test_user",suoke";
    );
    const suokeResponse = await executeAgentTask(;)
      "推荐一些健康服务",suokeContext;
    );
    console.log("✅ 智能体切换测试通过");
    console.log(`小克响应: ${suokeResponse.response.substring(0, 100)}...`);
  } catch (error) {
    console.error("❌ 快速测试失败:", error);
  }
}
/**
* 运行完整测试套件
*/
export async function runFullTestSuite(): Promise<TestResult[]> {
  const tester = new AgentSystemTester();
  try {
    const results = await tester.runAllTests();
    return results;
  } finally {
    await tester.cleanup();
  }
}
// 如果直接运行此文件，执行快速测试
if (require.main === module) {
  quickTest().catch(console.error);
}