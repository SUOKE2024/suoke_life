/**
 * 索儿服务主应用
 */
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');

const config = require('./config');
const logger = require('./utils/logger');
const { httpRequestTimer, metricsHandler } = require('./metrics');
const healthRoutes = require('./routes/health');

// 创建Express应用
const app = express();

// 基本安全中间件
app.use(helmet());

// CORS配置
app.use(cors(config.cors));

// 内容压缩
app.use(compression());

// 请求解析
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// 日志中间件
app.use(logger.requestContextMiddleware);

// 指标收集中间件
app.use(httpRequestTimer);

// 速率限制
app.use(rateLimit(config.rateLimit));

// 暴露指标端点
app.get('/metrics', metricsHandler);

// 健康检查路由
app.use('/', healthRoutes);

// API路由
app.use('/api', require('./routes/api'));

// 错误处理中间件
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  
  // 记录错误
  logger.error(`请求处理错误: ${err.message}`, {
    stack: err.stack,
    path: req.path,
    method: req.method,
    status_code: statusCode,
    request_id: req.requestId,
    trace_id: req.traceId
  });
  
  // 发送错误响应
  res.status(statusCode).json({
    error: {
      message: err.message,
      code: err.code || 'INTERNAL_ERROR',
      request_id: req.requestId
    }
  });
});

// 未找到路由处理
app.use((req, res) => {
  res.status(404).json({
    error: {
      message: '请求的资源不存在',
      code: 'NOT_FOUND',
      request_id: req.requestId
    }
  });
});

module.exports = app;