import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'four-diagnosis-coordinator' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
  ],
});

// 在非生产环境下，同时输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    ),
  }));
}

export class Logger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  info(message: string, meta?: Record<string, any>): void {
    logger.info(`[${this.context}] ${message}`, meta);
  }

  error(message: string, meta?: Record<string, any>): void {
    logger.error(`[${this.context}] ${message}`, meta);
  }

  warn(message: string, meta?: Record<string, any>): void {
    logger.warn(`[${this.context}] ${message}`, meta);
  }

  debug(message: string, meta?: Record<string, any>): void {
    logger.debug(`[${this.context}] ${message}`, meta);
  }
}

export default logger; 