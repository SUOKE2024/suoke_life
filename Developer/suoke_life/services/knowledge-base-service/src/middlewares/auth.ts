/**
 * 身份认证中间件
 */

import { Request, Response, NextFunction } from 'express';
import axios from 'axios';
import logger from '../utils/logger';

// 声明Express Request接口扩展
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        roles: string[];
        permissions: string[];
      };
    }
  }
}

/**
 * 验证请求中的JWT令牌并设置用户信息
 */
export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    const requestId = req.headers['x-request-id'] as string;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: '未提供认证令牌',
      });
    }
    
    const token = authHeader.split(' ')[1];
    
    // 调用认证服务验证令牌并获取用户信息
    const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:3010';
    
    try {
      const response = await axios.post(
        `${authServiceUrl}/api/auth/verify-token`,
        { token },
        {
          headers: {
            'Content-Type': 'application/json',
            'x-request-id': requestId,
          },
        }
      );
      
      if (response.data.success) {
        // 设置用户信息到请求对象
        req.user = {
          id: response.data.user.id,
          roles: response.data.user.roles || [],
          permissions: response.data.user.permissions || [],
        };
        next();
      } else {
        return res.status(401).json({
          success: false,
          message: '无效的认证令牌',
        });
      }
    } catch (error: any) {
      logger.error('验证令牌失败', {
        requestId,
        error: error.message,
      });
      
      if (error.response && error.response.status === 401) {
        return res.status(401).json({
          success: false,
          message: '无效的认证令牌',
        });
      }
      
      throw error;
    }
  } catch (error) {
    logger.error('身份认证中间件错误', { error });
    next(error);
  }
};