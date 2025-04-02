/**
 * 错误处理中间件
 * 统一处理API请求中的错误
 */
const { logger } = require('../utils');
const { AppError } = require('../utils/error-handler');
const { error: errorResponse } = require('../utils/response-handler');

/**
 * 404错误处理中间件
 * 处理未找到的路由请求
 */
const notFoundHandler = (req, res, next) => {
  const error = new AppError(`找不到请求的路径: ${req.originalUrl}`, 404);
  next(error);
};

/**
 * 全局错误处理中间件
 * 处理应用程序中的所有错误
 */
const globalErrorHandler = (err, req, res, next) => {
  // 默认错误状态和消息
  let statusCode = err.statusCode || 500;
  let message = err.message || '服务器内部错误';
  let errorDetails = err.details || null;
  
  // 根据错误类型进行特定处理
  if (err.name === 'ValidationError') { // Mongoose验证错误
    statusCode = 400;
    message = '数据验证失败';
    errorDetails = Object.values(err.errors).map(error => ({
      path: error.path,
      message: error.message
    }));
  } else if (err.name === 'CastError') { // Mongoose类型转换错误
    statusCode = 400;
    message = `无效的${err.path}: ${err.value}`;
  } else if (err.name === 'MongoError' || err.name === 'MongoServerError') { // MongoDB错误
    if (err.code === 11000) { // 重复键错误
      statusCode = 409;
      message = '数据冲突，可能存在重复记录';
      
      // 提取重复字段信息
      const field = Object.keys(err.keyValue)[0];
      const value = err.keyValue[field];
      errorDetails = { field, value };
    }
  } else if (err.name === 'JsonWebTokenError') { // JWT错误
    statusCode = 401;
    message = '无效的身份验证令牌';
  } else if (err.name === 'TokenExpiredError') { // JWT过期错误
    statusCode = 401;
    message = '身份验证令牌已过期';
  } else if (err.code === 'LIMIT_FILE_SIZE') { // 文件上传大小限制错误
    statusCode = 400;
    message = '文件大小超出限制';
  } else if (err.code === 'LIMIT_UNEXPECTED_FILE') { // 文件上传字段错误
    statusCode = 400;
    message = '意外的文件上传字段';
  } else if (err.code === 'ECONNREFUSED' || err.code === 'ENOTFOUND') { // 连接错误
    statusCode = 503;
    message = '服务暂时不可用';
  }
  
  // 记录错误日志
  if (statusCode >= 500) {
    // 严重错误记录详细信息
    logger.error(`[${req.method}] ${req.originalUrl} - ${statusCode}`, {
      error: err.message,
      stack: err.stack,
      requestBody: req.body,
      requestParams: req.params,
      requestQuery: req.query,
      userId: req.user?.id || 'anonymous'
    });
  } else {
    // 客户端错误简单记录
    logger.warn(`[${req.method}] ${req.originalUrl} - ${statusCode}: ${message}`, {
      userId: req.user?.id || 'anonymous',
      requestPath: req.originalUrl
    });
  }
  
  // 在开发环境中返回完整的错误堆栈
  if (process.env.NODE_ENV === 'development') {
    return errorResponse(res, message, statusCode, {
      ...errorDetails,
      stack: err.stack,
      name: err.name
    });
  }
  
  // 在生产环境中返回安全的错误信息
  return errorResponse(res, message, statusCode, errorDetails);
};

/**
 * 异步函数错误包装器
 * 用于捕获异步函数中的错误并传递给错误处理中间件
 * @param {Function} fn - 异步处理函数
 * @returns {Function} 包装后的中间件函数
 */
const catchAsync = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

/**
 * 请求超时中间件
 * 在请求处理时间过长时返回超时响应
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Function} 超时中间件
 */
const requestTimeout = (timeout = 30000) => {
  return (req, res, next) => {
    // 设置超时
    const timeoutId = setTimeout(() => {
      logger.warn(`请求超时: [${req.method}] ${req.originalUrl}`, {
        timeout,
        userId: req.user?.id || 'anonymous'
      });
      
      return errorResponse(res, '请求处理超时', 504);
    }, timeout);
    
    // 保存原始的响应结束方法
    const originalEnd = res.end;
    
    // 覆盖响应结束方法
    res.end = function(...args) {
      // 清除超时
      clearTimeout(timeoutId);
      // 调用原始的结束方法
      return originalEnd.apply(this, args);
    };
    
    next();
  };
};

/**
 * 限速中间件错误处理
 * 处理速率限制超出错误
 */
const rateLimitErrorHandler = (err, req, res, next) => {
  if (err.name === 'RateLimitExceeded') {
    return errorResponse(res, '请求频率过高，请稍后再试', 429);
  }
  next(err);
};

module.exports = {
  notFoundHandler,
  globalErrorHandler,
  catchAsync,
  requestTimeout,
  rateLimitErrorHandler
}; 