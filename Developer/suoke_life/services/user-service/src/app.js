/**
 * 索克生活用户服务
 * 应用入口文件
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const config = require('./config');
const { 
  errorMiddleware, 
  errorHandlerMiddleware, 
  i18nMiddleware,
  loggingMiddleware,
  responseTimeMiddleware,
  highLoadDetectionMiddleware,
  metricsCollectionMiddleware
} = require('./middlewares');
const { 
  metrics, 
  logger, 
  cacheService,
  db
} = require('./utils');
const routes = require('./routes');

// 初始化应用
const app = express();

// 基础中间件
app.use(helmet());
app.use(compression());
app.use(cors(config.cors));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// 日志中间件
app.use(loggingMiddleware);

// 国际化中间件
app.use(i18nMiddleware);

// 性能监控中间件
app.use(responseTimeMiddleware);
app.use(highLoadDetectionMiddleware);
app.use(metricsCollectionMiddleware);

// 指标收集中间件
app.use(metrics.requestCountMiddleware);
app.use(metrics.responseTimeMiddleware);

// API路由
app.use('/api', routes);

// 指标路由
app.get('/metrics', metrics.metricsMiddleware);

// 错误处理中间件
app.use(errorMiddleware);
app.use(errorHandlerMiddleware);

// 启动服务器
const startServer = async () => {
  try {
    // 初始化缓存服务
    await cacheService.init();
    
    // 启动HTTP服务器
    const server = app.listen(config.port, () => {
      logger.info(`用户服务已启动，监听端口 ${config.port}`);
      logger.info(`环境: ${config.env}`);
    });
    
    // 优雅关闭处理
    const gracefulShutdown = async (signal) => {
      logger.info(`收到 ${signal} 信号，开始优雅关闭...`);
      
      server.close(async () => {
        logger.info('HTTP服务器已关闭');
        
        try {
          // 关闭缓存连接
          await cacheService.close();
          logger.info('缓存连接已关闭');
          
          // 关闭数据库连接
          await db.close();
          logger.info('数据库连接已关闭');
          
          logger.info('所有连接已关闭，进程退出');
          process.exit(0);
        } catch (err) {
          logger.error('关闭连接时出错:', err);
          process.exit(1);
        }
      });
      
      // 如果10秒内没有完成关闭，强制退出
      setTimeout(() => {
        logger.error('无法在超时时间内完成优雅关闭，强制退出');
        process.exit(1);
      }, 10000);
    };
    
    // 注册信号处理程序
    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
    
    return server;
  } catch (err) {
    logger.error('启动服务器时出错:', err);
    process.exit(1);
  }
};

// 导出应用和启动函数
module.exports = { app, startServer }; 