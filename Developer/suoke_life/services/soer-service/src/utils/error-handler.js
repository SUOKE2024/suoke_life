/**
 * 错误处理工具模块
 * 提供统一的错误处理机制
 */
const logger = require('./logger');

/**
 * 创建自定义错误对象
 * @param {string} code - 错误代码
 * @param {string} message - 错误消息
 * @param {number} status - HTTP状态码
 * @param {Object} details - 错误详情
 * @returns {Error} 自定义错误对象
 */
function createError(code, message, status = 400, details = null) {
  const error = new Error(message);
  error.code = code;
  error.status = status;
  error.details = details;
  error.isCustom = true;
  error.timestamp = new Date().toISOString();
  
  return error;
}

/**
 * 处理异步路由错误
 * @param {Function} fn - 异步路由处理函数
 * @returns {Function} 包装后的错误处理函数
 */
function asyncHandler(fn) {
  return (req, res, next) => {
    return Promise.resolve(fn(req, res, next)).catch(next);
  };
}

/**
 * 全局错误处理中间件
 * @param {Error} err - 错误对象
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
function errorMiddleware(err, req, res, next) {
  // 设置默认响应状态码
  const statusCode = err.status || err.statusCode || 500;
  const errorCode = err.code || 'INTERNAL_SERVER_ERROR';
  const message = err.message || '服务器内部错误';
  const details = err.details || null;
  
  // 记录错误
  if (statusCode >= 500) {
    logger.error(`服务器错误: ${message}`, {
      code: errorCode,
      statusCode,
      path: req.path,
      method: req.method,
      stack: err.stack,
      details
    });
  } else {
    logger.warn(`客户端错误: ${message}`, {
      code: errorCode,
      statusCode,
      path: req.path,
      method: req.method,
      details
    });
  }
  
  // 生产环境中不暴露服务器错误详情
  if (process.env.NODE_ENV === 'production' && statusCode >= 500) {
    return res.status(statusCode).json({
      success: false,
      code: errorCode,
      message: '服务器内部错误',
      requestId: req.requestId
    });
  }
  
  // 返回错误响应
  return res.status(statusCode).json({
    success: false,
    code: errorCode,
    message,
    details: process.env.NODE_ENV === 'development' ? details : undefined,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
    requestId: req.requestId
  });
}

module.exports = {
  createError,
  asyncHandler,
  errorMiddleware
}; 