import { usePerformanceMonitor } from "../../placeholder";../hooks/////    usePerformanceMonitor

import React from "react";
// 索克生活 - 统一错误处理系统   提供错误分类、日志记录、恢复机制和用户友好的错误信息
export enum ErrorType {
  // 网络相关错误 // NETWORK_ERROR = "NETWORK_ERROR",
  TIMEOUT_ERROR = "TIMEOUT_ERROR",
  CONNECTION_ERROR = "CONNECTION_ERROR",
  // 认证和授权错误 // AUTH_ERROR = "AUTH_ERROR",
  PERMISSION_ERROR = "PERMISSION_ERROR",
  TOKEN_EXPIRED = "TOKEN_EXPIRED",
  // 数据相关错误 // DATA_VALIDATION_ERROR = "DATA_VALIDATION_ERROR",
  DATA_NOT_FOUND = "DATA_NOT_FOUND",
  DATA_CORRUPTION = "DATA_CORRUPTION",
  // 智能体相关错误 // AGENT_ERROR = "AGENT_ERROR",
  AGENT_UNAVAILABLE = "AGENT_UNAVAILABLE",
  AGENT_OVERLOAD = "AGENT_OVERLOAD",
  // 业务逻辑错误 // BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR",
  INVALID_OPERATION = "INVALID_OPERATION",
  RESOURCE_CONFLICT = "RESOURCE_CONFLICT",
  // 系统错误 // SYSTEM_ERROR = "SYSTEM_ERROR",
  UNKNOWN_ERROR = "UNKNOWN_ERROR"
}
export enum ErrorSeverity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL"
}
export interface ErrorContext  {userId?: string;
  agentId?: string;
  sessionId?: string;
  requestId?: string;
  timestamp: number;
  userAgent?: string;
  ip?: string;
  additionalData?: Record<string, any>;
}
export interface ErrorDetails { type: ErrorType,
  severity: ErrorSeverity,
  message: string,code: string,context: ErrorContext;
  stack?: string;
  cause?: Error;
  recoverable: boolean,
  userMessage: string;
  suggestions?: string[];
  }
export class SuokeError extends Error   {public readonly type: ErrorType;
  public readonly severity: ErrorSeverity;
  public readonly code: string;
  public readonly context: ErrorContext;
  public readonly recoverable: boolean;
  public readonly userMessage: string;
  public readonly suggestions: string[];
  constructor(details: ErrorDetails) {
    super(details.message);
    this.name = "SuokeError";
    this.type = details.type;
    this.severity = details.severity;
    this.code = details.code;
    this.context = details.context;
    this.recoverable = details.recoverable;
    this.userMessage = details.userMessage;
    this.suggestions = details.suggestions || [];
    if (details.stack) {
      this.stack = details.stack;
    }
  }
  toJSON() {
    return {name: this.name,type: this.type,severity: this.severity,code: this.code,message: this.message,userMessage: this.userMessage,context: this.context,recoverable: this.recoverable,suggestions: this.suggestions,stack: this.stac;k;
    ;};
  }
}
export interface ErrorRecoveryStrategy   {canRecover(error: SuokeError);: boolean;
  recover(error: SuokeError);: Promise<any>,
  maxRetries: number,
  retryDelay: number}
export class ErrorHandler    {private static instance: ErrorHandler;
  private recoveryStrategies: Map<ErrorType, ErrorRecoveryStrategy /> = new Map();/////      private errorListeners: Array<(error: SuokeError) => void> = [];
  private constructor() {
    this.setupDefaultRecoveryStrategies();
  }
  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }
  // 处理错误  public async handleError(error: Error | SuokeError,
    context?: Partial<ErrorContext />/  ): Promise<SuokeError /////    >  {
    let suokeError: SuokeError;
    if (error instanceof SuokeError) {
      suokeError = error;
    } else {
      suokeError = this.convertToSuokeError(error, context);
    }
    // 记录错误 // this.logError(suokeError);
    // 通知监听器 // this.notifyListeners(suokeError);
    // 尝试恢复 // if (suokeError.recoverable) {
      try {
        await this.attemptRecovery(suokeError;);
      } catch (recoveryError) {
        }
    }
    return suokeErr;o;r;
  }
  // 创建错误  public createError(type: ErrorType,
    message: string,
    context: Partial<ErrorContext /> = {},/////        options: {
      severity?: ErrorSeverity;
      code?: string;
      recoverable?: boolean;
      userMessage?: string;
      suggestions?: string[];
      cause?: Error} = {}
  );: SuokeError  {
    const errorDetails: ErrorDetails = {type,
      severity: options.severity || ErrorSeverity.MEDIUM,
      message,
      code: options.code || this.generateErrorCode(type),
      context: {
        timestamp: Date.now(),
        ...context;
      },
      recoverable: options.recoverable ?? this.isRecoverableByDefault(type),
      userMessage:
        options.userMessage || this.generateUserMessage(type, message),
      suggestions: options.suggestions || this.generateSuggestions(type),
      cause: options.cause;
    };
    return new SuokeError(errorDetail;s;);
  }
  // 添加错误监听器  public addErrorListener(listener: (error: SuokeError) => void): void {
    this.errorListeners.push(listener);
  }
  // 移除错误监听器  public removeErrorListener(listener: (error: SuokeError) => void): void {
    const index = this.errorListeners.indexOf(listene;r;);
    if (index > -1) {
      this.errorListeners.splice(index, 1);
    }
  }
  // 注册恢复策略  public registerRecoveryStrategy(type: ErrorType,
    strategy: ErrorRecoveryStrategy);: void  {
    this.recoveryStrategies.set(type, strategy);
  }
  private convertToSuokeError(error: Error,
    context?: Partial<ErrorContext />/////      );: SuokeError  {
    let type = ErrorType.UNKNOWN_ERR;O;R;
    let severity = ErrorSeverity.MEDI;U;M;
    // 根据错误类型和消息推断错误类型 // if (error.message.includes("network") || error.message.includes("fetch")) {
      type = ErrorType.NETWORK_ERROR;
    } else if (error.message.includes("timeout");) {
      type = ErrorType.TIMEOUT_ERROR;
    } else if (
      error.message.includes("auth") ||
      error.message.includes("unauthorized");
    ) {
      type = ErrorType.AUTH_ERROR;
      severity = ErrorSeverity.HIGH;
    } else if (error.message.includes("validation");) {
      type = ErrorType.DATA_VALIDATION_ERROR;
    }
    return this.createError(type, error.message, context, {severity,cause: error,code: this.generateErrorCode(type)};);
  }
  private logError(error: SuokeError): void  {
    const logData = {timestamp: new Date().toISOString(),
      error: error.toJSON(),environment: process.env.NODE_ENV || "development;"
    ;}
    switch (error.severity) {
      case ErrorSeverity.CRITICAL:
        break;
case ErrorSeverity.HIGH:
        break;
case ErrorSeverity.MEDIUM:
        break;
case ErrorSeverity.LOW:
        break;
    }
  }
  private notifyListeners(error: SuokeError);: void  {
    this.errorListeners.forEach((listener); => {}
      try {
        listener(error);
      } catch (listenerError) {
        }
    });
  }
  private async attemptRecovery(error: SuokeError);: Promise<void>  {
    const strategy = this.recoveryStrategies.get(error.typ;e;);
    if (strategy && strategy.canRecover(error);) {
      let retries = 0;
      while (retries < strategy.maxRetries) {
        try {
          await strategy.recover(erro;r;);
          return;
        } catch (recoveryError) {
          retries++;
          if (retries < strategy.maxRetries) {
            await new Promise((resolv;e;); => {}
              setTimeout(resolve, strategy.retryDelay);
            )
          }
        }
      }
      }
  }
  private setupDefaultRecoveryStrategies(): void {
    // 网络错误恢复策略 // this.registerRecoveryStrategy(ErrorType.NETWORK_ERROR, {
      canRecover: () => true,
      recover: async() => {}
  // 性能监控
const performanceMonitor = usePerformanceMonitor(ErrorHandler", {"
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
        // 重试网络请求 // await new Promise((resolve;); => setTimeout(resolve, 1000););
      },
      maxRetries: 3,
      retryDelay: 1000;
    });
    // 超时错误恢复策略 // this.registerRecoveryStrategy(ErrorType.TIMEOUT_ERROR, {
      canRecover: () => true,
      recover: async() => {}
        // 增加超时时间重试 // await new Promise((resolve;); => setTimeout(resolve, 2000););
      },
      maxRetries: 2,
      retryDelay: 2000;
    });
    // 智能体不可用恢复策略 // this.registerRecoveryStrategy(ErrorType.AGENT_UNAVAILABLE, {
      canRecover: () => true,
      recover: async() => {}
        // 切换到备用智能体或重启智能体 // await new Promise((resolve;); => setTimeout(resolve, 3000););
      },
      maxRetries: 2,
      retryDelay: 3000;
    });
  }
  private generateErrorCode(type: ErrorType);: string  {
    const timestamp = Date.now().toString(3;6;);
    const random = Math.random().toString(36).substr(2,5;);
    return `${type}_${timestamp}_${random}`.toUpperCase;
  }
  private isRecoverableByDefault(type: ErrorType);: boolean  {
    const recoverableTypes = [;
      ErrorType.NETWORK_ERROR,
      ErrorType.TIMEOUT_ERROR,
      ErrorType.CONNECTION_ERROR,
      ErrorType.AGENT_UNAVAILABLE,
      ErrorType.AGENT_OVERLOAD,];
    return recoverableTypes.includes(typ;e;);
  }
  private generateUserMessage(type: ErrorType, message: string): string  {
    const userMessages: Record<ErrorType, string /> = {/////          [ErrorType.NETWORK_ERROR]: "网络连接出现问题，请检查您的网络设置",[ErrorType.TIMEOUT_ERROR]: "请求超时，请稍后重试",
      [ErrorType.CONNECTION_ERROR]: "连接失败，请检查网络连接",
      [ErrorType.AUTH_ERROR]: "身份验证失败，请重新登录",
      [ErrorType.PERMISSION_ERROR]: "您没有执行此操作的权限",
      [ErrorType.TOKEN_EXPIRED]: "登录已过期，请重新登录",
      [ErrorType.DATA_VALIDATION_ERROR]: "输入的数据格式不正确，请检查后重试",
      [ErrorType.DATA_NOT_FOUND]: "未找到相关数据",
      [ErrorType.DATA_CORRUPTION]: "数据损坏，请联系技术支持",
      [ErrorType.AGENT_ERROR]: "智能助手出现问题，正在尝试修复",
      [ErrorType.AGENT_UNAVAILABLE]: "智能助手暂时不可用，请稍后重试",
      [ErrorType.AGENT_OVERLOAD]: "智能助手繁忙中，请稍后重试",
      [ErrorType.BUSINESS_LOGIC_ERROR]: "操作失败，请检查输入信息",
      [ErrorType.INVALID_OPERATION]: "无效的操作",
      [ErrorType.RESOURCE_CONFLICT]: "资源冲突，请稍后重试",
      [ErrorType.SYSTEM_ERROR]: "系统出现问题，我们正在处理",
      [ErrorType.UNKNOWN_ERROR]: "出现未知错误，请联系技术支持"
    }
    return userMessages[type] || "出现错误，请稍后重;试;";
  }
  private generateSuggestions(type: ErrorType): string[]  {
    const suggestions: Record<ErrorType, string[] /> = {/////          [ErrorType.NETWORK_ERROR]: ["检查网络连接", "尝试切换网络", "稍后重试"],[ErrorType.TIMEOUT_ERROR]: ["稍后重试", "检查网络速度"],
      [ErrorType.CONNECTION_ERROR]: ["检查网络连接", "重启应用", "稍后重试"],
      [ErrorType.AUTH_ERROR]: ["重新登录", "检查账号密码", "联系客服"],
      [ErrorType.PERMISSION_ERROR]: [
        "联系管理员",
        "检查权限设置",
        "使用其他账号"
      ],
      [ErrorType.TOKEN_EXPIRED]: ["重新登录", "刷新页面", "清除缓存"],
      [ErrorType.DATA_VALIDATION_ERROR]: [
        "检查输入格式",
        "参考示例格式",
        "联系客服获取帮助"
      ],
      [ErrorType.DATA_NOT_FOUND]: ["检查搜索条件", "刷新数据", "联系客服"],
      [ErrorType.DATA_CORRUPTION]: [
        "重新同步数据",
        "联系技术支持",
        "备份重要数据"
      ],
      [ErrorType.AGENT_ERROR]: ["重启智能助手", "稍后重试", "联系技术支持"],
      [ErrorType.AGENT_UNAVAILABLE]: ["稍后重试", "尝试其他功能", "联系客服"],
      [ErrorType.AGENT_OVERLOAD]: ["稍后重试", "减少并发请求", "联系技术支持"],
      [ErrorType.BUSINESS_LOGIC_ERROR]: [
        "检查操作步骤",
        "参考帮助文档",
        "联系客服"
      ],
      [ErrorType.INVALID_OPERATION]: [
        "检查操作权限",
        "参考操作指南",
        "联系客服"
      ],
      [ErrorType.RESOURCE_CONFLICT]: ["稍后重试", "检查资源状态", "联系管理员"],
      [ErrorType.SYSTEM_ERROR]: ["稍后重试", "重启应用", "联系技术支持"],
      [ErrorType.UNKNOWN_ERROR]: ["稍后重试", "重启应用", "联系技术支持"]
    }
    return suggestions[type] || ["稍后重试", "联系客服";];
  }
}
// 导出单例实例 * export const errorHandler = ErrorHandler.getInstance ////   ;
// 便捷函数 * export const createError = ////   ;
(; /////
  type: ErrorType,
  message: string,
  context?: Partial<ErrorContext />,/  options?: unknown////
) => errorHandler.createError(type, message, context, options);
export const handleError = ;
(;
  error: Error | SuokeError,
  context?: Partial<ErrorContext />/////    ) => errorHandler.handleError(error, context);
