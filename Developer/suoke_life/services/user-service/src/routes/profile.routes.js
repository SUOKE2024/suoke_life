/**
 * 个人资料路由
 */
const express = require('express');
const router = express.Router();
const { profileController } = require('../controllers');
const { authMiddleware } = require('@suoke/shared').middleware;
const { validate } = require('@suoke/shared').utils;
const { profileModel } = require('../models');

// 所有路由都需要认证
router.use(authMiddleware.authenticate);

// 个人资料操作
router.get('/', profileController.getProfile);
router.post('/', validate(profileModel.createSchema), profileController.createProfile);
router.put('/', validate(profileModel.updateSchema), profileController.updateProfile);
router.delete('/', profileController.deleteProfile);

// 头像操作
router.get('/avatar', profileController.getAvatar);
router.put('/avatar', validate(profileModel.avatarSchema), profileController.updateAvatar);

// 昵称检查
router.get('/check-nickname', profileController.checkNicknameAvailability);

// 管理员路由
router.get('/search', authMiddleware.isAdmin, profileController.searchProfiles);

module.exports = router; 