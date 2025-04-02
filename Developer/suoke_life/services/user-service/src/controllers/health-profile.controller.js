/**
 * 健康资料控制器
 */
const { healthProfileService } = require('../services');
const { ApiResponse } = require('@suoke/shared').responses;
const { logger } = require('@suoke/shared').utils;

/**
 * 获取用户健康资料
 */
exports.getHealthProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await healthProfileService.getHealthProfile(userId);
    return ApiResponse.success(res, result, '获取健康资料成功');
  } catch (error) {
    logger.error('获取健康资料失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 创建用户健康资料
 */
exports.createHealthProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await healthProfileService.createHealthProfile(userId, req.body);
    return ApiResponse.success(res, result, '创建健康资料成功');
  } catch (error) {
    logger.error('创建健康资料失败', { error: error.message, userId: req.user.id, body: req.body });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 更新用户健康资料
 */
exports.updateHealthProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await healthProfileService.updateHealthProfile(userId, req.body);
    return ApiResponse.success(res, result, '更新健康资料成功');
  } catch (error) {
    logger.error('更新健康资料失败', { error: error.message, userId: req.user.id, body: req.body });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 删除用户健康资料
 */
exports.deleteHealthProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await healthProfileService.deleteHealthProfile(userId);
    return ApiResponse.success(res, result, '删除健康资料成功');
  } catch (error) {
    logger.error('删除健康资料失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 更新最后检查时间
 */
exports.updateLastCheckup = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await healthProfileService.updateLastCheckup(userId);
    return ApiResponse.success(res, result, '更新最后检查时间成功');
  } catch (error) {
    logger.error('更新最后检查时间失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 更新体质类型
 */
exports.updateConstitutionType = async (req, res) => {
  try {
    const userId = req.user.id;
    const { constitutionType } = req.body;
    const result = await healthProfileService.updateConstitutionType(userId, constitutionType);
    return ApiResponse.success(res, result, '更新体质类型成功');
  } catch (error) {
    logger.error('更新体质类型失败', { error: error.message, userId: req.user.id, constitutionType: req.body.constitutionType });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 获取健康建议
 */
exports.getHealthRecommendations = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await healthProfileService.getHealthRecommendations(userId);
    return ApiResponse.success(res, result, '获取健康建议成功');
  } catch (error) {
    logger.error('获取健康建议失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 获取按体质类型分组的用户数量 (仅管理员)
 */
exports.getConstitutionTypeCounts = async (req, res) => {
  try {
    // 检查是否有管理员权限
    if (req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '没有权限访问');
    }

    const result = await healthProfileService.getConstitutionTypeCounts();
    return ApiResponse.success(res, result, '获取体质类型统计成功');
  } catch (error) {
    logger.error('获取体质类型统计失败', { error: error.message });
    return ApiResponse.error(res, error.message);
  }
}; 