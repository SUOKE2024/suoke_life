/**
 * 索克生活API错误处理服务
 * 统一处理API错误响应和状态码
 */

export interface ApiError {
  code: number;
  message: string;
  details?: any;
  timestamp: string;
  requestId?: string;
}

export interface ErrorResponse {
  success: false;
  error: ApiError;
  data?: null;
}

export class ApiErrorHandler {
  /**
   * 创建标准化错误响应
   */
  static createErrorResponse(
    code: number,
    message: string,
    details?: any,
    requestId?: string
  ): ErrorResponse {
    return {
      success: false,
      error: {
        code,
        message,
        details,
        timestamp: new Date().toISOString(),
        requestId,
      },
      data: null,
    };
  }

  /**
   * 处理404错误
   */
  static handle404Error(resource: string, requestId?: string): ErrorResponse {
    return this.createErrorResponse(
      404,
      `资源未找到: ${resource}`,
      { resource },
      requestId
    );
  }

  /**
   * 处理400错误
   */
  static handle400Error(
    message: string,
    validationErrors?: any,
    requestId?: string
  ): ErrorResponse {
    return this.createErrorResponse(
      400,
      message || "请求参数无效",
      { validationErrors },
      requestId
    );
  }

  /**
   * 处理401错误
   */
  static handle401Error(requestId?: string): ErrorResponse {
    return this.createErrorResponse(
      401,
      "未授权访问，请先登录",
      null,
      requestId
    );
  }

  /**
   * 处理403错误
   */
  static handle403Error(requestId?: string): ErrorResponse {
    return this.createErrorResponse(
      403,
      "权限不足，无法访问该资源",
      null,
      requestId
    );
  }

  /**
   * 处理500错误
   */
  static handle500Error(message?: string, requestId?: string): ErrorResponse {
    return this.createErrorResponse(
      500,
      message || "服务器内部错误",
      null,
      requestId
    );
  }

  /**
   * 处理网络错误
   */
  static handleNetworkError(requestId?: string): ErrorResponse {
    return this.createErrorResponse(
      0,
      "网络连接失败，请检查网络设置",
      null,
      requestId
    );
  }

  /**
   * 处理超时错误
   */
  static handleTimeoutError(requestId?: string): ErrorResponse {
    return this.createErrorResponse(
      408,
      "请求超时，请稍后重试",
      null,
      requestId
    );
  }

  /**
   * 根据错误类型自动处理
   */
  static handleError(error: any, requestId?: string): ErrorResponse {
    if (error.response) {
      // HTTP错误响应
      const { status, data } = error.response;

      switch (status) {
        case 400:
          return this.handle400Error(
            data?.message || "请求参数无效",
            data?.validationErrors,
            requestId
          );
        case 401:
          return this.handle401Error(requestId);
        case 403:
          return this.handle403Error(requestId);
        case 404:
          return this.handle404Error(data?.resource || "请求的资源", requestId);
        case 500:
          return this.handle500Error(
            data?.message || "服务器内部错误",
            requestId
          );
        default:
          return this.createErrorResponse(
            status,
            data?.message || `HTTP错误 ${status}`,
            data,
            requestId
          );
      }
    } else if (error.request) {
      // 网络错误
      return this.handleNetworkError(requestId);
    } else if (error.code === "ECONNABORTED") {
      // 超时错误
      return this.handleTimeoutError(requestId);
    } else {
      // 其他错误
      return this.createErrorResponse(
        -1,
        error.message || "未知错误",
        error,
        requestId
      );
    }
  }

  /**
   * 记录错误日志
   */
  static logError(error: ApiError, context?: any): void {
    console.error("[API Error]", {
      code: error.code,
      message: error.message,
      details: error.details,
      timestamp: error.timestamp,
      requestId: error.requestId,
      context,
    });
  }
}

export default ApiErrorHandler;
