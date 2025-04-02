/**
 * 认证中间件
 */
import { Request, Response, NextFunction } from 'express';
import { loadConfig } from '../utils/config-loader';
import logger from '../utils/logger';
import { ErrorCode, AppError } from '../utils/error-handler';

/**
 * API认证中间件
 */
export function authenticate(req: Request, res: Response, next: NextFunction): void {
  try {
    const config = loadConfig();
    
    // 如果禁用了API认证，直接通过
    if (!config.security.enableApiAuthentication) {
      return next();
    }
    
    // 获取API密钥
    const apiKey = req.headers['x-api-key'] as string;
    
    // 验证API密钥
    if (!apiKey || apiKey !== process.env.API_KEY) {
      logger.warn('未授权的API访问尝试', {
        ip: req.ip,
        path: req.path,
        method: req.method,
      });
      
      throw new AppError(
        '未授权的请求，缺少有效的API密钥',
        ErrorCode.UNAUTHORIZED,
        401
      );
    }
    
    next();
  } catch (error) {
    next(error);
  }
}

/**
 * 代理认证中间件 - 验证代理请求来源
 */
export function authenticateAgent(req: Request, res: Response, next: NextFunction): void {
  try {
    const config = loadConfig();
    
    // 如果禁用了代理认证，直接通过
    if (!config.security.enableAgentAuthentication) {
      return next();
    }
    
    // 获取代理密钥
    const agentKey = req.headers['x-agent-key'] as string;
    const agentId = req.headers['x-agent-id'] as string;
    
    // 代理ID必须提供
    if (!agentId) {
      throw new AppError(
        '未授权的请求，缺少代理ID',
        ErrorCode.UNAUTHORIZED,
        401
      );
    }
    
    // 验证代理密钥 (实际实现中应该从安全存储中获取正确的密钥)
    const validKey = process.env[`${agentId.toUpperCase()}_KEY`];
    
    if (!agentKey || agentKey !== validKey) {
      logger.warn('未授权的代理访问尝试', {
        ip: req.ip,
        path: req.path,
        method: req.method,
        agentId,
      });
      
      throw new AppError(
        '未授权的请求，代理密钥无效',
        ErrorCode.UNAUTHORIZED,
        401
      );
    }
    
    next();
  } catch (error) {
    next(error);
  }
} 