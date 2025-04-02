/**
 * 禁止访问错误
 * 用于表示用户没有权限执行请求的操作
 */
export class ForbiddenError extends Error {
  statusCode = 403;

  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, ForbiddenError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message }];
  }
}