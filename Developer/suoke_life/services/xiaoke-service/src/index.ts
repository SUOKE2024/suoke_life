import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { setupMetrics, recordMetric } from './utils/metrics';
import { setupRoutes } from './core/routes';
import { errorMiddleware } from './core/middleware/error.middleware';
import { requestLoggerMiddleware } from './core/middleware/request-logger.middleware';
import { setupAgentSystem } from './core/agent';
import { connectToDatabase } from './core/database';
import { setupRedisClient } from './core/cache';
import { logger } from './utils/logger';
import { setupOpenTelemetry } from './utils/telemetry';
import { getSecretFromVault, setupVault } from './utils/vault';
import fs from 'fs';
import path from 'path';

// 加载环境变量
dotenv.config();

// 初始化日志记录器
const logger = logger('app');

// 应用程序初始化
async function initializeApp() {
  try {
    // 设置OpenTelemetry
    await setupOpenTelemetry();
    logger.info('OpenTelemetry initialized');

    // 设置Vault(如果启用)
    if (process.env.USE_VAULT === 'true') {
      await setupVault();
      logger.info('Vault initialized');
    }

    // 初始化指标
    const metricsRegistry = setupMetrics();
    logger.info('Metrics initialized');

    // 创建Express应用
    const app = express();
    const PORT = process.env.PORT || 3011;
    const METRICS_PORT = process.env.METRICS_PORT || 9464;

    // 创建HTTP服务器和WebSocket
    const httpServer = createServer(app);
    const io = new Server(httpServer, {
      cors: {
        origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : '*',
        methods: ['GET', 'POST'],
        credentials: true
      }
    });

    // 设置中间件
    app.use(cors({
      origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : '*',
      credentials: true
    }));
    app.use(express.json({ limit: '50mb' }));
    app.use(express.urlencoded({ extended: true, limit: '50mb' }));
    app.use(requestLoggerMiddleware);

    // 请求日志中间件
    app.use((req: Request, res: Response, next: NextFunction) => {
      const start = Date.now();
      
      res.on('finish', () => {
        const duration = Date.now() - start;
        logger.info(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
        
        // 记录请求指标
        recordMetric('xiaoke_requests_total', 1, { 
          method: req.method, 
          path: req.path, 
          status: res.statusCode.toString() 
        });
        
        recordMetric('xiaoke_response_time', duration, { 
          method: req.method, 
          path: req.path 
        });
        
        if (res.statusCode >= 400) {
          recordMetric('xiaoke_errors_total', 1, { 
            method: req.method, 
            path: req.path, 
            status: res.statusCode.toString() 
          });
        }
      });
      
      next();
    });

    // 健康检查路由
    app.get('/health', (req: Request, res: Response) => {
      res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    // 读取配置文件示例(包括从Vault获取密钥)
    app.get('/api/v1/config-info', async (req: Request, res: Response) => {
      try {
        let dbConfig = {
          host: process.env.MONGODB_URI || 'mongodb://localhost:27017',
          type: 'MongoDB',
          secured: true
        };
        
        // 演示从Vault获取密钥(如果启用)
        if (process.env.USE_VAULT === 'true') {
          const mongoPassword = await getSecretFromVault('mongodb-password');
          const redisPassword = await getSecretFromVault('redis-password');
          dbConfig = {
            ...dbConfig,
            passwordSource: 'Vault',
            passwordLength: mongoPassword ? mongoPassword.length : 0,
            redisPasswordLength: redisPassword ? redisPassword.length : 0
          };
        }
        
        res.json({
          service: 'xiaoke-service',
          version: '1.0.0',
          environment: process.env.NODE_ENV,
          database: dbConfig
        });
      } catch (error) {
        logger.error('Error fetching config info', error);
        res.status(500).json({ error: 'Failed to fetch configuration information' });
      }
    });

    // 读取系统状态
    app.get('/api/v1/status', (req: Request, res: Response) => {
      const memoryUsage = process.memoryUsage();
      const formattedMemory = {
        rss: `${Math.round(memoryUsage.rss / 1024 / 1024)} MB`,
        heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)} MB`,
        heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)} MB`,
        external: `${Math.round(memoryUsage.external / 1024 / 1024)} MB`
      };

      res.json({
        uptime: process.uptime(),
        timestamp: Date.now(),
        memoryUsage: formattedMemory,
        environment: process.env.NODE_ENV
      });
    });

    // 设置API路由
    setupRoutes(app, io);

    // 错误处理中间件 (必须在所有路由之后)
    app.use(errorMiddleware);

    // 启动服务器
    await connectToDatabase();
    await setupRedisClient();
    await setupAgentSystem();
    httpServer.listen(PORT, () => {
      logger.info(`Server running on port ${PORT}`);
    });

    // 启动指标服务器
    const metricsApp = express();
    metricsApp.get('/metrics', async (req: Request, res: Response) => {
      try {
        const metrics = await metricsRegistry.metrics();
        res.set('Content-Type', metricsRegistry.contentType);
        res.end(metrics);
      } catch (error) {
        logger.error('Error generating metrics', error);
        res.status(500).end();
      }
    });

    metricsApp.listen(METRICS_PORT, () => {
      logger.info(`Metrics server running on port ${METRICS_PORT}`);
    });

  } catch (error) {
    logger.error('Failed to initialize application', error);
    process.exit(1);
  }
}

// 启动应用
initializeApp().catch(error => {
  console.error('Fatal error during initialization:', error);
  process.exit(1);
});

// 优雅关闭
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received, closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received, closing HTTP server');
  process.exit(0);
}); 