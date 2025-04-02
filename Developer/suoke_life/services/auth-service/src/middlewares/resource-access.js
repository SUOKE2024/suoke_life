/**
 * 知识资源访问权限中间件
 * 用于验证用户对知识库和知识图谱资源的访问权限
 */
const { logger } = require('@suoke/shared').utils;

/**
 * 知识资源访问权限中间件
 * @param {Array|String} requiredPermissions 所需权限，可以是单个权限字符串或权限数组
 * @returns {Function} Express中间件
 */
const resourceAccessMiddleware = (requiredPermissions) => {
  return async (req, res, next) => {
    try {
      // 确保用户已通过认证
      if (!req.user) {
        return res.status(401).json({ 
          success: false, 
          message: '未授权访问', 
          code: 'auth/unauthorized' 
        });
      }

      // 将单个权限转换为数组
      const permissions = Array.isArray(requiredPermissions) 
        ? requiredPermissions 
        : [requiredPermissions];

      // 获取用户的权限
      const userPermissions = req.user.permissions || [];
      
      // 系统管理员拥有所有权限
      if (userPermissions.includes('admin') || req.user.role === 'admin') {
        return next();
      }

      // 验证用户是否拥有所需的所有权限
      const hasAllPermissions = permissions.every(permission => 
        userPermissions.includes(permission)
      );

      if (!hasAllPermissions) {
        logger.warn(`用户 ${req.user.id} 尝试访问需要 ${permissions.join(', ')} 权限的资源`);
        return res.status(403).json({ 
          success: false, 
          message: '权限不足', 
          code: 'auth/insufficient-permissions' 
        });
      }

      // 权限验证通过
      next();
    } catch (error) {
      logger.error(`资源访问权限验证错误: ${error.message}`);
      return res.status(500).json({ 
        success: false, 
        message: '内部服务器错误', 
        code: 'server/internal-error' 
      });
    }
  };
};

/**
 * 知识库访问权限中间件
 * @returns {Function} Express中间件
 */
const knowledgeBaseAccessMiddleware = () => {
  return resourceAccessMiddleware('knowledge:read');
};

/**
 * 知识图谱访问权限中间件
 * @returns {Function} Express中间件
 */
const knowledgeGraphAccessMiddleware = () => {
  return resourceAccessMiddleware('graph:read');
};

/**
 * 高级知识访问权限中间件（用于敏感知识）
 * @returns {Function} Express中间件
 */
const sensitiveKnowledgeAccessMiddleware = () => {
  return resourceAccessMiddleware(['knowledge:read', 'sensitive:read']);
};

/**
 * 知识编辑权限中间件
 * @returns {Function} Express中间件
 */
const knowledgeEditMiddleware = () => {
  return resourceAccessMiddleware('knowledge:write');
};

/**
 * 知识图谱编辑权限中间件
 * @returns {Function} Express中间件
 */
const graphEditMiddleware = () => {
  return resourceAccessMiddleware('graph:write');
};

/**
 * 领域特定知识访问中间件
 * @param {String} domain 知识领域（如 'tcm', 'nutrition', 'mental-health'）
 * @returns {Function} Express中间件
 */
const domainKnowledgeAccessMiddleware = (domain) => {
  return resourceAccessMiddleware(`${domain}:read`);
};

module.exports = {
  resourceAccessMiddleware,
  knowledgeBaseAccessMiddleware,
  knowledgeGraphAccessMiddleware,
  sensitiveKnowledgeAccessMiddleware,
  knowledgeEditMiddleware,
  graphEditMiddleware,
  domainKnowledgeAccessMiddleware
};