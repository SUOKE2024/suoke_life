/**
 * 应用程序错误基类
 */
export class AppError extends Error {
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  
  constructor(message: string, statusCode: number, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    
    Error.captureStackTrace(this, this.constructor);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

/**
 * 验证错误
 */
export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 400);
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * 未找到资源错误
 */
export class NotFoundError extends AppError {
  constructor(message: string) {
    super(message, 404);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

/**
 * 未授权错误
 */
export class UnauthorizedError extends AppError {
  constructor(message: string = '未授权访问') {
    super(message, 401);
    Object.setPrototypeOf(this, UnauthorizedError.prototype);
  }
}

/**
 * 禁止访问错误
 */
export class ForbiddenError extends AppError {
  constructor(message: string = '禁止访问') {
    super(message, 403);
    Object.setPrototypeOf(this, ForbiddenError.prototype);
  }
}

/**
 * 服务内部错误
 */
export class InternalServerError extends AppError {
  constructor(message: string = '服务器内部错误') {
    super(message, 500, false);
    Object.setPrototypeOf(this, InternalServerError.prototype);
  }
}

/**
 * 远程服务错误
 */
export class ServiceError extends AppError {
  constructor(message: string, statusCode: number = 500) {
    super(message, statusCode, false);
    Object.setPrototypeOf(this, ServiceError.prototype);
  }
}

/**
 * 业务逻辑错误
 */
export class BusinessError extends AppError {
  constructor(message: string) {
    super(message, 400);
    Object.setPrototypeOf(this, BusinessError.prototype);
  }
}

/**
 * 数据库操作错误
 */
export class DatabaseError extends AppError {
  constructor(message: string) {
    super(message, 500, false);
    Object.setPrototypeOf(this, DatabaseError.prototype);
  }
}

/**
 * AI服务错误
 */
export class AIServiceError extends AppError {
  constructor(message: string) {
    super(message, 503, false);
    Object.setPrototypeOf(this, AIServiceError.prototype);
  }
}

/**
 * 服务不可用错误
 */
export class ServiceUnavailableError extends AppError {
  constructor(message: string = '服务暂时不可用') {
    super(message, 503, false);
    Object.setPrototypeOf(this, ServiceUnavailableError.prototype);
  }
}

/**
 * 格式化错误响应
 * @param err 错误对象
 * @returns 格式化的错误响应对象
 */
export function formatErrorResponse(err: any) {
  if (err instanceof AppError) {
    return {
      success: false,
      status: err.statusCode,
      message: err.message,
      error: {
        type: err.constructor.name,
        isOperational: err.isOperational
      }
    };
  }
  
  // 处理未知错误
  return {
    success: false,
    status: 500,
    message: '服务器内部错误',
    error: {
      type: 'InternalServerError',
      isOperational: false
    }
  };
}