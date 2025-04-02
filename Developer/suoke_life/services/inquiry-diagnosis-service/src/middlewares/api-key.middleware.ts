import { Request, Response, NextFunction } from 'express';
import config from '../config';
import { logger } from '../utils/logger';

/**
 * API密钥认证中间件
 * 验证请求中的X-API-KEY头是否与配置的API密钥匹配
 */
export const apiKeyMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const apiKey = req.headers['x-api-key'] as string;

  if (!apiKey || apiKey !== config.auth.apiKey) {
    logger.warn('API密钥验证失败', {
      ip: req.ip,
      path: req.path,
      method: req.method,
      userAgent: req.headers['user-agent']
    });
    
    res.status(401).json({
      success: false,
      message: 'API密钥无效',
      statusCode: 401,
      error: 'Unauthorized',
      timestamp: new Date().toISOString()
    });
    return;
  }

  next();
};

export default { apiKeyMiddleware };