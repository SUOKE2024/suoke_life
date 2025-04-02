/**
 * 知识偏好控制器
 * 处理用户知识偏好相关请求
 */
const { knowledgePreferenceService } = require('../services');
const { ApiResponse } = require('@suoke/shared').responses;
const { logger } = require('@suoke/shared').utils;

/**
 * 获取用户知识偏好
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const getUserKnowledgePreferences = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以访问
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权访问此资源');
    }
    
    const preferences = await knowledgePreferenceService.getUserKnowledgePreferences(userId);
    
    return ApiResponse.success(res, preferences, '获取用户知识偏好成功');
  } catch (error) {
    logger.error(`获取用户知识偏好失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

/**
 * 更新用户知识偏好
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const updateUserKnowledgePreferences = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以更新
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权更新此资源');
    }
    
    const preferences = await knowledgePreferenceService.updateUserKnowledgePreferences(userId, req.body);
    
    return ApiResponse.success(res, preferences, '更新用户知识偏好成功');
  } catch (error) {
    logger.error(`更新用户知识偏好失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

/**
 * 获取用户感兴趣的知识领域
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const getUserInterestedDomains = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以访问
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权访问此资源');
    }
    
    const domains = await knowledgePreferenceService.getUserInterestedDomains(userId);
    
    return ApiResponse.success(res, { domains }, '获取用户感兴趣的知识领域成功');
  } catch (error) {
    logger.error(`获取用户感兴趣的知识领域失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

/**
 * 获取用户知识内容访问历史
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const getUserViewHistory = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以访问
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权访问此资源');
    }
    
    const { limit, page, domain } = req.query;
    
    const history = await knowledgePreferenceService.getUserViewHistory(userId, {
      limit: parseInt(limit) || 10,
      page: parseInt(page) || 1,
      domain
    });
    
    return ApiResponse.success(res, { history }, '获取用户知识内容访问历史成功');
  } catch (error) {
    logger.error(`获取用户知识内容访问历史失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

/**
 * 记录用户知识内容访问
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const recordContentView = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const contentData = req.body;
    
    await knowledgePreferenceService.recordContentView(userId, contentData);
    
    return ApiResponse.success(res, null, '记录用户知识内容访问成功');
  } catch (error) {
    logger.error(`记录用户知识内容访问失败: ${error.message}`, { userId: req.user.id, contentData: req.body, error });
    return next(error);
  }
};

/**
 * 获取推荐给用户的知识内容
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const getRecommendedContent = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以访问
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权访问此资源');
    }
    
    const { limit, domains } = req.query;
    
    const content = await knowledgePreferenceService.getRecommendedContent(userId, {
      limit: parseInt(limit) || 10,
      domains: domains ? domains.split(',') : []
    });
    
    return ApiResponse.success(res, { content }, '获取推荐知识内容成功');
  } catch (error) {
    logger.error(`获取推荐知识内容失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

/**
 * 获取用户收藏的知识内容
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const getUserFavorites = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以访问
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权访问此资源');
    }
    
    const { limit, page, domain } = req.query;
    
    const favorites = await knowledgePreferenceService.getUserFavorites(userId, {
      limit: parseInt(limit) || 10,
      page: parseInt(page) || 1,
      domain
    });
    
    return ApiResponse.success(res, { favorites }, '获取用户收藏知识内容成功');
  } catch (error) {
    logger.error(`获取用户收藏知识内容失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

/**
 * 添加知识内容到用户收藏
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const addToFavorites = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const contentData = req.body;
    
    const favorite = await knowledgePreferenceService.addToFavorites(userId, contentData);
    
    return ApiResponse.success(res, { favorite }, '添加知识内容到收藏成功');
  } catch (error) {
    logger.error(`添加知识内容到收藏失败: ${error.message}`, { userId: req.user.id, contentData: req.body, error });
    return next(error);
  }
};

/**
 * 从用户收藏中移除知识内容
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const removeFromFavorites = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { contentId } = req.params;
    
    await knowledgePreferenceService.removeFromFavorites(userId, contentId);
    
    return ApiResponse.success(res, null, '从收藏中移除知识内容成功');
  } catch (error) {
    logger.error(`从收藏中移除知识内容失败: ${error.message}`, { userId: req.user.id, contentId: req.params.contentId, error });
    return next(error);
  }
};

/**
 * 获取用户知识图谱交互历史
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @param {Function} next 下一个中间件
 */
const getKnowledgeGraphInteractions = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // 检查权限，只有用户自己或管理员可以访问
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '您无权访问此资源');
    }
    
    const { limit, page } = req.query;
    
    const interactions = await knowledgePreferenceService.getKnowledgeGraphInteractions(userId, {
      limit: parseInt(limit) || 10,
      page: parseInt(page) || 1
    });
    
    return ApiResponse.success(res, { interactions }, '获取用户知识图谱交互历史成功');
  } catch (error) {
    logger.error(`获取用户知识图谱交互历史失败: ${error.message}`, { userId: req.params.userId, error });
    return next(error);
  }
};

module.exports = {
  getUserKnowledgePreferences,
  updateUserKnowledgePreferences,
  getUserInterestedDomains,
  getUserViewHistory,
  recordContentView,
  getRecommendedContent,
  getUserFavorites,
  addToFavorites,
  removeFromFavorites,
  getKnowledgeGraphInteractions
};