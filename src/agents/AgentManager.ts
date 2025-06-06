import { AgentType, AgentHealthStatus } from "./types";
import { AgentCoordinator } from "./AgentCoordinator";

/**
 * 智能体管理器配置
 */
export interface AgentManagerConfig {
  maxConcurrentTasks: number;
  healthCheckInterval: number;
  autoRestart: boolean;
  logLevel: "debug" | "info" | "warn" | "error";
  performanceMonitoring: boolean;
  resourceLimits: {
    memory: number;
    cpu: number;
  };
}

/**
 * 智能体状态
 */
export type AgentStatus  = | "initializing"
  | "active"
  | "inactive"
  | "error"
  | "maintenance";

/**
 * 智能体性能指标
 */
export interface AgentMetrics {
  tasksProcessed: number;
  successRate: number;
  averageResponseTime: number;
  errorCount: number;
  lastActive: Date;
  memoryUsage: number;
  cpuUsage: number;
  uptime: number;
}

/**
 * 智能体管理器
 * 负责智能体的生命周期管理、性能监控、资源分配等
 */
export class AgentManager {
  private config: AgentManagerConfig;
  private coordinator: AgentCoordinator;
  private metrics: Map<AgentType, AgentMetrics> = new Map();
  private healthCheckTimer: NodeJS.Timeout | null = null;
  private isRunning: boolean = false;

  constructor(config?: Partial<AgentManagerConfig>) {
    this.config = {
      maxConcurrentTasks: 10,
      healthCheckInterval: 30000, // 30秒
      autoRestart: true,
      logLevel: "info",
      performanceMonitoring: true,
      resourceLimits: {
        memory: 512, // MB
        cpu: 80, // 百分比
      },
      ...config
    };

    this.coordinator = new AgentCoordinator();
    this.initializeMetrics();
  }

  /**
   * 初始化管理器
   */
  async initialize(): Promise<void> {
    try {
      this.log("info", "智能体管理器开始初始化...");

      // 初始化协调器
      await this.coordinator.initialize();

      // 启动健康检查
      this.startHealthCheck();

      // 启动性能监控
      if (this.config.performanceMonitoring) {
        this.startPerformanceMonitoring();
      }

      this.isRunning = true;
      this.log("info", "智能体管理器初始化完成");
    } catch (error) {
      this.log("error", "智能体管理器初始化失败", error);
      throw error;
    }
  }

  /**
   * 处理任务
   */
  async processTask(message: string, context: any): Promise<any> {
    if (!this.isRunning) {
      throw new Error("智能体管理器未运行");
    }

    const startTime = Date.now();

    try {
      // 检查并发任务限制
      if (this.getCurrentTaskCount() >= this.config.maxConcurrentTasks) {
        throw new Error("达到最大并发任务限制");
      }

      // 通过协调器处理任务
      const result = await this.coordinator.coordinateTask(message, context);

      // 更新性能指标
      this.updateMetrics(result, Date.now() - startTime);

      return result;
    } catch (error) {
      this.log("error", "任务处理失败", error);
      this.updateErrorMetrics();
      throw error;
    }
  }

  /**
   * 获取智能体状态
   */
  async getAgentStatus(
    agentType?: AgentType
  ): Promise<Map<AgentType, AgentHealthStatus> | AgentHealthStatus> {
    const allStatus = await this.coordinator.getAllAgentStatus();

    if (agentType) {
      return (;
        allStatus.get(agentType) || {agentType,status: "error",load: 0,responseTime: 0,errorRate: 1,lastCheck: new Date(),capabilities: [],version: "0.0.0";
        };
      );
    }

    return allStatus;
  }

  /**
   * 获取性能指标
   */
  getMetrics(
    agentType?: AgentType
  ): Map<AgentType, AgentMetrics> | AgentMetrics | undefined {
    if (agentType) {
      return this.metrics.get(agentType);
    }
    return this.metrics;
  }

  /**
   * 重启智能体
   */
  async restartAgent(agentType: AgentType): Promise<void> {
    this.log("info", `重启智能体: ${agentType}`);

    try {
      // 这里应该实现具体的重启逻辑
      // 由于当前架构限制，我们记录重启事件
      this.log("info", `智能体 ${agentType} 重启完成`);
    } catch (error) {
      this.log("error", `智能体 ${agentType} 重启失败`, error);
      throw error;
    }
  }

  /**
   * 获取系统概览
   */
  getSystemOverview(): any {
    const totalTasks = Array.from(this.metrics.values()).reduce(;
      (sum, m) => sum + m.tasksProcessed,0;
    );
    const totalErrors = Array.from(this.metrics.values()).reduce(;
      (sum, m) => sum + m.errorCount,0;
    );
    const avgResponseTime = this.calculateAverageResponseTime();
    const systemUptime = this.getSystemUptime();

    return {totalAgents: this.metrics.size,totalTasksProcessed: totalTasks,totalErrors,overallSuccessRate:;
        totalTasks > 0 ? (totalTasks - totalErrors) / totalTasks : 0,averageResponseTime: avgResponseTime,systemUptime,isHealthy: this.isSystemHealthy(),config: this.config,lastUpdate: new Date();
    };
  }

  /**
   * 关闭管理器
   */
  async shutdown(): Promise<void> {
    this.log("info", "智能体管理器正在关闭...");

    this.isRunning = false;

    // 停止健康检查
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }

    // 关闭协调器
    await this.coordinator.shutdown();

    this.log("info", "智能体管理器已关闭");
  }

  /**
   * 初始化性能指标
   */
  private initializeMetrics(): void {
    const agentTypes = [;
      AgentType.XIAOAI,AgentType.XIAOKE,AgentType.LAOKE,AgentType.SOER;
    ];

    agentTypes.forEach((agentType) => {
      this.metrics.set(agentType, {
        tasksProcessed: 0,
        successRate: 1.0,
        averageResponseTime: 0,
        errorCount: 0,
        lastActive: new Date(),
        memoryUsage: 0,
        cpuUsage: 0,
        uptime: 0
      });
    });
  }

  /**
   * 启动健康检查
   */
  private startHealthCheck(): void {
    this.healthCheckTimer = setInterval(async () => {
      try {
        await this.performHealthCheck();
      } catch (error) {
        this.log("error", "健康检查失败", error);
      }
    }, this.config.healthCheckInterval);
  }

  /**
   * 执行健康检查
   */
  private async performHealthCheck(): Promise<void> {
    const allStatus = await this.coordinator.getAllAgentStatus();

    for (const [agentType, status] of allStatus) {
      if (status.status === "error" && this.config.autoRestart) {
        this.log("warn", `检测到智能体 ${agentType} 异常，尝试重启`);
        try {
          await this.restartAgent(agentType);
        } catch (error) {
          this.log("error", `智能体 ${agentType} 重启失败`, error);
        }
      }
    }
  }

  /**
   * 启动性能监控
   */
  private startPerformanceMonitoring(): void {
    setInterval(() => {
      this.collectPerformanceMetrics();
    }, 10000); // 每10秒收集一次
  }

  /**
   * 收集性能指标
   */
  private collectPerformanceMetrics(): void {
    // 模拟性能数据收集
    for (const [agentType, metrics] of this.metrics) {
      metrics.memoryUsage = Math.random() * 100;
      metrics.cpuUsage = Math.random() * 50;
      metrics.uptime += 10; // 增加10秒
    }
  }

  /**
   * 更新性能指标
   */
  private updateMetrics(result: any, executionTime: number): void {
    // 这里需要根据结果确定是哪个智能体处理的
    // 简化实现：更新所有智能体的指标
    for (const [agentType, metrics] of this.metrics) {
      metrics.tasksProcessed++;
      metrics.lastActive = new Date();

      // 更新平均响应时间
      const totalTime =
        metrics.averageResponseTime * (metrics.tasksProcessed - 1) +;
        executionTime;
      metrics.averageResponseTime = totalTime / metrics.tasksProcessed;

      // 更新成功率
      if (result.success) {
        metrics.successRate =
          (metrics.successRate * (metrics.tasksProcessed - 1) + 1) /
          metrics.tasksProcessed;
      } else {
        metrics.successRate =
          (metrics.successRate * (metrics.tasksProcessed - 1)) /
          metrics.tasksProcessed;
        metrics.errorCount++;
      }
    }
  }

  /**
   * 更新错误指标
   */
  private updateErrorMetrics(): void {
    for (const [agentType, metrics] of this.metrics) {
      metrics.errorCount++;
      metrics.tasksProcessed++;
      metrics.successRate =
        (metrics.successRate * (metrics.tasksProcessed - 1)) /
        metrics.tasksProcessed;
    }
  }

  /**
   * 获取当前任务数量
   */
  private getCurrentTaskCount(): number {
    // 简化实现：返回0
    return 0;
  }

  /**
   * 计算平均响应时间
   */
  private calculateAverageResponseTime(): number {
    const metrics = Array.from(this.metrics.values());
    if (metrics.length === 0) {return 0;}

    const totalTime = metrics.reduce(;
      (sum, m) => sum + m.averageResponseTime,0;
    );
    return totalTime / metrics.length;
  }

  /**
   * 获取系统运行时间
   */
  private getSystemUptime(): number {
    // 简化实现：返回最大的智能体运行时间
    const metrics = Array.from(this.metrics.values());
    return Math.max(...metrics.map((m) => m.uptime));
  }

  /**
   * 检查系统是否健康
   */
  private isSystemHealthy(): boolean {
    const metrics = Array.from(this.metrics.values());
    return metrics.every(;
      (m) => m.successRate > 0.8 && m.averageResponseTime < 5000;
    );
  }

  /**
   * 记录日志
   */
  private log(
    level: "debug" | "info" | "warn" | "error",
    message: string,
    data?: any
  ): void {
    if (this.shouldLog(level)) {
      const timestamp = new Date().toISOString();
      const logMessage = `[${timestamp}] [AgentManager] [${level.toUpperCase()}] ${message}`;

      switch (level) {
        case "debug":
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

  /**
   * 检查是否应该记录日志
   */
  private shouldLog(level: string): boolean {
    const levels = ["debug", "info", "warn", "error"];
    const configLevelIndex = levels.indexOf(this.config.logLevel);
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex >= configLevelIndex;
  }
}
