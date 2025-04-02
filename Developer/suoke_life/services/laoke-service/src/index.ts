/**
 * 老克服务入口文件
 */

import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { logger } from './utils/logger';
import routes from './api/routes';
import laokeService from './laoke-service';

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3002;

// 中间件
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 请求日志中间件
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.originalUrl}`);
  next();
});

// 路由
app.use('/api/laoke', routes);

// 404处理
app.use((req, res) => {
  logger.warn(`404 Not Found: ${req.method} ${req.originalUrl}`);
  
  res.status(404).json({
    success: false,
    message: '接口不存在'
  });
});

// 错误处理
// eslint-disable-next-line @typescript-eslint/no-unused-vars
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('服务器错误', {
    error: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
    path: req.originalUrl,
    method: req.method
  });
  
  res.status(500).json({
    success: false,
    message: '服务器内部错误',
    error: process.env.NODE_ENV === 'production' ? undefined : (err instanceof Error ? err.message : String(err))
  });
});

// 启动服务
async function startServer() {
  try {
    // 初始化老克服务
    await laokeService.initialize();
    
    // 启动老克服务
    await laokeService.start();
    
    // 启动HTTP服务器
    app.listen(PORT, () => {
      logger.info(`老克服务启动成功，监听端口 ${PORT}`);
    });
    
    // 处理进程退出
    process.on('SIGINT', async () => {
      logger.info('收到SIGINT信号，准备关闭服务...');
      await shutdown();
    });
    
    process.on('SIGTERM', async () => {
      logger.info('收到SIGTERM信号，准备关闭服务...');
      await shutdown();
    });
    
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('未处理的Promise拒绝', {
        reason: reason instanceof Error ? reason.message : String(reason),
        stack: reason instanceof Error ? reason.stack : undefined,
        promise
      });
    });
    
    process.on('uncaughtException', (error) => {
      logger.error('未捕获的异常', {
        error: error.message,
        stack: error.stack
      });
      
      // 对于未捕获的异常，应该进行优雅关闭
      shutdown().catch((err) => {
        logger.error('关闭服务失败', {
          error: err instanceof Error ? err.message : String(err)
        });
        process.exit(1);
      });
    });
  } catch (error) {
    logger.error('启动服务失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    process.exit(1);
  }
}

// 关闭服务
async function shutdown() {
  logger.info('正在关闭老克服务...');
  
  try {
    // 关闭老克服务
    await laokeService.shutdown();
    
    logger.info('老克服务已关闭，退出进程');
    process.exit(0);
  } catch (error) {
    logger.error('关闭服务失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    process.exit(1);
  }
}

// 启动服务
startServer();