/**
 * 认证中间件
 * 处理用户身份验证和授权
 */
const jwt = require('jsonwebtoken');
const { token: tokenUtils } = require('../utils/encryption');
const { AuthenticationError, AuthorizationError } = require('../utils/error-handler');
const logger = require('../utils/logger');
const config = require('../config');

/**
 * 从请求中提取令牌
 * @param {Object} req - Express请求对象
 * @returns {string|null} 提取的令牌或null
 */
const extractToken = (req) => {
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer ')) {
    return req.headers.authorization.split(' ')[1];
  }
  
  if (req.cookies && req.cookies.token) {
    return req.cookies.token;
  }
  
  if (req.query && req.query.token) {
    return req.query.token;
  }
  
  return null;
};

/**
 * 验证用户身份，将用户信息附加到req.user
 * 如果未提供令牌，也允许请求继续（用于可选验证）
 * @param {Object} options - 中间件选项
 * @returns {Function} Express中间件
 */
const authenticate = (options = {}) => {
  return async (req, res, next) => {
    try {
      const token = extractToken(req);
      
      if (!token) {
        if (options.required) {
          throw new AuthenticationError('未提供身份验证令牌');
        }
        
        // 可选验证 - 允许未验证的请求继续
        return next();
      }
      
      // 验证令牌
      const decoded = tokenUtils.verify(token);
      
      if (!decoded) {
        throw new AuthenticationError('无效或过期的身份验证令牌');
      }
      
      // 将用户信息附加到请求对象
      req.user = decoded;
      
      // 检查令牌是否即将过期，如果是，在响应中包含新令牌
      const tokenExp = decoded.exp * 1000; // 转换为毫秒
      const now = Date.now();
      const timeUntilExpiry = tokenExp - now;
      
      // 如果令牌将在24小时内过期，刷新它
      if (timeUntilExpiry < 24 * 60 * 60 * 1000) {
        const newToken = tokenUtils.generate({ 
          id: decoded.id,
          email: decoded.email,
          role: decoded.role
        });
        
        // 在响应头中设置新令牌
        res.setHeader('X-New-Token', newToken);
        
        // 如果有cookie，更新cookie
        if (req.cookies && req.cookies.token) {
          res.cookie('token', newToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: config.jwt.cookieExpiresIn || 24 * 60 * 60 * 1000 // 默认1天
          });
        }
      }
      
      next();
    } catch (error) {
      // 仅记录非预期错误
      if (!(error instanceof AuthenticationError)) {
        logger.error('认证中间件错误', { error: error.message, stack: error.stack });
      }
      
      if (options.required) {
        return next(error);
      }
      
      // 可选验证 - 允许请求继续，即使验证失败
      next();
    }
  };
};

/**
 * 必需的身份验证中间件
 */
const requireAuth = authenticate({ required: true });

/**
 * 可选的身份验证中间件
 */
const optionalAuth = authenticate({ required: false });

/**
 * 检查用户角色授权
 * @param {...string} roles - 允许的角色列表
 * @returns {Function} Express中间件
 */
const requireRole = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return next(new AuthenticationError('需要身份验证'));
    }
    
    if (!roles.includes(req.user.role)) {
      return next(new AuthorizationError(`需要以下角色之一：${roles.join(', ')}`));
    }
    
    next();
  };
};

/**
 * 检查用户权限授权
 * @param {...string} permissions - 允许的权限列表
 * @returns {Function} Express中间件
 */
const requirePermission = (...permissions) => {
  return (req, res, next) => {
    if (!req.user) {
      return next(new AuthenticationError('需要身份验证'));
    }
    
    // 系统管理员拥有所有权限
    if (req.user.role === 'system') {
      return next();
    }
    
    // 检查用户是否拥有所有必需的权限
    const userPermissions = req.user.permissions || [];
    const hasAllPermissions = permissions.every(permission => userPermissions.includes(permission));
    
    if (!hasAllPermissions) {
      return next(new AuthorizationError(`需要以下权限：${permissions.join(', ')}`));
    }
    
    next();
  };
};

/**
 * 检查资源所有权
 * @param {Function} getResourceOwnerId - 从请求获取资源所有者ID的函数
 * @param {Object} options - 选项配置
 * @returns {Function} Express中间件
 */
const requireOwnership = (getResourceOwnerId, options = {}) => {
  const { allowAdmin = true } = options;
  
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return next(new AuthenticationError('需要身份验证'));
      }
      
      // 系统管理员和管理员可以访问任何资源（如果允许）
      if (allowAdmin && (req.user.role === 'system' || req.user.role === 'admin')) {
        return next();
      }
      
      // 获取资源所有者ID
      const ownerId = await getResourceOwnerId(req);
      
      // 字符串比较或ObjectId比较
      const isOwner = String(ownerId) === String(req.user.id);
      
      if (!isOwner) {
        return next(new AuthorizationError('您无权访问此资源'));
      }
      
      next();
    } catch (error) {
      next(error);
    }
  };
};

module.exports = {
  requireAuth,
  optionalAuth,
  requireRole,
  requirePermission,
  requireOwnership
}; 