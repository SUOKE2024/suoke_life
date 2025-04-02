import 'reflect-metadata';
import { App } from './app';
import config from './config';
import { logger } from './utils/logger';

/**
 * 应用启动函数
 */
const startServer = async (): Promise<void> => {
  try {
    // 创建应用实例
    const app = new App(config.server.port);
    
    // 启动监听
    app.listen();
    
    // 优雅关闭处理
    setupGracefulShutdown(app);
  } catch (error) {
    logger.error('应用启动失败', { error });
    process.exit(1);
  }
};

/**
 * 设置优雅关闭处理
 * @param app 应用实例
 */
const setupGracefulShutdown = (app: App): void => {
  // 捕获终止信号
  const signals = ['SIGINT', 'SIGTERM', 'SIGQUIT'];
  
  signals.forEach(signal => {
    process.on(signal, async () => {
      logger.info(`收到${signal}信号，正在优雅关闭服务...`);
      
      try {
        // 这里可以添加清理资源的代码
        // 例如关闭数据库连接、发送最后的指标等
        
        logger.info('服务已成功关闭');
        process.exit(0);
      } catch (error) {
        logger.error('关闭服务时发生错误', { error });
        process.exit(1);
      }
    });
  });
  
  // 捕获未处理的异常和拒绝
  process.on('uncaughtException', (error) => {
    logger.error('未捕获的异常', { error });
  });
  
  process.on('unhandledRejection', (reason) => {
    logger.error('未处理的Promise拒绝', { reason });
  });
};

// 启动服务
startServer();