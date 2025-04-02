/**
 * API错误类
 */
export class ApiError extends Error {
  statusCode: number;
  isOperational: boolean;
  
  constructor(
    statusCode: number,
    message: string,
    isOperational = true,
    stack = ''
  ) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    
    if (stack) {
      this.stack = stack;
    } else {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

/**
 * 400 - 错误请求
 */
export class BadRequestError extends ApiError {
  constructor(message = '错误请求') {
    super(400, message);
  }
}

/**
 * 401 - 未授权
 */
export class UnauthorizedError extends ApiError {
  constructor(message = '未授权') {
    super(401, message);
  }
}

/**
 * 403 - 禁止访问
 */
export class ForbiddenError extends ApiError {
  constructor(message = '禁止访问') {
    super(403, message);
  }
}

/**
 * 404 - 未找到
 */
export class NotFoundError extends ApiError {
  constructor(message = '资源未找到') {
    super(404, message);
  }
}

/**
 * 409 - 资源冲突
 */
export class ConflictError extends ApiError {
  constructor(message = '资源冲突') {
    super(409, message);
  }
}

/**
 * 422 - 无法处理的实体
 */
export class UnprocessableEntityError extends ApiError {
  constructor(message = '无法处理的实体') {
    super(422, message);
  }
}

/**
 * 429 - 请求过多
 */
export class TooManyRequestsError extends ApiError {
  constructor(message = '请求过多') {
    super(429, message);
  }
}

/**
 * 500 - 服务器内部错误
 */
export class InternalServerError extends ApiError {
  constructor(message = '服务器内部错误') {
    super(500, message);
  }
}

/**
 * 502 - 网关错误
 */
export class BadGatewayError extends ApiError {
  constructor(message = '网关错误') {
    super(502, message);
  }
}

/**
 * 503 - 服务不可用
 */
export class ServiceUnavailableError extends ApiError {
  constructor(message = '服务不可用') {
    super(503, message);
  }
}

/**
 * 504 - 网关超时
 */
export class GatewayTimeoutError extends ApiError {
  constructor(message = '网关超时') {
    super(504, message);
  }
} 