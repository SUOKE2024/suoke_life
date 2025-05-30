import { Alert } from "react-native";



/**
 * 统一错误处理工具
 * 提供用户友好的错误信息和处理策略
 */

export interface ErrorInfo {
  code: string;
  message: string;
  userMessage: string;
  severity: "low" | "medium" | "high" | "critical";
  action?: "retry" | "redirect" | "ignore" | "contact_support";
  retryable: boolean;
}

// 错误类型映射
const ERROR_MAPPING: Record<string, ErrorInfo> = {
  // 网络错误
  NETWORK_ERROR: {
    code: "NETWORK_ERROR",
    message: "Network request failed",
    userMessage: "网络连接失败，请检查网络设置",
    severity: "medium",
    action: "retry",
    retryable: true,
  },
  TIMEOUT_ERROR: {
    code: "TIMEOUT_ERROR",
    message: "Request timeout",
    userMessage: "请求超时，请稍后重试",
    severity: "medium",
    action: "retry",
    retryable: true,
  },

  // 认证错误
  AUTH_EXPIRED: {
    code: "AUTH_EXPIRED",
    message: "Authentication token expired",
    userMessage: "登录已过期，请重新登录",
    severity: "high",
    action: "redirect",
    retryable: false,
  },
  AUTH_INVALID: {
    code: "AUTH_INVALID",
    message: "Invalid authentication credentials",
    userMessage: "登录信息无效，请重新登录",
    severity: "high",
    action: "redirect",
    retryable: false,
  },

  // 服务错误
  SERVICE_UNAVAILABLE: {
    code: "SERVICE_UNAVAILABLE",
    message: "Service temporarily unavailable",
    userMessage: "服务暂时不可用，请稍后重试",
    severity: "high",
    action: "retry",
    retryable: true,
  },
  AGENT_OFFLINE: {
    code: "AGENT_OFFLINE",
    message: "AI agent is offline",
    userMessage: "智能体服务暂时离线，正在尝试重新连接",
    severity: "medium",
    action: "retry",
    retryable: true,
  },

  // 数据错误
  INVALID_DATA: {
    code: "INVALID_DATA",
    message: "Invalid data format",
    userMessage: "数据格式错误，请检查输入内容",
    severity: "low",
    action: "ignore",
    retryable: false,
  },
  DATA_NOT_FOUND: {
    code: "DATA_NOT_FOUND",
    message: "Requested data not found",
    userMessage: "未找到相关数据",
    severity: "low",
    action: "ignore",
    retryable: false,
  },

  // 权限错误
  PERMISSION_DENIED: {
    code: "PERMISSION_DENIED",
    message: "Permission denied",
    userMessage: "权限不足，无法执行此操作",
    severity: "medium",
    action: "contact_support",
    retryable: false,
  },

  // 系统错误
  INTERNAL_ERROR: {
    code: "INTERNAL_ERROR",
    message: "Internal server error",
    userMessage: "系统内部错误，我们正在处理中",
    severity: "critical",
    action: "contact_support",
    retryable: false,
  },

  // 默认错误
  UNKNOWN_ERROR: {
    code: "UNKNOWN_ERROR",
    message: "Unknown error occurred",
    userMessage: "发生未知错误，请稍后重试",
    severity: "medium",
    action: "retry",
    retryable: true,
  },
};

/**
 * 错误处理器类
 */
export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: Array<{
    timestamp: Date;
    error: ErrorInfo;
    context?: any;
  }> = [];

  private constructor() {}

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  /**
   * 处理错误
   */
  handleError(error: any, context?: any): ErrorInfo {
    const errorInfo = this.parseError(error);

    // 记录错误
    this.logError(errorInfo, context);

    // 根据错误严重程度决定处理方式
    this.processError(errorInfo, context);

    return errorInfo;
  }

  /**
   * 解析错误
   */
  private parseError(error: any): ErrorInfo {
    // 如果是已知的错误代码
    if (typeof error === "string" && ERROR_MAPPING[error]) {
      return ERROR_MAPPING[error];
    }

    // 如果是网络错误
    if (
      error?.code === "NETWORK_ERROR" ||
      error?.message?.includes("Network")
    ) {
      return ERROR_MAPPING.NETWORK_ERROR;
    }

    // 如果是超时错误
    if (error?.code === "TIMEOUT" || error?.message?.includes("timeout")) {
      return ERROR_MAPPING.TIMEOUT_ERROR;
    }

    // 如果是认证错误
    if (error?.status === 401 || error?.message?.includes("Unauthorized")) {
      return ERROR_MAPPING.AUTH_EXPIRED;
    }

    // 如果是权限错误
    if (error?.status === 403 || error?.message?.includes("Forbidden")) {
      return ERROR_MAPPING.PERMISSION_DENIED;
    }

    // 如果是服务不可用
    if (
      error?.status === 503 ||
      error?.message?.includes("Service Unavailable")
    ) {
      return ERROR_MAPPING.SERVICE_UNAVAILABLE;
    }

    // 如果是内部服务器错误
    if (
      error?.status === 500 ||
      error?.message?.includes("Internal Server Error")
    ) {
      return ERROR_MAPPING.INTERNAL_ERROR;
    }

    // 默认错误
    return {
      ...ERROR_MAPPING.UNKNOWN_ERROR,
      message: error?.message || "Unknown error",
    };
  }

  /**
   * 记录错误
   */
  private logError(errorInfo: ErrorInfo, context?: any): void {
    const logEntry = {
      timestamp: new Date(),
      error: errorInfo,
      context,
    };

    this.errorLog.push(logEntry);

    // 只保留最近100条错误记录
    if (this.errorLog.length > 100) {
      this.errorLog = this.errorLog.slice(-100);
    }

    // 控制台输出（开发环境）
    if (__DEV__) {
      console.error("Error handled:", logEntry);
    }
  }

  /**
   * 处理错误
   */
  private processError(errorInfo: ErrorInfo, context?: any): void {
    switch (errorInfo.severity) {
      case "critical":
        this.showCriticalErrorAlert(errorInfo);
        break;
      case "high":
        this.showHighSeverityAlert(errorInfo);
        break;
      case "medium":
        this.showMediumSeverityAlert(errorInfo);
        break;
      case "low":
        // 低严重程度错误可以静默处理或显示轻量提示
        console.warn("Low severity error:", errorInfo.userMessage);
        break;
    }
  }

  /**
   * 显示严重错误警告
   */
  private showCriticalErrorAlert(errorInfo: ErrorInfo): void {
    Alert.alert(
      "系统错误",
      errorInfo.userMessage + "\n\n如果问题持续存在，请联系客服。",
      [
        {
          text: "联系客服",
          onPress: () => this.contactSupport(errorInfo),
        },
        {
          text: "确定",
          style: "default",
        },
      ]
    );
  }

  /**
   * 显示高严重程度警告
   */
  private showHighSeverityAlert(errorInfo: ErrorInfo): void {
    const buttons: any[] = [];

    if (errorInfo.retryable) {
      buttons.push({
        text: "重试",
        onPress: () => this.retryLastAction(errorInfo),
      });
    }

    if (errorInfo.action === "redirect") {
      buttons.push({
        text: "重新登录",
        onPress: () => this.redirectToLogin(),
      });
    }

    buttons.push({
      text: "确定",
      style: "cancel",
    });

    Alert.alert("错误", errorInfo.userMessage, buttons);
  }

  /**
   * 显示中等严重程度警告
   */
  private showMediumSeverityAlert(errorInfo: ErrorInfo): void {
    if (errorInfo.retryable) {
      Alert.alert("提示", errorInfo.userMessage, [
        {
          text: "重试",
          onPress: () => this.retryLastAction(errorInfo),
        },
        {
          text: "取消",
          style: "cancel",
        },
      ]);
    } else {
      Alert.alert("提示", errorInfo.userMessage, [{ text: "确定" }]);
    }
  }

  /**
   * 重试上次操作
   */
  private retryLastAction(errorInfo: ErrorInfo): void {
    // 这里可以实现重试逻辑
    console.log("Retrying action for error:", errorInfo.code);
  }

  /**
   * 重定向到登录页面
   */
  private redirectToLogin(): void {
    // 这里可以实现重定向逻辑
    console.log("Redirecting to login");
  }

  /**
   * 联系客服
   */
  private contactSupport(errorInfo: ErrorInfo): void {
    // 这里可以实现联系客服的逻辑
    console.log("Contacting support for error:", errorInfo.code);
  }

  /**
   * 获取错误日志
   */
  getErrorLog(): Array<{ timestamp: Date; error: ErrorInfo; context?: any }> {
    return [...this.errorLog];
  }

  /**
   * 清除错误日志
   */
  clearErrorLog(): void {
    this.errorLog = [];
  }

  /**
   * 获取错误统计
   */
  getErrorStats(): {
    total: number;
    bySeverity: Record<string, number>;
    byCode: Record<string, number>;
    recent: number; // 最近1小时的错误数
  } {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);

    const bySeverity: Record<string, number> = {};
    const byCode: Record<string, number> = {};
    let recent = 0;

    this.errorLog.forEach((entry) => {
      // 按严重程度统计
      bySeverity[entry.error.severity] =
        (bySeverity[entry.error.severity] || 0) + 1;

      // 按错误代码统计
      byCode[entry.error.code] = (byCode[entry.error.code] || 0) + 1;

      // 最近1小时的错误
      if (entry.timestamp > oneHourAgo) {
        recent++;
      }
    });

    return {
      total: this.errorLog.length,
      bySeverity,
      byCode,
      recent,
    };
  }
}

// 导出单例实例
export const errorHandler = ErrorHandler.getInstance();

// 便捷函数
export const handleError = (error: any, context?: any): ErrorInfo => {
  return errorHandler.handleError(error, context);
};

export const getErrorStats = () => {
  return errorHandler.getErrorStats();
};

export const clearErrorLog = () => {
  errorHandler.clearErrorLog();
};
