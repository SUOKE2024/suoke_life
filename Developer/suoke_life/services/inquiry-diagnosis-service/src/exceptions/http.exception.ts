/**
 * HTTP异常基类
 */
export class HttpException extends Error {
  /**
   * HTTP状态码
   */
  public statusCode: number;
  
  /**
   * 错误详情
   */
  public details?: Record<string, any>;

  /**
   * 创建HTTP异常
   * @param message 错误消息
   * @param statusCode HTTP状态码
   * @param details 错误详情
   */
  constructor(message: string, statusCode: number = 500, details?: Record<string, any>) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * 400 Bad Request
 */
export class BadRequestException extends HttpException {
  constructor(message: string = '请求参数错误', details?: Record<string, any>) {
    super(message, 400, details);
  }
}

/**
 * 401 Unauthorized
 */
export class UnauthorizedException extends HttpException {
  constructor(message: string = '未授权', details?: Record<string, any>) {
    super(message, 401, details);
  }
}

/**
 * 403 Forbidden
 */
export class ForbiddenException extends HttpException {
  constructor(message: string = '权限不足', details?: Record<string, any>) {
    super(message, 403, details);
  }
}

/**
 * 404 Not Found
 */
export class NotFoundException extends HttpException {
  constructor(resource: string = '资源', id?: string, details?: Record<string, any>) {
    super(
      id ? `${resource} (ID: ${id}) 不存在` : `${resource}不存在`, 
      404, 
      { ...details, resource, id }
    );
  }
}

/**
 * 409 Conflict
 */
export class ConflictException extends HttpException {
  constructor(message: string = '资源冲突', details?: Record<string, any>) {
    super(message, 409, details);
  }
}

/**
 * 422 Unprocessable Entity
 */
export class UnprocessableEntityException extends HttpException {
  constructor(message: string = '请求格式正确，但语义错误无法处理', details?: Record<string, any>) {
    super(message, 422, details);
  }
}

/**
 * 429 Too Many Requests
 */
export class TooManyRequestsException extends HttpException {
  constructor(message: string = '请求过于频繁，请稍后再试', details?: Record<string, any>) {
    super(message, 429, details);
  }
}

/**
 * 500 Internal Server Error
 */
export class InternalServerErrorException extends HttpException {
  constructor(message: string = '服务器内部错误', details?: Record<string, any>) {
    super(message, 500, details);
  }
}

/**
 * 502 Bad Gateway
 */
export class BadGatewayException extends HttpException {
  constructor(message: string = '网关错误', details?: Record<string, any>) {
    super(message, 502, details);
  }
}

/**
 * 503 Service Unavailable
 */
export class ServiceUnavailableException extends HttpException {
  constructor(message: string = '服务暂时不可用', details?: Record<string, any>) {
    super(message, 503, details);
  }
}

export default {
  HttpException,
  BadRequestException,
  UnauthorizedException,
  ForbiddenException,
  NotFoundException,
  ConflictException,
  UnprocessableEntityException,
  TooManyRequestsException,
  InternalServerErrorException,
  BadGatewayException,
  ServiceUnavailableException
};