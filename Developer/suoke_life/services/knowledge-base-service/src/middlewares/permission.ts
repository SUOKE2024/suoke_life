/**
 * 权限检查中间件
 */

import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';

/**
 * 检查用户是否具有指定权限
 * @param permission 所需权限
 */
export const checkPermission = (permission: string) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const requestId = req.headers['x-request-id'] as string;
      
      // 确保用户已认证
      if (!req.user) {
        return res.status(401).json({
          success: false,
          message: '需要身份认证',
        });
      }
      
      // 检查用户是否有管理员角色
      const isAdmin = req.user.roles.includes('admin');
      
      // 管理员拥有所有权限
      if (isAdmin) {
        return next();
      }
      
      // 检查用户是否具有特定权限
      if (req.user.permissions.includes(permission)) {
        return next();
      }
      
      // 记录权限被拒绝
      logger.warn('权限检查失败', {
        requestId,
        userId: req.user.id,
        requiredPermission: permission,
        userPermissions: req.user.permissions,
      });
      
      return res.status(403).json({
        success: false,
        message: '权限不足',
      });
    } catch (error) {
      logger.error('权限检查中间件错误', { error });
      next(error);
    }
  };
};