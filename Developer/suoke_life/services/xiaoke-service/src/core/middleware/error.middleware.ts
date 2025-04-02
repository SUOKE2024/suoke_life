import { Request, Response, NextFunction } from 'express';
import { logger } from '../../utils/logger';

/**
 * 自定义API错误类
 */
export class ApiError extends Error {
  statusCode: number;
  code: string;
  
  constructor(statusCode: number, message: string, code: string = 'UNKNOWN_ERROR') {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * 错误处理中间件
 * 处理所有API错误并返回统一的错误响应格式
 */
export const errorMiddleware = (
  err: Error | ApiError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // 默认错误状态和响应
  let statusCode = 500;
  let errorCode = 'INTERNAL_SERVER_ERROR';
  let errorMessage = '服务器内部错误';
  
  // 如果是API错误，使用其中的状态码和消息
  if (err instanceof ApiError) {
    statusCode = err.statusCode;
    errorCode = err.code;
    errorMessage = err.message;
  } else if (err.name === 'ValidationError') {
    // 处理验证错误
    statusCode = 400;
    errorCode = 'VALIDATION_ERROR';
    errorMessage = err.message;
  } else if (err.name === 'UnauthorizedError') {
    // 处理授权错误
    statusCode = 401;
    errorCode = 'UNAUTHORIZED';
    errorMessage = '未授权访问';
  } else if (err.name === 'ForbiddenError') {
    // 处理禁止访问错误
    statusCode = 403;
    errorCode = 'FORBIDDEN';
    errorMessage = '禁止访问';
  } else {
    // 其他未知错误
    errorMessage = err.message || errorMessage;
  }
  
  // 记录错误日志
  logger.error(`${errorCode}: ${errorMessage}`, {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    ip: req.ip,
    requestId: req.headers['x-request-id'] || ''
  });
  
  // 发送错误响应
  res.status(statusCode).json({
    success: false,
    error: {
      code: errorCode,
      message: errorMessage,
      requestId: req.headers['x-request-id'] || ''
    }
  });
};

/**
 * 404错误处理中间件
 */
export const notFoundMiddleware = (req: Request, res: Response) => {
  logger.warn(`404 - 资源未找到: ${req.originalUrl}`);
  
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: `路径 '${req.originalUrl}' 不存在`,
      requestId: req.headers['x-request-id'] || ''
    }
  });
}; 