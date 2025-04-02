/**
 * 全局错误处理中间件
 */
const logger = require('../utils/logger');

/**
 * 错误处理中间件
 * @param {Error} err - 错误对象
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const errorHandler = (err, req, res, next) => {
  // 记录错误
  logger.error(`错误: ${err.message}`, {
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip
  });
  
  // 默认错误状态码和信息
  let statusCode = 500;
  let message = '服务器内部错误';
  let errors = null;
  
  // 根据错误类型设置不同的状态码和消息
  if (err.name === 'ValidationError') {
    // Mongoose 验证错误
    statusCode = 400;
    message = '数据验证失败';
    errors = Object.values(err.errors).map(e => e.message);
  } else if (err.name === 'MongoError' && err.code === 11000) {
    // MongoDB 唯一性冲突
    statusCode = 409;
    message = '数据冲突';
  } else if (err.name === 'CastError') {
    // Mongoose 类型转换错误
    statusCode = 400;
    message = '无效的ID格式';
  } else if (err.name === 'JsonWebTokenError') {
    // JWT 错误
    statusCode = 401;
    message = '无效的身份验证令牌';
  } else if (err.name === 'TokenExpiredError') {
    // JWT 过期错误
    statusCode = 401;
    message = '身份验证令牌已过期';
  } else if (err.statusCode) {
    // 自定义HTTP错误
    statusCode = err.statusCode;
    message = err.message;
    errors = err.errors;
  }
  
  // 构建错误响应
  const response = {
    status: 'error',
    message
  };
  
  // 添加详细错误信息
  if (errors) {
    response.errors = errors;
  }
  
  // 在开发环境中添加错误堆栈
  if (process.env.NODE_ENV === 'development') {
    response.stack = err.stack;
  }
  
  res.status(statusCode).json(response);
};

/**
 * 404处理器中间件
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 */
const notFoundHandler = (req, res) => {
  res.status(404).json({
    status: 'error',
    message: '请求的资源不存在'
  });
};

/**
 * 创建自定义错误
 * @param {String} message - 错误消息
 * @param {Number} statusCode - HTTP状态码
 * @param {Array|Object} errors - 详细错误信息
 * @returns {Error} 错误对象
 */
const createError = (message, statusCode = 400, errors = null) => {
  const error = new Error(message);
  error.statusCode = statusCode;
  if (errors) {
    error.errors = errors;
  }
  return error;
};

module.exports = {
  errorHandler,
  notFoundHandler,
  createError
}; 