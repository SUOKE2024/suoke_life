/**
 * API错误处理和重试机制
 * 提供统一的错误处理、重试策略和用户友好的错误提示
 */

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  service: string;
  method: string;
  retryCount: number;
  originalError?: Error;
}

export interface RetryConfig {
  maxRetries: number;
  baseDelay: number; // 基础延迟时间（毫秒）
  maxDelay: number; // 最大延迟时间（毫秒）
  backoffMultiplier: number; // 退避乘数
  retryCondition: (error: any) => boolean;
}

export interface ErrorHandlerConfig {
  enableLogging: boolean;
  enableReporting: boolean;
  userFriendlyMessages: boolean;
  showToast: boolean;
}

// 错误类型定义
export enum ErrorType {
  NETWORK = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT_ERROR', 
  SERVER = 'SERVER_ERROR',
  CLIENT = 'CLIENT_ERROR',
  VALIDATION = 'VALIDATION_ERROR',
  AUTHENTICATION = 'AUTH_ERROR',
  AUTHORIZATION = 'PERMISSION_ERROR',
  RATE_LIMIT = 'RATE_LIMIT_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  UNKNOWN = 'UNKNOWN_ERROR',
}

// 用户友好的错误消息映射
const ERROR_MESSAGES: { [key in ErrorType]: string } = {
  [ErrorType.NETWORK]: '网络连接异常，请检查网络设置',
  [ErrorType.TIMEOUT]: '请求超时，请稍后重试',
  [ErrorType.SERVER]: '服务器内部错误，我们正在修复中',
  [ErrorType.CLIENT]: '请求参数错误，请检查输入信息',
  [ErrorType.VALIDATION]: '输入信息格式不正确，请重新填写',
  [ErrorType.AUTHENTICATION]: '身份验证失败，请重新登录',
  [ErrorType.AUTHORIZATION]: '您没有权限执行此操作',
  [ErrorType.RATE_LIMIT]: '请求过于频繁，请稍后再试',
  [ErrorType.SERVICE_UNAVAILABLE]: '服务暂时不可用，请稍后重试',
  [ErrorType.UNKNOWN]: '发生未知错误，请联系客服',
};

// 不同服务的重试配置
const RETRY_CONFIGS: { [key: string]: Partial<RetryConfig> } = {
  'xiaoai': {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffMultiplier: 2,
  },
  'xiaoke': {
    maxRetries: 2,
    baseDelay: 500,
    maxDelay: 5000,
    backoffMultiplier: 1.5,
  },
  'laoke': {
    maxRetries: 3,
    baseDelay: 800,
    maxDelay: 8000,
    backoffMultiplier: 2,
  },
  'soer': {
    maxRetries: 2,
    baseDelay: 600,
    maxDelay: 6000,
    backoffMultiplier: 1.8,
  },
};

class ApiErrorHandler {
  private config: ErrorHandlerConfig = {
    enableLogging: true,
    enableReporting: true,
    userFriendlyMessages: true,
    showToast: true,
  };

  private defaultRetryConfig: RetryConfig = {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffMultiplier: 2,
    retryCondition: (error: any) => {
      // 默认重试条件：网络错误、超时、5xx服务器错误
      const isNetworkError = !error.response;
      const isTimeout = error.code === 'TIMEOUT' || error.message?.includes('timeout');
      const isServerError = error.response?.status >= 500;
      const isRateLimit = error.response?.status === 429;
      
      return isNetworkError || isTimeout || isServerError || isRateLimit;
    },
  };

  /**
   * 设置配置
   */
  setConfig(config: Partial<ErrorHandlerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * 分类错误类型
   */
  private categorizeError(error: any): ErrorType {
    if (!error.response) {
      // 网络错误或请求被取消
      return error.code === 'NETWORK_ERROR' ? ErrorType.NETWORK : ErrorType.TIMEOUT;
    }

    const status = error.response.status;
    
    if (status >= 500) {
      return ErrorType.SERVER;
    } else if (status === 429) {
      return ErrorType.RATE_LIMIT;
    } else if (status === 503) {
      return ErrorType.SERVICE_UNAVAILABLE;
    } else if (status === 401) {
      return ErrorType.AUTHENTICATION;
    } else if (status === 403) {
      return ErrorType.AUTHORIZATION;
    } else if (status >= 400) {
      return status === 422 ? ErrorType.VALIDATION : ErrorType.CLIENT;
    }

    return ErrorType.UNKNOWN;
  }

  /**
   * 创建标准化错误对象
   */
  createError(
    error: any,
    service: string,
    method: string,
    retryCount = 0
  ): ApiError {
    const errorType = this.categorizeError(error);
    const message = this.config.userFriendlyMessages 
      ? ERROR_MESSAGES[errorType]
      : error.message || '请求失败';

    const apiError: ApiError = {
      code: errorType,
      message,
      details: error.response?.data,
      timestamp: new Date().toISOString(),
      service,
      method,
      retryCount,
      originalError: error,
    };

    return apiError;
  }

  /**
   * 计算延迟时间
   */
  private calculateDelay(retryCount: number, config: RetryConfig): number {
    const exponentialDelay = config.baseDelay * Math.pow(config.backoffMultiplier, retryCount);
    const jitter = Math.random() * 0.1 * exponentialDelay; // 添加10%的随机抖动
    return Math.min(exponentialDelay + jitter, config.maxDelay);
  }

  /**
   * 执行延迟
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 带重试的API调用
   */
  async withRetry<T>(
    apiCall: () => Promise<T>,
    service: string,
    method: string,
    customRetryConfig?: Partial<RetryConfig>
  ): Promise<T> {
    const serviceConfig = RETRY_CONFIGS[service] || {};
    const retryConfig: RetryConfig = {
      ...this.defaultRetryConfig,
      ...serviceConfig,
      ...customRetryConfig,
    };

    let lastError: any;
    let retryCount = 0;

    while (retryCount <= retryConfig.maxRetries) {
      try {
        const result = await apiCall();
        
        // 成功时记录日志（如果之前有重试）
        if (retryCount > 0 && this.config.enableLogging) {
          console.log(`✅ ${service}.${method} 重试成功 (尝试次数: ${retryCount + 1})`);
        }
        
        return result;
      } catch (error) {
        lastError = error;
        
        // 检查是否应该重试
        if (retryCount >= retryConfig.maxRetries || !retryConfig.retryCondition(error)) {
          break;
        }

        retryCount++;
        const delayMs = this.calculateDelay(retryCount - 1, retryConfig);

        if (this.config.enableLogging) {
          console.warn(`⚠️ ${service}.${method} 重试 ${retryCount}/${retryConfig.maxRetries}，${delayMs}ms后重试`, error);
        }

        await this.delay(delayMs);
      }
    }

    // 所有重试都失败，抛出最后的错误
    const apiError = this.createError(lastError, service, method, retryCount);
    this.handleError(apiError);
    throw apiError;
  }

  /**
   * 处理错误
   */
  private handleError(error: ApiError): void {
    // 记录错误日志
    if (this.config.enableLogging) {
      console.error(`❌ API错误 [${error.service}.${error.method}]:`, error);
    }

    // 上报错误（生产环境）
    if (this.config.enableReporting && __DEV__ === false) {
      this.reportError(error);
    }

    // 显示用户提示
    if (this.config.showToast) {
      this.showUserError(error);
    }
  }

  /**
   * 上报错误到监控系统
   */
  private reportError(error: ApiError): void {
    // 这里可以集成错误监控服务（如Sentry、Bugsnag等）
    // 示例实现：
    try {
      // await errorReportingService.captureException(error);
      console.log('📊 错误已上报到监控系统:', error.code);
    } catch (reportError) {
      console.warn('错误上报失败:', reportError);
    }
  }

  /**
   * 显示用户友好的错误提示
   */
  private showUserError(error: ApiError): void {
    // 这里可以集成Toast组件或Alert
    // 示例实现：
    console.log(`💡 用户提示: ${error.message}`);
    
    // 在React Native中可以使用ToastAndroid或自定义Toast组件
    // ToastAndroid.show(error.message, ToastAndroid.SHORT);
  }

  /**
   * 获取错误恢复建议
   */
  getRecoveryAdvice(error: ApiError): string[] {
    const advice: string[] = [];

    switch (error.code) {
      case ErrorType.NETWORK:
        advice.push('检查网络连接');
        advice.push('尝试切换到其他网络');
        advice.push('稍后重试');
        break;
      
      case ErrorType.AUTHENTICATION:
        advice.push('重新登录账号');
        advice.push('检查账号状态');
        break;
      
      case ErrorType.RATE_LIMIT:
        advice.push('稍等片刻再试');
        advice.push('避免频繁操作');
        break;
      
      case ErrorType.SERVER:
        advice.push('稍后重试');
        advice.push('联系客服报告问题');
        break;
      
      default:
        advice.push('重新尝试操作');
        advice.push('如问题持续存在，请联系客服');
    }

    return advice;
  }

  /**
   * 检查错误是否可恢复
   */
  isRecoverable(error: ApiError): boolean {
    const recoverableErrors = [
      ErrorType.NETWORK,
      ErrorType.TIMEOUT,
      ErrorType.RATE_LIMIT,
      ErrorType.SERVICE_UNAVAILABLE,
    ];

    return recoverableErrors.includes(error.code as ErrorType);
  }

  /**
   * 获取错误统计信息
   */
  getErrorStats(): { [key: string]: number } {
    // 这里可以返回错误统计信息
    // 实际实现中可以使用持久化存储来记录错误统计
    return {
      totalErrors: 0,
      networkErrors: 0,
      serverErrors: 0,
      clientErrors: 0,
    };
  }
}

// 导出单例实例
export const apiErrorHandler = new ApiErrorHandler();

/**
 * API调用装饰器，自动添加错误处理和重试
 */
export function withErrorHandling(
  service: string,
  customRetryConfig?: Partial<RetryConfig>
) {
  return function(
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
  ) {
    const method = descriptor.value;

    descriptor.value = async function(...args: any[]) {
      return apiErrorHandler.withRetry(
        () => method.apply(this, args),
        service,
        propertyName,
        customRetryConfig
      );
    };
  };
}

/**
 * 快速错误处理函数
 */
export function handleApiError(error: any, service: string, method: string): ApiError {
  return apiErrorHandler.createError(error, service, method);
}

/**
 * 检查网络连接状态
 */
export async function checkNetworkStatus(): Promise<boolean> {
  try {
    // 在React Native中可以使用NetInfo
    // const state = await NetInfo.fetch();
    // return state.isConnected;
    
    // 简单的网络检查
    const response = await fetch('https://www.google.com', {
      method: 'HEAD',
      timeout: 5000,
    });
    return response.ok;
  } catch {
    return false;
  }
}