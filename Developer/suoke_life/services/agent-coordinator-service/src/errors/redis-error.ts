/**
 * Redis操作错误类
 */
export class RedisError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RedisError';
  }
} 