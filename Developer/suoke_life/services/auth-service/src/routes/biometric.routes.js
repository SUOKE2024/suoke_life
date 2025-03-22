/**
 * 生物识别认证路由
 */
const express = require('express');
const router = express.Router();
const { body, param, query } = require('express-validator');
const biometricService = require('../services/biometric.service');
const { validateRequest, authenticate } = require('../middlewares');
const logger = require('../utils/logger');

/**
 * @route POST /api/auth/biometric/register
 * @desc 注册生物识别凭据
 * @access 需要认证
 */
router.post(
  '/register',
  authenticate,
  [
    body('deviceId').notEmpty().withMessage('设备ID不能为空'),
    body('biometricType').notEmpty().withMessage('生物识别类型不能为空')
      .isIn(['fingerprint', 'faceId', 'voiceRecognition']).withMessage('不支持的生物识别类型'),
    body('publicKey').notEmpty().withMessage('公钥不能为空'),
    body('deviceInfo').isObject().withMessage('设备信息必须是一个对象')
  ],
  validateRequest,
  async (req, res) => {
    try {
      const { deviceId, biometricType, publicKey, deviceInfo, attestation } = req.body;
      
      // 使用当前已认证用户的ID
      const userId = req.user.id;
      
      const result = await biometricService.register({
        userId,
        deviceId,
        biometricType,
        publicKey,
        deviceInfo,
        attestation
      });
      
      res.status(201).json({
        success: true,
        message: result.isNewRegistration ? '生物识别凭据注册成功' : '生物识别凭据更新成功',
        data: result
      });
    } catch (error) {
      logger.error(`生物识别凭据注册失败: ${error.message}`, { error });
      
      res.status(error.status || 500).json({
        success: false,
        message: error.message || '生物识别凭据注册失败',
        errors: error.errors || null
      });
    }
  }
);

/**
 * @route POST /api/auth/biometric/verify
 * @desc 验证生物识别凭据
 * @access 公开
 */
router.post(
  '/verify',
  [
    body('userId').notEmpty().withMessage('用户ID不能为空'),
    body('deviceId').notEmpty().withMessage('设备ID不能为空'),
    body('biometricType').notEmpty().withMessage('生物识别类型不能为空')
      .isIn(['fingerprint', 'faceId', 'voiceRecognition']).withMessage('不支持的生物识别类型'),
    body('signature').notEmpty().withMessage('签名不能为空'),
    body('challenge').notEmpty().withMessage('挑战值不能为空')
  ],
  validateRequest,
  async (req, res) => {
    try {
      const { userId, deviceId, biometricType, signature, challenge } = req.body;
      
      const verifyResult = await biometricService.verify({
        userId,
        deviceId,
        biometricType,
        signature,
        challenge
      });
      
      // 验证成功后，生成认证令牌
      if (verifyResult.isValid) {
        // 导入认证服务
        const authService = require('../services/auth.service');
        
        // 获取用户信息
        const userService = require('../services/user.service');
        const user = await userService.getUserById(userId);
        
        if (!user) {
          throw new Error('用户不存在');
        }
        
        // 生成认证令牌
        const tokens = await authService.generateTokens(user);
        
        // 创建会话记录
        await authService.createSession({
          userId: user.id,
          refreshToken: tokens.refreshToken,
          deviceId,
          deviceInfo: {
            type: deviceId.split(':')[0] || 'unknown',
            name: deviceId.split(':')[1] || deviceId,
            biometricType: biometricType
          },
          ip: req.ip,
          userAgent: req.headers['user-agent']
        });
        
        // 返回用户信息和令牌
        res.status(200).json({
          success: true,
          message: '生物识别验证成功',
          user: {
            id: user.id,
            username: user.username,
            email: user.email,
            name: user.name,
            avatar: user.avatar,
            phone: user.phone,
            createdAt: user.created_at,
            updatedAt: user.updated_at
          },
          token: {
            accessToken: tokens.accessToken,
            refreshToken: tokens.refreshToken,
            expiresIn: tokens.expiresIn
          },
          verified: verifyResult,
          requires2FA: false
        });
      } else {
        throw new Error('生物识别验证失败');
      }
    } catch (error) {
      logger.error(`生物识别验证失败: ${error.message}`, { error });
      
      res.status(error.status || 401).json({
        success: false,
        message: error.message || '生物识别验证失败',
        errors: error.errors || null,
        code: 'auth/biometric-verify-failed'
      });
    }
  }
);

/**
 * @route POST /api/auth/biometric/challenge
 * @desc 生成生物识别挑战值
 * @access 公开
 */
router.post(
  '/challenge',
  [
    body('userId').notEmpty().withMessage('用户ID不能为空'),
    body('deviceId').notEmpty().withMessage('设备ID不能为空')
  ],
  validateRequest,
  async (req, res) => {
    try {
      const { userId, deviceId } = req.body;
      
      const challenge = await biometricService.generateChallenge({
        userId,
        deviceId
      });
      
      res.status(200).json({
        success: true,
        message: '生物识别挑战值生成成功',
        data: challenge
      });
    } catch (error) {
      logger.error(`生物识别挑战值生成失败: ${error.message}`, { error });
      
      res.status(error.status || 500).json({
        success: false,
        message: error.message || '生物识别挑战值生成失败',
        errors: error.errors || null
      });
    }
  }
);

/**
 * @route DELETE /api/auth/biometric/unregister
 * @desc 取消注册生物识别凭据
 * @access 需要认证
 */
router.delete(
  '/unregister',
  authenticate,
  [
    body('deviceId').notEmpty().withMessage('设备ID不能为空'),
    body('biometricType').optional()
      .isIn(['fingerprint', 'faceId', 'voiceRecognition']).withMessage('不支持的生物识别类型')
  ],
  validateRequest,
  async (req, res) => {
    try {
      const { deviceId, biometricType } = req.body;
      
      // 使用当前已认证用户的ID
      const userId = req.user.id;
      
      const result = await biometricService.unregister({
        userId,
        deviceId,
        biometricType
      });
      
      res.status(200).json({
        success: true,
        message: '生物识别凭据取消注册成功',
        data: result
      });
    } catch (error) {
      logger.error(`生物识别凭据取消注册失败: ${error.message}`, { error });
      
      res.status(error.status || 500).json({
        success: false,
        message: error.message || '生物识别凭据取消注册失败',
        errors: error.errors || null
      });
    }
  }
);

/**
 * @route GET /api/auth/biometric/credentials
 * @desc 获取用户生物识别凭据列表
 * @access 需要认证
 */
router.get(
  '/credentials',
  authenticate,
  async (req, res) => {
    try {
      // 使用当前已认证用户的ID
      const userId = req.user.id;
      
      const credentials = await biometricService.getUserCredentials(userId);
      
      res.status(200).json({
        success: true,
        message: '获取生物识别凭据列表成功',
        data: credentials
      });
    } catch (error) {
      logger.error(`获取生物识别凭据列表失败: ${error.message}`, { error });
      
      res.status(error.status || 500).json({
        success: false,
        message: error.message || '获取生物识别凭据列表失败',
        errors: error.errors || null
      });
    }
  }
);

/**
 * @route PATCH /api/auth/biometric/credentials/:id
 * @desc 更新生物识别凭据
 * @access 需要认证
 */
router.patch(
  '/credentials/:id',
  authenticate,
  [
    param('id').notEmpty().withMessage('凭据ID不能为空'),
    body('expiresAt').optional().isISO8601().withMessage('过期时间必须是有效的ISO日期格式')
  ],
  validateRequest,
  async (req, res) => {
    try {
      const id = req.params.id;
      const { expiresAt } = req.body;
      
      // 使用当前已认证用户的ID
      const userId = req.user.id;
      
      const result = await biometricService.updateCredential({
        id,
        userId,
        updates: {
          expiresAt
        }
      });
      
      res.status(200).json({
        success: true,
        message: '生物识别凭据更新成功',
        data: result
      });
    } catch (error) {
      logger.error(`生物识别凭据更新失败: ${error.message}`, { error });
      
      res.status(error.status || 500).json({
        success: false,
        message: error.message || '生物识别凭据更新失败',
        errors: error.errors || null
      });
    }
  }
);

module.exports = router; 