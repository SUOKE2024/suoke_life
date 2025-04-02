/**
 * 日志工具封装
 */
const winston = require('winston');
const config = require('../config');

// 定义日志等级
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
  trace: 5
};

// 创建日志格式
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// 创建日志转换器
const consoleFormat = winston.format.printf(({ level, message, timestamp, ...meta }) => {
  const metaString = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
  return `${timestamp} [${level.toUpperCase()}]: ${message} ${metaString}`;
});

// 创建日志转换器 - 控制台彩色
const consoleColorFormat = winston.format.combine(
  winston.format.colorize({ all: true }),
  consoleFormat
);

// 获取日志等级
const getLogLevel = () => {
  const env = config.env || 'development';
  return env === 'production' ? 'info' : 'debug';
};

// 创建日志记录器
const logger = winston.createLogger({
  levels: logLevels,
  level: getLogLevel(),
  format: logFormat,
  defaultMeta: { service: 'auth-service' },
  transports: [
    // 控制台输出
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
        consoleColorFormat
      )
    }),
    // 文件输出 - 错误日志
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // 文件输出 - 所有日志
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ],
  exitOnError: false
});

// 开发环境特殊处理
if (config.env !== 'production') {
  logger.level = 'debug';
}

// 测试环境特殊处理
if (config.env === 'test') {
  logger.level = 'error';
  
  // 移除所有传输器并只使用控制台传输器
  logger.clear();
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
      consoleColorFormat
    ),
    silent: true // 测试环境默认不输出日志
  }));
}

// 添加便捷的跟踪级别
logger.trace = (...args) => logger.log('trace', ...args);

module.exports = logger; 