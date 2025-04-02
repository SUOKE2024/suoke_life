/**
 * API响应工具
 */

/**
 * 成功响应
 * @param {Object} res - Express响应对象
 * @param {Object} data - 响应数据
 * @param {String} message - 响应消息
 * @param {Number} statusCode - HTTP状态码
 */
const success = (res, data = {}, message = '操作成功', statusCode = 200) => {
  return res.status(statusCode).json({
    status: 'success',
    message,
    data
  });
};

/**
 * 错误响应
 * @param {Object} res - Express响应对象
 * @param {String} message - 错误消息
 * @param {Number} statusCode - HTTP状态码
 * @param {Object} errors - 详细错误信息
 */
const error = (res, message = '操作失败', statusCode = 400, errors = null) => {
  const response = {
    status: 'error',
    message
  };

  if (errors) {
    response.errors = errors;
  }

  return res.status(statusCode).json(response);
};

/**
 * 未找到资源响应
 * @param {Object} res - Express响应对象
 * @param {String} message - 错误消息
 */
const notFound = (res, message = '资源不存在') => {
  return error(res, message, 404);
};

/**
 * 服务器错误响应
 * @param {Object} res - Express响应对象
 * @param {String} message - 错误消息
 * @param {Object} err - 错误对象
 */
const serverError = (res, message = '服务器内部错误', err = null) => {
  const response = {
    status: 'error',
    message
  };

  if (process.env.NODE_ENV === 'development' && err) {
    response.error = {
      message: err.message,
      stack: err.stack
    };
  }

  return res.status(500).json(response);
};

/**
 * 未授权响应
 * @param {Object} res - Express响应对象
 * @param {String} message - 错误消息
 */
const unauthorized = (res, message = '未授权访问') => {
  return error(res, message, 401);
};

/**
 * 禁止访问响应
 * @param {Object} res - Express响应对象
 * @param {String} message - 错误消息
 */
const forbidden = (res, message = '禁止访问') => {
  return error(res, message, 403);
};

module.exports = {
  success,
  error,
  notFound,
  serverError,
  unauthorized,
  forbidden
};
