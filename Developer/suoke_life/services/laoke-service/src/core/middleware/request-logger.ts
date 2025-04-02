import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';

/**
 * 请求日志中间件
 */
export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  // 获取请求开始时间
  const start = Date.now();
  
  // 处理请求完成
  res.on('finish', () => {
    // 计算处理时间
    const duration = Date.now() - start;
    
    // 获取请求信息
    const method = req.method;
    const url = req.originalUrl;
    const status = res.statusCode;
    const userAgent = req.get('User-Agent') || '';
    const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').toString();
    
    // 记录请求信息
    const level = status >= 500 ? 'error' : status >= 400 ? 'warn' : 'info';
    
    logger[level](`${method} ${url} ${status} - ${duration}ms - ${ip} - ${userAgent}`);
  });
  
  next();
}; 