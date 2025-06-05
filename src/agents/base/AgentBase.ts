import {
  AgentType,
  AgentCapability,
  AgentResponse,
  AgentContext,
} from "../types";

/**
 * 智能体基础抽象类
 * 为所有智能体提供统一的基础功能和接口
 */
export abstract class AgentBase {
  protected agentType: AgentType;
  protected name: string;
  protected description: string;
  protected capabilities: AgentCapability[];
  protected isInitialized: boolean = false;
  protected version: string = "1.0.0";

  constructor() {
    this.agentType = AgentType.XIAOAI; // 默认值，子类会覆盖
    this.name = "";
    this.description = "";
    this.capabilities = [];
  }

  /**
   * 初始化智能体
   */
  abstract initialize(): Promise<void>;

  /**
   * 处理用户消息
   */
  abstract processMessage(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse>;

  /**
   * 获取智能体健康状态
   */
  abstract getHealthStatus(): Promise<any>;

  /**
   * 关闭智能体
   */
  abstract shutdown(): Promise<void>;

  /**
   * 获取智能体名称
   */
  getName(): string {
    return this.name;
  }

  /**
   * 获取智能体描述
   */
  getDescription(): string {
    return this.description;
  }

  /**
   * 获取智能体能力列表
   */
  getCapabilities(): AgentCapability[] {
    return [...this.capabilities];
  }

  /**
   * 获取智能体类型
   */
  getAgentType(): AgentType {
    return this.agentType;
  }

  /**
   * 检查是否已初始化
   */
  isReady(): boolean {
    return this.isInitialized;
  }

  /**
   * 获取版本信息
   */
  getVersion(): string {
    return this.version;
  }

  /**
   * 检查是否支持特定能力
   */
  hasCapability(capability: AgentCapability): boolean {
    return this.capabilities.includes(capability);
  }

  /**
   * 验证上下文
   */
  protected validateContext(context: AgentContext): boolean {
    return context && typeof context.userId === "string";
  }

  /**
   * 生成响应ID
   */
  protected generateResponseId(): string {
    return `${this.agentType}_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
  }

  /**
   * 记录日志
   */
  protected log(
    level: "info" | "warn" | "error",
    message: string,
    data?: any
  ): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${
      this.agentType
    }] [${level.toUpperCase()}] ${message}`;

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

  /**
   * 创建标准错误响应
   */
  protected createErrorResponse(
    message: string,
    error?: any,
    context?: AgentContext
  ): AgentResponse {
    return {
      success: false,
      response: message,
      error: error?.message || error,
      context: context || { userId: "unknown" },
      metadata: {
        agentType: this.agentType,
        timestamp: new Date().toISOString(),
        responseId: this.generateResponseId(),
      },
    };
  }

  /**
   * 创建标准成功响应
   */
  protected createSuccessResponse(
    message: string,
    data?: any,
    context?: AgentContext,
    metadata?: any
  ): AgentResponse {
    return {
      success: true,
      response: message,
      data,
      context: context || { userId: "unknown" },
      metadata: {
        agentType: this.agentType,
        timestamp: new Date().toISOString(),
        responseId: this.generateResponseId(),
        ...metadata,
      },
    };
  }
}
