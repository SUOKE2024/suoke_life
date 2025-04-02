import { Request, Response, NextFunction } from 'express';
import { AnyZodObject, ZodError } from 'zod';
import { HttpException } from '../exceptions/http.exception';

/**
 * 请求验证中间件
 * 使用Zod验证请求的body, query或params
 */
export const validationMiddleware = (schema: AnyZodObject, source: 'body' | 'query' | 'params' = 'body') => {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const data = await schema.parseAsync(req[source]);
      req[source] = data;
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const formattedErrors = error.errors.map(err => ({
          path: err.path.join('.'),
          message: err.message
        }));
        
        next(new HttpException(400, '请求验证失败', { errors: formattedErrors }));
      } else {
        next(error);
      }
    }
  };
};