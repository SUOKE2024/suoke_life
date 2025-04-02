import { Request, Response, NextFunction } from 'express';
import { Logger } from '../utils/logger';

const logger = new Logger('ErrorMiddleware');

/**
 * 自定义错误类
 */
export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;
  
  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * 处理404错误
 */
export const notFoundHandler = (req: Request, res: Response, next: NextFunction): void => {
  const error = new AppError(`找不到路径: ${req.originalUrl}`, 404);
  next(error);
};

/**
 * 全局错误处理中间件
 */
export const errorHandler = (err: any, req: Request, res: Response, next: NextFunction): void => {
  const statusCode = err.statusCode || 500;
  const message = err.message || '服务器内部错误';
  
  // 记录错误日志
  logger.error(`错误: ${message}`, {
    statusCode,
    stack: err.stack,
    path: req.path,
    method: req.method,
    requestId: req.id || 'unknown',
    body: JSON.stringify(req.body),
    query: JSON.stringify(req.query)
  });
  
  // 区分操作错误和程序错误
  const isOperational = err.isOperational !== undefined ? err.isOperational : false;
  
  // 开发环境返回完整错误，生产环境返回简化错误
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  const errorResponse = {
    success: false,
    status: statusCode,
    message,
    error: err.name || 'Error',
    ...(isDevelopment || isOperational ? { stack: err.stack } : {})
  };
  
  res.status(statusCode).json(errorResponse);
};

/**
 * 请求ID中间件
 * 为每个请求分配唯一ID
 */
export const requestIdMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  req.id = `req-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  next();
};

/**
 * 请求日志中间件
 * 记录所有请求的基本信息
 */
export const requestLoggerMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const start = Date.now();
  
  // 请求开始时记录
  logger.info(`开始请求: ${req.method} ${req.path}`, {
    requestId: req.id,
    method: req.method,
    path: req.path,
    query: req.query,
    ip: req.ip
  });
  
  // 响应完成时记录
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info(`完成请求: ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`, {
      requestId: req.id,
      statusCode: res.statusCode,
      duration
    });
  });
  
  next();
};