/**
 * 请求验证中间件
 * 验证请求的参数和请求体
 */
import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { BadRequestError } from '../errors/bad-request-error';

export const validateRequest = (req: Request, res: Response, next: NextFunction) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    const messages = errors.array().map(error => {
      return { message: error.msg, field: error.param };
    });
    
    throw new BadRequestError(messages[0].message);
  }
  
  next();
};