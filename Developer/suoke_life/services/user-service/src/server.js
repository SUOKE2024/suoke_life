/**
 * 索克生活用户服务
 * 服务器启动文件
 */
// 初始化OpenTelemetry，必须在其他模块之前导入
const { initTelemetry } = require('./utils/telemetry');
// 仅在非测试环境下初始化遥测
if (process.env.NODE_ENV !== 'test') {
  initTelemetry();
}

const { app, startServer } = require('./app');
const config = require('./config');
const { logger } = require('./utils');

// 设置正确的端口
config.port = process.env.PORT || 3004;

// 启动服务器
startServer().then(server => {
  logger.info(`用户服务已启动，监听端口 ${config.port}`);
  
  // 注册进程终止处理函数
  process.on('uncaughtException', (error) => {
    logger.error('未捕获的异常', error);
  });
  
  process.on('unhandledRejection', (reason, promise) => {
    logger.error('未处理的Promise拒绝', { reason, promise });
  });
}).catch(error => {
  logger.error('启动服务器时出错', error);
  process.exit(1);
}); 