/**
 * 认证中间件
 */
import { Request, Response, NextFunction } from 'express';
import { loadConfig } from '../utils/config-loader';
import logger from '../utils/logger';

/**
 * API密钥认证中间件
 */
export function authenticateApiKey(req: Request, res: Response, next: NextFunction) {
  // 如果未启用API认证，则直接通过
  const config = loadConfig();
  if (!config.security.enableApiAuthentication) {
    return next();
  }

  // 获取API密钥
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  // 检查API密钥
  if (!apiKey || apiKey !== process.env.API_KEY) {
    logger.warn('未授权的API访问尝试', {
      ip: req.ip,
      path: req.path,
    });
    
    return res.status(401).json({
      success: false,
      message: '未授权访问',
    });
  }
  
  // 认证通过
  next();
}

/**
 * 代理服务认证中间件
 */
export function authenticateAgent(req: Request, res: Response, next: NextFunction) {
  // 如果未启用代理认证，则直接通过
  const config = loadConfig();
  if (!config.security.enableAgentAuthentication) {
    return next();
  }

  // 获取代理密钥
  const agentKey = req.headers['x-agent-key'];
  const agentId = req.headers['x-agent-id'];
  
  // 检查代理密钥
  if (!agentKey || !agentId || agentKey !== process.env.AGENT_SECRET_KEY) {
    logger.warn('未授权的代理访问尝试', {
      agentId,
      path: req.path,
    });
    
    return res.status(401).json({
      success: false,
      message: '未授权代理访问',
    });
  }
  
  // 认证通过
  next();
}