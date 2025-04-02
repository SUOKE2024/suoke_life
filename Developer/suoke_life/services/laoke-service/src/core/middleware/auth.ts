import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { ApiError } from '../utils/errors';
import logger from '../utils/logger';

// 扩展Request类型以包含用户信息
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        role: string;
        permissions: string[];
      };
    }
  }
}

/**
 * 身份验证中间件
 */
export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new ApiError(401, '未提供有效的身份验证令牌');
    }

    const token = authHeader.split(' ')[1];

    if (!token) {
      throw new ApiError(401, '未提供有效的身份验证令牌');
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'default_secret') as any;
      
      req.user = {
        id: decoded.id,
        role: decoded.role,
        permissions: decoded.permissions || []
      };
      
      next();
    } catch (error) {
      logger.error('JWT验证失败:', error);
      throw new ApiError(401, '身份验证令牌无效或已过期');
    }
  } catch (error) {
    next(error);
  }
};

/**
 * 角色授权中间件
 * @param roles 允许的角色列表
 */
export const authorize = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return next(new ApiError(401, '未授权访问'));
    }

    if (!roles.includes(req.user.role)) {
      return next(new ApiError(403, '没有足够的权限执行此操作'));
    }

    next();
  };
};

/**
 * 权限授权中间件
 * @param requiredPermissions 所需权限列表
 */
export const hasPermission = (requiredPermissions: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return next(new ApiError(401, '未授权访问'));
    }

    const hasAllPermissions = requiredPermissions.every(permission =>
      req.user!.permissions.includes(permission)
    );

    if (!hasAllPermissions) {
      return next(new ApiError(403, '没有足够的权限执行此操作'));
    }

    next();
  };
}; 