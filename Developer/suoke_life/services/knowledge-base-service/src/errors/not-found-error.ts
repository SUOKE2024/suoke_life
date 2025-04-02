/**
 * 资源未找到错误
 * 用于表示请求的资源不存在
 */
export class NotFoundError extends Error {
  statusCode = 404;

  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message }];
  }
}