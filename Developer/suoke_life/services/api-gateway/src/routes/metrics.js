/**
 * 监控指标路由
 */
const express = require('express');
const router = express.Router();
const os = require('os');
const responseCache = require('../utils/response-cache');
const { getAllCircuitBreakersStatus } = require('../middlewares/circuit-breaker');

/**
 * 获取系统基本信息
 */
function getSystemInfo() {
  return {
    hostname: os.hostname(),
    platform: os.platform(),
    arch: os.arch(),
    cpus: os.cpus().length,
    loadavg: os.loadavg(),
    totalmem: os.totalmem(),
    freemem: os.freemem(),
    uptime: os.uptime()
  };
}

/**
 * 获取进程指标
 */
function getProcessMetrics() {
  const memoryUsage = process.memoryUsage();
  
  return {
    uptime: process.uptime(),
    memory: {
      rss: memoryUsage.rss, // 常驻集大小
      heapTotal: memoryUsage.heapTotal, // 总堆大小
      heapUsed: memoryUsage.heapUsed, // 已用堆大小
      external: memoryUsage.external, // 外部内存
      arrayBuffers: memoryUsage.arrayBuffers || 0
    },
    cpu: process.cpuUsage()
  };
}

/**
 * 获取请求统计信息
 */
function getRequestStats(req) {
  // 从应用上下文获取请求统计信息
  const stats = req.app.get('requestStats') || {
    total: 0,
    byMethod: {},
    byPath: {},
    byStatus: {},
    errors: 0
  };
  
  return stats;
}

/**
 * @route GET /metrics
 * @description 获取API网关监控指标
 * @access 需要管理员权限
 */
router.get('/', (req, res) => {
  const system = getSystemInfo();
  const process = getProcessMetrics();
  const requestStats = getRequestStats(req);
  const cacheStats = responseCache.getStats();
  const circuitBreakers = getAllCircuitBreakersStatus();
  
  // 从应用上下文获取服务负载均衡器
  const serviceLBMap = req.app.get('serviceLBMap') || new Map();
  const serviceStats = {};
  
  // 收集各服务负载均衡状态
  for (const [serviceName, lb] of serviceLBMap.entries()) {
    serviceStats[serviceName] = {
      urls: lb.urls,
      strategy: lb.strategy,
      totalRequests: lb.getTotalRequests ? lb.getTotalRequests() : 0,
      urlStats: lb.getUrlStats ? lb.getUrlStats() : {}
    };
  }
  
  // 返回所有指标
  res.json({
    timestamp: new Date().toISOString(),
    system,
    process,
    requests: requestStats,
    cache: cacheStats,
    circuitBreakers,
    services: serviceStats
  });
});

/**
 * @route GET /metrics/system
 * @description 获取系统指标
 * @access 需要管理员权限
 */
router.get('/system', (req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    system: getSystemInfo(),
    process: getProcessMetrics()
  });
});

/**
 * @route GET /metrics/requests
 * @description 获取请求统计指标
 * @access 需要管理员权限
 */
router.get('/requests', (req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    requests: getRequestStats(req)
  });
});

/**
 * @route GET /metrics/cache
 * @description 获取缓存统计信息
 * @access 需要管理员权限
 */
router.get('/cache', (req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    cache: responseCache.getStats()
  });
});

/**
 * @route POST /metrics/cache/clear
 * @description 清空缓存
 * @access 需要管理员权限
 */
router.post('/cache/clear', (req, res) => {
  responseCache.clear();
  res.json({
    message: '缓存已清空',
    timestamp: new Date().toISOString()
  });
});

/**
 * @route POST /metrics/cache/clear/:prefix
 * @description 按前缀清空缓存
 * @access 需要管理员权限
 */
router.post('/cache/clear/:prefix', (req, res) => {
  const prefix = req.params.prefix;
  const count = responseCache.clearByPrefix(prefix);
  
  res.json({
    message: `已清空前缀为 "${prefix}" 的 ${count} 条缓存`,
    timestamp: new Date().toISOString()
  });
});

/**
 * @route GET /metrics/circuit-breakers
 * @description 获取断路器状态
 * @access 需要管理员权限
 */
router.get('/circuit-breakers', (req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    circuitBreakers: getAllCircuitBreakersStatus()
  });
});

/**
 * @route GET /metrics/services/agent-coordinator
 * @description 获取代理协调器服务的监控指标
 * @access 需要管理员权限
 */
router.get('/services/agent-coordinator', (req, res) => {
  // 从应用上下文获取服务负载均衡器
  const serviceLBMap = req.app.get('serviceLBMap') || new Map();
  const coordinatorLB = serviceLBMap.get('agent-coordinator-service');
  
  // 获取断路器状态
  const circuitBreakers = getAllCircuitBreakersStatus();
  const circuitBreakerStatus = circuitBreakers['agent-coordinator-service'] || {
    state: 'UNKNOWN',
    failureCount: 0,
    successCount: 0,
    isAllowed: true
  };
  
  // 构建响应
  const coordinatorStats = {
    service: 'agent-coordinator-service',
    timestamp: new Date().toISOString(),
    availability: circuitBreakerStatus.isAllowed ? 'available' : 'unavailable',
    circuitBreakerState: circuitBreakerStatus.state,
    urls: coordinatorLB ? coordinatorLB.urls : [],
    metrics: {
      totalRequests: coordinatorLB ? (coordinatorLB.getTotalRequests ? coordinatorLB.getTotalRequests() : 0) : 0,
      urlStats: coordinatorLB ? (coordinatorLB.getUrlStats ? coordinatorLB.getUrlStats() : {}) : {},
      failureCount: circuitBreakerStatus.failureCount,
      successCount: circuitBreakerStatus.successCount
    }
  };
  
  res.json(coordinatorStats);
});

module.exports = router;