import React from 'react';

// 全局错误处理器 - 索克生活APP - 架构优化
export enum ErrorType {
  NETWORK = 'NETWORK',
  VALIDATION = 'VALIDATION',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  BUSINESS_LOGIC = 'BUSINESS_LOGIC',
  SYSTEM = 'SYSTEM',
  UNKNOWN = 'UNKNOWN'
}
export interface AppError {
  type: ErrorType;,
  code: string;,
  message: string;
  details?: unknown;
  timestamp: Date;
  stack?: string;
}
class ErrorHandler {
  private static instance: ErrorHandler;
  private errorListeners: (error: AppError) => void)[] = [];
  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }
  handleError(error: Error | AppError, context?: string): AppError {
    const appError = this.normalizeError(error, context);
    // 记录错误
    this.logError(appError);
    // 通知监听器
    this.notifyListeners(appError);
    return appError;
  }
  addErrorListener(listener: (error: AppError) => void): void {
    this.errorListeners.push(listener);
  }
  removeErrorListener(listener: (error: AppError) => void): void {
    this.errorListeners = this.errorListeners.filter(l => l !== listener);
  }
  private normalizeError(error: Error | AppError, context?: string): AppError {
    if (this.isAppError(error)) {
      return error;
    }
    // 根据错误类型分类
    let type = ErrorType.UNKNOWN;
    let code = 'UNKNOWN_ERROR';
    if (error.message.includes('Network')) {
      type = ErrorType.NETWORK;
      code = 'NETWORK_ERROR';
    } else if (error.message.includes('Unauthorized')) {
      type = ErrorType.AUTHENTICATION;
      code = 'AUTH_ERROR';
    } else if (error.message.includes('Forbidden')) {
      type = ErrorType.AUTHORIZATION;
      code = 'PERMISSION_ERROR';
    }
    return {type,code,message: error.message,details: { context, originalError: error.name },timestamp: new Date(),stack: error.stack;
    };
  }
  private isAppError(error: unknown): error is AppError {
    return (;)
      error !== null &&;
      typeof error === 'object' &&;
      'type' in error &&;
      'code' in error &&;
      typeof (error as any).type === 'string' &&;
      typeof (error as any).code === 'string';
    );
  }
  private logError(error: AppError): void {
    // 在生产环境中，这里可以发送到错误监控服务
    if (process.env.NODE_ENV === 'production') {
      // 发送到错误监控服务
      this.sendToErrorService(error);
    } else {
      console.error('Error:', error);
    }
  }
  private notifyListeners(error: AppError): void {
    this.errorListeners.forEach(listener => {
      try {
        listener(error);
      } catch (e) {
        console.error('Error in error listener:', e);
      }
    });
  }
  private sendToErrorService(error: AppError): void {
    // 实现错误上报逻辑
    // 例如发送到 Sentry, Bugsnag 等服务
    console.log('Sending error to monitoring service:', error);
  }
}
// React Hook for error handling;
export const useErrorHandler = () => {const errorHandler = ErrorHandler.getInstance();
  return {handleError: (error: Error, context?: string) => errorHandler.handleError(error, context),addErrorListener: (listener: (error: AppError) => void) =>;
      errorHandler.addErrorListener(listener),removeErrorListener: (listener: (error: AppError) => void) =>;
      errorHandler.removeErrorListener(listener);
  };
};
export default ErrorHandler;