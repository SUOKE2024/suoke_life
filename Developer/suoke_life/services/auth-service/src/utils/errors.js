/**
 * 自定义错误类型
 */

/**
 * 验证错误
 */
class ValidationError extends Error {
  constructor(message, code = 'validation/invalid-input') {
    super(message);
    this.name = 'ValidationError';
    this.code = code;
    this.statusCode = 400;
  }
}

/**
 * 认证错误
 */
class AuthenticationError extends Error {
  constructor(message, code = 'auth/unauthorized') {
    super(message);
    this.name = 'AuthenticationError';
    this.code = code;
    this.statusCode = 401;
  }
}

/**
 * 授权错误
 */
class AuthorizationError extends Error {
  constructor(message, code = 'auth/forbidden') {
    super(message);
    this.name = 'AuthorizationError';
    this.code = code;
    this.statusCode = 403;
  }
}

/**
 * 资源不存在错误
 */
class NotFoundError extends Error {
  constructor(message, code = 'server/not-found') {
    super(message);
    this.name = 'NotFoundError';
    this.code = code;
    this.statusCode = 404;
  }
}

/**
 * 冲突错误
 */
class ConflictError extends Error {
  constructor(message, code = 'server/conflict') {
    super(message);
    this.name = 'ConflictError';
    this.code = code;
    this.statusCode = 409;
  }
}

/**
 * 服务器错误
 */
class ServerError extends Error {
  constructor(message, code = 'server/internal-error') {
    super(message);
    this.name = 'ServerError';
    this.code = code;
    this.statusCode = 500;
  }
}

/**
 * 令牌错误
 */
class TokenError extends Error {
  constructor(message, code = 'auth/token-invalid') {
    super(message);
    this.name = 'TokenError';
    this.code = code;
    this.statusCode = 401;
  }
}

/**
 * 业务逻辑错误
 */
class BusinessError extends Error {
  constructor(message, code = 'business/error', statusCode = 400) {
    super(message);
    this.name = 'BusinessError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

/**
 * 限流错误
 */
class RateLimitError extends Error {
  constructor(message = '请求过于频繁，请稍后再试', code = 'server/rate-limit') {
    super(message);
    this.name = 'RateLimitError';
    this.code = code;
    this.statusCode = 429;
  }
}

module.exports = {
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ConflictError,
  ServerError,
  TokenError,
  BusinessError,
  RateLimitError
}; 