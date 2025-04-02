/**
 * 用户控制器
 */
const { userService, profileService, healthProfileService } = require('../services');
const { ApiResponse } = require('@suoke/shared').responses;
const { logger } = require('@suoke/shared').utils;
const jwt = require('jsonwebtoken');
const config = require('../config');
const { redisClient } = require('../utils/redis');
const { validateRequest } = require('../middlewares/validation.middleware');
const { userSchemas } = require('../schemas');

/**
 * 用户注册
 */
const register = async (req, res, next) => {
  try {
    const user = await userService.register(req.body);
    ApiResponse.success(res, '注册成功,请查收验证邮件', { userId: user.id });
  } catch (error) {
    next(error);
  }
};

/**
 * 用户登录
 */
const login = async (req, res, next) => {
  try {
    const { user, session, tokens } = await userService.login({
      ...req.body,
      deviceInfo: req.headers['user-agent'],
      ipAddress: req.ip
    });

    // 移除敏感信息
    const { password, mfa_secret, mfa_backup_codes, ...userWithoutSensitiveData } = user;

    ApiResponse.success(res, '登录成功', {
      user: userWithoutSensitiveData,
      session,
      tokens
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 用户登出
 */
const logout = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return ApiResponse.error(res, '未提供认证令牌');
    }

    const decoded = jwt.decode(token);
    await userService.logout(req.user.id, decoded.sessionId);
    ApiResponse.success(res, '登出成功');
  } catch (error) {
    next(error);
  }
};

/**
 * 刷新访问令牌
 */
const refreshToken = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    if (!refreshToken) {
      return ApiResponse.error(res, '未提供刷新令牌');
    }

    const decoded = jwt.verify(refreshToken, config.jwt.refreshSecret);
    const user = await userService.getUserById(decoded.userId);
    const tokens = await userService.generateTokens(user, decoded.sessionId);

    ApiResponse.success(res, '令牌刷新成功', { tokens });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取当前用户信息
 */
const getCurrentUser = async (req, res, next) => {
  try {
    const user = await userService.getUserById(req.user.id);
    const { password, mfa_secret, mfa_backup_codes, ...userWithoutSensitiveData } = user;
    ApiResponse.success(res, '获取用户信息成功', { user: userWithoutSensitiveData });
  } catch (error) {
    next(error);
  }
};

/**
 * 启用多因素认证
 */
exports.enableMFA = async (req, res) => {
  try {
    const { user } = req;
    const result = await userService.enableMFA(user.id);
    return ApiResponse.success(res, result, '多因素认证已启用');
  } catch (error) {
    logger.error('启用多因素认证失败', { error: error.message, userId: req.user?.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 禁用多因素认证
 */
exports.disableMFA = async (req, res) => {
  try {
    const { user } = req;
    await userService.disableMFA(user.id);
    return ApiResponse.success(res, null, '多因素认证已禁用');
  } catch (error) {
    logger.error('禁用多因素认证失败', { error: error.message, userId: req.user?.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 获取用户会话列表
 */
const getUserSessions = async (req, res, next) => {
  try {
    const sessions = await userService.getUserSessions(req.user.id, req.query);
    ApiResponse.success(res, '获取会话列表成功', { sessions });
  } catch (error) {
    next(error);
  }
};

/**
 * 终止指定会话
 */
const terminateSession = async (req, res, next) => {
  try {
    await userService.terminateSession(req.user.id, req.params.sessionId);
    ApiResponse.success(res, '终止会话成功');
  } catch (error) {
    next(error);
  }
};

/**
 * 终止所有会话
 */
const terminateAllSessions = async (req, res, next) => {
  try {
    await userService.terminateAllSessions(req.user.id);
    ApiResponse.success(res, '终止所有会话成功');
  } catch (error) {
    next(error);
  }
};

/**
 * 请求密码重置
 */
exports.requestPasswordReset = async (req, res) => {
  try {
    const { email } = req.body;
    await userService.requestPasswordReset(email);
    
    // 出于安全考虑，不管用户是否存在都返回相同的消息
    return ApiResponse.success(res, null, '如果该邮箱存在，重置密码的邮件已发送');
  } catch (error) {
    logger.error('请求密码重置失败', { error: error.message, email: req.body.email });
    // 出于安全考虑，不返回具体错误信息
    return ApiResponse.success(res, null, '如果该邮箱存在，重置密码的邮件已发送');
  }
};

/**
 * 重置密码
 */
exports.resetPassword = async (req, res) => {
  try {
    const { token, password } = req.body;
    await userService.resetPassword(token, password);
    
    return ApiResponse.success(res, null, '密码重置成功，请使用新密码登录');
  } catch (error) {
    logger.error('重置密码失败', { error: error.message });
    return ApiResponse.error(res, '重置密码失败，令牌可能已过期或无效');
  }
};

/**
 * 修改密码
 */
exports.changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    const { user } = req;
    
    await userService.changePassword(user.id, currentPassword, newPassword);
    
    // 修改密码后，撤销当前令牌
    await redisClient.set(
      `revoked_token:${req.token}`, 
      '1', 
      'EX', 
      config.jwt.expiresIn
    );
    
    return ApiResponse.success(res, null, '密码修改成功，请重新登录');
  } catch (error) {
    logger.error('修改密码失败', { error: error.message, userId: req.user?.id });
    return ApiResponse.error(res, error.message || '修改密码失败，请重试');
  }
};

/**
 * 删除账号
 */
exports.deleteAccount = async (req, res) => {
  try {
    const { id } = req.params;
    const { user } = req;
    
    // 检查是否是删除自己的账号
    if (id !== user.id) {
      return ApiResponse.forbidden(res, '您只能删除自己的账号');
    }
    
    await userService.deleteAccount(id);
    
    // 撤销当前令牌
    await redisClient.set(
      `revoked_token:${req.token}`, 
      '1', 
      'EX', 
      config.jwt.expiresIn
    );
    
    return ApiResponse.success(res, null, '账号已成功删除');
  } catch (error) {
    logger.error('删除账号失败', { error: error.message, userId: req.params.id });
    return ApiResponse.error(res, '删除账号失败，请重试');
  }
};

/**
 * 验证邮箱
 */
exports.verifyEmail = async (req, res) => {
  try {
    const { token } = req.body;
    await userService.verifyEmail(token);
    
    return ApiResponse.success(res, null, '邮箱验证成功');
  } catch (error) {
    logger.error('邮箱验证失败', { error: error.message });
    return ApiResponse.error(res, error.message || '邮箱验证失败，令牌可能已过期或无效');
  }
};

/**
 * 验证手机号
 */
exports.verifyPhone = async (req, res) => {
  try {
    const { phone, code } = req.body;
    await userService.verifyPhone(phone, code);
    
    return ApiResponse.success(res, null, '手机号验证成功');
  } catch (error) {
    logger.error('手机号验证失败', { error: error.message, phone: req.body.phone });
    return ApiResponse.error(res, error.message || '手机号验证失败，验证码可能已过期或无效');
  }
};

/**
 * 重新发送验证码
 */
exports.resendVerification = async (req, res) => {
  try {
    const { type } = req.body; // 'email' 或 'phone'
    const { user } = req;
    
    if (type === 'email') {
      await userService.sendEmailVerification(user.id);
      return ApiResponse.success(res, null, '验证邮件已发送');
    } else if (type === 'phone') {
      await userService.sendPhoneVerification(user.id);
      return ApiResponse.success(res, null, '验证短信已发送');
    } else {
      return ApiResponse.badRequest(res, '无效的验证类型');
    }
  } catch (error) {
    logger.error('重新发送验证码失败', { error: error.message, userId: req.user?.id, type: req.body.type });
    return ApiResponse.error(res, error.message || '发送验证码失败，请重试');
  }
};

/**
 * 获取用户信息（管理员接口）
 */
exports.getUserById = async (req, res) => {
  try {
    const { id } = req.params;
    
    const user = await userService.findById(id);
    if (!user) {
      return ApiResponse.notFound(res, '用户不存在');
    }
    
    const userProfile = await profileService.getProfileByUserId(id);
    const healthProfile = await healthProfileService.getHealthProfileByUserId(id);
    
    const userData = {
      ...user,
      profile: userProfile,
      healthProfile: healthProfile
    };
    
    // 敏感信息不返回
    delete userData.password;
    delete userData.resetToken;
    delete userData.resetTokenExpiry;
    
    return ApiResponse.success(res, userData, '获取用户信息成功');
  } catch (error) {
    logger.error('获取用户信息失败', { error: error.message, userId: req.params.id });
    return ApiResponse.error(res, '获取用户信息失败，请重试');
  }
};

/**
 * 用户验证
 */
exports.verify = async (req, res) => {
  try {
    const { token } = req.params;
    const result = await userService.verifyUser(token);
    return ApiResponse.success(res, result, '用户验证成功');
  } catch (error) {
    logger.error('用户验证失败', { error: error.message, token: req.params.token });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 发送验证码
 */
exports.sendVerificationCode = async (req, res) => {
  try {
    const { type, contact } = req.body;
    const result = await userService.sendVerificationCode(type, contact);
    return ApiResponse.success(res, result, '验证码发送成功');
  } catch (error) {
    logger.error('发送验证码失败', { error: error.message, body: req.body });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 验证验证码
 */
exports.verifyCode = async (req, res) => {
  try {
    const { token, code } = req.body;
    const result = await userService.verifyCode(token, code);
    return ApiResponse.success(res, result, '验证码验证成功');
  } catch (error) {
    logger.error('验证码验证失败', { error: error.message, token: req.body.token });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 获取用户信息
 */
exports.getUserInfo = async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await userService.getUserInfo(userId);
    return ApiResponse.success(res, result, '获取用户信息成功');
  } catch (error) {
    logger.error('获取用户信息失败', { error: error.message, userId: req.user.id });
    return ApiResponse.error(res, error.message);
  }
};

/**
 * 更新用户信息
 */
const updateUser = async (req, res, next) => {
  try {
    const user = await userService.updateUser(req.user.id, req.body);
    const { password, mfa_secret, mfa_backup_codes, ...userWithoutSensitiveData } = user;
    ApiResponse.success(res, '更新用户信息成功', { user: userWithoutSensitiveData });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取用户列表 (仅管理员)
 */
exports.listUsers = async (req, res) => {
  try {
    // 检查是否有管理员权限
    if (req.user.role !== 'admin') {
      return ApiResponse.forbidden(res, '没有权限访问');
    }

    const { page = 1, pageSize = 10, ...filters } = req.query;
    const result = await userService.listUsers(Number(page), Number(pageSize), filters);
    return ApiResponse.success(res, result, '获取用户列表成功');
  } catch (error) {
    logger.error('获取用户列表失败', { error: error.message, query: req.query });
    return ApiResponse.error(res, error.message);
  }
};

module.exports = {
  register: [validateRequest(userSchemas.register), register],
  login: [validateRequest(userSchemas.login), login],
  logout: [verifyToken, logout],
  refreshToken: [validateRequest(userSchemas.refreshToken), refreshToken],
  getCurrentUser: [verifyToken, getCurrentUser],
  updateUser: [verifyToken, validateRequest(userSchemas.updateUser), updateUser],
  getUserSessions: [verifyToken, getUserSessions],
  terminateSession: [verifyToken, terminateSession],
  terminateAllSessions: [verifyToken, terminateAllSessions],
  deleteAccount: [verifyToken, deleteAccount],
  verifyEmail: [verifyToken, verifyEmail],
  verifyPhone: [verifyToken, verifyPhone],
  resendVerification: [verifyToken, resendVerification],
  getUserById: [verifyToken, getUserById],
  verify: [verifyToken, verify],
  sendVerificationCode: [verifyToken, sendVerificationCode],
  verifyCode: [verifyToken, verifyCode],
  getUserInfo: [verifyToken, getUserInfo],
  listUsers: [verifyToken, listUsers]
}; 