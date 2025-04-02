/**
 * 错误处理中间件
 */
const { ApiResponse } = require('@suoke/shared').responses;
const { logger } = require('@suoke/shared').utils;
const config = require('@suoke/shared').config;

/**
 * 统一错误处理中间件
 */
const errorHandler = (err, req, res, next) => {
  // 记录错误详情
  logger.error('请求处理错误', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    ip: req.ip,
    userId: req.user?.id,
    requestId: req.requestId
  });

  // 尝试翻译错误消息
  if (req.t && config.i18n?.translateResponseMessages) {
    let errorKey = '';
    
    // 根据错误类型和代码确定翻译键
    if (err.code) {
      if (err.code.includes('.')) {
        errorKey = err.code; // 已经是格式化的错误键
      } else {
        // 根据错误代码推断错误类型前缀
        const errorPrefix = getErrorPrefixByCode(err.code);
        errorKey = `${errorPrefix}.${err.code.toLowerCase()}`;
      }
    } else {
      errorKey = 'common.internal_error';
    }
    
    // 翻译错误消息
    const translatedMessage = req.t(errorKey, { module: 'errors' });
    
    // 如果找到翻译，则使用翻译后的消息
    if (translatedMessage && translatedMessage !== errorKey) {
      err.message = translatedMessage;
    }
  }

  // 设置默认状态码
  const statusCode = err.statusCode || 500;

  // 构建错误响应
  const response = {
    code: err.code || 'INTERNAL_SERVER_ERROR',
    message: err.message || '服务器内部错误',
    requestId: req.requestId
  };

  // 在开发环境下添加堆栈信息
  if (process.env.NODE_ENV === 'development') {
    response.stack = err.stack;
  }

  // 发送错误响应
  res.status(statusCode).json(response);
};

/**
 * 404错误处理中间件
 */
const notFoundHandler = (req, res, next) => {
  const error = new Error(`未找到请求的资源: ${req.originalUrl}`);
  error.statusCode = 404;
  error.code = 'NOT_FOUND';
  next(error);
};

/**
 * 根据错误代码获取错误类型前缀
 * @param {string} code - 错误代码
 * @returns {string} - 错误类型前缀
 */
function getErrorPrefixByCode(code) {
  const codeStr = code.toLowerCase();
  
  if (codeStr.includes('user') || codeStr.includes('auth') || codeStr.includes('login')) {
    return 'user';
  } else if (codeStr.includes('health') || codeStr.includes('profile')) {
    return 'health';
  } else if (codeStr.includes('file') || codeStr.includes('upload')) {
    return 'file';
  } else if (codeStr.includes('db') || codeStr.includes('database')) {
    return 'database';
  } else if (codeStr.includes('session')) {
    return 'session';
  } else if (codeStr.includes('encrypt') || codeStr.includes('crypt')) {
    return 'encryption';
  }
  
  return 'common';
}

module.exports = {
  errorHandler,
  notFoundHandler
}; 