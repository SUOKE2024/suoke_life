import {
  Agent,
  AgentCapability,
  AgentStatus,
  AgentMetrics,
  AgentTask,
} from "../types";

/**
 * 基础智能体抽象类
 * 提供所有智能体的通用功能和接口
 */
export abstract class BaseAgent implements Agent {
  protected id: string;
  protected name: string;
  protected description: string;
  protected capabilities: string[];
  protected status: AgentStatus;
  protected config: any;
  protected context: any = {};

  // 性能指标
  protected tasksProcessed: number = 0;
  protected successfulTasks: number = 0;
  protected totalResponseTime: number = 0;
  protected lastActive: Date = new Date();

  constructor(params: {
    id: string;
    name: string;
    description: string;
    capabilities: string[];
    status: AgentStatus;
    config?: any;
  }) {
    this.id = params.id;
    this.name = params.name;
    this.description = params.description;
    this.capabilities = params.capabilities;
    this.status = params.status;
    this.config = params.config || {};
  }

  // 抽象方法，子类必须实现
  abstract processTask(task: AgentTask): Promise<any>;
  abstract getCapabilities(): AgentCapability[];
  abstract getStatus(): AgentStatus;
  abstract getMetrics(): AgentMetrics;

  // 通用方法
  getId(): string {
    return this.id;
  }

  getName(): string {
    return this.name;
  }

  getDescription(): string {
    return this.description;
  }

  updateStatus(status: AgentStatus): void {
    this.status = status;
    this.lastActive = new Date();
  }

  async initialize(): Promise<void> {
    console.log(`初始化智能体: ${this.name}`);
    this.status = "idle";
  }

  async shutdown(): Promise<void> {
    console.log(`关闭智能体: ${this.name}`);
    this.status = "offline";
  }

  // 性能追踪
  protected trackTaskStart(): number {
    return Date.now();
  }

  protected trackTaskEnd(startTime: number, success: boolean): void {
    const responseTime = Date.now() - startTime;
    this.tasksProcessed++;
    this.totalResponseTime += responseTime;

    if (success) {
      this.successfulTasks++;
    }

    this.lastActive = new Date();
  }

  // 错误处理
  protected handleError(error: Error, task: AgentTask): void {
    console.error(`智能体 ${this.name} 处理任务 ${task.taskId} 时出错:`, error);
  }

  // 上下文管理
  getContext(): any {
    return this.context;
  }

  setContext(context: any): void {
    this.context = { ...this.context, ...context };
  }

  clearContext(): void {
    this.context = {};
  }
}
