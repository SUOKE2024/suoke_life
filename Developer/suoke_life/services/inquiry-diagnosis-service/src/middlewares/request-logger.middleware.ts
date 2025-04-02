import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

/**
 * 请求日志中间件
 * 记录所有请求的详细信息，并为每个请求分配唯一ID
 */
export const requestLoggerMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  // 为请求添加唯一ID
  const requestId = req.headers['x-request-id'] as string || uuidv4();
  
  // 扩展req对象，添加requestId
  Object.defineProperty(req, 'id', { 
    value: requestId,
    writable: false
  });
  
  // 设置响应头中的请求ID
  res.setHeader('X-Request-ID', requestId);
  
  // 处理请求开始时间
  const startTime = Date.now();
  
  // 记录请求信息
  logger.http(`收到请求: ${req.method} ${req.url}`, {
    requestId,
    method: req.method,
    url: req.url,
    path: req.path,
    params: req.params,
    query: req.query,
    headers: {
      ...req.headers,
      // 隐藏敏感信息
      authorization: req.headers.authorization ? '[REDACTED]' : undefined,
      cookie: req.headers.cookie ? '[REDACTED]' : undefined,
    },
    ip: req.ip,
    userAgent: req.headers['user-agent'],
  });
  
  // 监听响应完成事件
  res.on('finish', () => {
    const responseTime = Date.now() - startTime;
    const logMethod = res.statusCode >= 400 ? 'warn' : 'http';
    
    // 日志对象
    const logObject = {
      requestId,
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      responseTime: `${responseTime}ms`,
      userAgent: req.headers['user-agent'],
      ip: req.ip,
    };
    
    // 记录响应信息
    if (res.statusCode >= 400) {
      logger.warn(`请求结束: ${req.method} ${req.url} ${res.statusCode} (${responseTime}ms)`, logObject);
    } else {
      logger.http(`请求结束: ${req.method} ${req.url} ${res.statusCode} (${responseTime}ms)`, logObject);
    }
  });
  
  next();
};

export default { requestLoggerMiddleware };