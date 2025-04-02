/**
 * 自定义错误类库
 * 定义应用中使用的各种错误类型
 */

/**
 * 应用基础错误类
 */
class AppError extends Error {
  /**
   * 构造函数
   * @param {string} message - 错误消息
   * @param {number} statusCode - HTTP状态码
   * @param {Object} details - 错误详情
   */
  constructor(message, statusCode = 500, details = null) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.details = details;
    
    // 保留原始错误的堆栈信息
    if (details && details.cause instanceof Error) {
      this.cause = details.cause;
      this.stack = `${this.stack}\nCaused by: ${details.cause.stack}`;
    }

    Error.captureStackTrace(this, this.constructor);
  }

  /**
   * 将错误转换为JSON
   * @returns {Object} JSON对象
   */
  toJSON() {
    return {
      error: {
        name: this.name,
        message: this.message,
        statusCode: this.statusCode,
        details: this.details ? (this.details.cause ? { ...this.details, cause: undefined } : this.details) : null
      }
    };
  }
}

/**
 * 验证错误
 * 用于表示请求参数验证失败的情况
 */
class ValidationError extends AppError {
  constructor(message = '请求验证失败', details = null) {
    super(message, 400, details);
    this.errorCode = 'VALIDATION_ERROR';
  }
}

/**
 * 未找到错误
 * 用于表示请求的资源不存在
 */
class NotFoundError extends AppError {
  constructor(message = '资源未找到', details = null) {
    super(message, 404, details);
    this.errorCode = 'NOT_FOUND';
  }
}

/**
 * 未授权错误
 * 用于表示用户未经授权访问资源
 */
class UnauthorizedError extends AppError {
  constructor(message = '未授权访问', details = null) {
    super(message, 401, details);
    this.errorCode = 'UNAUTHORIZED';
  }
}

/**
 * 禁止访问错误
 * 用于表示用户无权限执行操作
 */
class ForbiddenError extends AppError {
  constructor(message = '禁止访问', details = null) {
    super(message, 403, details);
    this.errorCode = 'FORBIDDEN';
  }
}

/**
 * 冲突错误
 * 用于表示请求与当前状态冲突
 */
class ConflictError extends AppError {
  constructor(message = '请求冲突', details = null) {
    super(message, 409, details);
    this.errorCode = 'CONFLICT';
  }
}

/**
 * 服务不可用错误
 * 用于表示外部服务不可用
 */
class ServiceUnavailableError extends AppError {
  constructor(message = '服务暂不可用', details = null) {
    super(message, 503, details);
    this.errorCode = 'SERVICE_UNAVAILABLE';
  }
}

/**
 * 数据库错误
 * 用于表示数据库操作失败
 */
class DatabaseError extends AppError {
  constructor(message = '数据库操作失败', details = null) {
    super(message, 500, details);
    this.errorCode = 'DATABASE_ERROR';
  }
}

/**
 * 服务器错误
 * 用于表示服务器内部错误
 */
class ServerError extends AppError {
  constructor(message = '服务器内部错误', details = null) {
    super(message, 500, details);
    this.errorCode = 'SERVER_ERROR';
  }
}

/**
 * 业务逻辑错误
 * 用于表示业务逻辑验证失败的情况
 */
class BusinessError extends AppError {
  constructor(message = '业务逻辑错误', details = null) {
    super(message, 422, details);
    this.errorCode = 'BUSINESS_ERROR';
  }
}

/**
 * 请求超时错误
 * 用于表示请求处理超时
 */
class TimeoutError extends AppError {
  constructor(message = '请求处理超时', details = null) {
    super(message, 408, details);
    this.errorCode = 'TIMEOUT';
  }
}

/**
 * 限流错误
 * 用于表示请求被限流
 */
class RateLimitError extends AppError {
  constructor(message = '请求频率超过限制', details = null) {
    super(message, 429, details);
    this.errorCode = 'RATE_LIMIT';
  }
}

/**
 * 创建自定义错误的工厂函数
 * @param {string} code - 错误代码
 * @param {string} message - 错误消息
 * @param {number} statusCode - HTTP状态码
 * @param {Object} details - 错误详情
 * @returns {AppError} 自定义错误对象
 */
function createError(code, message, statusCode = 500, details = null) {
  const error = new AppError(message, statusCode, details);
  error.errorCode = code;
  return error;
}

module.exports = {
  AppError,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError,
  ConflictError,
  ServiceUnavailableError,
  DatabaseError,
  ServerError,
  BusinessError,
  TimeoutError,
  RateLimitError,
  createError
}; 