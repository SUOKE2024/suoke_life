/**
 * 响应处理工具模块
 * 提供统一的API响应格式
 */

/**
 * 成功响应
 * @param {Object} res - Express响应对象
 * @param {any} data - 响应数据
 * @param {string} message - 成功消息
 * @param {number} statusCode - HTTP状态码
 */
const success = (res, data = null, message = '操作成功', statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    message,
    data,
    timestamp: new Date().toISOString()
  });
};

/**
 * 错误响应
 * @param {Object} res - Express响应对象
 * @param {string} message - 错误消息
 * @param {number} statusCode - HTTP状态码
 * @param {Object} errors - 错误详情
 */
const error = (res, message = '操作失败', statusCode = 400, errors = null) => {
  return res.status(statusCode).json({
    success: false,
    message,
    errors,
    timestamp: new Date().toISOString()
  });
};

/**
 * 分页响应
 * @param {Object} res - Express响应对象
 * @param {Array} data - 数据项数组
 * @param {number} total - 总数据量
 * @param {number} page - 当前页码
 * @param {number} limit - 每页数据量
 * @param {string} message - 成功消息
 */
const paginated = (res, data = [], total = 0, page = 1, limit = 10, message = '获取成功') => {
  return res.status(200).json({
    success: true,
    message,
    data,
    pagination: {
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    },
    timestamp: new Date().toISOString()
  });
};

/**
 * 未授权响应
 * @param {Object} res - Express响应对象
 * @param {string} message - 错误消息
 */
const unauthorized = (res, message = '未授权访问') => {
  return error(res, message, 401);
};

/**
 * 禁止访问响应
 * @param {Object} res - Express响应对象
 * @param {string} message - 错误消息
 */
const forbidden = (res, message = '禁止访问') => {
  return error(res, message, 403);
};

/**
 * 未找到响应
 * @param {Object} res - Express响应对象
 * @param {string} message - 错误消息
 */
const notFound = (res, message = '资源未找到') => {
  return error(res, message, 404);
};

/**
 * 服务器错误响应
 * @param {Object} res - Express响应对象
 * @param {string} message - 错误消息
 */
const serverError = (res, message = '服务器内部错误') => {
  return error(res, message, 500);
};

// 导出响应处理工具
module.exports = {
  success,
  error,
  paginated,
  unauthorized,
  forbidden,
  notFound,
  serverError
}; 