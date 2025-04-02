/**
 * 用户相关路由
 */
const express = require('express');
const { authMiddleware, validationMiddleware } = require('@suoke/shared').middlewares;
const userController = require('../controllers/user.controller');
const userValidation = require('../models/user.validation');
const { userModel } = require('../models');
const { validate } = require('@suoke/shared').utils;
const { auth, rbac, validation: validationMiddleware } = require('../middlewares');
const { schemas } = validationMiddleware.validation;
const { verifyToken, verifyRefreshToken } = require('../middlewares/auth.middleware');
const { checkPermission } = require('../middlewares/rbac.middleware');
const { userSchemas } = require('../models/user.model');
const { loginLimiter, registerLimiter } = require('../middlewares/rate-limit.middleware');

const router = express.Router();

/**
 * @route GET /api/v1/users
 * @desc 获取用户列表
 * @access 管理员
 */
router.get('/', authMiddleware.isAdmin, userController.getUsers);

/**
 * @route GET /api/v1/users/:id
 * @desc 获取用户详情
 * @access 认证用户
 */
router.get('/:id', authMiddleware.isAuthenticated, userController.getUserById);

/**
 * @route POST /api/v1/users
 * @desc 创建用户
 * @access 公开
 */
router.post('/', validationMiddleware(userValidation.createUser), userController.createUser);

/**
 * @route PUT /api/v1/users/:id
 * @desc 更新用户
 * @access 认证用户
 */
router.put('/:id', authMiddleware.isAuthenticated, validationMiddleware(userValidation.updateUser), userController.updateUser);

/**
 * @route DELETE /api/v1/users/:id
 * @desc 删除用户
 * @access 管理员
 */
router.delete('/:id', authMiddleware.isAdmin, userController.deleteUser);

// 公开路由
router.post('/register', registerLimiter, userController.register);
router.post('/login', loginLimiter, userController.login);
router.post('/verify', validate(userSchemas.verifySchema), userController.verifyUser);
router.post('/resend-verification', validate(userSchemas.resendVerificationSchema), userController.resendVerification);
router.post('/forgot-password', validate(userSchemas.forgotPasswordSchema), userController.forgotPassword);
router.post('/reset-password', validate(userSchemas.resetPasswordSchema), userController.resetPassword);

// 需要认证的路由
router.use(verifyToken);

// 用户信息相关
router.get('/me', userController.getCurrentUser);
router.put('/profile', validate(userSchemas.updateProfileSchema), userController.updateProfile);
router.delete('/account', validate(userSchemas.deleteAccountSchema), userController.deleteAccount);

// 多因素认证相关
router.post('/mfa/enable', userController.enableMFA);
router.post('/mfa/disable', userController.disableMFA);

// 会话管理相关
router.get('/sessions', userController.getUserSessions);
router.delete('/sessions/:sessionId', userController.terminateSession);
router.delete('/sessions', userController.terminateAllSessions);

// 令牌相关
router.post('/logout', userController.logout);
router.post('/refresh-token', verifyRefreshToken, userController.refreshToken);

// 管理员路由
router.use(checkPermission('admin'));
router.get('/users', validate(userSchemas.querySchema), userController.getUsers);
router.get('/users/:id', validate(userSchemas.idSchema), userController.getUserById);
router.put('/users/:id', validate(userSchemas.updateUserSchema), userController.updateUser);
router.delete('/users/:id', validate(userSchemas.idSchema), userController.deleteUser);

/**
 * @route POST /api/users/verify-email
 * @desc 验证邮箱
 * @access Public
 */
router.post('/verify-email', userController.verifyEmail);

/**
 * @route POST /api/users/verify-phone
 * @desc 验证手机号
 * @access Public
 */
router.post('/verify-phone', userController.verifyPhone);

/**
 * @route GET /api/users/:id
 * @desc 获取用户信息（管理员接口）
 * @access Private/Admin
 */
router.get('/:id', 
  auth.verifyToken,
  validation.validate(schemas.idParam, 'params'),
  rbac.hasRole(['admin', 'system_admin']),
  userController.getUserById
);

module.exports = router; 