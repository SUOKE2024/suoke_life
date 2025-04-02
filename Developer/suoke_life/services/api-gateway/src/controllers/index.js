/**
 * 控制器模块
 */
const express = require('express');
const router = express.Router();
const os = require('os');
const process = require('process');
const prometheusClient = require('prom-client');
const config = require('../config');
const logger = require('../utils/logger');

// 初始化Prometheus指标收集
const register = new prometheusClient.Registry();
prometheusClient.collectDefaultMetrics({ register });

// 自定义指标
const httpRequestCounter = new prometheusClient.Counter({
  name: 'api_gateway_http_requests_total',
  help: 'HTTP请求总数',
  labelNames: ['method', 'path', 'status'],
  registers: [register]
});

const httpRequestDuration = new prometheusClient.Histogram({
  name: 'api_gateway_http_request_duration_seconds',
  help: '请求处理时间分布',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
  registers: [register]
});

/**
 * 健康检查控制器
 */
exports.healthCheck = (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: config.service.name,
    version: config.service.version,
    timestamp: new Date().toISOString()
  });
};

/**
 * 就绪检查控制器
 */
exports.readinessCheck = (req, res) => {
  // 获取所有服务的可用性状态
  const serviceLBMap = req.app.get('serviceLBMap') || new Map();
  const serviceStatus = {};

  for (const [serviceName, lb] of serviceLBMap.entries()) {
    serviceStatus[serviceName] = {
      available: lb.getHealthyCount() > 0,
      healthy: lb.getHealthyCount(),
      total: lb.urls.length,
      percentage: Math.floor((lb.getHealthyCount() / lb.urls.length) * 100)
    };
  }

  res.status(200).json({
    status: 'ready',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    services: serviceStatus
  });
};

/**
 * 指标收集控制器
 */
exports.getMetrics = async (req, res) => {
  try {
    const metrics = await register.metrics();
    res.set('Content-Type', register.contentType);
    res.end(metrics);
  } catch (err) {
    logger.error('获取指标失败:', err);
    res.status(500).json({ error: '获取指标失败' });
  }
};

/**
 * 系统信息控制器
 */
exports.getSystemInfo = (req, res) => {
  const memory = process.memoryUsage();
  const cpuUsage = process.cpuUsage();
  
  res.json({
    system: {
      hostname: os.hostname(),
      platform: os.platform(),
      arch: os.arch(),
      cpus: os.cpus().length,
      loadavg: os.loadavg(),
      totalmem: os.totalmem(),
      freemem: os.freemem(),
      uptime: os.uptime()
    },
    process: {
      uptime: process.uptime(),
      pid: process.pid,
      memory: {
        rss: memory.rss,
        heapTotal: memory.heapTotal,
        heapUsed: memory.heapUsed,
        external: memory.external,
        arrayBuffers: memory.arrayBuffers
      },
      cpu: {
        user: cpuUsage.user,
        system: cpuUsage.system
      },
      versions: process.versions
    }
  });
};

/**
 * 请求计数中间件
 */
exports.requestCounterMiddleware = (req, res, next) => {
  // 记录请求开始时间
  const start = Date.now();
  
  // 在响应完成时记录指标
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000; // 转换为秒
    const method = req.method;
    const path = req.route ? req.route.path : req.path;
    const status = res.statusCode;
    const statusGroup = Math.floor(status / 100) + 'xx';
    
    // 统计请求总数
    httpRequestCounter.inc({ method, path, status: statusGroup }, 1);
    
    // 统计请求时间
    httpRequestDuration.observe({ method, path, status: statusGroup }, duration);
  });
  
  next();
};

// 导出其他控制器
exports.router = router;