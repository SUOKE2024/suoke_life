import {
  AgentType,
  AgentCapability,
  AgentResponse,
  AgentContext,
  AgentCollaborationMessage,
  AgentDecisionResult,
} from "./types";
import { XiaoaiAgentImpl } from "./xiaoai/XiaoaiAgentImpl";
import { XiaokeAgentImpl } from "./xiaoke/XiaokeAgentImpl";
import { LaokeAgentImpl } from "./laoke/LaokeAgentImpl";
import { SoerAgentImpl } from "./soer/SoerAgentImpl";

/**
 * 智能体协调器
 * 负责多智能体协作、任务分发、决策协调等核心功能
 */
export class AgentCoordinator {
  private agents: Map<AgentType, any> = new Map();
  private collaborationHistory: AgentCollaborationMessage[] = [];
  private isInitialized: boolean = false;

  constructor() {
    this.log("info", "智能体协调器创建");
  }

  /**
   * 初始化协调器和所有智能体
   */
  async initialize(): Promise<void> {
    try {
      this.log("info", "开始初始化智能体协调器...");

      // 创建所有智能体实例
      const xiaoai = new XiaoaiAgentImpl();
      const xiaoke = new XiaokeAgentImpl();
      const laoke = new LaokeAgentImpl();
      const soer = new SoerAgentImpl();

      // 初始化所有智能体
      await Promise.all([
        xiaoai.initialize(),
        xiaoke.initialize(),
        laoke.initialize(),
        soer.initialize(),
      ]);

      // 注册智能体
      this.agents.set(AgentType.XIAOAI, xiaoai);
      this.agents.set(AgentType.XIAOKE, xiaoke);
      this.agents.set(AgentType.LAOKE, laoke);
      this.agents.set(AgentType.SOER, soer);

      this.isInitialized = true;
      this.log("info", "智能体协调器初始化完成");
    } catch (error) {
      this.log("error", "智能体协调器初始化失败", error);
      throw error;
    }
  }

  /**
   * 协调处理用户任务
   */
  async coordinateTask(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    if (!this.isInitialized) {
      throw new Error("智能体协调器尚未初始化");
    }

    try {
      // 分析任务类型和所需智能体
      const taskAnalysis = await this.analyzeTask(message, context);

      // 根据任务类型选择协作模式
      switch (taskAnalysis.collaborationMode) {
        case "single":
          return await this.handleSingleAgentTask(
            taskAnalysis,
            message,
            context
          );
        case "sequential":
          return await this.handleSequentialCollaboration(
            taskAnalysis,
            message,
            context
          );
        case "parallel":
          return await this.handleParallelCollaboration(
            taskAnalysis,
            message,
            context
          );
        case "consensus":
          return await this.handleConsensusCollaboration(
            taskAnalysis,
            message,
            context
          );
        default:
          return await this.handleDefaultTask(message, context);
      }
    } catch (error) {
      this.log("error", "任务协调失败", error);
      throw error;
    }
  }

  /**
   * 分析任务类型和协作需求
   */
  private async analyzeTask(
    message: string,
    context: AgentContext
  ): Promise<any> {
    const keywords = message.toLowerCase();

    // 健康诊断类任务 - 需要多智能体协作
    if (
      keywords.includes("诊断") ||
      keywords.includes("症状") ||
      keywords.includes("健康分析")
    ) {
      return {
        type: "health_diagnosis",
        primaryAgent: AgentType.XIAOAI,
        supportingAgents: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],
        collaborationMode: "sequential",
        priority: "high",
      };
    }

    // 生活方式优化 - 需要索儿主导，其他支持
    if (
      keywords.includes("生活方式") ||
      keywords.includes("习惯") ||
      keywords.includes("改善")
    ) {
      return {
        type: "lifestyle_optimization",
        primaryAgent: AgentType.SOER,
        supportingAgents: [AgentType.XIAOAI, AgentType.LAOKE],
        collaborationMode: "sequential",
        priority: "medium",
      };
    }

    // 知识学习类 - 老克主导
    if (
      keywords.includes("学习") ||
      keywords.includes("知识") ||
      keywords.includes("教育")
    ) {
      return {
        type: "knowledge_learning",
        primaryAgent: AgentType.LAOKE,
        supportingAgents: [AgentType.XIAOAI],
        collaborationMode: "single",
        priority: "medium",
      };
    }

    // 服务推荐类 - 小克主导
    if (
      keywords.includes("推荐") ||
      keywords.includes("服务") ||
      keywords.includes("预约")
    ) {
      return {
        type: "service_recommendation",
        primaryAgent: AgentType.XIAOKE,
        supportingAgents: [AgentType.XIAOAI, AgentType.SOER],
        collaborationMode: "sequential",
        priority: "medium",
      };
    }

    // 紧急情况 - 需要所有智能体协作
    if (
      keywords.includes("紧急") ||
      keywords.includes("急救") ||
      keywords.includes("危险")
    ) {
      return {
        type: "emergency",
        primaryAgent: AgentType.XIAOAI,
        supportingAgents: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],
        collaborationMode: "parallel",
        priority: "critical",
      };
    }

    // 默认单智能体处理
    return {
      type: "general",
      primaryAgent: this.selectPrimaryAgent(context),
      supportingAgents: [],
      collaborationMode: "single",
      priority: "low",
    };
  }

  /**
   * 处理单智能体任务
   */
  private async handleSingleAgentTask(
    taskAnalysis: any,
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const agent = this.agents.get(taskAnalysis.primaryAgent);
    if (!agent) {
      throw new Error(`智能体 ${taskAnalysis.primaryAgent} 不可用`);
    }

    return await agent.processMessage(message, context);
  }

  /**
   * 处理顺序协作任务
   */
  private async handleSequentialCollaboration(
    taskAnalysis: any,
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const results: AgentResponse[] = [];

    // 主智能体处理
    const primaryAgent = this.agents.get(taskAnalysis.primaryAgent);
    const primaryResult = await primaryAgent.processMessage(message, context);
    results.push(primaryResult);

    // 支持智能体依次处理
    for (const agentType of taskAnalysis.supportingAgents) {
      const agent = this.agents.get(agentType);
      if (agent) {
        const supportContext = {
          ...context,
          previousResults: results,
          collaborationMode: "supporting",
        };

        const supportResult = await agent.processMessage(
          `协作支持: ${message}`,
          supportContext
        );
        results.push(supportResult);
      }
    }

    // 整合结果
    return this.integrateCollaborationResults(results, taskAnalysis);
  }

  /**
   * 处理并行协作任务
   */
  private async handleParallelCollaboration(
    taskAnalysis: any,
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const agentPromises: Promise<AgentResponse>[] = [];

    // 主智能体处理
    const primaryAgent = this.agents.get(taskAnalysis.primaryAgent);
    agentPromises.push(primaryAgent.processMessage(message, context));

    // 支持智能体并行处理
    for (const agentType of taskAnalysis.supportingAgents) {
      const agent = this.agents.get(agentType);
      if (agent) {
        const supportContext = {
          ...context,
          collaborationMode: "parallel_supporting",
        };
        agentPromises.push(
          agent.processMessage(`并行协作: ${message}`, supportContext)
        );
      }
    }

    // 等待所有结果
    const results = await Promise.all(agentPromises);

    // 整合结果
    return this.integrateCollaborationResults(results, taskAnalysis);
  }

  /**
   * 处理共识协作任务
   */
  private async handleConsensusCollaboration(
    taskAnalysis: any,
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const decisions: AgentDecisionResult[] = [];

    // 所有相关智能体提供决策意见
    const allAgents = [
      taskAnalysis.primaryAgent,
      ...taskAnalysis.supportingAgents,
    ];

    for (const agentType of allAgents) {
      const agent = this.agents.get(agentType);
      if (agent) {
        const decision = await this.getAgentDecision(agent, message, context);
        decisions.push(decision);
      }
    }

    // 基于共识算法整合决策
    const consensusResult = this.buildConsensus(decisions);

    return {
      success: true,
      response: consensusResult.decision,
      data: {
        consensusConfidence: consensusResult.confidence,
        participatingAgents: allAgents,
        individualDecisions: decisions,
        reasoning: consensusResult.reasoning,
      },
      context,
      metadata: {
        collaborationType: "consensus",
        agentCount: allAgents.length,
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * 处理默认任务
   */
  private async handleDefaultTask(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const primaryAgent = this.selectPrimaryAgent(context);
    const agent = this.agents.get(primaryAgent);

    if (!agent) {
      throw new Error("没有可用的智能体");
    }

    return await agent.processMessage(message, context);
  }

  /**
   * 选择主要智能体
   */
  private selectPrimaryAgent(context: AgentContext): AgentType {
    // 根据当前频道选择主要智能体
    switch (context.currentChannel) {
      case "suoke":
        return AgentType.XIAOKE;
      case "explore":
        return AgentType.LAOKE;
      case "life":
        return AgentType.SOER;
      default:
        return AgentType.XIAOAI;
    }
  }

  /**
   * 整合协作结果
   */
  private integrateCollaborationResults(
    results: AgentResponse[],
    taskAnalysis: any
  ): AgentResponse {
    const primaryResult = results[0];
    const supportingResults = results.slice(1);

    return {
      success: primaryResult.success,
      response: primaryResult.response,
      data: {
        primaryResult: primaryResult.data,
        supportingResults: supportingResults.map((r) => r.data),
        collaborationSummary: this.generateCollaborationSummary(results),
        taskType: taskAnalysis.type,
        collaborationMode: taskAnalysis.collaborationMode,
      },
      context: primaryResult.context,
      metadata: {
        ...primaryResult.metadata,
        collaborationType: taskAnalysis.collaborationMode,
        participatingAgents: [
          taskAnalysis.primaryAgent,
          ...taskAnalysis.supportingAgents,
        ],
        totalExecutionTime: results.reduce(
          (sum, r) => sum + (r.metadata?.executionTime || 0),
          0
        ),
      },
    };
  }

  /**
   * 获取智能体决策
   */
  private async getAgentDecision(
    agent: any,
    message: string,
    context: AgentContext
  ): Promise<AgentDecisionResult> {
    const response = await agent.processMessage(
      `决策请求: ${message}`,
      context
    );

    return {
      decision: response.response,
      confidence: response.metadata?.confidence || 0.5,
      reasoning: [response.response],
      alternatives: [],
      recommendedActions: [],
      metadata: {
        agentType: agent.getAgentType(),
        executionTime: response.metadata?.executionTime,
      },
    };
  }

  /**
   * 构建共识
   */
  private buildConsensus(decisions: AgentDecisionResult[]): any {
    // 简单的共识算法：基于置信度加权
    const totalWeight = decisions.reduce((sum, d) => sum + d.confidence, 0);
    const weightedDecision = decisions.reduce((acc, d) => {
      const weight = d.confidence / totalWeight;
      return acc + weight;
    }, 0);

    return {
      decision: decisions[0].decision, // 简化：选择第一个决策
      confidence: weightedDecision,
      reasoning: decisions.flatMap((d) => d.reasoning),
    };
  }

  /**
   * 生成协作摘要
   */
  private generateCollaborationSummary(results: AgentResponse[]): string {
    const successCount = results.filter((r) => r.success).length;
    return `协作完成，${successCount}/${results.length} 个智能体成功响应`;
  }

  /**
   * 获取所有智能体状态
   */
  async getAllAgentStatus(): Promise<Map<AgentType, any>> {
    const statusMap = new Map();

    for (const [agentType, agent] of this.agents) {
      try {
        const status = await agent.getHealthStatus();
        statusMap.set(agentType, status);
      } catch (error) {
        statusMap.set(agentType, {
          status: "error",
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }

    return statusMap;
  }

  /**
   * 关闭协调器
   */
  async shutdown(): Promise<void> {
    this.log("info", "智能体协调器正在关闭...");

    // 关闭所有智能体
    const shutdownPromises = Array.from(this.agents.values()).map((agent) =>
      agent.shutdown()
    );
    await Promise.all(shutdownPromises);

    this.agents.clear();
    this.collaborationHistory = [];
    this.isInitialized = false;

    this.log("info", "智能体协调器已关闭");
  }

  /**
   * 记录日志
   */
  private log(
    level: "info" | "warn" | "error",
    message: string,
    data?: any
  ): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [AgentCoordinator] [${level.toUpperCase()}] ${message}`;

    switch (level) {
      case "info":
        console.log(logMessage, data || "");
        break;
      case "warn":
        console.warn(logMessage, data || "");
        break;
      case "error":
        console.error(logMessage, data || "");
        break;
    }
  }
}

// 创建全局协调器实例
export const agentCoordinator = new AgentCoordinator();
