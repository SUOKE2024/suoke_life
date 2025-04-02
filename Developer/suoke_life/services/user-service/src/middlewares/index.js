/**
 * 中间件索引文件
 * 导出所有中间件
 */
const errorMiddleware = require('./error.middleware');
const errorHandlerMiddleware = require('./error-handler.middleware');
const authMiddleware = require('./auth.middleware');
const validationMiddleware = require('./validation.middleware');
const rbacMiddleware = require('./rbac.middleware');
const rateLimitMiddleware = require('./rate-limit.middleware');
const i18nMiddleware = require('./i18n.middleware');
const loggingMiddleware = require('./logging.middleware');
const { 
  responseTimeMiddleware,
  highLoadDetectionMiddleware,
  metricsCollectionMiddleware 
} = require('./performance.middleware');

module.exports = {
  errorMiddleware,
  errorHandlerMiddleware,
  authMiddleware,
  validationMiddleware,
  rbacMiddleware,
  rateLimitMiddleware,
  i18nMiddleware,
  loggingMiddleware,
  // 性能监控中间件
  responseTimeMiddleware,
  highLoadDetectionMiddleware,
  metricsCollectionMiddleware
}; 