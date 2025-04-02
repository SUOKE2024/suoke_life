import { Request, Response, NextFunction } from 'express';
import { Schema } from 'joi';
import { ApiError } from '../utils/errors';

/**
 * 请求数据验证中间件
 * @param schema Joi验证模式
 */
export const validateRequest = (schema: Schema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false, // 返回所有错误
      stripUnknown: true, // 移除未定义的属性
      allowUnknown: true, // 允许额外属性（不验证）
    });

    if (error) {
      const errorMessage = error.details
        .map((detail) => detail.message)
        .join(', ');
      
      return next(new ApiError(400, errorMessage));
    }

    // 替换请求体为已验证的值
    req.body = value;
    return next();
  };
}; 