/**
 * 健康资料路由
 */
const express = require('express');
const router = express.Router();
const { healthProfileController } = require('../controllers');
const { authMiddleware } = require('@suoke/shared').middleware;
const { validate } = require('@suoke/shared').utils;
const { healthProfileModel } = require('../models');

// 所有路由都需要认证
router.use(authMiddleware.authenticate);

// 健康资料操作
router.get('/', healthProfileController.getHealthProfile);
router.post('/', validate(healthProfileModel.createSchema), healthProfileController.createHealthProfile);
router.put('/', validate(healthProfileModel.updateSchema), healthProfileController.updateHealthProfile);
router.delete('/', healthProfileController.deleteHealthProfile);

// 健康资料特殊操作
router.put('/last-checkup', healthProfileController.updateLastCheckup);
router.put('/constitution-type', validate(healthProfileModel.constitutionTypeSchema), healthProfileController.updateConstitutionType);

// 健康建议
router.get('/recommendations', healthProfileController.getHealthRecommendations);

// 管理员路由
router.get('/constitution-type-counts', authMiddleware.isAdmin, healthProfileController.getConstitutionTypeCounts);

module.exports = router; 