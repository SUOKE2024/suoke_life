/**
 * 性能监控中间件
 * 用于跟踪API响应时间和资源使用情况
 */
const logger = require('../utils/logger');

/**
 * 响应时间追踪中间件
 * 记录每个请求的响应时间和相关信息
 */
const responseTimeMiddleware = (req, res, next) => {
  // 记录请求开始时间
  const start = process.hrtime();
  
  // 记录请求内存使用
  const startMemory = process.memoryUsage();
  
  // 当响应结束时计算时间差
  res.on('finish', () => {
    // 计算请求处理时间（毫秒）
    const diff = process.hrtime(start);
    const time = (diff[0] * 1e3 + diff[1] * 1e-6).toFixed(2);
    
    // 计算内存使用变化
    const endMemory = process.memoryUsage();
    const memoryDiff = {
      rss: ((endMemory.rss - startMemory.rss) / 1024 / 1024).toFixed(2) + ' MB',
      heapTotal: ((endMemory.heapTotal - startMemory.heapTotal) / 1024 / 1024).toFixed(2) + ' MB',
      heapUsed: ((endMemory.heapUsed - startMemory.heapUsed) / 1024 / 1024).toFixed(2) + ' MB'
    };
    
    // 获取请求信息
    const method = req.method;
    const url = req.originalUrl || req.url;
    const status = res.statusCode;
    const contentLength = res.get('content-length') || 0;
    const userAgent = req.get('user-agent') || '';
    
    // 只记录慢请求(超过500ms)或错误请求
    if (time > 500 || status >= 400) {
      logger.warn({
        message: `慢响应或错误: ${method} ${url}`,
        performance: {
          responseTime: `${time} ms`,
          status,
          contentLength: `${contentLength} bytes`,
          memoryDiff
        },
        request: {
          method,
          url,
          userAgent,
          ip: req.ip || req.ips
        }
      });
    } else {
      // 正常请求记录为调试信息
      logger.debug({
        message: `请求完成: ${method} ${url}`,
        performance: {
          responseTime: `${time} ms`,
          status,
          contentLength: `${contentLength} bytes`
        }
      });
    }
    
    // 将响应时间添加到响应头
    res.set('X-Response-Time', `${time} ms`);
  });
  
  next();
};

/**
 * 高负载检测中间件
 * 监控系统负载，当负载过高时发出警告
 */
const highLoadDetectionMiddleware = (req, res, next) => {
  // 获取当前CPU和内存使用情况
  const cpuUsage = process.cpuUsage();
  const memoryUsage = process.memoryUsage();
  
  // 如果堆内存使用超过80%，记录警告
  const heapUsedPercentage = (memoryUsage.heapUsed / memoryUsage.heapTotal) * 100;
  if (heapUsedPercentage > 80) {
    logger.warn({
      message: '内存使用过高警告',
      performance: {
        heapUsed: `${(memoryUsage.heapUsed / 1024 / 1024).toFixed(2)} MB`,
        heapTotal: `${(memoryUsage.heapTotal / 1024 / 1024).toFixed(2)} MB`,
        heapUsedPercentage: `${heapUsedPercentage.toFixed(2)}%`
      },
      request: {
        method: req.method,
        url: req.originalUrl || req.url
      }
    });
  }
  
  next();
};

/**
 * 核心指标中间件
 * 收集关键API性能指标
 */
const metricsCollectionMiddleware = (req, res, next) => {
  // 将指标收集逻辑添加到响应完成事件
  res.on('finish', () => {
    // 收集的指标可以后续通过Prometheus或其他监控工具导出
    // 此处仅记录不添加导出逻辑
    const metrics = {
      path: req.route ? req.route.path : req.path,
      method: req.method,
      statusCode: res.statusCode,
      timestamp: new Date()
    };
    
    // 在生产环境中可将指标发送到监控系统
    global.performanceMetrics = global.performanceMetrics || [];
    global.performanceMetrics.push(metrics);
    
    // 定期清理以避免内存泄漏
    if (global.performanceMetrics.length > 1000) {
      global.performanceMetrics = global.performanceMetrics.slice(-1000);
    }
  });
  
  next();
};

// 导出所有中间件
module.exports = {
  responseTimeMiddleware,
  highLoadDetectionMiddleware,
  metricsCollectionMiddleware
};