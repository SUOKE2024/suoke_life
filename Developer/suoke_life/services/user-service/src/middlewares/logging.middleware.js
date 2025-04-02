/**
 * 日志中间件
 * 提供请求日志和错误日志功能
 */
const { createRequestLogger } = require('../utils/logger');

// 创建请求日志中间件
const requestLogger = createRequestLogger();

module.exports = {
  requestLogger
}; 