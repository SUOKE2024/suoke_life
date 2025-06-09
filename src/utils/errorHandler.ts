import React from 'react';
import { Alert } from 'react-native';
import crashlytics from '@react-native-firebase/crashlytics';
// 错误类型枚举
export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTHENTICATION = 'AUTHENTICATION',
  VALIDATION = 'VALIDATION',
  PERMISSION = 'PERMISSION',
  AGENT_SERVICE = 'AGENT_SERVICE',
  DATA_PROCESSING = 'DATA_PROCESSING',
  UI_RENDERING = 'UI_RENDERING',
  UNKNOWN = 'UNKNOWN'
}
// 错误严重程度
export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}
// 错误接口
export interface AppError {
  id: string;,
  type: ErrorType;
  severity: ErrorSeverity;,
  message: string;
  details?: any;
  timestamp: number;
  userId?: string;
  sessionId?: string;
  stackTrace?: string;
  context?: Record<string, any>;
  resolved?: boolean;
}
// 错误处理配置
interface ErrorHandlerConfig {
  enableCrashlytics: boolean;,
  enableLocalLogging: boolean;
  enableUserNotification: boolean;,
  maxErrorsInMemory: number;
  autoReportThreshold: ErrorSeverity;
}
// 默认配置
const defaultConfig: ErrorHandlerConfig = {,
  enableCrashlytics: true,
  enableLocalLogging: true,
  enableUserNotification: true,
  maxErrorsInMemory: 100,
  autoReportThreshold: ErrorSeverity.HIGH};
// 错误处理器类
export class ErrorHandler {
  private static instance: ErrorHandler;
  private config: ErrorHandlerConfig;
  private errorQueue: AppError[] = [];
  private errorListeners: Set<(error: AppError) => void> = new Set();
  private constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
    this.setupGlobalErrorHandlers();
  }
  // 获取单例实例
  public static getInstance(config?: Partial<ErrorHandlerConfig>): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler(config);
    }
    return ErrorHandler.instance;
  }
  // 设置全局错误处理器
  private setupGlobalErrorHandlers(): void {
    // 处理未捕获的Promise拒绝
    const originalHandler = global.onunhandledrejection;
    global.onunhandledrejection = (event) => {
      this.handleError({
        type: ErrorType.UNKNOWN,
        severity: ErrorSeverity.HIGH,
        message: 'Unhandled Promise Rejection',
        details: event.reason,
        stackTrace: event.reason?.stack});
      if (originalHandler) {
        originalHandler(event);
      }
    };
    // 处理JavaScript错误
    const originalErrorHandler = global.ErrorUtils?.getGlobalHandler();
    global.ErrorUtils?.setGlobalHandler(error, isFatal) => {
      this.handleError({
        type: ErrorType.UNKNOWN,
        severity: isFatal ? ErrorSeverity.CRITICAL : ErrorSeverity.HIGH,
        message: error.message || 'JavaScript Error',
        details: error,
        stackTrace: error.stack});
      if (originalErrorHandler) {
        originalErrorHandler(error, isFatal);
      }
    });
  }
  // 处理错误
  public handleError(errorInput: Partial<AppError> & { type: ErrorType; message: string }): AppError {
    const error: AppError = {,
  id: this.generateErrorId(),
      severity: ErrorSeverity.MEDIUM,
      timestamp: Date.now(),
      resolved: false,
      ...errorInput};
    // 添加到错误队列
    this.addToErrorQueue(error);
    // 记录错误
    this.logError(error);
    // 上报错误
    this.reportError(error);
    // 通知监听器
    this.notifyListeners(error);
    // 显示用户通知
    this.showUserNotification(error);
    return error;
  }
  // 处理网络错误
  public handleNetworkError(error: any, context?: Record<string, any>): AppError {
    let message = '网络连接失败';
    let severity = ErrorSeverity.MEDIUM;
    if (error.code === 'NETWORK_ERROR') {
      message = '网络不可用，请检查网络连接';
      severity = ErrorSeverity.HIGH;
    } else if (error.status === 401) {
      message = '身份验证失败，请重新登录';
      severity = ErrorSeverity.HIGH;
    } else if (error.status === 403) {
      message = '权限不足，无法访问该资源';
      severity = ErrorSeverity.MEDIUM;
    } else if (error.status === 404) {
      message = '请求的资源不存在';
      severity = ErrorSeverity.LOW;
    } else if (error.status >= 500) {
      message = '服务器内部错误，请稍后重试';
      severity = ErrorSeverity.HIGH;
    }
    return this.handleError({
      type: ErrorType.NETWORK,
      severity,
      message,
      details: {,
  status: error.status,
        statusText: error.statusText,
        url: error.config?.url,
        method: error.config?.method},
      context});
  }
  // 处理智能体服务错误
  public handleAgentServiceError(error: any, agentId?: string, context?: Record<string, any>): AppError {
    let message = '智能体服务异常';
    let severity = ErrorSeverity.MEDIUM;
    if (error.message?.includes('offline')) {
      message = `智能体${agentId ? ` ${agentId}` : ''} 当前离线`;
      severity = ErrorSeverity.LOW;
    } else if (error.message?.includes('busy')) {
      message = `智能体${agentId ? ` ${agentId}` : ''} 当前忙碌`;
      severity = ErrorSeverity.LOW;
    } else if (error.message?.includes('timeout')) {
      message = '智能体响应超时，请稍后重试';
      severity = ErrorSeverity.MEDIUM;
    } else if (error.message?.includes('not found')) {
      message = '智能体不存在或已被删除';
      severity = ErrorSeverity.HIGH;
    }
    return this.handleError({
      type: ErrorType.AGENT_SERVICE,
      severity,
      message,
      details: { agentId, originalError: error },
      context});
  }
  // 处理验证错误
  public handleValidationError(field: string, value: any, rule: string): AppError {
    return this.handleError({
      type: ErrorType.VALIDATION,
      severity: ErrorSeverity.LOW,
      message: `字段 ${field} 验证失败`,
      details: { field, value, rule }});
  }
  // 处理权限错误
  public handlePermissionError(permission: string, context?: Record<string, any>): AppError {
    return this.handleError({
      type: ErrorType.PERMISSION,
      severity: ErrorSeverity.MEDIUM,
      message: `缺少权限: ${permission}`,
      details: { permission },
      context});
  }
  // 添加错误监听器
  public addErrorListener(listener: (error: AppError) => void): () => void {
    this.errorListeners.add(listener);
    return () => {
      this.errorListeners.delete(listener);
    };
  }
  // 获取错误历史
  public getErrorHistory(): AppError[] {
    return [...this.errorQueue];
  }
  // 获取特定类型的错误
  public getErrorsByType(type: ErrorType): AppError[] {
    return this.errorQueue.filter(error => error.type === type);
  }
  // 获取未解决的错误
  public getUnresolvedErrors(): AppError[] {
    return this.errorQueue.filter(error => !error.resolved);
  }
  // 标记错误为已解决
  public resolveError(errorId: string): void {
    const error = this.errorQueue.find(e => e.id === errorId);
    if (error) {
      error.resolved = true;
    }
  }
  // 清除错误历史
  public clearErrorHistory(): void {
    this.errorQueue = [];
  }
  // 生成错误ID;
  private generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  // 添加到错误队列
  private addToErrorQueue(error: AppError): void {
    this.errorQueue.push(error);
    // 保持队列大小限制
    if (this.errorQueue.length > this.config.maxErrorsInMemory) {
      this.errorQueue.shift();
    }
  }
  // 记录错误
  private logError(error: AppError): void {
    if (!this.config.enableLocalLogging) return;
    const logLevel = this.getLogLevel(error.severity);
    const logMessage = `[${error.type}] ${error.message}`;
    console[logLevel](logMessage, {
      id: error.id,
      severity: error.severity,
      timestamp: new Date(error.timestamp).toISOString(),
      details: error.details,
      context: error.context});
  }
  // 上报错误
  private reportError(error: AppError): void {
    if (!this.config.enableCrashlytics) return;
    if (error.severity < this.config.autoReportThreshold) return;
    try {
      // 上报到Crashlytics;
      crashlytics().recordError(new Error(error.message), {
        errorId: error.id,
        errorType: error.type,
        severity: error.severity,
        timestamp: error.timestamp,
        details: JSON.stringify(error.details),
        context: JSON.stringify(error.context)});
      // 设置自定义属性
      crashlytics().setAttributes({
        errorType: error.type,
        severity: error.severity,
        userId: error.userId || 'unknown',
        sessionId: error.sessionId || 'unknown'});
    } catch (reportError) {
      console.warn('Failed to report error to Crashlytics:', reportError);
    }
  }
  // 通知监听器
  private notifyListeners(error: AppError): void {
    this.errorListeners.forEach(listener => {
      try {
        listener(error);
      } catch (listenerError) {
        console.warn('Error listener failed:', listenerError);
      }
    });
  }
  // 显示用户通知
  private showUserNotification(error: AppError): void {
    if (!this.config.enableUserNotification) return;
    if (error.severity < ErrorSeverity.MEDIUM) return;
    const title = this.getErrorTitle(error.type);
    const message = this.getUserFriendlyMessage(error);
    Alert.alert()
      title,
      message,
      [
        {
      text: "确定",
      style: 'default'},
        ...(error.severity >= ErrorSeverity.HIGH ? [{
      text: "反馈问题",
      style: 'default',
          onPress: () => this.openFeedback(error)}] : [])],
    );
  }
  // 获取日志级别
  private getLogLevel(severity: ErrorSeverity): 'log' | 'warn' | 'error' {
    switch (severity) {
      case ErrorSeverity.LOW:
        return 'log';
      case ErrorSeverity.MEDIUM:
        return 'warn';
      case ErrorSeverity.HIGH:
      case ErrorSeverity.CRITICAL:
        return 'error',
  default:
        return 'log';
    }
  }
  // 获取错误标题
  private getErrorTitle(type: ErrorType): string {
    switch (type) {
      case ErrorType.NETWORK:
        return '网络错误';
      case ErrorType.AUTHENTICATION:
        return '身份验证错误';
      case ErrorType.VALIDATION:
        return '输入验证错误';
      case ErrorType.PERMISSION:
        return '权限错误';
      case ErrorType.AGENT_SERVICE:
        return '智能体服务错误';
      case ErrorType.DATA_PROCESSING:
        return '数据处理错误';
      case ErrorType.UI_RENDERING:
        return '界面渲染错误',
  default:
        return '系统错误';
    }
  }
  // 获取用户友好的错误消息
  private getUserFriendlyMessage(error: AppError): string {
    // 如果已经是用户友好的消息，直接返回
    if (this.isUserFriendlyMessage(error.message)) {
      return error.message;
    }
    // 根据错误类型返回通用消息
    switch (error.type) {
      case ErrorType.NETWORK:
        return '网络连接出现问题，请检查网络设置后重试。';
      case ErrorType.AUTHENTICATION:
        return '身份验证失败，请重新登录。';
      case ErrorType.AGENT_SERVICE:
        return '智能体服务暂时不可用，请稍后重试。';
      case ErrorType.DATA_PROCESSING:
        return '数据处理出现问题，请稍后重试。',
  default:
        return '系统出现异常，我们正在努力修复。';
    }
  }
  // 检查是否为用户友好的消息
  private isUserFriendlyMessage(message: string): boolean {
    // 简单的启发式检查
    return !message.includes('Error:') &&
          !message.includes('Exception:') &&
          !message.includes('undefined') &&
          !message.includes('null') &&
          message.length < 100;
  }
  // 打开反馈页面
  private openFeedback(error: AppError): void {
    // TODO: 实现反馈功能
    console.log('Opening feedback for error:', error.id);
  }
  // 更新配置
  public updateConfig(newConfig: Partial<ErrorHandlerConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }
  // 获取错误统计
  public getErrorStats(): {
    total: number,
  byType: Record<ErrorType, number>;
    bySeverity: Record<ErrorSeverity, number>;
    resolved: number,
  unresolved: number;
  } {
    const stats = {
      total: this.errorQueue.length,
      byType: {} as Record<ErrorType, number>,
      bySeverity: {} as Record<ErrorSeverity, number>,
      resolved: 0,
      unresolved: 0};
    // 初始化计数器
    Object.values(ErrorType).forEach(type => {
      stats.byType[type] = 0;
    });
    Object.values(ErrorSeverity).forEach(severity => {
      stats.bySeverity[severity] = 0;
    });
    // 统计错误
    this.errorQueue.forEach(error => {
      stats.byType[error.type]++;
      stats.bySeverity[error.severity]++;
      if (error.resolved) {
        stats.resolved++;
      } else {
        stats.unresolved++;
      }
    });
    return stats;
  }
}
// 创建全局错误处理器实例
export const errorHandler = ErrorHandler.getInstance();
// 便捷函数
export const handleError = (error: Partial<AppError> & { type: ErrorType; message: string }) =>
  errorHandler.handleError(error);
export const handleNetworkError = (error: any, context?: Record<string, any>) =>
  errorHandler.handleNetworkError(error, context);
export const handleAgentServiceError = (error: any, agentId?: string, context?: Record<string, any>) =>
  errorHandler.handleAgentServiceError(error, agentId, context);
export const handleValidationError = (field: string, value: any, rule: string) =>
  errorHandler.handleValidationError(field, value, rule);
export const handlePermissionError = (permission: string, context?: Record<string, any>) =>
  errorHandler.handlePermissionError(permission, context);
// React Hook for error handling;
export const useErrorHandler = () => {
  return {
    handleError,
    handleNetworkError,
    handleAgentServiceError,
    handleValidationError,
    handlePermissionError,
    getErrorHistory: () => errorHandler.getErrorHistory(),
    getErrorStats: () => errorHandler.getErrorStats(),
    addErrorListener: (listener: (error: AppError) => void) => errorHandler.addErrorListener(listener),
    resolveError: (errorId: string) => errorHandler.resolveError(errorId),
    clearErrorHistory: () => errorHandler.clearErrorHistory()};
};
export default errorHandler;