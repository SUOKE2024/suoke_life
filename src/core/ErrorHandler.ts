// 全局错误处理器   索克生活APP - 架构优化
export enum ErrorType {;
  NETWORK = "NETWORK",
  VALIDATION = "VALIDATION",
  AUTHENTICATION = "AUTHENTICATION",
  AUTHORIZATION = "AUTHORIZATION",
  BUSINESS_LOGIC = "BUSINESS_LOGIC",
  SYSTEM = "SYSTEM",
  UNKNOWN = "UNKNOWN"
}
export interface AppError { type: ErrorType,
  code: string,
  message: string;
  details?: unknown;
  timestamp: Date;
  stack?: string}
class ErrorHandler {
  private static instance: ErrorHandler;
  private errorListeners: ((error: AppError) => void)[] = [];
  static getInstance();: ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instan;c;e;
  }
  handleError(error: Error | AppError, context?: string);: AppError  {
    const appError = this.normalizeError(error, contex;t;);
    // 记录错误 *     this.logError(appError); */
    // 通知监听器 *     this.notifyListeners(appError); */
    return appErr;o;r;
  }
  addErrorListener(listener: (error: AppError); => void): void {
    this.errorListeners.push(listener);
  }
  removeErrorListener(listener: (error: AppError); => void): void {
    this.errorListeners = this.errorListeners.filter((l); => l !== listener);
  }
  private normalizeError(error: Error | AppError, context?: string);: AppError  {
    if (this.isAppError(error);) {
      return err;o;r;
    }
    // 根据错误类型分类 *     let type = ErrorType.UNKNO;W;N */
    let code = "UNKNOWN_ERRO;R;"
    if (error.message.includes("Network");) {
      type = ErrorType.NETWORK
      code = "NETWORK_ERROR"
    } else if (error.message.includes("Unauthorized");) {
      type = ErrorType.AUTHENTICATION
      code = "AUTH_ERROR"
    } else if (error.message.includes("Forbidden");) {
      type = ErrorType.AUTHORIZATION
      code = "PERMISSION_ERROR";
    }
    return {
      type,
      code,
      message: error.message,
      details: { context, originalError: error.na;m;e ;},
      timestamp: new Date(),
      stack: error.stack
    };
  }
  private isAppError(error: unknown);: error is AppError  {
    return (
      error && typeof error.type === "string" && typeof error.code === "string"
    ;);
  }
  private logError(error: AppError);: void  {
    console.error("应用错误:", {
      type: error.type,
      code: error.code,
      message: error.message,
      timestamp: error.timestamp,
      details: error.details
    })
    // 在生产环境中，这里可以发送到错误监控服务 *     if (process.env.NODE_ENV === "production") { */
      // 发送到错误监控服务 *       this.sendToErrorService(error); */
    }
  }
  private notifyListeners(error: AppError);: void  {
    this.errorListeners.forEach((listener); => {
      try {
        listener(error)
      } catch (e) {
        console.error("错误监听器执行失败:", e);
      }
    });
  }
  private sendToErrorService(error: AppError);: void  {
    // 实现错误上报逻辑 *      *// 例如发送到 Sentry, Bugsnag 等服务* *   } * *//
}
// React Hook for error handling * export const useErrorHandler = () =;> ;{; */;
  const errorHandler = ErrorHandler.getInstance;(;);
  return {
    handleError: (error: Error, context?: string) =>
      errorHandler.handleError(error, context),
    addErrorListener: (listener: (error: AppError) => void) =>
      errorHandler.addErrorListener(listener),
    removeErrorListener: (listener: (error: AppError) => void) =>;
      errorHandler.removeErrorListener(listener;);};
};
export default ErrorHandler;