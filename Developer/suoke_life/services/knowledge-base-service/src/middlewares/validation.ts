/**
 * 请求验证中间件
 */

import { Request, Response, NextFunction } from 'express';
import { ZodSchema } from 'zod';
import logger from '../utils/logger';

/**
 * 验证请求数据中间件
 * @param schema Zod验证模式
 */
export const validateRequest = (schema: ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      // 根据请求方法选择验证的数据
      const dataToValidate = req.method === 'GET' ? req.query : req.body;
      
      // 使用Zod验证数据
      const result = schema.safeParse(dataToValidate);
      
      if (!result.success) {
        const requestId = req.headers['x-request-id'] as string;
        
        logger.warn('请求验证失败', {
          requestId,
          errors: result.error.errors,
          path: req.path,
          method: req.method,
        });
        
        return res.status(400).json({
          success: false,
          message: '请求数据验证失败',
          errors: result.error.errors.map(error => ({
            path: error.path.join('.'),
            message: error.message,
          })),
        });
      }
      
      // 对于GET请求，更新请求的query对象
      if (req.method === 'GET') {
        req.query = result.data as any;
      } else {
        // 对于其他请求，更新请求的body对象
        req.body = result.data;
      }
      
      next();
    } catch (error) {
      logger.error('验证请求时发生错误', { error });
      next(error);
    }
  };
};