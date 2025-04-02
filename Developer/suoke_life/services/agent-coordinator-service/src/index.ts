/**
 * 代理协调器服务入口文件
 */
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import swaggerUi from 'swagger-ui-express';
import routes from './routes';
import { setupRedisConnection } from './services/redis-service';
import { loadConfig } from './utils/config-loader';
import logger from './utils/logger';
import { swaggerSpec } from './utils/swagger';
import { handleError } from './utils/error-handler';
import { metricsMiddleware } from './utils/metrics';

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3007;

// 加载配置
const config = loadConfig();

// 安全中间件
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 指标监控中间件
app.use(metricsMiddleware);

// 请求日志
if (config.logging.enableRequestLogging) {
  app.use(morgan('combined', {
    stream: {
      write: (message: string) => {
        logger.info(message.trim());
      },
    },
  }));
}

// 速率限制
if (config.security.rateLimiting.enabled) {
  app.use(
    rateLimit({
      windowMs: 60 * 1000,
      max: config.security.rateLimiting.maxRequestsPerMinute,
      message: '请求频率过高，请稍后再试',
      standardHeaders: true,
      legacyHeaders: false,
    })
  );
}

// Swagger API文档
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  explorer: true,
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: '代理协调器服务 API 文档',
}));

// 指标监控API
app.get('/metrics', (req, res) => {
  const metrics = require('./utils/metrics').metricsCollector.getMetrics();
  res.status(200).json(metrics);
});

// 健康检查路由
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    timestamp: new Date().toISOString(),
    service: 'agent-coordinator-service',
    version: process.env.npm_package_version || '1.2.0',
  });
});

app.get('/ready', (req, res) => {
  res.status(200).json({
    status: 'READY',
    timestamp: new Date().toISOString(),
  });
});

// API路由
app.use('/api', routes);

// 错误处理中间件
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  handleError(err, res);
});

// 404处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: '未找到请求的资源',
    }
  });
});

// 启动服务器
const startServer = async () => {
  try {
    // 初始化Redis连接
    if (process.env.AGENT_STATE_PERSISTENCE === 'redis') {
      await setupRedisConnection();
      logger.info('Redis连接已建立');
    }
    
    app.listen(PORT, () => {
      logger.info(`代理协调器服务启动成功，端口: ${PORT}`);
      logger.info(`API文档可访问: http://localhost:${PORT}/api-docs`);
      logger.info(`指标监控可访问: http://localhost:${PORT}/metrics`);
    });
  } catch (error) {
    logger.error('服务启动失败', { error });
    process.exit(1);
  }
};

// 处理未捕获的异常和拒绝的Promise
process.on('uncaughtException', (error) => {
  logger.error(`未捕获的异常: ${error.message}`, { error });
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error(`未处理的Promise拒绝`, { reason, promise });
});

// 优雅关闭
process.on('SIGTERM', () => {
  logger.info('收到SIGTERM信号，准备关闭服务器');
  process.exit(0);
});

// 启动服务器
startServer();