/**
 * 知识库认证控制器
 * 处理与知识库和知识图谱访问权限相关的请求
 */
const { responseHandler, errorHandler } = require('@suoke/shared').utils;
const knowledgeAuthService = require('../services/knowledge-auth.service');
const { knexClient } = require('../utils/db');
const logger = require('../utils/logger');

/**
 * 获取当前用户的知识库权限
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getCurrentUserPermissions = async (req, res) => {
  try {
    const userId = req.user.id;
    const permissions = await knowledgeAuthService.getUserPermissions(userId);
    
    // 过滤出与知识库相关的权限
    const knowledgePermissions = permissions.filter(permission => {
      return permission.includes('knowledge:') || 
             permission.includes('graph:') || 
             permission.includes('sensitive:') ||
             permission.includes(':read') ||
             permission.includes(':write');
    });
    
    // 根据角色获取有效权限
    const effectivePermissions = knowledgeAuthService.getEffectivePermissions(permissions);
    
    return responseHandler.success(res, { 
      permissions: knowledgePermissions,
      effectivePermissions 
    });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 检查对特定资源的访问权限
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const checkAccess = async (req, res) => {
  try {
    const userId = req.user.id;
    const { resourceType, resourceId, action } = req.body;
    
    // 验证请求参数
    if (!resourceType || !resourceId || !action) {
      return res.status(400).json({
        success: false,
        message: '缺少必需参数',
        code: 'validation/missing-params'
      });
    }
    
    const hasAccess = await knowledgeAuthService.checkAccess(
      userId,
      resourceType,
      resourceId,
      action
    );
    
    return responseHandler.success(res, { hasAccess });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 批量检查对多个资源的访问权限
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const batchCheckAccess = async (req, res) => {
  try {
    const userId = req.user.id;
    const { resources } = req.body;
    
    // 验证请求参数
    if (!Array.isArray(resources) || resources.length === 0) {
      return res.status(400).json({
        success: false,
        message: '资源列表必须是非空数组',
        code: 'validation/invalid-resources'
      });
    }
    
    // 验证每个资源对象
    for (const resource of resources) {
      if (!resource.resourceType || !resource.resourceId || !resource.action) {
        return res.status(400).json({
          success: false,
          message: '资源对象缺少必需字段',
          code: 'validation/invalid-resource'
        });
      }
    }
    
    // 批量检查权限
    const accessResults = await knowledgeAuthService.batchCheckAccess(userId, resources);
    
    // 转换为客户端友好的格式
    const results = [];
    resources.forEach(resource => {
      const { resourceType, resourceId, action } = resource;
      const key = `${resourceType}:${resourceId}:${action}`;
      const hasAccess = accessResults.get(key) || false;
      
      results.push({
        resourceType,
        resourceId,
        action,
        hasAccess
      });
    });
    
    return responseHandler.success(res, { results });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 获取指定用户的知识库权限
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getUserPermissions = async (req, res) => {
  try {
    const userId = parseInt(req.params.userId, 10);
    
    if (isNaN(userId)) {
      return res.status(400).json({
        success: false,
        message: '无效的用户ID',
        code: 'validation/invalid-user-id'
      });
    }
    
    const permissions = await knowledgeAuthService.getUserPermissions(userId);
    
    // 过滤出与知识库相关的权限
    const knowledgePermissions = permissions.filter(permission => {
      return permission.includes('knowledge:') || 
             permission.includes('graph:') || 
             permission.includes('sensitive:') ||
             permission.includes(':read') ||
             permission.includes(':write');
    });
    
    // 根据角色获取有效权限
    const effectivePermissions = knowledgeAuthService.getEffectivePermissions(permissions);
    
    return responseHandler.success(res, { 
      permissions: knowledgePermissions,
      effectivePermissions
    });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 分配知识库权限给用户
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const assignPermissions = async (req, res) => {
  try {
    const userId = parseInt(req.params.userId, 10);
    const { permissions } = req.body;
    
    if (isNaN(userId)) {
      return res.status(400).json({
        success: false,
        message: '无效的用户ID',
        code: 'validation/invalid-user-id'
      });
    }
    
    if (!Array.isArray(permissions) || permissions.length === 0) {
      return res.status(400).json({
        success: false,
        message: '权限必须是非空数组',
        code: 'validation/invalid-permissions'
      });
    }
    
    // 验证权限格式
    const validPermissionPattern = /^[a-z_]+:[a-z_]+$/;
    const allPermissionsValid = permissions.every(permission => 
      validPermissionPattern.test(permission)
    );
    
    if (!allPermissionsValid) {
      return res.status(400).json({
        success: false,
        message: '权限格式无效，应为"资源:操作"格式',
        code: 'validation/invalid-permission-format'
      });
    }
    
    await knowledgeAuthService.assignPermissions(userId, permissions);
    
    // 记录操作
    logger.info(`管理员 ${req.user.id} 为用户 ${userId} 分配知识库权限: ${permissions.join(', ')}`);
    
    return responseHandler.success(res, { 
      message: '权限分配成功',
      userId,
      permissions
    });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 撤销用户的知识库权限
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const revokePermissions = async (req, res) => {
  try {
    const userId = parseInt(req.params.userId, 10);
    const { permissions } = req.body;
    
    if (isNaN(userId)) {
      return res.status(400).json({
        success: false,
        message: '无效的用户ID',
        code: 'validation/invalid-user-id'
      });
    }
    
    if (!Array.isArray(permissions) || permissions.length === 0) {
      return res.status(400).json({
        success: false,
        message: '权限必须是非空数组',
        code: 'validation/invalid-permissions'
      });
    }
    
    await knowledgeAuthService.revokePermissions(userId, permissions);
    
    // 记录操作
    logger.info(`管理员 ${req.user.id} 撤销用户 ${userId} 的知识库权限: ${permissions.join(', ')}`);
    
    return responseHandler.success(res, { 
      message: '权限撤销成功',
      userId,
      permissions
    });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 记录知识资源访问日志
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const logAccess = async (req, res) => {
  try {
    const userId = req.user.id;
    const { resourceType, resourceId, action } = req.body;
    
    // 验证请求参数
    if (!resourceType || !resourceId || !action) {
      return res.status(400).json({
        success: false,
        message: '缺少必需参数',
        code: 'validation/missing-params'
      });
    }
    
    // 获取请求元数据
    const metadata = {
      ip_address: req.ip,
      user_agent: req.headers['user-agent'],
      referrer: req.headers.referer || req.headers.referrer || '',
      service: req.headers['x-service-name'] || 'unknown'
    };
    
    await knowledgeAuthService.logAccess(
      userId,
      resourceType,
      resourceId,
      action,
      metadata
    );
    
    return responseHandler.success(res, { message: '访问日志记录成功' });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 获取知识资源访问日志
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getAccessLogs = async (req, res) => {
  try {
    const {
      userId,
      resourceType,
      resourceId,
      startDate,
      endDate,
      page = 1,
      limit = 20
    } = req.query;
    
    const offset = (page - 1) * limit;
    
    // 构建查询
    let query = knexClient('knowledge_access_logs')
      .select([
        'id',
        'user_id',
        'resource_type',
        'resource_id',
        'action',
        'ip_address',
        'user_agent',
        'accessed_at'
      ])
      .orderBy('accessed_at', 'desc')
      .limit(limit)
      .offset(offset);
    
    // 根据筛选条件添加where子句
    if (userId) {
      query = query.where('user_id', userId);
    }
    
    if (resourceType) {
      query = query.where('resource_type', resourceType);
    }
    
    if (resourceId) {
      query = query.where('resource_id', resourceId);
    }
    
    if (startDate) {
      query = query.where('accessed_at', '>=', new Date(startDate));
    }
    
    if (endDate) {
      query = query.where('accessed_at', '<=', new Date(endDate));
    }
    
    // 执行查询
    const logs = await query;
    
    // 查询总记录数
    let countQuery = knexClient('knowledge_access_logs').count('id as total');
    
    // 应用相同的筛选条件
    if (userId) {
      countQuery = countQuery.where('user_id', userId);
    }
    
    if (resourceType) {
      countQuery = countQuery.where('resource_type', resourceType);
    }
    
    if (resourceId) {
      countQuery = countQuery.where('resource_id', resourceId);
    }
    
    if (startDate) {
      countQuery = countQuery.where('accessed_at', '>=', new Date(startDate));
    }
    
    if (endDate) {
      countQuery = countQuery.where('accessed_at', '<=', new Date(endDate));
    }
    
    const [{ total }] = await countQuery;
    
    return responseHandler.success(res, {
      logs,
      pagination: {
        page: parseInt(page, 10),
        limit: parseInt(limit, 10),
        total: parseInt(total, 10),
        totalPages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

module.exports = {
  getCurrentUserPermissions,
  checkAccess,
  batchCheckAccess,
  getUserPermissions,
  assignPermissions,
  revokePermissions,
  logAccess,
  getAccessLogs
};