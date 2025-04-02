import express from 'express';
import client from 'prom-client';

// 创建指标注册表
const register = new client.Registry();

// 添加默认指标
client.collectDefaultMetrics({ register });

// 创建HTTP请求计数器
const httpRequestsTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status'],
  registers: [register],
});

// 创建HTTP请求持续时间直方图
const httpRequestDurationSeconds = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
  registers: [register],
});

// 创建AI调用计数器
const aiCallsTotal = new client.Counter({
  name: 'ai_calls_total',
  help: 'Total number of AI model calls',
  labelNames: ['model', 'status'],
  registers: [register],
});

// 创建AI调用持续时间直方图
const aiCallDurationSeconds = new client.Histogram({
  name: 'ai_call_duration_seconds',
  help: 'AI model call duration in seconds',
  labelNames: ['model'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60],
  registers: [register],
});

// 创建批处理大小直方图
const batchSizeHistogram = new client.Histogram({
  name: 'batch_size',
  help: 'Batch size for processing',
  buckets: [1, 2, 4, 8, 16],
  registers: [register],
});

// 导出指标和注册表
export {
  register,
  httpRequestsTotal,
  httpRequestDurationSeconds,
  aiCallsTotal,
  aiCallDurationSeconds,
  batchSizeHistogram,
};

// 指标中间件
export const metricsMiddleware = (app: express.Application): void => {
  // 为每个请求添加指标
  app.use((req, res, next) => {
    // 跳过指标端点本身
    if (req.path === '/metrics') {
      return next();
    }

    const start = Date.now();

    // 请求完成后记录指标
    res.on('finish', () => {
      const duration = Date.now() - start;
      const route = req.route ? req.route.path : req.path;
      const method = req.method;
      const status = res.statusCode;

      // 记录请求计数
      httpRequestsTotal.inc({ method, route, status });
      
      // 记录请求持续时间
      httpRequestDurationSeconds.observe(
        { method, route, status },
        duration / 1000
      );
    });

    next();
  });

  // 添加指标端点
  app.get('/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  });
};