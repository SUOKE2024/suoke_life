import { Request, Response, NextFunction } from 'express';
import { ServiceUnavailableError } from '../utils/error-handler';
import { Logger } from '../utils/logger';

/**
 * 简单内存型速率限制器
 * 注意：这只适用于单节点环境，分布式环境应使用Redis等外部存储
 */
class MemoryRateLimiter {
  private requestCounts: Map<string, { count: number, resetTime: number }>;
  private logger: Logger;
  
  constructor() {
    this.requestCounts = new Map();
    this.logger = new Logger('MemoryRateLimiter');
    
    // 每分钟清理过期的计数器
    setInterval(() => this.cleanup(), 60000);
  }
  
  /**
   * 检查请求是否超出限制
   * @param key 限制键（如IP地址或用户ID）
   * @param limit 时间窗口内的最大请求数
   * @param windowMs 时间窗口（毫秒）
   * @returns 是否允许请求
   */
  isAllowed(key: string, limit: number, windowMs: number): boolean {
    const now = Date.now();
    const record = this.requestCounts.get(key);
    
    // 如果没有记录或记录已过期，创建新记录
    if (!record || now > record.resetTime) {
      this.requestCounts.set(key, {
        count: 1,
        resetTime: now + windowMs
      });
      return true;
    }
    
    // 检查是否超出限制
    if (record.count >= limit) {
      return false;
    }
    
    // 增加计数
    record.count++;
    return true;
  }
  
  /**
   * 获取剩余配额和重置时间
   * @param key 限制键
   * @param limit 最大请求数
   * @returns 剩余配额和重置时间
   */
  getRateLimitInfo(key: string, limit: number): { remaining: number, resetTime: number } {
    const record = this.requestCounts.get(key);
    
    if (!record) {
      return {
        remaining: limit,
        resetTime: Date.now() + 60000 // 默认重置时间1分钟
      };
    }
    
    return {
      remaining: Math.max(0, limit - record.count),
      resetTime: record.resetTime
    };
  }
  
  /**
   * 清理过期的计数器
   */
  private cleanup(): void {
    const now = Date.now();
    let expiredCount = 0;
    
    for (const [key, record] of this.requestCounts.entries()) {
      if (now > record.resetTime) {
        this.requestCounts.delete(key);
        expiredCount++;
      }
    }
    
    if (expiredCount > 0) {
      this.logger.debug(`已清理 ${expiredCount} 个过期的速率限制记录`);
    }
  }
}

/**
 * 速率限制选项
 */
interface RateLimitOptions {
  /**
   * 时间窗口内的最大请求数
   */
  limit: number;
  
  /**
   * 时间窗口（毫秒）
   */
  windowMs: number;
  
  /**
   * 用于生成限制键的函数
   */
  keyGenerator?: (req: Request) => string;
  
  /**
   * 跳过限制的请求判断函数
   */
  skip?: (req: Request) => boolean;
  
  /**
   * 处理超出限制的函数
   */
  handler?: (req: Request, res: Response, next: NextFunction) => void;
}

// 创建全局速率限制器实例
const limiter = new MemoryRateLimiter();

/**
 * 速率限制中间件
 * 限制单个IP或用户的请求频率
 * 
 * @param options 速率限制选项
 * @returns Express中间件函数
 */
export function rateLimitMiddleware(options: RateLimitOptions) {
  const logger = new Logger('RateLimitMiddleware');
  
  // 设置默认选项
  const limit = options.limit || 60; // 默认每分钟60个请求
  const windowMs = options.windowMs || 60000; // 默认1分钟窗口
  
  // 默认使用IP作为限制键
  const keyGenerator = options.keyGenerator || ((req: Request) => {
    return req.ip || req.headers['x-forwarded-for'] as string || 'unknown';
  });
  
  // 默认不跳过任何请求
  const skip = options.skip || (() => false);
  
  // 默认处理超出限制的请求
  const handler = options.handler || ((req: Request, res: Response, next: NextFunction) => {
    logger.warn('请求超出速率限制', { ip: req.ip, path: req.path });
    next(new ServiceUnavailableError('请求频率过高，请稍后再试'));
  });
  
  return (req: Request, res: Response, next: NextFunction) => {
    // 如果请求应该跳过限制，直接继续
    if (skip(req)) {
      return next();
    }
    
    // 生成限制键
    const key = keyGenerator(req);
    
    // 检查是否允许请求
    if (limiter.isAllowed(key, limit, windowMs)) {
      // 获取速率限制信息
      const rateLimitInfo = limiter.getRateLimitInfo(key, limit);
      
      // 添加速率限制头部
      res.setHeader('X-RateLimit-Limit', limit.toString());
      res.setHeader('X-RateLimit-Remaining', rateLimitInfo.remaining.toString());
      res.setHeader('X-RateLimit-Reset', Math.ceil(rateLimitInfo.resetTime / 1000).toString());
      
      // 允许请求继续
      return next();
    }
    
    // 请求超出限制，调用处理函数
    handler(req, res, next);
  };
}