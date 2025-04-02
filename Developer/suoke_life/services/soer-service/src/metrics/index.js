/**
 * 索儿服务指标收集模块
 * 提供 Prometheus 格式的指标收集和导出功能
 */
const promClient = require('prom-client');
const config = require('../config');
const logger = require('../utils/logger');

// 创建默认注册表
const register = new promClient.Registry();

// 配置默认指标
promClient.collectDefaultMetrics({
  register,
  prefix: 'soer_',
  labels: { service: 'soer-service' }
});

// 定义计数器
const counters = {
  httpRequestsTotal: new promClient.Counter({
    name: 'soer_http_requests_total',
    help: '处理的HTTP请求总数',
    labelNames: ['method', 'path', 'status'],
    registers: [register]
  }),
  
  databaseQueriesTotal: new promClient.Counter({
    name: 'soer_database_queries_total',
    help: '执行的数据库查询总数',
    labelNames: ['type', 'table', 'status'],
    registers: [register]
  }),
  
  healthChecksTotal: new promClient.Counter({
    name: 'soer_health_checks_total',
    help: '健康检查请求总数',
    labelNames: ['type'],
    registers: [register]
  }),
  
  errorTotal: new promClient.Counter({
    name: 'soer_errors_total',
    help: '产生的错误总数',
    labelNames: ['module', 'code'],
    registers: [register]
  }),
  
  businessOperationsTotal: new promClient.Counter({
    name: 'soer_business_operations_total',
    help: '业务操作总数',
    labelNames: ['operation', 'status'],
    registers: [register]
  })
};

// 定义测量指标
const gauges = {
  activeConnections: new promClient.Gauge({
    name: 'soer_active_connections',
    help: '当前活跃连接数',
    labelNames: ['type'],
    registers: [register]
  }),
  
  jobQueueSize: new promClient.Gauge({
    name: 'soer_job_queue_size',
    help: '当前任务队列大小',
    labelNames: ['queue'],
    registers: [register]
  }),
  
  resourceUsage: new promClient.Gauge({
    name: 'soer_resource_usage',
    help: '资源使用情况',
    labelNames: ['resource'],
    registers: [register]
  }),
  
  cacheHitRatio: new promClient.Gauge({
    name: 'soer_cache_hit_ratio',
    help: '缓存命中率',
    labelNames: ['cache'],
    registers: [register]
  })
};

// 定义直方图
const histograms = {
  httpRequestDuration: new promClient.Histogram({
    name: 'soer_http_request_duration_seconds',
    help: 'HTTP请求处理时间直方图',
    labelNames: ['method', 'path', 'status'],
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
    registers: [register]
  }),
  
  databaseQueryDuration: new promClient.Histogram({
    name: 'soer_database_query_duration_seconds',
    help: '数据库查询时间直方图',
    labelNames: ['type', 'table'],
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
    registers: [register]
  }),
  
  externalServiceDuration: new promClient.Histogram({
    name: 'soer_external_service_duration_seconds',
    help: '外部服务调用时间直方图',
    labelNames: ['service', 'operation'],
    buckets: [0.05, 0.1, 0.5, 1, 2, 5, 10, 30],
    registers: [register]
  })
};

// 增加计数器
function incrementCounter(name, labels = {}) {
  if (counters[name]) {
    counters[name].inc(labels);
  } else {
    logger.warn(`尝试增加不存在的计数器: ${name}`);
  }
}

// 设置测量值
function setGauge(name, value, labels = {}) {
  if (gauges[name]) {
    gauges[name].set(labels, value);
  } else {
    logger.warn(`尝试设置不存在的测量值: ${name}`);
  }
}

// 观察直方图值
function observeHistogram(name, value, labels = {}) {
  if (histograms[name]) {
    histograms[name].observe(labels, value);
  } else {
    logger.warn(`尝试观察不存在的直方图: ${name}`);
  }
}

// HTTP请求计时中间件
function httpRequestTimer(req, res, next) {
  const start = Date.now();
  
  // 为响应添加一个结束监听器
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000; // 转换为秒
    const path = req.route ? req.route.path : req.path;
    
    // 记录请求计数
    incrementCounter('httpRequestsTotal', {
      method: req.method,
      path,
      status: res.statusCode
    });
    
    // 记录请求持续时间
    observeHistogram('httpRequestDuration', duration, {
      method: req.method, 
      path,
      status: res.statusCode
    });
  });
  
  next();
}

// 指标路由处理程序
function metricsHandler(req, res) {
  res.set('Content-Type', register.contentType);
  register.metrics().then(metrics => {
    res.end(metrics);
  }).catch(err => {
    logger.error('生成指标时出错', { error: err.message });
    res.status(500).end('指标生成失败');
  });
}

// 导出模块
module.exports = {
  register,
  counters,
  gauges,
  histograms,
  incrementCounter,
  setGauge,
  observeHistogram,
  httpRequestTimer,
  metricsHandler
};