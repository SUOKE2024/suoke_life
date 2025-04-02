/**
 * 短信认证路由
 */
const express = require('express');
const router = express.Router();
const smsAuthController = require('../controllers/sms-auth.controller');
const { verifyToken } = require('../middlewares/auth.middleware');

/**
 * @swagger
 * /api/auth/sms/send:
 *   post:
 *     tags:
 *       - 短信认证
 *     summary: 发送短信验证码
 *     description: 发送短信验证码，支持登录、注册、重置密码等场景
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - phone
 *               - type
 *             properties:
 *               phone:
 *                 type: string
 *                 description: 手机号
 *               type:
 *                 type: string
 *                 enum: [login, register, reset_password, change_phone, verify_phone, two_factor]
 *                 description: 验证码类型
 *               userId:
 *                 type: string
 *                 description: 用户ID（某些场景可选）
 *     responses:
 *       200:
 *         description: 验证码发送成功
 *       400:
 *         description: 参数错误或手机号已注册
 *       429:
 *         description: 请求过于频繁
 *       500:
 *         description: 服务器错误
 */
router.post('/send', smsAuthController.sendVerificationCode);

/**
 * @swagger
 * /api/auth/sms/login:
 *   post:
 *     tags:
 *       - 短信认证
 *     summary: 短信验证码登录
 *     description: 使用手机号和短信验证码进行登录
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - phone
 *               - code
 *             properties:
 *               phone:
 *                 type: string
 *                 description: 手机号
 *               code:
 *                 type: string
 *                 description: 短信验证码
 *     responses:
 *       200:
 *         description: 登录成功或需要二因素认证
 *       400:
 *         description: 参数错误
 *       401:
 *         description: 验证码错误
 *       403:
 *         description: 账户已锁定或未激活
 *       404:
 *         description: 用户不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/login', smsAuthController.loginWithSmsCode);

/**
 * @swagger
 * /api/auth/sms/register:
 *   post:
 *     tags:
 *       - 短信认证
 *     summary: 短信验证码注册
 *     description: 使用手机号和短信验证码进行注册
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - phone
 *               - code
 *               - username
 *             properties:
 *               phone:
 *                 type: string
 *                 description: 手机号
 *               code:
 *                 type: string
 *                 description: 短信验证码
 *               username:
 *                 type: string
 *                 description: 用户名
 *               password:
 *                 type: string
 *                 description: 密码（可选）
 *     responses:
 *       201:
 *         description: 注册成功
 *       400:
 *         description: 参数错误或手机号/用户名已存在
 *       401:
 *         description: 验证码错误
 *       500:
 *         description: 服务器错误
 */
router.post('/register', smsAuthController.registerWithSmsCode);

/**
 * @swagger
 * /api/auth/sms/reset-password:
 *   post:
 *     tags:
 *       - 短信认证
 *     summary: 短信验证码重置密码
 *     description: 使用手机号和短信验证码重置密码
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - phone
 *               - code
 *               - newPassword
 *             properties:
 *               phone:
 *                 type: string
 *                 description: 手机号
 *               code:
 *                 type: string
 *                 description: 短信验证码
 *               newPassword:
 *                 type: string
 *                 description: 新密码
 *     responses:
 *       200:
 *         description: 密码重置成功
 *       400:
 *         description: 参数错误
 *       401:
 *         description: 验证码错误
 *       404:
 *         description: 用户不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/reset-password', smsAuthController.resetPasswordWithSmsCode);

/**
 * @swagger
 * /api/auth/sms/verify-phone:
 *   post:
 *     tags:
 *       - 短信认证
 *     summary: 验证手机号
 *     description: 验证手机号归属（需要登录）
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - phone
 *               - code
 *             properties:
 *               phone:
 *                 type: string
 *                 description: 手机号
 *               code:
 *                 type: string
 *                 description: 短信验证码
 *     responses:
 *       200:
 *         description: 手机号验证成功
 *       400:
 *         description: 参数错误或手机号已被使用
 *       401:
 *         description: 未授权或验证码错误
 *       500:
 *         description: 服务器错误
 */
router.post('/verify-phone', verifyToken, smsAuthController.verifyPhone);

/**
 * @swagger
 * /api/auth/sms/change-phone:
 *   post:
 *     tags:
 *       - 短信认证
 *     summary: 更改手机号
 *     description: 更改绑定的手机号（需要登录）
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - newPhone
 *               - code
 *             properties:
 *               newPhone:
 *                 type: string
 *                 description: 新手机号
 *               code:
 *                 type: string
 *                 description: 短信验证码
 *     responses:
 *       200:
 *         description: 手机号更改成功
 *       400:
 *         description: 参数错误或手机号已被使用
 *       401:
 *         description: 未授权或验证码错误
 *       500:
 *         description: 服务器错误
 */
router.post('/change-phone', verifyToken, smsAuthController.changePhone);

module.exports = router; 