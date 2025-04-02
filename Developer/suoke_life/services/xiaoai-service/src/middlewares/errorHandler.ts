import { Request, Response, NextFunction } from 'express';
import { logger } from '../index';

/**
 * 应用错误类
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
 * 全局错误处理中间件
 */
export const errorHandler = (
  err: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // 默认状态码和错误消息
  let statusCode = 500;
  let message = '服务器内部错误';
  let isOperational = false;
  
  // 如果是应用错误，使用其状态码和消息
  if (err instanceof AppError) {
    statusCode = err.statusCode;
    message = err.message;
    isOperational = err.isOperational;
  }
  
  // 记录错误
  logger.error(
    `[${req.method}] ${req.path} - 状态码: ${statusCode}, 消息: ${message}`,
    {
      error: err.stack,
      body: req.body,
      params: req.params,
      query: req.query,
    }
  );
  
  // 发送错误响应
  res.status(statusCode).json({
    success: false,
    error: {
      message,
      // 仅在开发环境中返回堆栈信息
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
    },
  });
};