import express from 'express';
import http from 'http';
import cors from 'cors';
import dotenv from 'dotenv';
import { Server } from 'socket.io';
import winston from 'winston';
import routes from './routes';
import { initDatabaseConnection, closeDatabaseConnection } from './config/database';
import { errorHandler } from './middlewares/errorHandler';
import { setupSocketHandlers } from './core/socketHandlers';
import { accessibilityMiddleware } from './middlewares/accessibilityMiddleware';
import { metricsMiddleware } from './middlewares/metricsMiddleware';
import { initTracing } from './middlewares/tracingMiddleware';
import { initializeServices, shutdownServices } from './di/providers';

// 初始化追踪
const tracingSdk = initTracing();

// 加载环境变量
dotenv.config();

// 创建日志记录器
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
  ],
});

// 创建Express应用
const app = express();
const server = http.createServer(app);

// 创建Socket.io服务
const io = new Server(server, {
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    methods: ['GET', 'POST'],
  },
});

// 应用中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(accessibilityMiddleware);

// 初始化指标中间件
if (process.env.ENABLE_METRICS === 'true') {
  metricsMiddleware(app);
  logger.info('指标监控已启用，端点: /metrics');
}

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    service: 'xiaoai-service',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// 注册路由
app.use('/api', routes);

// 错误处理中间件
app.use(errorHandler);

// 设置Socket.io事件处理
setupSocketHandlers(io);

// 初始化应用程序
const initializeApp = async () => {
  try {
    // 连接数据库
    await initDatabaseConnection();
    
    // 初始化服务
    await initializeServices();
    
    // 启动服务器
    const PORT = process.env.PORT || 3040;
    server.listen(PORT, () => {
      logger.info(`小艾智能体服务已启动，监听端口: ${PORT}`);
      logger.info('服务信息:');
      logger.info('- 版本: 1.0.0');
      logger.info('- 环境: ' + (process.env.NODE_ENV || 'development'));
      logger.info('- 功能: 四诊协调、无障碍服务、语音引导');
      logger.info('- 指标监控: ' + (process.env.ENABLE_METRICS === 'true' ? '已启用' : '未启用'));
      logger.info('- 链路追踪: ' + (process.env.ENABLE_TRACING === 'true' ? '已启用' : '未启用'));
      logger.info('- 数据库: 已连接');
      logger.info('- 缓存服务: 已连接');
    });
  } catch (error) {
    logger.error('应用程序初始化失败:', error);
    process.exit(1);
  }
};

// 启动应用程序
initializeApp();

// 优雅关闭应用程序
const gracefulShutdown = async () => {
  logger.info('正在优雅关闭应用程序...');
  
  try {
    // 关闭链路追踪
    if (tracingSdk) {
      tracingSdk.shutdown();
    }
    
    // 关闭服务器
    server.close();
    logger.info('服务器已关闭');
    
    // 关闭服务
    await shutdownServices();
    logger.info('服务已关闭');
    
    // 关闭数据库连接
    await closeDatabaseConnection();
    logger.info('数据库连接已关闭');
    
  } catch (error) {
    logger.error('关闭应用程序时出错:', error);
  } finally {
    process.exit(0);
  }
};

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
  logger.error('未捕获的异常:', error);
});

// 处理未处理的Promise拒绝
process.on('unhandledRejection', (reason, promise) => {
  logger.error('未处理的Promise拒绝:', reason);
});

// 处理进程终止信号
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

export { app, server, io, logger };