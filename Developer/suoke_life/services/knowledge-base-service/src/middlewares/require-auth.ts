/**
 * 身份验证中间件
 * 确保用户已登录
 */
import { Request, Response, NextFunction } from 'express';
import { ForbiddenError } from '../errors/forbidden-error';

export const requireAuth = (req: Request, res: Response, next: NextFunction) => {
  if (!req.currentUser) {
    throw new ForbiddenError('未授权');
  }
  
  next();
};