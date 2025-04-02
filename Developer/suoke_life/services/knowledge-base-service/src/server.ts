/**
 * 知识库服务入口文件
 */

import app from './app';
import logger from './utils/logger';

// 获取端口配置
const PORT = process.env.PORT || 3002;

// 启动服务器
const server = app.listen(PORT, () => {
  logger.info(`知识库服务启动成功，端口: ${PORT}`);
  logger.info(`API文档地址: http://localhost:${PORT}/api-docs`);
});

// 处理未捕获的异常和拒绝的Promise
process.on('uncaughtException', (error) => {
  logger.error(`未捕获的异常: ${error.message}`, { error });
  // 出现未捕获的异常时，应该优雅地关闭服务器
  server.close(() => {
    logger.info('服务器已关闭');
    process.exit(1);
  });
  // 如果10秒内服务器没有关闭，则强制退出
  setTimeout(() => {
    logger.error('强制关闭服务器');
    process.exit(1);
  }, 10000);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error(`未处理的Promise拒绝`, { reason, promise });
});

// 优雅关闭
process.on('SIGTERM', () => {
  logger.info('收到SIGTERM信号，准备关闭服务器');
  server.close(() => {
    logger.info('服务器已关闭');
    process.exit(0);
  });
  // 如果10秒内服务器没有关闭，则强制退出
  setTimeout(() => {
    logger.error('强制关闭服务器');
    process.exit(1);
  }, 10000);
});

export default server;