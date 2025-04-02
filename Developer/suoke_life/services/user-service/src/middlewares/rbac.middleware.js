/**
 * 基于角色的访问控制(RBAC)中间件
 * 用于控制不同角色对API的访问权限
 */
const { ApiResponse } = require('@suoke/shared').responses;
const { logger } = require('@suoke/shared').utils;

/**
 * 角色权限配置
 */
const ROLES = {
  user: ['read:own', 'update:own'],
  premium_user: ['read:own', 'update:own', 'premium_features'],
  admin: ['read:any', 'update:any', 'delete:any', 'create:any'],
  system_admin: ['*']
};

/**
 * 检查是否有权限
 * @param {string} userRole - 用户角色
 * @param {string} requiredPermission - 需要的权限
 * @returns {boolean} - 是否有权限
 */
const hasPermission = (userRole, requiredPermission) => {
  if (!ROLES[userRole]) {
    return false;
  }

  // 系统管理员拥有所有权限
  if (userRole === 'system_admin') {
    return true;
  }

  return ROLES[userRole].includes(requiredPermission) || 
         ROLES[userRole].includes('*');
};

/**
 * 检查资源所有权
 * @param {Object} user - 当前用户
 * @param {string} resourceId - 资源ID
 * @param {string} resourceType - 资源类型
 * @returns {Promise<boolean>} - 是否拥有资源
 */
const checkOwnership = async (user, resourceId, resourceType) => {
  // 根据不同的资源类型进行所有权检查
  switch (resourceType) {
    case 'profile':
      return user.id === resourceId;
    case 'health-profile':
      return user.id === resourceId;
    case 'points':
      return user.id === resourceId;
    case 'achievement':
      // 这里可以调用成就服务检查所有权
      return user.id === resourceId;
    // 可以添加更多资源类型的检查
    default:
      return false;
  }
};

/**
 * 检查用户是否有权限进行操作
 * @param {string} permission - 需要的权限
 * @param {string} resourceType - 资源类型
 */
exports.hasPermission = (permission, resourceType = null) => {
  return async (req, res, next) => {
    try {
      // 确保用户已经通过了身份验证
      if (!req.user) {
        return ApiResponse.unauthorized(res, '请先登录');
      }

      const userRole = req.user.role || 'user';
      let hasAccess = false;

      // 检查用户角色是否有所需权限
      if (permission.endsWith(':own')) {
        // 对于自己资源的权限，需要检查资源所有权
        const resourceId = req.params.id || req.body.id || req.query.id;
        
        if (!resourceId) {
          return ApiResponse.forbidden(res, '缺少资源ID');
        }

        const isOwner = await checkOwnership(req.user, resourceId, resourceType);
        
        if (isOwner && hasPermission(userRole, permission)) {
          hasAccess = true;
        }
      } else {
        // 对于任何资源的权限，直接检查角色权限
        hasAccess = hasPermission(userRole, permission);
      }

      if (hasAccess) {
        return next();
      }

      logger.warn('权限不足', {
        user: req.user.id,
        role: userRole,
        permission,
        resourceType,
        path: req.path
      });

      return ApiResponse.forbidden(res, '您没有权限执行此操作');
    } catch (error) {
      logger.error('权限检查失败', { error: error.message });
      return ApiResponse.error(res, '权限验证失败，请重试');
    }
  };
};

/**
 * 检查用户是否拥有指定角色
 * @param {string|array} roles - 允许的角色
 */
exports.hasRole = (roles) => {
  return (req, res, next) => {
    try {
      // 确保用户已经通过了身份验证
      if (!req.user) {
        return ApiResponse.unauthorized(res, '请先登录');
      }

      const userRole = req.user.role || 'user';
      
      // 转换为数组以便统一处理
      const allowedRoles = Array.isArray(roles) ? roles : [roles];
      
      // 系统管理员可以访问任何内容
      if (userRole === 'system_admin') {
        return next();
      }
      
      // 检查用户角色是否在允许的角色列表中
      if (allowedRoles.includes(userRole)) {
        return next();
      }

      logger.warn('角色权限不足', {
        user: req.user.id,
        role: userRole,
        requiredRoles: allowedRoles,
        path: req.path
      });

      return ApiResponse.forbidden(res, '您没有访问此资源的权限');
    } catch (error) {
      logger.error('角色检查失败', { error: error.message });
      return ApiResponse.error(res, '权限验证失败，请重试');
    }
  };
}; 