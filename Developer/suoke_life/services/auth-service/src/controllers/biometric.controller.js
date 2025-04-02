/**
 * 生物识别认证控制器
 */
const BiometricService = require('../services/biometric.service');
const { validationResult } = require('express-validator');
const logger = require('../utils/logger');
const { ValidationError } = require('../utils/errors');

// 创建生物识别服务实例
const biometricService = new BiometricService();

/**
 * 注册生物识别凭据
 * @param {Request} req - Express请求对象
 * @param {Response} res - Express响应对象
 * @param {NextFunction} next - Express下一个中间件函数
 */
exports.register = async (req, res, next) => {
  try {
    // 验证请求
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: '请求验证失败',
        errors: errors.array(),
        code: 'validation/invalid-input'
      });
    }

    const { userId, deviceId, biometricType, publicKey, deviceInfo, attestation } = req.body;
    
    // 检查用户权限
    if (req.user.id !== userId && !req.user.isAdmin) {
      return res.status(403).json({
        success: false,
        message: '没有权限为其他用户注册生物识别凭据',
        code: 'auth/forbidden'
      });
    }
    
    // 调用服务注册生物识别凭据
    const result = await biometricService.register({
      userId,
      deviceId,
      biometricType,
      publicKey,
      deviceInfo,
      attestation
    });
    
    // 记录活动日志
    logger.info(`用户 ${userId} 注册了生物识别凭据 (类型: ${biometricType}, 设备: ${deviceId})`, {
      action: 'biometric_register',
      userId,
      deviceId,
      biometricType,
      isNewRegistration: result.isNewRegistration
    });
    
    return res.status(201).json({
      success: true,
      message: result.isNewRegistration ? '生物识别凭据注册成功' : '生物识别凭据更新成功',
      data: result
    });
    
  } catch (error) {
    logger.error(`生物识别凭据注册失败: ${error.message}`, { error });
    next(error);
  }
};

/**
 * 生成生物识别挑战值
 * @param {Request} req - Express请求对象
 * @param {Response} res - Express响应对象
 * @param {NextFunction} next - Express下一个中间件函数
 */
exports.generateChallenge = async (req, res, next) => {
  try {
    // 验证请求
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: '请求验证失败',
        errors: errors.array(),
        code: 'validation/invalid-input'
      });
    }

    const { userId, deviceId } = req.body;
    
    // 检查用户权限
    if (req.user.id !== userId && !req.user.isAdmin) {
      return res.status(403).json({
        success: false,
        message: '没有权限为其他用户生成挑战值',
        code: 'auth/forbidden'
      });
    }
    
    // 调用服务生成挑战值
    const result = await biometricService.generateChallenge({
      userId,
      deviceId
    });
    
    return res.status(200).json({
      success: true,
      message: '生物识别挑战值生成成功',
      data: result
    });
    
  } catch (error) {
    logger.error(`生物识别挑战值生成失败: ${error.message}`, { error });
    next(error);
  }
};

/**
 * 验证生物识别凭据
 * @param {Request} req - Express请求对象
 * @param {Response} res - Express响应对象
 * @param {NextFunction} next - Express下一个中间件函数
 */
exports.verify = async (req, res, next) => {
  try {
    // 验证请求
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: '请求验证失败',
        errors: errors.array(),
        code: 'validation/invalid-input'
      });
    }

    const { userId, deviceId, biometricType, signature, challenge } = req.body;
    
    // 验证生物识别凭据
    const result = await biometricService.verify({
      userId,
      deviceId,
      biometricType,
      signature,
      challenge
    });
    
    // 记录活动日志
    logger.info(`用户 ${userId} 使用生物识别凭据验证成功 (类型: ${biometricType}, 设备: ${deviceId})`, {
      action: 'biometric_verify',
      userId,
      deviceId,
      biometricType
    });
    
    return res.status(200).json({
      success: true,
      message: '生物识别验证成功',
      data: result
    });
    
  } catch (error) {
    // 特殊处理验证错误
    if (error instanceof ValidationError) {
      logger.warn(`生物识别验证失败: ${error.message}`, {
        error: error.message
      });
      
      return res.status(400).json({
        success: false,
        message: error.message,
        code: 'auth/biometric-verification-failed'
      });
    }
    
    logger.error(`生物识别验证失败: ${error.message}`, { error });
    next(error);
  }
};

/**
 * 获取用户的生物识别凭据列表
 * @param {Request} req - Express请求对象
 * @param {Response} res - Express响应对象
 * @param {NextFunction} next - Express下一个中间件函数
 */
exports.getCredentials = async (req, res, next) => {
  try {
    const { userId } = req.query;
    
    // 检查用户权限
    if (req.user.id !== userId && !req.user.isAdmin) {
      return res.status(403).json({
        success: false,
        message: '没有权限查看其他用户的生物识别凭据',
        code: 'auth/forbidden'
      });
    }
    
    // 调用服务获取凭据列表
    const credentials = await biometricService.getCredentials(userId);
    
    return res.status(200).json({
      success: true,
      message: '获取生物识别凭据列表成功',
      data: credentials
    });
    
  } catch (error) {
    logger.error(`获取生物识别凭据列表失败: ${error.message}`, { error });
    next(error);
  }
};

/**
 * 删除生物识别凭据
 * @param {Request} req - Express请求对象
 * @param {Response} res - Express响应对象
 * @param {NextFunction} next - Express下一个中间件函数
 */
exports.deleteCredential = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { userId } = req.body;
    
    // 检查用户权限
    if (req.user.id !== userId && !req.user.isAdmin) {
      return res.status(403).json({
        success: false,
        message: '没有权限删除其他用户的生物识别凭据',
        code: 'auth/forbidden'
      });
    }
    
    // 调用服务删除凭据
    const result = await biometricService.deleteCredential(id, userId);
    
    if (!result) {
      return res.status(404).json({
        success: false,
        message: '生物识别凭据不存在',
        code: 'auth/credential-not-found'
      });
    }
    
    // 记录活动日志
    logger.info(`用户 ${userId} 删除了生物识别凭据 (ID: ${id})`, {
      action: 'biometric_delete',
      userId,
      credentialId: id
    });
    
    return res.status(200).json({
      success: true,
      message: '生物识别凭据删除成功'
    });
    
  } catch (error) {
    logger.error(`删除生物识别凭据失败: ${error.message}`, { error });
    next(error);
  }
};

/**
 * 更新生物识别凭据
 * @param {Request} req - Express请求对象
 * @param {Response} res - Express响应对象
 * @param {NextFunction} next - Express下一个中间件函数
 */
exports.updateCredential = async (req, res, next) => {
  try {
    // 验证请求
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: '请求验证失败',
        errors: errors.array(),
        code: 'validation/invalid-input'
      });
    }

    const { id } = req.params;
    const { userId, name } = req.body;
    
    // 检查用户权限
    if (req.user.id !== userId && !req.user.isAdmin) {
      return res.status(403).json({
        success: false,
        message: '没有权限更新其他用户的生物识别凭据',
        code: 'auth/forbidden'
      });
    }
    
    // 调用服务更新凭据
    const result = await biometricService.updateCredential(id, userId, { name });
    
    if (!result) {
      return res.status(404).json({
        success: false,
        message: '生物识别凭据不存在',
        code: 'auth/credential-not-found'
      });
    }
    
    // 记录活动日志
    logger.info(`用户 ${userId} 更新了生物识别凭据 (ID: ${id})`, {
      action: 'biometric_update',
      userId,
      credentialId: id
    });
    
    return res.status(200).json({
      success: true,
      message: '生物识别凭据更新成功',
      data: result
    });
    
  } catch (error) {
    logger.error(`更新生物识别凭据失败: ${error.message}`, { error });
    next(error);
  }
}; 