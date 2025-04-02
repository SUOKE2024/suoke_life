import { CacheManager } from '../cache';
import logger from '../logger';

export interface RateLimitConfig {
  windowMs: number;     // 时间窗口（毫秒）
  maxRequests: number;  // 最大请求数
  blockDuration: number;// 超限后阻塞时间（毫秒）
}

export interface RateLimitInfo {
  remaining: number;    // 剩余请求数
  reset: number;        // 重置时间
  total: number;        // 总请求限制
}

export class RateLimiter {
  private static instance: RateLimiter;
  private cacheManager: CacheManager;
  private readonly RATE_LIMIT_PREFIX = 'ratelimit:';
  
  private readonly DEFAULT_CONFIG: RateLimitConfig = {
    windowMs: 60000,    // 1分钟
    maxRequests: 100,   // 每分钟100次请求
    blockDuration: 300000 // 5分钟
  };

  private constructor() {
    this.cacheManager = CacheManager.getInstance();
  }

  public static getInstance(): RateLimiter {
    if (!RateLimiter.instance) {
      RateLimiter.instance = new RateLimiter();
    }
    return RateLimiter.instance;
  }

  /**
   * 检查是否超出限制
   */
  public async checkLimit(key: string, config: Partial<RateLimitConfig> = {}): Promise<RateLimitInfo> {
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    const cacheKey = this.generateCacheKey(key);

    try {
      const current = await this.getCurrentState(cacheKey);
      
      if (!current) {
        // 首次访问
        const state = {
          count: 1,
          firstRequest: Date.now(),
          blocked: false
        };
        
        await this.saveState(cacheKey, state, finalConfig.windowMs);
        
        return {
          remaining: finalConfig.maxRequests - 1,
          reset: Date.now() + finalConfig.windowMs,
          total: finalConfig.maxRequests
        };
      }

      if (current.blocked) {
        throw new Error('请求被限制，请稍后重试');
      }

      const timePassed = Date.now() - current.firstRequest;
      
      if (timePassed > finalConfig.windowMs) {
        // 时间窗口已过，重置计数
        const state = {
          count: 1,
          firstRequest: Date.now(),
          blocked: false
        };
        
        await this.saveState(cacheKey, state, finalConfig.windowMs);
        
        return {
          remaining: finalConfig.maxRequests - 1,
          reset: Date.now() + finalConfig.windowMs,
          total: finalConfig.maxRequests
        };
      }

      if (current.count >= finalConfig.maxRequests) {
        // 超出限制，标记为阻塞
        const state = {
          ...current,
          blocked: true
        };
        
        await this.saveState(cacheKey, state, finalConfig.blockDuration);
        
        throw new Error('请求频率超出限制');
      }

      // 更新计数
      const state = {
        ...current,
        count: current.count + 1
      };
      
      await this.saveState(cacheKey, state, finalConfig.windowMs);

      return {
        remaining: finalConfig.maxRequests - state.count,
        reset: current.firstRequest + finalConfig.windowMs,
        total: finalConfig.maxRequests
      };
    } catch (error) {
      logger.error('限流检查失败:', error);
      throw error;
    }
  }

  /**
   * 重置限制
   */
  public async resetLimit(key: string): Promise<void> {
    const cacheKey = this.generateCacheKey(key);
    await this.cacheManager.delete(cacheKey, this.RATE_LIMIT_PREFIX);
  }

  private generateCacheKey(key: string): string {
    return `${key}`;
  }

  private async getCurrentState(key: string): Promise<{
    count: number;
    firstRequest: number;
    blocked: boolean;
  } | null> {
    return await this.cacheManager.get(key, this.RATE_LIMIT_PREFIX);
  }

  private async saveState(key: string, state: any, ttl: number): Promise<void> {
    await this.cacheManager.set(key, state, {
      ttl: Math.ceil(ttl / 1000),
      prefix: this.RATE_LIMIT_PREFIX
    });
  }
}