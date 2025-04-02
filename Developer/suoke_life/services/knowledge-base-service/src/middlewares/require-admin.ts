/**
 * 管理员权限中间件
 * 确保用户具有管理员权限
 */
import { Request, Response, NextFunction } from 'express';
import { ForbiddenError } from '../errors/forbidden-error';

export const requireAdmin = (req: Request, res: Response, next: NextFunction) => {
  if (!req.currentUser || !req.currentUser.isAdmin) {
    throw new ForbiddenError('需要管理员权限');
  }
  
  next();
};