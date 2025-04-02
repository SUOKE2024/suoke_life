/**
 * 错误处理中间件
 * 统一处理应用中的错误，并返回适当的响应
 */
const { StatusCodes } = require('http-status-codes');
const { createLogger } = require('../utils/logger');
const config = require('../config');

const logger = createLogger('error-handler');

/**
 * 错误处理中间件
 * 处理应用中的各种错误，并返回适当的响应
 */
const errorHandler = (err, req, res, next) => {
  // 默认错误状态码和消息
  let statusCode = err.status || err.statusCode || StatusCodes.INTERNAL_SERVER_ERROR;
  let errorMessage = err.message || 'Internal Server Error';
  let errorType = err.name || 'Error';
  let errors = err.errors || {};
  
  // 记录错误
  const logLevel = statusCode >= 500 ? 'error' : 'warn';
  logger[logLevel](`${errorType}: ${errorMessage}`, {
    error: err.message,
    stack: err.stack,
    statusCode,
    requestId: req.requestId,
    path: req.path,
    method: req.method,
    userId: req.user ? req.user.id : undefined
  });
  
  // 处理特定类型的错误
  switch (errorType) {
    case 'ValidationError':
      // Joi验证错误
      statusCode = StatusCodes.BAD_REQUEST;
      errorMessage = req.t('common.validation_error', { namespace: 'errors' });
      if (err.details) {
        errors = err.details.reduce((acc, detail) => {
          const key = detail.path.join('.');
          acc[key] = {
            message: req.t(`validation.${detail.type}`, {
              namespace: 'validation',
              variables: {
                field: req.t(`fields.${key}`, { namespace: 'validation', fallbackToKey: true }),
                limit: detail.context ? detail.context.limit : undefined
              }
            }),
            type: detail.type,
            context: detail.context
          };
          return acc;
        }, {});
      }
      break;
      
    case 'UnauthorizedError':
      // JWT认证错误
      statusCode = StatusCodes.UNAUTHORIZED;
      errorMessage = req.t('common.unauthorized', { namespace: 'errors' });
      break;
      
    case 'ForbiddenError':
      // 权限错误
      statusCode = StatusCodes.FORBIDDEN;
      errorMessage = req.t('common.forbidden', { namespace: 'errors' });
      break;
      
    case 'NotFoundError':
      // 资源未找到
      statusCode = StatusCodes.NOT_FOUND;
      errorMessage = req.t('common.not_found', { namespace: 'errors' });
      break;
      
    case 'ConflictError':
      // 资源冲突
      statusCode = StatusCodes.CONFLICT;
      errorMessage = req.t('error.resource_already_exists', { namespace: 'errors' });
      break;
      
    case 'RateLimitError':
      // 速率限制
      statusCode = StatusCodes.TOO_MANY_REQUESTS;
      errorMessage = req.t('common.rate_limit', { namespace: 'errors' });
      break;
      
    case 'DatabaseError':
      // 数据库错误
      statusCode = StatusCodes.INTERNAL_SERVER_ERROR;
      errorMessage = req.t('database.query_error', { namespace: 'errors' });
      // 在生产环境中隐藏详细错误
      if (process.env.NODE_ENV === 'production') {
        errors = {};
      }
      break;
      
    case 'SequelizeValidationError':
    case 'SequelizeUniqueConstraintError':
      // Sequelize验证错误
      statusCode = StatusCodes.BAD_REQUEST;
      errorMessage = req.t('common.validation_error', { namespace: 'errors' });
      if (err.errors) {
        errors = err.errors.reduce((acc, error) => {
          acc[error.path] = {
            message: req.t(`validation.${error.type || 'invalid'}`, {
              namespace: 'validation',
              variables: {
                field: req.t(`fields.${error.path}`, { namespace: 'validation', fallbackToKey: true })
              }
            }),
            type: error.type,
            value: error.value
          };
          return acc;
        }, {});
      }
      break;
  }
  
  // 在开发环境中包含堆栈信息
  const devInfo = process.env.NODE_ENV !== 'production' ? {
    stack: err.stack,
    type: errorType
  } : {};
  
  // 发送错误响应
  return res.status(statusCode).json({
    success: false,
    message: errorMessage,
    errors,
    requestId: req.requestId,
    ...devInfo
  });
};

module.exports = {
  errorHandler
}; 