import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { HttpException } from '../exceptions/http.exception';
import { logger } from '../utils/logger';
import jwt from 'jsonwebtoken';

/**
 * 认证中间件
 * 验证请求中的JWT令牌
 */
export const authMiddleware = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new HttpException(401, '未提供认证令牌');
    }
    
    const token = authHeader.split(' ')[1];
    
    if (!token) {
      throw new HttpException(401, '无效的认证令牌格式');
    }
    
    try {
      const secret = process.env.JWT_SECRET || 'default_jwt_secret';
      const decoded = jwt.verify(token, secret) as { userId: string };
      
      req.user = {
        id: decoded.userId
      };
      
      next();
    } catch (error) {
      logger.error('认证令牌验证失败', { error });
      throw new HttpException(401, '认证令牌无效或已过期');
    }
  } catch (error) {
    next(error);
  }
};