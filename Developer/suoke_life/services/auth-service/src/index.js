/**
 * 索克生活认证服务
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const { logger } = require('@suoke/shared').utils;
const prometheusClient = require('prom-client');
const { vaultService } = require('./services/vault.service');
const { initialize: initializeSync } = require('./utils/sync');
const { initDatabase } = require('./config/database-init');

// 创建Express应用
const app = express();

// 配置Prometheus指标收集
const collectDefaultMetrics = prometheusClient.collectDefaultMetrics;
collectDefaultMetrics({ 
  prefix: 'auth_service_',
  labels: {
    service: 'auth-service',
    region: process.env.POD_REGION || 'unknown',
    instance: require('os').hostname()
  }
});

// HTTP请求计数器
const httpRequestsTotal = new prometheusClient.Counter({
  name: 'auth_service_http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status']
});

// HTTP请求持续时间
const httpRequestDurationMicroseconds = new prometheusClient.Histogram({
  name: 'auth_service_http_request_duration_ms',
  help: 'Duration of HTTP requests in ms',
  labelNames: ['method', 'route', 'status'],
  buckets: [1, 5, 15, 50, 100, 200, 300, 400, 500, 1000, 2000, 5000, 10000]
});

// 应用程序中间件
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// 请求计时中间件
app.use((req, res, next) => {
  const start = Date.now();
  
  // 捕获响应完成事件
  res.on('finish', () => {
    const duration = Date.now() - start;
    httpRequestsTotal.inc({ 
      method: req.method, 
      route: req.route ? req.route.path : req.path, 
      status: res.statusCode 
    });
    httpRequestDurationMicroseconds.observe(
      { 
        method: req.method, 
        route: req.route ? req.route.path : req.path, 
        status: res.statusCode 
      },
      duration
    );
  });
  
  next();
});

// 健康检查端点
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.get('/health/ready', async (req, res) => {
  const healthChecks = require('./utils/health-checks');
  const result = await healthChecks.checkReadiness();
  
  if (result.status === 'UP') {
    return res.status(200).json(result);
  } else {
    return res.status(503).json(result);
  }
});

app.get('/health/startup', async (req, res) => {
  const healthChecks = require('./utils/health-checks');
  const result = await healthChecks.checkStartup();
  
  if (result.status === 'UP') {
    return res.status(200).json({ status: 'ready' });
  } else {
    return res.status(503).json({ status: 'not_ready', reason: result.reason });
  }
});

// 添加通用健康检查路由，符合Kubernetes配置
app.get('/health', async (req, res) => {
  const healthChecks = require('./utils/health-checks');
  const result = await healthChecks.checkLiveness();
  
  return res.status(200).json(result);
});

// 指标端点
app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', prometheusClient.register.contentType);
    const metrics = await prometheusClient.register.metrics();
    res.end(metrics);
  } catch (error) {
    logger.error(`获取指标失败: ${error.message}`);
    res.status(500).end();
  }
});

// 注册API路由
app.use('/api/v1/auth', require('./routes/auth'));
app.use('/api/v1/users', require('./routes/users'));
app.use('/api/v1/oauth', require('./routes/oauth'));
app.use('/api/v1/internal', require('./routes/internal'));

// 错误处理中间件
app.use((err, req, res, next) => {
  logger.error(`应用错误: ${err.message}`);
  logger.error(err.stack);
  
  const statusCode = err.statusCode || 500;
  const errorMessage = process.env.NODE_ENV === 'production' && statusCode === 500
    ? '服务器内部错误'
    : err.message;
  
  res.status(statusCode).json({
    success: false,
    message: errorMessage
  });
});

// 获取端口号
const PORT = process.env.PORT || 3000;

// 启动服务器
let server;

const startServer = async () => {
  try {
    // 初始化Vault服务
    if (process.env.VAULT_ENABLED === 'true') {
      logger.info('初始化Vault服务...');
      await vaultService.refreshSecrets();
    }
    
    // 初始化数据库表结构
    logger.info('初始化数据库表结构...');
    await initDatabase();
    
    // 初始化跨区域同步服务
    logger.info('初始化跨区域同步服务...');
    await initializeSync();
    
    // 启动服务器
    server = app.listen(PORT, () => {
      logger.info(`认证服务已启动，监听端口 ${PORT}`);
    });
    
    // 添加优雅关闭逻辑
    setupGracefulShutdown(server);
  } catch (error) {
    logger.error(`服务启动失败: ${error.message}`);
    process.exit(1);
  }
};

// 优雅关闭函数
const setupGracefulShutdown = (server) => {
  // 处理进程信号
  const signals = ['SIGINT', 'SIGTERM', 'SIGQUIT'];
  
  signals.forEach(signal => {
    process.on(signal, async () => {
      logger.info(`收到 ${signal} 信号，准备优雅关闭...`);
      
      // 标记应用程序为关闭状态
      app.set('shutting_down', true);
      
      // 尝试关闭服务器
      server.close(async (err) => {
        if (err) {
          logger.error(`关闭HTTP服务器出错: ${err.message}`);
          process.exit(1);
        }
        
        try {
          // 关闭数据库连接
          const { closeConnection } = require('./config/database');
          await closeConnection();
          logger.info('数据库连接已关闭');
          
          // 关闭Redis连接
          const redis = require('./config/redis');
          await redis.quit();
          logger.info('Redis连接已关闭');
          
          logger.info('所有连接已安全关闭，退出进程');
          process.exit(0);
        } catch (error) {
          logger.error(`关闭连接出错: ${error.message}`);
          process.exit(1);
        }
      });
      
      // 设置超时，确保在一定时间内关闭
      setTimeout(() => {
        logger.error('强制关闭进程 - 超过关闭超时');
        process.exit(1);
      }, 30000); // 30秒超时
    });
  });
};

// 启动服务器
startServer();

module.exports = app; // 导出供测试使用 