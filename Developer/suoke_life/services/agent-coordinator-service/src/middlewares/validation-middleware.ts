/**
 * 请求验证中间件
 */
import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';

/**
 * 创建会话请求验证
 */
export function validateCreateSession(req: Request, res: Response, next: NextFunction) {
  const { userId, preferredAgentId } = req.body;
  
  if (!userId) {
    return res.status(400).json({
      success: false,
      message: '用户ID不能为空',
    });
  }
  
  next();
}

/**
 * 更新会话请求验证
 */
export function validateUpdateSession(req: Request, res: Response, next: NextFunction) {
  const { sessionId } = req.params;
  const { status } = req.body;
  
  if (!sessionId) {
    return res.status(400).json({
      success: false,
      message: '会话ID不能为空',
    });
  }
  
  if (status && !['active', 'paused', 'completed'].includes(status)) {
    return res.status(400).json({
      success: false,
      message: '无效的会话状态',
    });
  }
  
  next();
}

/**
 * 代理请求验证
 */
export function validateAgentRequest(req: Request, res: Response, next: NextFunction) {
  const { agentId } = req.params;
  const { sessionId, query } = req.body;
  
  if (!agentId) {
    return res.status(400).json({
      success: false,
      message: '代理ID不能为空',
    });
  }
  
  if (!sessionId) {
    return res.status(400).json({
      success: false,
      message: '会话ID不能为空',
    });
  }
  
  if (!query) {
    return res.status(400).json({
      success: false,
      message: '查询内容不能为空',
    });
  }
  
  next();
}

/**
 * 协调请求验证
 */
export function validateCoordinationRequest(req: Request, res: Response, next: NextFunction) {
  const { sessionId, query } = req.body;
  
  if (!sessionId) {
    return res.status(400).json({
      success: false,
      message: '会话ID不能为空',
    });
  }
  
  if (!query) {
    return res.status(400).json({
      success: false,
      message: '查询内容不能为空',
    });
  }
  
  next();
}