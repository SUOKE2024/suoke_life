import { Request, Response, NextFunction } from 'express';
import * as client from 'prom-client';
import express from 'express';
import logger from '../utils/logger';

// 创建指标注册表
export const register = new client.Registry();

// 添加默认指标
client.collectDefaultMetrics({ register });

// HTTP请求计数器
export const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status']
});

// HTTP请求持续时间
export const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

// 活跃用户数
export const activeUsersGauge = new client.Gauge({
  name: 'active_users',
  help: 'Number of active users'
});

// 知识内容计数器
export const knowledgeContentCounter = new client.Counter({
  name: 'knowledge_content_total',
  help: 'Total number of knowledge content items',
  labelNames: ['type']
});

// 博客内容计数器
export const blogContentCounter = new client.Counter({
  name: 'blog_content_total',
  help: 'Total number of blog content items',
  labelNames: ['status']
});

// AI处理计数器
export const aiProcessingCounter = new client.Counter({
  name: 'ai_processing_total',
  help: 'Total number of AI processing operations',
  labelNames: ['type', 'status']
});

// AI处理持续时间
export const aiProcessingDuration = new client.Histogram({
  name: 'ai_processing_duration_seconds',
  help: 'AI processing duration in seconds',
  labelNames: ['type', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60, 120]
});

// 缓存命中率
export const cacheHitRatio = new client.Gauge({
  name: 'cache_hit_ratio',
  help: 'Cache hit ratio',
  labelNames: ['cache']
});

// 活跃媒体流
export const activeAudioStreamsGauge = new client.Gauge({
  name: 'active_audio_streams',
  help: 'Number of active audio streams'
});

// 活跃视频流
export const activeVideoStreamsGauge = new client.Gauge({
  name: 'active_video_streams',
  help: 'Number of active video streams'
});

// 媒体处理计数器
export const mediaProcessingCounter = new client.Counter({
  name: 'media_processing_total',
  help: 'Total number of media processing operations',
  labelNames: ['type', 'status']
});

// 方言处理计数器
export const dialectProcessingCounter = new client.Counter({
  name: 'dialect_processing_total',
  help: 'Total number of dialect processing operations',
  labelNames: ['dialect', 'operation', 'status']
});

// 注册指标
register.registerMetric(httpRequestCounter);
register.registerMetric(httpRequestDuration);
register.registerMetric(activeUsersGauge);
register.registerMetric(knowledgeContentCounter);
register.registerMetric(blogContentCounter);
register.registerMetric(aiProcessingCounter);
register.registerMetric(aiProcessingDuration);
register.registerMetric(cacheHitRatio);
register.registerMetric(activeAudioStreamsGauge);
register.registerMetric(activeVideoStreamsGauge);
register.registerMetric(mediaProcessingCounter);
register.registerMetric(dialectProcessingCounter);

/**
 * 设置指标监控服务
 */
export const setupMetrics = (port: number | string = 9465) => {
  const app = express();
  
  // 指标端点
  app.get('/metrics', async (req, res) => {
    try {
      res.set('Content-Type', register.contentType);
      res.end(await register.metrics());
    } catch (error) {
      logger.error('获取指标数据出错:', error);
      res.status(500).end();
    }
  });
  
  // 健康检查端点
  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
  });
  
  // 启动服务器
  const server = app.listen(port, () => {
    logger.info(`指标监控服务已启动在端口: ${port}`);
  });
  
  return server;
};

/**
 * 请求指标中间件
 */
export const metricsMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const path = req.path;
  const method = req.method;
  
  // 记录原始的响应结束方法
  const originalEnd = res.end;
  
  // 重写响应结束方法
  res.end = function() {
    // 获取执行时间
    const duration = Date.now() - start;
    
    // 获取状态码
    const statusCode = res.statusCode.toString();
    
    // 增加请求计数
    httpRequestCounter.inc({ method, route: path, status: statusCode });
    
    // 记录请求持续时间
    httpRequestDuration.observe({ method, route: path, status: statusCode }, duration / 1000);
    
    // 调用原始方法
    return originalEnd.apply(res, arguments as any);
  };
  
  next();
};

/**
 * 更新活动用户数
 */
export const updateActiveUsers = (count: number) => {
  activeUsersGauge.set(count);
};

/**
 * 更新知识内容数量
 */
export const updateKnowledgeContentTotal = (count: number) => {
  knowledgeContentCounter.inc({ type: 'total' });
};

/**
 * 更新博客内容数量
 */
export const updateBlogContentTotal = (count: number) => {
  blogContentCounter.inc({ status: 'total' });
};

/**
 * 记录AI处理操作
 */
export const recordAiProcessing = (type: string, status: string, durationMs: number) => {
  aiProcessingCounter.inc({ type, status });
  aiProcessingDuration.observe({ type, status }, durationMs / 1000);
};

/**
 * 更新缓存命中率
 */
export const updateCacheHitRatio = (cache: string, hits: number, total: number) => {
  if (total > 0) {
    cacheHitRatio.set({ cache }, hits / total);
  }
};

/**
 * 记录媒体处理
 */
export const recordMediaProcessing = (type: string, status: string, durationMs: number) => {
  mediaProcessingCounter.inc({ type, status });
  aiProcessingDuration.observe({ type, status }, durationMs / 1000);
};

/**
 * 记录方言处理
 */
export const recordDialectProcessing = (dialect: string, operation: string, status: string, durationMs: number) => {
  dialectProcessingCounter.inc({ dialect, operation, status });
  aiProcessingDuration.observe({ type: `dialect_${operation}`, status }, durationMs / 1000);
};

export {
  register,
  httpRequestCounter,
  httpRequestDuration,
  activeUsersGauge,
  knowledgeContentCounter,
  blogContentCounter,
  aiProcessingCounter,
  aiProcessingDuration,
  cacheHitRatio,
  activeAudioStreamsGauge,
  activeVideoStreamsGauge,
  mediaProcessingCounter,
  dialectProcessingCounter
};