/**
 * 指标中间件
 */
const metricsService = require('../services/metrics.service');

/**
 * HTTP请求指标中间件
 * @param {Object} req - Express请求对象
 * @param {Object} res - Express响应对象
 * @param {Function} next - Express下一个中间件函数
 */
function metricsMiddleware(req, res, next) {
  // 记录请求开始时间
  const endTimer = metricsService.startTimer('http_request_duration', {
    method: req.method,
    path: req.route ? req.route.path : req.path,
  });

  // 增加请求计数
  metricsService.increment('http_requests_total', {
    method: req.method,
    path: req.route ? req.route.path : req.path,
  });

  // 记录原始end方法
  const originalEnd = res.end;

  // 重写end方法
  res.end = function(...args) {
    // 调用原始end方法
    originalEnd.apply(res, args);

    // 结束计时器并记录指标
    const duration = endTimer();

    // 记录响应状态码
    metricsService.increment('http_responses_total', {
      method: req.method,
      path: req.route ? req.route.path : req.path,
      status: res.statusCode
    });

    // 如果响应状态码为错误，记录错误指标
    if (res.statusCode >= 400) {
      metricsService.increment('http_errors_total', {
        method: req.method,
        path: req.route ? req.route.path : req.path,
        status: res.statusCode
      });
    }

    // 记录活跃连接数量
    metricsService.gauge('http_active_connections', 
      metricsService.metrics.gauges.get('http_active_connections') - 1 || 0);
  };

  // 记录活跃连接数量
  metricsService.gauge('http_active_connections', 
    (metricsService.metrics.gauges.get('http_active_connections') || 0) + 1);

  next();
}

module.exports = metricsMiddleware;
