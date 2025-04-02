import { Request } from 'express';

// 扩展Express请求接口，添加自定义属性
declare global {
  namespace Express {
    interface Request {
      id?: string;
      user?: {
        id: string;
        role: string;
        username: string;
      };
    }
  }
} 