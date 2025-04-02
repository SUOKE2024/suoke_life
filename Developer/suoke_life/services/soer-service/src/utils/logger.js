/**
 * 日志工具模块
 * 提供统一的日志记录功能
 */
const winston = require('winston');
const { format, transports } = winston;

// 日志输出格式
const logFormat = format.combine(
  format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  format.errors({ stack: true }),
  format.splat(),
  format.json()
);

// 创建Winston日志记录器
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: { service: 'soer-service' },
  transports: [
    // 输出所有级别的日志到控制台
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.printf(({ level, message, timestamp, ...meta }) => {
          return `${timestamp} ${level}: ${message} ${Object.keys(meta).length > 0 ? JSON.stringify(meta) : ''}`;
        })
      )
    }),
    // 输出错误级别日志到文件
    new transports.File({ 
      filename: 'logs/error.log', 
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // 输出所有级别日志到文件
    new transports.File({ 
      filename: 'logs/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// 开发环境下增加更多控制台日志输出
if (process.env.NODE_ENV !== 'production') {
  logger.add(new transports.Console({
    format: format.combine(
      format.colorize(),
      format.simple()
    )
  }));
}

// 简单封装日志方法，方便调用
module.exports = {
  /**
   * 记录信息级别日志
   * @param {string} message - 日志消息
   * @param {Object} meta - 附加元数据
   */
  info: (message, meta = {}) => {
    logger.info(message, meta);
  },
  
  /**
   * 记录警告级别日志
   * @param {string} message - 日志消息
   * @param {Object} meta - 附加元数据
   */
  warn: (message, meta = {}) => {
    logger.warn(message, meta);
  },
  
  /**
   * 记录错误级别日志
   * @param {string} message - 日志消息
   * @param {Object} meta - 附加元数据
   */
  error: (message, meta = {}) => {
    logger.error(message, meta);
  },
  
  /**
   * 记录调试级别日志
   * @param {string} message - 日志消息
   * @param {Object} meta - 附加元数据
   */
  debug: (message, meta = {}) => {
    logger.debug(message, meta);
  },
  
  /**
   * 获取原始winston日志记录器实例
   * @returns {Object} Winston日志记录器
   */
  getLogger: () => logger
};