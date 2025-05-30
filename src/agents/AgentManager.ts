import { XiaoaiAgentImpl } from "./xiaoai/XiaoaiAgentImpl";
import { XiaoaiAgent } from "./xiaoai/types";





  AgentCoordinator,
  AgentType,
  AgentTask,
  AgentCoordinationResult,
} from "./AgentCoordinator";

/**
 * 智能体管理器 - 统一管理四个智能体
 * 基于README.md描述实现智能体生命周期管理
 */

export interface AgentManagerConfig {
  enableAutoStart: boolean;
  enableHealthMonitoring: boolean;
  enableLoadBalancing: boolean;
  enableFailover: boolean;
  maxRetries: number;
  timeoutMs: number;
  healthCheckIntervalMs: number;
  logLevel: "debug" | "info" | "warn" | "error";
}

export interface AgentStatus {
  agentType: AgentType;
  status: "initializing" | "active" | "inactive" | "error" | "maintenance";
  uptime: number;
  lastHealthCheck: Date;
  errorCount: number;
  successCount: number;
  averageResponseTime: number;
  currentLoad: number;
  capabilities: string[];
  version: string;
}

export interface AgentMetrics {
  totalTasks: number;
  successfulTasks: number;
  failedTasks: number;
  averageResponseTime: number;
  peakLoad: number;
  uptime: number;
  errorRate: number;
  lastUpdate: Date;
}

export class AgentManager {
  private coordinator: AgentCoordinator;
  private config: AgentManagerConfig;
  private agentInstances: Map<AgentType, any> = new Map();
  private agentMetrics: Map<AgentType, AgentMetrics> = new Map();
  private isInitialized: boolean = false;
  private healthCheckTimer?: ReturnType<typeof setInterval>;
  private metricsTimer?: ReturnType<typeof setInterval>;

  constructor(config: Partial<AgentManagerConfig> = {}) {
    this.config = {
      enableAutoStart: true,
      enableHealthMonitoring: true,
      enableLoadBalancing: true,
      enableFailover: true,
      maxRetries: 3,
      timeoutMs: 30000,
      healthCheckIntervalMs: 60000,
      logLevel: "info",
      ...config,
    };

    this.coordinator = new AgentCoordinator({
      enableLoadBalancing: this.config.enableLoadBalancing,
      enableFailover: this.config.enableFailover,
      maxRetries: this.config.maxRetries,
      timeoutMs: this.config.timeoutMs,
      healthCheckIntervalMs: this.config.healthCheckIntervalMs,
    });

    this.initializeMetrics();
  }

  /**
   * 初始化所有智能体
   */
  async initialize(): Promise<void> {
    try {
      this.log("info", "开始初始化智能体管理器...");

      // 初始化各个智能体实例
      await this.initializeAgents();

      // 启动健康监控
      if (this.config.enableHealthMonitoring) {
        this.startHealthMonitoring();
      }

      // 启动指标收集
      this.startMetricsCollection();

      this.isInitialized = true;
      this.log("info", "智能体管理器初始化完成");
    } catch (error: any) {
      this.log("error", `智能体管理器初始化失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 初始化各个智能体
   */
  private async initializeAgents(): Promise<void> {
    const agentTypes: AgentType[] = ["xiaoai", "xiaoke", "laoke", "soer"];

    for (const agentType of agentTypes) {
      try {
        this.log("info", `初始化 ${agentType} 智能体...`);

        const agentInstance = await this.createAgentInstance(agentType);
        this.agentInstances.set(agentType, agentInstance);

        // 初始化指标
        this.initializeAgentMetrics(agentType);

        this.log("info", `${agentType} 智能体初始化成功`);
      } catch (error: any) {
        this.log("error", `${agentType} 智能体初始化失败: ${error.message}`);
        throw error;
      }
    }
  }

  /**
   * 创建智能体实例
   */
  private async createAgentInstance(agentType: AgentType): Promise<any> {
    switch (agentType) {
      case "xiaoai":
        return new XiaoaiAgentImpl();
      case "xiaoke":
        // 这里应该返回实际的小克智能体实现
        return this.createMockAgent(agentType);
      case "laoke":
        // 这里应该返回实际的老克智能体实现
        return this.createMockAgent(agentType);
      case "soer":
        // 这里应该返回实际的索儿智能体实现
        return this.createMockAgent(agentType);
      default:
        throw new Error(`未知的智能体类型: ${agentType}`);
    }
  }

  /**
   * 创建模拟智能体（临时实现）
   */
  private createMockAgent(agentType: AgentType): any {
    return {
      processMessage: async (message: string, context: any) => {
        return { response: `${agentType} 处理消息: ${message}`, context };
      },
      getHealthStatus: async () => {
        return {
          agentType,
          status: "healthy",
          load: Math.random() * 0.5,
          responseTime: Math.random() * 1000,
          errorRate: Math.random() * 0.1,
          lastCheck: new Date(),
          capabilities: [`${agentType}_capability`],
          version: "1.0.0",
        };
      },
      cleanup: async () => {
        // 清理逻辑
      },
    };
  }

  /**
   * 执行智能体任务
   */
  async executeTask(task: AgentTask): Promise<AgentCoordinationResult> {
    if (!this.isInitialized) {
      throw new Error("智能体管理器尚未初始化");
    }

    try {
      this.log("debug", `执行任务: ${task.taskId}, 类型: ${task.type}`);

      const startTime = Date.now();
      const result = await this.coordinator.coordinateTask(task);
      const executionTime = Date.now() - startTime;

      // 更新指标
      this.updateTaskMetrics(task, result, executionTime);

      this.log(
        "debug",
        `任务 ${task.taskId} 执行完成, 耗时: ${executionTime}ms`
      );

      return result;
    } catch (error: any) {
      this.log("error", `任务 ${task.taskId} 执行失败: ${error.message}`);

      // 更新失败指标
      this.updateFailureMetrics(task);

      throw error;
    }
  }

  /**
   * 获取智能体状态
   */
  async getAgentStatus(
    agentType?: AgentType
  ): Promise<Map<AgentType, AgentStatus>> {
    const statusMap = new Map<AgentType, AgentStatus>();
    const healthMap = await this.coordinator.getAgentHealth(agentType);

    for (const [type, health] of healthMap) {
      const metrics = this.agentMetrics.get(type);
      const instance = this.agentInstances.get(type);

      statusMap.set(type, {
        agentType: type,
        status: this.mapHealthToStatus(health.status),
        uptime: metrics?.uptime || 0,
        lastHealthCheck: health.lastCheck,
        errorCount: this.calculateErrorCount(type),
        successCount: metrics?.successfulTasks || 0,
        averageResponseTime: health.responseTime,
        currentLoad: health.load,
        capabilities: health.capabilities,
        version: health.version,
      });
    }

    return statusMap;
  }

  /**
   * 获取智能体指标
   */
  getAgentMetrics(agentType?: AgentType): Map<AgentType, AgentMetrics> {
    if (agentType) {
      const metrics = this.agentMetrics.get(agentType);
      const result = new Map<AgentType, AgentMetrics>();
      if (metrics) {
        result.set(agentType, metrics);
      }
      return result;
    }

    return new Map(this.agentMetrics);
  }

  /**
   * 重启智能体
   */
  async restartAgent(agentType: AgentType): Promise<void> {
    try {
      this.log("info", `重启 ${agentType} 智能体...`);

      // 清理现有实例
      const existingInstance = this.agentInstances.get(agentType);
      if (existingInstance && existingInstance.cleanup) {
        await existingInstance.cleanup();
      }

      // 创建新实例
      const newInstance = await this.createAgentInstance(agentType);
      this.agentInstances.set(agentType, newInstance);

      // 重置指标
      this.initializeAgentMetrics(agentType);

      this.log("info", `${agentType} 智能体重启成功`);
    } catch (error: any) {
      this.log("error", `${agentType} 智能体重启失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 启动健康监控
   */
  private startHealthMonitoring(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }

    this.healthCheckTimer = setInterval(async () => {
      try {
        await this.performHealthCheck();
      } catch (error: any) {
        this.log("error", `健康检查失败: ${error.message}`);
      }
    }, this.config.healthCheckIntervalMs);

    this.log("info", "健康监控已启动");
  }

  /**
   * 执行健康检查
   */
  private async performHealthCheck(): Promise<void> {
    const healthMap = await this.coordinator.getAgentHealth();

    for (const [agentType, health] of healthMap) {
      if (health.status !== "healthy") {
        this.log("warn", `智能体 ${agentType} 健康状态异常: ${health.status}`);

        if (this.config.enableFailover && health.status === "unhealthy") {
          this.log("info", `尝试重启不健康的智能体: ${agentType}`);
          try {
            await this.restartAgent(agentType);
          } catch (error: any) {
            this.log("error", `智能体 ${agentType} 重启失败: ${error.message}`);
          }
        }
      }
    }
  }

  /**
   * 启动指标收集
   */
  private startMetricsCollection(): void {
    if (this.metricsTimer) {
      clearInterval(this.metricsTimer);
    }

    this.metricsTimer = setInterval(() => {
      this.updateUptimeMetrics();
    }, 60000); // 每分钟更新一次运行时间

    this.log("info", "指标收集已启动");
  }

  /**
   * 初始化指标
   */
  private initializeMetrics(): void {
    const agentTypes: AgentType[] = ["xiaoai", "xiaoke", "laoke", "soer"];

    for (const agentType of agentTypes) {
      this.initializeAgentMetrics(agentType);
    }
  }

  /**
   * 初始化智能体指标
   */
  private initializeAgentMetrics(agentType: AgentType): void {
    this.agentMetrics.set(agentType, {
      totalTasks: 0,
      successfulTasks: 0,
      failedTasks: 0,
      averageResponseTime: 0,
      peakLoad: 0,
      uptime: 0,
      errorRate: 0,
      lastUpdate: new Date(),
    });
  }

  /**
   * 更新任务指标
   */
  private updateTaskMetrics(
    task: AgentTask,
    result: AgentCoordinationResult,
    executionTime: number
  ): void {
    const agentTypes = task.requiredAgents || [
      this.getDefaultAgentForTask(task),
    ];

    for (const agentType of agentTypes) {
      const metrics = this.agentMetrics.get(agentType);
      if (metrics) {
        metrics.totalTasks++;
        if (result.status === "completed") {
          metrics.successfulTasks++;
        } else {
          metrics.failedTasks++;
        }

        // 更新平均响应时间
        metrics.averageResponseTime =
          (metrics.averageResponseTime * (metrics.totalTasks - 1) +
            executionTime) /
          metrics.totalTasks;

        // 更新错误率
        metrics.errorRate = metrics.failedTasks / metrics.totalTasks;

        metrics.lastUpdate = new Date();
      }
    }
  }

  /**
   * 更新失败指标
   */
  private updateFailureMetrics(task: AgentTask): void {
    const agentTypes = task.requiredAgents || [
      this.getDefaultAgentForTask(task),
    ];

    for (const agentType of agentTypes) {
      const metrics = this.agentMetrics.get(agentType);
      if (metrics) {
        metrics.totalTasks++;
        metrics.failedTasks++;
        metrics.errorRate = metrics.failedTasks / metrics.totalTasks;
        metrics.lastUpdate = new Date();
      }
    }
  }

  /**
   * 更新运行时间指标
   */
  private updateUptimeMetrics(): void {
    for (const [agentType, metrics] of this.agentMetrics) {
      metrics.uptime += 1; // 增加1分钟
      metrics.lastUpdate = new Date();
    }
  }

  /**
   * 根据任务类型获取默认智能体
   */
  private getDefaultAgentForTask(task: AgentTask): AgentType {
    switch (task.type) {
      case "diagnosis":
        return "xiaoai";
      case "recommendation":
        return "xiaoke";
      case "education":
        return "laoke";
      case "lifestyle":
        return "soer";
      default:
        return "xiaoai";
    }
  }

  /**
   * 映射健康状态到智能体状态
   */
  private mapHealthToStatus(healthStatus: string): AgentStatus["status"] {
    switch (healthStatus) {
      case "healthy":
        return "active";
      case "degraded":
        return "inactive";
      case "unhealthy":
        return "error";
      case "offline":
        return "inactive";
      default:
        return "error";
    }
  }

  /**
   * 计算错误数量
   */
  private calculateErrorCount(agentType: AgentType): number {
    const metrics = this.agentMetrics.get(agentType);
    return metrics?.failedTasks || 0;
  }

  /**
   * 日志记录
   */
  private log(
    level: "debug" | "info" | "warn" | "error",
    message: string
  ): void {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    const configLevel = levels[this.config.logLevel];
    const messageLevel = levels[level];

    if (messageLevel >= configLevel) {
      const timestamp = new Date().toISOString();
      console.log(
        `[${timestamp}] [${level.toUpperCase()}] [AgentManager] ${message}`
      );
    }
  }

  /**
   * 清理资源
   */
  async cleanup(): Promise<void> {
    this.log("info", "开始清理智能体管理器...");

    // 停止定时器
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }
    if (this.metricsTimer) {
      clearInterval(this.metricsTimer);
    }

    // 清理所有智能体实例
    for (const [agentType, instance] of this.agentInstances) {
      try {
        if (instance.cleanup) {
          await instance.cleanup();
        }
        this.log("info", `${agentType} 智能体已清理`);
      } catch (error: any) {
        this.log("error", `清理 ${agentType} 智能体失败: ${error.message}`);
      }
    }

    // 清理协调器
    await this.coordinator.cleanup();

    // 清理内部状态
    this.agentInstances.clear();
    this.agentMetrics.clear();
    this.isInitialized = false;

    this.log("info", "智能体管理器清理完成");
  }

  /**
   * 获取管理器状态
   */
  getManagerStatus(): {
    initialized: boolean;
    agentCount: number;
    totalTasks: number;
    successfulTasks: number;
    failedTasks: number;
    uptime: number;
  } {
    let totalTasks = 0;
    let successfulTasks = 0;
    let failedTasks = 0;
    let maxUptime = 0;

    for (const metrics of this.agentMetrics.values()) {
      totalTasks += metrics.totalTasks;
      successfulTasks += metrics.successfulTasks;
      failedTasks += metrics.failedTasks;
      maxUptime = Math.max(maxUptime, metrics.uptime);
    }

    return {
      initialized: this.isInitialized,
      agentCount: this.agentInstances.size,
      totalTasks,
      successfulTasks,
      failedTasks,
      uptime: maxUptime,
    };
  }
}

// 导出单例实例
export const agentManager = new AgentManager();
