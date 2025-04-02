import { Request, Response, NextFunction } from 'express';
import { formatError } from '../utils/response-formatter';
import { logger } from '../utils/logger';
import { HttpException } from '../exceptions/http.exception';

/**
 * 全局错误处理中间件
 * 捕获并处理应用中的所有错误，返回格式化的错误响应
 */
export const errorMiddleware = (
  error: Error | HttpException,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  try {
    let statusCode = 500;
    let errorType = 'InternalServerError';
    let errorMessage = '服务器内部错误';
    let errorDetails: Record<string, any> | undefined = undefined;

    // 处理自定义HTTP异常
    if (error instanceof HttpException) {
      statusCode = error.statusCode;
      errorType = error.name;
      errorMessage = error.message;
      errorDetails = error.details;
    } 
    // 处理Joi验证错误
    else if (error.name === 'ValidationError') {
      statusCode = 400;
      errorType = 'ValidationError';
      errorMessage = '请求数据验证失败';
      errorDetails = {
        originalError: error.message,
        // 如果存在详细的错误字段，可以在这里解析
      };
    }
    // 处理未处理的其他错误
    else {
      errorMessage = error.message || '服务器内部错误';
    }

    // 记录错误日志
    logger.error(`[${errorType}] ${errorMessage}`, {
      statusCode,
      path: req.path,
      method: req.method,
      errorDetails,
      stack: error.stack
    });

    // 非生产环境下返回详细错误信息
    if (process.env.NODE_ENV !== 'production') {
      errorDetails = {
        ...errorDetails,
        stack: error.stack?.split('\n')
      };
    }

    // 发送格式化的错误响应
    res.status(statusCode).json(
      formatError(errorMessage, statusCode, errorType, errorDetails)
    );
  } catch (formatError) {
    // 处理格式化错误时的异常
    logger.error('格式化错误响应时发生异常', { error: formatError });
    
    // 发送基本错误响应
    res.status(500).json({
      success: false,
      message: '服务器错误',
      statusCode: 500,
      timestamp: new Date().toISOString()
    });
  }
};

export default { errorMiddleware };