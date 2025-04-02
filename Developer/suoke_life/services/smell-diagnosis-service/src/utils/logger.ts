import winston from 'winston';
import path from 'path';

const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
};

const logColors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white',
};

winston.addColors(logColors);

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.printf(
    (info) => `${info.timestamp} ${info.level}: [${info.label}] ${info.message}`
  )
);

const logLevel = process.env.NODE_ENV === 'development' ? 'debug' : 'info';

/**
 * 日志工具类
 */
export class Logger {
  private logger: winston.Logger;

  constructor(serviceName: string) {
    const logDir = path.join(process.cwd(), 'logs');

    this.logger = winston.createLogger({
      level: process.env.LOG_LEVEL || logLevel,
      levels: logLevels,
      format: winston.format.combine(
        winston.format.label({ label: serviceName }),
        logFormat
      ),
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize({ all: true }),
            winston.format.label({ label: serviceName }),
            logFormat
          ),
        }),
        new winston.transports.File({
          filename: path.join(logDir, 'error.log'),
          level: 'error',
        }),
        new winston.transports.File({
          filename: path.join(logDir, 'combined.log'),
        }),
      ],
    });
  }

  info(message: string, meta?: Record<string, any>): void {
    this.logger.info(message, meta);
  }

  error(message: string, meta?: Record<string, any>): void {
    this.logger.error(message, meta);
  }

  warn(message: string, meta?: Record<string, any>): void {
    this.logger.warn(message, meta);
  }

  debug(message: string, meta?: Record<string, any>): void {
    this.logger.debug(message, meta);
  }

  http(message: string, meta?: Record<string, any>): void {
    this.logger.http(message, meta);
  }
} 