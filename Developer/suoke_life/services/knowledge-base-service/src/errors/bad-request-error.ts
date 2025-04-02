/**
 * 请求错误
 * 用于表示客户端发送了不正确的请求
 */
export class BadRequestError extends Error {
  statusCode = 400;

  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, BadRequestError.prototype);
  }

  serializeErrors() {
    return [{ message: this.message }];
  }
}