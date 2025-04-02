/**
 * 错误处理工具模块
 * 提供统一的错误处理机制
 */
const logger = require('./logger');

/**
 * 基础应用错误类
 */
class AppError extends Error {
  /**
   * 创建应用错误实例
   * @param {string} message - 错误消息
   * @param {number} statusCode - HTTP状态码
   * @param {Object} details - 错误详情
   */
  constructor(message, statusCode = 500, details = null) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date().toISOString();
    this.isOperational = true; // 表示这是已知的操作错误
    
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * 未找到错误
 */
class NotFoundError extends AppError {
  constructor(message = '资源未找到', details = null) {
    super(message, 404, details);
  }
}

/**
 * 认证错误
 */
class AuthenticationError extends AppError {
  constructor(message = '认证失败', details = null) {
    super(message, 401, details);
  }
}

/**
 * 授权错误
 */
class AuthorizationError extends AppError {
  constructor(message = '没有权限', details = null) {
    super(message, 403, details);
  }
}

/**
 * 验证错误
 */
class ValidationError extends AppError {
  constructor(message = '数据验证失败', details = null) {
    super(message, 400, details);
  }
}

/**
 * 服务不可用错误
 */
class ServiceUnavailableError extends AppError {
  constructor(message = '服务暂不可用', details = null) {
    super(message, 503, details);
  }
}

/**
 * 数据库错误
 */
class DatabaseError extends AppError {
  constructor(message = '数据库操作失败', details = null) {
    super(message, 500, details);
  }
}

/**
 * 处理Express全局错误
 * @param {Error} err - 错误对象
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const globalErrorHandler = (err, req, res, next) => {
  // 默认为500，表示服务器错误
  let statusCode = err.statusCode || 500;
  let message = err.message || '服务器内部错误';
  let details = err.details || null;
  
  // 记录错误日志
  if (statusCode >= 500) {
    logger.error(`[${req.method}] ${req.path} - ${statusCode}: ${message}`, {
      error: err.stack,
      details,
      request: {
        method: req.method,
        path: req.path,
        query: req.query,
        // 确保不记录敏感信息
        headers: {
          'user-agent': req.headers['user-agent'],
          host: req.headers.host,
          referer: req.headers.referer
        }
      }
    });
  } else {
    logger.warn(`[${req.method}] ${req.path} - ${statusCode}: ${message}`, {
      details,
      request: {
        method: req.method,
        path: req.path
      }
    });
  }
  
  // 生产环境下隐藏实际错误详情
  if (process.env.NODE_ENV === 'production' && statusCode >= 500) {
    message = '服务器内部错误';
    details = null;
  }
  
  // 发送错误响应
  res.status(statusCode).json({
    success: false,
    message,
    details,
    timestamp: new Date().toISOString()
  });
};

// 导出错误处理工具
module.exports = {
  AppError,
  NotFoundError,
  AuthenticationError,
  AuthorizationError,
  ValidationError,
  ServiceUnavailableError,
  DatabaseError,
  globalErrorHandler
}; 