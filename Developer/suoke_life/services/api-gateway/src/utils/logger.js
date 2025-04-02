/**
 * 日志工具模块
 */
const winston = require('winston');
const path = require('path');
const fs = require('fs');

// 确保日志目录存在
const logDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// 定义日志格式
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// 控制台输出格式
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ level, message, timestamp, ...meta }) => {
    return `${timestamp} ${level}: ${message} ${Object.keys(meta).length ? JSON.stringify(meta, null, 2) : ''}`;
  })
);

// 创建logger实例
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: { service: 'api-gateway' },
  transports: [
    // 控制台输出
    new winston.transports.Console({
      format: consoleFormat
    }),
    // 信息日志文件
    new winston.transports.File({
      filename: path.join(logDir, 'info.log'),
      level: 'info'
    }),
    // 错误日志文件
    new winston.transports.File({
      filename: path.join(logDir, 'error.log'),
      level: 'error'
    }),
    // 所有日志文件
    new winston.transports.File({
      filename: path.join(logDir, 'combined.log')
    })
  ]
});

// 非生产环境下记录详细日志
if (process.env.NODE_ENV !== 'production') {
  logger.level = 'debug';
}

// 测试环境下禁用文件日志
if (process.env.NODE_ENV === 'test') {
  logger.transports.forEach((t) => {
    if (t instanceof winston.transports.File) {
      t.silent = true;
    }
  });
}

module.exports = logger;