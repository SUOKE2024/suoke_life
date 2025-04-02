/**
 * 中间件模块索引
 * 导出所有中间件模块
 */

// 导入中间件模块
const auth = require('./auth.middleware');
const error = require('./error.middleware');

/**
 * 导出所有中间件模块
 */
module.exports = {
  auth,
  error
}; 