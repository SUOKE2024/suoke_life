/**
 * 知识授权服务
 * 提供与知识库和知识图谱访问权限相关的功能
 */
const { logger } = require('@suoke/shared').utils;
const { knexClient } = require('../utils/db');
const HttpError = require('../utils/http-error');
const { redisClient } = require('../utils/redis');

// 权限缓存TTL（秒）
const PERMISSIONS_CACHE_TTL = 1800; // 30分钟
const ACCESS_CACHE_TTL = 3600; // 1小时
const ROLE_PERMISSIONS_CACHE_TTL = 7200; // 2小时

// 权限缓存分级
const CACHE_LEVELS = {
  L1: 'L1', // 高频访问权限（10分钟TTL）
  L2: 'L2', // 标准权限（30分钟TTL）
  L3: 'L3'  // 低频访问权限（2小时TTL）
};

/**
 * 知识授权服务
 */
class KnowledgeAuthService {
  constructor() {
    // 初始化内存缓存
    this.memoryCache = {
      accessChecks: new Map(),
      userPermissions: new Map()
    };
    
    // 定时清理内存缓存（每5分钟）
    setInterval(() => this.cleanupMemoryCache(), 300000);
  }
  
  /**
   * 获取缓存级别TTL
   * @param {string} level 缓存级别
   * @returns {number} TTL（秒）
   */
  getCacheTTL(level) {
    switch(level) {
      case CACHE_LEVELS.L1:
        return 600; // 10分钟
      case CACHE_LEVELS.L2:
        return PERMISSIONS_CACHE_TTL; // 30分钟
      case CACHE_LEVELS.L3:
        return ROLE_PERMISSIONS_CACHE_TTL; // 2小时
      default:
        return PERMISSIONS_CACHE_TTL;
    }
  }
  
  /**
   * 清理内存缓存
   */
  cleanupMemoryCache() {
    const now = Date.now();
    
    // 清理过期的访问权限检查缓存
    this.memoryCache.accessChecks.forEach((item, key) => {
      if (now > item.expiresAt) {
        this.memoryCache.accessChecks.delete(key);
      }
    });
    
    // 清理过期的用户权限缓存
    this.memoryCache.userPermissions.forEach((item, key) => {
      if (now > item.expiresAt) {
        this.memoryCache.userPermissions.delete(key);
      }
    });
    
    logger.debug(`内存缓存清理完成, 当前缓存大小: accessChecks=${this.memoryCache.accessChecks.size}, userPermissions=${this.memoryCache.userPermissions.size}`);
  }
  
  /**
   * 确定资源的缓存级别
   * @param {string} resourceType 资源类型
   * @param {string} action 操作类型
   * @returns {string} 缓存级别
   */
  determineCacheLevel(resourceType, action) {
    // 高频访问的只读资源使用L1缓存
    if (action === 'read' && 
        (resourceType === 'knowledge_base' || 
         resourceType === 'knowledge_node' || 
         resourceType === 'article')) {
      return CACHE_LEVELS.L1;
    }
    
    // 基本知识资源使用L2缓存
    if (resourceType.startsWith('knowledge_') || 
        resourceType.startsWith('graph_')) {
      return CACHE_LEVELS.L2;
    }
    
    // 其他资源使用L3缓存
    return CACHE_LEVELS.L3;
  }
  
  /**
   * 从内存缓存获取值
   * @param {Map} cache 缓存Map
   * @param {string} key 键
   * @returns {any|null} 缓存值或null
   */
  getFromMemoryCache(cache, key) {
    const item = cache.get(key);
    if (item && Date.now() < item.expiresAt) {
      return item.value;
    }
    return null;
  }
  
  /**
   * 设置内存缓存
   * @param {Map} cache 缓存Map
   * @param {string} key 键
   * @param {any} value 值
   * @param {number} ttl TTL（秒）
   */
  setMemoryCache(cache, key, value, ttl) {
    cache.set(key, {
      value,
      expiresAt: Date.now() + (ttl * 1000)
    });
  }
  
  /**
   * 检查用户是否拥有指定知识资源的访问权限
   * @param {number} userId 用户ID
   * @param {string} resourceType 资源类型 ('knowledge_base', 'knowledge_graph', etc.)
   * @param {string} resourceId 资源ID
   * @param {string} action 操作类型 ('read', 'write', 'query', etc.)
   * @returns {Promise<boolean>} 是否有权限
   */
  async checkAccess(userId, resourceType, resourceId, action) {
    try {
      // 内存缓存键
      const memoryCacheKey = `${userId}:${resourceType}:${resourceId}:${action}`;
      
      // 1. 检查内存缓存
      const memoryCachedResult = this.getFromMemoryCache(
        this.memoryCache.accessChecks, 
        memoryCacheKey
      );
      
      if (memoryCachedResult !== null) {
        return memoryCachedResult;
      }
      
      // 2. 检查Redis缓存
      const redisCacheKey = `access:${userId}:${resourceType}:${resourceId}:${action}`;
      const cachedResult = await redisClient.get(redisCacheKey);
      
      if (cachedResult !== null) {
        // 更新内存缓存
        const cacheLevel = this.determineCacheLevel(resourceType, action);
        const ttl = this.getCacheTTL(cacheLevel);
        this.setMemoryCache(
          this.memoryCache.accessChecks,
          memoryCacheKey,
          cachedResult === 'true',
          ttl
        );
        
        return cachedResult === 'true';
      }
      
      // 3. 获取用户权限
      const userPermissions = await this.getUserPermissions(userId);
      
      // 系统管理员拥有所有权限
      if (userPermissions.includes('admin')) {
        // 缓存结果
        const cacheLevel = CACHE_LEVELS.L2;
        const ttl = this.getCacheTTL(cacheLevel);
        
        await redisClient.set(redisCacheKey, 'true', 'EX', ttl);
        this.setMemoryCache(
          this.memoryCache.accessChecks,
          memoryCacheKey,
          true,
          ttl
        );
        
        return true;
      }
      
      // 4. 根据资源类型和操作确定所需权限
      const requiredPermission = this.getRequiredPermission(resourceType, action);
      
      // 5. 检查用户是否拥有所需权限
      const hasPermission = userPermissions.includes(requiredPermission);
      
      // 6. 确定缓存级别并设置过期时间
      const cacheLevel = this.determineCacheLevel(resourceType, action);
      const ttl = this.getCacheTTL(cacheLevel);
      
      // 7. 缓存结果
      await redisClient.set(redisCacheKey, hasPermission ? 'true' : 'false', 'EX', ttl);
      this.setMemoryCache(
        this.memoryCache.accessChecks,
        memoryCacheKey,
        hasPermission,
        ttl
      );
      
      return hasPermission;
    } catch (error) {
      logger.error(`检查访问权限错误: ${error.message}`);
      throw new HttpError(500, '检查访问权限时出错');
    }
  }
  
  /**
   * 批量检查用户是否拥有指定知识资源的访问权限
   * @param {number} userId 用户ID
   * @param {Array<{resourceType: string, resourceId: string, action: string}>} resources 资源列表
   * @returns {Promise<Map<string, boolean>>} 权限检查结果映射
   */
  async batchCheckAccess(userId, resources) {
    try {
      const results = new Map();
      const checkPromises = [];
      
      for (const resource of resources) {
        const { resourceType, resourceId, action } = resource;
        const resultKey = `${resourceType}:${resourceId}:${action}`;
        
        // 创建检查Promise
        checkPromises.push(
          this.checkAccess(userId, resourceType, resourceId, action)
            .then(hasAccess => {
              results.set(resultKey, hasAccess);
            })
            .catch(error => {
              logger.error(`批量检查权限错误: ${error.message}`);
              results.set(resultKey, false); // 错误时默认无权限
            })
        );
      }
      
      // 等待所有检查完成
      await Promise.all(checkPromises);
      
      return results;
    } catch (error) {
      logger.error(`批量检查访问权限错误: ${error.message}`);
      throw new HttpError(500, '批量检查访问权限时出错');
    }
  }
  
  /**
   * 记录资源访问日志
   * @param {number} userId 用户ID
   * @param {string} resourceType 资源类型
   * @param {string} resourceId 资源ID
   * @param {string} action 操作类型
   * @param {object} metadata 额外元数据
   * @returns {Promise<void>}
   */
  async logAccess(userId, resourceType, resourceId, action, metadata = {}) {
    try {
      const { ip_address, user_agent } = metadata;
      
      await knexClient('knowledge_access_logs').insert({
        user_id: userId,
        resource_type: resourceType,
        resource_id: resourceId,
        action,
        ip_address,
        user_agent,
        accessed_at: new Date()
      });
    } catch (error) {
      logger.error(`记录访问日志错误: ${error.message}`);
      // 不抛出异常，日志记录不应影响主要业务流程
    }
  }
  
  /**
   * 获取用户权限列表
   * @param {number} userId 用户ID
   * @returns {Promise<Array<string>>} 权限列表
   */
  async getUserPermissions(userId) {
    try {
      // 检查内存缓存
      const memoryCacheKey = `user_permissions:${userId}`;
      const memoryCachedPermissions = this.getFromMemoryCache(
        this.memoryCache.userPermissions,
        memoryCacheKey
      );
      
      if (memoryCachedPermissions) {
        return memoryCachedPermissions;
      }
      
      // 检查Redis缓存
      const redisCacheKey = `user_permissions:${userId}`;
      const cachedPermissions = await redisClient.get(redisCacheKey);
      
      if (cachedPermissions) {
        const permissions = JSON.parse(cachedPermissions);
        
        // 更新内存缓存
        this.setMemoryCache(
          this.memoryCache.userPermissions,
          memoryCacheKey,
          permissions,
          PERMISSIONS_CACHE_TTL
        );
        
        return permissions;
      }
      
      // 获取用户信息和角色
      const user = await knexClient('users')
        .select(['id', 'role', 'secondary_roles'])
        .where('id', userId)
        .first();
      
      if (!user) {
        throw new HttpError(404, '用户不存在');
      }
      
      // 获取用户权限记录
      const permissionsRecord = await knexClient('user_permissions')
        .where('user_id', userId)
        .first();
      
      // 获取用户组权限记录
      const userGroups = await knexClient('user_groups')
        .select('group_id')
        .where('user_id', userId);
      
      const groupIds = userGroups.map(g => g.group_id);
      
      const groupPermissions = groupIds.length > 0
        ? await knexClient('group_permissions')
            .whereIn('group_id', groupIds)
        : [];
      
      const permissions = new Set();
      
      // 将主角色添加到权限列表
      permissions.add(user.role);
      
      // 处理次要角色（可能存储为JSON字符串或数组）
      if (user.secondary_roles) {
        let secondaryRoles = user.secondary_roles;
        
        if (typeof secondaryRoles === 'string') {
          try {
            secondaryRoles = JSON.parse(secondaryRoles);
          } catch (e) {
            // 如果解析失败，尝试将其视为逗号分隔的字符串
            secondaryRoles = secondaryRoles.split(',').map(r => r.trim());
          }
        }
        
        // 添加所有次要角色
        if (Array.isArray(secondaryRoles)) {
          secondaryRoles.forEach(role => permissions.add(role));
        }
      }
      
      // 处理用户直接权限
      if (permissionsRecord) {
        Object.entries(permissionsRecord).forEach(([key, value]) => {
          // 跳过用户ID和主键字段
          if (key === 'user_id' || key === 'id') return;
          
          // 仅添加值为true的权限
          if (value === true || value === 1) {
            // 将下划线分隔的字段转换为冒号分隔的权限格式
            // 例如 knowledge_read => knowledge:read
            const permission = key.replace(/_/g, ':');
            permissions.add(permission);
          }
        });
      }
      
      // 处理用户组权限
      groupPermissions.forEach(group => {
        Object.entries(group).forEach(([key, value]) => {
          // 跳过组ID和主键字段
          if (key === 'group_id' || key === 'id') return;
          
          // 仅添加值为true的权限
          if (value === true || value === 1) {
            // 将下划线分隔的字段转换为冒号分隔的权限格式
            const permission = key.replace(/_/g, ':');
            permissions.add(permission);
          }
        });
      });
      
      // 获取基于角色的预定义权限
      const rolePermissions = await this.getRolePermissions([...permissions]);
      
      // 合并角色权限
      rolePermissions.forEach(permission => permissions.add(permission));
      
      // 转为数组
      const permissionsArray = [...permissions];
      
      // 缓存权限列表
      await redisClient.set(redisCacheKey, JSON.stringify(permissionsArray), 'EX', PERMISSIONS_CACHE_TTL);
      
      // 更新内存缓存
      this.setMemoryCache(
        this.memoryCache.userPermissions,
        memoryCacheKey,
        permissionsArray,
        PERMISSIONS_CACHE_TTL
      );
      
      return permissionsArray;
    } catch (error) {
      logger.error(`获取用户权限错误: ${error.message}`);
      throw new HttpError(500, '获取用户权限时出错');
    }
  }
  
  /**
   * 获取角色对应的预定义权限
   * @param {Array<string>} roles 角色列表
   * @returns {Promise<Array<string>>} 权限列表
   */
  async getRolePermissions(roles) {
    try {
      if (!roles || roles.length === 0) {
        return [];
      }
      
      // 角色排序以确保缓存键一致性
      const sortedRoles = [...roles].sort();
      
      // 检查内存缓存
      const memoryCacheKey = `role_permissions:${sortedRoles.join(',')}`;
      const memoryCachedPermissions = this.getFromMemoryCache(
        this.memoryCache.userPermissions,
        memoryCacheKey
      );
      
      if (memoryCachedPermissions) {
        return memoryCachedPermissions;
      }
      
      // 检查Redis缓存
      const redisCacheKey = `role_permissions:${sortedRoles.join(',')}`;
      const cachedPermissions = await redisClient.get(redisCacheKey);
      
      if (cachedPermissions) {
        const permissions = JSON.parse(cachedPermissions);
        
        // 更新内存缓存
        this.setMemoryCache(
          this.memoryCache.userPermissions,
          memoryCacheKey,
          permissions,
          ROLE_PERMISSIONS_CACHE_TTL
        );
        
        return permissions;
      }
      
      // 从数据库获取角色权限
      const rolePermissionsRecords = await knexClient('role_permissions')
        .whereIn('role', roles);
      
      const permissions = new Set();
      
      // 处理角色权限
      rolePermissionsRecords.forEach(record => {
        Object.entries(record).forEach(([key, value]) => {
          // 跳过角色字段和主键
          if (key === 'role' || key === 'id') return;
          
          // 仅添加值为true的权限
          if (value === true || value === 1) {
            // 将下划线分隔的字段转换为冒号分隔的权限格式
            const permission = key.replace(/_/g, ':');
            permissions.add(permission);
          }
        });
      });
      
      // 特殊角色处理
      if (roles.includes('admin')) {
        // 管理员拥有所有权限
        const adminPermissions = [
          'knowledge:read', 'knowledge:write',
          'graph:read', 'graph:write',
          'sensitive:read', 'sensitive:write',
          'tcm:read', 'tcm:write',
          'nutrition:read', 'nutrition:write',
          'mental_health:read', 'mental_health:write',
          'environmental_health:read', 'environmental_health:write',
          'precision_medicine:read', 'precision_medicine:write'
        ];
        
        adminPermissions.forEach(perm => permissions.add(perm));
      }
      
      // 转为数组
      const permissionsArray = [...permissions];
      
      // 缓存权限列表，使用更长的TTL
      await redisClient.set(redisCacheKey, JSON.stringify(permissionsArray), 'EX', ROLE_PERMISSIONS_CACHE_TTL);
      
      // 更新内存缓存
      this.setMemoryCache(
        this.memoryCache.userPermissions,
        memoryCacheKey,
        permissionsArray,
        ROLE_PERMISSIONS_CACHE_TTL
      );
      
      return permissionsArray;
    } catch (error) {
      logger.error(`获取角色权限错误: ${error.message}`);
      return [];
    }
  }
  
  /**
   * 根据资源类型和操作确定所需权限
   * @param {string} resourceType 资源类型
   * @param {string} action 操作类型
   * @returns {string} 所需权限
   */
  getRequiredPermission(resourceType, action) {
    // 资源类型到权限前缀的映射
    const resourceTypeMap = {
      'knowledge_base': 'knowledge',
      'knowledge_node': 'knowledge',
      'knowledge_graph': 'graph',
      'graph_node': 'graph',
      'graph_relation': 'graph',
      'graph_query': 'graph',
      'sensitive_data': 'sensitive',
      'tcm_knowledge': 'tcm',
      'nutrition_knowledge': 'nutrition',
      'mental_health_knowledge': 'mental_health',
      'environmental_health_knowledge': 'environmental_health',
      'precision_medicine_knowledge': 'precision_medicine'
    };
    
    // 操作到权限后缀的映射
    const actionMap = {
      'read': 'read',
      'view': 'read',
      'get': 'read',
      'list': 'read',
      'search': 'read',
      'write': 'write',
      'create': 'write',
      'update': 'write',
      'delete': 'write',
      'query': 'read'
    };
    
    // 获取权限前缀和后缀
    const permPrefix = resourceTypeMap[resourceType] || resourceType;
    const permSuffix = actionMap[action] || action;
    
    // 返回完整权限名称
    return `${permPrefix}:${permSuffix}`;
  }
  
  /**
   * 分配知识库权限给用户
   * @param {number} userId 用户ID
   * @param {Array<string>} permissions 权限列表
   * @returns {Promise<void>}
   */
  async assignPermissions(userId, permissions) {
    try {
      // 验证用户是否存在
      const user = await knexClient('users')
        .select('id')
        .where('id', userId)
        .first();
        
      if (!user) {
        throw new HttpError(404, '用户不存在');
      }
      
      // 获取现有权限记录
      let permissionsRecord = await knexClient('user_permissions')
        .where('user_id', userId)
        .first();
      
      // 准备更新数据
      const updateData = {};
      
      // 转换权限格式：knowledge:read => knowledge_read
      permissions.forEach(permission => {
        const permKey = permission.replace(':', '_');
        updateData[permKey] = true;
      });
      
      // 如果用户权限记录存在，则更新
      if (permissionsRecord) {
        await knexClient('user_permissions')
          .where('user_id', userId)
          .update(updateData);
      } else {
        // 否则创建新记录
        updateData.user_id = userId;
        await knexClient('user_permissions')
          .insert(updateData);
      }
      
      // 删除用户权限缓存
      await redisClient.del(`user_permissions:${userId}`);
      
      // 删除内存缓存
      this.memoryCache.userPermissions.delete(`user_permissions:${userId}`);
      
      // 删除与用户相关的访问检查缓存
      const accessCachePattern = `access:${userId}:*`;
      const accessCacheKeys = await redisClient.keys(accessCachePattern);
      
      if (accessCacheKeys.length > 0) {
        await redisClient.del(accessCacheKeys);
      }
      
      // 清理用户相关的内存访问缓存
      const userPrefix = `${userId}:`;
      for (const key of this.memoryCache.accessChecks.keys()) {
        if (key.startsWith(userPrefix)) {
          this.memoryCache.accessChecks.delete(key);
        }
      }
      
    } catch (error) {
      logger.error(`分配知识库权限错误: ${error.message}`);
      if (error instanceof HttpError) {
        throw error;
      }
      throw new HttpError(500, '分配知识库权限时出错');
    }
  }
  
  /**
   * 撤销用户的知识库权限
   * @param {number} userId 用户ID
   * @param {Array<string>} permissions 权限列表
   * @returns {Promise<void>}
   */
  async revokePermissions(userId, permissions) {
    try {
      // 获取现有权限记录
      const permissionsRecord = await knexClient('user_permissions')
        .where('user_id', userId)
        .first();
      
      // 如果用户权限记录不存在，则无需操作
      if (!permissionsRecord) {
        return;
      }
      
      // 准备更新数据
      const updateData = {};
      
      // 转换权限格式：knowledge:read => knowledge_read
      permissions.forEach(permission => {
        const permKey = permission.replace(':', '_');
        updateData[permKey] = false;
      });
      
      // 更新权限记录
      await knexClient('user_permissions')
        .where('user_id', userId)
        .update(updateData);
      
      // 删除用户权限缓存
      await redisClient.del(`user_permissions:${userId}`);
      
      // 删除内存缓存
      this.memoryCache.userPermissions.delete(`user_permissions:${userId}`);
      
      // 删除与用户相关的访问检查缓存
      const accessCachePattern = `access:${userId}:*`;
      const accessCacheKeys = await redisClient.keys(accessCachePattern);
      
      if (accessCacheKeys.length > 0) {
        await redisClient.del(accessCacheKeys);
      }
      
      // 清理用户相关的内存访问缓存
      const userPrefix = `${userId}:`;
      for (const key of this.memoryCache.accessChecks.keys()) {
        if (key.startsWith(userPrefix)) {
          this.memoryCache.accessChecks.delete(key);
        }
      }
      
    } catch (error) {
      logger.error(`撤销知识库权限错误: ${error.message}`);
      throw new HttpError(500, '撤销知识库权限时出错');
    }
  }

  /**
   * 获取用户的实际有效权限，解决多角色下的权限冲突
   * @param {Array<string>} permissions 原始权限列表
   * @returns {Object} 有效权限映射
   */
  getEffectivePermissions(permissions) {
    // 从权限列表中提取角色
    const roles = permissions.filter(perm => 
      !perm.includes(':') && !['admin', 'user'].includes(perm)
    );
    
    // 提取实际权限（格式为 resource:action）
    const permissionList = permissions.filter(perm => perm.includes(':'));
    
    // 创建资源到权限的映射
    const resourcePermissions = {};
    
    // 处理明确的权限
    permissionList.forEach(permission => {
      const [resource, action] = permission.split(':');
      
      if (!resourcePermissions[resource]) {
        resourcePermissions[resource] = {};
      }
      
      resourcePermissions[resource][action] = true;
    });
    
    // 角色优先级，数字越大优先级越高
    const rolePriorities = {
      'user': 0,
      'knowledge_reader': 10,
      'knowledge_contributor': 20,
      'knowledge_editor': 30,
      'knowledge_manager': 40,
      'graph_reader': 15,
      'graph_editor': 35,
      'sensitive_reader': 25,
      'admin': 100
    };
    
    // 角色权限映射
    const rolePermissionMap = {
      'admin': {
        'knowledge': ['read', 'write', 'delete', 'admin'],
        'graph': ['read', 'write', 'query', 'delete', 'admin'],
        'sensitive': ['read', 'write'],
        'tcm': ['read', 'write'],
        'nutrition': ['read', 'write'],
        'mental_health': ['read', 'write'],
        'environmental_health': ['read', 'write'],
        'precision_medicine': ['read', 'write']
      },
      'knowledge_manager': {
        'knowledge': ['read', 'write', 'delete'],
        'graph': ['read', 'query']
      },
      'knowledge_editor': {
        'knowledge': ['read', 'write']
      },
      'knowledge_contributor': {
        'knowledge': ['read', 'write']
      },
      'knowledge_reader': {
        'knowledge': ['read']
      },
      'graph_editor': {
        'graph': ['read', 'write', 'query']
      },
      'graph_reader': {
        'graph': ['read', 'query']
      },
      'sensitive_reader': {
        'sensitive': ['read']
      }
    };
    
    // 为每个资源应用基于角色的权限，考虑角色优先级
    roles.forEach(role => {
      // 获取角色优先级，默认为最低优先级
      const rolePriority = rolePriorities[role] || 0;
      
      // 跳过未知角色
      if (!rolePermissionMap[role]) {
        return;
      }
      
      // 处理角色权限
      const rolePerms = rolePermissionMap[role];
      
      // 遍历角色的所有资源权限
      Object.entries(rolePerms).forEach(([resource, actions]) => {
        if (!resourcePermissions[resource]) {
          resourcePermissions[resource] = {};
        }
        
        // 为每个操作应用权限，考虑优先级
        actions.forEach(action => {
          // 检查是否已有此操作的权限及其优先级
          const existingPriority = resourcePermissions[resource][`_priority_${action}`] || 0;
          
          // 只有当当前角色优先级高于已有权限的优先级时，才覆盖现有权限
          if (rolePriority > existingPriority) {
            resourcePermissions[resource][action] = true;
            resourcePermissions[resource][`_priority_${action}`] = rolePriority;
          }
        });
      });
    });
    
    // 移除内部使用的优先级标记
    Object.keys(resourcePermissions).forEach(resource => {
      Object.keys(resourcePermissions[resource]).forEach(key => {
        if (key.startsWith('_priority_')) {
          delete resourcePermissions[resource][key];
        }
      });
    });
    
    // 如果用户拥有admin角色，则拥有所有权限
    if (permissions.includes('admin')) {
      const adminPermissions = rolePermissionMap['admin'];
      Object.entries(adminPermissions).forEach(([resource, actions]) => {
        if (!resourcePermissions[resource]) {
          resourcePermissions[resource] = {};
        }
        
        actions.forEach(action => {
          resourcePermissions[resource][action] = true;
        });
      });
    }
    
    return resourcePermissions;
  }
}

module.exports = new KnowledgeAuthService();