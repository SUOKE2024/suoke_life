/**
 * 双因素认证路由
 */
const express = require('express');
const router = express.Router();
const twoFactorController = require('../controllers/two-factor.controller');
const { verifyToken, verifyTwoFactorSession } = require('../middlewares/auth.middleware');

/**
 * @swagger
 * /api/auth/2fa/setup:
 *   post:
 *     tags:
 *       - 双因素认证
 *     summary: 生成二因素认证密钥
 *     description: 生成TOTP二因素认证密钥和二维码
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功生成密钥
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.post('/setup', verifyToken, twoFactorController.generateTwoFactorSecret);

/**
 * @swagger
 * /api/auth/2fa/activate:
 *   post:
 *     tags:
 *       - 双因素认证
 *     summary: 验证并激活二因素认证
 *     description: 验证TOTP令牌并激活二因素认证
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - setupId
 *               - token
 *             properties:
 *               setupId:
 *                 type: string
 *               token:
 *                 type: string
 *     responses:
 *       200:
 *         description: 成功激活二因素认证
 *       400:
 *         description: 验证失败或参数错误
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.post('/activate', verifyToken, twoFactorController.verifyAndActivateTwoFactor);

/**
 * @swagger
 * /api/auth/2fa/verify:
 *   post:
 *     tags:
 *       - 双因素认证
 *     summary: 验证二因素认证令牌
 *     description: 验证TOTP令牌或恢复码
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *               - token
 *             properties:
 *               userId:
 *                 type: string
 *               token:
 *                 type: string
 *     responses:
 *       200:
 *         description: 验证成功
 *       401:
 *         description: 验证失败
 *       500:
 *         description: 服务器错误
 */
router.post('/verify', twoFactorController.verifyTwoFactor);

/**
 * @swagger
 * /api/auth/2fa/recovery-codes:
 *   post:
 *     tags:
 *       - 双因素认证
 *     summary: 重新生成恢复码
 *     description: 为已启用二因素认证的用户重新生成恢复码
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功生成恢复码
 *       400:
 *         description: 用户未启用二因素认证
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.post('/recovery-codes', verifyToken, twoFactorController.regenerateRecoveryCodes);

/**
 * @swagger
 * /api/auth/2fa/disable:
 *   post:
 *     tags:
 *       - 双因素认证
 *     summary: 禁用二因素认证
 *     description: 禁用用户的二因素认证
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - password
 *             properties:
 *               password:
 *                 type: string
 *     responses:
 *       200:
 *         description: 成功禁用二因素认证
 *       400:
 *         description: 用户未启用二因素认证或参数错误
 *       401:
 *         description: 未授权或密码验证失败
 *       500:
 *         description: 服务器错误
 */
router.post('/disable', verifyToken, twoFactorController.disableTwoFactor);

/**
 * @swagger
 * /api/auth/2fa/status:
 *   get:
 *     tags:
 *       - 双因素认证
 *     summary: 获取二因素认证状态
 *     description: 检查用户是否已启用二因素认证
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功获取状态
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.get('/status', verifyToken, twoFactorController.getTwoFactorStatus);

/**
 * @swagger
 * /auth/2fa/verify-login:
 *   post:
 *     summary: 验证二因素认证并完成登录
 *     description: 验证二因素认证码或恢复码并完成登录流程
 *     tags: [认证, 二因素认证]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *               - tempSessionId
 *               - code
 *             properties:
 *               userId:
 *                 type: string
 *                 description: 用户ID
 *               tempSessionId:
 *                 type: string
 *                 description: 临时会话ID
 *               code:
 *                 type: string
 *                 description: 二因素认证码或恢复码
 *               rememberDevice:
 *                 type: boolean
 *                 description: 是否记住此设备(延长会话期限)
 *                 default: false
 *     responses:
 *       200:
 *         description: 二因素认证成功，返回令牌和用户信息
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     accessToken:
 *                       type: string
 *                     refreshToken:
 *                       type: string
 *                     expiresIn:
 *                       type: number
 *                     user:
 *                       type: object
 *                     sessionId:
 *                       type: string
 *       400:
 *         description: 请求参数错误
 *       401:
 *         description: 认证码无效或会话已过期
 *       500:
 *         description: 服务器错误
 */
router.post('/verify-login', verifyTwoFactorSession, twoFactorController.verifyTwoFactorAndLogin);

module.exports = router; 