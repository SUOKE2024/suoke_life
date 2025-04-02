import express from 'express';
import http from 'http';
import client from 'prom-client';
import { logger } from '../../utils/logger';

// 创建默认的注册表
export const register = new client.Registry();

// 添加默认指标
client.collectDefaultMetrics({
  prefix: 'xiaoke_',
  register
});

// HTTP请求计数器
export const httpRequestsTotal = new client.Counter({
  name: 'xiaoke_http_requests_total',
  help: '总HTTP请求数',
  labelNames: ['method', 'path', 'status'] as const,
  registers: [register]
});

// HTTP请求持续时间
export const httpRequestDurationSeconds = new client.Histogram({
  name: 'xiaoke_http_request_duration_seconds',
  help: 'HTTP请求持续时间(秒)',
  labelNames: ['method', 'path', 'status'] as const,
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
  registers: [register]
});

// 供应链产品查询计数器
export const productQueryCounter = new client.Counter({
  name: 'xiaoke_product_queries_total',
  help: '产品信息查询总数',
  labelNames: ['product_type', 'source', 'result'] as const,
  registers: [register]
});

// 订单处理计数器
export const orderProcessCounter = new client.Counter({
  name: 'xiaoke_order_processing_total',
  help: '订单处理总数',
  labelNames: ['order_type', 'status'] as const,
  registers: [register]
});

// 订单处理时间
export const orderProcessingTimeSeconds = new client.Histogram({
  name: 'xiaoke_order_processing_seconds',
  help: '订单处理时间(秒)',
  labelNames: ['order_type'] as const,
  buckets: [1, 5, 15, 30, 60, 120, 300, 600],
  registers: [register]
});

// 产品库存数量
export const productInventoryGauge = new client.Gauge({
  name: 'xiaoke_product_inventory',
  help: '产品库存数量',
  labelNames: ['product_id', 'product_name', 'category'] as const,
  registers: [register]
});

// 节气食材推荐查询
export const seasonalRecommendationCounter = new client.Counter({
  name: 'xiaoke_seasonal_recommendations_total',
  help: '节气食材推荐查询总数',
  labelNames: ['solar_term', 'season', 'constitution'] as const,
  registers: [register]
});

// 服务订阅计数器
export const serviceSubscriptionCounter = new client.Counter({
  name: 'xiaoke_service_subscriptions_total',
  help: '服务订阅总数',
  labelNames: ['service_type', 'duration', 'status'] as const,
  registers: [register]
});

// 农事活动计数器
export const farmActivityCounter = new client.Counter({
  name: 'xiaoke_farm_activities_total',
  help: '农事活动预订总数',
  labelNames: ['activity_type', 'location', 'status'] as const,
  registers: [register]
});

// 初始化指标服务器
export const setupMetrics = (app: express.Application, metricsPort: number | string): http.Server => {
  const port = Number(metricsPort);
  const metricsApp = express();
  
  // 仅导出指标端点
  metricsApp.get('/metrics', async (req, res) => {
    try {
      res.set('Content-Type', register.contentType);
      res.end(await register.metrics());
    } catch (error) {
      logger.error('获取指标失败:', error);
      res.status(500).end();
    }
  });
  
  // 健康检查端点
  metricsApp.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', service: 'xiaoke-metrics' });
  });
  
  // 启动专用的指标服务器
  const server = metricsApp.listen(port, () => {
    logger.info(`指标服务器监听端口 ${port}`);
  });
  
  // 为主应用添加指标中间件
  app.use((req, res, next) => {
    const start = Date.now();
    
    // 记录请求结束和持续时间
    res.on('finish', () => {
      const duration = (Date.now() - start) / 1000;
      const path = req.path || req.url || '/unknown';
      const method = req.method;
      const status = res.statusCode.toString();
      
      httpRequestsTotal.inc({ method, path, status });
      httpRequestDurationSeconds.observe(
        { method, path, status },
        duration
      );
    });
    
    next();
  });
  
  return server;
};

export default {
  register,
  httpRequestsTotal,
  httpRequestDurationSeconds,
  productQueryCounter,
  orderProcessCounter,
  orderProcessingTimeSeconds,
  productInventoryGauge,
  seasonalRecommendationCounter,
  serviceSubscriptionCounter,
  farmActivityCounter,
  setupMetrics
}; 