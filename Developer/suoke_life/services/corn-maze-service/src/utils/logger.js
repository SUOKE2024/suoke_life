/**
 * 日志工具
 */
const { createLogger, format, transports } = require('winston');
const path = require('path');
const fs = require('fs');

// 确保日志目录存在
const logDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// 日志文件路径
const logFilePath = process.env.LOG_FILE_PATH || path.join(logDir, 'corn-maze-service.log');

// 日志级别
const logLevel = process.env.LOG_LEVEL || 'info';

// 创建日志格式
const logFormat = format.combine(
  format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  format.errors({ stack: true }),
  format.splat(),
  format.json()
);

// 创建日志记录器
const logger = createLogger({
  level: logLevel,
  format: logFormat,
  defaultMeta: { service: 'corn-maze-service' },
  transports: [
    // 控制台输出
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.printf(
          (info) => `${info.timestamp} ${info.level}: ${info.message}`
        )
      )
    }),
    // 文件输出
    new transports.File({ 
      filename: logFilePath,
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    })
  ],
  exitOnError: false
});

module.exports = logger;
