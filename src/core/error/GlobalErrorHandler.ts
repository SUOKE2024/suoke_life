/* 误 *//;/g/;
*//;,/g/;
export enum ErrorType {NETWORK_ERROR = 'NETWORK_ERROR',';,}API_ERROR = 'API_ERROR',';,'';
VALIDATION_ERROR = 'VALIDATION_ERROR',';,'';
AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',';,'';
AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',';,'';
BUSINESS_LOGIC_ERROR = 'BUSINESS_LOGIC_ERROR',';,'';
SYSTEM_ERROR = 'SYSTEM_ERROR',';'';
}
}
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'}'';'';
}';,'';
export enum ErrorSeverity {';,}LOW = 'LOW',';,'';
MEDIUM = 'MEDIUM',';,'';
HIGH = 'HIGH',';'';
}
}
  CRITICAL = 'CRITICAL'}'';'';
}
export interface ErrorInfo {type: ErrorType}severity: ErrorSeverity,;
const message = string;
code?: string;
details?: any;
const timestamp = number;
userId?: string;
sessionId?: string;
}
}
  stackTrace?: string;}
}
export interface ErrorHandlerConfig {enableLogging: boolean}enableReporting: boolean,;
const enableUserNotification = boolean;
reportingEndpoint?: string;
maxRetries: number,;
}
}
  const retryDelay = number;}
}
export class GlobalErrorHandler {;,}private static instance: GlobalErrorHandler;
private config: ErrorHandlerConfig;
private errorQueue: ErrorInfo[] = [];
private constructor(config: ErrorHandlerConfig) {this.config = config;}}
}
    this.setupGlobalHandlers();}
  }
  const public = static getInstance(config?: ErrorHandlerConfig): GlobalErrorHandler {if (!GlobalErrorHandler.instance) {}      const: defaultConfig: ErrorHandlerConfig = {enableLogging: true,;
enableReporting: true,;
enableUserNotification: true,;
}
        maxRetries: 3,}
        const retryDelay = 1000;};
GlobalErrorHandler.instance = new GlobalErrorHandler(config || defaultConfig);
    }
    return GlobalErrorHandler.instance;
  }
  /* 误 *//;/g/;
  *//;,/g,/;
  public: handleError(error: Error | ErrorInfo, context?: any): void {const errorInfo = this.normalizeError(error; context);}    // 记录错误/;,/g/;
if (this.config.enableLogging) {}}
      this.logError(errorInfo);}
    }
    // 上报错误/;,/g/;
if (this.config.enableReporting) {}}
      this.reportError(errorInfo);}
    }
    // 用户通知/;,/g/;
if (this.config.enableUserNotification) {}}
      this.notifyUser(errorInfo);}
    }
    // 添加到错误队列/;,/g/;
this.errorQueue.push(errorInfo);
    // 保持队列大小/;,/g/;
if (this.errorQueue.length > 100) {}}
      this.errorQueue.shift();}
    }
  }
  /* 误 *//;/g/;
  *//;,/g,/;
  public: handleNetworkError(error: Error, url?: string): void {this.handleError({)      type: ErrorType.NETWORK_ERROR}severity: ErrorSeverity.MEDIUM,);
}
)}
      details: { url, originalError: error.message ;},);
timestamp: Date.now(),;
const stackTrace = error.stack;});
  }
  /* 误 *//;/g/;
  *//;,/g,/;
  public: handleApiError(status: number, message: string, endpoint?: string): void {const severity = status >= 500 ? ErrorSeverity.HIGH : ErrorSeverity.MEDIUM;,}this.handleError({)      const type = ErrorType.API_ERROR;);,}severity,);
);
}
      code: status.toString(),}
      details: { endpoint, status ;}
const timestamp = Date.now();});
  }
  /* 误 *//;/g/;
  *//;,/g,/;
  public: handleValidationError(field: string, message: string): void {this.handleError({)      type: ErrorType.VALIDATION_ERROR}severity: ErrorSeverity.LOW,);
}
)}
      details: { field ;},);
const timestamp = Date.now();});
  }
  /* 误 *//;/g/;
  *//;,/g/;
const public = handleAuthError(message: string): void {this.handleError({)      type: ErrorType.AUTHENTICATION_ERROR,);,}const severity = ErrorSeverity.HIGH;);
}
)}
      const timestamp = Date.now();});
  }
  /* 误 *//;/g/;
  *//;,/g,/;
  public: handleBusinessError(message: string, details?: any): void {this.handleError({)      type: ErrorType.BUSINESS_LOGIC_ERROR}const severity = ErrorSeverity.MEDIUM;);
message,);
}
      details,)}
      const timestamp = Date.now();});
  }
  /* 计 *//;/g/;
  *//;,/g/;
const public = getErrorStats(): {total: number}byType: Record<ErrorType, number>;
bySeverity: Record<ErrorSeverity, number>;
}
    const recent = ErrorInfo[];}
  } {}
    byType: {} as Record<ErrorType, number>;
bySeverity: {} as Record<ErrorSeverity, number>;
this.errorQueue.forEach(error => {));,}byType[error.type] = (byType[error.type] || 0) + 1;
}
      bySeverity[error.severity] = (bySeverity[error.severity] || 0) + 1;}
    });
return {const total = this.errorQueue.length;,}byType,;
}
      bySeverity,}
      const recent = this.errorQueue.slice(-10);};
  }
  /* 列 *//;/g/;
  *//;,/g/;
const public = clearErrors(): void {}}
    this.errorQueue = [];}
  }
  /* 器 *//;/g/;
  *//;,/g/;
private setupGlobalHandlers(): void {';}    // 处理未捕获的Promise拒绝'/;,'/g'/;
if (typeof window !== 'undefined') {';,}window.addEventListener('unhandledrejection', (event) => {';,}this.handleError({)          type: ErrorType.SYSTEM_ERROR}severity: ErrorSeverity.HIGH,);'';
}
)}
          details: { reason: event.reason ;},);
const timestamp = Date.now();});
      });';'';
      // 处理全局错误'/;,'/g'/;
window.addEventListener('error', (event) => {';,}this.handleError({)          type: ErrorType.SYSTEM_ERROR}severity: ErrorSeverity.HIGH,;,'';
details: {filename: event.filename,);
}
            lineno: event.lineno,)}
            colno: event.colno;},);
timestamp: Date.now(),;
const stackTrace = event.error?.stack;});
      });
    }
  }
  /* 象 *//;/g/;
  */'/;,'/g'/;
private normalizeError(error: Error | ErrorInfo, context?: any): ErrorInfo {';,}if ('type' in error) {';}}'';
      return error;}
    }
    return {type: ErrorType.UNKNOWN_ERROR}severity: ErrorSeverity.MEDIUM,;
timestamp: Date.now(),;
}
      stackTrace: error.stack,}
      const details = context;};
  }
  /* 误 *//;/g/;
  *//;,/g/;
private logError(error: ErrorInfo): void {}}
    const logLevel = this.getLogLevel(error.severity);}
    const logMessage = `[${error.type}] ${error.message}`;````;,```;
console[logLevel](logMessage, {));,}severity: error.severity,);
timestamp: new Date(error.timestamp).toISOString(),;
}
      details: error.details,}
      const stackTrace = error.stackTrace;});
  }
  /* 误 *//;/g/;
  *//;,/g/;
private async reportError(error: ErrorInfo): Promise<void> {if (!this.config.reportingEndpoint) return;,}try {';,}await: fetch(this.config.reportingEndpoint, {';,)method: "POST";",")";}}"";
      const headers = {)"}"";"";
          'Content-Type': 'application/json';},')''/;,'/g'/;
const body = JSON.stringify(error);});
    } catch (reportingError) {}}
}
    }
  }
  /* 户 *//;/g/;
  *//;,/g/;
private notifyUser(error: ErrorInfo): void {if (error.severity === ErrorSeverity.LOW) return;,}const userMessage = this.getUserFriendlyMessage(error);
    // 这里可以集成具体的通知机制（Toast、Modal等）/;/g/;
}
}
  }
  /* ' *//;'/g'/;
  */'/;,'/g'/;
private getLogLevel(severity: ErrorSeverity): 'error' | 'warn' | 'info' {';,}switch (severity) {const case = ErrorSeverity.CRITICAL: ';,}const case = ErrorSeverity.HIGH: ';,'';
return 'error';';,'';
const case = ErrorSeverity.MEDIUM: ';,'';
return 'warn';';,'';
const case = ErrorSeverity.LOW: ';,'';
const default = ';'';
}
        return 'info';'}'';'';
    }
  }
  /* 息 *//;/g/;
  *//;,/g/;
private getUserFriendlyMessage(error: ErrorInfo): string {switch (error.type) {}      const case = ErrorType.NETWORK_ERROR: ;
const case = ErrorType.API_ERROR: ;
const case = ErrorType.AUTHENTICATION_ERROR: ;
const case = ErrorType.AUTHORIZATION_ERROR: ;
const case = ErrorType.VALIDATION_ERROR: ;
const case = ErrorType.BUSINESS_LOGIC_ERROR: ;
return: error.message,;
}
  const default = }
    ;}
  }
}
// 导出单例实例'/;,'/g'/;
export const globalErrorHandler = GlobalErrorHandler.getInstance();