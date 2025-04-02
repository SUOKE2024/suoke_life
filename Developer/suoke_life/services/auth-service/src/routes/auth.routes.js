/**
 * 基础认证相关路由
 */
const express = require('express');
const passport = require('passport');
const { validationMiddleware } = require('@suoke/shared').middlewares;
const authController = require('../controllers/auth.controller');
const authValidation = require('../models/auth.validation');
const { verifyToken } = require('../middlewares/auth.middleware');
const { generateCsrfToken, validateCsrfToken } = require('../middlewares/csrf.middleware');
const { 
  loginLimiter, 
  registerLimiter, 
  passwordResetLimiter 
} = require('../middlewares/rate-limit.middleware');

const router = express.Router();

/**
 * @swagger
 * tags:
 *   name: 认证
 *   description: 用户认证与授权API
 */

/**
 * @swagger
 * /auth/register:
 *   post:
 *     summary: 用户注册
 *     tags: [认证]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - username
 *               - email
 *               - password
 *             properties:
 *               username:
 *                 type: string
 *                 description: 用户名
 *               email:
 *                 type: string
 *                 format: email
 *                 description: 邮箱地址
 *               password:
 *                 type: string
 *                 format: password
 *                 description: 密码
 *     responses:
 *       201:
 *         description: 注册成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 用户注册成功
 *                 userId:
 *                   type: string
 *                   example: 550e8400-e29b-41d4-a716-446655440000
 *       400:
 *         description: 无效的请求参数
 *       409:
 *         description: 用户名或邮箱已存在
 */
router.post('/register', registerLimiter, validateCsrfToken, authController.register);

/**
 * @swagger
 * /auth/login:
 *   post:
 *     summary: 用户登录
 *     tags: [认证]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - username
 *               - password
 *             properties:
 *               username:
 *                 type: string
 *                 description: 用户名或邮箱
 *               password:
 *                 type: string
 *                 format: password
 *                 description: 密码
 *               deviceInfo:
 *                 type: object
 *                 description: 设备信息（可选）
 *                 properties:
 *                   name:
 *                     type: string
 *                     description: 设备名称
 *                   type:
 *                     type: string
 *                     description: 设备类型
 *                   os:
 *                     type: string
 *                     description: 操作系统
 *                   clientId:
 *                     type: string
 *                     description: 客户端标识符
 *     responses:
 *       200:
 *         description: 登录成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 accessToken:
 *                   type: string
 *                 refreshToken:
 *                   type: string
 *                 user:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: string
 *                     username:
 *                       type: string
 *                     email:
 *                       type: string
 *                 session:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: string
 *                     status:
 *                       type: string
 *                     deviceInfo:
 *                       type: object
 *       400:
 *         description: 无效的请求参数
 *       401:
 *         description: 用户名或密码错误
 */
router.post('/login', loginLimiter, authController.login);

/**
 * @swagger
 * /auth/logout:
 *   post:
 *     summary: 用户登出
 *     tags: [认证]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 登出成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 登出成功
 *       401:
 *         description: 未授权
 */
router.post('/logout', verifyToken, validateCsrfToken, authController.logout);

/**
 * @swagger
 * /auth/refresh-token:
 *   post:
 *     summary: 刷新访问令牌
 *     tags: [认证]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - refreshToken
 *             properties:
 *               refreshToken:
 *                 type: string
 *                 description: 刷新令牌
 *     responses:
 *       200:
 *         description: 令牌刷新成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 accessToken:
 *                   type: string
 *                 refreshToken:
 *                   type: string
 *       400:
 *         description: 无效的请求参数
 *       401:
 *         description: 无效或过期的刷新令牌
 */
router.post('/refresh-token', authController.refreshToken);

/**
 * @swagger
 * /auth/forgot-password:
 *   post:
 *     summary: 忘记密码请求
 *     tags: [认证]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *                 description: 用户注册邮箱
 *     responses:
 *       200:
 *         description: 重置密码邮件发送成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 重置密码邮件已发送
 *       400:
 *         description: 无效的请求参数
 *       404:
 *         description: 邮箱未注册
 */
router.post('/forgot-password', passwordResetLimiter, validateCsrfToken, authController.forgotPassword);

/**
 * @swagger
 * /auth/reset-password:
 *   post:
 *     summary: 重置密码
 *     tags: [认证]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - token
 *               - password
 *             properties:
 *               token:
 *                 type: string
 *                 description: 重置密码令牌
 *               password:
 *                 type: string
 *                 format: password
 *                 description: 新密码
 *     responses:
 *       200:
 *         description: 密码重置成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 密码重置成功
 *       400:
 *         description: 无效的请求参数
 *       401:
 *         description: 无效或过期的重置令牌
 */
router.post('/reset-password', passwordResetLimiter, validateCsrfToken, authController.resetPassword);

/**
 * @swagger
 * /auth/get-csrf-token:
 *   get:
 *     summary: 获取CSRF令牌
 *     tags: [认证]
 *     responses:
 *       200:
 *         description: CSRF令牌获取成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 csrfToken:
 *                   type: string
 *                 csrfSignature:
 *                   type: string
 */
router.get('/get-csrf-token', generateCsrfToken, (req, res) => {
  res.status(200).json({
    success: true,
    csrfToken: res.locals.csrfToken,
    csrfSignature: res.locals.csrfSignature
  });
});

module.exports = router; 