import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';
import { ApiError } from '../utils/errors';

/**
 * 全局错误处理中间件
 */
export const errorHandler = (
  err: Error | ApiError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // 记录错误
  logger.error(`[${req.method}] ${req.path} - 错误:`, err);
  
  // 判断是否为API错误
  if (err instanceof ApiError) {
    return res.status(err.statusCode).json({
      success: false,
      message: err.message,
      error: process.env.NODE_ENV === 'development' ? err.stack : undefined
    });
  }
  
  // 处理验证错误
  if (err.name === 'ValidationError') {
    return res.status(422).json({
      success: false,
      message: '数据验证失败',
      error: err.message,
    });
  }
  
  // 处理Mongoose错误
  if (err.name === 'CastError') {
    return res.status(400).json({
      success: false,
      message: '无效的ID格式',
      error: err.message,
    });
  }
  
  // 处理MongoDB重复键错误
  if (err.name === 'MongoError' && (err as any).code === 11000) {
    return res.status(409).json({
      success: false,
      message: '资源已存在',
      error: '存在重复的键值',
    });
  }
  
  // 处理JWT错误
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      success: false,
      message: '无效的令牌',
      error: err.message,
    });
  }
  
  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      success: false,
      message: '令牌已过期',
      error: err.message,
    });
  }
  
  // 默认处理为500错误
  return res.status(500).json({
    success: false,
    message: '服务器内部错误',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
};