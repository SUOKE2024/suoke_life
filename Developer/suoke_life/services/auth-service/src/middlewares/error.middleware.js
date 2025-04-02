/**
 * 错误处理中间件
 */
const logger = require('../utils/logger');

/**
 * 全局错误处理中间件
 * 用于捕获所有未处理的错误并返回适当的响应
 * 
 * @param {Error} err - 错误对象
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 * @param {Function} next - 下一个中间件函数
 */
const errorHandler = (err, req, res, next) => {
  // 提取错误信息和状态码
  const statusCode = err.statusCode || 500;
  const message = err.message || '服务器内部错误';
  const errorCode = err.code || 'server_error';
  const stack = process.env.NODE_ENV === 'development' ? err.stack : undefined;
  
  // 记录错误日志
  logger.error(`请求错误: ${message}`, {
    method: req.method,
    url: req.originalUrl,
    statusCode,
    errorCode,
    stack,
    requestId: req.id,
    userId: req.userId
  });
  
  // 构建错误响应
  const response = {
    success: false,
    message,
    code: errorCode,
    requestId: req.id
  };
  
  // 开发环境下包含错误堆栈
  if (process.env.NODE_ENV === 'development') {
    response.stack = stack;
  }
  
  // 发送错误响应
  res.status(statusCode).json(response);
};

module.exports = errorHandler; 