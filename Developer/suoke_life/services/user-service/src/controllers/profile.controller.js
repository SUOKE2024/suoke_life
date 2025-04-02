/**
 * 个人资料控制器
 */
const { profileService } = require('../services');
const { ApiResponse } = require('@suoke/shared').responses;
const { logger } = require('@suoke/shared').utils;

/**
 * 获取用户个人资料
 */
exports.getProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await profileService.getProfile(userId);
    return ApiResponse.success(res, result, '获取个人资料成功');
  } catch (error) {
    logger.error('获取个人资料失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 创建用户个人资料
 */
exports.createProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await profileService.createProfile(userId, req.body);
    return ApiResponse.success(res, result, '创建个人资料成功');
  } catch (error) {
    logger.error('创建个人资料失败', { error: error.message, userId: req.user.id, body: req.body });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 更新用户个人资料
 */
exports.updateProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await profileService.updateProfile(userId, req.body);
    return ApiResponse.success(res, result, '更新个人资料成功');
  } catch (error) {
    logger.error('更新个人资料失败', { error: error.message, userId: req.user.id, body: req.body });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 删除用户个人资料
 */
exports.deleteProfile = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await profileService.deleteProfile(userId);
    return ApiResponse.success(res, result, '删除个人资料成功');
  } catch (error) {
    logger.error('删除个人资料失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 获取用户头像
 */
exports.getAvatar = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await profileService.getAvatar(userId);
    return ApiResponse.success(res, result, '获取用户头像成功');
  } catch (error) {
    logger.error('获取用户头像失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 更新用户头像
 */
exports.updateAvatar = async (req, res) => {
  try {
    const userId = req.user.id;
    const avatarUrl = req.body.avatarUrl;
    const result = await profileService.updateAvatar(userId, avatarUrl);
    return ApiResponse.success(res, result, '更新用户头像成功');
  } catch (error) {
    logger.error('更新用户头像失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 检查昵称可用性
 */
exports.checkNicknameAvailability = async (req, res) => {
  try {
    const { nickname } = req.query;
    const result = await profileService.checkNicknameAvailability(nickname);
    return ApiResponse.success(res, result, '检查昵称可用性成功');
  } catch (error) {
    logger.error('检查昵称可用性失败', { error: error.message, nickname: req.query.nickname });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 搜索个人资料
 */
exports.searchProfiles = async (req, res) => {
  try {
    // 检查是否有管理员权限
    if (req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '没有权限访问');
    }

    const { query, page = 1, pageSize = 10 } = req.query;
    const result = await profileService.searchProfiles(query, Number(page), Number(pageSize));
    return ApiResponse.success(res, result, '搜索个人资料成功');
  } catch (error) {
    logger.error('搜索个人资料失败', { error: error.message, query: req.query });
    return ApiResponse.error(res, error.message);
  }
}; 