import { ERROR_CODES } from '../constants/config';

// 错误类型定义
export interface AppError extends Error {
  code: string;
  status?: number;
  service?: string;
  requestId?: string;
  timestamp?: string;
  recoverable?: boolean;
  userMessage?: string;
  technicalMessage?: string;
}

// 错误恢复建议
export interface ErrorRecovery {
  action: 'retry' | 'refresh' | 'navigate' | 'contact_support' | 'wait';
  message: string;
  autoRetry?: boolean;
  retryDelay?: number;
  maxRetries?: number;
}

// 错误处理器类
export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorHistory: AppError[] = [];
  private maxHistorySize = 50;

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  // 处理错误并返回用户友好的信息
  handleError(error: any, context?: string): AppError {
    const appError = this.normalizeError(error, context);
    this.logError(appError);
    this.addToHistory(appError);
    return appError;
  }

  // 标准化错误对象
  private normalizeError(error: any, context?: string): AppError {
    const timestamp = new Date().toISOString();
    const requestId = this.generateRequestId();

    // 如果已经是AppError，直接返回
    if (error.code && error.userMessage) {
      return {
        ...error,
        timestamp,
        requestId,
      };
    }

    // 网络错误
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        name: 'NetworkError',
        message: error.message,
        code: ERROR_CODES.NETWORK_ERROR,
        userMessage: '网络连接失败，请检查网络设置',
        technicalMessage: error.message,
        recoverable: true,
        timestamp,
        requestId,
        service: context,
      };
    }

    // HTTP错误
    if (error.status) {
      return {
        name: 'HttpError',
        message: error.message || `HTTP ${error.status}`,
        code: this.mapHttpStatusToErrorCode(error.status),
        status: error.status,
        userMessage: this.getHttpErrorMessage(error.status),
        technicalMessage: error.message,
        recoverable: this.isHttpErrorRecoverable(error.status),
        timestamp,
        requestId,
        service: context,
      };
    }

    // 超时错误
    if (error.name === 'AbortError' || error.message.includes('timeout')) {
      return {
        name: 'TimeoutError',
        message: error.message,
        code: ERROR_CODES.TIMEOUT,
        userMessage: '请求超时，请稍后重试',
        technicalMessage: error.message,
        recoverable: true,
        timestamp,
        requestId,
        service: context,
      };
    }

    // 通用错误
    return {
      name: error.name || 'UnknownError',
      message: error.message || '未知错误',
      code: ERROR_CODES.OPERATION_FAILED,
      userMessage: '操作失败，请稍后重试',
      technicalMessage: error.message || error.toString(),
      recoverable: true,
      timestamp,
      requestId,
      service: context,
    };
  }

  // 映射HTTP状态码到错误代码
  private mapHttpStatusToErrorCode(status: number): string {
    switch (status) {
      case 400: return ERROR_CODES.VALIDATION_ERROR;
      case 401: return ERROR_CODES.UNAUTHORIZED;
      case 403: return ERROR_CODES.FORBIDDEN;
      case 404: return ERROR_CODES.NOT_FOUND;
      case 408: return ERROR_CODES.TIMEOUT;
      case 500: return ERROR_CODES.SERVER_ERROR;
      case 502:
      case 503:
      case 504: return ERROR_CODES.SERVICE_UNAVAILABLE;
      default: return ERROR_CODES.OPERATION_FAILED;
    }
  }

  // 获取HTTP错误的用户友好信息
  private getHttpErrorMessage(status: number): string {
    switch (status) {
      case 400: return '请求参数有误，请检查输入信息';
      case 401: return '身份验证失败，请重新登录';
      case 403: return '没有权限执行此操作';
      case 404: return '请求的资源不存在';
      case 408: return '请求超时，请稍后重试';
      case 429: return '请求过于频繁，请稍后重试';
      case 500: return '服务器内部错误，请稍后重试';
      case 502: return '网关错误，请稍后重试';
      case 503: return '服务暂时不可用，请稍后重试';
      case 504: return '网关超时，请稍后重试';
      default: return '服务异常，请稍后重试';
    }
  }

  // 判断HTTP错误是否可恢复
  private isHttpErrorRecoverable(status: number): boolean {
    // 4xx客户端错误中，除了401、408、429外，通常不可恢复
    if (status >= 400 && status < 500) {
      return [401, 408, 429].includes(status);
    }
    // 5xx服务器错误通常可恢复
    return status >= 500;
  }

  // 获取错误恢复建议
  getRecoveryAdvice(error: AppError): ErrorRecovery {
    switch (error.code) {
      case ERROR_CODES.NETWORK_ERROR:
        return {
          action: 'retry',
          message: '请检查网络连接后重试',
          autoRetry: true,
          retryDelay: 3000,
          maxRetries: 3,
        };

      case ERROR_CODES.UNAUTHORIZED:
        return {
          action: 'refresh',
          message: '请重新登录',
          autoRetry: false,
        };

      case ERROR_CODES.TIMEOUT:
        return {
          action: 'retry',
          message: '请求超时，正在重试...',
          autoRetry: true,
          retryDelay: 2000,
          maxRetries: 2,
        };

      case ERROR_CODES.SERVICE_UNAVAILABLE:
        return {
          action: 'wait',
          message: '服务暂时不可用，请稍后重试',
          autoRetry: true,
          retryDelay: 10000,
          maxRetries: 3,
        };

      case ERROR_CODES.VALIDATION_ERROR:
        return {
          action: 'navigate',
          message: '请检查输入信息',
          autoRetry: false,
        };

      case ERROR_CODES.FORBIDDEN:
        return {
          action: 'contact_support',
          message: '权限不足，请联系管理员',
          autoRetry: false,
        };

      default:
        return {
          action: 'retry',
          message: '操作失败，请重试',
          autoRetry: false,
        };
    }
  }

  // 记录错误日志
  private logError(error: AppError): void {
    const logLevel = this.getLogLevel(error);
    const logMessage = {
      level: logLevel,
      timestamp: error.timestamp,
      requestId: error.requestId,
      service: error.service,
      code: error.code,
      message: error.technicalMessage,
      userMessage: error.userMessage,
      recoverable: error.recoverable,
      stack: error.stack,
    };

    if (logLevel === 'error') {
      console.error('App Error:', logMessage);
    } else if (logLevel === 'warn') {
      console.warn('App Warning:', logMessage);
    } else {
      console.log('App Info:', logMessage);
    }

    // 在生产环境中，这里可以发送到日志服务
    if (process.env.NODE_ENV === 'production') {
      this.sendToLogService(logMessage);
    }
  }

  // 获取日志级别
  private getLogLevel(error: AppError): 'error' | 'warn' | 'info' {
    if (!error.recoverable || error.code === ERROR_CODES.SERVER_ERROR) {
      return 'error';
    }
    if (error.code === ERROR_CODES.NETWORK_ERROR || error.code === ERROR_CODES.TIMEOUT) {
      return 'warn';
    }
    return 'info';
  }

  // 发送到日志服务（生产环境）
  private sendToLogService(logMessage: any): void {
    // 这里可以集成第三方日志服务，如Sentry、LogRocket等
    // 暂时只是占位符
    console.log('Would send to log service:', logMessage);
  }

  // 添加到错误历史
  private addToHistory(error: AppError): void {
    this.errorHistory.unshift(error);
    if (this.errorHistory.length > this.maxHistorySize) {
      this.errorHistory = this.errorHistory.slice(0, this.maxHistorySize);
    }
  }

  // 获取错误历史
  getErrorHistory(): AppError[] {
    return [...this.errorHistory];
  }

  // 清除错误历史
  clearErrorHistory(): void {
    this.errorHistory = [];
  }

  // 获取错误统计
  getErrorStats(): {
    total: number;
    byCode: Record<string, number>;
    byService: Record<string, number>;
    recoverable: number;
    recent: number; // 最近1小时的错误数
  } {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
    
    const stats = {
      total: this.errorHistory.length,
      byCode: {} as Record<string, number>,
      byService: {} as Record<string, number>,
      recoverable: 0,
      recent: 0,
    };

    this.errorHistory.forEach(error => {
      // 按错误代码统计
      stats.byCode[error.code] = (stats.byCode[error.code] || 0) + 1;
      
      // 按服务统计
      if (error.service) {
        stats.byService[error.service] = (stats.byService[error.service] || 0) + 1;
      }
      
      // 可恢复错误统计
      if (error.recoverable) {
        stats.recoverable++;
      }
      
      // 最近错误统计
      if (error.timestamp && error.timestamp > oneHourAgo) {
        stats.recent++;
      }
    });

    return stats;
  }

  // 生成请求ID
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 检查是否为关键错误（需要立即处理）
  isCriticalError(error: AppError): boolean {
    const criticalCodes = [
      ERROR_CODES.UNAUTHORIZED,
      ERROR_CODES.FORBIDDEN,
      ERROR_CODES.SERVER_ERROR,
    ];
    return criticalCodes.includes(error.code) || !error.recoverable;
  }

  // 格式化错误信息用于显示
  formatErrorForDisplay(error: AppError): {
    title: string;
    message: string;
    actions: string[];
  } {
    const recovery = this.getRecoveryAdvice(error);
    
    return {
      title: this.getErrorTitle(error.code),
      message: error.userMessage || error.message,
      actions: this.getActionLabels(recovery.action),
    };
  }

  // 获取错误标题
  private getErrorTitle(code: string): string {
    switch (code) {
      case ERROR_CODES.NETWORK_ERROR: return '网络连接失败';
      case ERROR_CODES.UNAUTHORIZED: return '身份验证失败';
      case ERROR_CODES.FORBIDDEN: return '权限不足';
      case ERROR_CODES.NOT_FOUND: return '资源不存在';
      case ERROR_CODES.TIMEOUT: return '请求超时';
      case ERROR_CODES.SERVER_ERROR: return '服务器错误';
      case ERROR_CODES.SERVICE_UNAVAILABLE: return '服务不可用';
      default: return '操作失败';
    }
  }

  // 获取操作按钮标签
  private getActionLabels(action: string): string[] {
    switch (action) {
      case 'retry': return ['重试', '取消'];
      case 'refresh': return ['重新登录', '取消'];
      case 'navigate': return ['确定'];
      case 'contact_support': return ['联系客服', '确定'];
      case 'wait': return ['稍后重试', '取消'];
      default: return ['确定'];
    }
  }
}

// 导出单例实例
export const errorHandler = ErrorHandler.getInstance();

// 导出便捷函数
export const handleError = (error: any, context?: string): AppError => {
  return errorHandler.handleError(error, context);
};

export const getRecoveryAdvice = (error: AppError): ErrorRecovery => {
  return errorHandler.getRecoveryAdvice(error);
};

export const formatErrorForDisplay = (error: AppError) => {
  return errorHandler.formatErrorForDisplay(error);
}; 