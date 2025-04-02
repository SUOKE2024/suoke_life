import winston from 'winston';
import 'winston-daily-rotate-file';

/**
 * 日志级别
 */
export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  DEBUG = 'debug'
}

/**
 * 创建日志格式
 */
const logFormat = winston.format.printf(({ level, message, timestamp, service }) => {
  return `${timestamp} [${service}] ${level}: ${message}`;
});

/**
 * 创建日志转换器
 */
const loggerTransports = [
  // 控制台输出
  new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      logFormat
    ),
  }),
  
  // 文件输出 - 按日期轮换
  new winston.transports.DailyRotateFile({
    filename: 'logs/looking-diagnosis-%DATE%.log',
    datePattern: 'YYYY-MM-DD',
    maxSize: '20m',
    maxFiles: '14d',
    format: winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      logFormat
    ),
  }),
];

/**
 * 日志服务类
 */
export class Logger {
  private logger: winston.Logger;
  
  /**
   * 构造函数
   * @param service 服务名称，用于标识日志来源
   */
  constructor(private service: string) {
    this.logger = winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service },
      transports: loggerTransports,
    });
  }
  
  /**
   * 记录错误级别日志
   * @param message 日志消息
   * @param meta 元数据
   */
  error(message: string, meta?: any): void {
    this.logger.error(message, meta);
  }
  
  /**
   * 记录警告级别日志
   * @param message 日志消息
   * @param meta 元数据
   */
  warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }
  
  /**
   * 记录信息级别日志
   * @param message 日志消息
   * @param meta 元数据
   */
  info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }
  
  /**
   * 记录调试级别日志
   * @param message 日志消息
   * @param meta 元数据
   */
  debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }
  
  /**
   * 为请求附加ID并记录日志
   * @param req 请求对象
   * @param message 日志消息
   * @param level 日志级别
   */
  logWithRequestId(req: any, message: string, level: LogLevel = LogLevel.INFO): void {
    const requestId = req.id || 'unknown';
    const logMessage = `[ReqID:${requestId}] ${message}`;
    
    switch (level) {
      case LogLevel.ERROR:
        this.error(logMessage);
        break;
      case LogLevel.WARN:
        this.warn(logMessage);
        break;
      case LogLevel.INFO:
        this.info(logMessage);
        break;
      case LogLevel.DEBUG:
        this.debug(logMessage);
        break;
      default:
        this.info(logMessage);
    }
  }
}