/**
 * 索儿服务启动文件
 */
const app = require('./app');
const http = require('http');
const config = require('./config');
const logger = require('./utils/logger');

// 获取端口
const port = process.env.PORT || config.port || 3000;

// 创建HTTP服务器
const server = http.createServer(app);

// 优雅关闭处理
const gracefulShutdown = async (signal) => {
  logger.info(`收到 ${signal} 信号，开始优雅关闭...`);
  
  // 30秒超时
  const shutdownTimeout = setTimeout(() => {
    logger.error('优雅关闭超时，强制退出');
    process.exit(1);
  }, 30000);
  
  try {
    // 停止接受新的请求
    server.close(() => {
      logger.info('HTTP服务器已关闭');
      
      // 关闭数据库连接池
      if (global.dbPool) {
        global.dbPool.end((err) => {
          if (err) {
            logger.error('关闭数据库连接池失败', { error: err.message });
          } else {
            logger.info('数据库连接池已关闭');
          }
          
          // 关闭Redis客户端
          if (global.redisClient) {
            global.redisClient.quit();
            logger.info('Redis客户端已关闭');
          }
          
          clearTimeout(shutdownTimeout);
          logger.info('优雅关闭完成');
          process.exit(0);
        });
      } else {
        clearTimeout(shutdownTimeout);
        logger.info('优雅关闭完成');
        process.exit(0);
      }
    });
  } catch (error) {
    logger.error('关闭服务时发生错误', { error: error.message });
    clearTimeout(shutdownTimeout);
    process.exit(1);
  }
};

// 启动服务器
server.listen(port, () => {
  logger.info(`索儿服务已启动，监听端口 ${port}`);
  logger.info(`环境: ${config.env}`);
  logger.info(`版本: ${config.version}`);
});

// 未处理的异常
process.on('uncaughtException', (error) => {
  logger.error('未捕获的异常', { error: error.message, stack: error.stack });
  // 对于未捕获的异常，我们应该认为进程状态不确定，所以需要退出
  gracefulShutdown('uncaughtException');
});

// 未处理的Promise拒绝
process.on('unhandledRejection', (reason, promise) => {
  logger.error('未处理的Promise拒绝', { 
    reason: reason instanceof Error ? reason.message : reason,
    stack: reason instanceof Error ? reason.stack : 'No stack trace'
  });
  // 对于未处理的Promise拒绝，我们可以选择不退出进程
});

// 注册关闭信号
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

module.exports = server;