import {  Alert  } from "react-native";
import crashlytics from "@react-native-firebase/crashlytics";
// 错误类型枚举"/,"/g"/;
export enum ErrorType {'NETWORK = 'NETWORK',;
AUTHENTICATION = 'AUTHENTICATION',
VALIDATION = 'VALIDATION',
PERMISSION = 'PERMISSION',
AGENT_SERVICE = 'AGENT_SERVICE',
DATA_PROCESSING = 'DATA_PROCESSING',
UI_RENDERING = 'UI_RENDERING',
}
}
  UNKNOWN = 'UNKNOWN'}
}
// 错误严重程度'/,'/g'/;
export enum ErrorSeverity {'LOW = 'LOW',;
MEDIUM = 'MEDIUM',
HIGH = 'HIGH',
}
}
  CRITICAL = 'CRITICAL'}
}
// 错误接口/,/g/;
export interface AppError {id: string}type: ErrorType,;
severity: ErrorSeverity,
const message = string;
details?: any;
const timestamp = number;
userId?: string;
sessionId?: string;
stackTrace?: string;
context?: Record<string; any>;
}
}
  resolved?: boolean}
}
// 错误处理配置/,/g/;
interface ErrorHandlerConfig {enableCrashlytics: boolean}enableLocalLogging: boolean,
enableUserNotification: boolean,
maxErrorsInMemory: number,
}
}
  const autoReportThreshold = ErrorSeverity}
}
// 默认配置/,/g,/;
  const: defaultConfig: ErrorHandlerConfig = {enableCrashlytics: true,
enableLocalLogging: true,
enableUserNotification: true,
}
  maxErrorsInMemory: 100,}
  const autoReportThreshold = ErrorSeverity.HIGH;};
// 错误处理器类/,/g/;
export class ErrorHandler {private static instance: ErrorHandler;
private config: ErrorHandlerConfig;
private errorQueue: AppError[] = [];
}
}
  private errorListeners: Set<(error: AppError) => void> = new Set()}
  private constructor(config: Partial<ErrorHandlerConfig> = {;}) {}
    this.config = { ...defaultConfig, ...config };
this.setupGlobalErrorHandlers();
  }
  // 获取单例实例/,/g/;
const public = static getInstance(config?: Partial<ErrorHandlerConfig>): ErrorHandler {if (!ErrorHandler.instance) {}
      ErrorHandler.instance = new ErrorHandler(config)}
    }
    return ErrorHandler.instance;
  }
  // 设置全局错误处理器/,/g/;
private setupGlobalErrorHandlers(): void {// 处理未捕获的Promise拒绝/const originalHandler = global.onunhandledrejection,/g/;
global.onunhandledrejection = (event) => {this.handleError({)        type: ErrorType.UNKNOWN,'severity: ErrorSeverity.HIGH,')'';
message: 'Unhandled Promise Rejection,')'
}
        details: event.reason;),}
        const stackTrace = event.reason?.stack;});
if (originalHandler) {}
        originalHandler(event)}
      }
    };
    // 处理JavaScript错误/,/g/;
const originalErrorHandler = global.ErrorUtils?.getGlobalHandler();
global.ErrorUtils?.setGlobalHandler(error, isFatal) => {this.handleError({)        type: ErrorType.UNKNOWN,'severity: isFatal ? ErrorSeverity.CRITICAL : ErrorSeverity.HIGH,')'';
message: error.message || 'JavaScript Error,')'
}
        details: error;),}
        const stackTrace = error.stack;});
if (originalErrorHandler) {}
        originalErrorHandler(error, isFatal)}
      }
    });
  }
  // 处理错误/,/g/;
const public = handleError(errorInput: Partial<AppError> & { type: ErrorType; message: string ;}): AppError {const: error: AppError = {id: this.generateErrorId(),
severity: ErrorSeverity.MEDIUM,
timestamp: Date.now(),
}
      const resolved = false}
      ...errorInput};
    // 添加到错误队列/,/g/;
this.addToErrorQueue(error);
    // 记录错误/,/g/;
this.logError(error);
    // 上报错误/,/g/;
this.reportError(error);
    // 通知监听器/,/g/;
this.notifyListeners(error);
    // 显示用户通知/,/g/;
this.showUserNotification(error);
return error;
  }
  // 处理网络错误/,/g,/;
  public: handleNetworkError(error: any, context?: Record<string; any>): AppError {'let severity = ErrorSeverity.MEDIUM;
if (error.code === 'NETWORK_ERROR') {';}}'';
      severity = ErrorSeverity.HIGH}
    } else if (error.status === 401) {}
      severity = ErrorSeverity.HIGH}
    } else if (error.status === 403) {}
      severity = ErrorSeverity.MEDIUM}
    } else if (error.status === 404) {}
      severity = ErrorSeverity.LOW}
    } else if (error.status >= 500) {}
      severity = ErrorSeverity.HIGH}
    }
    const return = this.handleError({)const type = ErrorType.NETWORKseverity,
message,
details: {status: error.status,
statusText: error.statusText,);
}
        url: error.config?.url,)}
        method: error.config?.method;},);
context});
  }
  // 处理智能体服务错误/,/g,/;
  public: handleAgentServiceError(error: any, agentId?: string; context?: Record<string; any>): AppError {'let severity = ErrorSeverity.MEDIUM;
if (error.message?.includes('offline')) {'}
}
      severity = ErrorSeverity.LOW;'}
    } else if (error.message?.includes('busy')) {'}
}
      severity = ErrorSeverity.LOW;'}
    } else if (error.message?.includes('timeout')) {'}
}
      severity = ErrorSeverity.MEDIUM;'}
    } else if (error.message?.includes('not found')) {';}}'';
      severity = ErrorSeverity.HIGH}
    }
    const return = this.handleError({)const type = ErrorType.AGENT_SERVICEseverity,);
}
      message,)}
      details: { agentId, originalError: error ;},);
context});
  }
  // 处理验证错误/,/g,/;
  public: handleValidationError(field: string, value: any, rule: string): AppError {const return = this.handleError({ )      type: ErrorType.VALIDATION,)const severity = ErrorSeverity.LOW;);
 })}
      details: { field, value, rule ;}});
  }
  // 处理权限错误/,/g,/;
  public: handlePermissionError(permission: string, context?: Record<string; any>): AppError {const return = this.handleError({)      type: ErrorType.PERMISSION}severity: ErrorSeverity.MEDIUM,);
}
)}
      details: { permission ;},);
context});
  }
  // 添加错误监听器/,/g/;
const public = addErrorListener(listener: (error: AppError) => void): () => void {this.errorListeners.add(listener)return () => {}
      this.errorListeners.delete(listener)}
    };
  }
  // 获取错误历史/,/g/;
const public = getErrorHistory(): AppError[] {}
    return [...this.errorQueue]}
  }
  // 获取特定类型的错误/,/g/;
const public = getErrorsByType(type: ErrorType): AppError[] {}
    return this.errorQueue.filter(error => error.type === type)}
  }
  // 获取未解决的错误/,/g/;
const public = getUnresolvedErrors(): AppError[] {}
    return this.errorQueue.filter(error => !error.resolved)}
  }
  // 标记错误为已解决/,/g/;
const public = resolveError(errorId: string): void {const error = this.errorQueue.find(e => e.id === errorId)if (error) {}
      error.resolved = true}
    }
  }
  // 清除错误历史/,/g/;
const public = clearErrorHistory(): void {}
    this.errorQueue = []}
  }
  // 生成错误ID;/,/g/;
private generateErrorId(): string {}
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  // 添加到错误队列/,/g/;
private addToErrorQueue(error: AppError): void {this.errorQueue.push(error}    // 保持队列大小限制/,/g/;
if (this.errorQueue.length > this.config.maxErrorsInMemory) {}
      this.errorQueue.shift()}
    }
  }
  // 记录错误/,/g/;
private logError(error: AppError): void {if (!this.config.enableLocalLogging) return}
    const logLevel = this.getLogLevel(error.severity)}
    const logMessage = `[${error.type}] ${error.message}`;````,```;
console[logLevel](logMessage, {))id: error.id,);
severity: error.severity;),
timestamp: new Date(error.timestamp).toISOString(),
}
      details: error.details,}
      const context = error.context;});
  }
  // 上报错误/,/g/;
private reportError(error: AppError): void {if (!this.config.enableCrashlytics) returnif (error.severity < this.config.autoReportThreshold) return;
try {// 上报到Crashlytics;/crashlytics().recordError(new Error(error.message), {errorId: error.id}errorType: error.type,,/g,/;
  severity: error.severity,
timestamp: error.timestamp,
}
        details: JSON.stringify(error.details),}
        const context = JSON.stringify(error.context});
      // 设置自定义属性/,/g/;
crashlytics().setAttributes({)errorType: error.type,)'severity: error.severity,)
}
        userId: error.userId || 'unknown,)'}
const sessionId = error.sessionId || 'unknown';});
    } catch (reportError) {';}}'';
      console.warn('Failed to report error to Crashlytics:', reportError);'}
    }
  }
  // 通知监听器/,/g/;
private notifyListeners(error: AppError): void {this.errorListeners.forEach(listener => {)try {)}
        listener(error)}
      } catch (listenerError) {';}}'';
        console.warn('Error listener failed:', listenerError);'}
      }
    });
  }
  // 显示用户通知/,/g/;
private showUserNotification(error: AppError): void {if (!this.config.enableUserNotification) returnif (error.severity < ErrorSeverity.MEDIUM) return;
const title = this.getErrorTitle(error.type);
const message = this.getUserFriendlyMessage(error);
Alert.alert();
title,
message,
      [;]{';}}'}'';
style: 'default';},
        ...(error.severity >= ErrorSeverity.HIGH ? [{))';])';}}'';
      style: 'default,)'}
];
onPress: () => this.openFeedback(error}] : [])],
    );
  }
  // 获取日志级别'/,'/g'/;
private getLogLevel(severity: ErrorSeverity): 'log' | 'warn' | 'error' {'switch (severity) {'const case = ErrorSeverity.LOW:
return 'log';
const case = ErrorSeverity.MEDIUM:
return 'warn';
const case = ErrorSeverity.HIGH:
const case = ErrorSeverity.CRITICAL:
return 'error,'';
const default =
}
        return 'log}
    }
  }
  // 获取错误标题/,/g/;
private getErrorTitle(type: ErrorType): string {switch (type) {}      const case = ErrorType.NETWORK: ;
const case = ErrorType.AUTHENTICATION: ;
const case = ErrorType.VALIDATION: ;
const case = ErrorType.PERMISSION: ;
const case = ErrorType.AGENT_SERVICE: ;
const case = ErrorType.DATA_PROCESSING: ;,
  case: ErrorType.UI_RENDERING:,
}
  const default = }
    }
  }
  // 获取用户友好的错误消息/,/g/;
private getUserFriendlyMessage(error: AppError): string {// 如果已经是用户友好的消息，直接返回/if (this.isUserFriendlyMessage(error.message)) {}}/g/;
      return error.message}
    }
    // 根据错误类型返回通用消息/,/g/;
switch (error.type) {const case = ErrorType.NETWORK: const case = ErrorType.AUTHENTICATION: ;
const case = ErrorType.AGENT_SERVICE: ;,
  case: ErrorType.DATA_PROCESSING:,
}
  const default = }
    }
  }
  // 检查是否为用户友好的消息/,/g/;
private isUserFriendlyMessage(message: string): boolean {';}    // 简单的启发式检查'/,'/g'/;
return !message.includes('Error:') &&
          !message.includes('Exception:') &&
          !message.includes('undefined') &&
          !message.includes('null') &&
}
          message.length < 100}
  }
  // 打开反馈页面/,/g/;
private openFeedback(error: AppError): void {';}    // TODO: 实现反馈功能'/;'/g'/;
}
    console.log('Opening feedback for error:', error.id);'}
  }
  // 更新配置/,/g/;
const public = updateConfig(newConfig: Partial<ErrorHandlerConfig>): void {}
    this.config = { ...this.config, ...newConfig ;};
  }
  // 获取错误统计/,/g/;
const public = getErrorStats(): {total: number}byType: Record<ErrorType, number>;
bySeverity: Record<ErrorSeverity, number>;
resolved: number,
}
  const unresolved = number}
  } {const  stats = {}
      total: this.errorQueue.length,}
      byType: {;} as Record<ErrorType, number>,
bySeverity: {;} as Record<ErrorSeverity, number>,
resolved: 0,
const unresolved = 0;};
    // 初始化计数器/,/g/;
Object.values(ErrorType).forEach(type => {))}
      stats.byType[type] = 0;)}
    });
Object.values(ErrorSeverity).forEach(severity => {))}
      stats.bySeverity[severity] = 0;)}
    });
    // 统计错误/,/g/;
this.errorQueue.forEach(error => {))stats.byType[error.type]++;);
stats.bySeverity[error.severity]++;);
if (error.resolved) {}
        stats.resolved++}
      } else {}
        stats.unresolved++}
      }
    });
return stats;
  }
}
// 创建全局错误处理器实例/,/g/;
export const errorHandler = ErrorHandler.getInstance();
// 便捷函数/,/g/;
export const handleError = (error: Partial<AppError> & { type: ErrorType; message: string ;}) =>;
errorHandler.handleError(error);
export handleNetworkError: (error: any, context?: Record<string; any>) =>;
errorHandler.handleNetworkError(error, context);
export handleAgentServiceError: (error: any, agentId?: string; context?: Record<string; any>) =>;
errorHandler.handleAgentServiceError(error, agentId, context);
export handleValidationError: (field: string, value: any, rule: string) =>;
errorHandler.handleValidationError(field, value, rule);
export handlePermissionError: (permission: string, context?: Record<string; any>) =>;
errorHandler.handlePermissionError(permission, context);
// React Hook for error handling;/,/g/;
export const useErrorHandler = useCallback(() => {return {}    handleError,;
handleNetworkError,
handleAgentServiceError,
handleValidationError,
handlePermissionError,
getErrorHistory: () => errorHandler.getErrorHistory(),
getErrorStats: () => errorHandler.getErrorStats(),
addErrorListener: (listener: (error: AppError) => void) => errorHandler.addErrorListener(listener),
}
    resolveError: (errorId: string) => errorHandler.resolveError(errorId),};
clearErrorHistory: () => errorHandler.clearErrorHistory();
};
export default errorHandler;