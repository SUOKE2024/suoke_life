/**
 * 认证中间件
 * 处理用户认证和授权
 */
const jwt = require('jsonwebtoken');
const { StatusCodes } = require('http-status-codes');
const { createLogger } = require('../utils/logger');
const config = require('../config');
const { cacheService } = require('../utils/cache-service');
const { metrics } = require('../utils');

const logger = createLogger('auth');

/**
 * 验证JWT令牌
 * @param {string} token - JWT令牌
 * @returns {Promise<Object>} - 解码后的令牌数据
 */
const verifyToken = (token) => {
  return new Promise((resolve, reject) => {
    jwt.verify(token, config.jwt.secret, {
      algorithms: [config.jwt.algorithm || 'HS256']
    }, (err, decoded) => {
      if (err) {
        return reject(err);
      }
      resolve(decoded);
    });
  });
};

/**
 * 从请求中提取令牌
 * @param {Object} req - Express请求对象
 * @returns {string|null} - 提取的令牌或null
 */
const extractToken = (req) => {
  // 从Authorization头中提取
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer ')) {
    return req.headers.authorization.substring(7);
  }
  
  // 从查询参数中提取
  if (req.query && req.query.token) {
    return req.query.token;
  }
  
  // 从Cookie中提取
  if (req.cookies && req.cookies.token) {
    return req.cookies.token;
  }
  
  return null;
};

/**
 * 检查令牌是否被撤销
 * @param {string} tokenId - 令牌ID
 * @returns {Promise<boolean>} - 如果令牌被撤销则为true
 */
const isTokenRevoked = async (tokenId) => {
  // 检查缓存中是否存在此令牌ID
  const cacheKey = `revoked_token:${tokenId}`;
  return !!(await cacheService.get(cacheKey));
};

/**
 * 认证中间件
 * 验证请求中的JWT令牌
 */
const authenticate = async (req, res, next) => {
  try {
    // 提取令牌
    const token = extractToken(req);
    
    if (!token) {
      const error = new Error(req.t('auth.auth_required', { namespace: 'errors' }));
      error.name = 'UnauthorizedError';
      error.status = StatusCodes.UNAUTHORIZED;
      return next(error);
    }
    
    // 验证令牌
    const decoded = await verifyToken(token);
    
    // 检查令牌是否被撤销
    if (decoded.jti && await isTokenRevoked(decoded.jti)) {
      const error = new Error(req.t('auth.token_revoked', { namespace: 'errors' }));
      error.name = 'UnauthorizedError';
      error.status = StatusCodes.UNAUTHORIZED;
      return next(error);
    }
    
    // 将用户信息添加到请求对象
    req.user = decoded;
    req.token = token;
    
    // 记录成功认证指标
    metrics.trackAuthMetrics('jwt', true);
    
    next();
  } catch (err) {
    // 处理不同类型的JWT错误
    let errorMessage = req.t('auth.invalid_token', { namespace: 'errors' });
    let errorReason = 'invalid_token';
    
    if (err.name === 'TokenExpiredError') {
      errorMessage = req.t('auth.token_expired', { namespace: 'errors' });
      errorReason = 'token_expired';
    } else if (err.name === 'JsonWebTokenError') {
      errorMessage = req.t('auth.invalid_token', { namespace: 'errors' });
      errorReason = 'invalid_signature';
    } else if (err.name === 'NotBeforeError') {
      errorMessage = req.t('auth.token_not_active', { namespace: 'errors' });
      errorReason = 'token_not_active';
    }
    
    metrics.trackAuthMetrics('jwt', false, errorReason);
    
    const authError = new Error(errorMessage);
    authError.name = 'UnauthorizedError';
    authError.status = StatusCodes.UNAUTHORIZED;
    authError.originalError = err;
    
    next(authError);
  }
};

/**
 * 授权中间件
 * 检查用户是否具有所需角色
 * @param {string|string[]} roles - 所需角色
 * @returns {Function} - Express中间件
 */
const authorize = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      const error = new Error(req.t('auth.auth_required', { namespace: 'errors' }));
      error.name = 'UnauthorizedError';
      error.status = StatusCodes.UNAUTHORIZED;
      return next(error);
    }
    
    const userRoles = Array.isArray(req.user.roles) ? req.user.roles : [req.user.role];
    const requiredRoles = Array.isArray(roles) ? roles : [roles];
    
    // 检查用户是否具有所需角色
    const hasRole = requiredRoles.some(role => userRoles.includes(role));
    
    if (!hasRole) {
      const error = new Error(req.t('common.forbidden', { namespace: 'errors' }));
      error.name = 'ForbiddenError';
      error.status = StatusCodes.FORBIDDEN;
      return next(error);
    }
    
    next();
  };
};

/**
 * 可选认证中间件
 * 如果请求中包含有效的令牌，则添加用户信息，否则继续
 */
const optionalAuthenticate = async (req, res, next) => {
  try {
    // 提取令牌
    const token = extractToken(req);
    
    if (!token) {
      return next();
    }
    
    // 验证令牌
    const decoded = await verifyToken(token);
    
    // 检查令牌是否被撤销
    if (decoded.jti && await isTokenRevoked(decoded.jti)) {
      return next();
    }
    
    // 将用户信息添加到请求对象
    req.user = decoded;
    req.token = token;
    
    next();
  } catch (err) {
    // 令牌无效，但这是可选的，所以继续
    next();
  }
};

/**
 * 设置认证中间件
 * @param {Object} app - Express应用
 */
const setupAuthMiddleware = (app) => {
  // 添加全局可选认证
  app.use(optionalAuthenticate);
  
  // 添加认证和授权方法到应用
  app.authenticate = authenticate;
  app.authorize = authorize;
};

module.exports = {
  authenticate,
  authorize,
  optionalAuthenticate,
  setupAuthMiddleware,
  verifyToken,
  extractToken,
  isTokenRevoked
};