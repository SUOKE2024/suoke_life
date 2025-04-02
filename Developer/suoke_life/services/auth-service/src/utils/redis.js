/**
 * Redis连接工具
 */
const { createClient } = require('redis');
const logger = require('./logger');
const config = require('../config');

// 创建Redis客户端
const redisClient = createClient({
  url: `redis://${config.redis.password ? `:${config.redis.password}@` : ''}${config.redis.host}:${config.redis.port}`,
  database: config.redis.db
});

// 连接事件处理
redisClient.on('connect', () => {
  logger.info('Redis客户端已连接');
});

redisClient.on('ready', () => {
  logger.info('Redis客户端已就绪');
});

redisClient.on('error', (err) => {
  logger.error('Redis连接错误', { error: err.message });
});

redisClient.on('reconnecting', () => {
  logger.warn('Redis客户端正在重连...');
});

redisClient.on('end', () => {
  logger.info('Redis客户端已断开连接');
});

// 连接Redis
(async () => {
  try {
    if (!redisClient.isOpen) {
      await redisClient.connect();
    }
  } catch (error) {
    logger.error('Redis连接失败', { error: error.message });
  }
})();

// 优雅关闭连接
process.on('SIGINT', async () => {
  try {
    if (redisClient.isOpen) {
      await redisClient.quit();
      logger.info('Redis连接已关闭');
    }
  } catch (error) {
    logger.error('Redis关闭连接失败', { error: error.message });
    process.exit(1);
  }
});

module.exports = redisClient; 