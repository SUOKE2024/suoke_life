import { Request, Response, NextFunction } from 'express';
import { requestLogger } from '../../utils/logger';

/**
 * 请求日志中间件
 * 记录所有进入的HTTP请求信息
 */
export const requestLoggerMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  
  // 为保护隐私，过滤敏感信息
  const filteredHeaders = { ...req.headers };
  if (filteredHeaders.authorization) {
    filteredHeaders.authorization = 'Bearer [FILTERED]';
  }
  
  // 请求开始日志
  requestLogger.info('收到请求', {
    method: req.method,
    url: req.url,
    ip: req.ip,
    query: req.query,
    headers: filteredHeaders,
    requestId: req.headers['x-request-id'] || '',
    userAgent: req.headers['user-agent'] || ''
  });
  
  // 响应结束后的处理
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    
    // 请求完成日志
    requestLogger.info('请求完成', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      requestId: req.headers['x-request-id'] || '',
      contentLength: res.getHeader('content-length') || 0
    });
  });
  
  next();
}; 