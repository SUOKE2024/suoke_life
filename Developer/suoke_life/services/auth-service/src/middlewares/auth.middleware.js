/**
 * 认证中间件
 * 用于验证用户身份和授权
 */
const jwt = require('jsonwebtoken');
const Redis = require('ioredis');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port
});

/**
 * 验证JWT令牌中间件
 */
const verifyToken = async (req, res, next) => {
  try {
    // 从Authorization头获取令牌
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ 
        success: false, 
        message: '未提供认证令牌', 
        code: 'auth/no-token' 
      });
    }
    
    const token = authHeader.substring(7); // 去掉'Bearer '前缀
    
    // 验证令牌
    const decoded = jwt.verify(token, config.jwt.secret, {
      algorithms: ['HS256'], // 指定算法
      issuer: config.app.name || 'suoke-auth-service', // 验证签发者
      audience: config.app.baseUrl || 'https://suoke.life' // 验证接收者
    });
    
    // 检查令牌类型
    if (decoded.type !== 'access') {
      return res.status(401).json({
        success: false,
        message: '无效的令牌类型',
        code: 'auth/invalid-token-type'
      });
    }
    
    // 检查令牌是否在黑名单中
    if (decoded.jti) {
      const blacklisted = await redis.exists(`blacklist:${decoded.jti}`);
      if (blacklisted) {
        return res.status(401).json({
          success: false,
          message: '令牌已被撤销',
          code: 'auth/token-revoked'
        });
      }
    }
    
    // 将用户信息添加到请求对象
    req.user = {
      id: decoded.sub,
      role: decoded.role,
      tokenId: decoded.jti
    };
    
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: '认证令牌已过期',
        code: 'auth/token-expired'
      });
    } else if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: '无效的认证令牌',
        code: 'auth/invalid-token'
      });
    } else if (error.name === 'NotBeforeError') {
      return res.status(401).json({
        success: false,
        message: '令牌尚未激活',
        code: 'auth/token-not-active'
      });
    } else {
      logger.error(`验证令牌错误: ${error.message}`, { error });
      return res.status(500).json({
        success: false,
        message: '内部服务器错误',
        code: 'server/internal-error'
      });
    }
  }
};

/**
 * 验证用户是否为管理员
 */
const verifyAdmin = (req, res, next) => {
  try {
    // 必须先经过verifyToken中间件
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        message: '未授权访问', 
        code: 'auth/unauthorized' 
      });
    }
    
    // 检查用户角色
    if (req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: '需要管理员权限',
        code: 'auth/admin-required'
      });
    }
    
    next();
  } catch (error) {
    logger.error(`验证管理员权限错误: ${error.message}`, { error });
    return res.status(500).json({
      success: false,
      message: '内部服务器错误',
      code: 'server/internal-error'
    });
  }
};

/**
 * 可选的令牌验证中间件
 * 如果提供了令牌，则验证并添加用户信息到请求
 * 如果没有提供令牌，则继续处理请求
 */
const optionalToken = async (req, res, next) => {
  try {
    // 从Authorization头获取令牌
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      // 没有提供令牌，继续处理
      return next();
    }
    
    const token = authHeader.substring(7); // 去掉'Bearer '前缀
    
    try {
      // 验证令牌
      const decoded = jwt.verify(token, config.jwt.secret, {
        algorithms: ['HS256'],
        issuer: config.app.name || 'suoke-auth-service',
        audience: config.app.baseUrl || 'https://suoke.life'
      });

      // 检查令牌是否在黑名单中
      if (decoded.jti) {
        const blacklisted = await redis.exists(`blacklist:${decoded.jti}`);
        if (blacklisted) {
          return next();
        }
      }
      
      // 将用户信息添加到请求对象
      req.user = {
        id: decoded.sub,
        role: decoded.role,
        tokenId: decoded.jti
      };
    } catch (tokenError) {
      // 令牌验证失败，但由于是可选的，我们不返回错误
      logger.debug(`可选令牌验证失败: ${tokenError.message}`);
    }
    
    next();
  } catch (error) {
    // 由于是可选的，只记录日志并继续处理
    logger.debug(`可选令牌处理错误: ${error.message}`);
    next();
  }
};

/**
 * 验证用户具有特定角色的中间件
 * @param {string|string[]} roles 所需角色，可以是单个角色字符串或角色数组
 * @returns {Function} Express中间件
 */
const verifyRole = (roles) => {
  return (req, res, next) => {
    try {
      // 必须先经过verifyToken中间件
      if (!req.user) {
        return res.status(401).json({ 
          success: false, 
          message: '未授权访问', 
          code: 'auth/unauthorized' 
        });
      }
      
      // 将单个角色转换为数组
      const requiredRoles = Array.isArray(roles) ? roles : [roles];
      
      // 检查用户角色是否在所需角色列表中
      if (!requiredRoles.includes(req.user.role)) {
        return res.status(403).json({
          success: false,
          message: '权限不足',
          code: 'auth/insufficient-role',
          requiredRoles: requiredRoles
        });
      }
      
      next();
    } catch (error) {
      logger.error(`验证角色权限错误: ${error.message}`, { error });
      return res.status(500).json({
        success: false,
        message: '内部服务器错误',
        code: 'server/internal-error'
      });
    }
  };
};

/**
 * 验证用户拥有特定权限的中间件
 * @param {string|string[]} permissions 所需权限，可以是单个权限字符串或权限数组
 * @returns {Function} Express中间件
 */
const verifyPermission = (permissions) => {
  return async (req, res, next) => {
    try {
      // 必须先经过verifyToken中间件
      if (!req.user) {
        return res.status(401).json({ 
          success: false, 
          message: '未授权访问', 
          code: 'auth/unauthorized' 
        });
      }
      
      // 将单个权限转换为数组
      const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions];
      
      // 从Redis或数据库获取用户权限
      const userPermissions = await getUserPermissions(req.user.id);
      
      // 检查用户是否拥有所需权限
      const hasPermission = requiredPermissions.every(permission => 
        userPermissions.includes(permission)
      );
      
      if (!hasPermission) {
        return res.status(403).json({
          success: false,
          message: '权限不足',
          code: 'auth/insufficient-permission',
          requiredPermissions: requiredPermissions
        });
      }
      
      next();
    } catch (error) {
      logger.error(`验证权限错误: ${error.message}`, { error });
      return res.status(500).json({
        success: false,
        message: '内部服务器错误',
        code: 'server/internal-error'
      });
    }
  };
};

/**
 * 获取用户权限
 * @param {string} userId 用户ID
 * @returns {Promise<string[]>} 用户权限列表
 */
const getUserPermissions = async (userId) => {
  try {
    // 首先尝试从Redis缓存获取
    const cachedPermissions = await redis.get(`user_permissions:${userId}`);
    if (cachedPermissions) {
      return JSON.parse(cachedPermissions);
    }
    
    // 如果缓存中没有，从数据库查询
    const { db } = require('../config/database');
    const userRoles = await db('user_roles')
      .join('roles', 'user_roles.role_id', 'roles.id')
      .where('user_roles.user_id', userId)
      .select('roles.name');
    
    const rolePermissions = await db('role_permissions')
      .join('permissions', 'role_permissions.permission_id', 'permissions.id')
      .whereIn('role_permissions.role_id', userRoles.map(r => r.id))
      .select('permissions.name')
      .distinct();
    
    const permissions = rolePermissions.map(p => p.name);
    
    // 缓存结果，有效期1小时
    await redis.set(
      `user_permissions:${userId}`,
      JSON.stringify(permissions),
      'EX',
      60 * 60
    );
    
    return permissions;
  } catch (error) {
    logger.error(`获取用户权限错误: ${error.message}`, { error, userId });
    return []; // 权限获取失败时返回空数组
  }
};

/**
 * 验证二因素认证会话
 * 用于验证二因素认证流程中的临时会话
 * @returns {Function} 中间件函数
 */
const verifyTwoFactorSession = async (req, res, next) => {
  try {
    const { tempSessionId, userId } = req.body;
    
    if (!tempSessionId || !userId) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数',
        code: 'auth/missing-parameters'
      });
    }
    
    // 获取会话服务
    const sessionService = require('../services/session.service');
    const session = await sessionService.getSessionById(tempSessionId);
    
    // 验证会话是否有效
    if (!session || session.user_id !== userId || session.status !== 'pending_2fa') {
      return res.status(401).json({
        success: false,
        message: '无效的二因素认证会话',
        code: 'auth/invalid-session'
      });
    }
    
    // 检查会话是否过期
    const now = new Date();
    if (new Date(session.expires_at) < now) {
      return res.status(401).json({
        success: false,
        message: '二因素认证会话已过期',
        code: 'auth/session-expired'
      });
    }
    
    // 验证通过，继续请求
    next();
  } catch (error) {
    logger.error('验证二因素认证会话失败', { error });
    return res.status(500).json({
      success: false,
      message: '服务器错误',
      code: 'server/error'
    });
  }
};

// 导出中间件
module.exports = {
  verifyToken,
  verifyAdmin,
  optionalToken,
  verifyRole,
  verifyPermission,
  verifyTwoFactorSession
};