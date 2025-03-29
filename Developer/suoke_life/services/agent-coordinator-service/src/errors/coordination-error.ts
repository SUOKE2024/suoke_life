/**
 * 协调服务错误类
 */
export class CoordinationError extends Error {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'CoordinationError';
  }
} 