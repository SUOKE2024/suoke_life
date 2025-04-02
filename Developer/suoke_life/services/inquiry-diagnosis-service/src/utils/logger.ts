import winston from 'winston';
import path from 'path';
import config from '../config';

// 自定义日志级别
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
};

// 根据环境选择日志级别
const level = () => {
  return config.logs.level || 'info';
};

// 自定义日志颜色
const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'blue',
};

// 添加颜色
winston.addColors(colors);

// 日志格式
const format = winston.format.combine(
  // 添加时间戳
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  // 生产环境使用JSON格式，开发环境使用彩色格式
  config.server.isProd
    ? winston.format.json()
    : winston.format.combine(
        winston.format.colorize({ all: true }),
        winston.format.printf(
          (info) => `${info.timestamp} ${info.level}: ${info.message} ${info.metadata ? JSON.stringify(info.metadata) : ''}`
        )
      )
);

// 日志存储目标
const transports = [
  // 总是打印到控制台
  new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize({ all: true }),
      winston.format.printf(
        (info) => `${info.timestamp} ${info.level}: ${info.message} ${
          info.metadata && Object.keys(info.metadata).length ? JSON.stringify(info.metadata, null, 2) : ''
        }`
      )
    ),
  }),
];

// 如果是生产环境，添加文件日志
if (config.server.isProd) {
  const logDir = path.join(process.cwd(), 'logs');
  
  // 添加错误日志文件
  transports.push(
    new winston.transports.File({
      filename: path.join(logDir, 'error.log'),
      level: 'error',
    })
  );
  
  // 添加所有日志文件
  transports.push(
    new winston.transports.File({ 
      filename: path.join(logDir, 'combined.log') 
    })
  );
}

// 创建日志记录器
export const logger = winston.createLogger({
  level: level(),
  levels,
  format,
  transports,
  // 不退出程序
  exitOnError: false,
});

export default { logger };