/**
* 全局错误处理器
* 统一处理应用中的所有错误
*/
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  API_ERROR = 'API_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  BUSINESS_LOGIC_ERROR = 'BUSINESS_LOGIC_ERROR',
  SYSTEM_ERROR = 'SYSTEM_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}
export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}
export interface ErrorInfo {
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  code?: string;
  details?: any;
  timestamp: number;
  userId?: string;
  sessionId?: string;
  stackTrace?: string;
}
export interface ErrorHandlerConfig {
  enableLogging: boolean;
  enableReporting: boolean;
  enableUserNotification: boolean;
  reportingEndpoint?: string;
  maxRetries: number;
  retryDelay: number;
}
export class GlobalErrorHandler {
  private static instance: GlobalErrorHandler;
  private config: ErrorHandlerConfig;
  private errorQueue: ErrorInfo[] = [];
  private constructor(config: ErrorHandlerConfig) {
    this.config = config;
    this.setupGlobalHandlers();
  }
  public static getInstance(config?: ErrorHandlerConfig): GlobalErrorHandler {
    if (!GlobalErrorHandler.instance) {
      const defaultConfig: ErrorHandlerConfig = {,
  enableLogging: true,
        enableReporting: true,
        enableUserNotification: true,
        maxRetries: 3,
        retryDelay: 1000,
      };
      GlobalErrorHandler.instance = new GlobalErrorHandler(config || defaultConfig);
    }
    return GlobalErrorHandler.instance;
  }
  /**
  * 处理错误
  */
  public handleError(error: Error | ErrorInfo, context?: any): void {
    const errorInfo = this.normalizeError(error, context);
    // 记录错误
    if (this.config.enableLogging) {
      this.logError(errorInfo);
    }
    // 上报错误
    if (this.config.enableReporting) {
      this.reportError(errorInfo);
    }
    // 用户通知
    if (this.config.enableUserNotification) {
      this.notifyUser(errorInfo);
    }
    // 添加到错误队列
    this.errorQueue.push(errorInfo);
    // 保持队列大小
    if (this.errorQueue.length > 100) {
      this.errorQueue.shift();
    }
  }
  /**
  * 处理网络错误
  */
  public handleNetworkError(error: Error, url?: string): void {
    this.handleError({
      type: ErrorType.NETWORK_ERROR,
      severity: ErrorSeverity.MEDIUM,
      message: `网络请求失败: ${error.message}`,
      details: { url, originalError: error.message },
      timestamp: Date.now(),
      stackTrace: error.stack,
    });
  }
  /**
  * 处理API错误
  */
  public handleApiError(status: number, message: string, endpoint?: string): void {
    const severity = status >= 500 ? ErrorSeverity.HIGH : ErrorSeverity.MEDIUM;
    this.handleError({
      type: ErrorType.API_ERROR,
      severity,
      message: `API错误 (${status}): ${message}`,
      code: status.toString(),
      details: { endpoint, status },
      timestamp: Date.now(),
    });
  }
  /**
  * 处理验证错误
  */
  public handleValidationError(field: string, message: string): void {
    this.handleError({
      type: ErrorType.VALIDATION_ERROR,
      severity: ErrorSeverity.LOW,
      message: `验证失败: ${field} - ${message}`,
      details: { field },
      timestamp: Date.now(),
    });
  }
  /**
  * 处理认证错误
  */
  public handleAuthError(message: string): void {
    this.handleError({
      type: ErrorType.AUTHENTICATION_ERROR,
      severity: ErrorSeverity.HIGH,
      message: `认证失败: ${message}`,
      timestamp: Date.now(),
    });
  }
  /**
  * 处理业务逻辑错误
  */
  public handleBusinessError(message: string, details?: any): void {
    this.handleError({
      type: ErrorType.BUSINESS_LOGIC_ERROR,
      severity: ErrorSeverity.MEDIUM,
      message,
      details,
      timestamp: Date.now(),
    });
  }
  /**
  * 获取错误统计
  */
  public getErrorStats(): {
    total: number,
  byType: Record<ErrorType, number>;
    bySeverity: Record<ErrorSeverity, number>;
    recent: ErrorInfo[];
  } {
    const byType = {} as Record<ErrorType, number>;
    const bySeverity = {} as Record<ErrorSeverity, number>;
    this.errorQueue.forEach(error => {
      byType[error.type] = (byType[error.type] || 0) + 1;
      bySeverity[error.severity] = (bySeverity[error.severity] || 0) + 1;
    });
    return {
      total: this.errorQueue.length,
      byType,
      bySeverity,
      recent: this.errorQueue.slice(-10),
    };
  }
  /**
  * 清除错误队列
  */
  public clearErrors(): void {
    this.errorQueue = [];
  }
  /**
  * 设置全局错误处理器
  */
  private setupGlobalHandlers(): void {
    // 处理未捕获的Promise拒绝
    if (typeof window !== 'undefined') {
      window.addEventListener('unhandledrejection', (event) => {
        this.handleError({
          type: ErrorType.SYSTEM_ERROR,
          severity: ErrorSeverity.HIGH,
          message: `未处理的Promise拒绝: ${event.reason}`,
          details: { reason: event.reason },
          timestamp: Date.now(),
        });
      });
      // 处理全局错误
      window.addEventListener('error', (event) => {
        this.handleError({
          type: ErrorType.SYSTEM_ERROR,
          severity: ErrorSeverity.HIGH,
          message: `全局错误: ${event.message}`,
          details: {,
  filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
          },
          timestamp: Date.now(),
          stackTrace: event.error?.stack,
        });
      });
    }
  }
  /**
  * 标准化错误对象
  */
  private normalizeError(error: Error | ErrorInfo, context?: any): ErrorInfo {
    if ('type' in error) {
      return error;
    }
    return {
      type: ErrorType.UNKNOWN_ERROR,
      severity: ErrorSeverity.MEDIUM,
      message: error.message || '未知错误',
      timestamp: Date.now(),
      stackTrace: error.stack,
      details: context,
    };
  }
  /**
  * 记录错误
  */
  private logError(error: ErrorInfo): void {
    const logLevel = this.getLogLevel(error.severity);
    const logMessage = `[${error.type}] ${error.message}`;
    console[logLevel](logMessage, {
      severity: error.severity,
      timestamp: new Date(error.timestamp).toISOString(),
      details: error.details,
      stackTrace: error.stackTrace,
    });
  }
  /**
  * 上报错误
  */
  private async reportError(error: ErrorInfo): Promise<void> {
    if (!this.config.reportingEndpoint) return;
    try {
      await fetch(this.config.reportingEndpoint, {
      method: "POST",
      headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(error),
      });
    } catch (reportingError) {
      console.error('错误上报失败:', reportingError);
    }
  }
  /**
  * 通知用户
  */
  private notifyUser(error: ErrorInfo): void {
    if (error.severity === ErrorSeverity.LOW) return;
    const userMessage = this.getUserFriendlyMessage(error);
    // 这里可以集成具体的通知机制（Toast、Modal等）
    console.warn('用户通知:', userMessage);
  }
  /**
  * 获取日志级别
  */
  private getLogLevel(severity: ErrorSeverity): 'error' | 'warn' | 'info' {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
      case ErrorSeverity.HIGH:
        return 'error';
      case ErrorSeverity.MEDIUM:
        return 'warn';
      case ErrorSeverity.LOW:
      default:
        return 'info';
    }
  }
  /**
  * 获取用户友好的错误消息
  */
  private getUserFriendlyMessage(error: ErrorInfo): string {
    switch (error.type) {
      case ErrorType.NETWORK_ERROR:
        return '网络连接异常，请检查网络设置';
      case ErrorType.API_ERROR:
        return '服务暂时不可用，请稍后重试';
      case ErrorType.AUTHENTICATION_ERROR:
        return '登录已过期，请重新登录';
      case ErrorType.AUTHORIZATION_ERROR:
        return '您没有权限执行此操作';
      case ErrorType.VALIDATION_ERROR:
        return '输入信息有误，请检查后重试';
      case ErrorType.BUSINESS_LOGIC_ERROR:
        return error.message,
  default:
        return '系统异常，请稍后重试';
    }
  }
}
// 导出单例实例
export const globalErrorHandler = GlobalErrorHandler.getInstance();
